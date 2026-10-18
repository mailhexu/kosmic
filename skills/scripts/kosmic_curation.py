#!/usr/bin/env python3
"""Story 004 deterministic curation stages: prepare and finalize.

One curation job = three explicit stages orchestrated by one outer agent:

1. ``curation-prepare`` (deterministic CLI): freezes the cutoff ``U`` at run
   start, selects every interval-eligible note (``L < changed <= U``) in the
   declared scope, snapshots revision identities (references only, never
   note bytes) into the managed-run workspace, and closes the newly opened
   run on any failure. Coordination between runs comes ENTIRELY from the
   existing managed-run lifecycle: an active run for the same
   project+scope (identified by its own snapshot under the run workspace)
   makes prepare busy; terminal runs never block. Prepare never writes the
   Project checkpoint.
2. Semantic review (an agent, never the CLI): reads the selected notes in
   place and records per-note dispositions into the EXISTING governing work
   record under a documented ``curation_review`` mapping.
3. ``curation-finalize`` (deterministic CLI): validates the explicit run
   handle and its snapshot identity (project, scope, record, run id),
   review coverage (with skip eligibility), snapshot revalidation, and
   window evolution; only after the managed run closes as ``succeeded``
   does it publish the per-scope checkpoint to exactly ``U``. If the
   checkpoint write fails the cursor stays old and the next window safely
   rescans — an incomplete cursor is never consumed.

The CLI never invokes a model and never infers semantic review from a
process exit status. Scope is a bounded notes-subtree path (default
``notes``); each scope keeps an independent checkpoint. The per-scope
flock is retained through the existing run-root namespace for short
in-process transactions only; cross-process serialization comes from the
native run lease, never from a lockfile.
"""

from __future__ import annotations

import errno
import fcntl
import hashlib
import json
import os
import re
import stat
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Any, Sequence

try:  # package import (tests: skills.scripts.…)
    from . import kosmic_runs
    from . import kosmic_work
    from .kosmic_project_skills import (
        ISO_DATE_RE,
        KosmicError,
        Project,
        load_project,
        note_skill_candidate,
        note_skill_resources,
        parse_markdown,
        validated_note_updated,
    )
except ImportError:  # script execution from the scripts directory
    import kosmic_runs
    import kosmic_work
    from kosmic_project_skills import (
        ISO_DATE_RE,
        KosmicError,
        Project,
        load_project,
        note_skill_candidate,
        note_skill_resources,
        parse_markdown,
        validated_note_updated,
    )

__all__ = [
    "CURATION_ROOT_SCOPE",
    "CurationError",
    "finalize_curation",
    "normalize_scope",
    "prepare_curation",
    "run_cli",
]

#: The default (root) notes scope; bounded subtrees hang below it.
CURATION_ROOT_SCOPE = "notes"

#: Reserved bundle entry points are never atomic concept notes.
_RESERVED_NOTE_NAMES = frozenset({"index.md", "log.md"})

#: Recorded review dispositions (work-record ``curation_review`` schema).
DISPOSITIONS = ("reviewed", "no-action", "skipped")

_IN_WINDOW = "in-window"
_OUT_OF_WINDOW = "out-of-window"
_AMBIGUOUS = "ambiguous"

_UTC_INSTANT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")
_SAFE_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
_CONTROL_SCHEMA = 1
_SNAPSHOT_SCHEMA = 1
_SNAPSHOT_NAME = "curation-snapshot.json"


class CurationError(KosmicError):
    """Typed deterministic-stage failure; always leaves the checkpoint unchanged."""


def _fail(code: str, detail: str) -> CurationError:
    return CurationError(f"{code}: {detail}")


