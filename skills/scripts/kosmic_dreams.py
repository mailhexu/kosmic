#!/usr/bin/env python3
"""Deterministic Dream harvest, validation, and publication mechanics.

Dream Reflection (Epic 26) splits previous-day reflection into a deterministic
collector (this module), bounded agent judgment (Task D), and publisher-owned
validation/publication.  The collector computes the observable target-day
union from Git history, Markdown frontmatter, and enumerated dirty state; it
never performs judgment and never writes vault content.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import unicodedata
from datetime import date as date_cls
from datetime import datetime, time, timedelta, timezone as dt_timezone
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

try:
    from . import kosmic_runs
    from .kosmic_routines import publish_tree
except ImportError:  # direct script import
    import kosmic_runs
    from kosmic_routines import publish_tree

HARVEST_SCHEMA = "kosmic.dream.harvest/1"
RECORD_SCHEMA = "kosmic.dream.record/1"
CANDIDATE_SCHEMA = "kosmic.dream.candidate/1"
IDEAS_INPUT_SCHEMA = "kosmic.dream.ideas/1"

DREAMS_DIR_NAME = "dreams"
RECORD_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
PROJECTS_PREFIX = "Projects/"
SKILLS_PREFIX = "Skills/"
EXCLUDED_SURFACES = ("dreams/",)
DREAMS_EMPTY_SHA256 = hashlib.sha256(b"kosmic.dreams.empty/1").hexdigest()
NULL_BLOB = "0" * 40
GIT_STATUS_TO_CHANGE = {
    "A": "created",
    "C": "created",
    "M": "modified",
    "T": "modified",
    "D": "deleted",
    "R": "renamed",
}


class DreamError(RuntimeError):
    """A Dream mechanic failed closed with a stable machine code."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


def _nfc(value: Any) -> Any:
    if isinstance(value, str):
        return unicodedata.normalize("NFC", value)
    if isinstance(value, list):
        return [_nfc(item) for item in value]
    if isinstance(value, dict):
        return { _nfc(key): _nfc(item) for key, item in value.items() }
    return value


def canonical_json(value: Any) -> bytes:
    """Serialize a harvest payload to canonical deterministic bytes."""
    return (
        json.dumps(_nfc(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse a simple YAML frontmatter block of scalar ``key: value`` lines."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if not stripped or stripped.startswith("#"):
            continue
        key, separator, value = stripped.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def resolve_timezone(explicit: str | None) -> str:
    """Resolve the effective IANA timezone, failing closed when unknown."""
    if explicit:
        try:
            ZoneInfo(explicit)
        except (ZoneInfoNotFoundError, ValueError, KeyError) as error:
            raise DreamError("TIMEZONE_INVALID", explicit) from error
        return explicit
    candidate = Path("/etc/localtime").resolve()
    parts = candidate.parts
    if "zoneinfo" in parts:
        name = "/".join(parts[parts.index("zoneinfo") + 1 :])
        if name:
            try:
                ZoneInfo(name)
                return name
            except (ZoneInfoNotFoundError, ValueError, KeyError):
                pass
    raise DreamError("TIMEZONE_UNRESOLVED", "host IANA timezone could not be resolved; pass --timezone")


def _validate_date(value: str) -> str:
    if not RECORD_DATE_RE.fullmatch(value):
        raise DreamError("DATE_INVALID", value)
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as error:
        raise DreamError("DATE_INVALID", value) from error
    return value


def default_date(zone_name: str) -> str:
    """Previous calendar date in the resolved timezone."""
    today = datetime.now(ZoneInfo(zone_name)).date()
    return (today - timedelta(days=1)).isoformat()


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=str(repo), capture_output=True, text=True
    )
    if completed.returncode != 0:
        raise DreamError("GIT_FAILED", f"git {' '.join(args[:3])}: {completed.stderr.strip()[:200]}")
    return completed.stdout


def _repo_root(vault: Path) -> Path:
    vault = vault.expanduser().resolve()
    if not vault.is_dir():
        raise DreamError("VAULT_MISSING", str(vault))
    try:
        root_text = _git(vault, "rev-parse", "--show-toplevel").strip()
    except DreamError as error:
        raise DreamError("NO_REPOSITORY", str(vault)) from error
    return Path(root_text).resolve()


def _vault_relative(repo: Path, vault: Path, path_text: str) -> str | None:
    """Convert a repo-relative path to a vault-relative path, else None."""
    path = Path(path_text)
    try:
        relative = path.relative_to(vault)
    except ValueError:
        return None
    text = relative.as_posix()
    if not text or text == ".":
        return None
    return text


def _authoritative(text: str) -> bool:
    if any(text.startswith(prefix) for prefix in EXCLUDED_SURFACES):
        return False
    if text.startswith(PROJECTS_PREFIX) or text.startswith(SKILLS_PREFIX):
        return True
    return "/" not in text and text.endswith(".md")


def _project_of(text: str) -> str | None:
    if text.startswith(PROJECTS_PREFIX):
        remainder = text[len(PROJECTS_PREFIX) :]
        name, separator, _ = remainder.partition("/")
        if separator:
            return name or None
    return None


def _window_commits(repo: Path, zone_name: str, date_text: str) -> tuple[list[tuple[str, str]], bool]:
    zone = ZoneInfo(zone_name)
    start = datetime.combine(date_cls.fromisoformat(date_text), time.min, tzinfo=zone).astimezone(
        dt_timezone.utc
    )
    end = start + timedelta(days=1)
    log = _git(
        repo,
        "log",
        f"--since={start.isoformat()}",
        f"--until={end.isoformat()}",
        "--format=%H%x00%cI",
        "HEAD",
    )
    rows: list[tuple[str, str]] = []
    for line in log.splitlines():
        if not line.strip():
            continue
        sha, _, stamp = line.partition("\x00")
        try:
            instant = datetime.fromisoformat(stamp).astimezone(dt_timezone.utc)
        except ValueError:
            continue
        if start <= instant < end:
            rows.append((sha, instant.isoformat()))
    rows.sort(key=lambda row: (row[1], row[0]))
    shallow = _git(repo, "rev-parse", "--is-shallow-repository").strip() == "true"
    return [(sha, stamp) for sha, stamp in rows], shallow


def _diff_entries(repo: Path, commit: str) -> list[dict[str, Any]]:
    """Parse ``git diff-tree --raw`` into typed before/after observations."""
    raw = _git(
        repo,
        "diff-tree",
        "--no-commit-id",
        "--raw",
        "-r",
        "-M90%",
        "--root",
        "--first-parent",
        "-z",
        commit,
    )
    tokens = raw.split("\0")
    entries: list[dict[str, Any]] = []
    index = 0
    while index < len(tokens):
        meta = tokens[index]
        if not meta.startswith(":"):
            break
        index += 1
        fields = meta[1:].split(" ")
        if len(fields) < 5:
            continue
        old_blob, new_blob, letter = fields[2], fields[3], fields[4][0]
        if index >= len(tokens):
            break
        first_path = tokens[index]
        index += 1
        old_path = first_path
        new_path = first_path
        if letter == "R" or letter == "C":
            if index < len(tokens):
                new_path = tokens[index]
                index += 1
        entries.append(
            {
                "old_path": old_path,
                "new_path": new_path,
                "status": GIT_STATUS_TO_CHANGE.get(letter, "modified"),
                "old_blob": old_blob if old_blob != NULL_BLOB else None,
                "new_blob": new_blob if new_blob != NULL_BLOB else None,
                "origins": ["git"],
            }
        )
    return entries


def _dirty_state(repo: Path) -> dict[str, dict[str, Any]]:
    """Enumerate porcelain-v2 entries as path → dirty classification."""
    raw = _git(repo, "status", "--porcelain=v2", "-z")
    tokens = raw.split("\0")
    state: dict[str, dict[str, Any]] = {}
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if not token:
            index += 1
            continue
        if token.startswith("? "):
            path_text = token[2:]
            index += 1
            state[path_text] = {"classes": {"untracked"}, "x": "?", "y": "?"}
            continue
        if token.startswith("u "):
            fields = token.split(" ")
            path_text = fields[-1]
            index += 1
            state[path_text] = {"classes": {"unstaged"}, "x": "U", "y": "U"}
            continue
        if token.startswith(("1 ", "2 ")):
            fields = token.split(" ")
            xy = fields[1]
            path_text = fields[-1]
            index += 1
            if token.startswith("2 "):
                path_text = tokens[index]
                index += 1
            classes: set[str] = set()
            x, y = xy[0], xy[1]
            if x != ".":
                classes.add("staged")
            if y != ".":
                classes.add("unstaged")
            if "R" in xy:
                classes.add("renamed")
            if "D" in xy:
                classes.add("deleted")
            state[path_text] = {"classes": classes, "x": x, "y": y}
            continue
        index += 1
    return state


def _vault_markdown(vault: Path) -> list[str]:
    """List vault-relative Markdown paths in the authoritative surfaces."""
    results: list[str] = []
    for path in sorted(vault.rglob("*.md")):
        relative = path.relative_to(vault).as_posix()
        if relative.split("/", 1)[0].startswith("."):
            continue
        if _authoritative(relative):
            results.append(relative)
    return results


def dreams_tree_digest(vault: Path) -> str:
    """Digest the canonical dreams tree; stable empty sentinel when absent."""
    dreams = vault / DREAMS_DIR_NAME
    if not dreams.is_dir():
        return DREAMS_EMPTY_SHA256
    digest = hashlib.sha256()
    for path in sorted(p for p in dreams.rglob("*") if p.is_file()):
        relative = path.relative_to(dreams).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()
def _section_text(text: str, heading: str) -> str:
    """Return the body under an ``## heading`` section, empty when absent."""
    lines = text.splitlines()
    collecting = False
    collected: list[str] = []
    for line in lines:
        if line.startswith("## "):
            if collecting:
                break
            collecting = line[3:].strip() == heading
            continue
        if collecting:
            collected.append(line)
    return "\n".join(collected).strip()

def _blob_bytes(repo: Path, sha: str) -> bytes:
    completed = subprocess.run(
        ["git", "cat-file", "blob", sha], cwd=str(repo), capture_output=True
    )
    if completed.returncode != 0:
        raise DreamError("BLOB_MISSING", sha)
    return completed.stdout


def _head_blob_id(repo: Path, repo_path: str) -> str | None:
    completed = subprocess.run(
        ["git", "rev-parse", "--verify", f"HEAD:{repo_path}"],
        cwd=str(repo), capture_output=True, text=True,
    )
    return completed.stdout.strip() or None if completed.returncode == 0 else None


MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)\s]+)\)")


