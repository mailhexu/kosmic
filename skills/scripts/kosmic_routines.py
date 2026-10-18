#!/usr/bin/env python3
"""Static routine registry and shared deterministic mechanics for Kosmic."""

from __future__ import annotations

import fcntl
import ast
import hashlib
import json
import secrets
import subprocess
import re
import os
import shutil
import stat
import tempfile
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

SCHEMA = "kosmic.routines/v1"
ID_RE_TEXT = r"^[a-z0-9]+(?:-[a-z0-9]+)*/[a-z0-9]+(?:-[a-z0-9]+)*$"
SIDE_EFFECTS = {"filesystem", "subprocess"}
GENERATOR_VERSION = 1


class RoutineError(RuntimeError):
    """A routine declaration, inventory, query, or publication is invalid."""


@dataclass(frozen=True)
class RoutineQuery:
    query: str | None = None
    id: str | None = None
    domain: str | None = None
    module: str | None = None
    symbol: str | None = None
    owner: str | None = None
    caller: str | None = None
    procedure: str | None = None


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _contained(root: Path, path: Path, label: str) -> Path:
    root = root.resolve()
    path = path.resolve()
    if path != root and root not in path.parents:
        raise RoutineError(f"{label} escapes {root}: {path}")
    return path


def _definitions(tree: ast.Module) -> dict[str, int]:
    result: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            result[node.name] = result.get(node.name, 0) + 1
    return result


def _reference_exists(repo_root: Path, reference: str) -> bool:
    path_text, separator, symbol = reference.partition("::")
    if not separator or not symbol:
        return False
    path = _contained(repo_root, repo_root / path_text, "reference")
    if not path.is_file() or path.suffix != ".py":
        return False
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    names = _definitions(tree)
    if symbol in names:
        return names[symbol] == 1
    if "." in symbol:
        cls, method = symbol.split(".", 1)
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == cls:
                return sum(isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method for item in node.body) == 1
    return False

def _python_reference_exists(source_root: Path, reference: str) -> bool:
    if not reference.startswith("python:"):
        return False
    module, separator, symbol = reference[7:].partition(":")
    if not separator or not module or not symbol:
        return False
    path = _contained(source_root, source_root / (module.replace(".", "/") + ".py"), "caller")
    if not path.is_file():
        return False
    return _definitions(ast.parse(path.read_text(encoding="utf-8"), filename=str(path))).get(symbol) == 1


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise RoutineError(f"invalid Domain Topic frontmatter: {path}")
    result: dict[str, str] = {}
    for line in text.split("\n---\n", 1)[0].splitlines()[1:]:
        key, separator, value = line.partition(":")
        if separator:
            result[key.strip()] = value.strip()
    return result


def _string_list(value: str) -> list[str]:
    if value == "[]":
        return []
    if not value.startswith("[") or not value.endswith("]"):
        raise RoutineError(f"expected inline string list, got {value!r}")
    return [item.strip() for item in value[1:-1].split(",") if item.strip()]


def _domain_maintainers(library_root: Path, domain: str) -> list[str]:
    skill = _contained(library_root, library_root / domain / "SKILL.md", "domain")
    if not skill.is_file():
        raise RoutineError(f"routine domain is missing: {domain}")
    return _string_list(_frontmatter(skill).get("maintainers", "[]"))


def _procedure_uses(library_root: Path, reference: str, routine_id: str) -> bool:
    if not reference.startswith("topic:"):
        return False
    topic_id = reference[6:]
    parts = topic_id.split("/")
    if len(parts) != 3 or parts[1] not in {"usage", "development"}:
        return False
    path = _contained(library_root, library_root.joinpath(*parts[:2], parts[2] + ".md"), "procedure")
    if not path.is_file():
        return False
    metadata = _frontmatter(path)
    return (
        metadata.get("status") == "stable"
        and metadata.get("artifact_role") == "procedure"
        and routine_id in _string_list(metadata.get("uses_routines", "[]"))
    )


