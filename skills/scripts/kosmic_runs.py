"""Managed-run foundation: migration inventory and descriptor-anchored run root.

Story 043 delivers the two public seams later stories build on:

- a versioned migration inventory (``kosmic_runs_inventory.json``) plus a
  source-policy auditor that explains every production temporary-path caller
  and every scratch-policy document with zero unexplained entries; and
- ``resolve_run_root``, the sole resolver for the canonical worktree-local
  scratch root ``<git-worktree-root>/.tmp/kosmic/{runs,quarantine,operations,handles}``.

The resolver never reads ``TMPDIR``, ``TEMP``, or platform temporary defaults.
Every path component below the Git top-level is opened descriptor-relatively
with ``O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC`` and validated for directory type,
current UID, required mode, and device; symlinked or malformed ancestors fail
closed with a stable ``RunRootError`` code. Stored absolute paths in later run
records are diagnostic only; mutations derive paths from the retained
directory descriptors exposed by ``RunRoot``.
"""

from __future__ import annotations

import errno
import json
import os
import re
import stat
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

INVENTORY_SCHEMA = "kosmic.runs-inventory/v1"
INVENTORY_FILENAME = "kosmic_runs_inventory.json"
INVENTORY_DEFAULT_PATH = Path(__file__).with_name(INVENTORY_FILENAME)

CLASSIFICATIONS = ("managed-run", "atomic-single-file", "atomic-publication", "durable", "defect")
MANAGED_DIRECTORIES = ("runs", "quarantine", "operations", "handles")
PRIVATE_MODE = 0o700
SHARED_FORBIDDEN_MODE = 0o022

TEMPFILE_CALL_PATTERN = re.compile(
    r"tempfile\.(?:TemporaryDirectory|mkdtemp|mkstemp|mktemp|NamedTemporaryFile"
    r"|TemporaryFile|SpooledTemporaryFile|gettempdir\w*|tempdir)\b"
)
TEMPFILE_IMPORT_PATTERN = re.compile(r"from\s+tempfile\s+import\s+([^#\n]+)")
FORBIDDEN_TEMP_LITERAL_PATTERN = re.compile(
    r"(?:['\"]/tmp(?:/[^'\"]*)?['\"]|['\"]/dev/shm(?:/[^'\"]*)?['\"]"
    r"|gettempdir|['\"]TMPDIR?['\"]|['\"]TEMP['\"])"
)
ROOT_SCRATCH_PATTERN = re.compile(
    r"(?:Path\([^)]*\)\s*/\s*['\"](?:scratch|\.tmp|tmp)['\"]|"
    r"['\"](?:scratch|\.tmp|tmp)/[^'\"]*['\"])",
    re.IGNORECASE,
)
POLICY_MARKER_PATTERN = re.compile(r"File Hygiene|\.tmp/|\.scratch[/}]")
POLICY_DOCUMENT_ROOTS = ("skills", "docs")


class RunRootError(RuntimeError):
    """Fail-closed root resolution error with a stable machine-readable code."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


class InventoryError(RuntimeError):
    """The checked-in migration inventory is malformed or schema-unknown."""


@dataclass
class RunRoot:
    """A resolved run root holding retained, verified directory descriptors."""

    worktree: Path
    path: Path
    device: int
    kosmic_fd: int
    runs_fd: int
    quarantine_fd: int
    operations_fd: int
    handles_fd: int
    closed: bool = field(default=False, repr=False)

    def close(self) -> None:
        if self.closed:
            return
        for attribute in ("kosmic_fd", "runs_fd", "quarantine_fd", "operations_fd", "handles_fd"):
            descriptor = getattr(self, attribute)
            if descriptor >= 0:
                try:
                    os.close(descriptor)
                except OSError:
                    pass
                setattr(self, attribute, -1)
        self.closed = True

    def __enter__(self) -> "RunRoot":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()


@dataclass(frozen=True)
class AuditReport:
    ok: bool
    findings: tuple[str, ...]
    counts: dict[str, int]


def _run_git(repository: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", str(repository), *arguments], capture_output=True, text=True, check=False)


def _worktree_toplevel(worktree: Path) -> Path:
    try:
        completed = _run_git(worktree, "rev-parse", "--show-toplevel")
    except OSError as error:
        raise RunRootError("GIT_FAILURE", f"git is unavailable: {error}") from error
    if completed.returncode != 0:
        raise RunRootError("NO_GIT_WORKTREE", str(worktree))
    return Path(completed.stdout.strip())


def _root_ignored(toplevel: Path, *, create_if_missing: bool) -> bool:
    """Report whether Git ignore rules exclude ``.tmp``.

    Resolver mode may create the empty anchor before checking directory-only
    patterns. Auditor mode is read-only and therefore fails closed if the
    anchor is absent; callers that audit a fixture should materialize it.
    """
    scratch = toplevel / ".tmp"
    if not scratch.exists():
        if not create_if_missing:
            return False
        try:
            os.mkdir(scratch, PRIVATE_MODE)
        except FileExistsError:
            pass
    completed = _run_git(toplevel, "check-ignore", "--verbose", "--", ".tmp")
    if completed.returncode not in (0, 1):
        raise RunRootError("GIT_FAILURE", completed.stderr.strip())
    for line in completed.stdout.splitlines():
        columns = line.rsplit("\t", 1)
        if len(columns) == 2 and not columns[0].rsplit(":", 2)[-1].startswith("!"):
            return True
    return False


def _validate_component_stat(name: str, component_stat: Any, *, expected_device: int | None, private: bool) -> None:
    if not stat.S_ISDIR(component_stat.st_mode):
        raise RunRootError("COMPONENT_NOT_DIRECTORY", name)
    if component_stat.st_uid != os.geteuid():
        raise RunRootError("COMPONENT_OWNER_MISMATCH", name)
    if expected_device is not None and component_stat.st_dev != expected_device:
        raise RunRootError("DEVICE_MISMATCH", name)
    mode = stat.S_IMODE(component_stat.st_mode)
    if private and mode != PRIVATE_MODE:
        raise RunRootError("COMPONENT_MODE_MISMATCH", f"{name}: {mode:o} is not {PRIVATE_MODE:o}")
    if not private and mode & SHARED_FORBIDDEN_MODE:
        raise RunRootError("COMPONENT_MODE_MISMATCH", f"{name}: group/world-writable")


def _classify_open_failure(parent_fd: int, name: str) -> RunRootError:
    try:
        component_stat = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError:
        component_stat = None
    if component_stat is not None and stat.S_ISLNK(component_stat.st_mode):
        return RunRootError("COMPONENT_SYMLINK", name)
    return RunRootError("COMPONENT_NOT_DIRECTORY", name)


def _component_open_error(parent_fd: int, name: str, error: OSError) -> RunRootError:
    if error.errno in (errno.ELOOP, errno.ENOTDIR):
        return _classify_open_failure(parent_fd, name)
    return RunRootError("COMPONENT_OPEN_FAILED", f"{name}: {error}")


def _open_component(parent_fd: int, name: str, *, expected_device: int | None, private: bool) -> int:
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    try:
        descriptor = os.open(name, flags, dir_fd=parent_fd)
    except FileNotFoundError:
        try:
            os.mkdir(name, PRIVATE_MODE, dir_fd=parent_fd)
        except FileExistsError:
            pass
        except OSError as error:
            raise RunRootError("COMPONENT_CREATE_FAILED", f"{name}: {error}") from error
        try:
            descriptor = os.open(name, flags, dir_fd=parent_fd)
        except OSError as error:
            raise _component_open_error(parent_fd, name, error) from error
    except OSError as error:
        raise _component_open_error(parent_fd, name, error) from error
    try:
        _validate_component_stat(name, os.fstat(descriptor), expected_device=expected_device, private=private)
    except BaseException:
        os.close(descriptor)
        raise
    return descriptor


def resolve_run_root(worktree: Path) -> RunRoot:
    """Resolve the sole managed-run root for a Git worktree."""
    toplevel = _worktree_toplevel(Path(worktree).expanduser())
    scratch = toplevel / ".tmp"
    if scratch.exists():
        scratch_stat = scratch.lstat()
        if stat.S_ISLNK(scratch_stat.st_mode):
            raise RunRootError("COMPONENT_SYMLINK", ".tmp")
        if not stat.S_ISDIR(scratch_stat.st_mode):
            raise RunRootError("COMPONENT_NOT_DIRECTORY", ".tmp")
    if not _root_ignored(toplevel, create_if_missing=True):
        raise RunRootError("ROOT_IGNORE_MISSING", str(toplevel))

    retained: list[int] = []
    transient: list[int] = []
    try:
        toplevel_fd = os.open(toplevel, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        transient.append(toplevel_fd)
        toplevel_stat = os.fstat(toplevel_fd)
        _validate_component_stat("worktree root", toplevel_stat, expected_device=None, private=False)
        device = toplevel_stat.st_dev
        scratch_fd = _open_component(toplevel_fd, ".tmp", expected_device=device, private=False)
        transient.append(scratch_fd)
        kosmic_fd = _open_component(scratch_fd, "kosmic", expected_device=device, private=True)
        retained.append(kosmic_fd)
        managed: dict[str, int] = {}
        for name in MANAGED_DIRECTORIES:
            managed[name] = _open_component(kosmic_fd, name, expected_device=device, private=True)
            retained.append(managed[name])
    except BaseException:
        for descriptor in (*retained, *transient):
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise
    finally:
        for descriptor in transient:
            try:
                os.close(descriptor)
            except OSError:
                pass
    return RunRoot(toplevel, toplevel / ".tmp" / "kosmic", device, kosmic_fd, managed["runs"], managed["quarantine"], managed["operations"], managed["handles"])


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise InventoryError(message)


def _validated_anchor(row: dict[str, Any], row_id: str) -> str:
    anchor = row.get("anchor")
    _require(isinstance(anchor, str) and bool(anchor), f"{row_id}: anchor must be a non-empty string")
    try:
        re.compile(anchor)
    except re.error as error:
        raise InventoryError(f"{row_id}: anchor is not a valid pattern: {error}") from error
    return anchor


def load_migration_inventory(path: Path | None = None) -> dict[str, Any]:
    """Load and validate the checked-in versioned migration inventory."""
    inventory_path = Path(path) if path is not None else INVENTORY_DEFAULT_PATH
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise InventoryError(f"migration inventory is missing: {inventory_path}") from error
    except (OSError, json.JSONDecodeError) as error:
        raise InventoryError(f"migration inventory is unreadable: {error}") from error
    _require(isinstance(inventory, dict), "migration inventory must be a JSON object")
    _require(inventory.get("schema") == INVENTORY_SCHEMA, f"unsupported inventory schema: {inventory.get('schema')!r}")
    for key in ("created", "story", "callers", "policy_consumers", "root_ignore", "managed_callers"):
        _require(key in inventory, f"migration inventory missing required key: {key}")
    _require(isinstance(inventory["managed_callers"], list) and inventory["managed_callers"], "managed_callers must be a non-empty list")
    seen_ids: set[str] = set()

    def validate_rows(rows: Any, *, kind: str) -> None:
        _require(isinstance(rows, list) and rows, f"{kind} must be a non-empty list")
        for row in rows:
            _require(isinstance(row, dict), f"{kind} rows must be objects")
            row_id = row.get("id")
            _require(isinstance(row_id, str) and bool(row_id), f"{kind} row needs an id")
            _require(row_id not in seen_ids, f"duplicate inventory id: {row_id}")
            seen_ids.add(row_id)
            _require(row.get("classification") in CLASSIFICATIONS, f"{row_id}: invalid classification")
            _require(isinstance(row.get("rationale"), str) and bool(row["rationale"].strip()), f"{row_id}: rationale is required")
            _validated_anchor(row, row_id)

    validate_rows(inventory["callers"], kind="callers")
    for row in inventory["callers"]:
        _require(isinstance(row.get("module"), str) and re.fullmatch(r"skills/scripts/[A-Za-z0-9_./-]+\.py", row["module"]), f"{row['id']}: invalid caller module")
        _require(isinstance(row.get("function"), str) and bool(row["function"]), f"{row['id']}: function is required")
    for row in inventory["managed_callers"]:
        _require(isinstance(row, dict), "managed_callers rows must be objects")
        row_id = row.get("id")
        _require(isinstance(row_id, str) and bool(row_id), "managed_callers row needs an id")
        _require(row_id not in seen_ids, f"duplicate inventory id: {row_id}")
        seen_ids.add(row_id)
        _require(isinstance(row.get("module"), str) and re.fullmatch(r"skills/scripts/[A-Za-z0-9_./-]+\.py", row["module"]), f"{row_id}: invalid managed caller module")
        for field in ("function", "migrated_from", "mechanism"):
            _require(isinstance(row.get(field), str) and bool(row[field]), f"{row_id}: {field} is required")
        _require(isinstance(row.get("rationale"), str) and bool(row["rationale"].strip()), f"{row_id}: rationale is required")
    validate_rows(inventory["policy_consumers"], kind="policy_consumers")
    for row in inventory["policy_consumers"]:
        consumer_path = row.get("path")
        _require(isinstance(consumer_path, str) and consumer_path.endswith(".md") and any(consumer_path.startswith(f"{root}/") for root in POLICY_DOCUMENT_ROOTS), f"{row['id']}: invalid policy consumer path")
    root_ignore = inventory["root_ignore"]
    _require(isinstance(root_ignore, dict) and root_ignore.get("id") not in seen_ids, "root_ignore must be a unique row")
    _require(root_ignore.get("classification") in CLASSIFICATIONS, "root_ignore classification is invalid")
    _require(isinstance(root_ignore.get("rationale"), str) and bool(root_ignore["rationale"].strip()), "root_ignore rationale is required")
    return inventory


def _temporary_sites(text: str) -> dict[int, str]:
    imported: set[str] = set()
    for match in TEMPFILE_IMPORT_PATTERN.finditer(text):
        for name in match.group(1).split(","):
            symbol = name.strip().split(" as ", 1)[0].strip()
            if re.fullmatch(r"(?:TemporaryDirectory|mkdtemp|mkstemp|mktemp|NamedTemporaryFile|TemporaryFile|SpooledTemporaryFile|gettempdir\w*|tempdir)", symbol):
                imported.add(symbol)
    sites: dict[int, str] = {}
    for line_number, line in enumerate(text.splitlines(), 1):
        if TEMPFILE_CALL_PATTERN.search(line) or any(re.search(rf"\b{re.escape(symbol)}\s*\(", line) for symbol in imported):
            if not TEMPFILE_IMPORT_PATTERN.search(line):
                sites[line_number] = line
    return sites


def audit_temporary_policy(repo: Path, *, inventory_path: Path | None = None) -> AuditReport:
    """Read-only audit explaining every production temporary path and policy document."""
    repository = Path(repo).resolve()
    inventory = load_migration_inventory(inventory_path if inventory_path is not None else repository / "skills" / "scripts" / INVENTORY_FILENAME)
    findings: list[str] = []
    modules = sorted((repository / "skills" / "scripts").glob("*.py"))
    sites: dict[tuple[str, int], str] = {}
    module_text = {module.relative_to(repository).as_posix(): module.read_text(encoding="utf-8") for module in modules}
    for module_relative, text in module_text.items():
        for line_number, line in _temporary_sites(text).items():
            sites[(module_relative, line_number)] = line
    matched: set[tuple[str, int]] = set()
    for row in inventory["callers"]:
        pattern = re.compile(row["anchor"])
        hits = [key for key, line in sites.items() if key[0] == row["module"] and pattern.search(line)]
        if not hits:
            findings.append(f"STALE_INVENTORY_CALLER {row['id']}: anchor no longer matches {row['module']}")
        for key in hits:
            if key in matched:
                findings.append(f"AMBIGUOUS_INVENTORY_CALLER {row['id']}: duplicate anchor at {key[0]}:{key[1]}")
            matched.add(key)
    for key in sorted(sites):
        if key not in matched:
            findings.append(f"UNEXPLAINED_TEMPFILE_CALL {key[0]}:{key[1]}: {sites[key].strip()}")
    for module_relative, text in module_text.items():
        if Path(module_relative).name == Path(__file__).name:
            continue
        for line_number, line in enumerate(text.splitlines(), 1):
            forbidden = FORBIDDEN_TEMP_LITERAL_PATTERN.search(line)
            if forbidden:
                findings.append(f"FORBIDDEN_TEMP_PATH {module_relative}:{line_number}: {forbidden.group(0)}")
            root_scratch = ROOT_SCRATCH_PATTERN.search(line)
            if root_scratch:
                findings.append(f"ROOT_SCRATCH_PATH {module_relative}:{line_number}: {root_scratch.group(0)}")
    consumer_paths = {row["path"] for row in inventory["policy_consumers"]}
    documents = [path for root in POLICY_DOCUMENT_ROOTS for path in (repository / root).rglob("*.md")]
    for document in sorted(documents):
        relative = document.relative_to(repository).as_posix()
        if POLICY_MARKER_PATTERN.search(document.read_text(encoding="utf-8")) and relative not in consumer_paths:
            findings.append(f"UNEXPLAINED_POLICY_CONSUMER {relative}: scratch-policy prose is not inventoried")
    for row in inventory["policy_consumers"]:
        document = repository / row["path"]
        if not document.is_file() or not re.search(row["anchor"], document.read_text(encoding="utf-8")):
            findings.append(f"STALE_INVENTORY_CONSUMER {row['id']}: anchor/document missing")
    try:
        root_ignored = _root_ignored(repository, create_if_missing=False)
    except RunRootError as error:
        root_ignored = False
        findings.append(f"ROOT_IGNORE_CHECK_FAILED {error.code}")
    if not root_ignored:
        findings.append("ROOT_IGNORE_MISSING .tmp/ is not ignored at the worktree root")
    counts: dict[str, int] = {classification: 0 for classification in CLASSIFICATIONS}
    for row in (*inventory["callers"], *inventory["policy_consumers"]):
        counts[row["classification"]] += 1
    counts.update({"callers": len(inventory["callers"]), "policy-consumers": len(inventory["policy_consumers"]), "root-ignore": 1})
    return AuditReport(ok=not findings, findings=tuple(findings), counts=counts)

# ---------------------------------------------------------------------------
# Managed-run lifecycle (Stories 044-047 and 052)
# ---------------------------------------------------------------------------
#
# Story 044 adds the private GitSnapshot seam (strict porcelain-v2 -z capture,
# hashing, and before/after path classification) and the RunStore seam
# (versioned manifest, handle, receipt, operation, and history schemas written
# through descriptor-relative atomic replacement with required file and
# directory synchronization). Stories 045-047 and 052 build the lease, owner
# cleanup, promotion, and reporting operations on top of these seams.

import base64
import ctypes
import fcntl
import hashlib
import hmac
import secrets
import shutil
import socket as _socket
import struct
import time as _time
from datetime import datetime, timedelta, timezone
from pathlib import PurePath
from types import MappingProxyType
from typing import Mapping, Sequence

_RENAME_EXCHANGE = 2
_LIBC = ctypes.CDLL(None, use_errno=True)
_RENAMEAT2 = getattr(_LIBC, "renameat2", None)
if _RENAMEAT2 is not None:
    _RENAMEAT2.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    _RENAMEAT2.restype = ctypes.c_int

class RunError(RuntimeError):
    """Lifecycle error with a stable machine-readable code."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


