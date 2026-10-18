"""Execute pinned flat-spec migrations without changing work authority.

Plans are recomputed before publication. Each filesystem operation has durable
before/after images and an intent marker; recovery never overwrites unknown bytes.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

try:
    from . import kosmic_runs, kosmic_specs, kosmic_work
except ImportError:
    import kosmic_runs
    import kosmic_specs
    import kosmic_work

PLAN_SCHEMA = "kosmic.subproject-migration-plan/2"
TRANSACTION_SCHEMA = "kosmic.subproject-migration-transaction/1"
RECEIPT_SCHEMA = "kosmic.subproject-migration-receipt/1"
DIGEST = re.compile(r"[0-9a-f]{64}\Z")


class MigrationError(RuntimeError):
    def __init__(self, code: str, detail: str) -> None:
        self.code, self.detail = code, detail
        super().__init__(f"{code}: {detail}")


def _fail(condition: bool, code: str, detail: str) -> None:
    if condition:
        raise MigrationError(code, detail)


def _hash(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def _digest(plan: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps({k: v for k, v in plan.items() if k != "digest"},
                                    sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _parts(relative: str) -> tuple[str, ...]:
    _fail(not isinstance(relative, str) or not relative or "\\" in relative,
          "MIGRATION_PATH_UNSAFE", repr(relative))
    parts = tuple(relative.split("/"))
    _fail(any(part in ("", ".", "..") for part in parts),
          "MIGRATION_PATH_UNSAFE", relative)
    return parts


def _parent(root: Path, relative: str, *, create: bool = False) -> tuple[int, str]:
    parts = _parts(relative)
    absolute_root = Path(os.path.abspath(root))
    fd = os.open(absolute_root.anchor, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in absolute_root.parts[1:]:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        for part in parts[:-1]:
            if create:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                    os.fsync(fd)
                except FileExistsError:
                    pass
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = nxt
        return fd, parts[-1]
    except BaseException:
        os.close(fd)
        raise


def _read(root: Path, relative: str) -> bytes | None:
    try:
        fd, name = _parent(root, relative)
        try:
            child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            try:
                _fail(not stat.S_ISREG(os.fstat(child).st_mode), "MIGRATION_PATH_UNSAFE", relative)
                with os.fdopen(child, "rb") as stream:
                    child = -1
                    return stream.read()
            finally:
                if child >= 0:
                    os.close(child)
        finally:
            os.close(fd)
    except FileNotFoundError:
        return None
    except OSError as error:
        raise MigrationError("MIGRATION_PATH_UNSAFE", f"{root / relative}: {error.strerror}") from error


def _mode(root: Path, relative: str) -> int:
    try:
        fd, name = _parent(root, relative)
        try:
            info = os.stat(name, dir_fd=fd, follow_symlinks=False)
            _fail(not stat.S_ISREG(info.st_mode), "MIGRATION_PATH_UNSAFE", relative)
            return stat.S_IMODE(info.st_mode)
        finally:
            os.close(fd)
    except FileNotFoundError:
        return 0o600


def _write(root: Path, relative: str, data: bytes, *, exclusive: bool = False,
           mode: int = 0o600) -> None:
    fd = -1
    temporary = ".migration-" + os.urandom(12).hex()
    try:
        fd, name = _parent(root, relative, create=True)
        child = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                        mode, dir_fd=fd)
        os.fchmod(child, mode)
        with os.fdopen(child, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if exclusive:
            os.link(temporary, name, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
            os.unlink(temporary, dir_fd=fd)
        else:
            os.replace(temporary, name, src_dir_fd=fd, dst_dir_fd=fd)
        os.fsync(fd)
    except FileExistsError as error:
        raise MigrationError("MIGRATION_TARGET_COLLISION", str(root / relative)) from error
    except OSError as error:
        raise MigrationError("MIGRATION_WRITE_FAILED", f"{root / relative}: {error.strerror}") from error
    finally:
        if fd >= 0:
            try:
                os.unlink(temporary, dir_fd=fd)
            except FileNotFoundError:
                pass
            os.close(fd)


def _delete(root: Path, relative: str) -> None:
    fd, name = _parent(root, relative)
    try:
        os.unlink(name, dir_fd=fd)
        os.fsync(fd)
    finally:
        os.close(fd)


def _unique_json(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        _fail(key in result, "MIGRATION_PLAN_INVALID", f"duplicate JSON key {key!r}")
        result[key] = value
    return result


def _parse(data: bytes | None, detail: str) -> dict[str, Any]:
    _fail(data is None, "MIGRATION_PLAN_INVALID", f"missing {detail}")
    try:
        result = json.loads(data.decode("utf-8"), object_pairs_hook=_unique_json)
    except (ValueError, UnicodeError) as error:
        raise MigrationError("MIGRATION_PLAN_INVALID", f"{detail}: {error}") from error
    _fail(not isinstance(result, dict), "MIGRATION_PLAN_INVALID", detail)
    return result


def _absolute_file(path: Path) -> tuple[Path, str]:
    absolute = Path(os.path.abspath(Path(path).expanduser()))
    return Path(absolute.anchor), "/".join(absolute.parts[1:])


def _load_plan(path: Path, root: Path, approved_digest: str) -> dict[str, Any]:
    base, relative = _absolute_file(path)
    plan = _parse(_read(base, relative), str(path))
    _fail(plan.get("schema") != PLAN_SCHEMA, "MIGRATION_PLAN_INVALID",
          "regenerate the plan with the current migrate-subprojects-plan command")
    _fail(not isinstance(approved_digest, str) or not DIGEST.fullmatch(approved_digest)
          or plan.get("digest") != approved_digest or _digest(plan) != approved_digest,
          "MIGRATION_APPROVAL_MISMATCH", "the approved digest must match the complete saved plan")
    _fail(plan.get("project_root") != str(root), "MIGRATION_PROJECT_MISMATCH", str(root))
    _fail(not isinstance(plan.get("inputs"), dict) or not isinstance(plan.get("outputs"), list)
          or not isinstance(plan.get("deletions"), list) or not isinstance(plan.get("assignments"), dict),
          "MIGRATION_PLAN_INVALID", "missing complete inputs, assignments or operations")
    _fail(not isinstance(plan.get("project_id"), str)
          or not kosmic_specs.SLUG.fullmatch(plan["project_id"])
          or not isinstance(plan.get("records"), list)
          or not isinstance(plan.get("rewrites"), list)
          or not isinstance(plan.get("status_binding"), dict)
          or plan["status_binding"].get("disposition") not in ("bound", "unbound"),
          "MIGRATION_PLAN_INVALID", "missing Project identity, records or STATUS disposition")
    _fail(any(not isinstance(row, dict) or not all(isinstance(row.get(key), str)
              for key in ("source", "destination", "qualified_id")) for row in plan["records"]),
          "MIGRATION_PLAN_INVALID", "invalid record mapping")
    binding = plan["status_binding"]
    if binding["disposition"] == "bound":
        _fail(not isinstance(binding.get("content"), str)
              or _hash(binding["content"].encode()) != binding.get("after_sha256"),
              "MIGRATION_PLAN_INVALID", "bound STATUS requires exact reviewed bytes and hash")
    for path_text, value in plan["inputs"].items():
        _parts(path_text)
        _fail(not isinstance(value, str) or not DIGEST.fullmatch(value),
              "MIGRATION_PLAN_INVALID", f"invalid input hash: {path_text}")
    seen: set[str] = set()
    for row in [*plan["outputs"], *plan["deletions"]]:
        _fail(not isinstance(row, dict), "MIGRATION_PLAN_INVALID", "invalid operation")
        path_text = row.get("path")
        parts = _parts(path_text)
        _fail(path_text in seen or parts[0] in (".kosmic", ".git", ".tmp"),
              "MIGRATION_PLAN_INVALID", f"duplicate or reserved operation: {path_text}")
        seen.add(path_text)
        before = row.get("before_sha256")
        _fail(before is not None and (not isinstance(before, str) or not DIGEST.fullmatch(before)),
              "MIGRATION_PLAN_INVALID", f"invalid before hash: {path_text}")
        if "content" in row:
            _fail(not isinstance(row["content"], str) or _hash(row["content"].encode()) != row.get("after_sha256"),
                  "MIGRATION_PLAN_INVALID", f"invalid candidate bytes: {path_text}")
    _fail(any(not isinstance(row.get("content"), str) for row in plan["outputs"])
          or any(not isinstance(row.get("before_sha256"), str) or "content" in row
                 for row in plan["deletions"]),
          "MIGRATION_PLAN_INVALID", "outputs require content and deletions require source hashes")
    _fail(bool(plan.get("ambiguities")), "MIGRATION_AMBIGUOUS",
          "resolve every ambiguity with explicit assignments and regenerate the plan")
    return plan


def save_migration_plan(plan: dict[str, Any], path: Path) -> None:
    """Save one explicit planning output, exclusively and without symlink traversal."""
    base, relative = _absolute_file(path)
    _write(base, relative, _json_bytes(plan), exclusive=True)


def _authority(root: Path, reference: str, project_id: str):
    try:
        record = kosmic_work.resolve_work_record(root, reference, kinds=("quick-task",))
    except (kosmic_work.WorkdirError, kosmic_specs.SpecError) as error:
        raise MigrationError("MIGRATION_AUTHORITY_DENIED", str(error)) from error
    relative = record.path.relative_to(root).as_posix()
    accepted = {record.qualified_id, relative, str(record.path), record.local_id}
    _fail(reference not in accepted or record.project_id != project_id or record.subproject_id is not None
          or not relative.startswith("specs/quick-tasks/")
          or not kosmic_specs.SLUG.fullmatch(record.local_id),
          "MIGRATION_AUTHORITY_DENIED", "use this Project's approved canonical shared Quick Task")
    return record


def _transaction_path(digest: str) -> str:
    return f".kosmic/migrations/{digest}/transaction.json"


def _receipt_path(digest: str) -> str:
    return f".kosmic/migrations/{digest}/receipt.json"


def _check_other_transactions(root: Path, digest: str) -> None:
    try:
        fd, name = _parent(root, ".kosmic/migrations/item")
    except FileNotFoundError:
        return
    try:
        for candidate in sorted(os.listdir(fd)):
            _fail(not DIGEST.fullmatch(candidate), "MIGRATION_TRANSACTION_CONFLICT",
                  f"unexpected migration store entry {candidate!r}")
            if candidate == digest:
                continue
            journal = _parse(_read(root, _transaction_path(candidate)), candidate)
            _fail(journal.get("phase") not in ("committed", "rolled-back")
                  or (journal.get("phase") == "committed"
                      and _read(root, _receipt_path(candidate)) is None),
                  "MIGRATION_RECOVERY_REQUIRED", f"recover incomplete plan {candidate} first")
    finally:
        os.close(fd)


def _location(root: Path, plan: dict[str, Any], operation: dict[str, Any]) -> tuple[Path, str]:
    if operation["scope"] == "project":
        return root, operation["path"]
    _fail(operation["scope"] != "status" or operation["path"] != "STATUS.md",
          "MIGRATION_TRANSACTION_INVALID", "invalid external operation")
    binding = plan.get("status_binding", {})
    path = binding.get("path")
    _fail(not isinstance(path, str) or Path(path).name != "STATUS.md",
          "MIGRATION_TRANSACTION_INVALID", "invalid STATUS target")
    return Path(path).parent, "STATUS.md"


def _decode(value: str | None) -> bytes | None:
    try:
        return None if value is None else base64.b64decode(value, validate=True)
    except (ValueError, TypeError) as error:
        raise MigrationError("MIGRATION_TRANSACTION_INVALID", "invalid saved bytes") from error


def _encode(value: bytes | None) -> str | None:
    return None if value is None else base64.b64encode(value).decode("ascii")


def _operation(scope: str, path: str, before: bytes | None, after: bytes | None,
               mode: int) -> dict[str, Any]:
    return {"scope": scope, "path": path, "before": _encode(before), "after": _encode(after),
            "before_sha256": _hash(before), "after_sha256": _hash(after), "mode": mode, "state": "pending"}


def _input_snapshot(root: Path, plan: dict[str, Any]) -> dict[str, str]:
    snapshot: dict[str, str] = {}
    for relative, expected in sorted(plan["inputs"].items()):
        raw = _read(root, relative)
        _fail(_hash(raw) != expected, "MIGRATION_INPUT_DRIFT", f"regenerate the plan: {relative}")
        snapshot[relative] = _encode(raw)
    return snapshot


def _candidate(root: Path, plan: dict[str, Any], inputs: dict[str, str], record):
    try:
        handle = kosmic_runs.begin_run(root, "subproject-migration-candidate", project_root=root,
            provenance={"project_id": record.project_id, "governing_record": record.qualified_id})
    except (kosmic_runs.RunError, kosmic_runs.RunRootError) as error:
        raise MigrationError("MIGRATION_RUN_FAILED", str(error)) from error
    stage = handle.path / "scratch" / "candidate"
    stage.mkdir(mode=0o700)
    try:
        for relative, raw in inputs.items():
            _write(stage, relative, _decode(raw), exclusive=True)
        for row in plan["deletions"]:
            _delete(stage, row["path"])
        for row in plan["outputs"]:
            _write(stage, row["path"], row["content"].encode())
        catalog = kosmic_specs.SpecCatalog(stage)
        catalog.validate()
        kosmic_specs.validate_migration_links(stage, plan)
        return handle, stage, catalog
    except BaseException:
        kosmic_runs.finish_run(handle.handle_file, "failed", "migration candidate rejected")
        raise


def _status_operation(root: Path, plan: dict[str, Any], catalog) -> dict[str, Any] | None:
    binding = plan.get("status_binding", {})
    if binding.get("disposition") == "unbound":
        return None
    _fail(binding.get("disposition") != "bound", "MIGRATION_PLAN_INVALID", "missing STATUS disposition")
    try:
        if __package__:
            from . import kosmic_project_skills as cli
        else:
            import kosmic_project_skills as cli
        project = cli.load_project(root)
        bound = cli.resolve_status_root(project.status_root, project=root)
        _fail(str(bound / "STATUS.md") != binding.get("path"),
              "MIGRATION_INPUT_DRIFT", "STATUS binding changed")
        raw = _read(bound, "STATUS.md")
        _fail(_hash(raw) != binding.get("before_sha256"), "MIGRATION_INPUT_DRIFT", "STATUS.md changed")
        content = cli.render_status(project, binding.get("head", "unknown"), catalog=catalog)
        _fail(content != binding["content"].encode(), "MIGRATION_INPUT_DRIFT",
              "staged STATUS differs from the reviewed plan; regenerate it")
        return _operation("status", "STATUS.md", raw, content, _mode(bound, "STATUS.md"))
    except kosmic_specs.SpecError as error:
        raise MigrationError("MIGRATION_CANDIDATE_INVALID", str(error)) from error


def _operations(root: Path, plan: dict[str, Any], catalog) -> list[dict[str, Any]]:
    result = []
    for row in plan["outputs"]:
        raw = _read(root, row["path"])
        _fail(_hash(raw) != row.get("before_sha256"), "MIGRATION_TARGET_COLLISION", row["path"])
        after = row["content"].encode()
        if after != raw:
            result.append(_operation("project", row["path"], raw, after, _mode(root, row["path"])))
    for row in plan["deletions"]:
        raw = _read(root, row["path"])
        _fail(_hash(raw) != row["before_sha256"], "MIGRATION_INPUT_DRIFT", row["path"])
        result.append(_operation("project", row["path"], raw, None, _mode(root, row["path"])))
    status_op = _status_operation(root, plan, catalog)
    if status_op is not None:
        result.append(status_op)
    return result


def _missing_directories(root: Path, plan: dict[str, Any],
                         operations: list[dict[str, Any]]) -> list[dict[str, str]]:
    missing: set[tuple[str, str]] = set()
    for op in operations:
        base, relative = _location(root, plan, op)
        parts = _parts(relative)
        for count in range(1, len(parts)):
            directory = "/".join(parts[:count])
            try:
                fd, _ = _parent(base, directory + "/probe")
                os.close(fd)
            except FileNotFoundError:
                missing.add((op["scope"], directory))
    return [{"scope": scope, "path": path} for scope, path in sorted(missing)]


def _remove_created_directories(root: Path, journal: dict[str, Any]) -> None:
    allowed = {(op["scope"], "/".join(_parts(op["path"])[:count]))
               for op in journal["operations"]
               for count in range(1, len(_parts(op["path"])))}
    directories = journal.get("created_directories")
    _fail(not isinstance(directories, list), "MIGRATION_TRANSACTION_INVALID", "missing directory inventory")
    for row in sorted(directories, key=lambda item: item["path"].count("/"), reverse=True):
        _fail((row.get("scope"), row.get("path")) not in allowed,
              "MIGRATION_TRANSACTION_INVALID", "unapproved directory cleanup")
        base = root if row["scope"] == "project" else Path(journal["plan"]["status_binding"]["path"]).parent
        fd = -1
        try:
            fd, name = _parent(base, row["path"])
            os.rmdir(name, dir_fd=fd)
            os.fsync(fd)
        except FileNotFoundError:
            pass
        except OSError as error:
            raise MigrationError("MIGRATION_TRANSACTION_CONFLICT",
                                 f"cannot remove transaction-created directory {base / row['path']}: {error.strerror}") from error
        finally:
            if fd >= 0:
                os.close(fd)


def _persist(root: Path, journal: dict[str, Any]) -> None:
    _write(root, _transaction_path(journal["digest"]), _json_bytes(journal))


def _inject(point: str) -> None:
    selected = os.environ.get("KOSMIC_MIGRATION_FAIL_STAGE")
    if selected == "crash-" + point:
        os._exit(86)
    if selected == point:
        raise MigrationError("MIGRATION_INJECTED_FAILURE", point)


def _check_state(root: Path, journal: dict[str, Any], *, final: bool = False,
                 verify_inputs: bool = True) -> None:
    if verify_inputs:
        touched = {op["path"] for op in journal["operations"] if op["scope"] == "project"}
        for relative, expected in journal["plan"]["inputs"].items():
            if relative not in touched:
                _fail(_hash(_read(root, relative)) != expected, "MIGRATION_TRANSACTION_CONFLICT", relative)
    for op in journal["operations"]:
        base, relative = _location(root, journal["plan"], op)
        actual = _hash(_read(base, relative))
        allowed = {op["after_sha256"]} if final else {op["before_sha256"], op["after_sha256"]}
        _fail(actual not in allowed, "MIGRATION_TRANSACTION_CONFLICT", str(base / relative))


def _rollback(root: Path, journal: dict[str, Any]) -> None:
    _check_state(root, journal)
    journal["phase"] = "rolling-back"
    _persist(root, journal)
    for op in reversed(journal["operations"]):
        base, relative = _location(root, journal["plan"], op)
        current = _hash(_read(base, relative))
        if current != op["before_sha256"]:
            before = _decode(op["before"])
            if before is None:
                _delete(base, relative)
            else:
                _write(base, relative, before, mode=op["mode"])
        op["state"] = "restored"
        _persist(root, journal)
    _remove_created_directories(root, journal)
    journal["phase"] = "rolled-back"
    _persist(root, journal)


def _receipt(journal: dict[str, Any]) -> dict[str, Any]:
    plan = journal["plan"]
    return {"schema": RECEIPT_SCHEMA, "status": "successful", "project_id": plan["project_id"],
            "project_root": plan["project_root"], "plan_digest": plan["digest"],
            "work_record": journal["work_record"],
            "inputs": dict(sorted(plan["inputs"].items())),
            "mapping": [{key: row[key] for key in ("source", "destination", "qualified_id")}
                        for row in plan["records"]],
            "outputs": [{key: op[key] for key in ("scope", "path", "before_sha256", "after_sha256")}
                        for op in journal["operations"]],
            "status_disposition": plan["status_binding"]["disposition"],
            "proposal_rechecks": [{key: row.get(key) for key in
                ("source", "fingerprint_before", "fingerprint_after", "classification")}
                for row in plan["rewrites"] if row.get("fingerprint_recheck_required") ]}


def _finalize_candidate(root: Path, journal: dict[str, Any], outcome: str) -> None:
    """End the transaction's own run, including a holder left by a crashed CLI."""
    candidate = journal["candidate_run"]
    base = kosmic_runs.managed_run_root_path(root)
    handle_path = base / "handles" / candidate["handle_name"]
    handle = _parse(_read(base, f"handles/{candidate['handle_name']}"), "candidate run handle")
    _fail(handle.get("run_id") != candidate["run_id"],
          "MIGRATION_TRANSACTION_INVALID", "candidate handle identifies another run")
    if handle.get("kind") == "receipt":
        _fail(handle.get("project_id") != journal["plan"]["project_id"]
              or handle.get("governing_record") != journal["work_record"],
              "MIGRATION_TRANSACTION_INVALID", "candidate receipt belongs to another record")
    else:
        manifest = _parse(_read(base, f"runs/{candidate['run_id']}/RUN.json"), "candidate run manifest")
        try:
            kosmic_runs.validate_run_manifest(manifest)
        except kosmic_runs.RunError as error:
            raise MigrationError("MIGRATION_RUN_FAILED", str(error)) from error
        _fail(manifest.get("run_id") != candidate["run_id"]
              or manifest.get("project_id") != journal["plan"]["project_id"]
              or manifest.get("governing_record") != journal["work_record"]
              or manifest.get("purpose") != "subproject-migration-candidate"
              or manifest.get("worktree_root") != str(base.parent.parent),
              "MIGRATION_TRANSACTION_INVALID", "candidate run belongs to another operation")
    try:
        kosmic_runs.finish_run(handle_path, outcome, "migration recovered")
    except (kosmic_runs.RunError, kosmic_runs.RunRootError) as error:
        raise MigrationError("MIGRATION_RUN_FAILED", str(error)) from error