def _literal_declarations(path: Path, tree: ast.Module) -> list[dict[str, Any]]:
    assignments = [
        node for node in tree.body
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        and ((isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "KOSMIC_ROUTINES" for t in node.targets))
             or (isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "KOSMIC_ROUTINES"))
    ]
    if not assignments:
        return []
    if len(assignments) != 1:
        raise RoutineError(f"duplicate KOSMIC_ROUTINES declaration in {path}")
    value = assignments[0].value
    try:
        declarations = ast.literal_eval(value)
    except (ValueError, TypeError) as error:
        raise RoutineError(f"KOSMIC_ROUTINES must be literal in {path}") from error
    if not isinstance(declarations, (list, tuple)) or not all(isinstance(item, dict) for item in declarations):
        raise RoutineError(f"KOSMIC_ROUTINES must be a list or tuple of mappings in {path}")
    return list(declarations)


def build_routine_inventory(repo_root: Path, source_root: Path, library_root: Path) -> dict[str, object]:
    """Build a normalized inventory by parsing source; source modules are never imported."""
    repo_root = repo_root.resolve()
    source_root = _contained(repo_root, source_root, "source root")
    library_root = library_root.resolve()
    _contained(repo_root, repo_root / "tests", "tests root")
    if not (repo_root / "tests").is_dir():
        raise RoutineError(f"repository root has no tests directory: {repo_root}")
    records: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    seen_symbols: set[tuple[str, str]] = set()
    for path in sorted(source_root.rglob("*.py")):
        raw = path.read_bytes()
        tree = ast.parse(raw, filename=str(path))
        definitions = _definitions(tree)
        relative = path.relative_to(repo_root).as_posix()
        for declaration in _literal_declarations(path, tree):
            required = {"id", "symbol", "summary", "owner", "deterministic", "offline", "side_effects", "tests", "callers", "procedures"}
            if set(declaration) != required:
                raise RoutineError(f"invalid routine declaration keys in {relative}")
            routine_id = declaration["id"]
            symbol = declaration["symbol"]
            if not isinstance(routine_id, str) or not re.fullmatch(ID_RE_TEXT, routine_id):
                raise RoutineError(f"invalid routine id: {routine_id}")
            domain = routine_id.split("/", 1)[0]
            if routine_id in seen_ids:
                raise RoutineError(f"duplicate routine id: {routine_id}")
            if not isinstance(symbol, str) or definitions.get(symbol) != 1:
                raise RoutineError(f"routine symbol must resolve exactly once: {relative}::{symbol}")
            symbol_key = (relative, symbol)
            if symbol_key in seen_symbols:
                raise RoutineError(f"duplicate routine symbol: {relative}::{symbol}")
            for flag in ("deterministic", "offline"):
                if declaration[flag] is not True:
                    raise RoutineError(f"routine {routine_id} must declare {flag}: true")
            effects = declaration["side_effects"]
            tests = declaration["tests"]
            callers = declaration["callers"]
            procedures = declaration["procedures"]
            if not isinstance(effects, (list, tuple)) or not effects or not all(isinstance(x, str) for x in effects) or not set(effects) <= SIDE_EFFECTS:
                raise RoutineError(f"invalid side effects for {routine_id}")
            if not isinstance(tests, (list, tuple)) or not tests or not all(_reference_exists(repo_root, x) for x in tests):
                raise RoutineError(f"unresolvable tests for {routine_id}")
            if not isinstance(callers, (list, tuple)) or not callers or not all(_python_reference_exists(source_root, x) for x in callers):
                raise RoutineError(f"unresolvable callers for {routine_id}")
            if not isinstance(procedures, (list, tuple)) or not all(isinstance(x, str) for x in procedures):
                raise RoutineError(f"invalid procedures for {routine_id}")
            maintainers = _domain_maintainers(library_root, domain)
            if declaration["owner"] not in maintainers:
                raise RoutineError(f"invalid owner for routine {routine_id}: {declaration['owner']}")
            if not all(_procedure_uses(library_root, reference, routine_id) for reference in procedures):
                raise RoutineError(f"invalid or non-reciprocal procedure for {routine_id}")
            canonical = {
                key: sorted(set(declaration[key])) if key in {"side_effects", "tests", "callers", "procedures"} else declaration[key]
                for key in sorted(declaration)
            }
            declaration_sha = _sha(_json_bytes(canonical))
            record = dict(canonical)
            record.update({
                "domain": domain,
                "module": relative,
                "source_sha256": _sha(raw),
                "declaration_sha256": declaration_sha,
                "routine_sha256": _sha(raw + _json_bytes(canonical)),
            })
            record["procedures"] = [reference[6:] for reference in canonical["procedures"]]
            records.append(record)
            seen_ids.add(routine_id)
            seen_symbols.add(symbol_key)
    records.sort(key=lambda row: str(row["id"]))
    inventory: dict[str, object] = {
        "schema": SCHEMA,
        "generator_version": GENERATOR_VERSION,
        "source_root": source_root.relative_to(repo_root).as_posix(),
        "routines": records,
    }
    inventory["inventory_sha256"] = _sha(_json_bytes(inventory))
    return inventory


