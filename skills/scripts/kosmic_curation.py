#!/usr/bin/env python3
"""Story 004 deterministic curation stages: prepare and finalize.

One curation job = three explicit stages orchestrated by one outer agent:

1. ``curation-prepare`` (deterministic CLI): freezes the cutoff ``U``
   internally, selects every interval-eligible note (``L < changed <= U``)
   in the declared scope, snapshots revision identities (references only,
   never note bytes) into the managed-run workspace, and reserves the scope
   by atomically recording the active run in ONE per-scope control JSON.
2. Semantic review (an agent, never the CLI): reads the selected notes in
   place and records per-note dispositions into the EXISTING governing work
   record under a documented ``curation_review`` mapping.
3. ``curation-finalize`` (deterministic CLI): verifies the reservation, the
   work-record authority, per-identity disposition coverage, and snapshot
   revalidation, then advances the per-scope checkpoint to exactly ``U``.

The CLI never invokes a model and never infers semantic review from a
process exit status; only recorded dispositions count. A targeted subset
run never advances the full-scope checkpoint. Scope serialization is the
flock-guarded per-scope control JSON plus the managed-run lease: the flock
guards each in-process transaction, and the ``active_run`` reservation
serializes across CLI exits (the flock deliberately dies with the CLI
process; there is no daemon and no queue).

Checkpoint store: ``<project>/.kosmic/curation/<scope>.json`` (one small
per-scope JSON; ``last_successful`` UTC instant plus the active-run
reservation). Nothing else persists beyond the managed-run metadata and the
existing work record.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import re
from dataclasses import dataclass
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
    "CURATION_SCOPES",
    "CurationError",
    "finalize_curation",
    "prepare_curation",
    "run_cli",
]

#: Scopes curation knows today; each keeps an independent checkpoint.
CURATION_SCOPES = ("notes",)

#: Reserved bundle entry points are never atomic concept notes.
_RESERVED_NOTE_NAMES = frozenset({"index.md", "log.md"})

#: Recorded review dispositions (work-record ``curation_review`` schema).
DISPOSITIONS = ("reviewed", "no-action", "skipped")

# Window verdict literals share one source so selection and classification
# can never drift apart.
_IN_WINDOW = "in-window"
_OUT_OF_WINDOW = "out-of-window"
_AMBIGUOUS = "ambiguous"

_UTC_INSTANT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z$")
_CONTROL_SCHEMA = 1
_SNAPSHOT_SCHEMA = 1


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


# --- per-scope control JSON (checkpoint + active-run reservation) ------------


def _curation_dir(project_root: Path) -> Path:
    return Path(project_root) / ".kosmic" / "curation"


def _control_path(project_root: Path, scope: str) -> Path:
    return _curation_dir(project_root) / f"{scope}.json"


def _empty_control(scope: str) -> dict[str, Any]:
    return {
        "schema": _CONTROL_SCHEMA,
        "scope": scope,
        "last_successful": None,
        "active_run": None,
    }


def _read_control(project_root: Path, scope: str) -> dict[str, Any]:
    path = _control_path(project_root, scope)
    try:
        raw = path.read_bytes()
    except FileNotFoundError:
        return _empty_control(scope)
    if path.is_symlink():
        raise _fail("CURATION_CONTROL_INVALID", f"{path}: control file must be a regular file")
    control = json.loads(raw.decode("utf-8"))
    if not isinstance(control, dict) or control.get("scope") != scope:
        raise _fail("CURATION_CONTROL_INVALID", f"{path}: unexpected control content")
    return control


def _write_control(project_root: Path, scope: str, control: dict[str, Any]) -> None:
    directory = _curation_dir(project_root)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    target = _control_path(project_root, scope)
    if target.is_symlink():
        raise _fail("CURATION_CONTROL_INVALID", f"{target}: control file must be a regular file")
    temp = directory / f".{scope}.{os.getpid()}.tmp"
    try:
        descriptor = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            content = json.dumps(control, ensure_ascii=False, sort_keys=True).encode("utf-8")
            os.write(descriptor, content)
        finally:
            os.close(descriptor)
        os.replace(temp, target)
    except OSError as error:
        raise _fail("CURATION_CONTROL_WRITE_FAILED", f"{target}: {error}") from error


def _release_reservation(project_root: Path, scope: str, control: dict[str, Any]) -> None:
    control["active_run"] = None
    _write_control(project_root, scope, control)


@dataclass(frozen=True)
class _ScopeLock:
    """One NOFOLLOW flock per scope, held for a whole prepare/finalize transaction.

    The flock dies with this CLI process; cross-CLI serialization comes from
    the ``active_run`` reservation in the same control JSON, never from a
    pretend-persistent lock.
    """

    descriptor: int

    def release(self) -> None:
        try:
            fcntl.flock(self.descriptor, fcntl.LOCK_UN)
        finally:
            os.close(self.descriptor)


def _scope_lock(project_root: Path, scope: str) -> _ScopeLock:
    directory = _curation_dir(project_root)
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = directory / f"{scope}.lock"
    descriptor = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
    except OSError:
        os.close(descriptor)
        raise
    return _ScopeLock(descriptor)


# --- reservation liveness -----------------------------------------------------


def _reservation_liveness(worktree: Path, reservation: dict[str, Any]) -> str:
    """Classify the reserved run via the existing managed-run status seam.

    Returns ``"busy"``, ``"stale"``, or ``"finished"``; never invents state.
    Unresolved orphans stay ``busy`` (fail closed) — recovery belongs to the
    existing managed-run gc/extend mechanisms, never to a guess here.
    """
    run_id = str(reservation.get("run_id") or "")
    if not run_id:
        return "stale"
    try:
        status = kosmic_runs.run_live_status(worktree, run_id)
    except (kosmic_runs.RunError, kosmic_runs.RunRootError, OSError):
        return "stale"
    state = status.get("state")
    if state in kosmic_runs.TERMINAL_STATES:
        return "finished"
    if state not in ("active", "creating"):
        return "stale"
    if status.get("abandoned_candidate"):
        grace_until = status.get("grace_until")
        if grace_until:
            try:
                if _parse_utc_instant(grace_until, "grace_until") <= datetime.now(timezone.utc):
                    return "stale"
            except CurationError:
                return "busy"
        return "busy"
    return "busy"


def _retire_stale_reservation(
    worktree: Path,
    project_root: Path,
    scope: str,
    control: dict[str, Any],
    reservation: dict[str, Any],
    classification: str,
) -> None:
    """Clear a dead reservation through the EXISTING fail mechanism.

    A reserved run that reached a terminal state (or exceeded the abandon
    grace) releases the scope without touching ``last_successful``. Live or
    unresolved runs are never cleared here (fail closed).
    """
    handle_file = reservation.get("handle_file")
    if classification == "stale" and handle_file and Path(handle_file).is_file():
        try:
            kosmic_runs.finish_run(Path(handle_file), "failed", detail="stale curation reservation")
        except kosmic_runs.RunError:
            pass  # already terminal; the pointer clear below is the recovery
    _release_reservation(project_root, scope, control)


# --- note enumeration and window selection ------------------------------------


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
    resolved = project.notes_dir.joinpath(*parts)
    for parent in resolved.parents:
        if parent.is_symlink():
            raise _fail("CURATION_NOTE_INVALID", f"{value!r}: symlinked parent component")
    if not resolved.is_file() or resolved.is_symlink():
        raise _fail("CURATION_NOTE_INVALID", f"{value!r}: no such regular note under the notes scope")
    return "notes/" + "/".join(parts)


def _iter_scope_notes(project: Project) -> list[tuple[str, Path]]:
    """Existing note enumeration pattern: sorted rglob minus reserved entries."""
    selected: list[tuple[str, Path]] = []
    for path in sorted(project.notes_dir.rglob("*.md")):
        if path.name in _RESERVED_NOTE_NAMES:
            continue
        relative = path.relative_to(project.root).as_posix()
        selected.append((relative, path))
    return selected


def _note_identity(project: Project, path: Path, relative: str) -> dict[str, Any]:
    """One consistent read per note: frontmatter, semantic instant, hash."""
    try:
        source = path.read_bytes()
    except OSError as error:
        raise _fail("CURATION_NOTE_UNREADABLE", f"{relative}: {error}") from error
    if path.is_symlink():
        raise _fail("CURATION_NOTE_INVALID", f"{relative}: symlinked notes are outside the scope")
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


def _snapshot_entries(identities: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Candidate-flagged and live-resource notes first (review priority)."""
    return sorted(
        identities,
        key=lambda identity: (
            not (identity["candidate"] or identity["skill_resources"]),
            identity["path"],
        ),
    )