def _finish(root: Path, journal: dict[str, Any]) -> dict[str, Any]:
    _check_state(root, journal, final=True)
    catalog = kosmic_specs.SpecCatalog(root)
    catalog.validate()
    result = _receipt(journal)
    journal["phase"] = "committed"
    _persist(root, journal)
    _inject("before-receipt")
    _write(root, _receipt_path(journal["digest"]), _json_bytes(result), exclusive=True)
    return result


def _validate_journal(journal: dict[str, Any], plan: dict[str, Any]) -> None:
    _fail(journal.get("schema") != TRANSACTION_SCHEMA or journal.get("plan") != plan
          or journal.get("digest") != plan["digest"] or not isinstance(journal.get("operations"), list)
          or not isinstance(journal.get("input_bytes"), dict),
          "MIGRATION_TRANSACTION_INVALID", "transaction does not match the approved plan")
    _fail(journal.get("phase") not in ("prepared", "applying", "rolling-back", "rolled-back", "committed")
          or not isinstance(journal.get("created_directories"), list)
          or not isinstance(journal.get("work_record"), str)
          or not journal["work_record"].startswith(plan["project_id"] + "/quick-task/"),
          "MIGRATION_TRANSACTION_INVALID", "invalid transaction state or work identity")
    candidate = journal.get("candidate_run")
    _fail(not isinstance(candidate, dict) or not isinstance(candidate.get("run_id"), str)
          or not kosmic_runs.RUN_ID_RE.fullmatch(candidate["run_id"])
          or not isinstance(candidate.get("handle_name"), str)
          or re.fullmatch(r"[0-9a-f]{32}", candidate["handle_name"]) is None,
          "MIGRATION_TRANSACTION_INVALID", "invalid candidate run identity")
    _fail(set(journal["input_bytes"]) != set(plan["inputs"]),
          "MIGRATION_TRANSACTION_INVALID", "incomplete saved inputs")
    for relative, encoded in journal["input_bytes"].items():
        _fail(_hash(_decode(encoded)) != plan["inputs"][relative],
              "MIGRATION_TRANSACTION_INVALID", relative)
    intended = {("project", row["path"]): row for row in [*plan["outputs"], *plan["deletions"]]}
    seen = set()
    for op in journal["operations"]:
        _fail(not isinstance(op, dict), "MIGRATION_TRANSACTION_INVALID", "invalid operation")
        key = (op.get("scope"), op.get("path"))
        _fail(key in seen, "MIGRATION_TRANSACTION_INVALID", "duplicate operation")
        seen.add(key)
        if key == ("status", "STATUS.md"):
            binding = plan["status_binding"]
            _fail(binding["disposition"] != "bound"
                  or op.get("before_sha256") != binding.get("before_sha256")
                  or op.get("after_sha256") != binding.get("after_sha256")
                  or _decode(op.get("after")) != binding["content"].encode(),
                  "MIGRATION_TRANSACTION_INVALID", "STATUS differs from the approved plan")
        else:
            row = intended.pop(key, None)
            _fail(row is None or op.get("before_sha256") != row.get("before_sha256")
                  or op.get("after_sha256") != row.get("after_sha256"),
                  "MIGRATION_TRANSACTION_INVALID", str(key))
            _fail(_decode(op.get("after")) != (row["content"].encode() if "content" in row else None),
                  "MIGRATION_TRANSACTION_INVALID", str(key))
        _fail(_hash(_decode(op.get("before"))) != op.get("before_sha256")
              or _hash(_decode(op.get("after"))) != op.get("after_sha256")
              or op.get("state") not in ("pending", "intent", "applied", "restored")
              or not isinstance(op.get("mode"), int) or not 0 <= op["mode"] <= 0o777,
              "MIGRATION_TRANSACTION_INVALID", str(key))
    _fail(any(row.get("before_sha256") != row.get("after_sha256") for row in intended.values()),
          "MIGRATION_TRANSACTION_INVALID", "missing operations")
    _fail(plan["status_binding"]["disposition"] == "bound" and ("status", "STATUS.md") not in seen,
          "MIGRATION_TRANSACTION_INVALID", "missing STATUS operation")
    allowed = {(op["scope"], "/".join(_parts(op["path"])[:count]))
               for op in journal["operations"] for count in range(1, len(_parts(op["path"])))}
    directories = plan.get("directories")
    _fail(not isinstance(directories, list), "MIGRATION_TRANSACTION_INVALID", "missing planned directories")
    expected = [{"scope": scope, "path": path} for scope, path in sorted(allowed)
                if scope == "project" and path not in directories]
    _fail(journal["created_directories"] != expected,
          "MIGRATION_TRANSACTION_INVALID", "directory cleanup differs from the approved pre-state")