def _link_scan(vault: Path) -> list[dict[str, str]]:
    """One complete link-only pass over authoritative vault Markdown."""
    rows: list[dict[str, str]] = []
    for relative in _vault_markdown(vault):
        text = (vault / relative).read_text(encoding="utf-8", errors="replace")
        for line in text.splitlines():
            for match in MD_LINK_RE.finditer(line):
                target = match.group(2)
                if "://" in target or target.startswith(("mailto:", "#", "/")):
                    continue
                clean = target.split("#", 1)[0]
                if not clean:
                    continue
                resolved = (vault / relative).parent / clean
                try:
                    normalized = resolved.resolve().relative_to(vault).as_posix()
                except (ValueError, OSError):
                    continue
                if not normalized or normalized == ".":
                    continue
                rows.append({"source": relative, "target": normalized})
    return sorted(rows, key=lambda row: (row["source"], row["target"]))


def _parse_list_value(value: str) -> list[str]:
    value = value.strip()
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        return [item.strip().strip("'\"") for item in value[1:-1].split(",") if item.strip()]
    return [value.strip().strip("'\"")]


SPEC_TERMINAL = {"done", "rejected", "deprecated"}


def _spec_kind(relative: str) -> str | None:
    if not relative.startswith(PROJECTS_PREFIX) or "/specs/" not in relative:
        return None
    tail = relative.split("/specs/", 1)[1]
    name = tail.rsplit("/", 1)[-1]
    if tail.startswith("stories/story-"):
        return "story"
    if tail.startswith("epics/epic-"):
        return "epic"
    if tail.startswith("quick-tasks/"):
        return "quick-task"
    if tail.startswith("skill-proposals/"):
        remainder = tail[len("skill-proposals/"):]
        if "/" not in remainder and remainder.endswith(".md") and remainder[0].isdigit():
            return "proposal"
        return None
    if "/" not in tail and name.endswith(".md") and (
        name.startswith("prd") or name.startswith("architecture")
    ):
        return "prd" if name.startswith("prd") else "architecture"
    return None


def _open_work_scan(vault: Path, project: str | None) -> dict[str, list[dict[str, Any]]]:
    """Authoritative current open work per project, terminal records excluded."""
    result: dict[str, list[dict[str, Any]]] = {}
    for relative in _vault_markdown(vault):
        kind = _spec_kind(relative)
        if kind is None:
            continue
        owner = _project_of(relative)
        if owner is None:
            continue
        if project is not None and owner != project:
            continue
        metadata = parse_frontmatter((vault / relative).read_text(encoding="utf-8", errors="replace"))
        status = metadata.get("status") or ""
        decision = metadata.get("decision") or ""
        if kind in {"story", "epic", "quick-task"}:
            if status in SPEC_TERMINAL:
                continue
            blocker = status or "unknown-status"
        elif kind in {"prd", "architecture"}:
            if status != "draft":
                continue
            blocker = "draft-awaiting-approval"
        else:
            if decision and decision != "pending":
                continue
            blocker = "decision-pending"
        result.setdefault(owner, []).append(
            {
                "kind": kind,
                "path": relative,
                "status": status or None,
                "blocker": blocker,
                "updated": metadata.get("updated") or None,
            }
        )
    for entries in result.values():
        entries.sort(key=lambda entry: entry["path"])
    return result