# --- stage 1: prepare ---------------------------------------------------------


def _window_identities(
    project: Project, lower: datetime, upper: datetime
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """One consistent window enumeration shared by prepare and finalize.

    Returns ``(identities, ambiguous)`` for every note in the scope under
    ``L < semantic instant <= U``; date-only boundary overlaps are recorded
    as ambiguous, never dropped and never given invented instants.
    """
    identities: list[dict[str, Any]] = []
    ambiguous: list[dict[str, Any]] = []
    for relative, path in _iter_scope_notes(project):
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


def prepare_curation(
    project_root: Path,
    *,
    work_record: str,
    scope: str = "notes",
    from_instant: str | None = None,
    baseline: bool = False,
    subset: Sequence[str] = (),
    now: datetime | None = None,
) -> dict[str, Any]:
    """Freeze ``U``, snapshot interval-eligible identities, reserve the scope.

    ``now`` is injectable for fixed-clock tests; the CLI passes real time and
    there is no production clock backdoor. Returns the machine-JSON payload.
    """
    if now is None:
        now = datetime.now(timezone.utc)
    if scope not in CURATION_SCOPES:
        raise _fail("CURATION_SCOPE_UNKNOWN", f"{scope!r}: supported scopes: {', '.join(CURATION_SCOPES)}")
    if bool(from_instant) == bool(baseline):
        raise _fail(
            "CURATION_LOWER_BOUND_REQUIRED",
            "curation-prepare requires exactly one first lower bound: --from <UTC> or --baseline",
        )
    upper = now.astimezone(timezone.utc)
    if baseline:
        # Deliberate zero-width baseline: an empty window by design; prior
        # notes are neither swept nor rejected.
        lower = upper
    else:
        lower = _parse_utc_instant(str(from_instant), "--from")
        if lower >= upper:
            raise _fail(
                "CURATION_WINDOW_EMPTY",
                f"--from {from_instant} is not before the frozen cutoff {_utc_instant(upper)}",
            )

    project = load_project(project_root)
    worktree = project.root
    # Authority is re-resolved at invocation time (approved/in_progress record).
    record = kosmic_work.resolve_work_record(worktree, work_record)

    subset_paths = tuple(_bounded_note_path(project, note) for note in subset)
    if len(set(subset_paths)) != len(subset_paths):
        raise _fail("CURATION_NOTE_INVALID", "duplicate --note subset entries")

    lock = _scope_lock(worktree, scope)
    try:
        control = _read_control(worktree, scope)
        reservation = control.get("active_run")
        if reservation:
            classification = _reservation_liveness(worktree, reservation)
            if classification == "busy":
                raise _fail(
                    "CURATION_BUSY",
                    f"scope {scope} already has an active curation run "
                    f"{reservation.get('run_id')}; finalize it or let it expire",
                )
            _retire_stale_reservation(worktree, worktree, scope, control, reservation, classification)
            control = _read_control(worktree, scope)

        identities, ambiguous = _window_identities(project, lower, upper)

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
            purpose=f"curation-prepare {scope}",
            retention="diagnostic",
            provenance=provenance,
            project_root=worktree,
        )
        snapshot = {
            "schema": _SNAPSHOT_SCHEMA,
            "run_id": handle.run_id,
            "scope": scope,
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
        reservation = {
            "run_id": handle.run_id,
            "handle_file": str(handle.handle_file),
            "snapshot_file": str(handle.path / "output" / "curation-snapshot.json"),
            "work_record": record.qualified_id,
            "mode": mode,
            "prepared_at": _utc_instant(upper),
            "window": window,
            "notes": len(snapshot["notes"]),
            "ambiguous": len(ambiguous),
        }
        control["active_run"] = reservation
        _write_control(worktree, scope, control)

        snapshot_file = Path(reservation["snapshot_file"])
        snapshot_file.parent.mkdir(mode=0o700, exist_ok=True)
        temp = snapshot_file.parent / f".{snapshot_file.name}.{os.getpid()}.tmp"
        try:
            descriptor = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
            try:
                content = json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode("utf-8")
                os.write(descriptor, content)
            finally:
                os.close(descriptor)
            os.replace(temp, snapshot_file)
        except OSError as error:
            raise _fail("CURATION_SNAPSHOT_WRITE_FAILED", f"{snapshot_file}: {error}") from error

        return {
            "code": "OK",
            "run_id": handle.run_id,
            "handle_file": str(handle.handle_file),
            "snapshot_file": str(snapshot_file),
            "scope": scope,
            "mode": mode,
            "work_record": record.qualified_id,
            "window": window,
            "notes": snapshot["notes"],
            "ambiguous": ambiguous,
            "checkpoint": {"last_successful": control.get("last_successful")},
        }
    finally:
        lock.release()


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


def _validate_review(review: dict[str, Any], run_id: str) -> dict[str, dict[str, Any]]:
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
        if disposition == "skipped" and not str(entry.get("reason") or "").strip():
            raise _fail("CURATION_REVIEW_INVALID", f"{path}: skipped requires an explicit reason")
        recorded[path] = entry
    return recorded


# --- stage 3: finalize ---------------------------------------------------------


def finalize_curation(
    project_root: Path,
    *,
    run: str,
    work_record: str,
    scope: str = "notes",
    now: datetime | None = None,
) -> dict[str, Any]:
    """Validate the reservation, review coverage, and drift; advance to ``U``.

    Full-scope success with every prepared identity explicitly dispositioned
    advances ``last_successful`` to exactly the frozen ``U``. Any failure,
    ambiguity, drift, or targeted subset leaves the checkpoint unchanged
    (subset runs never advance it). Failures of the reserved run release the
    scope reservation without advancing; a foreign/invalid finalize never
    touches another run's lease.
    """
    if scope not in CURATION_SCOPES:
        raise _fail("CURATION_SCOPE_UNKNOWN", f"{scope!r}: supported scopes: {', '.join(CURATION_SCOPES)}")
    handle_file = Path(run).expanduser().resolve()
    project = load_project(project_root)
    worktree = project.root
    record = kosmic_work.resolve_work_record(worktree, work_record)

    lock = _scope_lock(worktree, scope)
    try:
        control = _read_control(worktree, scope)
        reservation = control.get("active_run")
        if not reservation:
            raise _fail("CURATION_NOT_RESERVED", f"scope {scope} has no active curation run to finalize")
        if reservation.get("work_record") != record.qualified_id:
            # Foreign record: fail without touching the other run's lease.
            raise _fail(
                "CURATION_RECORD_MISMATCH",
                f"{record.qualified_id} does not govern the reserved run "
                f"{reservation.get('run_id')}; nothing was modified",
            )
        if Path(str(reservation.get("handle_file") or "")).resolve() != handle_file:
            raise _fail(
                "CURATION_RUN_MISMATCH",
                f"--run {run} does not match the reserved run {reservation.get('run_id')}",
            )
        run_id = str(reservation["run_id"])
        status = kosmic_runs.run_live_status(worktree, run_id)
        if status.get("state") in kosmic_runs.TERMINAL_STATES:
            _release_reservation(worktree, scope, control)
            raise _fail(
                "CURATION_RUN_FINISHED",
                f"{run_id} already reached terminal state {status.get('state')}",
            )
        if status.get("state") not in ("active", "creating"):
            _release_reservation(worktree, scope, control)
            raise _fail("CURATION_RUN_LOST", f"{run_id}: managed-run state {status.get('state')!r}")

        def _abandon(detail: str) -> None:
            """Fail OUR reserved run and release the scope; checkpoint unchanged."""
            try:
                kosmic_runs.finish_run(handle_file, "failed", detail=detail)
            except kosmic_runs.RunError:
                pass
            _release_reservation(worktree, scope, control)

        snapshot_file = Path(str(reservation.get("snapshot_file") or ""))
        try:
            snapshot = json.loads(snapshot_file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _abandon("curation snapshot metadata unreadable")
            raise _fail("CURATION_SNAPSHOT_MISSING", f"{snapshot_file}: prepared snapshot unreadable")
        if snapshot.get("schema") != _SNAPSHOT_SCHEMA or snapshot.get("run_id") != run_id:
            _abandon("curation snapshot identity mismatch")
            raise _fail("CURATION_SNAPSHOT_INVALID", f"{snapshot_file}: snapshot does not match the run")

        try:
            review = _parse_review(record.path)
            recorded = _validate_review(review, run_id)
        except CurationError as error:
            # Missing/invalid review schema: fail OUR reserved run and release
            # the scope exactly as the routine promises; checkpoint unchanged.
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

        # Revalidate every prepared identity against current instants/bytes.
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

        # Re-enumerate the window: a full-scope advance must not move the
        # cursor past notes that became eligible after prepare (new in-window
        # notes or newly ambiguous boundary overlaps). Post-U revisions
        # reclassify out of the window and never block here. Subset runs
        # never advance, so they need no cursor-safety recheck.
        if snapshot.get("mode") == "full":
            lower = _parse_utc_instant(snapshot["window"]["from"], "snapshot from")
            current_identities, current_ambiguous = _window_identities(project, lower, upper)
            prepared_paths_now = {entry["path"] for entry in entries}
            fresh = sorted(
                identity["path"]
                for identity in current_identities
                if identity["path"] not in prepared_paths_now
            )
            recorded_ambiguous = {entry["path"] for entry in (snapshot.get("ambiguous") or [])}
            fresh_ambiguous = sorted(
                entry["path"] for entry in current_ambiguous if entry["path"] not in recorded_ambiguous
            )
            if fresh or fresh_ambiguous:
                _abandon("window evolved after prepare: newly eligible notes lack review")
                raise _fail(
                    "CURATION_WINDOW_EVOLVED",
                    "notes became eligible inside the window after prepare; prepare "
                    "and review them before advancing the checkpoint: "
                    + ", ".join(fresh + fresh_ambiguous),
                )

        ambiguous = snapshot.get("ambiguous") or []
        if ambiguous and snapshot.get("mode") == "full":
            _abandon("ambiguous boundary notes block full-scope advancement")
            raise _fail(
                "CURATION_AMBIGUOUS_BOUNDARY",
                "legacy date-only notes overlap the window boundary and block "
                "advancement until a bounded disposition resolves them: "
                + ", ".join(entry["path"] for entry in ambiguous),
            )

        advanced = False
        if snapshot.get("mode") == "full":
            control["last_successful"] = snapshot["window"]["until"]
            advanced = True
        receipt = kosmic_runs.finish_run(handle_file, "succeeded")
        _release_reservation(worktree, scope, control)
        return {
            "code": "OK",
            "run_id": run_id,
            "scope": scope,
            "mode": snapshot.get("mode"),
            "work_record": record.qualified_id,
            "reviewed": len(entries),
            "checkpoint": {"last_successful": control.get("last_successful")},
            "advanced": advanced,
            "run_state": receipt.state,
        }
    finally:
        lock.release()


# --- CLI adapter ---------------------------------------------------------------


def run_cli(args: Any) -> dict[str, Any]:
    """Adapter over the parsed argparse namespace for both curation commands."""
    if args.command == "curation-prepare":
        return prepare_curation(
            Path(args.project),
            work_record=args.work_record,
            scope=getattr(args, "scope", None) or "notes",
            from_instant=getattr(args, "from_instant", None),
            baseline=bool(getattr(args, "baseline", False)),
            subset=tuple(getattr(args, "note", None) or ()),
        )
    if args.command == "curation-finalize":
        return finalize_curation(
            Path(args.project),
            run=args.run,
            work_record=args.work_record,
            scope=getattr(args, "scope", None) or "notes",
        )
    raise _fail("CURATION_COMMAND_UNKNOWN", f"{args.command!r} is not a curation command")