def validate_routine_inventory(repo_root: Path, source_root: Path, library_root: Path, inventory: dict[str, object]) -> None:
    expected = build_routine_inventory(repo_root, source_root, library_root)
    if inventory != expected:
        raise RoutineError("stale or invalid routine inventory")


def query_routines(inventory: dict[str, object], query: RoutineQuery) -> tuple[dict[str, object], ...]:
    selectors = (query.query, query.id, query.domain, query.module, query.symbol, query.owner, query.caller, query.procedure)
    if not any(selectors):
        raise RoutineError("query-routines requires at least one selector")
    rows = list(inventory.get("routines", []))
    exact = {"id": query.id, "domain": query.domain, "module": query.module, "symbol": query.symbol, "owner": query.owner}
    for field, value in exact.items():
        if value is not None:
            rows = [row for row in rows if row.get(field) == value]
    if query.caller is not None:
        rows = [row for row in rows if query.caller in row.get("callers", [])]
    if query.procedure is not None:
        rows = [row for row in rows if query.procedure in row.get("procedures", [])]
    if query.query:
        tokens = set(query.query.lower().replace("-", " ").replace("/", " ").split())
        weights = {"id": 8, "summary": 6, "module": 4, "symbol": 4, "callers": 2, "procedures": 2, "domain": 2}
        scored: list[tuple[int, dict[str, object]]] = []
        for row in rows:
            score = 0
            for field, weight in weights.items():
                value = row.get(field, "")
                text = " ".join(value) if isinstance(value, list) else str(value)
                score += weight * len(tokens & set(text.lower().replace("-", " ").replace("/", " ").split()))
            if score:
                scored.append((score, row))
        if not scored:
            return ()
        best = max(score for score, _ in scored)
        rows = [row for score, row in scored if score == best]
    return tuple(sorted(rows, key=lambda row: str(row["id"])))


PUBLICATION_MARKER = ".kosmic-publish-marker.json"
PUBLICATION_PREFIX = ".kosmic-publish-backup-"
PUBLICATION_GRACE = timedelta(hours=24)
PUBLICATION_RETENTION = timedelta(days=7)
PUBLICATION_PHASES = frozenset({"prepared", "prior-tree-saved", "recovering-restore", "staged-installed", "committed"})


@dataclass(frozen=True)
class PublicationSiblingState:
    path: Path
    state: str
    reason: str
    marker: dict[str, Any] | None


@dataclass(frozen=True)
class PublicationRecoveryResult:
    path: Path
    action: str
    reason: str
    git_before_sha256: str | None
    git_after_sha256: str | None