def _existing_result(root: Path, plan: dict[str, Any]) -> dict[str, Any] | None:
    digest = plan["digest"]
    previous = _read(root, _transaction_path(digest))
    if previous is None:
        return None
    journal = _parse(previous, digest)
    _validate_journal(journal, plan)
    existing = _read(root, _receipt_path(digest))
    if existing is not None:
        receipt = _parse(existing, digest)
        _fail(receipt != _receipt(journal), "MIGRATION_TRANSACTION_INVALID", "receipt differs from transaction")
        _check_state(root, journal, final=True, verify_inputs=False)
        return receipt
    _fail(journal.get("phase") != "rolled-back", "MIGRATION_RECOVERY_REQUIRED",
          "run migrate-subprojects-recover for this exact plan before retrying")
    return None


def _recompute(root: Path, plan: dict[str, Any], fingerprint_fn: Any) -> None:
    for row in plan["outputs"]:
        actual = _hash(_read(root, row["path"]))
        _fail(actual != row["before_sha256"], "MIGRATION_TARGET_COLLISION"
              if row["before_sha256"] is None else "MIGRATION_INPUT_DRIFT", row["path"])
    try:
        current = kosmic_specs.migration_plan(root, work_record=plan.get("work_record"),
            assignments=plan["assignments"], fingerprint_fn=fingerprint_fn)
    except kosmic_specs.SpecError as error:
        raise MigrationError("MIGRATION_INPUT_DRIFT", str(error)) from error
    _fail(current != plan, "MIGRATION_INPUT_DRIFT",
          "inventory or candidate changed; regenerate and approve the plan")