def _log_items(vault: Path, owner: str, date_text: str) -> list[dict[str, str]]:
    relative = f"{PROJECTS_PREFIX}{owner}/log/{owner}-{date_text}.md"
    path = vault / relative
    if not path.is_file():
        return []
    items: list[dict[str, str]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if not re.match(r"^\s*[-*] ", line):
            continue
        if "[Extracted]" in line:
            continue
        items.append({"id": f"L{lineno}", "ref": f"{relative}#L{lineno}"})
    return items


def _impact_entries(vault: Path, owner: str, date_text: str) -> list[str]:
    relative = f"{PROJECTS_PREFIX}{owner}/impact.md"
    path = vault / relative
    if not path.is_file():
        return []
    refs = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        if line.startswith("- ") and f"date: {date_text}" in line:
            refs.append(f"{relative}#L{lineno}")
    return refs

def collect_harvest(
    vault: Path,
    *,
    date: str | None = None,
    timezone_name: str | None = None,
    project: str | None = None,
) -> dict[str, Any]:
    """Compute the observable target-day union as a canonical harvest dict."""
    vault = vault.expanduser().resolve()
    zone = resolve_timezone(timezone_name)
    date_text = _validate_date(date) if date else default_date(zone)
    repo = _repo_root(vault)

    commits, shallow = _window_commits(repo, zone, date_text)
    warnings: list[str] = []
    if shallow:
        warnings.append("shallow-repository: history before the clone depth is unobservable")

    head = None
    try:
        head = _git(repo, "rev-parse", "HEAD").strip() or None
    except DreamError:
        warnings.append("no-commits: repository has no HEAD")

    dirty = _dirty_state(repo)
    dirty_classes = sorted({name for entry in dirty.values() for name in entry["classes"]})

    files_by_path: dict[str, dict[str, Any]] = {}

    def _repo_to_vault(path_text: str) -> str | None:
        candidate = repo / path_text
        try:
            relative = candidate.resolve().relative_to(vault)
        except (ValueError, OSError):
            return None
        text = relative.as_posix()
        return text if text and text != "." else None

    for sha, _stamp in commits:
        for entry in _diff_entries(repo, sha):
            vault_path = _repo_to_vault(entry["new_path"])
            old_vault = _repo_to_vault(entry["old_path"])
            if vault_path is None:
                continue
            if not _authoritative(vault_path):
                continue
            existing = files_by_path.get(vault_path)
            record = {
                "old_path": old_vault if entry["status"] == "renamed" else vault_path,
                "new_path": vault_path,
                "status": entry["status"],
                "old_blob": entry["old_blob"],
                "new_blob": entry["new_blob"],
                "origins": {"git"},
            }
            if existing is None:
                files_by_path[vault_path] = record
            else:
                existing["origins"].update(record["origins"])
                existing["old_blob"] = existing["old_blob"] or record["old_blob"]

    for relative in _vault_markdown(vault):
        repo_relative = (vault / relative).relative_to(repo).as_posix()
        dirty_entry = dirty.get(repo_relative)
        metadata = parse_frontmatter((vault / relative).read_text(encoding="utf-8", errors="replace"))
        dated = metadata.get("created") == date_text or metadata.get("updated") == date_text
        if not dated:
            continue
        record = files_by_path.get(relative)
        if record is None:
            if dirty_entry and "D" in (dirty_entry["x"] + dirty_entry["y"]):
                continue
            status = "created" if dirty_entry and "untracked" in dirty_entry["classes"] else "modified"
            record = {
                "old_path": relative,
                "new_path": relative,
                "status": status,
                "old_blob": None,
                "new_blob": None,
                "origins": set(),
            }
            files_by_path[relative] = record
        if dated:
            record["origins"].add("frontmatter")
        if dirty_entry is not None:
            record["origins"].add("dirty")

    ordered = []
    for relative in sorted(files_by_path):
        record = files_by_path[relative]
        ordered.append(
            {
                "old_path": record["old_path"],
                "new_path": record["new_path"],
                "status": record["status"],
                "old_blob": record["old_blob"],
                "new_blob": record["new_blob"],
                "origins": sorted(record["origins"]),
            }
        )

    groups: dict[str | None, list[dict[str, Any]]] = {}
    for entry in ordered:
        owner = _project_of(entry["new_path"])
        if project is not None and owner is not None and owner != project:
            continue
        groups.setdefault(owner, []).append(entry)

    open_work = _open_work_scan(vault, project)
    for owner in open_work:
        groups.setdefault(owner, [])
    link_index = _link_scan(vault)

    checks: list[dict[str, Any]] = []
    flag_evidence: set[str] = set()

    def _note_hash(relative_path: str) -> str:
        return hashlib.sha256((vault / relative_path).read_bytes()).hexdigest()

    for entry in ordered:
        path_text = entry["new_path"]
        owner = _project_of(path_text)
        if owner is None or entry["status"] == "deleted":
            continue
        if not (vault / path_text).is_file():
            continue
        if "/notes/" not in path_text:
            continue
        metadata = parse_frontmatter((vault / path_text).read_text(encoding="utf-8", errors="replace"))
        if metadata.get("status") == "draft":
            cited = any(
                row["target"] == path_text and row["source"] != path_text for row in link_index
            )
            if not cited:
                checks.append(
                    {
                        "kind": "uncited-draft",
                        "subject": {"path": path_text},
                        "evidence": [{"path": path_text, "sha256": _note_hash(path_text)}],
                    }
                )
                flag_evidence.add(path_text)
        for evidence_ref in _parse_list_value(metadata.get("evidence", "")):
            manifest = f"{PROJECTS_PREFIX}{owner}/{evidence_ref.strip('/')}"
            manifest_path = vault / manifest
            if not manifest_path.is_file():
                continue
            manifest_meta = parse_frontmatter(manifest_path.read_text(encoding="utf-8", errors="replace"))
            pack_date = manifest_meta.get("date") or ""
            note_updated = metadata.get("updated") or ""
            if (
                RECORD_DATE_RE.fullmatch(pack_date)
                and RECORD_DATE_RE.fullmatch(note_updated)
                and pack_date > note_updated
            ):
                checks.append(
                    {
                        "kind": "evidence-order",
                        "subject": {"path": path_text},
                        "evidence": [{"path": manifest, "sha256": _note_hash(manifest)}],
                    }
                )
                flag_evidence.add(manifest)

    for relative in _vault_markdown(vault):
        if "/notes/" not in relative or not relative.startswith(PROJECTS_PREFIX):
            continue
        metadata = parse_frontmatter((vault / relative).read_text(encoding="utf-8", errors="replace"))
        stale = metadata.get("usage_stale") == "true"
        stale_after = metadata.get("stale_after") or ""
        if RECORD_DATE_RE.fullmatch(stale_after) and stale_after < date_text:
            stale = True
        if stale:
            checks.append(
                {
                    "kind": "declared-stale",
                    "subject": {"path": relative},
                    "evidence": [{"path": relative, "sha256": _note_hash(relative)}],
                }
            )
            flag_evidence.add(relative)

    projects_payload = []
    for name, entries in sorted(groups.items(), key=lambda item: (item[0] is None, item[0] or "")):
        log_items = _log_items(vault, name, date_text) if name else []
        for item in log_items:
            log_path = item["ref"].split("#", 1)[0]
            checks.append(
                {
                    "kind": "unextracted-log",
                    "subject": {"path": log_path, "id": item["id"]},
                    "evidence": [{"path": log_path, "sha256": _note_hash(log_path)}],
                }
            )
            flag_evidence.add(log_path)
        status_changes: list[dict[str, Any]] = []
        evidence_packs: list[str] = []
        if name:
            for entry in entries:
                path_text = entry["new_path"]
                if _spec_kind(path_text) is None:
                    continue
                old_bytes = _blob_bytes(repo, entry["old_blob"]) if entry["old_blob"] else None
                if (vault / path_text).is_file():
                    new_bytes = (vault / path_text).read_bytes()
                elif entry["new_blob"]:
                    new_bytes = _blob_bytes(repo, entry["new_blob"])
                else:
                    new_bytes = None
                if old_bytes is None:
                    repo_path = (vault / path_text).relative_to(repo).as_posix()
                    head_id = _head_blob_id(repo, repo_path)
                    old_bytes = _blob_bytes(repo, head_id) if head_id else None
                old_status = (
                    parse_frontmatter(old_bytes.decode("utf-8", errors="replace")).get("status")
                    if old_bytes is not None else None
                )
                new_status = (
                    parse_frontmatter(new_bytes.decode("utf-8", errors="replace")).get("status")
                    if new_bytes is not None else None
                )
                if old_status != new_status and (old_status is not None or new_status is not None):
                    status_changes.append(
                        {
                            "path": path_text,
                            "from": old_status,
                            "to": new_status,
                            "old_blob": entry["old_blob"],
                            "new_blob": entry["new_blob"],
                        }
                    )
                if "/evidence/" in path_text:
                    slug = path_text.split("/evidence/", 1)[1].split("/", 1)[0]
                    evidence_packs.append(f"{PROJECTS_PREFIX}{name}/evidence/{slug}")
        status_changes.sort(key=lambda change: change["path"])
        evidence_packs = sorted(set(evidence_packs))
        impact_entries = _impact_entries(vault, name, date_text) if name else []
        projects_payload.append(
            {
                "project": name,
                "files": entries,
                "log_items": log_items,
                "status_changes": status_changes,
                "open_work": open_work.get(name, []) if name else [],
                "evidence_packs": evidence_packs,
                "impact_entries": impact_entries,
            }
        )

    checks.sort(key=lambda check: (check["kind"], check["subject"]["path"], check["subject"].get("id") or ""))

    candidate_evidence: list[dict[str, str]] = []
    dreams_root = vault / DREAMS_DIR_NAME
    if dreams_root.is_dir():
        for path in sorted(dreams_root.glob("*.md")):
            if path.name == f"{date_text}.md" or path.name in {"index.md", "ideas.md"}:
                continue
            section = _section_text(path.read_text(encoding="utf-8", errors="replace"), "Skill Candidates")
            if section and section.strip() != "—":
                summary = next((line.strip() for line in section.splitlines() if line.strip()), "")
                candidate_evidence.append(
                    {"kind": "prior-dream", "ref": f"dreams/{path.name}", "summary": summary[:160]}
                )
    inventory = vault / "Skills" / ".kosmic" / "routines.json"
    if inventory.is_file():
        try:
            rows = json.loads(inventory.read_text(encoding="utf-8")).get("routines", [])
        except (ValueError, OSError):
            rows = []
        for row in sorted(rows, key=lambda item: str(item.get("id", "")))[:50]:
            candidate_evidence.append(
                {
                    "kind": "routine",
                    "ref": f"routine://{row.get('id', '')}",
                    "summary": str(row.get("procedure") or row.get("summary") or "")[:160],
                }
            )
    candidate_evidence.sort(key=lambda entry: (entry["kind"], entry["ref"]))

    read_set: dict[tuple[str, str], dict[str, str]] = {}
    for entry in ordered:
        path_text = entry["new_path"]
        if entry["status"] != "deleted" and (vault / path_text).is_file():
            read_set.setdefault(
                ("path", path_text),
                {"kind": "path", "ref": path_text, "role": "changed-note", "sha256": _note_hash(path_text)},
            )
        if entry["old_blob"]:
            blob = _blob_bytes(repo, entry["old_blob"])
            read_set.setdefault(
                ("git-blob", f"git:{entry['old_blob']}"),
                {
                    "kind": "git-blob",
                    "ref": f"git:{entry['old_blob']}",
                    "role": "changed-note",
                    "sha256": hashlib.sha256(blob).hexdigest(),
                },
            )
    for payload in projects_payload:
        for work in payload["open_work"]:
            path_text = work["path"]
            read_set.setdefault(
                ("path", path_text),
                {"kind": "path", "ref": path_text, "role": "open-work", "sha256": _note_hash(path_text)},
            )
    for path_text in sorted(flag_evidence):
        if (vault / path_text).is_file():
            read_set.setdefault(
                ("path", path_text),
                {"kind": "path", "ref": path_text, "role": "flag-evidence", "sha256": _note_hash(path_text)},
            )
    for entry in candidate_evidence:
        if entry["kind"] == "prior-dream":
            path_text = entry["ref"]
            read_set.setdefault(
                ("path", path_text),
                {"kind": "path", "ref": path_text, "role": "prior-candidate", "sha256": _note_hash(path_text)},
            )
    read_list = sorted(read_set.values(), key=lambda entry: (entry["kind"], entry["ref"]))

    existing_record_path = vault / DREAMS_DIR_NAME / f"{date_text}.md"
    replacement = {"existing": existing_record_path.is_file(), "generated_match": None, "requires_replace": None}

    return {
        "schema": HARVEST_SCHEMA,
        "date": date_text,
        "timezone": zone,
        "head": head,
        "source_commits": [sha for sha, _ in commits],
        "project_filter": project,
        "coverage": {
            "shallow": shallow,
            "dirty_classes": dirty_classes,
            "warnings": warnings,
            "excluded_surfaces": list(EXCLUDED_SURFACES),
        },
        "base_dreams_sha256": dreams_tree_digest(vault),
        "replacement": replacement,
        "projects": projects_payload,
        "knowledge_checks": checks,
        "link_index": link_index,
        "candidate_evidence": candidate_evidence,
        "read_set": read_list,
    }


SECTION_ORDER = ["Done", "In Flight", "Notes Digest", "Knowledge Flags", "Skill Candidates", "Ideas", "Today"]
RECORD_KEYS = [
    "schema",
    "type",
    "date",
    "projects",
    "source_commits",
    "timezone",
    "project_filter",
    "produced_by",
    "generated_content_sha256",
    "status",
    "coverage_warnings",
]
PRODUCED_BY_RE = re.compile(r"^dream/[A-Za-z0-9._-]+$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
IDEA_ID_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}-[a-z0-9]+(?:-[a-z0-9]+)*$")
DREAM_CHILD_RE = re.compile(r"^([0-9]{4}-[0-9]{2}-[0-9]{2})\.md$")
INDEX_ROW_RE = re.compile(r"^\| \[([0-9]{4}-[0-9]{2}-[0-9]{2})\]\(\1\.md\) \| (.*) \|$")
SECRET_PATTERNS = (
    re.compile(r"\.tmp/kosmic/[^\s)\"']*"),
    re.compile(r"handle_file\s*:", re.IGNORECASE),
    re.compile(r"\btoken\s*:", re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+"),
    re.compile(r"ghp_[A-Za-z0-9]{8,}"),
    re.compile(r"xoxb-[A-Za-z0-9-]+"),
    re.compile(r"sk-[A-Za-z0-9]{16,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def redact_text(text: str) -> str:
    """Replace credential-shaped and scratch-path content with [redacted]."""
    redacted = unicodedata.normalize("NFC", str(text))
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub("[redacted]", redacted)
    return redacted


def _render_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, list):
        return "[" + ", ".join(_render_scalar(item) for item in value) + "]"
    return unicodedata.normalize("NFC", str(value))


def _parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    current: str | None = None
    buffer: list[str] = []
    for line in text.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buffer).strip()
            current = line[3:].strip()
            buffer = []
        elif current is not None:
            buffer.append(line)
    if current is not None:
        sections[current] = "\n".join(buffer).strip()
    return sections


def parse_record(text: str) -> tuple[dict[str, Any], dict[str, str]]:
    """Parse a canonical dream record into typed fields and ordered sections."""
    fields_raw = parse_frontmatter(text)
    fields: dict[str, Any] = {}
    for key, value in fields_raw.items():
        if value == "null":
            fields[key] = None
        elif value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            fields[key] = [item.strip() for item in inner.split(",")] if inner else []
        else:
            fields[key] = value
    return fields, _parse_sections(text)


def _serialize_record(fields: dict[str, Any], sections: dict[str, str], generated_hash: str | None) -> bytes:
    ordered_fields: list[str] = []
    values = dict(fields)
    if generated_hash is not None:
        values["generated_content_sha256"] = generated_hash
    for key in RECORD_KEYS:
        if key == "generated_content_sha256" and generated_hash is None:
            continue
        if key not in values:
            continue
        ordered_fields.append(f"{key}: {_render_scalar(values[key])}")
    body_parts: list[str] = []
    for title in SECTION_ORDER:
        content = redact_text(sections.get(title, "")).strip() or "—"
        body_parts.append(f"## {title}\n\n{content}")
    body = "\n\n".join(body_parts)
    document = "---\n" + "\n".join(ordered_fields) + "\n---\n\n" + body + "\n"
    return unicodedata.normalize("NFC", document).encode("utf-8")


def compute_generated_hash(record_bytes: bytes) -> str:
    """Hash canonical record bytes with the generated-hash YAML line removed."""
    text = record_bytes.decode("utf-8")
    stripped = "\n".join(
        line for line in text.split("\n") if not line.startswith("generated_content_sha256:")
    )
    normalized = unicodedata.normalize("NFC", stripped)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def parse_candidate(text: str) -> dict[str, Any]:
    """Parse untrusted agent input; reject forged publisher-owned fields."""
    fields = parse_frontmatter(text)
    if fields.get("schema") != CANDIDATE_SCHEMA:
        raise DreamError("CANDIDATE_SCHEMA", f"expected {CANDIDATE_SCHEMA}, got {fields.get('schema')!r}")
    if fields.get("type") != "dream-candidate":
        raise DreamError("CANDIDATE_TYPE", str(fields.get("type")))
    allowed = {"schema", "type", "date"}
    forbidden = sorted(set(fields) - allowed)
    if forbidden:
        raise DreamError("CANDIDATE_FIELD_FORBIDDEN", ", ".join(forbidden))
    if not RECORD_DATE_RE.fullmatch(fields.get("date", "")):
        raise DreamError("DATE_INVALID", str(fields.get("date")))
    sections = _parse_sections(text)
    missing = [title for title in SECTION_ORDER if title not in sections]
    if missing:
        raise DreamError("SECTION_MISSING", ", ".join(missing))
    return {"date": fields["date"], "sections": sections}


def build_record_bytes(candidate: dict[str, Any], *, harvest: dict[str, Any], run_id: str) -> bytes:
    """Merge redacted candidate sections with publisher-owned fields."""
    if candidate["date"] != harvest["date"]:
        raise DreamError("CANDIDATE_DATE_MISMATCH", f"{candidate['date']} != {harvest['date']}")
    missing = [title for title in SECTION_ORDER if title not in candidate["sections"]]
    if missing:
        raise DreamError("SECTION_MISSING", ", ".join(missing))
    fields = {
        "schema": RECORD_SCHEMA,
        "type": "dream",
        "date": harvest["date"],
        "projects": sorted({entry["project"] for entry in harvest["projects"] if entry["project"]}),
        "source_commits": list(harvest["source_commits"]),
        "timezone": harvest["timezone"],
        "project_filter": harvest.get("project_filter"),
        "produced_by": f"dream/{run_id}",
        "status": "draft",
        "coverage_warnings": list(harvest["coverage"]["warnings"]),
    }
    without_hash = _serialize_record(fields, candidate["sections"], generated_hash=None)
    generated = compute_generated_hash(without_hash)
    return _serialize_record(fields, candidate["sections"], generated_hash=generated)


def validate_record_text(text: str, *, expected_date: str) -> None:
    """Fail closed on schema, section, provenance, hash, and secret defects."""
    fields, sections = parse_record(text)
    if fields.get("schema") != RECORD_SCHEMA:
        raise DreamError("RECORD_SCHEMA", str(fields.get("schema")))
    if fields.get("type") != "dream":
        raise DreamError("RECORD_TYPE", str(fields.get("type")))
    if fields.get("date") != expected_date or not RECORD_DATE_RE.fullmatch(str(fields.get("date", ""))):
        raise DreamError("RECORD_DATE", str(fields.get("date")))
    if fields.get("status") != "draft":
        raise DreamError("RECORD_STATUS", str(fields.get("status")))
    if not PRODUCED_BY_RE.fullmatch(str(fields.get("produced_by", ""))):
        raise DreamError("RECORD_PRODUCED_BY", str(fields.get("produced_by")))
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise DreamError("SECRET_CONTENT", pattern.pattern)
    digest = str(fields.get("generated_content_sha256", ""))
    if not SHA256_RE.fullmatch(digest):
        raise DreamError("RECORD_HASH_FORMAT", digest)
    if compute_generated_hash(text.encode("utf-8")) != digest:
        raise DreamError("RECORD_HASH_MISMATCH", digest)
    if list(sections) != SECTION_ORDER:
        raise DreamError("SECTION_ORDER", ", ".join(sections))


def parse_ideas(text: str) -> list[dict[str, str]]:
    """Parse ideas entries with optional indented merges lines."""
    entries: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- "):
            identifier, _, rest = stripped[2:].partition(" — ")
            if not IDEA_ID_RE.fullmatch(identifier):
                raise DreamError("IDEA_FORMAT", stripped[:80])
            current = {"id": identifier, "line": line.rstrip(), "merges": ""}
            entries.append(current)
        elif stripped.startswith("merges:") and current is not None:
            current["merges"] = stripped.partition("merges:")[2].strip()
        elif stripped:
            current = None
    return entries


def serialize_ideas(entries: list[dict[str, str]]) -> str:
    lines: list[str] = []
    for entry in entries:
        lines.append(entry["line"])
        if entry.get("merges"):
            lines.append(f"  merges: {entry['merges']}")
    return "\n".join(lines) + ("\n" if lines else "")


def merge_ideas(base_text: str, input_text: str) -> str:
    """Merge idea inputs; identical entries dedupe, conflicting IDs fail."""
    base_entries = parse_ideas(base_text)
    input_entries = parse_ideas(input_text)
    combined = {entry["id"]: entry for entry in base_entries}
    order = [entry["id"] for entry in base_entries]
    for entry in input_entries:
        existing = combined.get(entry["id"])
        if existing is not None:
            if existing["line"] != entry["line"]:
                raise DreamError("IDEA_ID_CONFLICT", entry["id"])
            continue
        combined[entry["id"]] = entry
        order.append(entry["id"])
    all_entries = [combined[identifier] for identifier in order]
    identifiers = {entry["id"] for entry in all_entries}
    for entry in all_entries:
        target = entry.get("merges") or ""
        if target and target not in identifiers:
            raise DreamError("MERGES_TARGET_MISSING", target)
    return serialize_ideas(all_entries)


def rebuild_index(summaries: dict[str, str]) -> bytes:
    """Deterministically rebuild the reverse-chronological dreams index."""
    rows = ["# Dreams", "", "| Date | Summary |", "|------|---------|"]
    for date_text in sorted(summaries, reverse=True):
        summary = redact_text(summaries[date_text]).replace("|", "/")[:80] or "—"
        rows.append(f"| [{date_text}]({date_text}.md) | {summary} |")
    return ("\n".join(rows) + "\n").encode("utf-8")


def _record_summary(record_text: str) -> str:
    sections = _parse_sections(record_text)
    done = sections.get("Done", "")
    for line in done.split("\n"):
        stripped = line.strip().lstrip("-* ").strip()
        if stripped and stripped != "—":
            return stripped[:80]
    return "—"


def validate_dream_tree(vault: Path, *, root: Path | None = None) -> None:
    """Validate a canonical or staged dreams tree, failing closed."""
    vault = vault.expanduser().resolve()
    tree = root.expanduser().resolve() if root else vault / DREAMS_DIR_NAME
    if not tree.is_dir():
        return
    dates: dict[str, str] = {}
    for child in sorted(tree.iterdir()):
        name = child.name
        if name in {"index.md", "ideas.md"}:
            continue
        if DREAM_CHILD_RE.fullmatch(name):
            text = child.read_text(encoding="utf-8")
            validate_record_text(text, expected_date=name[: -len(".md")])
            dates[name[: -len(".md")]] = _record_summary(text)
            for pattern in SECRET_PATTERNS:
                if pattern.search(text):
                    raise DreamError("SECRET_CONTENT", name)
            continue
        raise DreamError("DREAM_CHILD_UNKNOWN", name)

    index_path = tree / "index.md"
    if dates:
        if not index_path.is_file():
            raise DreamError("INDEX_MISMATCH", "index.md missing while records exist")
        rows = []
        for line in index_path.read_text(encoding="utf-8").split("\n"):
            match = INDEX_ROW_RE.fullmatch(line)
            if match:
                rows.append(match.group(1))
        if rows != sorted(dates, reverse=True):
            raise DreamError("INDEX_MISMATCH", f"index rows {rows} != records {sorted(dates, reverse=True)}")

    ideas_path = tree / "ideas.md"
    if ideas_path.is_file():
        entries = parse_ideas(ideas_path.read_text(encoding="utf-8"))
        seen: set[str] = set()
        for entry in entries:
            if entry["id"] in seen:
                raise DreamError("IDEA_ID_CONFLICT", entry["id"])
            seen.add(entry["id"])
        for entry in entries:
            target = entry.get("merges") or ""
            if target and target not in seen:
                raise DreamError("MERGES_TARGET_MISSING", target)
        for pattern in SECRET_PATTERNS:
            if pattern.search(ideas_path.read_text(encoding="utf-8")):
                raise DreamError("SECRET_CONTENT", "ideas.md")

    canonical_dreams = vault / DREAMS_DIR_NAME
    for date_text, _summary in dates.items():
        record_text = (tree / f"{date_text}.md").read_text(encoding="utf-8")
        for match in MD_LINK_RE.finditer(record_text):
            target = match.group(2)
            if "://" in target or target.startswith(("mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if not clean:
                continue
            resolved = (canonical_dreams / clean).resolve()
            if not resolved.is_relative_to(vault):
                raise DreamError("LINK_TARGET_MISSING", target)
            normalized = resolved.relative_to(vault).as_posix()
            if normalized == DREAMS_DIR_NAME or normalized.startswith(DREAMS_DIR_NAME + "/"):
                inner = normalized[len(DREAMS_DIR_NAME):].lstrip("/")
                if not inner or not (tree / inner).exists():
                    raise DreamError("LINK_TARGET_MISSING", target)
            elif not (vault / normalized).exists():
                raise DreamError("LINK_TARGET_MISSING", target)


DREAM_STATE_FILE = "dream-state.json"
DREAM_STATES = ("active", "publishing", "retryable-input", "retryable-validation", "reharvest-required", "succeeded", "failed")
RETRYABLE_INPUT_CODES = {
    "CANDIDATE_SCHEMA", "CANDIDATE_TYPE", "CANDIDATE_FIELD_FORBIDDEN", "CANDIDATE_DATE_MISMATCH",
    "DATE_INVALID", "SECTION_MISSING", "IDEA_FORMAT", "IDEA_ID_CONFLICT", "MERGES_TARGET_MISSING",
    "DREAM_INPUT_MISSING", "DREAM_MANUAL_DIVERGENCE",
}
RETRYABLE_VALIDATION_CODES = {
    "RECORD_SCHEMA", "RECORD_TYPE", "RECORD_DATE", "RECORD_STATUS", "RECORD_PRODUCED_BY",
    "RECORD_HASH_FORMAT", "RECORD_HASH_MISMATCH", "SECTION_ORDER", "SECRET_CONTENT",
    "INDEX_MISMATCH", "DREAM_CHILD_UNKNOWN", "LINK_TARGET_MISSING",
}
REHARVEST_CODES = {"DREAM_BASE_DRIFT", "DREAM_EVIDENCE_DRIFT"}
TERMINAL_STATES = {"succeeded", "failed"}


def _dream_dirs(run_path: Path) -> dict[str, Path]:
    base = run_path / "dream"
    return {
        "root": base,
        "base": base / "base",
        "evidence": base / "evidence",
        "candidate": base / "candidate",
        "control": base / "control",
        "publish": base / "publish",
    }


def _copy_tree_no_follow(source: Path, destination: Path) -> None:
    """Copy a tree rejecting symlinks and special files (no-follow)."""
    destination.mkdir(parents=True, exist_ok=True)
    for child in sorted(source.iterdir()):
        if child.is_symlink() or not (child.is_file() or child.is_dir()):
            raise DreamError("SOURCE_NOT_TRUSTED", str(child))
        target = destination / child.name
        if child.is_dir():
            _copy_tree_no_follow(child, target)
        else:
            target.write_bytes(child.read_bytes())


def _dream_state_path(dirs: dict[str, Path]) -> Path:
    return dirs["control"] / DREAM_STATE_FILE


def read_dream_state(handle_file: Path) -> dict[str, Any]:
    """Authenticate the handle and load dream control state."""
    root, name = kosmic_runs._root_for_handle(Path(handle_file))
    with root:
        handle = kosmic_runs.read_handle(root.handles_fd, name)
        run_dir = root.path / "runs" / handle["run_id"]
        dirs = _dream_dirs(run_dir)
        state_path = _dream_state_path(dirs)
        payload = {
            "run_id": handle["run_id"],
            "handle_state": handle.get("state") or handle.get("outcome") or "unknown",
            "run_dir": str(run_dir),
            "dirs": {key: str(value) for key, value in dirs.items()},
            "dream_state": json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else None,
        }
        return payload


def _write_state(dirs: dict[str, Path], state: str, detail: str = "") -> None:
    dirs["control"].mkdir(parents=True, exist_ok=True)
    payload = {"schema": 1, "state": state, "detail": redact_text(detail)[:512], "updated": _now_text()}
    (dirs["control"] / DREAM_STATE_FILE).write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def _now_text() -> str:
    from datetime import datetime, timezone as dt_tz

    return datetime.now(dt_tz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def dream_harvest(
    vault: Path,
    *,
    date: str | None = None,
    timezone_name: str | None = None,
    project: str | None = None,
) -> dict[str, Any]:
    """Begin a managed run and materialize the complete reflection contract."""
    vault = vault.expanduser().resolve()
    repo = _repo_root(vault)
    harvest = collect_harvest(vault, date=date, timezone_name=timezone_name, project=project)
    handle = kosmic_runs.begin_run(repo, purpose="dream-harvest", retention="diagnostic")
    try:
        dirs = _dream_dirs(handle.path)
        for key in ("base", "evidence", "candidate", "control"):
            dirs[key].mkdir(parents=True, exist_ok=True)
        dreams = vault / DREAMS_DIR_NAME
        if dreams.is_dir():
            _copy_tree_no_follow(dreams, dirs["base"])
        else:
            dirs["base"].mkdir(parents=True, exist_ok=True)
        manifest = []
        for index, entry in enumerate(harvest["read_set"]):
            if entry["kind"] == "path":
                source = vault / entry["ref"]
                if source.is_symlink() or not source.is_file():
                    raise DreamError("SOURCE_NOT_TRUSTED", entry["ref"])
                data = source.read_bytes()
            else:
                blob_id = entry["ref"].removeprefix("git:")
                data = _blob_bytes(repo, blob_id)
            if hashlib.sha256(data).hexdigest() != entry["sha256"]:
                raise DreamError("EVIDENCE_HASH_MISMATCH", entry["ref"])
            name = f"{index:04d}.bin"
            (dirs["evidence"] / name).write_bytes(data)
            manifest.append({**entry, "file": name})
        (dirs["evidence"] / "manifest.json").write_bytes(
            canonical_json({"schema": "kosmic.dream.evidence/1", "entries": manifest})
        )
        (dirs["control"] / "harvest.json").write_bytes(canonical_json(harvest))
        (dirs["control"] / "binding.json").write_bytes(
            canonical_json(
                {"schema": "kosmic.dream.binding/1", "vault": str(vault), "repo": str(repo), "head": harvest["head"]}
            )
        )
        _write_state(dirs, "active", f"harvest {harvest['date']}")
        return {
            "code": "OK",
            "run_id": handle.run_id,
            "handle_file": str(handle.handle_file),
            "harvest": str(dirs["control"] / "harvest.json"),
            "candidate_record": str(dirs["candidate"] / "record.md"),
            "candidate_ideas": str(dirs["candidate"] / "ideas.md"),
            "evidence_count": len(manifest),
            "base_dreams_sha256": harvest["base_dreams_sha256"],
            "date": harvest["date"],
        }
    except Exception:
        kosmic_runs.finish_run(handle.handle_file, "failed", detail="dream-harvest setup failed")
        raise


def _verify_evidence(vault: Path, dirs: dict[str, Path]) -> None:
    manifest_path = dirs["evidence"] / "manifest.json"
    if not manifest_path.is_file():
        raise DreamError("DREAM_EVIDENCE_DRIFT", "evidence manifest missing")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for entry in manifest.get("entries", []):
        path = dirs["evidence"] / entry["file"]
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
            raise DreamError("DREAM_EVIDENCE_DRIFT", entry["ref"])


def _stage_publish_tree(vault: Path, dirs: dict[str, Path], harvest: dict[str, Any], record_bytes: bytes, candidate_ideas: str) -> Path:
    stage = dirs["publish"] / DREAMS_DIR_NAME
    if stage.exists():
        import shutil

        shutil.rmtree(stage)
    _copy_tree_no_follow(dirs["base"], stage)
    date_text = harvest["date"]
    (stage / f"{date_text}.md").write_bytes(record_bytes)
    base_ideas = (stage / "ideas.md").read_text(encoding="utf-8") if (stage / "ideas.md").is_file() else ""
    merged = merge_ideas(base_ideas, candidate_ideas)
    (stage / "ideas.md").write_text(merged, encoding="utf-8")
    summaries: dict[str, str] = {}
    for child in sorted(stage.glob("*.md")):
        if child.name in {"index.md", "ideas.md"}:
            continue
        match = DREAM_CHILD_RE.fullmatch(child.name)
        if not match:
            raise DreamError("DREAM_CHILD_UNKNOWN", child.name)
        summaries[match.group(1)] = _record_summary(child.read_text(encoding="utf-8"))
    (stage / "index.md").write_bytes(rebuild_index(summaries))
    return stage


def dream_publish(vault: Path, handle_file: Path, *, replace: bool = False) -> dict[str, Any]:
    """Merge, validate, and atomically publish the dream tree from a run."""

    vault = vault.expanduser().resolve()
    state_info = read_dream_state(handle_file)
    run_dir = Path(state_info["run_dir"])
    dirs = _dream_dirs(run_dir)
    dream_state = (state_info["dream_state"] or {}).get("state", "active")
    if dream_state == "succeeded":
        receipt_path = dirs["control"] / "receipt.json"
        payload = json.loads(receipt_path.read_text(encoding="utf-8")) if receipt_path.is_file() else {}
        return {**payload, "code": "OK_ALREADY_PUBLISHED"}
    if dream_state == "failed":
        raise DreamError("DREAM_TERMINAL", f"run already failed: {(state_info['dream_state'] or {}).get('detail', '')}")
    if dream_state == "publishing":
        raise DreamError("DREAM_CONCURRENT_PUBLISH", state_info["run_id"])
    if state_info["handle_state"] != "active":
        raise DreamError("HANDLE_NOT_ACTIVE", str(state_info["handle_state"]))

    harvest_path = dirs["control"] / "harvest.json"
    binding_path = dirs["control"] / "binding.json"
    if not harvest_path.is_file():
        raise DreamError("DREAM_INPUT_MISSING", "harvest.json missing; run dream-harvest first")
    if binding_path.is_file():
        binding = json.loads(binding_path.read_text(encoding="utf-8"))
        if binding.get("vault") != str(vault):
            raise DreamError("VAULT_MISMATCH", f"run was harvested for {binding.get('vault')}")
    harvest = json.loads(harvest_path.read_text(encoding="utf-8"))
    record_path = dirs["candidate"] / "record.md"
    ideas_path = dirs["candidate"] / "ideas.md"

    try:
        for path in (record_path, ideas_path):
            if not path.is_file() or path.is_symlink():
                raise DreamError("DREAM_INPUT_MISSING", str(path))
        _verify_evidence(vault, dirs)
        repo = _repo_root(vault)
        for entry in harvest["read_set"]:
            if entry["kind"] != "path":
                continue
            source = vault / entry["ref"]
            if not source.is_file() or source.is_symlink():
                raise DreamError("DREAM_EVIDENCE_DRIFT", entry["ref"])
            if hashlib.sha256(source.read_bytes()).hexdigest() != entry["sha256"]:
                raise DreamError("DREAM_EVIDENCE_DRIFT", entry["ref"])
        if dreams_tree_digest(vault) != harvest["base_dreams_sha256"]:
            raise DreamError("DREAM_BASE_DRIFT", "canonical dreams tree changed since harvest")
        date_text = harvest["date"]
        existing = vault / DREAMS_DIR_NAME / f"{date_text}.md"
        if existing.is_file():
            existing_text = existing.read_text(encoding="utf-8")
            persisted = parse_frontmatter(existing_text).get("generated_content_sha256", "")
            generated_match = SHA256_RE.fullmatch(persisted) and compute_generated_hash(existing_text.encode("utf-8")) == persisted
            if not generated_match and not replace:
                raise DreamError("DREAM_MANUAL_DIVERGENCE", f"{date_text}.md was edited; pass --replace to overwrite")
        _write_state(dirs, "publishing", f"publish {date_text}")
        candidate = parse_candidate(record_path.read_text(encoding="utf-8"))
        candidate_ideas = ideas_path.read_text(encoding="utf-8")
        record_bytes = build_record_bytes(candidate, harvest=harvest, run_id=state_info["run_id"])
        stage = _stage_publish_tree(vault, dirs, harvest, record_bytes, candidate_ideas)
        validate_dream_tree(vault, root=stage)
        publish_tree(stage, vault / DREAMS_DIR_NAME)
        receipt = kosmic_runs.finish_run(Path(handle_file), "succeeded", detail=f"dream {date_text} published")
        _write_state(dirs, "succeeded", f"dream {date_text} published")
        payload = {
            "code": "OK",
            "run_id": state_info["run_id"],
            "date": date_text,
            "record_sha256": hashlib.sha256(record_bytes).hexdigest(),
            "outcome": receipt.state,
        }
        (dirs["control"] / "receipt.json").write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        return payload
    except DreamError as error:
        if error.code in REHARVEST_CODES:
            _write_state(dirs, "reharvest-required", error.code)
        elif error.code in RETRYABLE_INPUT_CODES:
            _write_state(dirs, "retryable-input", error.code)
        elif error.code in RETRYABLE_VALIDATION_CODES:
            _write_state(dirs, "retryable-validation", error.code)
        raise


def dream_abort(vault: Path, handle_file: Path, *, reason: str) -> dict[str, Any]:
    """Idempotently finalize a dream run as failed."""
    state_info = read_dream_state(handle_file)
    dirs = _dream_dirs(Path(state_info["run_dir"]))
    dream_state = (state_info["dream_state"] or {}).get("state", "active")
    if dream_state == "failed":
        return {"code": "OK_ALREADY_FAILED", "run_id": state_info["run_id"]}
    if state_info["handle_state"] != "active":
        raise DreamError("HANDLE_NOT_ACTIVE", str(state_info["handle_state"]))
    receipt = kosmic_runs.finish_run(Path(handle_file), "failed", detail=redact_text(reason)[:512])
    _write_state(dirs, "failed", reason)
    return {"code": "OK", "run_id": state_info["run_id"], "outcome": receipt.state}