def _format_publication_time(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_publication_time(value: object) -> datetime:
    if not isinstance(value, str):
        raise RoutineError("publication marker timestamp is missing")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise RoutineError("publication marker timestamp is invalid") from error


def _write_publication_marker(directory: Path, marker: dict[str, Any]) -> None:
    temporary = directory / f".{PUBLICATION_MARKER}.{secrets.token_hex(4)}"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        payload = _json_bytes(marker)
        os.write(descriptor, payload)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    os.replace(temporary, directory / PUBLICATION_MARKER)
    directory_fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def _path_digest(path: Path) -> str:
    digest = hashlib.sha256()
    if path.is_symlink():
        raise RoutineError(f"symlinked publication path: {path}")
    if path.is_file():
        digest.update(b"file\0")
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1 << 20), b""):
                digest.update(chunk)
        return digest.hexdigest()
    if not path.is_dir():
        raise RoutineError(f"unsupported publication path: {path}")
    digest.update(b"tree\0")
    for child in sorted(path.rglob("*"), key=lambda item: item.relative_to(path).as_posix()):
        relative = child.relative_to(path).as_posix().encode()
        if child.is_symlink():
            raise RoutineError(f"symlinked publication path: {child}")
        if child.is_dir():
            digest.update(b"dir\0" + relative + b"\0")
        elif child.is_file():
            digest.update(b"file\0" + relative + b"\0")
            with child.open("rb") as source:
                for chunk in iter(lambda: source.read(1 << 20), b""):
                    digest.update(chunk)
        else:
            raise RoutineError(f"unsupported publication path: {child}")
    return digest.hexdigest()


def _publication_marker(destination: Path, staged: Path, managed_paths: Sequence[str] | None) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    return {
        "schema": "kosmic.publish-marker/v1",
        "operation_id": secrets.token_hex(16),
        "destination": str(destination),
        "source_git_sha256": _path_digest(staged),
        "phase": "prepared",
        "pid": os.getpid(),
        "created_at": _format_publication_time(now),
        "grace_expires_at": _format_publication_time(now + PUBLICATION_GRACE),
        "retire_by": _format_publication_time(now + PUBLICATION_RETENTION),
        "mode": "whole-tree" if managed_paths is None else "managed-paths",
        "managed_paths": list(managed_paths or ()),
        "moved_paths": [],
        "installed_paths": [],
    }


def _marker_state(path: Path, destination: Path, moment: datetime) -> PublicationSiblingState:
    try:
        status = path.lstat()
        if not path.is_dir() or path.is_symlink() or status.st_uid != os.geteuid() or stat.S_IMODE(status.st_mode) != 0o700:
            return PublicationSiblingState(path, "ambiguous", "SIBLING_UNTRUSTED", None)
        marker_path = path / PUBLICATION_MARKER
        if marker_path.is_symlink() or not marker_path.is_file():
            return PublicationSiblingState(path, "malformed", "MARKER_MISSING", None)
        if marker_path.stat().st_size > 65536:
            return PublicationSiblingState(path, "malformed", "MARKER_TOO_LARGE", None)
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        if not isinstance(marker, dict) or marker.get("schema") != "kosmic.publish-marker/v1":
            return PublicationSiblingState(path, "malformed", "MARKER_SCHEMA", None)
        if marker.get("destination") != str(destination) or marker.get("phase") not in PUBLICATION_PHASES:
            return PublicationSiblingState(path, "ambiguous", "MARKER_IDENTITY", marker)
        grace = _parse_publication_time(marker.get("grace_expires_at"))
        _parse_publication_time(marker.get("retire_by"))
        pid = marker.get("pid")
        if moment < grace and isinstance(pid, int) and pid > 0:
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                pass
            except PermissionError:
                return PublicationSiblingState(path, "ambiguous", "MARKER_PID_UNREADABLE", marker)
            else:
                return PublicationSiblingState(path, "active", "OWNER_LIVE", marker)
        return PublicationSiblingState(path, "grace" if moment < grace else "expired", "LEASE_GRACE" if moment < grace else "LEASE_EXPIRED", marker)

    except (OSError, UnicodeDecodeError, json.JSONDecodeError, RoutineError):
        return PublicationSiblingState(path, "malformed", "MARKER_INVALID", None)