class _FaultInjected(RuntimeError):
    """Test-injected fault at a named lifecycle checkpoint."""


def _fault(stage: str) -> None:
    if os.environ.get("KOSMIC_RUNS_FAULT") == stage:
        raise _FaultInjected(stage)


_clock: "any" = None


def _now() -> datetime:
    if _clock is not None:
        return _clock()
    return datetime.now(timezone.utc)


def _format_utc(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_utc(text: object, context: str) -> datetime:
    if not isinstance(text, str):
        raise RunError("MANIFEST_INVALID", f"{context}: timestamp must be a string")
    try:
        parsed = datetime.strptime(text, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise RunError("MANIFEST_INVALID", f"{context}: invalid UTC timestamp {text!r}") from error
    return parsed


RUN_ID_RE = re.compile(r"[0-9]{8}T[0-9]{6}Z-[a-z0-9](?:[a-z0-9-]{0,22}[a-z0-9])?-[0-9a-f]{32}\Z")
HEX64_RE = re.compile(r"[0-9a-f]{64}\Z")
HANDLE_NAME_RE = re.compile(r"[0-9a-f]{32}\Z")

RUN_STATES = ("creating", "active", "finalizing", "succeeded", "failed", "abandoned")
TERMINAL_STATES = ("succeeded", "failed", "abandoned")
RETENTIONS = ("diagnostic", "disposable", "extended-diagnostic")
CREATION_RETENTIONS = ("diagnostic", "disposable")
OUTCOMES = ("succeeded", "failed")

ACTIVE_DEFAULT = timedelta(hours=24)
ACTIVE_MAX = timedelta(days=7)
FAILURE_RETENTION = timedelta(hours=72)
EXTENSION_CAP = timedelta(days=7)
UNLOCK_GRACE = timedelta(hours=24)
RECEIPT_TTL = timedelta(days=30)
HISTORY_MAX_BYTES = 10 * 1024 * 1024
HISTORY_READ_LIMIT = 256 * 1024 * 1024
HISTORY_MAX_AGE = timedelta(days=30)
HISTORY_FILENAME = "history.jsonl"
PER_RUN_WARN_BYTES = 1 << 30
AGGREGATE_WARN_BYTES = 4 << 30
REPORT_ENTRY_LIMIT = 10000

# AD-MRW10 staged destructive capability: explicit ``gc --apply`` and bounded
# startup collection are active; the migration-inventory auditor below remains
# as the permanent scratch-policy regression guard.
GC_APPLY_ENABLED = True
STARTUP_GC_ENABLED = True
STARTUP_GC_MAX_ENTRIES = 4
STARTUP_GC_MAX_BYTES = 256 << 20

STATE_TRANSITIONS = frozenset({
    ("creating", "active"),
    ("active", "finalizing"),
    ("finalizing", "succeeded"),
    ("finalizing", "failed"),
    ("active", "abandoned"),
})


CREDENTIAL_DETAIL_PATTERNS = (
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"gho_[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"(?i)(password|passwd|secret|token|api[_-]?key|private[_-]?key|credential)(\s*[=:]\s*)(\S+)"),
)


def _redact_detail(detail: str) -> str:
    """Redact credential-shaped values from caller-supplied diagnostic detail."""
    redacted = str(detail or "")[:512]
    for pattern in CREDENTIAL_DETAIL_PATTERNS:
        redacted = pattern.sub("[redacted]", redacted)
    return redacted


def _sanitize_purpose_slug(purpose: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", str(purpose).strip().lower()).strip("-")[:24]
    return slug or "run"


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _fsync_fd(descriptor: int, *, context: str) -> None:
    try:
        os.fsync(descriptor)
    except OSError as error:
        raise RunError("SYNC_FAILED", f"{context}: {error}") from error


def _atomic_replace_bytes(dir_fd: int, name: str, data: bytes, *, mode: int = 0o600, context: str | None = None) -> None:
    """Write ``data`` to ``name`` through same-directory staging and fsync."""
    context = context or name
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,96}", name):
        raise RunError("NAME_INVALID", context)
    temporary = f".{name}.new-{os.getpid()}-{secrets.token_hex(4)}"
    descriptor = -1
    try:
        descriptor = os.open(
            temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, mode, dir_fd=dir_fd
        )
        view = memoryview(data)
        offset = 0
        while offset < len(data):
            offset += os.write(descriptor, view[offset:])
        _fsync_fd(descriptor, context=context)
        os.close(descriptor)
        descriptor = -1
        os.replace(temporary, name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)
    except OSError as error:
        raise RunError("ATOMIC_WRITE_FAILED", f"{context}: {error}") from error
    finally:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                pass
            descriptor = -1
        if _exists_fd(dir_fd, temporary):
            try:
                os.unlink(temporary, dir_fd=dir_fd)
            except OSError:
                pass
    _fsync_fd(dir_fd, context=context)


def _read_bounded(dir_fd: int, name: str, *, limit: int, context: str) -> bytes:
    try:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=dir_fd)
    except OSError as error:
        raise RunError("READ_FAILED", f"{context}: {error}") from error
    try:
        status = os.fstat(descriptor)
        if not stat.S_ISREG(status.st_mode):
            raise RunError("NOT_A_FILE", context)
        if status.st_size > limit:
            raise RunError("PAYLOAD_TOO_LARGE", f"{context}: {status.st_size} bytes exceeds {limit}")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, min(65536, limit))
            if not chunk:
                break
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        os.close(descriptor)