def apply_migration(project_root: Path, plan_path: Path, approved_digest: str,
                    work_record: str, *, fingerprint_fn: Any = None) -> dict[str, Any]:
    """Apply an exact reviewed plan, or verify its already-completed receipt."""
    root = Path(project_root).expanduser().resolve()
    plan = _load_plan(plan_path, root, approved_digest)
    with kosmic_specs._creation_lock(root):
        record = _authority(root, work_record, plan["project_id"])
        _check_other_transactions(root, approved_digest)
        existing = _existing_result(root, plan)
        if existing is not None:
            return existing
        inputs = _input_snapshot(root, plan)
        _recompute(root, plan, fingerprint_fn)
    # begin_run forks a detached holder. It must never inherit the publication
    # lock: an interrupted parent would otherwise leave recovery deadlocked.
    handle, _, catalog = _candidate(root, plan, inputs, record)
    try:
        with kosmic_specs._creation_lock(root):
            record = _authority(root, work_record, plan["project_id"])
            _check_other_transactions(root, approved_digest)
            result = _existing_result(root, plan)
            if result is None:
                _input_snapshot(root, plan)
                _recompute(root, plan, fingerprint_fn)
                operations = _operations(root, plan, catalog)
                journal = {"schema": TRANSACTION_SCHEMA, "digest": approved_digest, "plan": plan,
                           "work_record": record.qualified_id, "input_bytes": inputs,
                           "operations": operations, "phase": "prepared",
                           "created_directories": _missing_directories(root, plan, operations),
                           "candidate_run": {"run_id": handle.run_id, "handle_name": handle.handle_file.name}}
                _persist(root, journal)
                try:
                    journal["phase"] = "applying"
                    _persist(root, journal)
                    for index, op in enumerate(operations):
                        base, relative = _location(root, plan, op)
                        _fail(_hash(_read(base, relative)) != op["before_sha256"],
                              "MIGRATION_TRANSACTION_CONFLICT", str(base / relative))
                        op["state"] = "intent"
                        _persist(root, journal)
                        _inject(f"after-intent:{index}")
                        after = _decode(op["after"])
                        if after is None:
                            _delete(base, relative)
                        else:
                            _write(base, relative, after, exclusive=op["before"] is None, mode=op["mode"])
                        _inject(f"after-write:{index}")
                        op["state"] = "applied"
                        _persist(root, journal)
                    result = _finish(root, journal)
                except BaseException:
                    if _read(root, _receipt_path(approved_digest)) is None:
                        _rollback(root, journal)
                    raise
    except BaseException:
        kosmic_runs.finish_run(handle.handle_file, "failed", "migration application failed")
        raise
    kosmic_runs.finish_run(handle.handle_file, "succeeded", "migration receipt verified")
    return result