def _utc_instant(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _parse_utc_instant(text: str, argument: str) -> datetime:
    if not isinstance(text, str) or not _UTC_INSTANT_RE.fullmatch(text):
        raise _fail(
            "CURATION_INSTANT_INVALID",
            f"{argument} expects an exact UTC instant "
            f"(YYYY-MM-DDTHH:MM:SS[.ffffff]Z), got {text!r}",
        )
    raw = text.rstrip("Z")
    if "." in raw:
        moment = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S.%f")
    else:
        moment = datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S")
    return moment.replace(tzinfo=timezone.utc)


def _parse_note_instant(raw: str, relative: str) -> tuple[datetime, datetime, bool]:
    """Resolve a validated note timestamp to the exact instant it certifies.

    Legacy date-only values certify the whole UTC day ``[00:00, 24:00)``:
    never an invented intra-day time. Returns ``(start, end, uncertain)``;
    exact instants return a zero-width interval with ``uncertain=False``.
    """
    if ISO_DATE_RE.fullmatch(raw):
        start = datetime.combine(date.fromisoformat(raw), time.min, tzinfo=timezone.utc)
        return start, start + timedelta(days=1), True
    text = raw.rstrip("Z")
    if "." in text:
        moment = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S.%f")
    else:
        moment = datetime.strptime(text, "%Y-%m-%dT%H:%M:%S")
    moment = moment.replace(tzinfo=timezone.utc)
    return moment, moment, False


# --- scope normalization and checkpoint naming --------------------------------


def normalize_scope(scope: str) -> str:
    """Normalize ``--scope`` to a bounded notes-subtree path.

    ``notes`` is the root scope; any other value is a subtree path below it
    (``notes/theory`` or plain ``theory``). Absolute paths, ``..``, empty or
    unsafe components, and backslashes are rejected; nofollow containment is
    enforced at read time, not by name alone.
    """
    text = str(scope or "").strip().replace("\\", "/")
    if not text:
        return CURATION_ROOT_SCOPE
    if text.startswith("/") or text.endswith("/"):
        raise _fail("CURATION_SCOPE_INVALID", f"{scope!r}: scope must be relative to notes/")
    parts = [part for part in text.split("/") if part]
    if parts and parts[0] == CURATION_ROOT_SCOPE:
        parts = parts[1:]
    if any(part in ("", ".", "..") or not _SAFE_NAME_RE.fullmatch(part) for part in parts):
        raise _fail("CURATION_SCOPE_INVALID", f"{scope!r}: unsafe scope component")
    if not parts:
        return CURATION_ROOT_SCOPE
    return "/".join([CURATION_ROOT_SCOPE, *parts])


def _scope_parts(scope: str) -> list[str]:
    return [] if scope == CURATION_ROOT_SCOPE else scope.split("/")[1:]


def _checkpoint_name(scope: str) -> str:
    """Stable per-scope checkpoint name; the root scope keeps ``notes.json``."""
    if scope == CURATION_ROOT_SCOPE:
        return "notes.json"
    digest = hashlib.sha256(scope.encode("utf-8")).hexdigest()[:16]
    return f"scope-{digest}.json"


@contextmanager
def _scope_transaction(worktree: Path):
    """Short transaction under the EXISTING native managed-run namespace.

    ``resolve_run_root`` creates/verifies the private O_NOFOLLOW components
    (including a missing root); the flock rides the native ``kosmic_fd``
    directory inode across processes — no ad-hoc path opens, no new lock
    file, and no Project-side write. The flock never outlives this context;
    cross-CLI serialization for a scope comes from the native run lease.
    """
    with kosmic_runs.resolve_run_root(worktree) as native:
        fcntl.flock(native.kosmic_fd, fcntl.LOCK_EX)
        try:
            yield native
        finally:
            fcntl.flock(native.kosmic_fd, fcntl.LOCK_UN)


def _read_checkpoint(project_root: Path, scope: str) -> dict[str, Any]:
    """Read-only checkpoint view; prepare never creates or mutates it.

    The whole ``.kosmic/curation`` path is verified component-by-component
    (O_NOFOLLOW); a symlinked component is refused and a missing tree simply
    means no cursor — no Project write happens here.
    """
    directory = _open_dir_fd(
            Path(project_root),
            (".kosmic", "curation"),
            invalid_code="CURATION_CHECKPOINT_INVALID",
        )
    if directory is None:
        return {"schema": _CONTROL_SCHEMA, "scope": scope, "last_successful": None}
    name = _checkpoint_name(scope)
    try:
        try:
            descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory)
        except FileNotFoundError:
            return {"schema": _CONTROL_SCHEMA, "scope": scope, "last_successful": None}
        except OSError as error:
            raise _fail("CURATION_CHECKPOINT_INVALID", f"{name}: {error}") from error
        try:
            if not os.fstat(descriptor).st_mode & 0o170000 == 0o100000:
                raise _fail(
                    "CURATION_CHECKPOINT_INVALID",
                    f"{name}: checkpoint must be a regular file",
                )
            chunks = []
            while True:
                chunk = os.read(descriptor, 1 << 16)
                if not chunk:
                    break
                chunks.append(chunk)
            raw = b"".join(chunks)
        finally:
            os.close(descriptor)
    finally:
        os.close(directory)
    control = json.loads(raw.decode("utf-8"))
    if not isinstance(control, dict) or control.get("scope") != scope:
        raise _fail("CURATION_CHECKPOINT_INVALID", f"{name}: unexpected checkpoint content")
    return control


def _publish_checkpoint(project_root: Path, scope: str, until: str) -> None:
    """Publish the ONLY durable checkpoint write, after a successful finalize.

    The verified directory walk creates ``.kosmic/curation`` (finalize only);
    the tempfile and final replace happen strictly relative to the verified
    directory descriptor, so a symlinked component can never redirect the
    publish outside the Project.
    """
    control = {"schema": _CONTROL_SCHEMA, "scope": scope, "last_successful": until}
    name = _checkpoint_name(scope)
    temp = f".{name}.{os.getpid()}.tmp"
    try:
        directory = _open_dir_fd(
            Path(project_root),
            (".kosmic", "curation"),
            create=True,
            invalid_code="CURATION_CHECKPOINT_INVALID",
        )
        if directory is None:  # pragma: no cover - create always yields fd
            raise _fail("CURATION_CHECKPOINT_WRITE_FAILED", "checkpoint directory missing")
        try:
            descriptor = os.open(
                temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory
            )
            try:
                os.write(descriptor, json.dumps(control, ensure_ascii=False, sort_keys=True).encode("utf-8"))
            finally:
                os.close(descriptor)
            os.replace(temp, name, src_dir_fd=directory, dst_dir_fd=directory)
        finally:
            os.close(directory)
    except OSError as error:
        # The run is already terminal; the cursor stays old and the next
        # window safely rescans. Never consume an unpublished cursor.
        raise _fail(
            "CURATION_CHECKPOINT_WRITE_FAILED", f"{name}: {error}"
        ) from error