def _read_json_bounded(dir_fd: int, name: str, *, limit: int, context: str) -> Any:
    try:
        return json.loads(_read_bounded(dir_fd, name, limit=limit, context=context).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise RunError("RECORD_MALFORMED", f"{context}: {error}") from error


# --- Git evidence (AD-MRW5) -------------------------------------------------


@dataclass(frozen=True)
class GitSnapshot:
    """A strict porcelain-v2 capture with hash and path classification."""

    head: str | None
    branch: str | None
    branch_oid: str | None
    toplevel: str
    common_dir: str
    raw: bytes
    sha256: str
    paths: tuple[str, ...]
    renames: tuple[tuple[str, str], ...]

    def summary(self) -> dict[str, Any]:
        return {
            "head": self.head,
            "branch": self.branch,
            "branch_oid": self.branch_oid,
            "toplevel": self.toplevel,
            "git_common_dir": self.common_dir,
            "porcelain_sha256": self.sha256,
            "path_count": len(self.paths),
        }


def _parse_porcelain_v2(raw: bytes, *, source: str) -> dict[str, Any]:
    """Parse ``git status --porcelain=v2 -z`` output strictly."""
    if not raw:
        return {"branch": {}, "entries": ()}
    parts = raw.split(b"\0")
    if parts[-1] != b"":
        raise RunError("GIT_SNAPSHOT_UNKNOWN_RECORD", f"{source}: missing final NUL terminator")
    records = parts[:-1]
    branch: dict[str, str] = {}
    entries: list[dict[str, Any]] = []
    index = 0
    while index < len(records):
        record = records[index]
        index += 1
        if record.startswith(b"# "):
            header = record[2:].split(b" ", 1)
            key = header[0].decode("ascii", "replace")
            if key not in {"branch.oid", "branch.head", "branch.upstream", "branch.ab"}:
                raise RunError("GIT_SNAPSHOT_UNKNOWN_RECORD", f"{source}: # {key}")
            branch[key] = os.fsdecode(header[1]) if len(header) > 1 else ""
            continue
        kind = record[:1]
        if kind == b"1":
            fields = record.split(b" ", 8)
            if len(fields) != 9:
                raise RunError("GIT_SNAPSHOT_UNKNOWN_RECORD", f"{source}: short ordinary record")
            entries.append({"kind": "ordinary", "xy": fields[1].decode("ascii", "replace"), "path": os.fsdecode(fields[8])})
        elif kind == b"2":
            fields = record.split(b" ", 9)
            if len(fields) != 10:
                raise RunError("GIT_SNAPSHOT_UNKNOWN_RECORD", f"{source}: short rename record")
            if index >= len(records):
                raise RunError("GIT_SNAPSHOT_UNKNOWN_RECORD", f"{source}: rename record missing origPath")
            entries.append({
                "kind": "renamed",
                "xy": fields[1].decode("ascii", "replace"),
                "path": os.fsdecode(fields[9]),
                "orig_path": os.fsdecode(records[index]),
            })
            index += 1
        elif kind == b"u":
            fields = record.split(b" ", 10)
            if len(fields) != 11:
                raise RunError("GIT_SNAPSHOT_UNKNOWN_RECORD", f"{source}: short unmerged record")
            entries.append({"kind": "unmerged", "xy": fields[1].decode("ascii", "replace"), "path": os.fsdecode(fields[10])})
        elif kind in (b"?", b"!"):
            fields = record.split(b" ", 1)
            if len(fields) != 2:
                raise RunError("GIT_SNAPSHOT_UNKNOWN_RECORD", f"{source}: short path record")
            entries.append({"kind": "untracked" if kind == b"?" else "ignored", "path": os.fsdecode(fields[1])})
        else:
            raise RunError("GIT_SNAPSHOT_UNKNOWN_RECORD", f"{source}: {os.fsdecode(record[:24])!r}")
    return {"branch": branch, "entries": tuple(entries)}


def capture_git_snapshot(worktree: Path, *, name: str = "snapshot") -> GitSnapshot:
    """Capture HEAD, branch, top-level, common dir, and strict porcelain-v2 status."""
    worktree = Path(worktree)

    def git(*arguments: str, allow_failure: bool = False) -> bytes:
        completed = subprocess.run(
            ["git", "-C", str(worktree), *arguments], capture_output=True, check=False
        )
        if completed.returncode != 0:
            if allow_failure:
                return b""
            detail = completed.stderr.decode("utf-8", "replace").strip()[:300]
            raise RunError("GIT_CAPTURE_FAILED", f"{name}: git {' '.join(arguments)}: {detail}")
        return completed.stdout

    head_output = git("rev-parse", "HEAD", allow_failure=True)
    head = head_output.decode("utf-8", "replace").strip() or None
    if head == "HEAD":
        head = None  # unborn branch: rev-parse echoes the unresolved name
    toplevel = git("rev-parse", "--show-toplevel").decode("utf-8", "replace").strip()
    common_dir = git("rev-parse", "--git-common-dir").decode("utf-8", "replace").strip()
    raw = git("status", "--porcelain=v2", "--branch", "--untracked-files=all", "-z")
    parsed = _parse_porcelain_v2(raw, source=name)
    branch_head = parsed["branch"].get("branch.head")
    if branch_head in ("(detached)", ""):
        branch_head = None
    branch_oid = parsed["branch"].get("branch.oid")
    if branch_oid == "(initial)":
        branch_oid = None
    if head is None and branch_oid is not None:
        head = branch_oid
    paths = tuple(sorted({entry["path"] for entry in parsed["entries"]}))
    renames = tuple(
        (entry["orig_path"], entry["path"]) for entry in parsed["entries"] if entry["kind"] == "renamed"
    )
    return GitSnapshot(
        head=head,
        branch=branch_head,
        branch_oid=branch_oid,
        toplevel=toplevel,
        common_dir=common_dir,
        raw=raw,
        sha256=hashlib.sha256(raw).hexdigest(),
        paths=paths,
        renames=renames,
    )


def git_delta(start: GitSnapshot, finish: GitSnapshot) -> dict[str, Any]:
    """Classify paths between two snapshots; classifications are never ownership."""
    start_paths = set(start.paths)
    finish_paths = set(finish.paths)
    renamed = [{"from": origin, "to": target} for origin, target in finish.renames if origin in start_paths]
    renamed_origins = {item["from"] for item in renamed}
    pre_existing = sorted(start_paths - finish_paths)
    return {
        "schema": 1,
        "head_changed": start.head != finish.head,
        "pre_existing": pre_existing,
        "introduced": sorted(finish_paths - start_paths),
        "modified": sorted(start_paths & finish_paths),
        "removed": sorted(set(pre_existing) - renamed_origins),
        "renamed": renamed,
        "unattributed": [],
    }

def _git_delta_from_basis(basis: dict[str, Any], finish: GitSnapshot) -> dict[str, Any]:
    start_paths = set(str(path) for path in basis.get("paths", ()))
    finish_paths = set(finish.paths)
    renamed = [{"from": origin, "to": target} for origin, target in finish.renames if origin in start_paths]
    renamed_origins = {item["from"] for item in renamed}
    pre_existing = sorted(start_paths - finish_paths)
    return {
        "schema": 1,
        "head_changed": basis.get("head") != finish.head,
        "pre_existing": pre_existing,
        "introduced": sorted(finish_paths - start_paths),
        "modified": sorted(start_paths & finish_paths),
        "removed": sorted(set(pre_existing) - renamed_origins),
        "renamed": renamed,
        "unattributed": [],
    }


# --- Run store (AD-MRW4) ----------------------------------------------------


MANIFEST_REQUIRED = (
    "schema", "sequence", "run_id", "project_id", "purpose", "state", "retention",
    "created_at", "finished_at", "expires_at", "lease_expires_at", "holder_pid",
    "token_sha256", "worktree_root", "git_common_dir", "git_start_sha256",
    "git_finish_sha256", "snapshot_complete",
)


def validate_run_manifest(manifest: Any, *, context: str = "manifest") -> dict[str, Any]:
    """Validate the canonical ``RUN.json`` schema v1."""
    if not isinstance(manifest, dict):
        raise RunError("MANIFEST_INVALID", f"{context}: not an object")
    missing = [field for field in MANIFEST_REQUIRED if field not in manifest]
    if missing:
        raise RunError("MANIFEST_INVALID", f"{context}: missing {', '.join(missing)}")
    if manifest["schema"] != 1:
        raise RunError("MANIFEST_SCHEMA_UNKNOWN", f"{context}: schema {manifest['schema']!r}")
    if not isinstance(manifest["sequence"], int) or manifest["sequence"] < 1:
        raise RunError("MANIFEST_INVALID", f"{context}: sequence must be a positive integer")
    if not isinstance(manifest["run_id"], str) or not RUN_ID_RE.fullmatch(manifest["run_id"]):
        raise RunError("MANIFEST_INVALID", f"{context}: run_id {manifest['run_id']!r}")
    if not isinstance(manifest["purpose"], str) or not manifest["purpose"].strip():
        raise RunError("MANIFEST_INVALID", f"{context}: purpose is required")
    if manifest["state"] not in RUN_STATES:
        raise RunError("MANIFEST_INVALID", f"{context}: state {manifest['state']!r}")
    if manifest["retention"] not in RETENTIONS:
        raise RunError("MANIFEST_INVALID", f"{context}: retention {manifest['retention']!r}")
    if manifest["state"] == "active" and manifest["retention"] == "extended-diagnostic":
        raise RunError("MANIFEST_INVALID", f"{context}: extended-diagnostic is post-failure only")
    _parse_utc(manifest["created_at"], context)
    for field in ("expires_at", "lease_expires_at", "finished_at"):
        if manifest[field] is not None:
            _parse_utc(manifest[field], context)
    if not isinstance(manifest["holder_pid"], int) or manifest["holder_pid"] < 0:
        raise RunError("MANIFEST_INVALID", f"{context}: holder_pid must be a non-negative integer")
    for field in ("token_sha256", "git_start_sha256"):
        if not isinstance(manifest[field], str) or not HEX64_RE.fullmatch(manifest[field]):
            raise RunError("MANIFEST_INVALID", f"{context}: {field} must be 64 lowercase hex")
    if manifest["git_finish_sha256"] is not None and (
        not isinstance(manifest["git_finish_sha256"], str) or not HEX64_RE.fullmatch(manifest["git_finish_sha256"])
    ):
        raise RunError("MANIFEST_INVALID", f"{context}: git_finish_sha256 must be 64 lowercase hex or null")
    if not isinstance(manifest["snapshot_complete"], bool):
        raise RunError("MANIFEST_INVALID", f"{context}: snapshot_complete must be boolean")
    for field in ("project_id", "worktree_root", "git_common_dir"):
        if not isinstance(manifest[field], str):
            raise RunError("MANIFEST_INVALID", f"{context}: {field} must be a string")
    requested = manifest.get("requested_outcome")
    if requested is not None and requested not in OUTCOMES:
        raise RunError("MANIFEST_INVALID", f"{context}: requested_outcome {requested!r}")
    return manifest


def _write_manifest(run_fd: int, manifest: dict[str, Any]) -> None:
    validate_run_manifest(manifest, context=manifest.get("run_id", "manifest"))
    _atomic_replace_bytes(run_fd, "RUN.json", _json_bytes(manifest), context=f"{manifest['run_id']}/RUN.json")


def load_manifest(run_fd: int, *, run_id: str | None = None) -> dict[str, Any]:
    context = f"{run_id or 'run'}/RUN.json"
    manifest = _read_json_bounded(run_fd, "RUN.json", limit=1 << 20, context=context)
    return validate_run_manifest(manifest, context=context)


def _transition_manifest(run_fd: int, manifest: dict[str, Any], **updates: Any) -> dict[str, Any]:
    """Apply a compare-before-write state transition monotonically."""
    updated = {**manifest, **updates, "sequence": int(manifest["sequence"]) + 1}
    updated = validate_run_manifest(updated, context=manifest.get("run_id", "manifest"))
    old_state = manifest["state"]
    new_state = updated["state"]
    if old_state != new_state and (old_state, new_state) not in STATE_TRANSITIONS:
        raise RunError("TRANSITION_INVALID", f"{manifest['run_id']}: {old_state} -> {new_state}")
    _write_manifest(run_fd, updated)
    return updated


def _write_handle(handles_fd: int, name: str, handle: dict[str, Any]) -> None:
    _atomic_replace_bytes(handles_fd, name, _json_bytes(handle), context=f"handles/{name}")


def _validated_handle(handle: Any, *, name: str) -> dict[str, Any]:
    if not isinstance(handle, dict) or handle.get("schema") != 1:
        raise RunError("HANDLE_INVALID", f"handles/{name}: unknown schema")
    kind = handle.get("kind")
    if kind == "handle":
        if not isinstance(handle.get("run_id"), str) or not RUN_ID_RE.fullmatch(handle["run_id"]):
            raise RunError("HANDLE_INVALID", f"handles/{name}: run_id")
        token = handle.get("token")
        if not isinstance(token, str) or not token:
            raise RunError("HANDLE_INVALID", f"handles/{name}: token")
        try:
            base64.b64decode(token, validate=True)
        except Exception as error:
            raise RunError("HANDLE_INVALID", f"handles/{name}: token encoding") from error
        if handle.get("state") != "active":
            raise RunError("HANDLE_INVALID", f"handles/{name}: state")
    elif kind == "receipt":
        outcome = handle.get("outcome")
        if outcome not in TERMINAL_STATES:
            raise RunError("HANDLE_INVALID", f"handles/{name}: receipt outcome")
        if not isinstance(handle.get("token_sha256"), str) or not HEX64_RE.fullmatch(handle["token_sha256"]):
            raise RunError("HANDLE_INVALID", f"handles/{name}: receipt token hash")
        if not isinstance(handle.get("run_id"), str) or not RUN_ID_RE.fullmatch(handle["run_id"]):
            raise RunError("HANDLE_INVALID", f"handles/{name}: receipt run_id")
        if handle.get("retention") not in RETENTIONS:
            raise RunError("HANDLE_INVALID", f"handles/{name}: receipt retention")
        for field in ("finished_at", "receipt_expires_at"):
            if not isinstance(handle.get(field), str):
                raise RunError("HANDLE_INVALID", f"handles/{name}: receipt {field}")
            try:
                datetime.strptime(handle[field], "%Y-%m-%dT%H:%M:%SZ")
            except ValueError as error:
                raise RunError("HANDLE_INVALID", f"handles/{name}: receipt {field}") from error
        if handle.get("expires_at") is not None and not isinstance(handle["expires_at"], str):
            raise RunError("HANDLE_INVALID", f"handles/{name}: receipt expires_at")
        for field in ("git_start_sha256",):
            if not isinstance(handle.get(field), str) or not HEX64_RE.fullmatch(handle[field]):
                raise RunError("HANDLE_INVALID", f"handles/{name}: receipt {field}")
        if handle.get("git_finish_sha256") is not None and (
            not isinstance(handle["git_finish_sha256"], str) or not HEX64_RE.fullmatch(handle["git_finish_sha256"])
        ):
            raise RunError("HANDLE_INVALID", f"handles/{name}: receipt git_finish_sha256")
        if not isinstance(handle.get("cleanup"), str) or not handle["cleanup"]:
            raise RunError("HANDLE_INVALID", f"handles/{name}: receipt cleanup")
    else:
        raise RunError("HANDLE_INVALID", f"handles/{name}: kind")
    return handle


def read_handle(handles_fd: int, name: str) -> dict[str, Any]:
    if not HANDLE_NAME_RE.fullmatch(name):
        raise RunError("HANDLE_NAME_INVALID", name)
    handle = _read_json_bounded(handles_fd, name, limit=1 << 16, context=f"handles/{name}")
    return _validated_handle(handle, name=name)


def _open_run(runs_fd: int, run_id: str) -> int:
    """Open a validated immediate run child descriptor-relatively."""
    if not RUN_ID_RE.fullmatch(run_id):
        raise RunError("RUN_ID_INVALID", run_id)
    try:
        descriptor = os.open(run_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=runs_fd)
    except (OSError, ValueError) as error:
        raise RunError("RUN_OPEN_FAILED", f"{run_id}: {error}") from error
    status = os.fstat(descriptor)
    if status.st_uid != os.geteuid() or stat.S_IMODE(status.st_mode) != PRIVATE_MODE:
        os.close(descriptor)
        raise RunError("RUN_UNTRUSTED", f"{run_id}: owner/mode {oct(stat.S_IMODE(status.st_mode))}")
    return descriptor


def _open_lock_nb(run_fd: int, *, run_id: str) -> tuple[int, bool]:
    """Open RUN.lock and attempt a non-blocking exclusive flock."""
    try:
        descriptor = os.open("RUN.lock", os.O_RDWR | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=run_fd)
    except OSError as error:
        raise RunError("RUN_LOCK_MISSING", f"{run_id}: {error}") from error
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return descriptor, True
    except BlockingIOError:
        return descriptor, False
    except OSError as error:
        os.close(descriptor)
        raise RunError("RUN_LOCK_FAILED", f"{run_id}: flock: {error}") from error


def _lock_held(run_fd: int, *, run_id: str) -> bool:
    descriptor, acquired = _open_lock_nb(run_fd, run_id=run_id)
    try:
        if acquired:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        return not acquired
    finally:
        os.close(descriptor)


def _tree_bytes(descriptor: int, *, device: int) -> tuple[int, bool]:
    """No-follow descriptor traversal; never crosses devices."""
    total = 0
    complete = True
    try:
        names = os.listdir(descriptor)
    except OSError:
        return 0, False
    for name in names:
        try:
            status = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        except OSError:
            complete = False
            continue
        if stat.S_ISLNK(status.st_mode):
            continue
        if stat.S_ISREG(status.st_mode):
            total += status.st_size
        elif stat.S_ISDIR(status.st_mode) and status.st_dev == device:
            try:
                child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=descriptor)
            except OSError:
                complete = False
                continue
            try:
                subtree, subtree_complete = _tree_bytes(child, device=device)
            finally:
                os.close(child)
            total += subtree
            complete = complete and subtree_complete
    return total, complete


def _static_run_classification(runs_fd: int, name: str) -> tuple[dict[str, Any] | None, str | None]:
    """Statically classify one immediate runs/ child without lease authority."""
    try:
        status = os.stat(name, dir_fd=runs_fd, follow_symlinks=False)
    except OSError as error:
        return None, f"UNREADABLE:{error.errno}"
    if stat.S_ISLNK(status.st_mode):
        return None, "SYMLINKED_RUN_CHILD"
    if not RUN_ID_RE.fullmatch(name):
        return None, "UNATTRIBUTED_NAME"
    if not stat.S_ISDIR(status.st_mode):
        return None, "NOT_A_DIRECTORY"
    if status.st_uid != os.geteuid() or stat.S_IMODE(status.st_mode) != PRIVATE_MODE:
        return None, "UNTRUSTED_OWNER_MODE"
    try:
        descriptor = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=runs_fd)
    except OSError as error:
        return None, f"OPEN_FAILED:{error.errno}"
    try:
        return load_manifest(descriptor, run_id=name), None
    except RunError as error:
        return None, f"MALFORMED_MANIFEST:{error.code}"
    finally:
        os.close(descriptor)


def enumerate_run_store(worktree: Path) -> dict[str, Any]:
    """Statically enumerate and byte-account every managed entry (Story 044).

    Authoritative live/abandoned classification arrives with the lease in
    Story 047's ``report_runs``; this seam is its read-only substrate.
    """
    with resolve_run_root(Path(worktree)) as root:
        entries: list[dict[str, Any]] = []
        complete = True
        for name in sorted(os.listdir(root.runs_fd)):
            manifest, reason = _static_run_classification(root.runs_fd, name)
            if manifest is None:
                entries.append({"name": name, "valid": False, "reason": reason, "bytes": 0})
                continue
            descriptor = _open_run(root.runs_fd, name)
            try:
                usage, usage_complete = _tree_bytes(descriptor, device=root.device)
            finally:
                os.close(descriptor)
            complete = complete and usage_complete
            entries.append({
                "name": name,
                "valid": True,
                "state": manifest["state"],
                "retention": manifest["retention"],
                "expires_at": manifest["expires_at"],
                "bytes": usage,
                "reason": None if usage_complete else "PARTIAL_BYTES",
            })
        return {"entries": tuple(entries), "complete": complete}


# --- Detached lease holder (AD-MRW3) ----------------------------------------


MAX_REQUEST_BYTES = 4096
MAX_RESPONSE_BYTES = 8192
HOLDER_TICK = 5.0


def _control_address(run_id: str) -> str:
    """Abstract-namespace control address for one run.

    Filesystem Unix sockets fail in deep worktrees because sun_path is limited
    to 107 bytes; the abstract namespace avoids the limit and the kernel
    reclaims the name when the holder dies. Peer credentials plus the token
    remain the authentication boundary.
    """
    return f"\0kosmic-run-{run_id}"


def _holder_loop(listener: "_socket.socket", run_fd: int, token: bytes, deadline: datetime) -> None:
    while True:
        remaining = (deadline - _now()).total_seconds()
        if remaining <= 0:
            manifest = load_manifest(run_fd)
            if manifest["state"] == "active":
                _transition_manifest(run_fd, manifest, state="abandoned", finished_at=_format_utc(_now()))
            return
        listener.settimeout(min(remaining, HOLDER_TICK))
        try:
            connection, _ = listener.accept()
        except _socket.timeout:
            # Exit quietly once the run directory itself is gone.
            try:
                os.stat("RUN.lock", dir_fd=run_fd, follow_symlinks=False)
            except OSError:
                return
            continue
        except OSError:
            return
        try:
            if _serve_holder_connection(connection, run_fd, token):
                return
        finally:
            try:
                connection.close()
            except OSError:
                pass


def _serve_holder_connection(connection: "_socket.socket", run_fd: int, token: bytes) -> bool:
    """Serve one bounded authenticated request; True means the holder exits."""
    connection.settimeout(5.0)
    try:
        credentials = connection.getsockopt(_socket.SOL_SOCKET, _socket.SO_PEERCRED, 12)
        peer_uid = struct.unpack("iii", credentials)[1]
        payload = b""
        while len(payload) <= MAX_REQUEST_BYTES:
            chunk = connection.recv(MAX_REQUEST_BYTES + 1)
            if not chunk:
                break
            payload += chunk
    except OSError:
        return False
    if peer_uid != os.geteuid() or not payload or len(payload) > MAX_REQUEST_BYTES:
        _holder_ack(connection, {"ok": False, "error": "AUTH"})
        return False
    try:
        request = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        _holder_ack(connection, {"ok": False, "error": "REQUEST"})
        return False
    if not isinstance(request, dict):
        _holder_ack(connection, {"ok": False, "error": "REQUEST"})
        return False
    operation = request.get("op")
    if not isinstance(operation, str):
        _holder_ack(connection, {"ok": False, "error": "OP"})
        return False
    supplied = request.get("token")
    if not isinstance(supplied, str):
        _holder_ack(connection, {"ok": False, "error": "TOKEN"})
        return False
    try:
        supplied_bytes = base64.b64decode(supplied, validate=True)
    except Exception:
        _holder_ack(connection, {"ok": False, "error": "TOKEN"})
        return False
    if not hmac.compare_digest(supplied_bytes, token):
        _holder_ack(connection, {"ok": False, "error": "TOKEN"})
        return False
    if operation == "ping":
        manifest = load_manifest(run_fd)
        _holder_ack(connection, {"ok": True, "state": manifest["state"], "live": True})
        return False
    if operation == "finish":
        outcome = request.get("outcome")
        if outcome not in OUTCOMES:
            _holder_ack(connection, {"ok": False, "error": "OUTCOME"})
            return False
        detail = _redact_detail(request.get("detail"))
        manifest = load_manifest(run_fd)
        if manifest["state"] != "active":
            _holder_ack(connection, {"ok": False, "error": "STATE", "state": manifest["state"]})
            return False
        _transition_manifest(
            run_fd,
            manifest,
            state="finalizing",
            requested_outcome=outcome,
            requested_detail=detail,
            requested_at=_format_utc(_now()),
        )
        _holder_ack(connection, {"ok": True, "state": "finalizing"})
        return True
    _holder_ack(connection, {"ok": False, "error": "OP"})
    return False


def _holder_ack(connection: "_socket.socket", response: dict[str, Any]) -> None:
    try:
        connection.sendall(json.dumps(response).encode("utf-8"))
    except OSError:
        pass