def detect_publication_siblings(destination: Path, *, now: datetime | None = None) -> tuple[PublicationSiblingState, ...]:
    destination = Path(destination).resolve()
    moment = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    try:
        children = tuple(destination.parent.iterdir())
    except OSError as error:
        raise RoutineError(f"publication parent is unreadable: {destination.parent}") from error
    return tuple(
        _marker_state(child, destination, moment)
        for child in sorted(children, key=lambda item: item.name)
        if child.name.startswith(PUBLICATION_PREFIX)
    )


def _git_status_sha256(path: Path) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(path), "status", "--porcelain=v2", "--branch", "--untracked-files=all", "-z"],
        capture_output=True,
        check=False,
    )
    return hashlib.sha256(completed.stdout).hexdigest() if completed.returncode == 0 else None


def _remove_publication_tree(path: Path) -> None:
    if path.is_symlink() or not path.is_dir():
        raise RoutineError(f"publication sibling is not a trusted directory: {path}")
    shutil.rmtree(path)


def recover_publication_siblings(destination: Path, *, now: datetime | None = None) -> tuple[PublicationRecoveryResult, ...]:
    """Recover only validated expired whole-tree publication siblings."""
    destination = Path(destination).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock_path = destination.parent / f".{destination.name}.kosmic-publish.lock"
    lock_fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    lock_acquired = False
    try:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            lock_acquired = True
        except BlockingIOError:
            return (PublicationRecoveryResult(lock_path, "report-only", "DESTINATION_LOCK_HELD", None, None),)
        before = _git_status_sha256(destination.parent)
        results: list[PublicationRecoveryResult] = []
        for state in detect_publication_siblings(destination, now=now):
            if state.state != "expired" or state.marker is None:
                results.append(PublicationRecoveryResult(state.path, "report-only", state.reason, before, before))
                continue
            marker = state.marker
            if marker.get("mode") == "managed-paths":
                # A crash can occur after moving a path and before the marker
                # durably records it.  The backup may be its sole copy.
                results.append(PublicationRecoveryResult(state.path, "report-only", "MANAGED_PATH_RECOVERY_AMBIGUOUS", before, before))
                continue
            if marker.get("mode") != "whole-tree":
                results.append(PublicationRecoveryResult(state.path, "report-only", "MARKER_MODE_UNKNOWN", before, before))
                continue
            saved = state.path / "destination"
            phase = marker["phase"]
            try:
                if phase == "prior-tree-saved":
                    if destination.exists() or not saved.is_dir() or saved.is_symlink():
                        raise RoutineError("RESTORE_AMBIGUOUS")
                    marker["phase"] = "recovering-restore"
                    _write_publication_marker(state.path, marker)
                    os.replace(saved, destination)
                    _remove_publication_tree(state.path)
                    action = "restored"
                elif phase == "recovering-restore":
                    if saved.exists() and not destination.exists() and saved.is_dir() and not saved.is_symlink():
                        os.replace(saved, destination)
                    elif saved.exists() or not destination.is_dir() or destination.is_symlink():
                        raise RoutineError("RESTORE_AMBIGUOUS")
                    _remove_publication_tree(state.path)
                    action = "restored"
                elif phase in {"staged-installed", "committed"}:
                    if not destination.is_dir() or destination.is_symlink():
                        raise RoutineError("FINISH_AMBIGUOUS")
                    _remove_publication_tree(state.path)
                    action = "finished"
                elif phase == "prepared":
                    raise RoutineError("RETIRE_AMBIGUOUS")
                else:
                    raise RoutineError("PHASE_UNKNOWN")
            except (OSError, RoutineError) as error:
                results.append(PublicationRecoveryResult(state.path, "report-only", str(error), before, before))
                continue
            after = _git_status_sha256(destination.parent)
            results.append(PublicationRecoveryResult(state.path, action, "OK", before, after))
        return tuple(results)
    finally:
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
        finally:
            os.close(lock_fd)
            if lock_acquired:
                try:
                    lock_path.unlink()
                except OSError:
                    pass
                pass