def recover_migration(project_root: Path, plan_path: Path, approved_digest: str,
                      work_record: str) -> dict[str, Any]:
    """Recover only the approved transaction; unknown external changes are conflicts."""
    root = Path(project_root).expanduser().resolve()
    plan = _load_plan(plan_path, root, approved_digest)
    with kosmic_specs._creation_lock(root):
        _authority(root, work_record, plan["project_id"])
        journal = _parse(_read(root, _transaction_path(approved_digest)), approved_digest)
        _validate_journal(journal, plan)
        existing = _read(root, _receipt_path(approved_digest))
        if existing is not None:
            result = _parse(existing, approved_digest)
            _fail(result != _receipt(journal), "MIGRATION_TRANSACTION_INVALID",
                  "receipt differs from transaction")
            _check_state(root, journal, final=True, verify_inputs=False)
            _finalize_candidate(root, journal, "succeeded")
            return result
        _check_state(root, journal)
        complete = all(_hash(_read(*_location(root, plan, op))) == op["after_sha256"]
                       for op in journal["operations"])
        if complete:
            result = _finish(root, journal)
            _finalize_candidate(root, journal, "succeeded")
            return result
        _rollback(root, journal)
        _finalize_candidate(root, journal, "failed")
        return {"schema": TRANSACTION_SCHEMA, "status": "rolled-back",
                "project_id": plan["project_id"], "plan_digest": approved_digest,
                "work_record": journal["work_record"]}