def _holder_process(run_fd: int, control_address: str, token: bytes, deadline: datetime, ready_write: int) -> None:
    """Final detached holder: hold flock, serve authenticated control, expire."""
    exit_code = 3
    listener = None
    lock_fd = -1
    try:
        try:
            lock_fd = os.open("RUN.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=run_fd)
            os.fchmod(lock_fd, 0o600)
        except OSError:
            os.write(ready_write, b"LOCK-FAILED\n")
            return
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            os.write(ready_write, b"LOCK-FAILED\n")
            return
        listener = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
        listener.bind(control_address)
        listener.listen(4)
        os.write(ready_write, f"READY {os.getpid()}\n".encode("ascii"))
        _holder_loop(listener, run_fd, token, deadline)
        exit_code = 0
    except BaseException:
        exit_code = 4
    finally:
        if listener is not None:
            try:
                listener.close()
            except OSError:
                pass
        if lock_fd >= 0:
            try:
                fcntl.flock(lock_fd, fcntl.LOCK_UN)
            except OSError:
                pass
            os.close(lock_fd)
        try:
            os.close(ready_write)
        except OSError:
            pass
        os._exit(exit_code)


def _spawn_holder(
    run_fd: int,
    control_address: str,
    token: bytes,
    deadline: datetime,
    inherited_descriptors: Sequence[int] = (),
) -> int:
    """Double-fork a session-detached holder; return its PID after readiness."""
    ready_read, ready_write = os.pipe()
    try:
        intermediate = os.fork()
    except OSError as error:
        os.close(ready_read)
        os.close(ready_write)
        raise RunError("HOLDER_SPAWN_FAILED", f"fork: {error}") from error
    if intermediate == 0:
        os.close(ready_read)
        for descriptor in inherited_descriptors:
            try:
                os.close(descriptor)
            except OSError:
                pass
        try:
            os.setsid()
        except OSError:
            pass
        null_fd = -1
        try:
            null_fd = os.open(os.devnull, os.O_RDWR | os.O_CLOEXEC)
        except OSError:
            null_fd = -1
        for stream in (0, 1, 2):
            try:
                if null_fd >= 0:
                    os.dup2(null_fd, stream)
            except OSError:
                pass
        if null_fd >= 0 and null_fd not in (0, 1, 2):
            try:
                os.close(null_fd)
            except OSError:
                pass
        try:
            child = os.fork()
        except OSError as error:
            os.write(ready_write, f"FORK-FAILED {error.errno}\n".encode("ascii"))
            os._exit(71)
        if child == 0:
            _holder_process(run_fd, control_address, token, deadline, ready_write)
            os._exit(0)
        os.close(ready_write)
        os._exit(0)
    os.close(ready_write)
    try:
        os.waitpid(intermediate, 0)
        ready = b""
        while b"\n" not in ready and len(ready) < 128:
            chunk = os.read(ready_read, 128)
            if not chunk:
                break
            ready += chunk
    finally:
        os.close(ready_read)
    line = ready.decode("ascii", "replace").strip()
    if not line.startswith("READY "):
        raise RunError("HOLDER_SPAWN_FAILED", line or "holder exited before readiness")
    try:
        return int(line.split()[1])
    except (IndexError, ValueError) as error:
        raise RunError("HOLDER_SPAWN_FAILED", f"unreadable readiness: {line!r}") from error


def _socket_request(address: str, request: dict[str, Any], *, timeout: float = 10.0) -> dict[str, Any] | None:
    """Send one bounded request to the holder control socket."""
    connection = _socket.socket(_socket.AF_UNIX, _socket.SOCK_STREAM)
    try:
        connection.settimeout(timeout)
        connection.connect(address)
        connection.sendall(json.dumps(request).encode("utf-8"))
        connection.shutdown(_socket.SHUT_WR)
        payload = b""
        while len(payload) <= MAX_RESPONSE_BYTES:
            chunk = connection.recv(MAX_RESPONSE_BYTES + 1)
            if not chunk:
                break
            payload += chunk
    except OSError:
        return None
    finally:
        try:
            connection.close()
        except OSError:
            pass
    if not payload or len(payload) > MAX_RESPONSE_BYTES:
        return None
    try:
        response = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    return response if isinstance(response, dict) else None


# --- Public lifecycle interface (AD-MRW1) -----------------------------------


@dataclass(frozen=True)
class RunHandle:
    run_id: str
    path: Path
    handle_file: Path
    state: str


@dataclass(frozen=True)
class RunReceipt:
    run_id: str
    state: str
    path: Path | None
    expires_at: datetime | None
    git_start_sha256: str
    git_finish_sha256: str | None
    code: str


@dataclass(frozen=True)
class PromotionReceipt:
    run_id: str
    source_sha256: str
    destination: Path
    destination_sha256: str
    git_before_sha256: str
    git_after_sha256: str
    code: str


@dataclass(frozen=True)
class RunEntry:
    run_id: str | None
    category: str
    state: str | None
    path: Path
    bytes: int
    expires_at: datetime | None
    report_only_reason: str | None
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunReport:
    entries: tuple[RunEntry, ...]
    counts: Mapping[str, int]
    total_bytes: int
    selected_bytes: int
    action: str
    code: str

    operations: tuple[dict[str, Any], ...] = ()
    diagnostics: tuple[dict[str, Any], ...] = ()
    remaining_eligible: int = 0
    remaining_bytes: int = 0

def _root_for_handle(handle_file: Path) -> tuple[RunRoot, str]:
    """Resolve the verified run root and handle name for a handle-file path."""
    resolved = Path(handle_file).expanduser().resolve()
    name = resolved.name
    if (
        not HANDLE_NAME_RE.fullmatch(name)
        or resolved.parent.name != "handles"
        or resolved.parent.parent.name != "kosmic"
        or resolved.parents[2].name != ".tmp"
    ):
        raise RunError("HANDLE_PATH_INVALID", str(handle_file))
    root = resolve_run_root(resolved.parents[3])
    return root, name


def _discard_tree(parent_fd: int, name: str) -> None:
    """Best-effort rollback removal of a creation that never completed."""
    try:
        status = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError:
        return
    if stat.S_ISDIR(status.st_mode) and not stat.S_ISLNK(status.st_mode):
        shutil.rmtree(name, dir_fd=parent_fd, ignore_errors=True)
    else:
        try:
            os.unlink(name, dir_fd=parent_fd)
        except OSError:
            pass


def begin_run(
    worktree: Path,
    purpose: str,
    retention: str = "diagnostic",
    active_for: timedelta = ACTIVE_DEFAULT,
) -> RunHandle:
    """Create a private leased run and return only after verified liveness."""
    if retention is None:
        retention = "diagnostic"
    if retention not in CREATION_RETENTIONS:
        raise RunError("RETENTION_UNKNOWN", f"{retention!r}; expected diagnostic or disposable")
    if not isinstance(active_for, timedelta) or active_for <= timedelta(0) or active_for > ACTIVE_MAX:
        raise RunError("ACTIVE_FOR_INVALID", f"{active_for!r}; expected (0, {ACTIVE_MAX}]")
    purpose = _redact_detail(str(purpose).strip())[:512] or "run"
    slug = _sanitize_purpose_slug(purpose)
    token = secrets.token_bytes(32)
    handle_name = secrets.token_hex(16)
    with resolve_run_root(Path(worktree)) as root:
        stamp = _now().strftime("%Y%m%dT%H%M%SZ")
        run_id = f"{stamp}-{slug}-{secrets.token_hex(16)}"
        deadline = _now() + active_for
        try:
            os.mkdir(run_id, PRIVATE_MODE, dir_fd=root.runs_fd)
        except OSError as error:
            raise RunError("RUN_CREATE_FAILED", f"{run_id}: {error}") from error
        run_fd = -1
        completed = False
        try:
            try:
                run_fd = os.open(run_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root.runs_fd)
                for child in ("git", "input", "logs", "output", "scratch"):
                    os.mkdir(child, PRIVATE_MODE, dir_fd=run_fd)
            except OSError as error:
                raise RunError("RUN_CREATE_FAILED", f"{run_id}: {error}") from error
            start = capture_git_snapshot(root.worktree, name="start")
            try:
                git_fd = os.open("git", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=run_fd)
                try:
                    _atomic_replace_bytes(git_fd, "start-status.porcelain-v2", start.raw, context=f"{run_id}/git/start")
                finally:
                    os.close(git_fd)
            except OSError as error:
                raise RunError("RUN_CREATE_FAILED", f"{run_id}/git: {error}") from error
            manifest = {
                "schema": 1,
                "sequence": 1,
                "run_id": run_id,
                "project_id": root.worktree.name,
                "purpose": purpose,
                "state": "creating",
                "retention": retention,
                "created_at": _format_utc(_now()),
                "finished_at": None,
                "expires_at": _format_utc(deadline),
                "lease_expires_at": _format_utc(deadline),
                "holder_pid": 0,
                "token_sha256": hashlib.sha256(token).hexdigest(),
                "worktree_root": str(root.worktree),
                "git_common_dir": start.common_dir,
                "git_start_sha256": start.sha256,
                "git_start_head": start.head,
                "git_start_branch": start.branch,
                "git_finish_sha256": None,
                "snapshot_complete": False,
            }
            _write_manifest(run_fd, manifest)
            _fsync_fd(run_fd, context=run_id)
            _fsync_fd(root.runs_fd, context="runs")
            handle = {
                "schema": 1,
                "kind": "handle",
                "run_id": run_id,
                "token": base64.b64encode(token).decode("ascii"),
                "uid": os.geteuid(),
                "created_at": _format_utc(_now()),
                "state": "active",
            }
            _write_handle(root.handles_fd, handle_name, handle)
            holder_pid = _spawn_holder(
                run_fd,
                _control_address(run_id),
                token,
                deadline,
                inherited_descriptors=(
                    root.kosmic_fd, root.runs_fd, root.quarantine_fd, root.operations_fd, root.handles_fd,
                ),
            )
            _fault("after-holder-spawn")
            probe_fd, acquired = _open_lock_nb(run_fd, run_id=run_id)
            try:
                if acquired:
                    raise RunError("HOLDER_DIED", f"{run_id}: lock released immediately after readiness")
            finally:
                os.close(probe_fd)
            manifest = _transition_manifest(
                run_fd,
                manifest,
                state="active",
                holder_pid=holder_pid,
            )
            _fault("after-activation")
            try:
                os.fsync(run_fd)
            except OSError as error:
                raise RunError("SYNC_FAILED", f"{run_id}: {error}") from error
            completed = True
            return RunHandle(
                run_id=run_id,
                path=root.path / "runs" / run_id,
                handle_file=root.path / "handles" / handle_name,
                state="active",
            )
        finally:
            if not completed:
                _discard_tree(root.handles_fd, handle_name)
                if run_fd >= 0:
                    try:
                        os.close(run_fd)
                    except OSError:
                        pass
                    run_fd = -1
                _discard_tree(root.runs_fd, run_id)
            elif run_fd >= 0:
                os.close(run_fd)


def _receipt_from_handle(handle: dict[str, Any]) -> RunReceipt:
    expires = _parse_utc(handle["expires_at"], "receipt") if handle.get("expires_at") else None
    return RunReceipt(
        run_id=handle["run_id"],
        state=str(handle["outcome"]),
        path=None,
        expires_at=expires,
        git_start_sha256=handle["git_start_sha256"],
        git_finish_sha256=handle.get("git_finish_sha256"),
        code=handle.get("code", "OK"),
    )


def _promotion_ids(root: RunRoot, run_id: str) -> list[str]:
    identifiers: list[str] = []
    for name in sorted(os.listdir(root.operations_fd)):
        if not name.endswith(".json"):
            continue
        try:
            operation = _read_json_bounded(root.operations_fd, name, limit=1 << 20, context=f"operations/{name}")
        except RunError:
            continue
        if isinstance(operation, dict) and operation.get("kind") == "promotion" and operation.get("run_id") == run_id:
            identifiers.append(str(operation.get("operation_id") or name[: -len(".json")]))
    return identifiers


def _terminal_receipt(
    run_id: str,
    handle: dict[str, Any],
    outcome: str,
    finished_at: str,
    expires_at: str | None,
    manifest: dict[str, Any],
    cleanup: str,
) -> dict[str, Any]:
    receipt_expires = _format_utc(_now() + RECEIPT_TTL)
    return {
        "schema": 1,
        "kind": "receipt",
        "run_id": run_id,
        "token_sha256": hashlib.sha256(base64.b64decode(handle["token"])).hexdigest(),
        "outcome": outcome,
        "detail": str(manifest.get("requested_detail") or ""),
        "finished_at": finished_at,
        "expires_at": expires_at,
        "retention": manifest["retention"],
        "git_start_sha256": manifest["git_start_sha256"],
        "git_finish_sha256": manifest["git_finish_sha256"],
        "cleanup": cleanup,
        "receipt_expires_at": receipt_expires,
        "promotions": list(manifest.get("promotions") or []),
    }


def _publish_receipt_with_promotions(root: RunRoot, handles_fd: int, handle_name: str, run_id: str, handle: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    receipt = _publish_receipt(root, handles_fd, handle_name, run_id, handle, manifest)
    promotions = _promotion_ids(root, run_id)
    if promotions and promotions != list(receipt.get("promotions") or []):
        receipt = {**receipt, "promotions": promotions}
        _write_handle(handles_fd, handle_name, receipt)
    return receipt


def finish_run(handle_file: Path, outcome: str, detail: str = "") -> RunReceipt:
    """Finalize a run idempotently with terminal Git evidence and retention."""
    if outcome not in OUTCOMES:
        raise RunError("OUTCOME_INVALID", repr(outcome))
    detail = _redact_detail(detail)
    root, handle_name = _root_for_handle(Path(handle_file))
    with root:
        handle = read_handle(root.handles_fd, handle_name)
        if handle["kind"] == "receipt":
            if handle["outcome"] != outcome:
                raise RunError("RUN_ALREADY_FINALIZED", f"{handle['run_id']}: {handle['outcome']}")
            if _exists_fd(root.runs_fd, handle["run_id"]):
                run_fd_replay = _open_run(root.runs_fd, handle["run_id"])
                try:
                    manifest_replay = load_manifest(run_fd_replay, run_id=handle["run_id"])
                    _execute_pending_cleanup(
                        root, handle["run_id"], manifest_replay, handle_name, handle,
                        held_lock_fd=None,
                    )
                finally:
                    os.close(run_fd_replay)
                handle = read_handle(root.handles_fd, handle_name)
            return _receipt_from_handle(handle)
        run_id = handle["run_id"]
        token_b64 = handle["token"]
        run_fd = _open_run(root.runs_fd, run_id)
        lock_fd = -1
        try:
            manifest = load_manifest(run_fd, run_id=run_id)
            state = manifest["state"]
            recovering_finalization = state == "finalizing"
            if state == "creating":
                raise RunError("RUN_NOT_ACTIVE", run_id)
            if state in TERMINAL_STATES:
                committed_outcome = manifest.get("requested_outcome")
                if committed_outcome not in OUTCOMES or committed_outcome != outcome:
                    raise RunError("RUN_ALREADY_FINALIZED", f"{run_id}: {state}")
                receipt = _publish_receipt(root, root.handles_fd, handle_name, run_id, handle, manifest)
                _execute_pending_cleanup(root, run_id, manifest, handle_name, handle, held_lock_fd=lock_fd if lock_fd >= 0 else None)
                return _receipt_from_handle(receipt)
            if state == "active":
                acknowledgment = _socket_request(_control_address(run_id), {
                    "op": "finish", "token": token_b64, "outcome": outcome, "detail": detail,
                })
                if acknowledgment is not None and not acknowledgment.get("ok"):
                    error = str(acknowledgment.get("error") or "HOLDER_REFUSED")
                    if error == "TOKEN":
                        raise RunError("HANDLE_TOKEN_MISMATCH", run_id)
                    raise RunError("HOLDER_REFUSED", f"{run_id}: {error}")
                if acknowledgment is None:
                    acquired = False
                    for _ in range(100):
                        lock_fd, acquired = _open_lock_nb(run_fd, run_id=run_id)
                        if acquired:
                            break
                        os.close(lock_fd)
                        lock_fd = -1
                        acknowledgment = _socket_request(_control_address(run_id), {
                            "op": "finish", "token": token_b64, "outcome": outcome, "detail": detail,
                        }, timeout=0.1)
                        if acknowledgment is not None:
                            break
                        _time.sleep(0.05)
                    if acknowledgment is None and not acquired:
                        raise RunError("LIVE_UNREACHABLE", run_id)
                    if acquired:
                        manifest = load_manifest(run_fd, run_id=run_id)
                        if manifest["state"] == "active":
                            manifest = _transition_manifest(
                                run_fd, manifest, state="finalizing", requested_outcome=outcome,
                                requested_detail=detail, requested_at=_format_utc(_now()),
                            )
                        elif manifest["state"] != "finalizing":
                            raise RunError("RUN_ALREADY_FINALIZED", f"{run_id}: {manifest['state']}")
                else:
                    manifest = load_manifest(run_fd, run_id=run_id)
                    if manifest["state"] != "finalizing" or manifest.get("requested_outcome") != outcome:
                        raise RunError("HOLDER_REFUSED", f"{run_id}: holder state {manifest['state']!r}")
                _fault("after-outcome-persist")
            if lock_fd < 0:
                for _ in range(100):
                    lock_fd, acquired = _open_lock_nb(run_fd, run_id=run_id)
                    if acquired:
                        break
                    os.close(lock_fd)
                    lock_fd = -1
                    _time.sleep(0.05)
                if lock_fd < 0 or not acquired:
                    raise RunError("LIVE_UNREACHABLE", run_id)
            _fault("after-lock-reacquire")
            manifest = load_manifest(run_fd, run_id=run_id)
            if manifest["state"] != "finalizing" or manifest.get("requested_outcome") not in OUTCOMES:
                raise RunError("TRANSITION_INVALID", f"{run_id}: {manifest['state']!r}")
            if manifest["requested_outcome"] != outcome:
                raise RunError("RUN_ALREADY_FINALIZED", f"{run_id}: persisted {manifest['requested_outcome']}")
            finish = capture_git_snapshot(root.worktree, name="finish")
            interrupted_capture = recovering_finalization
            snapshot_name = "recovery-status.porcelain-v2" if interrupted_capture else "finish-status.porcelain-v2"
            try:
                git_fd = os.open("git", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=run_fd)
            except OSError as error:
                raise RunError("RUN_OPEN_FAILED", f"{run_id}/git: {error}") from error
            try:
                _atomic_replace_bytes(git_fd, snapshot_name, finish.raw, context=f"{run_id}/git/{snapshot_name}")
                if interrupted_capture:
                    _atomic_replace_bytes(
                        git_fd, "recovery.json", _json_bytes({"schema": 1, "reason": "interrupted-finalization", "ts": _format_utc(_now())}), context=f"{run_id}/git/recovery.json"
                    )
                start_raw = _read_bounded(git_fd, "start-status.porcelain-v2", limit=64 << 20, context=f"{run_id}/git/start")
                start_snapshot = _snapshot_from_raw(start_raw, source=f"{run_id}/git/start")
                _atomic_replace_bytes(git_fd, "delta.json", _json_bytes(git_delta(start_snapshot, finish)), context=f"{run_id}/git/delta")
            finally:
                os.close(git_fd)
            _fault("after-terminal-git")
            terminal_instant = _now()
            finished_at = _format_utc(terminal_instant)
            if outcome == "failed" and manifest["retention"] in ("diagnostic", "extended-diagnostic"):
                expires_at = _format_utc(terminal_instant + FAILURE_RETENTION)
            else:
                expires_at = finished_at
            manifest = _transition_manifest(
                run_fd,
                manifest,
                state=outcome,
                finished_at=finished_at,
                expires_at=expires_at,
                git_finish_sha256=finish.sha256,
                git_finish_head=finish.head,
                git_finish_branch=finish.branch,
                snapshot_complete=True,
                recovered=True if interrupted_capture else None,
            )
            _fault("after-manifest-commit")
            receipt = _publish_receipt(root, root.handles_fd, handle_name, run_id, handle, manifest)
            _fault("after-receipt")
            _execute_pending_cleanup(root, run_id, manifest, handle_name, handle, held_lock_fd=lock_fd)
            return _receipt_from_handle(read_handle(root.handles_fd, handle_name))
        finally:
            if lock_fd >= 0:
                os.close(lock_fd)
            os.close(run_fd)


def _snapshot_file_exists(run_fd: int) -> bool:
    try:
        git_fd = os.open("git", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=run_fd)
    except OSError:
        return False
    try:
        return _exists_fd(git_fd, "finish-status.porcelain-v2")
    finally:
        os.close(git_fd)


def _snapshot_from_raw(raw: bytes, *, source: str) -> GitSnapshot:
    parsed = _parse_porcelain_v2(raw, source=source)
    branch_head = parsed["branch"].get("branch.head")
    if branch_head in ("(detached)", ""):
        branch_head = None
    branch_oid = parsed["branch"].get("branch.oid")
    if branch_oid == "(initial)":
        branch_oid = None
    return GitSnapshot(
        head=branch_oid,
        branch=branch_head,
        branch_oid=branch_oid,
        toplevel="",
        common_dir="",
        raw=raw,
        sha256=hashlib.sha256(raw).hexdigest(),
        paths=tuple(sorted({entry["path"] for entry in parsed["entries"]})),
        renames=tuple((entry["orig_path"], entry["path"]) for entry in parsed["entries"] if entry["kind"] == "renamed"),
    )


def _publish_receipt(
    root: RunRoot,
    handles_fd: int,
    handle_name: str,
    run_id: str,
    handle: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    """Atomically rewrite the private handle as a bounded terminal receipt."""
    cleanup_state = manifest.get("cleanup") or ("eligible" if _cleanup_eligible(manifest, _now()) else "retained")
    receipt = _terminal_receipt(
        run_id,
        handle,
        str(manifest["state"]),
        manifest["finished_at"] or _format_utc(_now()),
        manifest["expires_at"],
        manifest,
        cleanup_state,
    )
    _write_handle(handles_fd, handle_name, receipt)
    return receipt


def _cleanup_eligible(manifest: dict[str, Any], moment: datetime) -> bool:
    """Whole-run retention decision (AD-MRW6)."""
    state = manifest["state"]
    if state not in TERMINAL_STATES:
        return False
    if state == "abandoned":
        return True
    if manifest["retention"] == "disposable":
        return True
    if state == "succeeded":
        return manifest["retention"] == "diagnostic"
    expires = manifest.get("expires_at")
    if expires is None:
        return False
    return moment >= _parse_utc(expires, "expires_at")


def extend_run(handle_file: Path, until: datetime) -> RunReceipt:
    """Extend a failed diagnostic run once or repeatedly, capped at seven days."""
    if not isinstance(until, datetime) or until.tzinfo is None:
        raise RunError("EXTENSION_INVALID", "until must be an aware datetime")
    until = until.astimezone(timezone.utc)
    root, handle_name = _root_for_handle(Path(handle_file))
    with root:
        handle = read_handle(root.handles_fd, handle_name)
        run_id = handle["run_id"]
        if handle["kind"] == "receipt":
            current = _parse_utc(handle["expires_at"], "receipt") if handle.get("expires_at") else None
            if current is not None and until <= current:
                return _receipt_from_handle(handle)
        run_fd = _open_run(root.runs_fd, run_id)
        lock_fd = -1
        try:
            manifest = load_manifest(run_fd, run_id=run_id)
            if manifest["state"] != "failed" or manifest["retention"] not in ("diagnostic", "extended-diagnostic"):
                raise RunError("EXTENSION_INVALID_STATE", f"{run_id}: {manifest['state']}/{manifest['retention']}")
            lock_fd, acquired = _open_lock_nb(run_fd, run_id=run_id)
            if not acquired:
                raise RunError("LIVE_UNREACHABLE", run_id)
            manifest = load_manifest(run_fd, run_id=run_id)
            if manifest["state"] != "failed" or manifest["retention"] not in ("diagnostic", "extended-diagnostic"):
                raise RunError("EXTENSION_INVALID_STATE", f"{run_id}: {manifest['state']}/{manifest['retention']}")
            finished = _parse_utc(manifest["finished_at"], "finished_at")
            cap = finished + EXTENSION_CAP
            if until > cap:
                raise RunError("EXTENSION_CAP_EXCEEDED", f"{run_id}: cap {_format_utc(cap)}")
            if until <= _now():
                raise RunError("EXTENSION_INVALID", f"{run_id}: until {until.isoformat()} is not in the future")
            current_expiry = _parse_utc(manifest["expires_at"], "expires_at")
            if until <= current_expiry:
                if handle["kind"] != "receipt":
                    receipt = _publish_receipt(root, root.handles_fd, handle_name, run_id, handle, manifest)
                    return _receipt_from_handle(receipt)
                return _receipt_from_handle(handle)
            manifest = _transition_manifest(
                run_fd,
                manifest,
                retention="extended-diagnostic",
                expires_at=_format_utc(until),
                extended_at=_format_utc(_now()),
            )
            if handle["kind"] == "receipt":
                receipt = {
                    **handle,
                    "expires_at": manifest["expires_at"],
                    "retention": "extended-diagnostic",
                    "extended_at": manifest["extended_at"],
                }
                _write_handle(root.handles_fd, handle_name, receipt)
            else:
                receipt = _publish_receipt(root, root.handles_fd, handle_name, run_id, handle, manifest)
            return _receipt_from_handle(receipt)
        finally:
            if lock_fd >= 0:
                os.close(lock_fd)
            os.close(run_fd)


def run_live_status(worktree: Path, run_id: str) -> dict[str, Any]:
    """Authoritative single-run status: holder while leased, manifest otherwise."""
    with resolve_run_root(Path(worktree)) as root:
        run_fd = _open_run(root.runs_fd, run_id)
        try:
            manifest = load_manifest(run_fd, run_id=run_id)
            result: dict[str, Any] = {"run_id": run_id, "state": manifest["state"], "live": False, "code": "OK"}
            if manifest["state"] not in ("active", "creating"):
                result["expires_at"] = manifest["expires_at"]
                result["cleanup_eligible"] = _cleanup_eligible(manifest, _now())
                return result
            if _lock_held(run_fd, run_id=run_id):
                token_b64 = None
                for handle_name in sorted(os.listdir(root.handles_fd)):
                    if not HANDLE_NAME_RE.fullmatch(handle_name):
                        continue
                    try:
                        candidate = read_handle(root.handles_fd, handle_name)
                    except RunError:
                        continue
                    if candidate.get("kind") == "handle" and candidate.get("run_id") == run_id:
                        token_b64 = candidate.get("token")
                        break
                acknowledgment = None if token_b64 is None else _socket_request(
                    _control_address(run_id), {"op": "ping", "token": token_b64}, timeout=0.5
                )
                if acknowledgment is None or not acknowledgment.get("ok"):
                    return {"run_id": run_id, "state": manifest["state"], "live": False, "code": "LIVE_UNREACHABLE"}
                return {
                    "run_id": run_id, "state": acknowledgment.get("state", manifest["state"]),
                    "live": True, "code": "OK", "lease_expires_at": manifest["lease_expires_at"],
                }
            result["state"] = "active"
            result["abandoned_candidate"] = True
            result["grace_until"] = _format_utc(_parse_utc(manifest["lease_expires_at"], "lease") + UNLOCK_GRACE)
            return result
        finally:
            os.close(run_fd)


# --- Journaled cleanup transaction (AD-MRW7) --------------------------------


OPERATION_NAME_RE = re.compile(r"(?:cleanup|promote)-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{12}\Z")


def _operation_write(operations_fd: int, operation_id: str, operation: dict[str, Any]) -> None:
    if not OPERATION_NAME_RE.fullmatch(operation_id):
        raise RunError("OPERATION_ID_INVALID", operation_id)
    _atomic_replace_bytes(operations_fd, f"{operation_id}.json", _json_bytes(operation), context=f"operations/{operation_id}")


def _run_summary(manifest: dict[str, Any], usage_bytes: int = 0) -> dict[str, Any]:
    return {
        "run_id": manifest["run_id"],
        "purpose": manifest["purpose"],
        "state": manifest["state"],
        "retention": manifest["retention"],
        "created_at": manifest["created_at"],
        "finished_at": manifest["finished_at"],
        "expires_at": manifest["expires_at"],
        "git_start_sha256": manifest["git_start_sha256"],
        "git_finish_sha256": manifest["git_finish_sha256"],
        "snapshot_complete": manifest["snapshot_complete"],
        "bytes": usage_bytes,
    }


def _history_pending_operations(root: RunRoot) -> set[str]:
    pending: set[str] = set()
    for name in os.listdir(root.operations_fd):
        if not name.endswith(".json"):
            continue
        try:
            operation = _read_json_bounded(root.operations_fd, name, limit=1 << 20, context=f"operations/{name}")
        except RunError:
            pending.add(name[: -len(".json")])
            continue
        if isinstance(operation, dict) and operation.get("state") != "recorded":
            pending.add(str(operation.get("operation_id") or name[: -len(".json")]))
    return pending


def _rotate_history(root: RunRoot) -> None:
    """Rotate history by age and size, preserving incomplete operations.

    Records older than thirty days are dropped (unless their operation is
    still incomplete) and, when the file exceeds the size cap, the oldest
    remaining records are trimmed until it fits. An unreadable or oversized
    history file raises instead of silently skipping the bound.
    """
    raw = _read_bounded(root.kosmic_fd, HISTORY_FILENAME, limit=HISTORY_READ_LIMIT, context=HISTORY_FILENAME)
    pending = _history_pending_operations(root)
    cutoff = _now() - HISTORY_MAX_AGE
    kept: list[tuple[bytes, datetime]] = []
    for line in raw.splitlines(keepends=True):
        if not line.strip():
            continue
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            kept.append((line, _now()))
            continue
        timestamp = record.get("ts") if isinstance(record, dict) else None
        try:
            moment = _parse_utc(timestamp, "history") if isinstance(timestamp, str) else None
        except RunError:
            moment = None
        if moment is not None and moment < cutoff and str(record.get("operation_id") or "") not in pending:
            continue
        kept.append((line, moment or _now()))
    total = sum(len(line) for line, _ in kept)
    while kept and total > HISTORY_MAX_BYTES:
        line, _ = kept.pop(0)  # trim oldest first; stable chronological order
        total -= len(line)
    _atomic_replace_bytes(root.kosmic_fd, HISTORY_FILENAME, b"".join(line for line, _ in kept), context=HISTORY_FILENAME)


def _history_contains(root: RunRoot, operation_id: str) -> bool:
    try:
        raw = _read_bounded(root.kosmic_fd, HISTORY_FILENAME, limit=HISTORY_READ_LIMIT, context=HISTORY_FILENAME)
    except RunError:
        return False
    for line in raw.splitlines():
        try:
            record = json.loads(line.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
        if isinstance(record, dict) and record.get("operation_id") == operation_id:
            return True
    return False


def _history_append(root: RunRoot, record: dict[str, Any]) -> None:
    operation_id = str(record.get("operation_id") or "")
    if operation_id and _history_contains(root, operation_id):
        return  # idempotent history commit for replayed operations
    line = _json_bytes(record)
    try:
        descriptor = os.open(
            HISTORY_FILENAME, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=root.kosmic_fd
        )
    except OSError as error:
        raise RunError("HISTORY_WRITE_FAILED", f"{HISTORY_FILENAME}: {error}") from error
    try:
        view = memoryview(line)
        offset = 0
        while offset < len(line):
            try:
                offset += os.write(descriptor, view[offset:])
            except OSError as error:
                raise RunError("HISTORY_WRITE_FAILED", f"{HISTORY_FILENAME}: {error}") from error
        _fsync_fd(descriptor, context=HISTORY_FILENAME)
    finally:
        os.close(descriptor)
    _fsync_fd(root.kosmic_fd, context="kosmic")
    try:
        size = os.stat(HISTORY_FILENAME, dir_fd=root.kosmic_fd, follow_symlinks=False).st_size
    except OSError as error:
        # An unreadable size must not silently skip the rotation bound.
        raise RunError("HISTORY_WRITE_FAILED", f"{HISTORY_FILENAME}: post-append stat: {error}") from error
    if size >= HISTORY_MAX_BYTES:
        _rotate_history(root)


def _exists_fd(dir_fd: int, name: str) -> bool:
    try:
        os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
        return True
    except OSError:
        return False


def _new_operation_id(kind: str) -> str:
    return f"{kind}-{_now().strftime('%Y%m%dT%H%M%SZ')}-{secrets.token_hex(6)}"


def _execute_cleanup_transaction(
    root: RunRoot,
    run_id: str,
    manifest: dict[str, Any],
    *,
    operation: dict[str, Any] | None = None,
    held_lock_fd: int | None = None,
) -> dict[str, Any]:
    """Plan, quarantine, remove, and record one run deletion (AD-MRW7)."""
    if not shutil.rmtree.avoids_symlink_attacks:
        raise RunError("DESTRUCTIVE_UNSUPPORTED", "platform rmtree is not symlink-resistant")
    usage_bytes = 0
    run_fd = -1
    lock_fd = -1
    identity = None
    try:
        if operation is None:
            if not _exists_fd(root.runs_fd, run_id):
                raise RunError("RUN_MISSING", run_id)
            run_fd = _open_run(root.runs_fd, run_id)
            usage, _complete = _tree_bytes(run_fd, device=root.device)
            usage_bytes = usage
            operation_id = _new_operation_id("cleanup")
            before = capture_git_snapshot(root.worktree, name=f"cleanup-{run_id}-before")
            operation = {
                "schema": 1,
                "git_before_basis": {"head": before.head, "paths": list(before.paths)},
                "kind": "cleanup",
                "operation_id": operation_id,
                "run_id": run_id,
                "state": "planned",
                "run_summary": _run_summary(manifest, usage_bytes),
                "git_before_sha256": before.sha256,
                "git_after_sha256": None,
                "result": None,
                "created_at": _format_utc(_now()),
                "updated_at": _format_utc(_now()),
            }
            _operation_write(root.operations_fd, operation_id, operation)
        operation_id = operation["operation_id"]
        summary = dict(operation.get("run_summary") or {})
        usage_bytes = int(summary.get("bytes") or 0) or usage_bytes
        _fault("cleanup-after-planned")
        source_present = _exists_fd(root.runs_fd, run_id)
        quarantine_present = _exists_fd(root.quarantine_fd, operation_id)
        if source_present and quarantine_present:
            raise RunError("RECOVERY_CONFLICT", operation_id)
        if source_present:
            if run_fd < 0:
                run_fd = _open_run(root.runs_fd, run_id)
            if operation["state"] == "planned":
                if held_lock_fd is None:
                    lock_fd, acquired = _open_lock_nb(run_fd, run_id=run_id)
                    if not acquired:
                        os.close(lock_fd)
                        lock_fd = -1
                        raise RunError("RUN_ACTIVE", run_id)
                current = load_manifest(run_fd, run_id=run_id)
                if current["run_id"] != run_id:
                    raise RunError("RUN_ID_MISMATCH", run_id)
                if not _cleanup_eligible(current, _now()):
                    raise RunError("CLEANUP_NOT_ELIGIBLE", run_id)
                # Authoritative identity of the validated tree, captured under
                # the lease: the quarantined child must still be this inode.
                identity = os.fstat(run_fd)
                try:
                    os.mkdir(operation_id, PRIVATE_MODE, dir_fd=root.quarantine_fd)
                except OSError as error:
                    raise RunError("QUARANTINE_FAILED", f"{operation_id}: {error}") from error
                try:
                    os.rename(run_id, operation_id, src_dir_fd=root.runs_fd, dst_dir_fd=root.quarantine_fd)
                except OSError as error:
                    if error.errno == errno.EXDEV:
                        raise RunError("DEVICE_MISMATCH", f"{run_id}: quarantine rename crossed devices") from error
                    raise RunError("QUARANTINE_FAILED", f"{run_id}: {error}") from error
                _fsync_fd(root.runs_fd, context="runs")
                _fsync_fd(root.quarantine_fd, context="quarantine")
                operation = {**operation, "state": "quarantined", "updated_at": _format_utc(_now())}
                _operation_write(root.operations_fd, operation_id, operation)
                _verify_quarantined_identity(root, operation_id, identity, run_id)
            elif operation["state"] != "recorded":
                raise RunError("RECOVERY_CONFLICT", f"{operation_id}: {operation['state']} with source present")
        _fault("cleanup-after-quarantine")
        if _exists_fd(root.quarantine_fd, operation_id):
            if operation["state"] == "planned":
                # Crash between the quarantine rename and its journal write.
                operation = {**operation, "state": "quarantined", "updated_at": _format_utc(_now())}
                _operation_write(root.operations_fd, operation_id, operation)
            if identity is not None:
                _verify_quarantined_identity(root, operation_id, identity, run_id)
            try:
                status = os.stat(operation_id, dir_fd=root.quarantine_fd, follow_symlinks=False)
            except OSError as error:
                raise RunError("QUARANTINE_INVALID", f"{operation_id}: {error}") from error
            if stat.S_ISLNK(status.st_mode) or not stat.S_ISDIR(status.st_mode):
                raise RunError("QUARANTINE_INVALID", operation_id)
            if status.st_uid != os.geteuid():
                raise RunError("QUARANTINE_UNTRUSTED", operation_id)
            if status.st_dev != root.device:
                raise RunError("DEVICE_MISMATCH", f"{operation_id}: quarantined tree changed device")
            try:
                shutil.rmtree(operation_id, dir_fd=root.quarantine_fd)
            except OSError as error:
                raise RunError("REMOVAL_FAILED", f"{operation_id}: {error}") from error
            _fsync_fd(root.quarantine_fd, context="quarantine")
            operation = {**operation, "state": "deleted", "updated_at": _format_utc(_now())}
            _operation_write(root.operations_fd, operation_id, operation)
        _fault("cleanup-after-removed")
        if operation["state"] != "recorded":
            git_before_basis = operation.get("git_before_basis")
            if (
                not isinstance(git_before_basis, dict)
                or not isinstance(git_before_basis.get("paths"), list)
                or not all(isinstance(path, str) for path in git_before_basis["paths"])
                or (git_before_basis.get("head") is not None and not isinstance(git_before_basis.get("head"), str))
            ):
                raise RunError("GIT_BASIS_INVALID", operation_id)
            after = capture_git_snapshot(root.worktree, name=f"cleanup-{run_id}-after")
            cleanup_delta = _git_delta_from_basis(git_before_basis, after)
            _history_append(root, {
                "schema": 1,
                "kind": "cleanup",
                "ts": _format_utc(_now()),
                "run_id": run_id,
                "operation_id": operation_id,
                "run_summary": operation["run_summary"],
                "git_before_sha256": operation["git_before_sha256"],
                "git_after_sha256": after.sha256,
                "git_delta": cleanup_delta,
                "result": "removed",
            })
            operation = {
                **operation,
                "state": "recorded",
                "result": "removed",
                "git_after_sha256": after.sha256,
                "git_before_head": git_before_basis.get("head"),
                "git_after_head": after.head,
                "git_delta": cleanup_delta,
                "updated_at": _format_utc(_now()),
            }
            _operation_write(root.operations_fd, operation_id, operation)
        _fault("cleanup-after-history")
        try:
            os.unlink(f"{operation_id}.json", dir_fd=root.operations_fd)
            _fsync_fd(root.operations_fd, context="operations")
        except OSError:
            pass
        return {
            "operation_id": operation_id,
            "result": "removed",
            "bytes_removed": usage_bytes,
            "git_before_sha256": operation["git_before_sha256"],
            "git_after_sha256": operation["git_after_sha256"],
            "git_delta": operation.get("git_delta"),
        }
    finally:
        if lock_fd >= 0:
            os.close(lock_fd)
        if run_fd >= 0:
            os.close(run_fd)

def recover_cleanup_operations(worktree: Path, *, recover_promotions: bool = True) -> list[dict[str, Any]]:
    """Reprocess operation and quarantine remnants idempotently."""
    reports: list[dict[str, Any]] = []
    with resolve_run_root(Path(worktree)) as root:
        for name in sorted(os.listdir(root.operations_fd)):
            if not name.endswith(".json"):
                reports.append({"operation_id": name, "result": "report-only", "reason": "UNATTRIBUTED_OPERATION_NAME"})
                continue
            operation_id = name[: -len(".json")]
            if not OPERATION_NAME_RE.fullmatch(operation_id):
                reports.append({"operation_id": name, "result": "report-only", "reason": "UNATTRIBUTED_OPERATION_NAME"})
                continue
            try:
                operation = _read_json_bounded(
                    root.operations_fd, name, limit=1 << 20, context=f"operations/{name}"
                )
            except RunError as error:
                reports.append({"operation_id": operation_id, "result": "report-only", "reason": error.code})
                continue
            if not isinstance(operation, dict) or operation.get("schema") != 1:
                reports.append({"operation_id": operation_id, "result": "report-only", "reason": "OPERATION_SCHEMA_UNKNOWN"})
                continue
            if operation.get("kind") == "promotion":
                if recover_promotions:
                    reports.extend(_recover_promotion_operation(root, operation_id, operation))
                else:
                    reports.append({"operation_id": operation_id, "result": "deferred", "reason": "PROMOTION_RECOVERY_DISABLED"})
                continue
            if operation.get("kind") != "cleanup":
                reports.append({"operation_id": operation_id, "result": "report-only", "reason": "OPERATION_KIND_UNKNOWN"})
                continue
            run_id = str(operation.get("run_id") or "")
            if not RUN_ID_RE.fullmatch(run_id):
                reports.append({"operation_id": operation_id, "result": "report-only", "reason": "RUN_ID_INVALID"})
                continue
            if operation.get("state") == "recorded":
                handle_record = _find_run_handle(root, run_id)
                if handle_record is not None:
                    _update_receipt_cleanup(root.handles_fd, handle_record[0], "removed", "OK")
                try:
                    os.unlink(name, dir_fd=root.operations_fd)
                    reports.append({"operation_id": operation_id, "result": "recorded-leftover-removed"})
                except OSError:
                    pass
                continue
            source_present = _exists_fd(root.runs_fd, run_id)
            quarantine_present = _exists_fd(root.quarantine_fd, operation_id)
            if source_present and quarantine_present:
                reports.append({"operation_id": operation_id, "result": "report-only", "reason": "RECOVERY_CONFLICT"})
                continue
            if source_present and not quarantine_present:
                try:
                    run_fd = _open_run(root.runs_fd, run_id)
                except RunError:
                    reports.append({"operation_id": operation_id, "result": "report-only", "reason": "RUN_OPEN_FAILED"})
                    continue
                try:
                    manifest = load_manifest(run_fd, run_id=run_id)
                except RunError as error:
                    reports.append({"operation_id": operation_id, "result": "report-only", "reason": error.code})
                    continue
                finally:
                    os.close(run_fd)
                if not _cleanup_eligible(manifest, _now()):
                    reports.append({"operation_id": operation_id, "result": "report-only", "reason": "CLEANUP_NOT_ELIGIBLE"})
                    continue
            try:
                result = _execute_cleanup_transaction(root, run_id, dict(operation.get("run_summary") or {}), operation=operation)
            except RunError as error:
                reports.append({"operation_id": operation_id, "result": "report-only", "reason": error.code})
                continue
            # recovery history record for already-observed deletions
            handle_record = _find_run_handle(root, run_id)
            if handle_record is not None:
                _update_receipt_cleanup(root.handles_fd, handle_record[0], "removed", "OK")
            reports.append({"operation_id": operation_id, "result": result["result"], "recovered": True})
        for name in sorted(os.listdir(root.quarantine_fd)):
            if not _exists_fd(root.operations_fd, f"{name}.json"):
                reports.append({"operation_id": name, "result": "report-only", "reason": "ORPHAN_QUARANTINE_CHILD"})
    return reports


def _verify_quarantined_identity(root: RunRoot, operation_id: str, identity: os.stat_result, run_id: str) -> None:
    """Prove the quarantined child is the validated run inode before removal."""
    try:
        child_fd = os.open(
            operation_id, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root.quarantine_fd
        )
    except OSError as error:
        raise RunError("QUARANTINE_INVALID", f"{operation_id}: {error}") from error
    try:
        current = os.fstat(child_fd)
        if (current.st_dev, current.st_ino) != (identity.st_dev, identity.st_ino):
            raise RunError("QUARANTINE_IDENTITY_MISMATCH", operation_id)
        if stat.S_IMODE(current.st_mode) != PRIVATE_MODE or current.st_uid != os.geteuid():
            raise RunError("QUARANTINE_UNTRUSTED", operation_id)
        manifest = load_manifest(child_fd, run_id=run_id)
        if manifest["run_id"] != run_id:
            raise RunError("RUN_ID_MISMATCH", run_id)
    finally:
        os.close(child_fd)


def _recover_promotion_operation(root: RunRoot, operation_id: str, operation: dict[str, Any]) -> list[dict[str, Any]]:
    """Finish only a matching recorded publication; never touch an unexpected destination.

    A ``staged`` operation resumes publication only when the recorded
    destination precondition still holds (absent, or exactly the recorded
    overwrite hash); a ``published`` operation only needs its history record.
    Every other constellation is report-only ambiguity.
    """
    destination = str(operation.get("destination") or "")
    run_id = str(operation.get("run_id") or "")
    if not RUN_ID_RE.fullmatch(run_id):
        return [{"operation_id": operation_id, "result": "report-only", "reason": "RUN_ID_INVALID"}]
    git_before_basis = operation.get("git_before_basis")
    if (
        not isinstance(git_before_basis, dict)
        or not isinstance(git_before_basis.get("paths"), list)
        or not all(isinstance(path, str) for path in git_before_basis["paths"])
        or (git_before_basis.get("head") is not None and not isinstance(git_before_basis.get("head"), str))
    ):
        return [{"operation_id": operation_id, "result": "report-only", "reason": "GIT_BASIS_INVALID"}]
    precondition = operation.get("destination_precondition") or {}
    staging_name = str(operation.get("staging_name") or "")
    # Journal fields are untrusted input: recovery may only touch the exact
    # reserved staging basename derived from the validated operation id.
    if staging_name != f".kosmic-promote-{operation_id}.tmp":
        return [{"operation_id": operation_id, "result": "report-only", "reason": "STAGING_NAME_INVALID"}]
    parts = tuple(part for part in destination.split("/") if part)
    if not parts or any(part in ("", ".", "..") for part in parts):
        return [{"operation_id": operation_id, "result": "report-only", "reason": "DESTINATION_PATH_INVALID"}]
    try:
        parent_fd = _open_worktree_directory(root, parts[:-1])
    except RunError as error:
        return [{"operation_id": operation_id, "result": "report-only", "reason": error.code}]
    destination_name = parts[-1]
    parts = tuple(part for part in parts)
    destination_fd = -1
    stage_fd = -1
    try:
        try:
            destination_fd = os.open(
                destination_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent_fd
            )
        except OSError:
            destination_fd = -1
        try:
            destination_hash = _hash_fd(destination_fd) if destination_fd >= 0 else None
        except OSError as error:
            return [
                {
                    "operation_id": operation_id,
                    "result": "report-only",
                    "reason": f"PROMOTION_READ_FAILED:{error.errno}",
                }
            ]
        finally:
            if destination_fd >= 0:
                os.close(destination_fd)
            destination_fd = -1
        source_sha = str(operation.get("source_sha256") or "")
        try:
            stage_fd = os.open(staging_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent_fd)
        except OSError:
            stage_fd = -1
        state = str(operation.get("state") or "")
        if destination_hash == source_sha:
            # publication already happened before the crash; finish the record
            if state != "recorded":
                after = capture_git_snapshot(root.worktree, name=f"promotion-{operation_id}-recovery")
                promotion_delta = _git_delta_from_basis(git_before_basis, after)
                _history_append(root, {
                    "schema": 1, "kind": "promotion", "ts": _format_utc(_now()),
                    "run_id": run_id, "operation_id": operation_id,
                    "source": str(operation.get("source") or ""),
                    "source_sha256": source_sha, "destination": str(operation.get("destination") or ""),
                    "destination_sha256": destination_hash,
                    "overwrite": bool(operation.get("overwrite")),
                    "git_before_sha256": operation.get("git_before_sha256"),
                    "git_after_sha256": after.sha256,
                    "git_delta": promotion_delta,
                    "recovered": True, "result": "published",
                })
                operation = {
                    **operation,
                    "state": "recorded",
                    "result": "published",
                    "destination_sha256": destination_hash,
                    "git_after_sha256": after.sha256,
                    "git_before_head": git_before_basis.get("head"),
                    "git_after_head": after.head,
                    "git_delta": promotion_delta,
                    "updated_at": _format_utc(_now()),
                }
                _operation_write(root.operations_fd, operation_id, operation)
            return [{"operation_id": operation_id, "result": "published", "recovered": True}]
        if state != "staged":
            return [{"operation_id": operation_id, "result": "report-only", "reason": "PROMOTION_AMBIGUOUS"}]
        # an unexpected destination is never removed or replaced, whatever the stage state
        if precondition.get("exists"):
            if destination_hash != str(precondition.get("sha256") or ""):
                return [{"operation_id": operation_id, "result": "report-only", "reason": "PRECONDITION_MISMATCH"}]
        elif destination_hash is not None:
            return [{"operation_id": operation_id, "result": "report-only", "reason": "DESTINATION_APPEARED"}]
        if stage_fd < 0:
            return [{"operation_id": operation_id, "result": "report-only", "reason": "PROMOTION_AMBIGUOUS"}]
        try:
            stage_status = os.fstat(stage_fd)
            if not stat.S_ISREG(stage_status.st_mode) or stage_status.st_dev != root.device:
                return [{"operation_id": operation_id, "result": "report-only", "reason": "PROMOTION_AMBIGUOUS"}]
            if _hash_fd(stage_fd) != source_sha:
                return [{"operation_id": operation_id, "result": "report-only", "reason": "PROMOTION_HASH_MISMATCH"}]
        except OSError as error:
            return [{"operation_id": operation_id, "result": "report-only", "reason": f"PROMOTION_READ_FAILED:{error.errno}"}]
        try:
            published_hash = _publish_staged_file(
                parent_fd,
                staging_name,
                destination_name,
                source_sha,
                precondition,
                overwrite=bool(precondition.get("exists")),
                context=str(operation.get("destination") or destination_name),
            )
        except RunError as error:
            return [{"operation_id": operation_id, "result": "report-only", "reason": error.code}]
        after = capture_git_snapshot(root.worktree, name=f"promotion-{operation_id}-after")
        promotion_delta = _git_delta_from_basis(git_before_basis, after)
        _history_append(root, {
            "schema": 1,
            "kind": "promotion",
            "ts": _format_utc(_now()),
            "run_id": run_id,
            "operation_id": operation_id,
            "source": str(operation.get("source") or ""),
            "source_sha256": source_sha,
            "destination": str(operation.get("destination") or ""),
            "destination_sha256": published_hash,
            "overwrite": bool(operation.get("overwrite")),
            "git_before_sha256": operation.get("git_before_sha256"),
            "git_after_sha256": after.sha256,
            "git_delta": promotion_delta,
            "recovered": True,
            "result": "published",
        })
        operation = {
            **operation,
            "state": "recorded",
            "result": "published",
            "destination_sha256": published_hash,
            "git_after_sha256": after.sha256,
            "git_before_head": git_before_basis.get("head"),
            "git_after_head": after.head,
            "git_delta": promotion_delta,
            "updated_at": _format_utc(_now()),
        }
        _operation_write(root.operations_fd, operation_id, operation)
        return [{"operation_id": operation_id, "result": "published", "recovered": True}]
    finally:
        if destination_fd >= 0:
            try:
                os.close(destination_fd)
            except OSError:
                pass
        if stage_fd >= 0:
            try:
                os.close(stage_fd)
            except OSError:
                pass
        os.close(parent_fd)


def _update_receipt_cleanup(handles_fd: int, handle_name: str, cleanup: str, code: str) -> None:
    receipt = read_handle(handles_fd, handle_name)
    if receipt["kind"] != "receipt":
        return
    updated = {**receipt, "cleanup": cleanup, "code": code}
    _write_handle(handles_fd, handle_name, updated)


def _execute_pending_cleanup(
    root: RunRoot,
    run_id: str,
    manifest: dict[str, Any],
    handle_name: str,
    handle: dict[str, Any],
    held_lock_fd: int | None = None,
) -> None:
    """Owner-driven terminal cleanup through the journaled transaction."""
    if handle["kind"] == "receipt" and str(handle.get("cleanup") or "") == "removed":
        return
    if not _cleanup_eligible(manifest, _now()):
        _update_receipt_cleanup(root.handles_fd, handle_name, "retained", "OK")
        return
    try:
        result = _execute_cleanup_transaction(root, run_id, manifest, held_lock_fd=held_lock_fd)
    except RunError as error:
        _update_receipt_cleanup(root.handles_fd, handle_name, f"pending:{error.code}", f"CLEANUP_PENDING:{error.code}")
        return
    _update_receipt_cleanup(root.handles_fd, handle_name, "removed", "OK")


# --- Durable promotion (AD-MRW11) -------------------------------------------


def _hash_fd(descriptor: int) -> str:
    digest = hashlib.sha256()
    os.lseek(descriptor, 0, os.SEEK_SET)
    while True:
        chunk = os.read(descriptor, 1 << 20)
        if not chunk:
            break
        digest.update(chunk)
    return digest.hexdigest()


def _exchange_names(dir_fd: int, left: str, right: str) -> None:
    """Atomically exchange two sibling names or fail without changing either."""
    if _RENAMEAT2 is None:
        raise RunError("OVERWRITE_UNSUPPORTED", "renameat2(RENAME_EXCHANGE) is unavailable")
    ctypes.set_errno(0)
    result = _RENAMEAT2(
        dir_fd,
        os.fsencode(left),
        dir_fd,
        os.fsencode(right),
        _RENAME_EXCHANGE,
    )
    if result == 0:
        return
    number = ctypes.get_errno()
    if number in {errno.ENOSYS, errno.EINVAL, errno.EOPNOTSUPP, errno.EXDEV}:
        raise RunError("OVERWRITE_UNSUPPORTED", os.strerror(number))
    raise RunError("PROMOTION_FAILED", f"atomic exchange: {os.strerror(number)}")


def _hash_named_regular_file(dir_fd: int, name: str, *, context: str) -> str:
    try:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=dir_fd)
    except OSError as error:
        raise RunError("PROMOTION_FAILED", f"{context}: open: {error}") from error
    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise RunError("DESTINATION_NOT_A_FILE", context)
        return _hash_fd(descriptor)
    finally:
        os.close(descriptor)


def _publish_staged_file(
    parent_fd: int,
    stage_name: str,
    destination_name: str,
    source_sha256: str,
    precondition: dict[str, Any],
    *,
    overwrite: bool,
    context: str,
) -> str:
    """Publish one verified sibling stage without losing a raced destination."""
    if overwrite:
        expected = str(precondition.get("sha256") or "")
        if not precondition.get("exists") or not HEX64_RE.fullmatch(expected):
            raise RunError("PRECONDITION_INVALID", context)
        _exchange_names(parent_fd, stage_name, destination_name)
        _fsync_fd(parent_fd, context=context)

        def rollback(code: str) -> None:
            try:
                _exchange_names(parent_fd, stage_name, destination_name)
                _fsync_fd(parent_fd, context=context)
                if _hash_named_regular_file(parent_fd, stage_name, context=context) != source_sha256:
                    raise RunError("OVERWRITE_ROLLBACK_FAILED", f"{context}: stage ownership changed")
                os.unlink(stage_name, dir_fd=parent_fd)
                _fsync_fd(parent_fd, context=context)
            except (OSError, RunError) as error:
                if isinstance(error, RunError) and error.code == "OVERWRITE_ROLLBACK_FAILED":
                    raise
                raise RunError("OVERWRITE_ROLLBACK_FAILED", f"{context}: {error}") from error
            raise RunError(code, context)

        if _hash_named_regular_file(parent_fd, stage_name, context=context) != expected:
            rollback("PRECONDITION_MISMATCH")
        published_hash = _hash_named_regular_file(parent_fd, destination_name, context=context)
        if published_hash != source_sha256:
            rollback("PROMOTION_HASH_MISMATCH")
    else:
        try:
            os.link(stage_name, destination_name, src_dir_fd=parent_fd, dst_dir_fd=parent_fd)
        except FileExistsError as error:
            raise RunError("DESTINATION_EXISTS", context) from error
        except OSError as error:
            raise RunError("PROMOTION_FAILED", f"{context}: {error}") from error
        _fsync_fd(parent_fd, context=context)
        published_hash = _hash_named_regular_file(parent_fd, destination_name, context=context)
        if published_hash != source_sha256:
            if _hash_named_regular_file(parent_fd, stage_name, context=context) == source_sha256:
                try:
                    os.unlink(stage_name, dir_fd=parent_fd)
                    _fsync_fd(parent_fd, context=context)
                except OSError as error:
                    raise RunError("STAGING_CLEANUP_FAILED", f"{context}: {error}") from error
            raise RunError("PROMOTION_HASH_MISMATCH", context)
    try:
        os.unlink(stage_name, dir_fd=parent_fd)
    except OSError as error:
        raise RunError("STAGING_CLEANUP_FAILED", f"{context}: {error}") from error
    _fsync_fd(parent_fd, context=context)
    return published_hash
def _open_run_file(run_fd: int, parts: Sequence[str], *, device: int | None = None) -> int:
    """Open a contained run-relative regular file through no-follow opens."""
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise RunError("SOURCE_PATH_INVALID", "/".join(parts))
    current = run_fd
    opened: list[int] = []
    try:
        for part in parts[:-1]:
            current = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
            if device is not None and os.fstat(current).st_dev != device:
                raise RunError("DEVICE_MISMATCH", f"{'/'.join(parts)}: mounted component")
            opened.append(current)
        descriptor = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
        status = os.fstat(descriptor)
        if not stat.S_ISREG(status.st_mode):
            os.close(descriptor)
            raise RunError("SOURCE_NOT_A_FILE", "/".join(parts))
        if device is not None and status.st_dev != device:
            os.close(descriptor)
            raise RunError("DEVICE_MISMATCH", f"{'/'.join(parts)}: mounted source")
        return descriptor
    except OSError as error:
        raise RunError("SOURCE_OPEN_FAILED", f"{'/'.join(parts)}: {error}") from error
    finally:
        for descriptor in opened:
            os.close(descriptor)


def _open_worktree_directory(root: RunRoot, parts: Sequence[str], *, create: bool = False) -> int:
    """Open a worktree-relative directory through no-follow, same-device opens."""
    if any(part in ("", ".", "..") for part in parts):
        raise RunError("DESTINATION_PATH_INVALID", "/".join(parts))
    try:
        current = os.open(root.worktree, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
    except OSError as error:
        raise RunError("WORKTREE_OPEN_FAILED", f"{root.worktree}: {error}") from error
    opened = [current]
    try:
        for part in parts:
            try:
                current = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
            except FileNotFoundError:
                if not create:
                    raise
                os.mkdir(part, 0o755, dir_fd=current)
                current = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
            except NotADirectoryError:
                raise
            component_stat = os.fstat(current)
            if component_stat.st_dev != root.device:
                raise RunError("DEVICE_MISMATCH", f"{'/'.join(parts)}: mounted component")
            if stat.S_IMODE(component_stat.st_mode) & SHARED_FORBIDDEN_MODE:
                raise RunError("DESTINATION_PARENT_UNSAFE", f"{'/'.join(parts)}: group/world-writable")
            opened.append(current)
        descriptor = current
        opened.remove(current)
        return descriptor
    except OSError as error:
        raise RunError("DESTINATION_PARENT_MISSING", f"{'/'.join(parts)}: {error}") from error
    finally:
        for item in opened:
            os.close(item)


def promote_file(
    handle_file: Path,
    source: PurePath,
    destination: Path,
    overwrite: bool = False,
) -> PromotionReceipt:
    """Publish one run file into the worktree with Git evidence; no silent overwrite."""
    source_path = PurePath(source)
    if source_path.is_absolute() or ".." in source_path.parts:
        raise RunError("SOURCE_PATH_INVALID", str(source_path))
    destination_path = Path(destination)
    if destination_path.is_absolute():
        worktree_root = Path(handle_file).expanduser().resolve().parents[3]
        try:
            destination_path = destination_path.resolve().relative_to(worktree_root)
        except ValueError as error:
            raise RunError("DESTINATION_OUTSIDE_WORKTREE", str(destination)) from error
    if not destination_path.parts or ".." in destination_path.parts or destination_path.name in ("", ".", ".."):
        raise RunError("DESTINATION_PATH_INVALID", str(destination_path))
    root, handle_name = _root_for_handle(Path(handle_file))
    with root:
        handle = read_handle(root.handles_fd, handle_name)
        run_id = handle["run_id"]
        run_fd = _open_run(root.runs_fd, run_id)
        parent_fd = -1
        try:
            source_fd = _open_run_file(run_fd, source_path.parts, device=root.device)
            try:
                source_hash = _hash_fd(source_fd)
                parent_fd = _open_worktree_directory(root, destination_path.parent.parts, create=True)
                destination_name = destination_path.name
                try:
                    destination_fd = os.open(
                        destination_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent_fd
                    )
                except FileNotFoundError:
                    precondition = {"exists": False, "sha256": None}
                except OSError:
                    # Exists but is not an openable regular file (e.g. a
                    # symlink): present, unverifiable, and never replaceable.
                    raise RunError("DESTINATION_NOT_A_FILE", str(destination_path))
                else:
                    if not stat.S_ISREG(os.fstat(destination_fd).st_mode):
                        os.close(destination_fd)
                        raise RunError("DESTINATION_NOT_A_FILE", str(destination_path))
                    precondition = {"exists": True, "sha256": _hash_fd(destination_fd)}
                    os.close(destination_fd)
                if precondition["exists"] and not overwrite:
                    raise RunError("DESTINATION_EXISTS", str(destination_path))
                stage_identity: os.stat_result | None = None
                before = capture_git_snapshot(root.worktree, name="promote-before")
                operation_id = _new_operation_id("promote")
                operation = {
                    "schema": 1,
                    "kind": "promotion",
                    "operation_id": operation_id,
                    "run_id": run_id,
                    "state": "planned",
                    "source": str(source_path),
                    "source_sha256": source_hash,
                    "destination": str(destination_path),
                    "destination_precondition": precondition,
                    "overwrite": bool(overwrite),
                    "staging_name": f".kosmic-promote-{operation_id}.tmp",
                    "git_before_sha256": before.sha256,
                    "git_after_sha256": None,
                    "git_before_basis": {"head": before.head, "paths": list(before.paths)},
                    "result": None,
                    "created_at": _format_utc(_now()),
                    "updated_at": _format_utc(_now()),
                }
                _operation_write(root.operations_fd, operation_id, operation)
                _fault("promote-after-planned")
                stage_name = operation["staging_name"]
                try:
                    stage_fd = os.open(
                        stage_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600, dir_fd=parent_fd
                    )
                except OSError as error:
                    raise RunError("PROMOTION_FAILED", f"{destination_path}: stage create: {error}") from error
                try:
                    os.lseek(source_fd, 0, os.SEEK_SET)
                    while True:
                        chunk = os.read(source_fd, 1 << 20)
                        if not chunk:
                            break
                        offset = 0
                        view = memoryview(chunk)
                        while offset < len(chunk):
                            offset += os.write(stage_fd, view[offset:])
                    _fsync_fd(stage_fd, context=stage_name)
                    # Bind the verified stage bytes to their inode while the
                    # descriptor is open; publication re-proves this identity.
                    stage_identity = os.fstat(stage_fd)
                except OSError as error:
                    raise RunError("PROMOTION_FAILED", f"{destination_path}: stage write: {error}") from error
                finally:
                    os.close(stage_fd)
                try:
                    stage_read_fd = os.open(stage_name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent_fd)
                except OSError as error:
                    raise RunError("PROMOTION_FAILED", f"{destination_path}: stage read: {error}") from error
                try:
                    stage_hash = _hash_fd(stage_read_fd)
                finally:
                    os.close(stage_read_fd)
                if stage_hash != source_hash:
                    _discard_tree(parent_fd, stage_name)
                    raise RunError("PROMOTION_HASH_MISMATCH", f"stage {stage_name}")
                operation = {**operation, "state": "staged", "updated_at": _format_utc(_now())}
                _operation_write(root.operations_fd, operation_id, operation)
                _fault("promote-after-staged")
                try:
                    current_stage = os.stat(stage_name, dir_fd=parent_fd, follow_symlinks=False)
                    if stage_identity is None or (current_stage.st_dev, current_stage.st_ino) != (
                        stage_identity.st_dev,
                        stage_identity.st_ino,
                    ):
                        _discard_tree(parent_fd, stage_name)
                        raise RunError("STAGE_SWAPPED", f"stage {stage_name}")
                    destination_hash = _publish_staged_file(
                        parent_fd,
                        stage_name,
                        destination_name,
                        source_hash,
                        precondition,
                        overwrite=overwrite,
                        context=str(destination_path),
                    )
                except RunError:
                    raise
                except OSError as error:
                    raise RunError("PROMOTION_FAILED", f"{destination_path}: {error}") from error
                operation = {**operation, "state": "published", "updated_at": _format_utc(_now())}
                _operation_write(root.operations_fd, operation_id, operation)
                _fault("promote-after-published")
                after = capture_git_snapshot(root.worktree, name="promote-after")
                promotion_delta = git_delta(before, after)
                _history_append(root, {
                    "schema": 1,
                    "kind": "promotion",
                    "ts": _format_utc(_now()),
                    "run_id": run_id,
                    "operation_id": operation_id,
                    "source": str(source_path),
                    "source_sha256": source_hash,
                    "destination": str(destination_path),
                    "destination_sha256": destination_hash,
                    "overwrite": bool(overwrite),
                    "git_before_sha256": before.sha256,
                    "git_after_sha256": after.sha256,
                    "git_delta": promotion_delta,
                    "result": "published",
                })
                operation = {
                    **operation,
                    "state": "recorded",
                    "result": "published",
                    "destination_sha256": destination_hash,
                    "git_after_sha256": after.sha256,
                    "git_before_head": before.head,
                    "git_after_head": after.head,
                    "git_delta": promotion_delta,
                    "updated_at": _format_utc(_now()),
                }
                _operation_write(root.operations_fd, operation_id, operation)
                _fault("promote-after-history")
                if handle["kind"] == "receipt":
                    updated = {**handle, "promotions": [*handle.get("promotions", []), operation_id]}
                    _write_handle(root.handles_fd, handle_name, updated)
                return PromotionReceipt(
                    run_id=run_id,
                    source_sha256=source_hash,
                    destination=root.worktree / destination_path,
                    destination_sha256=destination_hash,
                    git_before_sha256=before.sha256,
                    git_after_sha256=after.sha256,
                    code="OK",
                )
            finally:
                os.close(source_fd)
        finally:
            if parent_fd >= 0:
                os.close(parent_fd)
            os.close(run_fd)


# --- Complete reporting (AD-MRW12) ------------------------------------------


REPORT_CATEGORIES = ("active", "retained", "expired", "abandoned", "oversized", "malformed", "unattributed")
KOSMIC_ROOT_ENTRIES = frozenset({"runs", "quarantine", "operations", "handles", HISTORY_FILENAME})


def _classify_run_entry(
    root: RunRoot,
    name: str,
    manifest: dict[str, Any],
    usage: int,
    moment: datetime,
) -> RunEntry:
    state = manifest["state"]
    flags: list[str] = []
    reason: str | None = None
    expires: datetime | None = None
    if manifest["expires_at"]:
        expires = _parse_utc(manifest["expires_at"], "expires_at")
    held = _lock_held_for_run(root, name)
    if state == "creating":
        category = "malformed"
        reason = "STUCK_CREATING"
    elif state == "active":
        if held:
            category = "active"
        else:
            category = "abandoned"
            flags.append("abandoned-candidate")
            grace_until = _parse_utc(manifest["lease_expires_at"], "lease") + UNLOCK_GRACE
            if moment < grace_until:
                flags.append("in-grace")
            else:
                flags.append("grace-elapsed")
                reason = "abandoned-candidate-past-grace"
                flags.append("selected")
    elif state == "finalizing":
        if held:
            category = "active"
            flags.append("finalizing")
        else:
            category = "retained"
            reason = "interrupted-finalization"
            flags.append("recovery")
    elif state == "abandoned":
        category = "abandoned"
        flags.append("selected")
        reason = "abandoned-expired"
    else:
        if _cleanup_eligible(manifest, moment):
            category = "expired"
            reason = (
                "cleanup-eligible"
                if state == "succeeded" or manifest["retention"] == "disposable"
                else "retention-expired"
            )
            flags.append("selected")
        else:
            category = "retained"
    if usage > PER_RUN_WARN_BYTES and category not in ("malformed", "unattributed"):
        flags.append(category)
        flags.append("oversized")
        category = "oversized"
    return RunEntry(
        run_id=name,
        category=category,
        state=state,
        path=Path("runs") / name,
        bytes=usage,
        expires_at=expires,
        report_only_reason=reason,
        flags=tuple(flags),
    )


def _lock_held_for_run(root: RunRoot, name: str) -> bool:
    run_fd = _open_run(root.runs_fd, name)
    try:
        return _lock_held(run_fd, run_id=name)
    finally:
        os.close(run_fd)


def _entry_tree_bytes(dir_fd: int, name: str, device: int) -> int:
    """Bounded byte accounting for an arbitrary immediate child, 0 when unsafe."""
    try:
        status = os.stat(name, dir_fd=dir_fd, follow_symlinks=False)
    except OSError:
        return 0
    if stat.S_ISREG(status.st_mode):
        return status.st_size
    if not stat.S_ISDIR(status.st_mode) or stat.S_ISLNK(status.st_mode) or status.st_dev != device:
        return 0
    try:
        descriptor = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=dir_fd)
    except OSError:
        return 0
    try:
        usage, _complete = _tree_bytes(descriptor, device=device)
        return usage
    finally:
        os.close(descriptor)


def _entry_bytes_at(dir_fd: int, name: str) -> int:
    try:
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=dir_fd)
    except OSError:
        return 0
    try:
        return os.fstat(descriptor).st_size
    finally:
        os.close(descriptor)


def report_runs(worktree: Path, action: str = "status", run_id: str | None = None) -> RunReport:
    """Classify every managed or unattributed entry with byte accounting."""
    if action not in ("status", "gc-dry-run", "gc-apply"):
        raise RunError("ACTION_INVALID", repr(action))
    if action == "gc-apply":
        if run_id is not None:
            raise RunError("GC_FILTER_UNSUPPORTED", run_id)
        return collect_runs(worktree, action="gc-apply")
    entries: list[RunEntry] = []
    partial = False
    moment = _now()
    with resolve_run_root(Path(worktree)) as root:
        run_names = sorted(os.listdir(root.runs_fd))
        for name in run_names:
            manifest, reason = _static_run_classification(root.runs_fd, name)
            if manifest is None:
                usage = _entry_tree_bytes(root.runs_fd, name, root.device)
                if usage:
                    partial = True
                if reason == "UNATTRIBUTED_NAME":
                    entries.append(RunEntry(name, "unattributed", None, Path("runs") / name, usage, None, "unattributed-runs-child"))
                else:
                    entries.append(RunEntry(name, "malformed", None, Path("runs") / name, usage, None, reason))
                continue
            try:
                run_fd = _open_run(root.runs_fd, name)
            except RunError:
                entries.append(RunEntry(name, "malformed", None, Path("runs") / name, 0, None, "RUN_UNTRUSTED"))
                continue
            try:
                usage, complete = _tree_bytes(run_fd, device=root.device)
            finally:
                os.close(run_fd)
            partial = partial or not complete
            entries.append(_classify_run_entry(root, name, manifest, usage, moment))
        for name in sorted(os.listdir(root.operations_fd)):
            if not name.endswith(".json") or not OPERATION_NAME_RE.fullmatch(name[: -len(".json")]):
                entries.append(RunEntry(None, "unattributed", None, Path("operations") / name, _entry_bytes_at(root.operations_fd, name), None, "unattributed-operation-name"))
                continue
            try:
                operation = _read_json_bounded(root.operations_fd, name, limit=1 << 20, context=f"operations/{name}")
            except RunError:
                entries.append(RunEntry(None, "malformed", None, Path("operations") / name, _entry_bytes_at(root.operations_fd, name), None, "RECORD_MALFORMED"))
                continue
            state = str(operation.get("state") or "")
            if state != "recorded":
                entries.append(RunEntry(operation.get("run_id"), "retained", state, Path("operations") / name, _entry_bytes_at(root.operations_fd, name), None, "operation-recovery-pending", ("recovery",)))
            else:
                entries.append(RunEntry(operation.get("run_id"), "retained", state, Path("operations") / name, _entry_bytes_at(root.operations_fd, name), None, "promotion-record"))
        for name in sorted(os.listdir(root.quarantine_fd)):
            entries.append(RunEntry(None, "retained", None, Path("quarantine") / name, _entry_tree_bytes(root.quarantine_fd, name, root.device), None, "quarantine-remnant", ("recovery",)))
        known_runs = set(run_names)
        for name in sorted(os.listdir(root.handles_fd)):
            if not HANDLE_NAME_RE.fullmatch(name):
                entries.append(RunEntry(None, "unattributed", None, Path("handles") / name, _entry_bytes_at(root.handles_fd, name), None, "unattributed-handle-name"))
                continue
            try:
                handle = read_handle(root.handles_fd, name)
            except RunError:
                entries.append(RunEntry(None, "malformed", None, Path("handles") / name, _entry_bytes_at(root.handles_fd, name), None, "HANDLE_INVALID"))
                continue
            if handle["kind"] == "handle":
                if handle["run_id"] not in known_runs:
                    entries.append(RunEntry(handle["run_id"], "malformed", None, Path("handles") / name, _entry_bytes_at(root.handles_fd, name), None, "orphan-handle"))
                continue
            receipt_expiry = _parse_utc(handle["receipt_expires_at"], "receipt") if handle.get("receipt_expires_at") else None
            if receipt_expiry is not None and moment >= receipt_expiry:
                entries.append(RunEntry(handle["run_id"], "expired", handle["outcome"], Path("handles") / name, _entry_bytes_at(root.handles_fd, name), receipt_expiry, "receipt-expired"))
            else:
                entries.append(RunEntry(handle["run_id"], "retained", handle["outcome"], Path("handles") / name, _entry_bytes_at(root.handles_fd, name), receipt_expiry, "terminal-receipt"))
        for name in sorted(os.listdir(root.kosmic_fd)):
            if name not in KOSMIC_ROOT_ENTRIES:
                entries.append(RunEntry(None, "unattributed", None, Path(name), _entry_tree_bytes(root.kosmic_fd, name, root.device), None, "unattributed-kosmic-child"))
        history_bytes = _entry_bytes_at(root.kosmic_fd, HISTORY_FILENAME)
        if run_id is not None:
            entries = [entry for entry in entries if entry.run_id == run_id]
            if not any(entry.path == Path("runs") / run_id for entry in entries):
                raise RunError("RUN_UNKNOWN", run_id)
        counts = {category: 0 for category in REPORT_CATEGORIES}
        for entry in entries:
            counts[entry.category] = counts.get(entry.category, 0) + 1
        total_bytes = sum(entry.bytes for entry in entries) + (0 if run_id is not None else history_bytes)
        selected_bytes = sum(entry.bytes for entry in entries if "selected" in entry.flags)
        return RunReport(
            entries=tuple(entries[:REPORT_ENTRY_LIMIT]),
            counts=MappingProxyType(counts),
            total_bytes=total_bytes,
            selected_bytes=selected_bytes,
            action=action,
            code="PARTIAL" if partial or len(entries) > REPORT_ENTRY_LIMIT else "OK",
        )


def _find_run_handle(root: RunRoot, run_id: str) -> tuple[str, dict[str, Any]] | None:
    for name in sorted(os.listdir(root.handles_fd)):
        if not HANDLE_NAME_RE.fullmatch(name):
            continue
        try:
            handle = read_handle(root.handles_fd, name)
        except RunError:
            continue
        if handle.get("run_id") == run_id:
            return name, handle
    return None


def _abandon_expired_active_run(
    root: RunRoot,
    run_fd: int,
    manifest: dict[str, Any],
    handle_name: str,
    handle: dict[str, Any],
) -> dict[str, Any]:
    moment = _now()
    grace_until = _parse_utc(manifest["lease_expires_at"], "lease") + UNLOCK_GRACE
    if moment < grace_until:
        raise RunError("CLEANUP_NOT_ELIGIBLE", manifest["run_id"])
    finish = capture_git_snapshot(root.worktree, name=f"abandon-{manifest['run_id']}")
    try:
        git_fd = os.open("git", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=run_fd)
    except OSError as error:
        raise RunError("GIT_CAPTURE_FAILED", f"{manifest['run_id']}: {error}") from error
    try:
        _atomic_replace_bytes(
            git_fd,
            "finish-status.porcelain-v2",
            finish.raw,
            context=f"{manifest['run_id']}/git/finish-status.porcelain-v2",
        )
        start_raw = _read_bounded(
            git_fd,
            "start-status.porcelain-v2",
            limit=64 << 20,
            context=f"{manifest['run_id']}/git/start",
        )
        start_snapshot = _snapshot_from_raw(start_raw, source=f"{manifest['run_id']}/git/start")
        _atomic_replace_bytes(
            git_fd,
            "delta.json",
            _json_bytes(git_delta(start_snapshot, finish)),
            context=f"{manifest['run_id']}/git/delta",
        )
    finally:
        os.close(git_fd)
    finished_at = _format_utc(moment)
    manifest = _transition_manifest(
        run_fd,
        manifest,
        state="abandoned",
        finished_at=finished_at,
        expires_at=finished_at,
        holder_pid=0,
        git_finish_sha256=finish.sha256,
        git_finish_head=finish.head,
        git_finish_branch=finish.branch,
        snapshot_complete=True,
        abandoned_reason="lease-expired-after-grace",
    )
    _publish_receipt_with_promotions(root, root.handles_fd, handle_name, manifest["run_id"], handle, manifest)
    return manifest


def collect_runs(
    worktree: Path,
    *,
    action: str = "gc-apply",
    max_entries: int | None = None,
    max_bytes: int | None = None,
) -> RunReport:
    """Apply the sole cleanup transaction to dry-run-selected immediate children."""
    if not GC_APPLY_ENABLED:
        raise RunError("GC_APPLY_DISABLED", "general gc --apply is not activated in this release")
    if action not in ("gc-apply", "startup-gc"):
        raise RunError("ACTION_INVALID", action)
    if max_entries is not None and max_entries < 1:
        raise RunError("GC_BOUND_INVALID", "max_entries must be positive")
    if max_bytes is not None and max_bytes < 1:
        raise RunError("GC_BOUND_INVALID", "max_bytes must be positive")

    recovery = recover_cleanup_operations(worktree, recover_promotions=False)
    diagnostics = [item for item in recovery if item.get("result") not in ("removed", "recorded-leftover-removed", "deferred")]
    operations = [item for item in recovery if item.get("result") == "removed"]
    dry_run = report_runs(worktree, action="gc-dry-run")
    candidates = [
        entry
        for entry in dry_run.entries
        if entry.run_id is not None and entry.path.parent == Path("runs") and "selected" in entry.flags
    ]
    selected_bytes = 0
    selected_count = 0
    with resolve_run_root(Path(worktree)) as root:
        for entry in candidates:
            if max_entries is not None and selected_count >= max_entries:
                continue
            if max_bytes is not None and selected_bytes + entry.bytes > max_bytes:
                continue
            selected_count += 1
            selected_bytes += entry.bytes
            run_id = str(entry.run_id)
            if not _exists_fd(root.runs_fd, run_id):
                continue
            run_fd = -1
            lock_fd = -1
            try:
                run_fd = _open_run(root.runs_fd, run_id)
                lock_fd, acquired = _open_lock_nb(run_fd, run_id=run_id)
                if not acquired:
                    diagnostics.append({"run_id": run_id, "result": "report-only", "reason": "RUN_ACTIVE"})
                    continue
                manifest = load_manifest(run_fd, run_id=run_id)
                handle_record = _find_run_handle(root, run_id)
                if handle_record is None:
                    diagnostics.append({"run_id": run_id, "result": "report-only", "reason": "HANDLE_MISSING"})
                    continue
                handle_name, handle = handle_record
                if manifest["state"] == "active":
                    manifest = _abandon_expired_active_run(root, run_fd, manifest, handle_name, handle)
                if not _cleanup_eligible(manifest, _now()):
                    diagnostics.append({"run_id": run_id, "result": "report-only", "reason": "CLEANUP_NOT_ELIGIBLE"})
                    continue
                result = _execute_cleanup_transaction(
                    root,
                    run_id,
                    manifest,
                    held_lock_fd=lock_fd,
                )
                _update_receipt_cleanup(root.handles_fd, handle_name, "removed", "OK")
                operations.append(result)
            except RunError as error:
                if _exists_fd(root.runs_fd, run_id):
                    diagnostics.append({"run_id": run_id, "result": "report-only", "reason": error.code})
            finally:
                if lock_fd >= 0:
                    os.close(lock_fd)
                if run_fd >= 0:
                    os.close(run_fd)

    after = report_runs(worktree, action="gc-dry-run")
    remaining = [
        entry
        for entry in after.entries
        if entry.run_id is not None and entry.path.parent == Path("runs") and "selected" in entry.flags
    ]
    return RunReport(
        entries=after.entries,
        counts=after.counts,
        total_bytes=after.total_bytes,
        selected_bytes=selected_bytes,
        action=action,
        code="PARTIAL" if diagnostics or after.code != "OK" else "OK",
        operations=tuple(operations),
        diagnostics=tuple(diagnostics),
        remaining_eligible=len(remaining),
        remaining_bytes=sum(entry.bytes for entry in remaining),
    )


def startup_collect(
    worktree: Path,
    *,
    max_entries: int = STARTUP_GC_MAX_ENTRIES,
    max_bytes: int = STARTUP_GC_MAX_BYTES,
) -> RunReport:
    """Run one bounded startup maintenance pass through explicit GC authority."""
    if not STARTUP_GC_ENABLED:
        raise RunError("STARTUP_GC_DISABLED", "startup collection is not activated in this release")
    return collect_runs(
        worktree,
        action="startup-gc",
        max_entries=max_entries,
        max_bytes=max_bytes,
    )
def report_to_json(report: RunReport) -> dict[str, Any]:
    return {
        "code": report.code,
        "action": report.action,
        "operations": list(report.operations),
        "diagnostics": list(report.diagnostics),
        "remaining_eligible": report.remaining_eligible,
        "remaining_bytes": report.remaining_bytes,
        "counts": dict(report.counts),
        "total_bytes": report.total_bytes,
        "selected_bytes": report.selected_bytes,
        "warn_thresholds": {"per_run_bytes": PER_RUN_WARN_BYTES, "aggregate_bytes": AGGREGATE_WARN_BYTES},
        "entries": [
            {
                "run_id": entry.run_id,
                "category": entry.category,
                "state": entry.state,
                "path": entry.path.as_posix(),
                "bytes": entry.bytes,
                "expires_at": _format_utc(entry.expires_at) if entry.expires_at else None,
                "report_only_reason": entry.report_only_reason,
                "flags": list(entry.flags),
            }
            for entry in report.entries
        ],
    }


def receipt_to_json(receipt: RunReceipt) -> dict[str, Any]:
    return {
        "code": receipt.code,
        "run_id": receipt.run_id,
        "state": receipt.state,
        "path": str(receipt.path) if receipt.path else None,
        "expires_at": _format_utc(receipt.expires_at) if receipt.expires_at else None,
        "git_start_sha256": receipt.git_start_sha256,
        "git_finish_sha256": receipt.git_finish_sha256,
    }


def promotion_to_json(receipt: PromotionReceipt) -> dict[str, Any]:
    return {
        "code": receipt.code,
        "run_id": receipt.run_id,
        "source_sha256": receipt.source_sha256,
        "destination": str(receipt.destination),
        "destination_sha256": receipt.destination_sha256,
        "git_before_sha256": receipt.git_before_sha256,
        "git_after_sha256": receipt.git_after_sha256,
    }