def publish_tree(staged: Path, destination: Path, managed_paths: Sequence[str] | None = None) -> None:
    """Publish a staged tree with durable destination-sibling crash markers."""
    staged = staged.resolve()
    destination = destination.resolve()
    if not staged.is_dir():
        raise RoutineError(f"staged tree does not exist: {staged}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix=PUBLICATION_PREFIX, dir=destination.parent))
    marker = _publication_marker(destination, staged, managed_paths)
    _write_publication_marker(backup, marker)
    moved: list[tuple[Path, Path]] = []
    rollback_complete = True
    installed: list[Path] = []
    try:
        if managed_paths is None:
            saved = backup / "destination"
            if destination.exists():
                os.replace(destination, saved)
                moved.append((saved, destination))
                marker["moved_paths"] = ["destination"]
                marker["phase"] = "prior-tree-saved"
                _write_publication_marker(backup, marker)
            if os.environ.get("KOSMIC_FAIL_STAGE") == "crash-after-backup":
                os._exit(86)
            if os.environ.get("KOSMIC_FAIL_STAGE") == "after-backup":
                raise OSError("injected publication failure after backup")
            os.replace(staged, destination)
            installed.append(destination)
            marker["installed_paths"] = ["destination"]
            marker["phase"] = "staged-installed"
            _write_publication_marker(backup, marker)
            if os.environ.get("KOSMIC_FAIL_STAGE") == "crash-after-installed":
                os._exit(87)
        else:
            for relative_text in sorted(set(managed_paths)):
                relative = Path(relative_text)
                if relative.is_absolute() or ".." in relative.parts:
                    raise RoutineError(f"invalid managed path: {relative_text}")
                source = staged / relative
                target = destination / relative
                if not source.exists():
                    raise RoutineError(f"missing staged managed path: {relative_text}")
                target.parent.mkdir(parents=True, exist_ok=True)
                saved = backup / relative
                if target.exists():
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(target, saved)
                    moved.append((saved, target))
                    marker["moved_paths"] = [*marker["moved_paths"], relative.as_posix()]
                    marker["phase"] = "prior-tree-saved"
                    _write_publication_marker(backup, marker)
                if os.environ.get("KOSMIC_FAIL_STAGE") == "after-backup":
                    raise OSError("injected publication failure after backup")
                if os.environ.get("KOSMIC_FAIL_STAGE") == "crash-after-backup":
                    os._exit(86)
                os.replace(source, target)
                installed.append(target)
                marker["installed_paths"] = [*marker["installed_paths"], relative.as_posix()]
                marker["phase"] = "staged-installed"
                if os.environ.get("KOSMIC_FAIL_STAGE") == "crash-after-installed":
                    os._exit(87)
                _write_publication_marker(backup, marker)
        marker["phase"] = "committed"
        _write_publication_marker(backup, marker)
    except Exception:
        for target in reversed(installed):
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
            else:
                target.unlink(missing_ok=True)
        for saved, target in reversed(moved):
            target.parent.mkdir(parents=True, exist_ok=True)
            if saved.exists():
                try:
                    os.replace(saved, target)
                except OSError:
                    rollback_complete = False
                    raise
        raise
    finally:
        if rollback_complete:
            shutil.rmtree(backup, ignore_errors=True)
KOSMIC_ROUTINES = [
    {
        "id": "kosmic/atomic-publish-tree",
        "symbol": "publish_tree",
        "summary": "Publish a staged tree atomically with complete rollback",
        "owner": "hexu",
        "deterministic": True,
        "offline": True,
        "side_effects": ["filesystem"],
        "tests": [
            "tests/test_kosmic_routines.py::RoutineRegistryTest.test_publish_tree_restores_destination_after_failure",
            "tests/test_project_skills_cli.py::ProjectionCliTest.test_publication_failure_preserves_previous_pair",
            "tests/test_shared_library.py::SharedLibraryTest.test_generation_rollback_preserves_previous_artifacts",
        ],
        "callers": [
            "python:kosmic_project_skills:generate",
            "python:kosmic_project_skills:migrate_notes_bundle",
            "python:kosmic_project_skills:update_mathdocs",
            "python:kosmic_shared_library:generate_library",
        ],
        "procedures": [],
    }
]
