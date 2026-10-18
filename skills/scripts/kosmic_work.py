"""Project-bound working-directory registry and Revision 2 work records.

Story 071 implements AD-SW4: a versioned Project registry
(``<project>/.kosmic/working-directories.json``, schema ``kosmic.workdirs/1``)
lists registered working directories by canonical path and directory ID.
Registration binds a directory to its Project and an optional fixed-subproject
constraint; it never selects an active task. One Project may register several
Git worktrees; two Projects can never register the same directory.

Initial registration needs no prior registry entry: ``begin_registration``
issues a registration-only context backed by a managed-run handle when an
approved project-level Quick Task explicitly declares the root and the
registration outputs.

Architecture Revision 2 (AD-SW5-R2/SW7-R2) replaces leased work sessions with
explicit work-record references: mutating commands resolve the governing
record at invocation time, writable work starts from a clean worktree, and
the worktree diff is the change attribution checked at completion.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import stat
import subprocess
import time
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from .kosmic_runs import (
        ACTIVE_DEFAULT, RunError, RunHandle, begin_run, run_live_status,
    )
    from .kosmic_specs import SpecCatalog, SpecError, SpecRef, read_document
except ImportError:
    from kosmic_runs import (
        ACTIVE_DEFAULT, RunError, RunHandle, begin_run, run_live_status,
    )
    from kosmic_specs import SpecCatalog, SpecError, SpecRef, read_document

WORKDIRS_SCHEMA = "kosmic.workdirs/1"
WORKDIR_ENTRY_SCHEMA = "kosmic.workdir/1"
BINDING_SCHEMA = "kosmic.workdir-binding/1"
REGISTRY_RELATIVE = ".kosmic/working-directories.json"
BINDING_RELATIVE = ".kosmic/workdir.json"
REGISTRY_LIMIT = 1 << 20

REGISTRATION_OPERATIONS = ("workdir-register", "registration-evidence")
REQUIRED_OUTPUTS = (REGISTRY_RELATIVE, "worktree:.kosmic/workdir.json")

#: Lifecycle statuses that authorize implementation or registration work.
AUTHORIZED_STATUSES = ("approved", "in_progress", "review")
IMPLEMENTATION_STATUSES = ("approved", "in_progress")
IMPLEMENTATION_KINDS = ("story", "quick-task")

#: Upper bound on waiting for a coordination flock so a lost holder can never
#: hang a caller or a whole test suite indefinitely.
LOCK_TIMEOUT_SECONDS = 120.0


class WorkdirError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


def _deny(condition: bool, code: str, detail: str = "") -> None:
    if condition:
        raise WorkdirError(code, detail)


def _run_git(worktree: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(worktree), *arguments],
        check=False, capture_output=True, text=True,
    )
    if completed.returncode:
        detail = completed.stderr.strip() or completed.stdout.strip() or "git command failed"
        raise WorkdirError("WORKTREE_INVALID", f"{worktree}: {detail}")
    return completed.stdout


def directory_id(path: Path) -> str:
    return "wd-" + hashlib.sha256(str(_canonical_directory(path)).encode()).hexdigest()[:16]


def _canonical_directory(path: Path | str) -> Path:
    """Canonical directory path, refusing symlinks and traversal inputs."""
    raw = Path(path)
    _deny(".." in raw.parts, "ROOT_INVALID", f"{raw}: path traversal is not a root")
    _deny(os.path.islink(raw), "ROOT_INVALID", f"{raw}: symlink is not a root")
    try:
        canonical = raw.resolve(strict=True)
    except OSError as error:
        raise WorkdirError("ROOT_INVALID", f"{raw}: {error}") from error
    _deny(not canonical.is_dir(), "ROOT_INVALID", f"{raw}: not a directory")
    _deny(os.path.islink(canonical), "ROOT_INVALID", f"{raw}: resolves through a symlink")
    return canonical


def _utcnow() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _open_control_directory(base: Path, relative: str) -> int:
    """Open a control subdirectory through no-follow descriptors."""
    parts = Path(relative).parts
    _deny(not parts or relative.startswith("/"), "STATE_INVALID", relative)
    fd = os.open(base, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        for part in parts:
            try:
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                                | os.O_CLOEXEC, dir_fd=fd)
            except FileNotFoundError:
                os.mkdir(part, 0o700, dir_fd=fd)
                child = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
                                | os.O_CLOEXEC, dir_fd=fd)
            os.close(fd)
            fd = child
    except OSError:
        os.close(fd)
        raise
    return fd


def _atomic_write(base: Path, relative: str, payload: bytes) -> None:
    """Write payload through a no-follow directory walk, rename-atomically."""
    target = Path(relative)
    _deny(not target.parts or target.is_absolute() or ".." in target.parts,
          "STATE_INVALID", relative)
    parent_fd = _open_control_directory(base, str(target.parent)) if target.parent != Path(".") \
        else os.open(base, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    try:
        temporary = f".{target.name}.{os.getpid()}.tmp"
        fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                     0o600, dir_fd=parent_fd)
        try:
            os.write(fd, payload)
            os.fsync(fd)
        finally:
            os.close(fd)
        os.rename(temporary, target.name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def _read_bounded(base: Path, relative: str) -> bytes | None:
    """Read a bounded regular file no-follow; None only when truly absent."""
    try:
        fd = os.open(Path(base) / relative, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return None
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > REGISTRY_LIMIT:
            raise WorkdirError("REGISTRY_INVALID", f"{relative}: not a bounded regular file")
        return os.read(fd, REGISTRY_LIMIT + 1)
    finally:
        os.close(fd)


def _validated_registry(document: Any, project_id: str) -> dict[str, Any]:
    _deny(not isinstance(document, dict) or document.get("schema") != WORKDIRS_SCHEMA
          or document.get("project_id") != project_id, "REGISTRY_INVALID",
          "schema or project identity mismatch")
    directories = document.get("directories")
    _deny(not isinstance(directories, list), "REGISTRY_INVALID", "directories")
    sequence = document.get("sequence")
    _deny(not isinstance(sequence, int) or isinstance(sequence, bool)
          or sequence != len(directories), "REGISTRY_INVALID",
          "sequence disagrees with directories")
    seen: set[str] = set()
    for entry in directories:
        _deny(not isinstance(entry, dict) or entry.get("schema") != WORKDIR_ENTRY_SCHEMA,
              "REGISTRY_INVALID", "entry schema")
        path = entry.get("path")
        _deny(not isinstance(path, str) or not path, "REGISTRY_INVALID", "entry path")
        _deny(path in seen, "REGISTRY_INVALID", f"duplicate directory {path}")
        seen.add(path)
        _deny(entry.get("directory_id") != "wd-" + hashlib.sha256(path.encode()).hexdigest()[:16],
              "REGISTRY_INVALID", f"directory_id does not match {path}")
        fixed = entry.get("fixed_subproject_id")
        _deny(fixed is not None and not isinstance(fixed, str), "REGISTRY_INVALID", "fixed subproject")
        authority = entry.get("authority")
        _deny(not isinstance(authority, dict) or not authority.get("record")
              or not authority.get("run_id"), "REGISTRY_INVALID", "entry authority")
    return document


def load_registry(project_root: Path) -> dict[str, Any]:
    """Load and validate the registry; unsafe state fails closed."""
    root = Path(project_root).expanduser().resolve()
    registry = root / REGISTRY_RELATIVE
    _deny(os.path.islink(registry), "REGISTRY_INVALID", f"{REGISTRY_RELATIVE}: symlink")
    payload = _read_bounded(root, REGISTRY_RELATIVE)
    if payload is None:
        return {"schema": WORKDIRS_SCHEMA, "project_id": _project_identity(root)[1],
                "sequence": 0, "directories": []}
    try:
        document = json.loads(payload.decode("utf-8"))
    except (ValueError, UnicodeError) as error:
        raise WorkdirError("REGISTRY_INVALID", f"{REGISTRY_RELATIVE}: invalid JSON") from error
    return _validated_registry(document, _project_identity(root)[1])


def _project_identity(project_root: Path) -> tuple[Path, str]:
    root = Path(project_root).expanduser().resolve()
    entry = root / "ProjectEntry.md"
    _deny(os.path.islink(entry) or not entry.is_file(), "PROJECT_INVALID",
          f"{root}: ProjectEntry.md missing")
    text = entry.read_text(encoding="utf-8")
    match = None
    import re
    match = re.search(r"^project_id:\s*[\"']?([\w.-]+)[\"']?\s*$", text, re.M)
    _deny(match is None, "PROJECT_INVALID", f"{root}: project_id missing")
    return root, match.group(1)


@dataclass(frozen=True)
class RegistrationContext:
    """Registration-only authority: the Quick Task record plus its run."""

    project_id: str
    project_root: Path
    worktree: Path
    directory_id: str
    record: str
    record_kind: str
    outputs: tuple[str, ...]
    run: RunHandle
    created_at: str

    def permits(self, operation: str) -> bool:
        return operation in REGISTRATION_OPERATIONS


def begin_registration(
    project_root: Path,
    worktree: Path,
    quick_task: str,
    *,
    active_for: Any = None,
) -> RegistrationContext:
    """Issue a registration-only context for an unregistered root.

    Requires an approved (or in-progress) project-level Quick Task whose
    ``registration_root`` names exactly this canonical worktree and whose
    ``registration_outputs`` declare the registry and worktree binding outputs.
    """
    root, project_id = _project_identity(project_root)
    catalog = SpecCatalog(root)
    try:
        record = catalog.resolve(quick_task, owner=None, kind="quick-task")
    except SpecError as error:
        raise WorkdirError("RECORD_INVALID", str(error)) from error
    _deny(record.subproject_id is not None, "RECORD_INVALID",
          "bootstrap requires a project-level Quick Task")
    _deny(record.status not in AUTHORIZED_STATUSES, "RECORD_NOT_AUTHORIZED",
          f"{record.qualified_id}: {record.status!r}")
    canonical = _canonical_directory(worktree)
    declared_root = record.metadata.get("registration_root")
    _deny(not isinstance(declared_root, str), "ROOT_MISMATCH", "registration_root missing")
    try:
        declared_canonical = _canonical_directory(declared_root)
    except WorkdirError as error:
        raise WorkdirError("ROOT_MISMATCH", f"registration_root: {error}") from error
    _deny(declared_canonical != canonical, "ROOT_MISMATCH",
          f"{declared_root} does not name {canonical}")
    outputs = record.metadata.get("registration_outputs")
    _deny(not isinstance(outputs, (list, tuple))
          or not all(isinstance(item, str) for item in outputs),
          "OUTPUTS_UNDECLARED", "registration_outputs must be a list of strings")
    _deny(any(required not in outputs for required in REQUIRED_OUTPUTS),
          "OUTPUTS_UNDECLARED", f"expected {list(REQUIRED_OUTPUTS)}")

    binding = _read_bounded(canonical, BINDING_RELATIVE)
    if binding is not None:
        try:
            bound = json.loads(binding.decode("utf-8"))
        except ValueError as error:
            raise WorkdirError("REGISTRY_INVALID", "unreadable worktree binding") from error
        _deny(bound.get("project_id") not in (None, project_id), "CROSS_PROJECT_DENIED",
              f"{canonical} is already registered by project {bound.get('project_id')!r}")
    registered = load_registry(root)["directories"]
    _deny(any(entry["path"] == str(canonical) for entry in registered),
          "DIRECTORY_REGISTERED", str(canonical))

    handle = begin_run(
        canonical, f"workdir-register {record.qualified_id}", "diagnostic",
        active_for or ACTIVE_DEFAULT,
        provenance={"project_id": project_id, "governing_record": record.qualified_id,
                    "record_path": record.path.relative_to(root).as_posix()},
        project_root=root,
    )
    return RegistrationContext(
        project_id=project_id, project_root=root, worktree=canonical,
        directory_id=directory_id(canonical), record=record.qualified_id,
        record_kind=record.kind, outputs=tuple(outputs), run=handle,
        created_at=handle.path.name.split("-")[0],
    )


@contextmanager
def _registry_lock(project_root: Path, *, name: str = "workdirs.lock"):
    root = Path(project_root).expanduser().resolve()
    control = root / ".kosmic"
    control.mkdir(mode=0o700, parents=True, exist_ok=True)
    lock_path = control / name
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                _deny(time.monotonic() >= deadline, "REGISTRY_BUSY", name)
                time.sleep(0.05)
        yield
    finally:
        os.close(fd)


def _checked_registration(context: RegistrationContext) -> tuple[SpecRef, dict[str, Any]]:
    """Re-resolve live authority: record status, declared outputs, run liveness."""
    catalog = SpecCatalog(context.project_root)
    try:
        record = catalog.resolve(context.record, owner=None, kind="quick-task")
    except SpecError as error:
        raise WorkdirError("RECORD_NOT_AUTHORIZED", str(error)) from error
    _deny(record.status not in AUTHORIZED_STATUSES, "RECORD_NOT_AUTHORIZED",
          f"{record.qualified_id}: {record.status!r}")
    outputs = record.metadata.get("registration_outputs")
    _deny(tuple(outputs or ()) != context.outputs, "CONTEXT_INVALID",
          "declared registration outputs changed")
    try:
        live = run_live_status(context.worktree, context.run.run_id)
    except RunError as error:
        raise WorkdirError("CONTEXT_INVALID", str(error)) from error
    _deny(live.get("state") != "active", "CONTEXT_INVALID", "registration run is not live")
    return record, live


def register_workdir(context: RegistrationContext, *, subproject_id: str | None = None) -> dict[str, Any]:
    """Publish the registry entry and worktree binding for a live context."""
    record, _ = _checked_registration(context)
    root = context.project_root
    if subproject_id is not None:
        entry_file = root / "subprojects" / subproject_id / "SubprojectEntry.md"
        _deny(not entry_file.is_file(), "SUBPROJECT_UNKNOWN", subproject_id)
    with _registry_lock(root):
        registry = load_registry(root)
        paths = [entry["path"] for entry in registry["directories"]]
        _deny(str(context.worktree) in paths, "DIRECTORY_REGISTERED", str(context.worktree))
        entry = {
            "schema": WORKDIR_ENTRY_SCHEMA,
            "path": str(context.worktree),
            "directory_id": context.directory_id,
            "fixed_subproject_id": subproject_id,
            "registered_at": _utcnow(),
            "authority": {"record": context.record, "run_id": context.run.run_id},
        }
        document = {**registry, "sequence": len(registry["directories"]) + 1,
                    "directories": [*registry["directories"], entry]}
        payload = (json.dumps(document, sort_keys=True, indent=2) + "\n").encode()
        _deny(len(payload) > REGISTRY_LIMIT, "REGISTRY_INVALID", "registry too large")
        binding = (json.dumps({"schema": BINDING_SCHEMA, "project_id": context.project_id,
                               "directory_id": context.directory_id},
                              sort_keys=True, indent=2) + "\n").encode()
        _atomic_write(root, REGISTRY_RELATIVE, payload)
        _atomic_write(context.worktree, BINDING_RELATIVE, binding)
    return entry


def resolve_directory(project_root: Path, worktree: Path) -> dict[str, Any]:
    """Exact registered-directory lookup, honoring the worktree binding."""
    root, project_id = _project_identity(project_root)
    registry = load_registry(root)
    try:
        resolved = Path(worktree).expanduser().resolve(strict=True)
    except OSError as error:
        raise WorkdirError("NOT_REGISTERED", f"{worktree}: {error}") from error
    entry = None
    canonical = resolved
    for candidate in (resolved, *resolved.parents):
        entry = next((item for item in registry["directories"]
                      if item["path"] == str(candidate)), None)
        if entry is not None:
            canonical = candidate
            break
    _deny(entry is None, "NOT_REGISTERED", str(resolved))
    binding = _read_bounded(canonical, BINDING_RELATIVE)
    _deny(binding is None, "BINDING_MISMATCH", f"{canonical}: worktree binding missing")
    try:
        bound = json.loads(binding.decode("utf-8"))
    except ValueError as error:
        raise WorkdirError("BINDING_MISMATCH", "unreadable binding") from error
    _deny(bound.get("project_id") != project_id
          or bound.get("directory_id") != entry["directory_id"],
          "BINDING_MISMATCH", str(canonical))
    return entry


# -- Revision 2: explicit work-record references (AD-SW5-R2/SW7-R2) --------

def resolve_work_record(project_root: Path, reference: str,
                        *, kinds: Sequence[str] = IMPLEMENTATION_KINDS,
                        statuses: Sequence[str] | None = None,
                        allow_terminal: bool = False) -> SpecRef:
    """Resolve an explicit work-record reference at command time.

    Re-resolved on every invocation; approval is never cached. The record
    must belong to this Project, hold the caller's kind, hold an
    authorized status, and (Stories) approved ancestry.

    ``kinds`` and ``statuses`` let one bounded caller re-authorize this same
    seam (ADR-E: ``generate-status`` passes union sets and then applies its
    own selective record matrix); the defaults leave every other caller on
    the implementation kinds/statuses unchanged.

    Authorization is record-bound: when the whole Project catalog cannot be
    enumerated, the record is resolved from its owner subtree plus the shared
    records (``SpecCatalog.bounded_for_reference``), so defects in unrelated
    subprojects never block this record. The record's own identity, ancestry,
    and lifecycle checks are the catalog's own and stay enforced.
    """
    root = Path(project_root).expanduser().resolve()
    _deny(not isinstance(reference, str) or not reference.strip(),
          "WORK_RECORD_REQUIRED", "mutating commands require --work-record")
    text = reference.strip()
    try:
        catalog = SpecCatalog(root)
        record = catalog.resolve(text, owner=None)
    except SpecError as error:
        if error.code == "MIGRATION_REQUIRED":
            # Flat Quick Tasks are bounded bootstrap records until the separately
            # approved subproject migration. They remain valid work authority.
            record = _resolve_flat_quick_task(root, text)
            catalog = None
        else:
            # Record-bound seam: unrelated subprojects are never enumerated.
            try:
                catalog = SpecCatalog.bounded_for_reference(root, text)
                record = catalog.resolve(text, owner=None)
            except SpecError as bounded_error:
                raise WorkdirError("RECORD_INVALID", str(bounded_error)) from bounded_error
    _deny(record.kind not in kinds, "WORK_PHASE_DENIED",
          f"{record.qualified_id}: {record.kind} is not an authorized record kind")
    base_statuses = IMPLEMENTATION_STATUSES if statuses is None else tuple(statuses)
    allowed_statuses = (*base_statuses, "done") if allow_terminal else base_statuses
    _deny(record.status not in allowed_statuses, "WORK_PHASE_DENIED",
          f"{record.qualified_id}: status {record.status!r} does not authorize this command")
    if record.kind == "story" and catalog is not None:
        _ancestry_approved(catalog, record)
    return record


def _resolve_flat_quick_task(root: Path, reference: str) -> SpecRef:
    project_id = _project_identity(root)[1]
    parts = reference.split("/")
    requested_local = parts[-1]
    requested_path = Path(reference)
    if len(parts) > 1 and parts[0] == "specs":
        requested_path = root / requested_path
        requested_local = requested_path.stem
    candidates = sorted((root / "specs" / "quick-tasks").glob("*.md"))
    if requested_path.is_absolute():
        candidates.insert(0, requested_path)
    for path in candidates:
        if not path.is_file() or path.is_symlink():
            continue
        document = read_document(root, path)
        metadata = document.metadata
        if (metadata.get("project_id") != project_id
                or metadata.get("record_kind") != "quick-task"
                or metadata.get("subproject_id") not in (None, "", "null")
                or not metadata.get("local_id")):
            continue
        local_id = str(metadata["local_id"])
        if requested_local not in (local_id, path.stem):
            continue
        title = next((line[2:].strip() for line in document.body.splitlines()
                      if line.startswith("# ")), path.stem)
        return SpecRef(project_id, None, "quick-task", local_id, path, metadata, title)
    raise WorkdirError("RECORD_INVALID", f"{reference}: no canonical flat Quick Task")





def _ancestry_approved(catalog: SpecCatalog, record: SpecRef) -> None:
    """Every spec ancestor must be approved or done; a revoked or draft
    ancestor blocks implementation."""
    for parent in catalog.ancestry(record):
        _deny(parent.effective_status not in ("approved", "done"), "ANCESTRY_INVALID",
              f"{parent.qualified_id}: ancestor status {parent.effective_status!r}")


def _normalize_claim(text: str) -> tuple[str, str]:
    root, separator, relative = str(text).partition(":")
    _deny(not separator or root not in ("worktree", "project"), "SCOPE_INVALID",
          f"{text!r}: expected worktree:PATH or project:PATH")
    parts = tuple(part for part in relative.strip("/").split("/") if part)
    _deny(not parts or ".." in parts, "SCOPE_INVALID", f"{text!r}: unsafe relative path")
    return root, "/".join(parts)


def changed_worktree_paths(worktree: Path) -> list[str]:
    """Every path changed in the worktree relative to HEAD (porcelain -z)."""
    out = _run_git(Path(worktree), "status", "--porcelain=v1", "-z", "--untracked-files=all")
    paths: list[str] = []
    entries = [item for item in out.split("\0") if item]
    index = 0
    while index < len(entries):
        entry = entries[index]
        status, path = entry[:2], entry[3:]
        if status[0] in "RC":
            index += 1  # skip the original path of a rename/copy
        paths.append(path)
        index += 1
    return sorted(set(paths))


def require_clean_worktree(worktree: Path) -> None:
    """Writable work starts from a clean worktree (AD-SW7-R2).

    Pre-existing uncommitted changes refuse the start; the user commits,
    stashes, or provides another worktree. Ambiguity is refused up front.
    """
    changed = changed_worktree_paths(worktree)
    if changed:
        raise WorkdirError("ATTRIBUTION_AMBIGUOUS",
                           "worktree has pre-existing changes: " + ", ".join(changed))


def check_record_changes(worktree: Path, scope: Sequence[str],
                         project_root: Path | None = None,
                         excluded_paths: Sequence[str] = ()) -> dict[str, Any]:
    """Check changed paths against declared worktree or Project scope."""
    claims = tuple(_normalize_claim(item) for item in scope)
    _deny(not claims, "SCOPE_DENIED", "completion requires at least one --scope claim")
    tree = Path(worktree).expanduser().resolve()
    root = Path(project_root).expanduser().resolve() if project_root else None
    same_root = root is not None and root == tree
    project_prefix = ""
    if root is not None and not same_root:
        try:
            project_prefix = root.relative_to(tree).as_posix() + "/"
        except ValueError:
            pass
    excluded = tuple(path.rstrip("/") for path in excluded_paths)
    changed = [path for path in changed_worktree_paths(tree)
               if not any(path == item or path.startswith(item + "/") for item in excluded)]
    outside = []
    for path in changed:
        if same_root:
            relative = path
            permitted = any(relative == declared or
                            relative.startswith(declared.rstrip("/") + "/")
                            for _kind, declared in claims)
        else:
            claim_root = "project" if project_prefix and path.startswith(project_prefix) else "worktree"
            relative = path[len(project_prefix):] if claim_root == "project" else path
            permitted = any(kind == claim_root and
                            (relative == declared or relative.startswith(declared.rstrip("/") + "/"))
                            for kind, declared in claims)
        if not permitted:
            outside.append(path)
    _deny(bool(outside), "SCOPE_DENIED",
          "changes outside the declared scope: " + ", ".join(outside))
    return {"changed": changed, "scope": list(scope)}


def record_run_provenance(project_root: Path, reference: str, worktree: Path) -> dict[str, Any]:
    """Declared provenance for a managed run triggered by a work record.

    Resolves the governing record live and returns the declared identity
    payload for ``kosmic_runs.begin_run``. Never carries handles or tokens.
    """
    root, project_id = _project_identity(project_root)
    record = resolve_work_record(root, reference)
    return {
        "project_id": project_id,
        "governing_record": record.qualified_id,
        "record_path": record.path.relative_to(root).as_posix(),
        "subproject": record.subproject_id,
        "directory_id": directory_id(worktree),
    }


def authorize_run_record(project_root: Path, worktree: Path,
                         provenance: Mapping[str, Any]) -> SpecRef:
    """``kosmic_runs.begin_run`` authorization boundary (AD-SW5-R2).

    The declared ``governing_record`` must resolve to a live authorized
    record of this Project. A declared project that is not the record's own
    fails with RUN_IDENTITY_MISMATCH, so one record's evidence can never be
    minted under another record of the same Project.
    """
    _deny(not isinstance(provenance, Mapping), "CONTEXT_INVALID", "provenance payload required")
    root, _ = _project_identity(project_root)
    declared_record = provenance.get("governing_record")
    _deny(not isinstance(declared_record, str) or not declared_record, "CONTEXT_INVALID",
          "governing_record required")
    record = resolve_work_record(root, declared_record)
    declared_project = provenance.get("project_id")
    _deny(declared_project is not None and declared_project != record.project_id,
          "RUN_IDENTITY_MISMATCH",
          f"declared project {declared_project!r} is not the project "
          f"{record.project_id!r} of record {record.qualified_id!r}")
    return record

def check_work_start(project_root: Path, worktree: Path, reference: str) -> SpecRef:
    """Stateless start check: validate record, binding, and clean worktree."""
    record = resolve_work_record(project_root, reference)
    registry = load_registry(project_root)
    if registry["directories"]:
        resolve_directory(project_root, worktree)
    require_clean_worktree(worktree)
    return record