# --- bounded note reads (scope precheck BEFORE any read) -----------------------


def _open_bounded_note(project: Project, parts: Sequence[str]) -> int:
    """Open a note through nofollow component walks; never follow symlinks."""
    try:
        dir_fd = os.open(project.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as error:
        raise _fail("CURATION_SCOPE_INVALID", f"{project.root}: {error}") from error
    try:
        for component in ("notes", *parts[:-1]):
            dir_fd, previous = os.open(
                component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=dir_fd
            ), dir_fd
            os.close(previous)
        return os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW, dir_fd=dir_fd)
    except OSError as error:
        raise _fail(
            "CURATION_NOTE_INVALID",
            f"notes/{'/'.join(parts)}: outside the bounded scope ({error})",
        ) from error
    finally:
        os.close(dir_fd)


def _read_bounded(project: Project, parts: Sequence[str], relative: str) -> bytes:
    """Scope precheck (nofollow walk) strictly before the first byte read."""
    fd = _open_bounded_note(project, parts)
    try:
        if not os.fstat(fd).st_mode & 0o170000 == 0o100000:
            raise _fail("CURATION_NOTE_INVALID", f"{relative}: not a regular file")
        chunks = []
        while True:
            chunk = os.read(fd, 1 << 16)
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(fd)


def _open_dir_fd(
    project_root: Path,
    parts: Sequence[str],
    *,
    create: bool = False,
    invalid_code: str = "CURATION_SCOPE_INVALID",
) -> int | None:
    """Open a directory via a verified O_NOFOLLOW component walk.

    Anchors at the Project root (never the process CWD) and walks without
    ever following symlinks. With ``create`` (finalize publish ONLY) every
    missing component is created mode 0700 relative to the verified parent;
    read paths never create (missing -> None). Component walk errors —
    symlinked components (ELOOP), non-directories, unreadable leaves — are
    surfaced as the caller's typed code, never swallowed and never raw.
    """
    base_fd = os.open(project_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    walked: list[int] = [base_fd]
    try:
        for index, component in enumerate(parts):
            try:
                next_fd = os.open(
                    component,
                    os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                    dir_fd=walked[-1],
                )
            except FileNotFoundError:
                if create:
                    os.mkdir(component, 0o700, dir_fd=walked[-1])
                    next_fd = os.open(
                        component,
                        os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                        dir_fd=walked[-1],
                    )
                else:
                    return None
            except NotADirectoryError as error:
                raise _fail(
                    invalid_code,
                    f"{'/'.join(parts[: index + 1])}: component is not a directory ({error})",
                ) from error
            except OSError as error:
                if error.errno == errno.ELOOP:
                    raise _fail(
                        invalid_code,
                        f"{'/'.join(parts[: index + 1])}: symlinked component refused",
                    ) from error
                raise
            walked.append(next_fd)
        return walked.pop()
    finally:
        for descriptor in walked:
            os.close(descriptor)


def _iter_scope_notes(project: Project, parts: Sequence[str]) -> list[tuple[str, Path]]:
    """Enumerate the declared scope through verified O_NOFOLLOW directories.

    Every component (including ``notes``) is opened nofollow BEFORE any
    enumeration, and subdirectories are descended through dir_fd-relative
    nofollow opens — a symlinked component or entry is refused typed instead
    of resolving outside the tree.
    """
    scope_fd = _open_dir_fd(project.root, ("notes", *parts))
    if scope_fd is None:
        raise _fail(
            "CURATION_SCOPE_INVALID", f"notes/{'/'.join(parts)}: no such scope directory"
        )
    selected: list[tuple[str, Path]] = []
    prefix = "notes" + ("/" + "/".join(parts) if parts else "")
    stack: list[tuple[int, str]] = [(scope_fd, prefix)]
    try:
        while stack:
            directory, base = stack.pop()
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        name = entry.name
                        relative = f"{base}/{name}"
                        if entry.is_dir(follow_symlinks=False):
                            if name in _RESERVED_NOTE_NAMES:
                                continue
                            child = os.open(
                                name,
                                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                dir_fd=directory,
                            )
                            stack.append((child, relative))
                        elif name.endswith(".md"):
                            if name in _RESERVED_NOTE_NAMES:
                                continue
                            info = os.stat(name, dir_fd=directory, follow_symlinks=False)
                            if not stat.S_ISREG(info.st_mode):
                                raise _fail(
                                    "CURATION_NOTE_INVALID",
                                    f"{relative}: notes must be regular files",
                                )
                            selected.append((relative, project.root / relative))
                        elif entry.is_symlink():
                            raise _fail(
                                "CURATION_NOTE_INVALID",
                                f"{relative}: symlinked notes are outside the scope",
                            )
            finally:
                os.close(directory)
        selected.sort(key=lambda item: item[0])
        return selected
    except BaseException:
        while stack:
            descriptor, _ = stack.pop()
            os.close(descriptor)
        raise


def _note_identity(project: Project, path: Path, relative: str) -> dict[str, Any]:
    """One consistent bounded read: scope precheck, frontmatter, instant, hash."""
    parts = relative.split("/")
    source = _read_bounded(project, parts[1:], relative)
    document = parse_markdown(source.decode("utf-8"), context=relative)
    if document.frontmatter_range is None or document.frontmatter_range[0] != 0:
        raise _fail("CURATION_NOTE_INVALID", f"{relative}: OKF notes require line-1 frontmatter")
    metadata = document.metadata
    raw_updated = validated_note_updated(metadata.get("updated"), relative)
    if not raw_updated:
        raw_updated = validated_note_updated(metadata.get("created"), relative)
    if not raw_updated:
        raise _fail(
            "CURATION_TIMESTAMP_UNKNOWN",
            f"{relative}: no updated or created timestamp; window membership is "
            "unknown, failing closed instead of sweeping history",
        )
    start, end, uncertain = _parse_note_instant(raw_updated, relative)
    return {
        "path": relative,
        "updated": raw_updated,
        "start": start,
        "end": end,
        "uncertain": uncertain,
        "revision": hashlib.sha256(source).hexdigest(),
        "candidate": note_skill_candidate(metadata, relative),
        "skill_resources": note_skill_resources(metadata, relative),
    }


def _classify(identity: dict[str, Any], lower: datetime, upper: datetime) -> str:
    """Window membership under AC1/AC8: exact instants decide; whole days
    wholly inside may be reviewed with recorded uncertainty, wholly outside
    days are skipped, and boundary overlap is ambiguous (never invented)."""
    if not identity["uncertain"]:
        moment = identity["start"]
        if lower < moment <= upper:
            return _IN_WINDOW
        return _OUT_OF_WINDOW
    start, end = identity["start"], identity["end"]
    if start > lower and end <= upper:
        return _IN_WINDOW
    if end <= lower or start > upper:
        return _OUT_OF_WINDOW
    return _AMBIGUOUS


def _window_identities(
    project: Project, parts: Sequence[str], lower: datetime, upper: datetime
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """One consistent window enumeration shared by prepare and finalize."""
    identities: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for relative, path in _iter_scope_notes(project, parts):
        identity = _note_identity(project, path, relative)
        verdict = _classify(identity, lower, upper)
        if verdict == _IN_WINDOW:
            identities.append(identity)
        elif verdict == _AMBIGUOUS:
            ambiguous.append(
                {
                    "path": relative,
                    "updated": identity["updated"],
                    "reason": (
                        "legacy date-only value overlaps the window boundary; "
                        "a bounded disposition must resolve it before advancement"
                    ),
                }
            )
    return identities, ambiguous


def _snapshot_entries(identities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Candidate-flagged and live-resource notes first (review priority)."""
    return sorted(
        identities,
        key=lambda identity: (
            not (identity["candidate"] or identity["skill_resources"]),
            identity["path"],
        ),
    )


# --- active-run coordination through the EXISTING managed-run lifecycle --------


def _snapshot_payload(run_path: Path) -> dict[str, Any] | None:
    """Read one small authoritative curation snapshot; unreadable -> None."""
    try:
        return json.loads((run_path / "output" / _SNAPSHOT_NAME).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _run_root(worktree: Path) -> Path:
    """Existing managed-run root for the worktree (Git-toplevel resolved)."""
    return kosmic_runs.managed_run_root_path(worktree)


def _retire_expired_run(worktree: Path, run_id: str) -> bool:
    """Close a grace-expired abandoned run via the EXISTING fail mechanism."""
    handles = _run_root(worktree) / "handles"
    try:
        names = sorted(os.listdir(handles))
    except OSError:
        return False
    for name in names:
        handle_file = handles / name
        try:
            data = json.loads(handle_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if data.get("kind") == "handle" and data.get("run_id") == run_id:
            try:
                kosmic_runs.finish_run(handle_file, "failed", detail="expired curation run")
                return True
            except kosmic_runs.RunError:
                return False
    return False


def _manifest_payload(run_path: Path) -> dict[str, Any] | None:
    """Read the small native RUN manifest; unreadable -> None (fail closed)."""
    try:
        return json.loads((run_path / "RUN.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _scope_busy_run(
    project: Project, scope: str, now: datetime
) -> dict[str, Any] | None:
    """Find an ACTIVE run for the same project+scope via existing run state.

    Relevance comes from the native RUN manifest (purpose + provenance
    project), independent of the snapshot: a relevant non-terminal run whose
    snapshot is missing/unreadable is BUSY (fail closed), not skipped — a
    crash between begin and publish still holds the scope. Native
    ``finalizing`` is non-terminal. A partial/truncated report or malformed
    run entries cannot prove absence of a relevant run -> BUSY. Truly
    unrelated purposes/projects are ignored; nothing is killed by guess.
    """
    try:
        report = kosmic_runs.report_runs(project.root, action="status")
    except (kosmic_runs.RunError, kosmic_runs.RunRootError, OSError) as error:
        raise _fail("CURATION_BUSY", f"managed-run status unreadable: {error}") from error
    if getattr(report, "code", "OK") not in ("", "OK"):
        raise _fail(
            "CURATION_BUSY",
            f"managed-run report is {report.code!r}; a partial report cannot "
            "prove the scope is free",
        )
    run_root = _run_root(project.root)
    for entry in report.entries:
        if entry.category in ("malformed", "unattributed") and entry.path.parts[:1] == ("runs",):
            raise _fail(
                "CURATION_BUSY",
                f"{entry.path}: unresolved run entry cannot prove the scope is free",
            )
        if not entry.run_id or entry.state in kosmic_runs.TERMINAL_STATES:
            continue
        manifest = _manifest_payload(run_root / entry.path)
        if manifest is None:
            raise _fail(
                "CURATION_BUSY",
                f"{entry.run_id}: native manifest unreadable on a non-terminal run",
            )
        purpose = str(manifest.get("purpose") or "")
        if manifest.get("project_id") != project.project_id:
            continue  # unrelated Project
        if purpose != f"curation-prepare {scope}":
            # Unrelated purpose OR a different scope inside this Project:
            # the native manifest purpose is exact, so another scope's run
            # (even snapshot-less) never blocks this scope.
            continue
        if entry.state not in ("active", "creating", "finalizing"):
            raise _fail(
                "CURATION_BUSY",
                f"{entry.run_id}: non-terminal managed-run state {entry.state!r}",
            )
        try:
            status = kosmic_runs.run_live_status(project.root, entry.run_id)
        except (kosmic_runs.RunError, kosmic_runs.RunRootError, OSError) as error:
            raise _fail(
                "CURATION_BUSY",
                f"{entry.run_id}: live state unresolved ({error}); refusing to guess",
            ) from error
        if status.get("state") in kosmic_runs.TERMINAL_STATES:
            continue  # authoritatively terminal: completed runs never block
        if status.get("abandoned_candidate"):
            grace_until = status.get("grace_until")
            expired = False
            if grace_until:
                try:
                    expired = _parse_utc_instant(grace_until, "grace_until") <= now
                except CurationError:
                    expired = False
            if expired and _retire_expired_run(project.root, entry.run_id):
                continue  # authoritative terminal via the existing fail path
        snapshot = _snapshot_payload(run_root / entry.path)
        if snapshot is None or snapshot.get("schema") != _SNAPSHOT_SCHEMA:
            raise _fail(
                "CURATION_BUSY",
                f"{entry.run_id}: relevant non-terminal run has no readable "
                "snapshot (crash between begin and publish); scope stays busy",
            )
        return {"run_id": entry.run_id, "path": str(entry.path)}
    return None


def _abandon_our_run(handle_file: Path, worktree: Path, run_id: str, detail: str) -> None:
    """Close OUR reserved run; fail closed while the lease stays unresolved.

    The scope frees only when the run authoritatively reaches a terminal
    state. A refused/unresolved closure raises and the native lease keeps
    serializing the scope — the checkpoint is never advanced here.
    """
    try:
        kosmic_runs.finish_run(handle_file, "failed", detail=detail)
        return
    except kosmic_runs.RunError:
        pass
    try:
        status = kosmic_runs.run_live_status(worktree, run_id)
    except (kosmic_runs.RunError, kosmic_runs.RunRootError, OSError) as error:
        raise _fail(
            "CURATION_ABANDON_UNRESOLVED",
            f"{run_id}: closure failed and state unresolved ({error}); scope stays busy",
        ) from error
    if status.get("state") not in kosmic_runs.TERMINAL_STATES:
        raise _fail(
            "CURATION_ABANDON_REFUSED",
            f"{run_id}: still active after closure attempt; scope stays busy",
        )


# --- stage 1: prepare ---------------------------------------------------------


def prepare_curation(
    project_root: Path,
    *,
    work_record: str,
    scope: str = CURATION_ROOT_SCOPE,
    from_instant: str | None = None,
    baseline: bool = False,
    subset: Sequence[str] = (),
    now: datetime | None = None,
) -> dict[str, Any]:
    """Freeze ``U``, snapshot interval-eligible identities under the managed run.

    Explicit ``--from``/``--baseline`` initialize a first cursor ONLY; once a
    scope checkpoint exists the persisted cursor is the lower bound and any
    provided bound is refused typed (never rewinds or skips history). With no
    checkpoint and no bound the typed first-lower-bound diagnostic fires.
    ``now`` is injectable for fixed-clock tests only. Prepare writes nothing
    under the Project except the managed run itself.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    normalized_scope = normalize_scope(scope)
    upper = now.astimezone(timezone.utc)
    project = load_project(project_root)
    worktree = project.root
    record = kosmic_work.resolve_work_record(worktree, work_record)
    if from_instant is not None and baseline:
        # Exactly one FIRST bound: simultaneous --from and --baseline are
        # refused instead of silently preferring baseline.
        raise _fail(
            "CURATION_LOWER_BOUND_REQUIRED",
            "curation-prepare accepts exactly one first bound: --from <UTC> or "
            "--baseline, never both",
        )

    with _scope_transaction(worktree):
        # Cursor read and window derivation happen INSIDE the native
        # transaction: a finalize landing at transaction entry is observed,
        # so a stale first-run baseline can never skip intervening history.
        control = _read_checkpoint(worktree, normalized_scope)
        cursor = control.get("last_successful")
        if cursor is not None and (from_instant is not None or baseline):
            raise _fail(
                "CURATION_CURSOR_INITIALIZED",
                f"scope {normalized_scope} already has a checkpoint cursor "
                f"({cursor!r}); --from/--baseline are first-run-only and may never "
                "rewind or skip history",
            )
        if cursor is not None:
            lower = _parse_utc_instant(str(cursor), "checkpoint cursor")
        elif baseline:
            lower = upper  # deliberate zero-width first window; scans nothing
        elif from_instant is not None:
            lower = _parse_utc_instant(str(from_instant), "--from")
        else:
            raise _fail(
                "CURATION_LOWER_BOUND_REQUIRED",
                "curation-prepare requires a first lower bound: --from <UTC> or --baseline",
            )
        # (L, U] is legitimately empty when L == U (a deliberate baseline or an
        # unchanged clock); only a bound after the frozen cutoff is invalid.
        if lower > upper:
            raise _fail(
                "CURATION_WINDOW_EMPTY",
                f"lower bound {_utc_instant(lower)} is after the frozen cutoff "
                f"{_utc_instant(upper)}",
            )
        busy = _scope_busy_run(project, normalized_scope, upper)
        if busy:
            raise _fail(
                "CURATION_BUSY",
                f"scope {normalized_scope} already has an active curation run "
                f"{busy['run_id']}; finalize it or let it expire",
            )
        subset_paths = tuple(_bounded_note_path(project, note) for note in subset)
        if len(set(subset_paths)) != len(subset_paths):
            raise _fail("CURATION_NOTE_INVALID", "duplicate --note subset entries")
        identities, ambiguous = _window_identities(
            project, _scope_parts(normalized_scope), lower, upper
        )
        selected = _snapshot_entries(identities)
        mode = "subset"
        if subset_paths:
            known = {entry["path"] for entry in selected}
            missing = sorted(set(subset_paths) - known)
            if missing:
                raise _fail(
                    "CURATION_NOTE_OUT_OF_WINDOW",
                    "--note subset entries are outside this window: " + ", ".join(missing),
                )
            selected = _snapshot_entries(
                [entry for entry in selected if entry["path"] in set(subset_paths)]
            )
        else:
            mode = "full"

        window = {"from": _utc_instant(lower), "until": _utc_instant(upper)}
        provenance = kosmic_work.record_run_provenance(worktree, record.qualified_id, worktree)
        handle = kosmic_runs.begin_run(
            worktree,
            purpose=f"curation-prepare {normalized_scope}",
            retention="diagnostic",
            provenance=provenance,
            project_root=worktree,
        )
        snapshot = {
            "schema": _SNAPSHOT_SCHEMA,
            "run_id": handle.run_id,
            "project_id": project.project_id,
            "scope": normalized_scope,
            "mode": mode,
            "work_record": record.qualified_id,
            "window": window,
            "notes": [
                {
                    "path": entry["path"],
                    "updated": entry["updated"],
                    "revision": entry["revision"],
                    "skill_candidate": entry["candidate"],
                    "skill_resources": entry["skill_resources"],
                    "uncertain": entry["uncertain"],
                }
                for entry in selected
            ],
            "ambiguous": ambiguous,
        }
        snapshot_file = handle.path / "output" / _SNAPSHOT_NAME
        try:
            snapshot_file.parent.mkdir(mode=0o700, exist_ok=True)
            temp = snapshot_file.parent / f".{snapshot_file.name}.{os.getpid()}.tmp"
            descriptor = os.open(
                temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600
            )
            try:
                content = json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode("utf-8")
                os.write(descriptor, content)
            finally:
                os.close(descriptor)
            os.replace(temp, snapshot_file)
        except OSError as error:
            # Publish-before-occupy: an unpublishable snapshot must not leave
            # an active run behind; close the run we just opened.
            _abandon_our_run(handle.handle_file, worktree, handle.run_id, "snapshot unwritable")
            raise _fail("CURATION_SNAPSHOT_WRITE_FAILED", f"{snapshot_file}: {error}") from error

        return {
            "code": "OK",
            "run_id": handle.run_id,
            "handle_file": str(handle.handle_file),
            "snapshot_file": str(snapshot_file),
            "scope": normalized_scope,
            "mode": mode,
            "work_record": record.qualified_id,
            "window": window,
            "notes": snapshot["notes"],
            "ambiguous": ambiguous,
            "checkpoint": {"last_successful": cursor},
        }


def _bounded_note_path(project: Project, value: str) -> str:
    """Normalize a --note subset entry to a bounded ``notes/<relative>`` path."""
    text = str(value or "").strip().replace("\\", "/")
    if not text or text.startswith("/") or ".." in text.split("/"):
        raise _fail("CURATION_NOTE_INVALID", f"{value!r}: expected a note path inside the notes scope")
    parts = [part for part in text.split("/") if part]
    if parts and parts[0] == "notes":
        parts = parts[1:]
    if not parts or parts[-1] in _RESERVED_NOTE_NAMES:
        raise _fail("CURATION_NOTE_INVALID", f"{value!r}: reserved bundle entry")
    fd = _open_bounded_note(project, parts)  # nofollow containment probe
    os.close(fd)
    return "notes/" + "/".join(parts)


# --- work-record review schema (documented; parsed structurally) ---------------


def _parse_review(record_path: Path) -> dict[str, Any]:
    text = record_path.read_text(encoding="utf-8")
    review = parse_markdown(text, context=str(record_path)).metadata.get("curation_review")
    if not isinstance(review, dict):
        raise _fail(
            "CURATION_REVIEW_MISSING",
            "the governing work record carries no curation_review mapping; the "
            "semantic review stage records it there (never the CLI)",
        )
    return review


def _validate_review(
    review: dict[str, Any], run_id: str, prepared: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    if review.get("run_id") != run_id:
        raise _fail(
            "CURATION_REVIEW_MISMATCH",
            f"work-record review run_id {review.get('run_id')!r} does not match "
            f"the prepared run {run_id!r}",
        )
    reviewer = review.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise _fail("CURATION_REVIEW_INVALID", "curation_review.reviewer must name the reviewing agent")
    entries = review.get("notes")
    if not isinstance(entries, list):
        raise _fail("CURATION_REVIEW_INVALID", "curation_review.notes must be a list of dispositions")
    recorded: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise _fail("CURATION_REVIEW_INVALID", f"disposition entry {entry!r} must be a mapping")
        path = entry.get("path")
        if not isinstance(path, str) or not path:
            raise _fail("CURATION_REVIEW_INVALID", "every disposition needs a note path")
        if path in recorded:
            raise _fail("CURATION_REVIEW_INVALID", f"{path}: duplicate disposition")
        disposition = entry.get("disposition")
        if disposition not in DISPOSITIONS:
            raise _fail(
                "CURATION_REVIEW_INVALID",
                f"{path}: disposition {disposition!r}; expected one of {', '.join(DISPOSITIONS)}",
            )
        if disposition == "skipped":
            if not str(entry.get("reason") or "").strip():
                raise _fail("CURATION_REVIEW_INVALID", f"{path}: skipped requires an explicit reason")
            identity = prepared.get(path)
            if identity is not None and (
                identity["skill_candidate"] or identity["skill_resources"]
            ):
                raise _fail(
                    "CURATION_REVIEW_INVALID",
                    f"{path}: only a candidate-false, resource-empty note may be "
                    "deliberately skipped; candidate or live-resource notes need "
                    "reviewed or no-action",
                )
        recorded[path] = entry
    return recorded


# --- stage 3: finalize ---------------------------------------------------------


def finalize_curation(
    project_root: Path,
    *,
    run: str,
    work_record: str,
    scope: str = CURATION_ROOT_SCOPE,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate handle, snapshot identity, coverage, and drift; advance to ``U``.

    The checkpoint publishes ONLY after the managed run closes as
    ``succeeded`` following full review coverage and revalidation. Any
    failure, ambiguity, drift, or targeted subset leaves the cursor
    unchanged. A foreign/invalid finalize never closes another run.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    normalized_scope = normalize_scope(scope)
    handle_file = Path(run).expanduser().resolve()
    project = load_project(project_root)
    worktree = project.root
    record = kosmic_work.resolve_work_record(worktree, work_record)

    try:
        handle_data = json.loads(handle_file.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise _fail("CURATION_HANDLE_INVALID", f"{handle_file}: {error}") from error
    run_id = str(handle_data.get("run_id") or "")
    if not run_id:
        raise _fail("CURATION_HANDLE_INVALID", f"{handle_file}: no run identity")

    with _scope_transaction(worktree):
        try:
            status = kosmic_runs.run_live_status(worktree, run_id)
        except (kosmic_runs.RunError, kosmic_runs.RunRootError, OSError) as error:
            # A foreign/invalid handle names a run this vault cannot open:
            # typed refusal BEFORE any mutation; native errors are caught at
            # this boundary only, never broadly suppressed.
            raise _fail(
                "CURATION_RUN_MISMATCH", f"{run_id}: unopenable/foreign run ({error})"
            ) from error
        state = status.get("state")
        if state in kosmic_runs.TERMINAL_STATES:
            raise _fail(
                "CURATION_RUN_FINISHED",
                f"{run_id} already reached terminal state {state}",
            )
        if state not in ("active", "creating"):
            raise _fail("CURATION_RUN_LOST", f"{run_id}: managed-run state {state!r}")

        run_dir = _run_root(worktree) / "runs" / run_id
        snapshot = _snapshot_payload(run_dir)
        if snapshot is None or snapshot.get("schema") != _SNAPSHOT_SCHEMA:
            raise _fail(
                "CURATION_SNAPSHOT_MISSING", f"{run_dir}: prepared snapshot unreadable"
            )
        if snapshot.get("run_id") != run_id:
            raise _fail("CURATION_SNAPSHOT_INVALID", f"{run_dir}: snapshot does not match the run")
        if snapshot.get("project_id") != project.project_id:
            raise _fail(
                "CURATION_RECORD_MISMATCH",
                f"snapshot project {snapshot.get('project_id')!r} is not this Project; "
                "nothing was modified",
            )
        if snapshot.get("scope") != normalized_scope:
            raise _fail(
                "CURATION_SCOPE_MISMATCH",
                f"snapshot scope {snapshot.get('scope')!r} does not match {normalized_scope!r}",
            )
        if snapshot.get("work_record") != record.qualified_id:
            raise _fail(
                "CURATION_RECORD_MISMATCH",
                f"{record.qualified_id} does not govern the reserved run "
                f"{run_id}; nothing was modified",
            )

        def _abandon(detail: str) -> None:
            _abandon_our_run(handle_file, worktree, run_id, detail)

        try:
            review = _parse_review(record.path)
            recorded = _validate_review(
                review, run_id, {entry["path"]: entry for entry in snapshot["notes"]}
            )
        except CurationError as error:
            _abandon(f"work-record review rejected: {error}")
            raise

        entries = snapshot["notes"]
        prepared_paths = {entry["path"] for entry in entries}
        unexpected = sorted(set(recorded) - prepared_paths)
        if unexpected:
            _abandon("review covers notes outside the prepared snapshot")
            raise _fail(
                "CURATION_REVIEW_OUTSIDE_SNAPSHOT",
                "dispositions cover non-prepared notes: " + ", ".join(unexpected),
            )
        missing = sorted(prepared_paths - set(recorded))
        if missing:
            _abandon("review coverage incomplete")
            raise _fail(
                "CURATION_REVIEW_INCOMPLETE",
                "prepared eligible identities without an explicit disposition: "
                + ", ".join(missing),
            )
        for entry in entries:
            disposition = recorded[entry["path"]]
            if disposition.get("revision") != entry["revision"]:
                _abandon("reviewed revision is stale")
                raise _fail(
                    "CURATION_REVIEW_STALE",
                    f"{entry['path']}: reviewed revision {disposition.get('revision')!r} does "
                    "not match the prepared snapshot identity",
                )

        upper = _parse_utc_instant(snapshot["window"]["until"], "snapshot until")
        for entry in entries:
            path = worktree / entry["path"]
            if not path.is_file():
                _abandon(f"prepared note {entry['path']} disappeared")
                raise _fail("CURATION_DRIFT", f"{entry['path']}: prepared note is missing at finalize")
            current = _note_identity(project, path, entry["path"])
            if current["revision"] == entry["revision"] and current["updated"] == entry["updated"]:
                continue
            try:
                current_instant = _parse_note_instant(current["updated"], entry["path"])[0]
            except CurationError:
                current_instant = None
            if current_instant is not None and current_instant > upper:
                continue  # post-cutoff revision: next run's window, never rewritten here
            _abandon(f"in-window revision drift on {entry['path']}")
            raise _fail(
                "CURATION_DRIFT",
                f"{entry['path']}: changed inside the window after prepare "
                f"(prepared {entry['updated']!r}, now {current['updated']!r})",
            )

        if snapshot.get("mode") == "full":
            lower = _parse_utc_instant(snapshot["window"]["from"], "snapshot from")
            current_identities, current_ambiguous = _window_identities(
                project, _scope_parts(normalized_scope), lower, upper
            )
            fresh = sorted(
                identity["path"]
                for identity in current_identities
                if identity["path"] not in prepared_paths
            )
            recorded_ambiguous = {entry["path"] for entry in (snapshot.get("ambiguous") or [])}
            fresh_ambiguous = sorted(
                entry["path"]
                for entry in current_ambiguous
                if entry["path"] not in recorded_ambiguous
            )
            if fresh or fresh_ambiguous:
                _abandon("window evolved after prepare: newly eligible notes lack review")
                raise _fail(
                    "CURATION_WINDOW_EVOLVED",
                    "notes became eligible inside the window after prepare; prepare "
                    "and review them before advancing the checkpoint: "
                    + ", ".join(fresh + fresh_ambiguous),
                )
            if snapshot.get("ambiguous"):
                _abandon("ambiguous boundary notes block full-scope advancement")
                raise _fail(
                    "CURATION_AMBIGUOUS_BOUNDARY",
                    "legacy date-only notes overlap the window boundary and block "
                    "advancement until a bounded disposition resolves them: "
                    + ", ".join(entry["path"] for entry in snapshot["ambiguous"]),
                )

        advanced = False
        receipt = kosmic_runs.finish_run(handle_file, "succeeded")
        if snapshot.get("mode") == "full":
            _publish_checkpoint(worktree, normalized_scope, snapshot["window"]["until"])
            advanced = True
        return {
            "code": "OK",
            "run_id": run_id,
            "scope": normalized_scope,
            "mode": snapshot.get("mode"),
            "work_record": record.qualified_id,
            "reviewed": len(entries),
            "checkpoint": {"last_successful": snapshot["window"]["until"] if advanced else None},
            "advanced": advanced,
            "run_state": receipt.state,
        }


# --- CLI adapter ---------------------------------------------------------------


def run_cli(args: Any) -> dict[str, Any]:
    """Adapter over the parsed argparse namespace for both curation commands."""
    if args.command == "curation-prepare":
        return prepare_curation(
            Path(args.project),
            work_record=args.work_record,
            scope=getattr(args, "scope", None) or CURATION_ROOT_SCOPE,
            from_instant=getattr(args, "from_instant", None),
            baseline=bool(getattr(args, "baseline", False)),
            subset=tuple(getattr(args, "note", None) or ()),
        )
    if args.command == "curation-finalize":
        return finalize_curation(
            Path(args.project),
            run=args.run,
            work_record=args.work_record,
            scope=getattr(args, "scope", None) or CURATION_ROOT_SCOPE,
        )
    raise _fail("CURATION_COMMAND_UNKNOWN", f"{args.command!r} is not a curation command")
