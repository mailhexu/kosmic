"""Authoritative Project/Subproject specification identity and ownership."""
from __future__ import annotations

import contextlib
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field, replace
import errno
import fcntl
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import unicodedata
import urllib.parse
import uuid
from types import MappingProxyType
from typing import Any
import hashlib

try:
    from .kosmic_shared_library import Document, LibraryError, parse_document_text
except ImportError:
    from kosmic_shared_library import Document, LibraryError, parse_document_text

SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")


class SpecError(RuntimeError):
    def __init__(self, code: str, detail: str = "") -> None:
        self.code = code
        self.detail = detail
        remedies = {
            "OWNER_REQUIRED": "Provide Project/subproject/kind/local-id or an explicit owner and kind.",
            "REFERENCE_AMBIGUOUS": "Specify the kind or use the fully qualified record identity.",
            "OWNER_MISMATCH": "Resolve the owning Project and subproject; correct owner metadata or use that explicit scope.",
            "SCOPE_DENIED": "Use a regular file inside the owning Project without symlink or traversal escapes.",
            "LOCAL_ID_INVALID": "Make local_id agree with its numeric specification filename before allocating another record.",
            "ANCESTRY_INVALID": "Repair owner-local parent links and their declared ancestor chain.",
            "DEPENDENCY_INVALID": "Resolve local dependencies and declare foreign dependencies by qualified identity.",
            "DEPENDENCY_CYCLE": "Remove the circular dependency before continuing work.",
            "RECORD_NOT_FOUND": "Check the canonical record path and qualified Project/owner identity.",
            "MIGRATION_REQUIRED": "Create and approve a flat-spec migration plan before using the subproject catalog.",
            "RESUME_REQUIRED": "Pass the explicit operation_id recorded at reservation; titles never select a reservation.",
            "OPERATION_NOT_FOUND": "Use the exact operation identifier returned when the reservation was created.",
            "WORK_HANDLE_REQUIRED": "Derived planning records need an explicit work handle from the governing session.",
            "RESERVATION_CONFLICT": "The target already holds different content; resume with the owning operation instead of overwriting.",
            "SHARED_ROOT_INVALID": "Keep notes/, mathdocs/, and skills/ only at the Project root; remove the subproject-local knowledge copy.",
            "WRITE_SCOPE_DENIED": "Write only inside the declared owner scope; cross-subproject and shared-root writes need Project authority or a reviewed scope expansion.",
            "ASSIGNMENT_INVALID": "Assign every ambiguous record to an explicit migrated PRD source path from the legacy inventory.",
            "MIGRATION_LINK_INVALID": "Regenerate the plan against the current snapshot; a mapped live link does not resolve in the staged view.",
            "MIGRATION_STATUS_INVALID": "Repair or remove the ProjectEntry status_root binding; planning never invents, replaces or silently drops a configured binding.",
            "FULL_CATALOG_REQUIRED": "Run the audit against the complete Project catalog; a record-bound view never authorizes a whole-Project audit.",
        }
        self.remediation = remedies.get(code, "Correct the specification identity or metadata and validate the Project again.")
        message = f"{code}: {detail}" if detail else code
        super().__init__(f"{message}. {self.remediation}")


def read_document(root: Path, path: Path) -> Document:
    """Read a regular UTF-8 file through retained, no-follow directory descriptors."""
    root = root.resolve()
    absolute = Path(os.path.abspath(path))
    try:
        parts = absolute.relative_to(root).parts
    except ValueError as error:
        raise SpecError("SCOPE_DENIED", str(path)) from error
    if not parts:
        raise SpecError("SCOPE_DENIED", str(path))
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = next_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=descriptor)
        try:
            if not stat.S_ISREG(os.fstat(file_fd).st_mode):
                raise SpecError("SCOPE_DENIED", str(path))
            with os.fdopen(file_fd, "r", encoding="utf-8") as stream:
                file_fd = -1
                text = stream.read()
        finally:
            if file_fd >= 0:
                os.close(file_fd)
    except OSError as error:
        raise SpecError("SCOPE_DENIED", f"{path}: {error.strerror}") from error
    finally:
        os.close(descriptor)
    try:
        return parse_document_text(text, absolute)
    except LibraryError as error:
        raise SpecError("SPEC_INVALID", str(error)) from error


@dataclass(frozen=True)
class SpecRef:
    project_id: str
    subproject_id: str | None
    kind: str
    local_id: str
    path: Path
    metadata: Mapping[str, Any]
    title: str
    receipt_pending: bool = False

    @property
    def qualified_id(self) -> str:
        owner = f"/{self.subproject_id}" if self.subproject_id is not None else ""
        return f"{self.project_id}{owner}/{self.kind}/{self.local_id}"

    @property
    def status(self) -> str:
        return str(self.metadata.get("status", ""))
    @property
    def effective_status(self) -> str:
        return "pending" if self.receipt_pending else self.status


def bounded_record_owner(root: Path, project_id: str, reference: str) -> str | None:
    """Owner subproject named by a record reference, without enumeration.

    Qualified identities (``project/owner/kind/local-id``) carry the owner in
    their second segment; path references carry it in their
    ``subprojects/<owner>/specs`` prefix. Every other form resolves against
    the shared records only. The result is a slug or None; it is a syntactic
    answer — existence and validity of the owner stay with the catalog.
    """
    root = Path(root).expanduser().resolve()
    text = str(reference).strip()
    pieces = text.split("/")
    if len(pieces) in (3, 4) and pieces[0] == project_id:
        owner = pieces[1] if len(pieces) == 4 else None
        return owner if owner is not None and SLUG.fullmatch(owner) else None
    path = Path(text)
    if path.is_absolute():
        normalized = Path(os.path.abspath(path))
    elif text.startswith(("specs/", "subprojects/")):
        normalized = Path(os.path.abspath(root / path))
    else:
        return None
    try:
        relative = normalized.relative_to(root)
    except ValueError:
        return None
    parts = relative.parts
    if (len(parts) >= 4 and parts[0] == "subprojects" and parts[2] == "specs"
            and SLUG.fullmatch(parts[1])):
        return parts[1]
    return None


@dataclass(frozen=True)
class _SpecStructure:
    """Claimed-facts structural inventory: identity, owner, claimed lifecycle.

    The shared private discovery behind :class:`SpecCatalog` construction and
    read-only history reporting. The scan is no-follow and fail-closed and
    never settles receipts or reads retrospective proof; history reporting
    resolves its configured subjects against a structure before any
    retrospective reader runs. Not an operational catalog.
    """

    root: Path
    project_id: str
    subprojects: Mapping[str, Mapping[str, Any]]
    records: tuple[SpecRef, ...]
    by_path: Mapping[Path, SpecRef]


#: Bounded scope sentinel: collect the shared records only, matching
#: ``SpecCatalog.bounded(root, None)``. Private to structural discovery.
_SHARED_ONLY = object()


def _scan_spec_records(root: Path, project_id: str, specs: Path, owner: str | None,
                       records: dict[str, SpecRef], paths: dict[Path, SpecRef]) -> None:
    """No-follow scan of one specs directory into the identity/path maps."""
    if specs.is_symlink():
        raise SpecError("SCOPE_DENIED", str(specs))
    patterns = [("quick-task", "quick-tasks/*.md"), ("proposal", "skill-proposals/*.md")]
    if owner is not None:
        patterns += [("prd", "prd.md"), ("architecture", "architecture.md"),
                     ("epic", "epics/epic-*.md"), ("story", "stories/story-*.md"),
                     ("research", "research/*.md")]
    for kind, pattern in patterns:
        for path in sorted(specs.glob(pattern)):
            doc = read_document(root, path)
            meta = doc.metadata
            if owner is None and meta.get("subproject_id") == "null":
                meta["subproject_id"] = None
            if ("subproject_id" not in meta or meta.get("project_id") != project_id
                    or meta.get("subproject_id") != owner or meta.get("record_kind") != kind):
                raise SpecError("OWNER_MISMATCH", str(path))
            local_id = meta.get("local_id")
            if not isinstance(local_id, str) or not SLUG.fullmatch(local_id):
                raise SpecError("LOCAL_ID_INVALID", str(path))
            if kind in {"epic", "story"}:
                number = re.match(rf"{kind}-([0-9]+)(?:-[a-z0-9]+(?:-[a-z0-9]+)*)?\.md\Z", path.name)
                if number is None or number.group(1) != local_id:
                    raise SpecError("LOCAL_ID_INVALID", f"{path}: filename disagrees with local_id")
            title = next((line[2:].strip() for line in doc.body.splitlines() if line.startswith("# ")), path.stem)
            immutable = MappingProxyType({key: tuple(value) if isinstance(value, list) else value
                                          for key, value in meta.items()})
            ref = SpecRef(project_id, owner, kind, local_id, path, immutable, title)
            if ref.qualified_id in records:
                raise SpecError("DUPLICATE_RECORD", ref.qualified_id)
            records[ref.qualified_id] = ref
            paths[path] = ref


def _scan_shared_records(root: Path, project_id: str,
                         records: dict[str, SpecRef], paths: dict[Path, SpecRef]) -> None:
    """Shared-records scan; flat feature specifications still require migration."""
    specs = root / "specs"
    if specs.is_symlink():
        raise SpecError("SCOPE_DENIED", str(specs))
    if not specs.exists():
        return
    active = list(specs.glob("prd*.md")) + list(specs.glob("architecture*.md"))
    for name in ("epics", "stories", "research"):
        active.extend((specs / name).glob("*.md"))
    if active:
        raise SpecError("MIGRATION_REQUIRED", "flat feature specifications need an approved migration plan")
    _scan_spec_records(root, project_id, specs, None, records, paths)


def _collect_spec_structure(project_root: Path, owner_scope: Any = None) -> _SpecStructure:
    """Shared private structural discovery (ADR-002); never settles receipts.

    ``owner_scope=None`` collects the whole Project exactly like
    ``SpecCatalog`` construction; an owner slug collects the shared records
    plus that owner's subtree; the private ``_SHARED_ONLY`` sentinel
    collects the shared records only, matching
    ``SpecCatalog.bounded(root, None)``. Scan order and errors match the
    constructors exactly. The result is a claimed-facts inventory for
    reporting callers, not an operational catalog.
    """
    root = Path(project_root).expanduser().resolve()
    entry = read_document(root, root / "ProjectEntry.md")
    project_id = str(entry.metadata.get("project_id", ""))
    if not SLUG.fullmatch(project_id):
        raise SpecError("PROJECT_ID_INVALID", str(root))
    subprojects: dict[str, dict[str, Any]] = {}
    records: dict[str, SpecRef] = {}
    paths: dict[Path, SpecRef] = {}
    _scan_shared_records(root, project_id, records, paths)
    if owner_scope is None:
        directory = root / "subprojects"
        if directory.is_symlink():
            raise SpecError("SCOPE_DENIED", str(directory))
        if directory.exists():
            for base in sorted(directory.iterdir()):
                if base.is_symlink() or not base.is_dir() or not SLUG.fullmatch(base.name):
                    raise SpecError("OWNER_MISMATCH", str(base))
                doc = read_document(root, base / "SubprojectEntry.md")
                meta = doc.metadata
                if (meta.get("schema") != "kosmic.subproject/1"
                        or meta.get("project_id") != project_id
                        or meta.get("subproject_id") != base.name):
                    raise SpecError("OWNER_MISMATCH", str(base / "SubprojectEntry.md"))
                subprojects[base.name] = meta
                _scan_spec_records(root, project_id, base / "specs", base.name, records, paths)
    elif owner_scope is not _SHARED_ONLY:
        if not SLUG.fullmatch(str(owner_scope)):
            raise SpecError("OWNER_MISMATCH", str(owner_scope))
        base = root / "subprojects" / str(owner_scope)
        if base.is_symlink():
            raise SpecError("SCOPE_DENIED", str(base))
        if base.is_dir():
            doc = read_document(root, base / "SubprojectEntry.md")
            meta = doc.metadata
            if (meta.get("schema") != "kosmic.subproject/1"
                    or meta.get("project_id") != project_id
                    or meta.get("subproject_id") != str(owner_scope)):
                raise SpecError("OWNER_MISMATCH", str(base / "SubprojectEntry.md"))
            subprojects[str(owner_scope)] = meta
            _scan_spec_records(root, project_id, base / "specs", str(owner_scope), records, paths)
        elif base.exists():
            raise SpecError("OWNER_MISMATCH", str(base))
        # A missing owner directory yields an empty owned set; resolution
        # then reports RECORD_NOT_FOUND exactly like the full catalog.
    return _SpecStructure(
        root=root,
        project_id=project_id,
        subprojects=MappingProxyType(subprojects),
        records=tuple(sorted(records.values(), key=lambda item: item.path.as_posix())),
        by_path=MappingProxyType(paths),
    )


class SpecCatalog:
    """One deterministic inventory; local references never infer a foreign owner."""
    def __init__(self, project_root: Path) -> None:
        self._adopt_structure(
            _collect_spec_structure(project_root), bounded=False, bounded_owner=None)
        self._settle_receipts()

    @classmethod
    def bounded(cls, project_root: Path, owner: str | None) -> "SpecCatalog":
        """Record-bound catalog: one owner's subtree plus the shared records.

        Contains the ProjectEntry, the owner SubprojectEntry (when owned), the
        owner-local record tree, and the shared records. Unrelated subprojects
        are never enumerated, so their defects cannot surface here; the
        referenced owner's own read or identity errors still propagate. Every
        other invariant is the catalog's own: immutable project_id checks,
        no-follow reads, duplicate detection, canonical path/local-id
        consistency, ancestry chains, and receipt-aware effective status.
        Full-catalog audits must use the regular constructor.
        """
        catalog = cls.__new__(cls)
        catalog._adopt_structure(
            _collect_spec_structure(
                project_root, _SHARED_ONLY if owner is None else owner),
            bounded=True, bounded_owner=owner)
        catalog._settle_receipts()
        return catalog

    @classmethod
    def bounded_for_reference(cls, project_root: Path, reference: str) -> "SpecCatalog":
        """Record-bound catalog for one work-record reference.

        The owner subproject comes from the reference itself: the second
        segment of a qualified identity, or the ``subprojects/<owner>/specs``
        prefix of a path reference. Path-less bare local ids resolve against
        the shared records only; owned records need a qualified or path
        reference because the bounded view never enumerates subprojects.
        """
        root = Path(project_root).expanduser().resolve()
        entry = read_document(root, root / "ProjectEntry.md")
        project_id = str(entry.metadata.get("project_id", ""))
        return cls.bounded(root, bounded_record_owner(root, project_id, str(reference)))

    def _adopt_structure(self, structure: _SpecStructure, *, bounded: bool,
                         bounded_owner: str | None) -> None:
        """Adopt a structural inventory as this catalog's immutable content."""
        self.root = structure.root
        #: Whole-Project inventory; record-bound views set ``bounded`` instead.
        self.bounded = bounded
        self.bounded_owner: str | None = bounded_owner
        self.project_id = structure.project_id
        self.subprojects: dict[str, dict[str, Any]] = dict(structure.subprojects)
        self._records: dict[str, SpecRef] = {ref.qualified_id: ref for ref in structure.records}
        self._paths: dict[Path, SpecRef] = dict(structure.by_path)
        self.records = structure.records

    def _settle_receipts(self) -> None:
        """Mark unreceipted done records pending; shared by both constructors."""
        try:
            from .kosmic_dreams import pending_terminal_receipts
        except ImportError:
            from kosmic_dreams import pending_terminal_receipts
        pending = pending_terminal_receipts(
            self.root,
            ((record.qualified_id, record.status) for record in self.records),
            catalog=self,
        )
        if pending:
            self._records = {
                identity: replace(record, receipt_pending=identity in pending)
                for identity, record in self._records.items()
            }
            self._paths = {record.path: record for record in self._records.values()}
        self.records = tuple(sorted(self._records.values(), key=lambda item: item.path.as_posix()))

    def resolve(self, reference: str | Path, *, owner: str | None = None, kind: str | None = None) -> SpecRef:
        if owner is not None and owner not in self.subprojects:
            raise SpecError("OWNER_MISMATCH", owner)
        text = str(reference)
        pieces = text.split("/")
        ref = None
        if len(pieces) in (3, 4) and pieces[0] == self.project_id:
            ref = self._records.get(text)
        elif isinstance(reference, Path) or "/" in text or text.endswith(".md"):
            path = Path(reference)
            if not path.is_absolute():
                if text.startswith(("specs/", "subprojects/")):
                    path = self.root / path
                else:
                    base = self.root / "subprojects" / owner / "specs" if owner else self.root / "specs"
                    path = base / path
            normalized = Path(os.path.abspath(path))
            read_document(self.root, normalized)
            ref = self._paths.get(normalized)
        else:
            matching = [item for item in self.records if item.local_id == text
                        and (kind is None or item.kind == kind)]
            candidates = [item for item in matching if item.subproject_id == owner]
            if owner is None and not candidates and matching:
                raise SpecError("OWNER_REQUIRED", text)
            if len(candidates) > 1:
                raise SpecError("REFERENCE_AMBIGUOUS", text)
            ref = candidates[0] if candidates else None
        if ref is None:
            raise SpecError("RECORD_NOT_FOUND", text)
        if owner is not None and ref.subproject_id != owner:
            raise SpecError("OWNER_MISMATCH", ref.qualified_id)
        if kind is not None and ref.kind != kind:
            raise SpecError("RECORD_KIND_MISMATCH", ref.qualified_id)
        return ref

    def _parent(self, record: SpecRef, key: str, kind: str) -> SpecRef:
        value = record.metadata.get(key)
        if not isinstance(value, str) or not value:
            raise SpecError("ANCESTRY_INVALID", f"{record.qualified_id}: missing {key}")
        reference = value if value.startswith(self.project_id + "/") else record.path.parent / value
        try:
            parent = self.resolve(reference, owner=record.subproject_id, kind=kind)
        except SpecError as error:
            raise SpecError("ANCESTRY_INVALID", f"{record.qualified_id}: {key}: {error}") from error
        if parent.subproject_id != record.subproject_id:
            raise SpecError("ANCESTRY_INVALID", f"{record.qualified_id}: foreign {key}")
        return parent

    def _checked(self, record: SpecRef) -> SpecRef:
        canonical = self._paths.get(record.path) if isinstance(record, SpecRef) else None
        if canonical is None or canonical != record:
            raise SpecError("OWNER_MISMATCH", "record is not a checked member of this catalog")
        return canonical

    def ancestry(self, record: SpecRef) -> tuple[SpecRef, ...]:
        record = self._checked(record)
        parents = {"story": ("linked_epic", "epic"),
                   "epic": ("linked_architecture", "architecture"),
                   "architecture": ("linked_prd", "prd"),
                   "research": ("linked_prd", "prd")}
        chain: list[SpecRef] = []
        seen = {record.qualified_id}
        current = record
        while current.kind in parents:
            key, kind = parents[current.kind]
            current = self._parent(current, key, kind)
            if current.qualified_id in seen:
                raise SpecError("ANCESTRY_INVALID", f"{record.qualified_id}: cycle")
            seen.add(current.qualified_id)
            chain.append(current)
        for ancestor in chain:
            key = "linked_" + ancestor.kind
            if self._parent(record, key, ancestor.kind) != ancestor:
                raise SpecError("ANCESTRY_INVALID", f"{record.qualified_id}: inconsistent {key}")
        return tuple(chain)

    def validate(self) -> None:
        if self.bounded:
            raise SpecError(
                "FULL_CATALOG_REQUIRED",
                f"record-bound view of "
                f"{self.bounded_owner or 'shared records'} cannot audit the whole Project",
            )
        validate_shared_roots(self.root)
        for owner, metadata in self.subprojects.items():
            reference = metadata.get("linked_prd")
            if not isinstance(reference, str) or not reference:
                raise SpecError("ANCESTRY_INVALID", f"{owner}: missing linked_prd")
            try:
                self.resolve(self.root / "subprojects" / owner / reference, owner=owner, kind="prd")
            except SpecError as error:
                raise SpecError("ANCESTRY_INVALID", f"{owner}: {error}") from error
        for record in self.records:
            self.ancestry(record)
            self.dependencies(record)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(record: SpecRef) -> None:
            identity = record.qualified_id
            if identity in visiting:
                raise SpecError("DEPENDENCY_CYCLE", identity)
            if identity in visited:
                return
            visiting.add(identity)
            for dependency in self.dependencies(record):
                visit(dependency)
            visiting.remove(identity)
            visited.add(identity)

        for record in self.records:
            visit(record)

    def dependencies(self, record: SpecRef) -> tuple[SpecRef, ...]:
        record = self._checked(record)
        values = record.metadata.get("depends_on", [])
        declared = record.metadata.get("cross_subproject_dependencies", [])
        for key, items in (("depends_on", values), ("cross_subproject_dependencies", declared)):
            if not isinstance(items, (list, tuple)) or any(not isinstance(item, str) or not item for item in items):
                raise SpecError("DEPENDENCY_INVALID", f"{record.qualified_id}: {key}")
        result: list[SpecRef] = []
        for value in dict.fromkeys([*values, *declared]):
            reference = value if value.startswith(self.project_id + "/") else record.path.parent / value
            try:
                dependency = self.resolve(reference)
            except SpecError as error:
                raise SpecError("DEPENDENCY_INVALID", f"{record.qualified_id}: {value}: {error}") from error
            foreign = dependency.subproject_id != record.subproject_id
            if foreign and (value not in declared or value != dependency.qualified_id):
                raise SpecError("DEPENDENCY_INVALID", f"{record.qualified_id}: undeclared foreign {value}")
            if value in declared and not foreign:
                raise SpecError("DEPENDENCY_INVALID", f"{record.qualified_id}: local cross-scope declaration {value}")
            result.append(dependency)
        return tuple(result)

    def next_local_id(self, kind: str, owner: str) -> str:
        """Propose a local numeric ID; creators reserve it while holding their lock."""
        if kind not in {"epic", "story"} or owner not in self.subprojects:
            raise SpecError("OWNER_MISMATCH", f"{owner}/{kind}")
        ids = [record.local_id for record in self.records
               if record.kind == kind and record.subproject_id == owner]
        if any(not value.isdecimal() for value in ids):
            raise SpecError("LOCAL_ID_INVALID", f"{owner}/{kind}")
        return str(max((int(value) for value in ids), default=0) + 1).zfill(3)


# --- Story068: subproject creation, reservation, recovery, publication ---

CREATED_KINDS = ("prd", "architecture", "epic", "story", "quick-task")
MAX_SUBPROJECT_ID = 64
OPERATION_ID = re.compile(r"[0-9a-f]{32}\Z")
CREATE_LOCK_PARTS = (".kosmic", "create.lock")
OPERATIONS_PARTS = (".kosmic", "create-ops")


def normalize_subproject_title(title: str) -> str:
    """NFKD, drop combining marks, keep lowercase ASCII alphanumerics, hyphenate runs."""
    text = unicodedata.normalize("NFKD", str(title))
    text = "".join(char for char in text if not unicodedata.combining(char))
    collapsed: list[str] = []
    for char in text.lower():
        if "a" <= char <= "z" or "0" <= char <= "9":
            collapsed.append(char)
        elif collapsed and collapsed[-1] != "-":
            collapsed.append("-")
    slug = "".join(collapsed).rstrip("-")[:MAX_SUBPROJECT_ID].rstrip("-")
    return slug or "subproject"


def _stage_bytes(root: Path, parts: tuple[str, ...], data: bytes, *, exclusive: bool = True) -> bool:
    """Write bytes under no-follow descriptors. Exclusive writes are idempotent only
    when the existing file holds identical content; any other existing target fails."""
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            try:
                os.mkdir(part, 0o700, dir_fd=fd)
            except FileExistsError:
                pass
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
        if not exclusive:
            unique = f".stage-{os.getpid()}-{os.urandom(6).hex()}"
            try:
                file_fd = os.open(unique, flags, 0o600, dir_fd=fd)
            except FileExistsError:
                raise SpecError("SCOPE_DENIED", "/".join(parts))
            try:
                with os.fdopen(file_fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.rename(unique, parts[-1], src_dir_fd=fd, dst_dir_fd=fd)
                dir_fd_tmp = os.open(".", os.O_RDONLY | os.O_DIRECTORY, dir_fd=fd)
                try:
                    os.fsync(dir_fd_tmp)
                finally:
                    os.close(dir_fd_tmp)
            except BaseException:
                try:
                    os.unlink(unique, dir_fd=fd)
                except OSError:
                    pass
                raise
            return True
        unique = f".stage-{os.getpid()}-{os.urandom(6).hex()}"
        temp_fd = os.open(unique, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                          0o600, dir_fd=fd)
        published = False
        try:
            with os.fdopen(temp_fd, "wb") as stream:
                temp_fd = -1
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            if exclusive:
                try:
                    os.link(unique, parts[-1], src_dir_fd=fd, dst_dir_fd=fd)
                    published = True
                    os.unlink(unique, dir_fd=fd)
                except FileExistsError:
                    check_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
                    try:
                        info = os.fstat(check_fd)
                        if not stat.S_ISREG(info.st_mode):
                            raise SpecError("RESERVATION_CONFLICT", "/".join(parts))
                        with os.fdopen(check_fd, "rb") as stream:
                            check_fd = -1
                            existing = stream.read()
                    finally:
                        if check_fd >= 0:
                            os.close(check_fd)
                    if existing != data:
                        raise SpecError("RESERVATION_CONFLICT", "/".join(parts))
                    return False
            else:
                os.rename(unique, parts[-1], src_dir_fd=fd, dst_dir_fd=fd)
                published = True
            dir_fd_tmp = os.open(".", os.O_RDONLY | os.O_DIRECTORY, dir_fd=fd)
            try:
                os.fsync(dir_fd_tmp)
            finally:
                os.close(dir_fd_tmp)
            return True
        finally:
            if temp_fd >= 0:
                os.close(temp_fd)
            if not published:
                try:
                    os.unlink(unique, dir_fd=fd)
                except OSError:
                    pass
    except OSError as error:
        raise SpecError("SCOPE_DENIED", f"{'/'.join(parts)}: {error.strerror}") from error
    finally:
        os.close(fd)


def _read_bytes(root: Path, parts: tuple[str, ...]) -> bytes:
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        info = os.fstat(file_fd)
        if not stat.S_ISREG(info.st_mode):
            raise SpecError("SCOPE_DENIED", "/".join(parts))
        with os.fdopen(file_fd, "rb") as stream:
            file_fd = -1
            return stream.read()
    except OSError as error:
        raise SpecError("SCOPE_DENIED", f"{'/'.join(parts)}: {error.strerror}") from error
    finally:
        os.close(fd)


@contextlib.contextmanager
def _creation_lock(root: Path):
    """Exclusive Project-wide creation lock held via retained descriptors."""
    root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            os.mkdir(".kosmic", 0o700, dir_fd=root_fd)
        except FileExistsError:
            pass
        control_fd = os.open(".kosmic", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=root_fd)
        try:
            lock_fd = os.open("create.lock", os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW,
                              0o600, dir_fd=control_fd)
        finally:
            os.close(control_fd)
    except OSError as error:
        raise SpecError("SCOPE_DENIED", f"create.lock: {error.strerror}") from error
    finally:
        os.close(root_fd)
    try:
        info = os.fstat(lock_fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise SpecError("SCOPE_DENIED", "create.lock")
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
    finally:
        os.close(lock_fd)


def _frontmatter(metadata: Mapping[str, Any]) -> bytes:
    body = "---\n" + "".join(f"{key}: {json.dumps(value)}\n" for key, value in metadata.items())
    return (body + "---\n").encode("utf-8")


def _document_bytes(metadata: Mapping[str, Any], title: str, body: str = "") -> bytes:
    text = _frontmatter(metadata).decode("utf-8") + f"\n# {title}\n"
    if body:
        text += f"\n{body}"
    return text.encode("utf-8")


def _operation_path(operation_id: str) -> tuple[str, ...]:
    if not OPERATION_ID.fullmatch(operation_id or ""):
        raise SpecError("OPERATION_NOT_FOUND", str(operation_id))
    return OPERATIONS_PARTS + (f"{operation_id}.json",)


def _load_operation(root: Path, operation_id: str) -> dict[str, Any]:
    try:
        raw = _read_bytes(root, _operation_path(operation_id))
    except SpecError as error:
        if error.code in {"SCOPE_DENIED", "OPERATION_NOT_FOUND"}:
            raise SpecError("OPERATION_NOT_FOUND", str(operation_id)) from error
        raise
    return json.loads(raw.decode("utf-8"))


def _store_operation(root: Path, operation: dict[str, Any], *, replace: bool) -> None:
    data = json.dumps(operation, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    _stage_bytes(root, _operation_path(operation["operation_id"]), data, exclusive=not replace)


def _fsync_dir(fd: int) -> None:
    os.fsync(fd)


def _reserve_owner_directory(root: Path, owner: str) -> None:
    """Descriptor-safe mkdir of the reserved owner directory, durably linked."""
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        created = False
        try:
            os.mkdir(".kosmic", 0o700, dir_fd=fd)
            created = True
        except FileExistsError:
            pass
        if created:
            _fsync_dir(fd)
        kosmic_fd = os.open(".kosmic", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
        _fsync_dir(kosmic_fd)
        try:
            created = False
            try:
                os.mkdir("subprojects", 0o700, dir_fd=kosmic_fd)
                created = True
            except FileExistsError:
                pass
            if created:
                _fsync_dir(kosmic_fd)
            subprojects_fd = os.open("subprojects", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=kosmic_fd)
            try:
                os.mkdir(owner, 0o700, dir_fd=subprojects_fd)
                _fsync_dir(subprojects_fd)
            except FileExistsError as error:
                raise SpecError("RESERVATION_CONFLICT", owner) from error
        finally:
            os.close(kosmic_fd)
    except OSError as error:
        raise SpecError("SCOPE_DENIED", f"{owner}: {error.strerror}") from error
    finally:
        os.close(fd)


def _reserve_subproject_id(root: Path, slug: str) -> str:
    """First free base/-2/-3 identifier; caller holds the creation lock."""
    reserved: set[str] = set()
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            os.mkdir(".kosmic", 0o700, dir_fd=fd)
        except FileExistsError:
            pass
        kosmic_fd = os.open(".kosmic", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
        try:
            try:
                os.mkdir("subprojects", 0o700, dir_fd=kosmic_fd)
            except FileExistsError:
                pass
            try:
                owners_fd = os.open("subprojects", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except FileNotFoundError:
                owners_fd = None
            if owners_fd is not None:
                try:
                    existing = sorted(
                        name for name in os.listdir(owners_fd)
                        if not name.startswith(".")
                    )
                finally:
                    os.close(owners_fd)
            else:
                existing = []
            subprojects_fd = None
            try:
                subprojects_fd = os.open("subprojects", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=kosmic_fd)
            except FileNotFoundError:
                pass
            if subprojects_fd is not None:
                try:
                    os.close(subprojects_fd)
                except OSError:
                    pass
            try:
                ops_fd = os.open("create-ops", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=kosmic_fd)
            except FileNotFoundError:
                ops_fd = None
            if ops_fd is not None:
                try:
                    for name in os.listdir(ops_fd):
                        if not name.endswith(".json"):
                            continue
                        try:
                            operation_fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=ops_fd)
                        except OSError:
                            continue
                        try:
                            info = os.fstat(operation_fd)
                            if not stat.S_ISREG(info.st_mode):
                                continue
                            with os.fdopen(operation_fd, "rb") as stream:
                                operation_fd = -1
                                payload = json.loads(stream.read().decode("utf-8"))
                            if isinstance(payload.get("subproject_id"), str):
                                reserved.add(payload["subproject_id"])
                        except (OSError, ValueError, json.JSONDecodeError):
                            if operation_fd >= 0:
                                os.close(operation_fd)
                            continue
                        finally:
                            if operation_fd >= 0:
                                os.close(operation_fd)
                finally:
                    os.close(ops_fd)
        finally:
            os.close(kosmic_fd)
    except OSError as error:
        raise SpecError("SCOPE_DENIED", f"subprojects: {error.strerror}") from error
    finally:
        os.close(fd)
    used = set(existing) | reserved
    base = slug[:MAX_SUBPROJECT_ID]
    if base not in used:
        return base
    suffix = 2
    while True:
        tail = f"-{suffix}"
        candidate = base[:MAX_SUBPROJECT_ID - len(tail)].rstrip("-") + tail
        if candidate not in used:
            return candidate
        suffix += 1
    taken = {entry.name for entry in base_dir.iterdir()}
    counter = 1
    while counter < 1_000_000:
        if counter == 1:
            candidate = slug[:MAX_SUBPROJECT_ID].rstrip("-") or slug[:MAX_SUBPROJECT_ID]
        else:
            suffix = f"-{counter}"
            candidate = slug[:MAX_SUBPROJECT_ID - len(suffix)].rstrip("-") + suffix
        if candidate not in taken and not SLUG.fullmatch(candidate):
            raise SpecError("LOCAL_ID_INVALID", candidate)
        if candidate in taken:
            counter += 1
            continue
        try:
            (base_dir / candidate).mkdir()
        except FileExistsError:
            taken.add(candidate)
            counter += 1
            continue
        return candidate
    raise SpecError("RESERVATION_CONFLICT", slug)


def _project_id(root: Path) -> str:
    entry = read_document(root, root / "ProjectEntry.md")
    return str(entry.metadata.get("project_id", ""))


def _subproject_documents(root: Path, owner: str, title: str) -> dict[tuple[str, ...], bytes]:
    pid = _project_id(root)
    common = {"project_id": pid, "subproject_id": owner, "status": "draft"}
    return {
        ("subprojects", owner, "SubprojectEntry.md"): _document_bytes(
            {"schema": "kosmic.subproject/1", "project_id": pid, "subproject_id": owner,
             "title": title, "linked_prd": "specs/prd.md", "status": "draft"}, title),
        ("subprojects", owner, "specs", "prd.md"): _document_bytes(
            {**common, "record_kind": "prd", "local_id": "prd"}, title,
            "## Purpose\n\n(draft)\n"),
        ("subprojects", owner, "specs", "INDEX.md"): (
            f"# {title} Specs\n\n- [PRD](prd.md)\n").encode("utf-8"),
    }


def _create_subproject(root: Path, title: str, *, resume: bool,
                       operation_id: str | None) -> dict[str, Any]:
    display = title.strip() or "Subproject"
    slug = normalize_subproject_title(title)
    resumed = False
    if resume:
        if not operation_id:
            raise SpecError("RESUME_REQUIRED", "explicit operation_id is required to resume")
        operation = _load_operation(root, operation_id)
        if operation.get("kind") != "prd":
            raise SpecError("OPERATION_NOT_FOUND", f"{operation_id}: kind mismatch")
        if operation.get("status") == "published":
            raise SpecError("RESERVATION_CONFLICT", f"{operation_id}: already published")
        owner = operation["subproject_id"]
        resumed = True
    else:
        with _creation_lock(root):
            owner = _reserve_subproject_id(root, slug)
            operation = {
                "operation_id": uuid.uuid4().hex,
                "project_id": _project_id(root),
                "kind": "prd",
                "title": display,
                "subproject_id": owner,
                "status": "reserved",
            }
            _store_operation(root, operation, replace=False)
        _reserve_owner_directory(root, owner)
    staged = _subproject_documents(root, owner, operation["title"])
    for parts, data in sorted(staged.items()):
        _stage_bytes(root, parts, data)
    operation["status"] = "published"
    with _creation_lock(root):
        _store_operation(root, operation, replace=True)
    return {
        "operation_id": operation["operation_id"],
        "project_id": operation["project_id"],
        "kind": "prd",
        "subproject_id": owner,
        "local_id": "prd",
        "title": operation["title"],
        "status": "published",
        "resumed": resumed,
        "paths": {"/".join(parts): parts for parts in staged},
    }


def _create_owned_record(root: Path, kind: str, title: str, owner: str | None,
                         parent: str | Path | None) -> dict[str, Any]:
    shared = owner is None
    if kind in {"architecture", "epic", "story"} and shared:
        raise SpecError("OWNER_MISMATCH", f"{kind} requires a subproject owner")
    with _creation_lock(root):
        try:
            catalog = SpecCatalog(root)
            pid = catalog.project_id
        except SpecError as error:
            if error.code != "MIGRATION_REQUIRED" or kind != "quick-task" or not shared:
                raise
            # Flat feature specs block the owner-aware catalog, not a draft
            # shared Quick Task used to request the migration itself.
            catalog = None
            pid = _project_id(root)
            if not SLUG.fullmatch(pid):
                raise SpecError("PROJECT_ID_INVALID", str(root))
        if shared:
            specs = root / "specs"
            common: dict[str, Any] = {"project_id": pid, "subproject_id": None, "status": "draft"}
            owner_key: str | None = None
        else:
            if owner not in catalog.subprojects:
                raise SpecError("OWNER_MISMATCH", str(owner))
            specs = root / "subprojects" / owner / "specs"
            common = {"project_id": pid, "subproject_id": owner, "status": "draft"}
            owner_key = owner
        parent_ref: SpecRef | None = None
        if kind == "architecture":
            local_id, relative, chain = "architecture", Path("architecture.md"), {}
        elif kind == "epic":
            parent_ref = catalog.resolve(parent, owner=owner_key, kind="architecture")
            number = catalog.next_local_id("epic", owner)
            local_id = number
            relative = Path("epics") / f"epic-{number}.md"
            chain = {"linked_architecture": parent_ref}
        elif kind == "story":
            parent_ref = catalog.resolve(parent, owner=owner_key, kind="epic")
            architecture = catalog._parent(parent_ref, "linked_architecture", "architecture")
            number = catalog.next_local_id("story", owner)
            local_id = number
            relative = Path("stories") / f"story-{number}.md"
            chain = {"linked_epic": parent_ref, "linked_architecture": architecture}
        else:
            local_id = normalize_subproject_title(title)
            relative = Path("quick-tasks") / f"{local_id}.md"
            chain = {}
        path = specs / relative
        if catalog is None:
            # The legacy work-record resolver also identifies flat tasks by
            # local_id; reject aliases at another filename before publishing.
            for existing in sorted((specs / "quick-tasks").glob("*.md")):
                meta = read_document(root, existing).metadata
                if (meta.get("project_id") == pid and meta.get("record_kind") == "quick-task"
                        and meta.get("subproject_id") in (None, "", "null")
                        and meta.get("local_id") == local_id):
                    raise SpecError("RESERVATION_CONFLICT", str(existing))
        if parent_ref is not None and parent_ref.subproject_id != owner_key:
            raise SpecError("OWNER_MISMATCH", f"{parent_ref.qualified_id}: foreign parent")
        metadata = {**common, "record_kind": kind, "local_id": local_id}
        if kind in {"architecture", "epic", "story"}:
            prd = catalog.resolve("prd", owner=owner_key, kind="prd")
            metadata["linked_prd"] = Path(os.path.relpath(prd.path, path.parent)).as_posix()
            for key, ancestor in chain.items():
                metadata[key] = Path(os.path.relpath(ancestor.path, path.parent)).as_posix()
            if kind == "story":
                metadata["depends_on"] = []
        parts = tuple(os.path.relpath(path, root).replace(os.sep, "/").split("/"))
        created = _stage_bytes(root, parts, _document_bytes(metadata, title.strip()))
        if not created:
            raise SpecError("RESERVATION_CONFLICT", str(path))
        qualified = f"{pid}/{owner}/{kind}/{local_id}" if owner else f"{pid}/{kind}/{local_id}"
        return {
            "operation_id": None,
            "project_id": pid,
            "kind": kind,
            "subproject_id": owner,
            "local_id": local_id,
            "title": title.strip(),
            "status": "draft",
            "resumed": False,
            "paths": {"/".join(parts): qualified},
        }


def create_spec(project_root: str | os.PathLike[str], kind: str, title: str, *,
                subproject: str | None = None, parent: str | Path | None = None,
                resume: bool = False, operation_id: str | None = None) -> dict[str, Any]:
    """Reserve and publish one specification record under an immutable identity.

    kind="prd" with subproject=None bootstraps a new subproject. Resume uses
    the explicit operation_id; titles never select, reuse, or overwrite an
    existing feature. Spec creation is bounded record bootstrap, not a work
    authorization mechanism.
    """
    root = Path(project_root).expanduser().resolve()
    if not isinstance(title, str):
        raise SpecError("SPEC_INVALID", "title must be a string")
    if kind not in CREATED_KINDS:
        raise SpecError("SPEC_INVALID", f"unknown record kind: {kind}")
    if kind == "prd":
        if subproject is not None:
            raise SpecError("OWNER_MISMATCH",
                            "prd creation reserves a new subproject; pass subproject=None")
        if resume and not operation_id:
            raise SpecError("RESUME_REQUIRED", "explicit operation_id is required to resume")
        return _create_subproject(root, title, resume=resume, operation_id=operation_id)
    if subproject is None and kind != "quick-task":
        raise SpecError("OWNER_REQUIRED", kind)
    return _create_owned_record(root, kind, title, subproject, parent)


def _legacy_spec_inventory(root: Path) -> dict[str, dict[str, Any]]:
    """Single-read snapshot; every later derivation uses exactly these bytes."""
    records: dict[str, dict[str, Any]] = {}
    patterns = (("prd", "prd*.md"), ("architecture", "architecture*.md"),
                ("epic", "epics/epic-*.md"), ("story", "stories/story-*.md"),
                ("research", "research/*.md"), ("quick-task", "quick-tasks/*.md"),
                ("proposal", "skill-proposals/*.md"))
    for kind, pattern in patterns:
        for path in sorted((root / "specs").glob(pattern)):
            parts = path.relative_to(root).parts
            raw = _read_bytes(root, parts)
            doc = parse_document_text(raw.decode("utf-8"), path)
            relative = path.relative_to(root).as_posix()
            title = next((line[2:].strip() for line in doc.body.splitlines() if line.startswith("# ")), path.stem)
            records[relative] = {"kind": kind, "metadata": doc.metadata, "body": doc.body,
                                 "title": title, "raw": raw,
                                 "before_sha256": hashlib.sha256(raw).hexdigest()}
    return records


# --- Deterministic flat-spec migration planning (schema /2) ---

_MIGRATION_PATH_KEYS = frozenset({"related_specs", "related_notes", "evidence_packs",
                                  "evidence", "review_record", "acceptance_evidence"})
_MIGRATION_PROTECTED_ROOTS = ("evidence", "log", "logs", "skills",
                              "specs/skill-proposals/inputs")
_INLINE_CODE_SPAN = re.compile(r"(`[^`\n]*`)")
_MD_INLINE_LINK = re.compile(r"(!?)\[((?:[^\[\]]|\[[^\]]*\])*)\]\(((?:[^()]|\([^()]*\))*)\)")
_MD_DEFINITION = re.compile(r"^( {0,3})\[([^\]]+)\]:([ \t]*)(<[^>]*>|\S+)([ \t]+[^\n]*)?")
_MD_HTML_REFERENCE = re.compile(
    r"<(?:a|img)\b[^>]*?\b(?:href|src)=(\"[^\"]*\"|'[^']*'|[^\s>]+)", re.IGNORECASE)
_MD_WIKI_LINK = re.compile(r"(!?)\[\[([^\[\]]+)\]\]")
_MD_TITLE = re.compile(r"\A(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*'|\([^()]*\))[ \t]*\Z")


def _is_link_key(key: str) -> bool:
    """YAML keys whose string leaves name link destinations or Project paths."""
    return key.startswith("linked_") or key in _MIGRATION_PATH_KEYS or key == "url"


def _split_destination(target: str) -> tuple[str, str, str]:
    """Split one destination into path, ``?query`` and ``#fragment`` parts.

    The parts concatenate back to ``target``; query and fragment bytes are
    preserved verbatim because authors bring them already URL-encoded.
    """
    destination, hash_separator, fragment = target.partition("#")
    path, query_separator, query = destination.partition("?")
    return path, query_separator + query, hash_separator + fragment


def _external_scheme(path_part: str) -> bool:
    """True when a destination names a remote resource instead of a Project file.

    Any URL scheme is external (http, mailto, routine, skill, ...) except a
    possibly project-local ``file:`` URI; ``//host/path`` is external too.
    """
    if path_part.startswith("//"):
        return True
    scheme = urllib.parse.urlsplit(path_part).scheme
    return bool(scheme) and scheme.lower() != "file"


def _decoded_link_path(root: Path, source: str, path_part: str) -> str | None:
    """Project-relative path a link destination resolves to, else None.

    Percent-encoding is decoded before matching; ``file:`` URIs and absolute
    paths anchor at the filesystem root, everything else at the source file's
    directory. None marks destinations outside the Project: they are never
    rewritten and never repaired.
    """
    text = path_part.strip()
    parsed = urllib.parse.urlsplit(text)
    if parsed.scheme:
        if parsed.scheme.lower() != "file" or parsed.netloc not in ("", "localhost"):
            return None
        decoded = urllib.parse.unquote(parsed.path)
        base = root
    else:
        decoded = urllib.parse.unquote(text)
        base = root if decoded.startswith("/") else root / Path(source).parent
    if not decoded:
        return None
    try:
        return Path(os.path.abspath(base / decoded)).relative_to(root).as_posix()
    except ValueError:
        return None


def _compose_destination(root: Path, destination: str, target: str,
                         query_part: str, fragment_part: str) -> str:
    """Rewritten destination text: percent-encoded relative path plus preserved
    query and fragment parts."""
    relative = os.path.relpath(root / target, root / Path(destination).parent)
    return urllib.parse.quote(relative.replace(os.sep, "/")) + query_part + fragment_part


def _link_filename_index(targets: Iterable[str],
                         mapping: Mapping[str, str]) -> dict[str, list[str]]:
    """basename and stem index over the final authoritative document view.

    Moved sources additionally index their old basename and stem as aliases,
    so a reference to a record's former name resolves to its new destination.
    Every key maps to a sorted candidate list; multi-entry lists are ambiguous
    and are never guessed.
    """
    index: dict[str, set[str]] = {}

    def add(key: str, target: str) -> None:
        if key:
            index.setdefault(key, set()).add(target)

    for target in targets:
        name = Path(target).name
        add(name, target)
        if name.endswith(".md"):
            add(name[:-3], target)
    for source, target in mapping.items():
        name = Path(source).name
        add(name, target)
        if name.endswith(".md"):
            add(name[:-3], target)
    return {key: sorted(found) for key, found in sorted(index.items())}


@dataclass
class _LinkAudit:
    """One shared link pipeline for a plan: resolve, rewrite, correct, report.

    Migrated records, staying Project documents and the read-only protected
    scan all route through ``rewrite_text`` and ``rewrite_metadata_value`` so
    YAML scalars, markdown destinations, HTML attributes and wiki references
    follow the same resolution rules. Ambiguous filename matches are reported
    and left untouched; nothing is ever guessed.
    """
    root: Path
    mapping: dict[str, str]
    view: frozenset[str]
    filename_index: dict[str, list[str]]
    alias_keys: frozenset[str] = frozenset()
    legacy: Mapping[str, dict[str, Any]] = field(default_factory=dict)
    live_links: list[dict[str, Any]] = field(default_factory=list)
    corrections: list[dict[str, Any]] = field(default_factory=list)
    problems: list[dict[str, Any]] = field(default_factory=list)
    historical: list[dict[str, str]] = field(default_factory=list)
    target_pins: dict[str, str] = field(default_factory=dict)

    def in_view(self, relative: str | None) -> bool:
        return relative is not None and (relative in self.view or relative in self.target_pins)

    def valid_target(self, relative: str) -> bool:
        """Explicit targets may be pinned without becoming write or repair candidates."""
        if self.in_view(relative):
            return True
        parts = tuple(relative.split("/"))
        if (not relative.endswith(".md") or any(part in {"", ".", ".."} for part in parts)
                or parts[0] in {".git", ".tmp", ".kosmic"}):
            return False
        try:
            raw = _read_bytes(self.root, parts)
        except SpecError as error:
            if isinstance(error.__cause__, OSError) and error.__cause__.errno == errno.ENOENT:
                return False
            raise
        self.target_pins[relative] = hashlib.sha256(raw).hexdigest()
        return True

    def record_live_link(self, source: str, target: str, fragment_part: str) -> None:
        if not self.in_view(target):
            return
        link: dict[str, Any] = {"source": source, "target": target}
        if fragment_part:
            link["fragment"] = fragment_part[1:]
        if link not in self.live_links:
            self.live_links.append(link)

    def _correction(self, source: str, reference: str, replacement: str,
                    target: str, basis: str) -> None:
        row = {"source": source, "reference": reference, "replacement": replacement,
               "target": target, "basis": basis}
        if row not in self.corrections:
            self.corrections.append(row)

    def report_problem(self, record: str, reference: str, reason: str,
                 candidates: list[str], *, protected: bool) -> None:
        row = {"record": record, "reference": reference, "reason": reason,
               "candidates": candidates, "protected": protected}
        if row not in self.problems:
            self.problems.append(row)

    def _historical(self, source: str, reference: str, old_relative: str) -> None:
        if (old_relative in self.legacy and old_relative not in self.mapping
                and not old_relative.startswith("specs/quick-tasks/")
                and not old_relative.startswith("specs/skill-proposals/")):
            row = {"source": source, "reference": reference, "old_path": old_relative,
                   "disposition": "historical-unresolved"}
            if row not in self.historical:
                self.historical.append(row)

    def filename_candidates(self, old_relative: str) -> list[str]:
        """Unique-filename candidates for a broken path: basename and stem."""
        name = Path(old_relative).name
        keys = {name}
        if name.endswith(".md"):
            keys.add(name[:-3])
        found: set[str] = set()
        for key in keys:
            found.update(self.filename_index.get(key, ()))
        return sorted(found)

    def _resolved_rewrite(self, source: str, destination: str, original: str,
                          old_relative: str, query_part: str, fragment_part: str,
                          *, repair: bool, protected: bool,
                          preserve_valid: bool = False) -> tuple[str, str]:
        """Rewrite one destination to an already-resolved Project-relative path."""
        if old_relative in self.mapping:
            target = self.mapping[old_relative]
            if protected:
                self.report_problem(source, original, "moved-reference", [target],
                                    protected=True)
                return original, "protected-moved"
            new = _compose_destination(self.root, destination, target,
                                       query_part, fragment_part)
            self._correction(source, original, new, target, "mapped-path")
            self.record_live_link(source, target, fragment_part)
            return new, "mapped"
        if self.valid_target(old_relative):
            if protected:
                return original, "protected-valid"
            self.record_live_link(source, old_relative, fragment_part)
            if preserve_valid:
                return original, "valid"
            new = _compose_destination(self.root, destination, old_relative,
                                       query_part, fragment_part)
            return new, "valid"
        if protected:
            candidates = self.filename_candidates(old_relative)
            self.report_problem(source, original,
                          "ambiguous-link" if len(candidates) > 1 else "unresolved-link",
                          candidates, protected=True)
            return original, "protected-broken"
        if not repair:
            return original, "label"
        candidates = self.filename_candidates(old_relative)
        if len(candidates) > 1:
            self.report_problem(source, original, "ambiguous-link", candidates,
                          protected=False)
            self._historical(source, original, old_relative)
            return original, "ambiguous"
        if not candidates:
            self.report_problem(source, original, "unresolved-link", [], protected=False)
            self._historical(source, original, old_relative)
            return original, "unresolved"
        new = _compose_destination(self.root, destination, candidates[0],
                                   query_part, fragment_part)
        name = Path(old_relative).name
        keys = {name, name[:-3]} if name.endswith(".md") else {name}
        basis = "moved-alias" if keys & self.alias_keys else "unique-filename"
        self._correction(source, original, new, candidates[0], basis)
        self.record_live_link(source, candidates[0], fragment_part)
        return new, "repaired"

    def rewrite_text(self, source: str, destination: str, target: str, *,
                     repair: bool = True, protected: bool = False,
                     project_relative_first: bool = False,
                     preserve_valid: bool = False) -> tuple[str, str]:
        """Rewrite one destination string; report, never guess.

        Returns the untouched text for external and anchor destinations, for
        ambiguous or unresolved references, and for guarded scalar labels
        (``repair=False`` keeps evidence hashes and similar labels intact).
        ``preserve_valid`` keeps already-valid references byte-identical for
        documents that stay in place. The outcome is one of ``external``,
        ``mapped``, ``valid``, ``repaired``, ``ambiguous``, ``unresolved``,
        ``label`` or a ``protected-*`` variant used by the read-only protected
        scan.
        """
        path_part, query_part, fragment_part = _split_destination(target)
        if not path_part.strip() or _external_scheme(path_part):
            return target, "external"
        if project_relative_first and not path_part.startswith(("../", "./")):
            decoded = urllib.parse.unquote(path_part)
            if decoded in self.mapping or self.valid_target(decoded):
                return self._resolved_rewrite(source, destination, target, decoded,
                                              query_part, fragment_part,
                                              repair=repair, protected=protected,
                                              preserve_valid=preserve_valid)
        old_relative = _decoded_link_path(self.root, source, path_part)
        if old_relative is None:
            return target, "external"
        return self._resolved_rewrite(source, destination, target, old_relative,
                                      query_part, fragment_part,
                                      repair=repair, protected=protected,
                                      preserve_valid=preserve_valid)

    def prune_unemitted(self, source: str, replacements: Mapping[str, Mapping[str, str]],
                        applied: set[tuple[str, str]]) -> None:
        """Report unresolved scalar placement instead of claiming an emitted repair."""
        stale = {old for key, values in replacements.items() for old in values
                 if (key, old) not in applied}
        if not stale:
            return
        retained = []
        for row in self.corrections:
            if row["source"] == source and row["reference"] in stale:
                self.report_problem(source, row["reference"], "unsupported-link-rewrite",
                                    [row["target"]], protected=False)
            else:
                retained.append(row)
        self.corrections[:] = retained

    def rewrite_metadata_value(self, source: str, destination: str, key: str,
                               value: str, *, protected: bool = False) -> str:
        """Rewrite one path-bearing YAML scalar under ``key``.

        Linked ancestry prefers an existing document-relative target; only
        without one does the Project-relative metadata convention apply.
        Other metadata retains Project-relative precedence. Non-path labels
        stay guarded, and valid references in staying documents retain bytes.
        """
        guarded = not (key.startswith("linked_") or key == "related_specs" or key == "url")
        project_relative_first = True
        if key.startswith("linked_"):
            local = _decoded_link_path(self.root, source, _split_destination(value)[0])
            project_relative_first = not (local in self.mapping
                                         or (local is not None and self.valid_target(local)))
        new, _outcome = self.rewrite_text(
            source, destination, value,
            repair=not guarded, protected=protected,
            project_relative_first=project_relative_first,
            preserve_valid=source == destination)
        return new


def _migration_directories(root: Path, existing_owners: list[str],
                           relevant_paths: list[str]) -> list[str]:
    """Existing Project-relative directories relevant to inputs/outputs/owners.

    Existing directories only: excludes .git, managed .tmp runs, migration
    transactions and all of .kosmic (the creation lock may materialize it
    during preflight; it is runtime state, never an approved output directory).
    """
    directories: set[str] = set()
    candidates = ["specs", "subprojects", "notes",
                  *(f"subprojects/{owner}" for owner in existing_owners),
                  *(f"subprojects/{owner}/specs" for owner in existing_owners),
                  *relevant_paths]
    for item in candidates:
        current = Path(item)
        chain: list[str] = []
        while str(current) != ".":
            chain.insert(0, current.as_posix())
            current = current.parent
        for name in chain:
            absolute = root / name
            if absolute.is_dir() and not absolute.is_symlink():
                directories.add(name)
    for owner in existing_owners:
        specs = root / "subprojects" / owner / "specs"
        if specs.is_dir() and not specs.is_symlink():
            for path in sorted(specs.rglob("*")):
                if path.is_dir() and not path.is_symlink():
                    directories.add(path.relative_to(root).as_posix())
    # .kosmic state (creation lock, receipts, migrations) and managed .tmp are
    # runtime state, not approved output directories; .git is never touched.
    return sorted(
        name for name in directories - {".git", ".tmp"}
        if not (name == ".kosmic" or name.startswith(".kosmic/")))


def _migration_cli():
    """Import the Project CLI lazily; one implementation, no import cycle."""
    if __package__:
        from . import kosmic_project_skills as cli
    else:
        import kosmic_project_skills as cli
    return cli


def _migration_status_binding(root: Path, entry_metadata: Mapping[str, Any]) -> dict[str, Any]:
    """Pin an already-valid STATUS binding; only absent metadata is unbound.

    A configured binding is validated through the existing
    ``resolve_status_root`` contract: a missing directory, a status_root
    outside a Git worktree or a sibling collision raises a typed
    ``MIGRATION_STATUS_INVALID`` error instead of producing an applicable plan
    or silently downgrading to ``unbound``. A bound directory whose STATUS.md
    does not exist yet stays ``bound`` with ``before_sha256`` None: migration
    creates it (FR-M09).
    """
    unbound: dict[str, Any] = {"path": None, "before_sha256": None, "head": "unknown",
                               "disposition": "unbound"}
    text = str(entry_metadata.get("status_root") or "").strip()
    if not text:
        return unbound
    candidate = Path(text)
    candidate = candidate if candidate.is_absolute() else root / candidate
    cli = _migration_cli()
    try:
        resolved = cli.resolve_status_root(candidate, project=root)
    except cli.KosmicError as error:
        raise SpecError("MIGRATION_STATUS_INVALID", str(error)) from error
    status_path = resolved / "STATUS.md"
    raw: bytes | None
    try:
        info = os.lstat(status_path)
    except FileNotFoundError:
        info = None
    except OSError as error:
        raise SpecError("MIGRATION_STATUS_INVALID",
                        f"{status_path}: {error.strerror}") from error
    if info is None:
        raw = None
    else:
        if not stat.S_ISREG(info.st_mode):
            raise SpecError("MIGRATION_STATUS_INVALID",
                            f"{status_path}: not a regular file")
        try:
            descriptor = os.open(status_path, os.O_RDONLY | os.O_NOFOLLOW)
            with os.fdopen(descriptor, "rb") as stream:
                raw = stream.read()
        except OSError as error:
            raise SpecError("MIGRATION_STATUS_INVALID",
                            f"{status_path}: {error.strerror}") from error
    completed = subprocess.run(["git", "-C", str(resolved), "rev-parse", "HEAD"],
                               check=False, capture_output=True, text=True)
    head = completed.stdout.strip() if completed.returncode == 0 else ""
    return {"path": str(status_path),
            "before_sha256": hashlib.sha256(raw).hexdigest() if raw is not None else None,
            "head": head or "unknown", "disposition": "bound"}


def _walk_markdown_files(root: Path, directory: Path) -> list[Path]:
    """Recursively list regular .md files; symlinks anywhere are typed errors."""
    if directory.is_symlink():
        raise SpecError("SCOPE_DENIED", str(directory))
    found: list[Path] = []
    for path in sorted(directory.iterdir()):
        if path.is_symlink():
            raise SpecError("SCOPE_DENIED", str(path))
        if path.is_dir():
            found.extend(_walk_markdown_files(root, path))
        elif path.is_file() and path.suffix == ".md":
            found.append(path)
    return found


def _migration_protected_paths(root: Path) -> list[Path]:
    """Inventory immutable Markdown targets with the same symlink guards as sources."""
    paths: list[Path] = []
    for name in _MIGRATION_PROTECTED_ROOTS:
        base = root / name
        if base.is_symlink():
            raise SpecError("SCOPE_DENIED", str(base))
        if base.is_dir():
            paths.extend(_walk_markdown_files(root, base))
    return paths


def _migration_inbound_paths(root: Path, existing_owners: list[str]) -> list[str]:
    """Active authoritative documents whose live references may point at moved records.

    Root Markdown, notes/, mathdocs/, authoritative specs and existing owner
    entries/specs are audited and rewritten surgically. Proposal input manifests
    and curated snapshots are protected, not authoritative records.
    """
    paths: list[str] = []
    for path in sorted(root.iterdir()):
        if path.suffix != ".md" or path.name == "STATUS.md":
            continue
        if path.is_symlink():
            raise SpecError("SCOPE_DENIED", str(path))
        if path.is_file():
            paths.append(path.name)
    for directory in ("notes", "mathdocs", "specs"):
        base = root / directory
        if base.is_dir():
            paths.extend(path.relative_to(root).as_posix()
                         for path in _walk_markdown_files(root, base))
    for owner in existing_owners:
        paths.append(f"subprojects/{owner}/SubprojectEntry.md")
        specs = root / "subprojects" / owner / "specs"
        if specs.is_dir():
            paths.extend(path.relative_to(root).as_posix()
                         for path in _walk_markdown_files(root, specs))
    return sorted(path for path in dict.fromkeys(paths)
                  if not any(path.startswith(protected + "/")
                             for protected in _MIGRATION_PROTECTED_ROOTS))


def _migration_state_inputs(root: Path) -> dict[str, str]:
    """Pin receipt/registry state STATUS rendering and recovery depend on.

    Migration transactions (.kosmic/migrations) and managed runs (.tmp) are
    excluded on purpose: they are never planning inputs.
    """
    inputs: dict[str, str] = {}
    kosmic = root / ".kosmic"
    if not kosmic.is_dir() or kosmic.is_symlink():
        return inputs
    if (kosmic / "workdirs.json").is_file():
        inputs[".kosmic/workdirs.json"] = hashlib.sha256(
            _read_bytes(root, (".kosmic", "workdirs.json"))).hexdigest()
    receipts = kosmic / "work-receipts"
    if receipts.is_dir() and not receipts.is_symlink():
        for path in sorted(receipts.glob("*.json")):
            parts = tuple(path.relative_to(root).parts)
            inputs[path.relative_to(root).as_posix()] = hashlib.sha256(
                _read_bytes(root, parts)).hexdigest()
    return inputs


def _read_quoted(line: str, start: int) -> tuple[str, str, str] | None:
    """Read one quoted scalar at ``start``: (token, logical value, quote char).

    Double-quoted escapes (including ``\\uXXXX``) are resolved for matching;
    single-quoted ``''`` doubling is unescaped. None marks an unterminated
    token: the line is left untouched.
    """
    quote = line[start]
    index = start + 1
    while index < len(line):
        char = line[index]
        if quote == "'" and char == "'":
            if line[index:index + 2] == "''":
                index += 2
                continue
            return line[start:index + 1], line[start + 1:index].replace("''", "'"), quote
        if quote == '"' and char == "\\":
            index += 2
            continue
        if quote == '"' and char == '"':
            token = line[start:index + 1]
            try:
                value = json.loads(token)
            except ValueError:
                value = line[start + 1:index]
            return token, str(value), quote
        index += 1
    return None


_YAML_INDICATORS = set("!&*[{}]>,%@`\"'#|?:-")


def _render_scalar(value: str, quote: str | None) -> str:
    """Render a replacement scalar, keeping the original quoting style."""
    if quote == "'":
        return "'" + value.replace("'", "''") + "'"
    if quote == '"':
        return json.dumps(value)
    if value == "" or value[0] in _YAML_INDICATORS or value[0].isspace() \
            or ": " in value or " #" in value or value.endswith(":"):
        return json.dumps(value)
    return value


_KEY_TOKEN = re.compile(r"([A-Za-z_][A-Za-z0-9_-]*):")

def _rewrite_frontmatter_scalars(head_text: str, replacements: Mapping[str, Mapping[str, str]]
                                 ) -> tuple[str, set[tuple[str, str]]]:
    """Surgically rewrite mapped path-bearing values in inbound YAML frontmatter.

    One scanner pass carries its state across physical lines: the flow stack
    (``[``/``{`` with entry keys, YAML ``key: v`` and JSON ``"key":v``
    spellings) and the pending block key persist until their closing
    delimiter, so multiline flow containers are rewritten in place. Scalars
    are only rewritten under their own key identity; comments, unrelated
    keys and same-text values under other keys keep their original bytes.
    Returns the rewritten header and the applied (key, old) pairs; callers
    drop recorded corrections for scalars that could not be placed, while
    problem diagnostics are always retained.
    """
    applied: set[tuple[str, str]] = set()
    if not replacements:
        return head_text, applied
    pending_key: str | None = None
    # Flow contexts: ("seq", inherited key, False) or ("map", entry key, expecting key).
    contexts: list[tuple[str, str | None, bool]] = []
    pieces: list[str] = []
    i, n = 0, len(head_text)
    at_line_start = True

    def current_key() -> str | None:
        if contexts:
            return contexts[-1][1]
        return pending_key

    while i < n:
        char = head_text[i]
        if char in " \t\n":
            pieces.append(char)
            i += 1
            if char == "\n":
                at_line_start = True
            continue
        if not contexts and at_line_start:
            entry = re.match(r"(?:-[ \t]+)*", head_text[i:])
            j = i + entry.end()
            pieces.append(head_text[i:j])
            i = j
            key_match = _KEY_TOKEN.match(head_text, i)
            if key_match is not None and (key_match.end() == n
                                          or head_text[key_match.end()] in " \t\n"):
                pending_key = key_match.group(1)
                end = key_match.end()
                while end < n and head_text[end] in " \t":
                    end += 1
                pieces.append(head_text[i:end])
                i = end
            at_line_start = False
            continue
        if char == ",":
            if contexts:
                contexts[-1] = ("map", None, True) if contexts[-1][0] == "map" \
                    else (contexts[-1][0], contexts[-1][1], False)
            pieces.append(char)
            i += 1
            continue
        if char in "[{":
            contexts.append(("map", None, True) if char == "{"
                            else ("seq", current_key(), False))
            pieces.append(char)
            i += 1
            continue
        if char in "]}":
            if contexts:
                contexts.pop()
            pieces.append(char)
            i += 1
            continue
        if contexts and contexts[-1][0] == "map" and contexts[-1][2]:
            # Entry start: accept quoted ("key":v) and bare (key: v / key:v) keys.
            quoted = _read_quoted(head_text, i) if char in "\"'" else None
            if quoted is not None and head_text[i + len(quoted[0]):].startswith(":"):
                end = i + len(quoted[0]) + 1
                while end < n and head_text[end] in " \t":
                    end += 1
                contexts[-1] = ("map", quoted[1], False)
                pieces.append(head_text[i:end])
                i = end
                continue
            bare = _KEY_TOKEN.match(head_text, i)
            if bare is not None:
                end = bare.end()
                while end < n and head_text[end] in " \t":
                    end += 1
                contexts[-1] = ("map", bare.group(1), False)
                pieces.append(head_text[i:end])
                i = end
                continue
            contexts[-1] = ("map", None, False)  # keyless entry: never a link leaf
        if char in "\"'":
            quoted = _read_quoted(head_text, i)
            if quoted is None:
                pieces.append(head_text[i:])
                break
            token, value, quote = quoted
            key = current_key()
            new = replacements.get(key, {}).get(value) if key else None
            if new is not None:
                pieces.append(_render_scalar(new, quote))
                applied.add((key, value))
            else:
                pieces.append(token)
            i += len(token)
            continue
        # Bare scalar: in flow until a delimiter, in block until comment or newline.
        end = i
        stop = ",]}" if contexts else ""
        while end < n and head_text[end] not in stop and head_text[end] != "\n":
            if head_text[end] == "#" and end > i and head_text[end - 1] in " \t":
                break
            end += 1
        region = head_text[i:end]
        value = region.strip()
        key = current_key()
        new = replacements.get(key, {}).get(value) if key else None
        if new is not None and value:
            lead = region[:len(region) - len(region.lstrip())]
            pieces.append(lead + _render_scalar(new, None))
            applied.add((key, value))
            i += len(lead) + len(value)
        else:
            pieces.append(region)
            i = end
    return "".join(pieces), applied


def _set_frontmatter_list(head: str, key: str, values: list[str]) -> str:
    """Replace only one flat YAML sequence; retain unrelated header bytes."""
    rows = head.splitlines(keepends=True)
    for index, line in enumerate(rows):
        match = re.match(rf"^(\s*{re.escape(key)}:\s*)", line)
        if match is None:
            continue
        end = index + 1
        while end < len(rows) and rows[end].lstrip().startswith("- "):
            end += 1
        newline = "\r\n" if line.endswith("\r\n") else "\n"
        rows[index:end] = [match.group(1).rstrip() + " " + json.dumps(values) + newline]
        return "".join(rows)
    newline = "\r\n" if "\r\n" in head else "\n"
    rows.insert(len(rows) - 1, f"{key}: {json.dumps(values)}{newline}")
    return "".join(rows)


def _migration_owner_entry_bytes(project_id: str, owner: str, title: str, status: str) -> bytes:
    return _document_bytes({"schema": "kosmic.subproject/1", "project_id": project_id,
                            "subproject_id": owner, "title": title,
                            "linked_prd": "specs/prd.md", "status": status}, title)


def _migration_owner_index_bytes(owner: str, owner_records: list[dict[str, Any]],
                                 legacy: Mapping[str, dict[str, Any]]) -> bytes:
    title = next((legacy[row["source"]]["title"] for row in owner_records
                  if row["kind"] == "prd"), owner)
    specs_prefix = f"subprojects/{owner}/specs"
    lines = [f"# {title} Specs", "", "- [PRD](prd.md)"]
    if any(row["kind"] == "architecture" for row in owner_records):
        lines.append("- [Architecture](architecture.md)")
    for heading, kind in (("Epics", "epic"), ("Stories", "story"), ("Research", "research")):
        rows = sorted((row for row in owner_records if row["kind"] == kind),
                      key=lambda row: row["destination"])
        if not rows:
            continue
        lines.extend(["", f"## {heading}"])
        for row in rows:
            relative = os.path.relpath(row["destination"], specs_prefix).replace(os.sep, "/")
            status = legacy[row["source"]]["metadata"].get("status", "draft")
            lines.append(f"- [{legacy[row['source']]['title']}]({relative}) — {status}")
    return ("\n".join(lines) + "\n").encode("utf-8")


def _migration_project_index_bytes(shared: list[str],
                                   legacy: Mapping[str, dict[str, Any]],
                                   owner_rows: list[tuple[str, str, str]]) -> bytes:
    lines = ["# Specs Index"]
    for heading, kind in (("Quick Tasks", "quick-task"), ("Skill Proposals", "proposal")):
        rows = [path for path in shared if legacy[path]["kind"] == kind]
        if not rows:
            continue
        lines.extend(["", f"## {heading}"])
        for path in rows:
            lines.append(f"- [{legacy[path]['title']}]({path[len('specs/'):]:s})"
                         f" — {legacy[path]['metadata'].get('status', 'draft')}")
    text = _apply_owner_navigation("\n".join(lines) + "\n", owner_rows) if owner_rows \
        else "\n".join(lines) + "\n"
    return text.encode("utf-8")


_MIGRATION_OWNERS_START = "<!-- kosmic:migration-owners:start -->"
_MIGRATION_OWNERS_END = "<!-- kosmic:migration-owners:end -->"


def _apply_owner_navigation(text: str, owner_rows: list[tuple[str, str, str]]) -> str:
    """Append or update the deterministic managed owner-navigation section.

    Unrelated index bytes are preserved; a previous managed section is replaced
    in place so replanning stays idempotent.
    """
    lines = [_MIGRATION_OWNERS_START, "", "## Migrated Subprojects", ""]
    for owner, title, status in owner_rows:
        lines.append(f"- [{title}](../subprojects/{owner}/specs/INDEX.md) — {status}")
    section = "\n".join(lines) + "\n" + _MIGRATION_OWNERS_END + "\n"
    start = text.find(_MIGRATION_OWNERS_START)
    end = text.find(_MIGRATION_OWNERS_END)
    if start != -1 and end >= start:
        text = text[:start] + text[end + len(_MIGRATION_OWNERS_END):]
    if not text.endswith("\n"):
        text += "\n"
    return text + section


def _stage_plan_view(scratch: Path, root: Path, inputs: Mapping[str, str],
                     outputs: list[dict[str, Any]], deletions: list[dict[str, Any]]) -> None:
    """Materialize the minimum candidate view: pinned inputs minus deletions plus outputs."""
    removed = {item["path"] for item in deletions}
    for relative in sorted(inputs):
        if relative in removed or Path(relative).parts[0] == ".tmp":
            continue
        _stage_bytes(scratch, tuple(Path(relative).parts),
                     _read_bytes(root, tuple(Path(relative).parts)), exclusive=False)
    for item in outputs:
        _stage_bytes(scratch, tuple(Path(item["path"]).parts),
                     item["content"].encode("utf-8"), exclusive=False)


def _planned_status_bytes(root: Path, head: str, resolved_status_root: Path,
                          inputs: Mapping[str, str], outputs: list[dict[str, Any]],
                          deletions: list[dict[str, Any]]) -> bytes | None:
    """Render the exact STATUS candidate from the staged plan view.

    Uses the existing read-only ``ephemeral_command_run`` scratch, the staged
    ``SpecCatalog`` and the existing ``render_status`` so the reviewed plan
    authenticates the planned STATUS bytes. Returns None when the staged view
    cannot validate (reported separately as a plan blocker).
    """
    cli = _migration_cli()
    try:
        with cli.ephemeral_command_run(root, "migration-plan-status") as scratch:
            _stage_plan_view(scratch, root, inputs, outputs, deletions)
            catalog = SpecCatalog(scratch)
            catalog.validate()
            project = replace(cli.load_project(root), status_root=resolved_status_root)
            return cli.render_status(project, head, catalog=catalog)
    except SpecError:
        return None


def validate_migration_links(stage_root: str | os.PathLike[str],
                             plan: Mapping[str, Any]) -> None:
    """Every mapped live link must resolve to its intended record in the staged view.

    Only migrated/mapped targets are checked; unrelated historical links in old
    fixtures must not block validation.
    """
    root = Path(stage_root).expanduser().resolve()
    links = sorted(plan.get("live_links") or [],
                   key=lambda item: (str(item.get("source", "")), str(item.get("target", "")),
                                     str(item.get("fragment", ""))))
    for link in links:
        source = str(link.get("source", ""))
        target = str(link.get("target", ""))
        try:
            resolved = (root / target).resolve(strict=True)
        except OSError as error:
            raise SpecError("MIGRATION_LINK_INVALID", f"{source} -> {target}: {error}") from error
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise SpecError("MIGRATION_LINK_INVALID", f"{source} -> {target}")


def migration_plan(project_root: Path, *, work_record: str | None = None,
                   assignments: Mapping[str, str] | None = None,
                   fingerprint_fn: Any = None) -> dict[str, Any]:
    """Propose owner/path mapping without writing or authorizing application.

    ``fingerprint_fn`` is the Project's canonical proposal fingerprint function
    (injected by the CLI to keep one implementation). Without it, shared
    proposals whose planned bytes change carry only the recheck flag.

    The returned plan (schema ``kosmic.subproject-migration-plan/2``) carries
    every recomputation input: the complete legacy inventory, existing owner
    entries/specs, active inbound notes/index links and pinned STATUS state.
    ``outputs``/``deletions`` hold Project-relative paths with exact bytes and
    hashes so an executor can stage, validate, delete and publish directly.
    """
    root = Path(project_root).expanduser().resolve()
    entry = read_document(root, root / "ProjectEntry.md")
    entry_sha = hashlib.sha256(_read_bytes(root, ("ProjectEntry.md",))).hexdigest()
    project_id = str(entry.metadata.get("project_id", ""))
    if not SLUG.fullmatch(project_id):
        raise SpecError("PROJECT_ID_INVALID", str(root))
    if work_record is not None:
        read_document(root, root / work_record)
    legacy = _legacy_spec_inventory(root)
    subprojects_dir = root / "subprojects"
    if subprojects_dir.is_symlink():
        raise SpecError("SCOPE_DENIED", str(subprojects_dir))
    existing_subprojects = (sorted(path.name for path in subprojects_dir.iterdir())
                            if subprojects_dir.is_dir() else [])
    owners: dict[str, str] = {}
    used = set(existing_subprojects)
    for path, row in sorted(legacy.items()):
        if row["kind"] != "prd":
            continue
        base = normalize_subproject_title(row["title"])
        candidate, suffix = base, 1
        while candidate in used:
            suffix += 1
            tail = f"-{suffix}"
            candidate = base[:MAX_SUBPROJECT_ID - len(tail)].rstrip("-") + tail
        used.add(candidate)
        owners[path] = candidate
    explicit: dict[str, str] = {}
    for key, value in sorted((assignments or {}).items()):
        if not isinstance(key, str) or key not in legacy:
            raise SpecError("ASSIGNMENT_INVALID", f"{key}: unknown legacy source record")
        if not isinstance(value, str) or value not in owners:
            raise SpecError("ASSIGNMENT_INVALID",
                            f"{key}: {value!r} does not name a migrated PRD source")
        explicit[key] = value
    ambiguities: list[dict[str, Any]] = []
    cache: dict[str, str | None] = {}

    def governing_prd(path: str, trail: tuple[str, ...] = ()) -> str | None:
        if path in cache:
            return cache[path]
        if path in trail:
            ambiguities.append({"record": path, "reason": "parent-cycle"})
            return None
        row = legacy.get(path)
        if row is None:
            ambiguities.append({"record": path, "reason": "dangling-parent"})
            return None
        if row["kind"] == "prd":
            return path
        if path in explicit:
            selected = explicit[path]
            if selected not in owners:
                raise SpecError("ASSIGNMENT_INVALID", f"migration assignment {path}: {selected}")
            cache[path] = selected
            return selected
        choices: set[str] = set()
        for key in ("linked_prd", "linked_architecture", "linked_epic"):
            value = row["metadata"].get(key)
            if not isinstance(value, str) or not value:
                continue
            absolute = Path(os.path.abspath(root / Path(path).parent / value))
            try:
                target = absolute.relative_to(root).as_posix()
            except ValueError as error:
                raise SpecError("SCOPE_DENIED", f"{path}: {key}") from error
            selected = governing_prd(target, (*trail, path))
            if selected:
                choices.add(selected)
        selected = next(iter(choices)) if len(choices) == 1 else None
        if selected is None:
            ambiguities.append({"record": path, "reason": "ambiguous-owner", "choices": sorted(choices)})
        cache[path] = selected
        return selected

    records: list[dict[str, Any]] = []
    shared: list[str] = []
    counters: dict[tuple[str, str], int] = {}
    for path, row in sorted(legacy.items()):
        kind = row["kind"]
        if kind in {"quick-task", "proposal"}:
            shared.append(path)
            continue
        prd = governing_prd(path)
        if prd is None:
            continue
        owner = owners[prd]
        prefix = f"subprojects/{owner}/specs"
        if kind in {"prd", "architecture"}:
            local_id = kind
            destination = f"{prefix}/{kind}.md"
        elif kind in {"epic", "story"}:
            key = (owner, kind)
            counters[key] = counters.get(key, 0) + 1
            local_id = str(counters[key]).zfill(3)
            suffix = re.sub(rf"^{kind}-[0-9]+-?", "", Path(path).stem)
            tail = "-" + suffix if suffix else ""
            folder = "stories" if kind == "story" else "epics"
            destination = f"{prefix}/{folder}/{kind}-{local_id}{tail}.md"
        else:
            local_id = Path(path).stem
            destination = f"{prefix}/research/{Path(path).name}"
        records.append({"source": path, "destination": destination, "kind": kind,
                        "project_id": project_id, "subproject_id": owner, "local_id": local_id,
                        "qualified_id": f"{project_id}/{owner}/{kind}/{local_id}",
                        "before_sha256": row["before_sha256"]})
    inbound_paths = _migration_inbound_paths(root, existing_subprojects)
    # Legacy records are inventoried (and pinned) exactly once from their raw
    # snapshot bytes; the inbound walk covers every other authoritative file.
    inbound: dict[str, bytes] = {path: _read_bytes(root, tuple(Path(path).parts))
                                 for path in inbound_paths if path not in legacy}
    # The active-spec catalog treats every epics/*.md and stories/*.md as
    # legacy; inventory all of them and block unsupported filenames explicitly
    # instead of silently omitting them from the recomputation inputs.
    inputs_unsupported: dict[str, str] = {}
    for folder, kind in (("epics", "epic"), ("stories", "story")):
        directory = root / "specs" / folder
        if not directory.is_dir() or directory.is_symlink():
            continue
        for path in sorted(directory.glob("*.md")):
            relative = path.relative_to(root).as_posix()
            if relative in legacy:
                continue
            inputs_unsupported[relative] = hashlib.sha256(
                _read_bytes(root, tuple(Path(relative).parts))).hexdigest()
            ambiguities.append({
                "record": relative, "reason": "unsupported-filename",
                "detail": (f"legacy {kind} inventory requires {kind}-<number>[-slug].md; "
                           "rename the record before migrating")})
    plan_rewrites = _plan_spec_rewrites(root, project_id, legacy, records, shared, inbound)
    rewrites = plan_rewrites.updates
    for row in records:
        changed = next(item for item in rewrites if item["source"] == row["source"])
        row["after_sha256"] = changed["after_sha256"]
    for row in plan_rewrites.problems:
        if not row["protected"] and row["reason"] in {"ambiguous-link", "unsupported-link-rewrite"}:
            ambiguities.append({"record": row["record"], "reason": row["reason"],
                                "reference": row["reference"],
                                "candidates": row["candidates"]})

    def output_row(path: str, data: bytes, before: str | None) -> dict[str, Any]:
        return {"path": path, "content": data.decode("utf-8"), "before_sha256": before,
                "after_sha256": hashlib.sha256(data).hexdigest()}

    outputs: list[dict[str, Any]] = []
    for update in rewrites:
        original = (legacy[update["source"]]["raw"] if update["source"] in legacy
                    else inbound[update["source"]])
        if update["source"] == update["destination"]:
            if update["content"].encode("utf-8") == original:
                continue  # canonicalization already satisfied; write nothing
            outputs.append(output_row(update["destination"],
                                      update["content"].encode("utf-8"),
                                      update["before_sha256"]))
        else:
            outputs.append(output_row(update["destination"],
                                      update["content"].encode("utf-8"), None))
    new_owners = sorted({row["subproject_id"] for row in records})
    navigation_rows: list[tuple[str, str, str]] = []
    for owner in new_owners:
        owner_specs = [row for row in records if row["subproject_id"] == owner]
        prd_row = next(row for row in owner_specs if row["kind"] == "prd")
        title = legacy[prd_row["source"]]["title"]
        status = str(legacy[prd_row["source"]]["metadata"].get("status", "draft"))
        navigation_rows.append((owner, title, status))
        outputs.append(output_row(f"subprojects/{owner}/SubprojectEntry.md",
                                  _migration_owner_entry_bytes(project_id, owner, title, status),
                                  None))
        outputs.append(output_row(f"subprojects/{owner}/specs/INDEX.md",
                                  _migration_owner_index_bytes(owner, owner_specs, legacy),
                                  None))
    if (shared or records) and "specs/INDEX.md" not in inbound:
        outputs.append(output_row("specs/INDEX.md",
                                  _migration_project_index_bytes(shared, legacy,
                                                                 navigation_rows),
                                  None))
    outputs.sort(key=lambda item: item["path"])
    for item in outputs:
        if item["before_sha256"] is not None:
            continue
        target = root / Path(item["path"])
        try:
            info = os.lstat(target)
        except FileNotFoundError:
            continue
        except OSError as error:
            raise SpecError("SCOPE_DENIED", f"{item['path']}: {error.strerror}") from error
        if stat.S_ISLNK(info.st_mode):
            raise SpecError("SCOPE_DENIED", f"{item['path']}: symlinked migration target")
        ambiguities.append({"record": item["path"], "reason": "target-exists",
                            "path": item["path"]})
    deletions = [{"path": row["source"], "before_sha256": row["before_sha256"]}
                 for row in sorted(records, key=lambda row: row["source"])]
    status_binding = _migration_status_binding(root, entry.metadata)
    inputs: dict[str, str] = {"ProjectEntry.md": entry_sha}
    inputs.update({path: row["before_sha256"] for path, row in legacy.items()})
    inputs.update({path: hashlib.sha256(raw).hexdigest() for path, raw in inbound.items()})
    inputs.update(plan_rewrites.protected_pins)
    inputs.update(_migration_state_inputs(root))
    inputs.update(inputs_unsupported)
    relevant_paths = [*(row["source"] for row in records), *legacy, *inbound,
                      *inputs_unsupported]
    directories = _migration_directories(root, existing_subprojects, relevant_paths)
    result: dict[str, Any] = {"schema": "kosmic.subproject-migration-plan/2",
                              "project_id": project_id, "project_root": str(root),
                              "work_record": work_record, "records": records,
                              "shared_records": shared, "ambiguities": ambiguities,
                              "approval": "required"}
    result["assignments"] = {key: explicit[key] for key in sorted(explicit)}
    result["inputs"] = inputs
    result["directories"] = directories
    result["existing_subprojects"] = existing_subprojects
    result["outputs"] = outputs
    result["deletions"] = deletions
    result["status_binding"] = status_binding
    live_links = sorted({(str(link["source"]), str(link["target"]), str(link.get("fragment", "")))
                         for link in plan_rewrites.live_links})
    result["live_links"] = [{"source": source, "target": target,
                             **({"fragment": fragment} if fragment else {})}
                            for source, target, fragment in live_links]
    result["rewrites"] = rewrites
    result["historical_references"] = plan_rewrites.historical
    result["link_corrections"] = sorted(
        plan_rewrites.corrections,
        key=lambda row: (row["source"], row["reference"], row["replacement"]))
    result["link_problems"] = sorted(
        plan_rewrites.problems,
        key=lambda row: (row["record"], row["reference"], row["reason"]))
    result["expected_outputs"] = sorted({
        "subprojects/{}/SubprojectEntry.md".format(row["subproject_id"])
        for row in records
    } | {
        "subprojects/{}/specs/INDEX.md".format(row["subproject_id"])
        for row in records
    } | {"STATUS.md regeneration at the bound working directory"})
    result["adapter_outputs"] = {"approval": "required",
                                 "note": "installed adapters change only via separately approved install"}
    result["work_record_before_sha256"] = (
        legacy[work_record]["before_sha256"] if work_record in legacy else None)
    result["project_entry_before_sha256"] = entry_sha
    # Fingerprint planning for shared proposals whose planned bytes change.
    if fingerprint_fn is not None:
        for row in result["rewrites"]:
            if not row.get("fingerprint_recheck_required"):
                continue
            before_doc = parse_document_text(legacy[row["source"]]["raw"].decode("utf-8"), Path(row["source"]))
            after_doc = parse_document_text(row["content"], Path(row["destination"]))
            def _compute(document):
                return fingerprint_fn(
                    str(document.metadata.get("result") or ""),
                    str(document.metadata.get("scope") or ""),
                    str(document.metadata.get("target") or ""),
                    (str(document.metadata.get("artifact_role")) if document.metadata.get("artifact_role") else None),
                    [str(x) for x in (document.metadata.get("related_notes") or [])],
                    [str(x) for x in (document.metadata.get("evidence_packs") or [])],
                    document.body,
                    None,
                )
            row["fingerprint_before"] = _compute(before_doc)
            row["fingerprint_after"] = _compute(after_doc)
            changed_fields = sorted(
                key for key in {*before_doc.metadata, *after_doc.metadata}
                if before_doc.metadata.get(key) != after_doc.metadata.get(key)
            )
            path_fields = {"linked_prd", "linked_architecture", "linked_epic",
                           "related_specs", "related_notes", "evidence_packs", "evidence",
                           "review_record", "acceptance_evidence",
                           "depends_on", "cross_subproject_dependencies",
                           "url", "sources"}
            row["classification"] = ("mechanical-path-mapping"
                                     if set(changed_fields) <= path_fields | {"project_id", "subproject_id", "record_kind", "local_id"}
                                     and re.sub(r"\(([^)]*\.md[^)]*)\)", "(X)", before_doc.body) == re.sub(r"\(([^)]*\.md[^)]*)\)", "(X)", after_doc.body)
                                     else "behavioral-review-required")
    # Referenced evidence payloads stay immutable; they are receipt-mapped.
    evidence_refs: dict[str, str] = {}
    for row in result["rewrites"]:
        for match in re.finditer(r"\((evidence/[^)#]+)\)", row["content"]):
            evidence_refs.setdefault(match.group(1), row["source"])
    result["evidence_inventory"] = [
        {"path": path, "referenced_by": source,
         "disposition": "historical-immutable"}
        for path, source in sorted(evidence_refs.items())
    ]
    destinations: dict[str, str] = {}
    for row in records:
        if row["destination"] in destinations:
            ambiguities.append({"record": row["source"], "reason": "destination-collision",
                                "other": destinations[row["destination"]]})
        destinations[row["destination"]] = row["source"]
    for source, expected in sorted(inputs.items()):
        current = hashlib.sha256(_read_bytes(root, tuple(Path(source).parts))).hexdigest()
        if current != expected:
            raise SpecError("MIGRATION_INPUT_DRIFT", source)
    # The reviewed plan authenticates the exact STATUS candidate: render it
    # from the staged inputs+outputs/deletions view with the existing CLI so
    # receipt verification compares against planned bytes, never re-rendered
    # state that later lifecycle changes would legitimately alter.
    if status_binding["disposition"] == "bound":
        status_bytes = _planned_status_bytes(
            root, str(status_binding["head"]), Path(status_binding["path"]).parent,
            inputs, outputs, deletions)
        if status_bytes is None:
            ambiguities.append({"record": "STATUS.md", "reason": "staged-catalog-invalid",
                                "detail": "staged candidate view failed SpecCatalog validation"})
        else:
            status_binding["content"] = status_bytes.decode("utf-8")
            status_binding["after_sha256"] = hashlib.sha256(status_bytes).hexdigest()
    result["digest"] = hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return result


@dataclass
class _RewriteOutcome:
    """Everything one planning pass derives from its pinned input snapshot."""
    updates: list[dict[str, Any]]
    historical: list[dict[str, str]]
    live_links: list[dict[str, Any]]
    corrections: list[dict[str, Any]]
    problems: list[dict[str, Any]]
    protected_pins: dict[str, str]


def _inline_destination_parts(raw: str) -> tuple[str, str, str] | None:
    """Split one parenthesized link body into (head, destination, tail).

    head/tail keep angle brackets, surrounding whitespace and title bytes
    exactly as written. None marks syntax the pipeline must not touch: an
    unterminated angle form, an empty destination or a remainder that is not
    a title.
    """
    if raw.startswith("<"):
        close = raw.find(">")
        if close < 0:
            return None
        return "<", raw[1:close], ">" + raw[close + 1:]
    stripped = raw.lstrip(" \t")
    if not stripped:
        return None
    lead = len(raw) - len(stripped)
    for index, char in enumerate(stripped):
        if char in " \t":
            tail = raw[lead + index:]
            if not _MD_TITLE.match(tail.strip()):
                return None
            return raw[:lead], stripped[:index], tail
    return raw[:lead], stripped, ""


def _rewrite_metadata_links(source: str, destination: str, metadata: Mapping[str, Any],
                            audit: _LinkAudit, *, migrated: bool,
                            protected: bool = False) -> tuple[dict[str, Any], dict[str, str]]:
    """Rewrite every path-bearing scalar leaf in structured frontmatter.

    Recursing dicts and lists keeps nested values (e.g. ``sources[].url``)
    intact apart from the rewritten link scalars. Returns the new metadata and
    the old->new replacements keyed by leaf key name for byte-surgical inbound
    headers; protected scans rewrite nothing and collect no replacements.
    Callers drop recorded rows for scalars the text rewrite could not place,
    so no correction is ever reported without an emitted change.
    """
    replacements: dict[str, dict[str, str]] = {}

    def walk(node: Any, key: str | None) -> Any:
        if isinstance(node, Mapping):
            return {str(inner_key): walk(value, str(inner_key))
                    for inner_key, value in node.items()}
        if isinstance(node, list):
            return [walk(item, key) for item in node]
        if isinstance(node, str) and key is not None and _is_link_key(key) and node:
            rewritten = audit.rewrite_metadata_value(source, destination, key, node,
                                                     protected=protected)
            if rewritten != node and not protected:
                replacements.setdefault(key, {})[node] = rewritten
            return rewritten
        return node

    return walk(metadata, None), replacements


def _plan_spec_rewrites(root: Path, project_id: str, legacy: Mapping[str, dict[str, Any]],
                        records: list[dict[str, Any]], shared: list[str],
                        inbound: Mapping[str, bytes]) -> _RewriteOutcome:
    """Produce candidate bytes from the snapshot; never publishes them.

    One mapper covers migrated records, shared records canonicalized in place
    and inbound Project documents (root Markdown, notes, mathdocs, specs
    indexes, existing owner entries/specs); the protected trees (evidence,
    logs, generated skills) are scanned and reported but never rewritten.
    Returns candidate updates, historical references, live links, link
    corrections, link problems and pinned protected inputs.
    """
    mapping = {row["source"]: row["destination"] for row in records}
    by_source = {row["source"]: row for row in records}
    owner_rows: list[tuple[str, str, str]] = []
    for owner in sorted({row["subproject_id"] for row in records}):
        prd = next(row for row in records
                   if row["subproject_id"] == owner and row["kind"] == "prd")
        owner_rows.append((owner, legacy[prd["source"]]["title"],
                           str(legacy[prd["source"]]["metadata"].get("status", "draft"))))
    authoritative_view = frozenset({*mapping.values(), *shared, *inbound,
                      *(f"subprojects/{owner}/SubprojectEntry.md"
                        for owner in {row["subproject_id"] for row in records}),
                      *(f"subprojects/{owner}/specs/INDEX.md"
                        for owner in {row["subproject_id"] for row in records})}
                     - set(mapping))
    protected_paths = _migration_protected_paths(root)
    view = authoritative_view | frozenset(path.relative_to(root).as_posix()
                                         for path in protected_paths)
    alias_keys: set[str] = set()
    for source in mapping:
        name = Path(source).name
        alias_keys.update({name, name[:-3]} if name.endswith(".md") else {name})
    audit = _LinkAudit(root=root, mapping=mapping, view=view,
                       filename_index=_link_filename_index(authoritative_view, mapping),
                       alias_keys=frozenset(alias_keys), legacy=legacy)

    def dependency_target(source: str, item: str) -> str | None:
        """Project-relative record an existing depends_on entry names."""
        path_part = _split_destination(item)[0]
        if not path_part.strip() or _external_scheme(path_part):
            return None
        decoded = urllib.parse.unquote(path_part)
        if decoded in by_source:
            return decoded
        old_relative = _decoded_link_path(root, source, path_part)
        return old_relative if old_relative in by_source else None

    def dependency_updates(source: str, destination: str, metadata: Mapping[str, Any],
                           owner: str | None) -> dict[str, list[str]]:
        updates: dict[str, list[str]] = {}
        foreign_ids: list[str] = []
        for key in ("depends_on", "cross_subproject_dependencies"):
            if key not in metadata:
                continue
            values = metadata[key]
            if not isinstance(values, list) or any(not isinstance(item, str) or not item for item in values):
                raise SpecError("DEPENDENCY_INVALID", f"{source}: {key} must be a string list")
            changed: list[str] = []
            for item in values:
                old_relative = dependency_target(source, item)
                if old_relative is None:
                    changed.append(item)
                    continue
                moved = by_source[old_relative]
                if moved["subproject_id"] != owner:
                    changed.append(moved["qualified_id"])
                    if key == "depends_on":
                        foreign_ids.append(moved["qualified_id"])
                elif key == "depends_on":
                    path_part, query_part, fragment_part = _split_destination(item)
                    changed.append(_compose_destination(root, destination,
                                                        mapping[old_relative],
                                                        query_part, fragment_part))
            updates[key] = changed
        if foreign_ids:
            declared = updates.get("cross_subproject_dependencies", [])
            updates["cross_subproject_dependencies"] = list(dict.fromkeys([*declared, *foreign_ids]))
        return updates

    def rewrite_body(source: str, destination: str, body: str, *,
                     migrated: bool, protected: bool = False) -> str:
        def destination_bytes(raw: str, value: str, head: str, tail: str,
                              new: str, outcome: str) -> str:
            if outcome in ("valid", "outside-view") and not migrated:
                return raw  # staying documents keep their exact bytes
            if outcome == "outside-view":
                path_part, query_part, fragment_part = _split_destination(value)
                old_relative = _decoded_link_path(root, source, path_part)
                if old_relative is None:
                    return raw
                new = _compose_destination(root, destination, old_relative,
                                           query_part, fragment_part)
            return f"{head}{new}{tail}"

        def rewrite_destination(raw: str) -> str:
            parts = _inline_destination_parts(raw)
            if parts is None:
                return raw
            head, value, tail = parts
            new, outcome = audit.rewrite_text(source, destination, value,
                                              protected=protected)
            return destination_bytes(raw, value, head, tail, new, outcome)

        def inline(match: re.Match[str]) -> str:
            return f"{match.group(1)}[{match.group(2)}]({rewrite_destination(match.group(3))})"

        def definition(match: re.Match[str]) -> str:
            token = match.group(4)
            angle = token.startswith("<") and token.endswith(">") and len(token) >= 2
            head, value, tail = ("<", token[1:-1], ">") if angle else ("", token, "")
            new, outcome = audit.rewrite_text(source, destination, value,
                                              protected=protected)
            rewritten = destination_bytes(token, value, head, tail, new, outcome)
            return (f"{match.group(1)}[{match.group(2)}]:{match.group(3)}"
                    f"{rewritten}{match.group(5) or ''}")

        def html(match: re.Match[str]) -> str:
            token = match.group(1)
            quote_char = token[0] if token[0] in "\"'" else ""
            value = token[1:-1] if quote_char else token
            new, outcome = audit.rewrite_text(source, destination, value,
                                              protected=protected)
            rewritten = destination_bytes(value, value, "", "", new, outcome)
            if quote_char:
                rewritten = f"{quote_char}{rewritten}{quote_char}"
            elif not rewritten or " " in rewritten:
                rewritten = f'"{rewritten}"'
            return f"{match.group(0)[:-len(token)]}{rewritten}"

        def wiki(match: re.Match[str]) -> str:
            head_part, pipe, alias = match.group(2).partition("|")
            if pipe and head_part.endswith("\\"):
                head_part = head_part[:-1]
                pipe = "\\|"
            path_part, hash_separator, fragment = head_part.partition("#")
            if not path_part.strip():
                return match.group(0)
            new, outcome = audit.rewrite_text(source, destination, head_part,
                                              protected=protected,
                                              project_relative_first=True)
            if outcome not in ("mapped", "repaired") and not (outcome == "valid" and migrated):
                return match.group(0)  # staying, external and reported refs stay
            target = os.path.normpath(str(Path(destination).parent / _split_destination(new)[0]))
            rebuilt = f"{target}{hash_separator}{fragment}{pipe}{alias}"
            return f"{match.group(1)}[[{rebuilt}]]"

        rendered: list[str] = []
        in_fence = False
        for line in body.splitlines(keepends=True):
            if re.match(r"\s{0,3}(?:```|~~~)", line):
                in_fence = not in_fence
                rendered.append(line)
                continue
            if in_fence:
                rendered.append(line)
                continue
            segments = _INLINE_CODE_SPAN.split(line)
            for index, segment in enumerate(segments):
                if index % 2:
                    continue
                segment = _MD_HTML_REFERENCE.sub(html, segment)
                segment = _MD_WIKI_LINK.sub(wiki, segment)
                segment = _MD_INLINE_LINK.sub(inline, segment)
                if index == 0:
                    segment = _MD_DEFINITION.sub(definition, segment)
                segments[index] = segment
            rendered.append("".join(segments))
        return "".join(rendered)

    updates: list[dict[str, Any]] = []
    for source in sorted({*mapping, *shared, *inbound}):
        destination = mapping.get(source, source)
        row = by_source.get(source)
        kind = legacy[source]["kind"] if source in legacy else "inbound"
        raw = legacy[source]["raw"] if source in legacy else inbound[source]
        raw_text = raw.decode("utf-8")
        if row is None and kind == "inbound":
            # Preserve inbound bytes exactly except corrected path-bearing values.
            metadata: dict[str, Any] = {}
            if raw_text.startswith(("---\n", "---\r\n")):
                try:
                    metadata = parse_document_text(raw_text, Path(source)).metadata
                except LibraryError as error:
                    raise SpecError("SPEC_INVALID", f"{source}: {error}") from error
                frontmatter = re.match(r"\A---\r?\n(?:.*?\r?\n)?---(?:\r?\n|\Z)", raw_text, re.S)
                if frontmatter is None:
                    raise SpecError("SPEC_INVALID", f"{source}: unterminated frontmatter")
                head, rest = frontmatter.group(0), raw_text[frontmatter.end():]
            else:
                head, rest = "", raw_text
            metadata, replacements = _rewrite_metadata_links(
                source, destination, metadata, audit, migrated=False)
            dependency_owner = Path(source).parts[1] if source.startswith("subprojects/") else None
            dependencies = dependency_updates(source, destination, metadata, dependency_owner)
            for old, new in zip(metadata.get("depends_on", []), dependencies.get("depends_on", [])):
                if old != new:
                    replacements.setdefault("depends_on", {})[old] = new
            head, applied = _rewrite_frontmatter_scalars(head, replacements)
            audit.prune_unemitted(source, replacements, applied)
            cross = dependencies.get("cross_subproject_dependencies")
            if cross is not None and cross != metadata.get("cross_subproject_dependencies"):
                head = _set_frontmatter_list(head, "cross_subproject_dependencies", cross)
            content = head + rewrite_body(source, destination, rest, migrated=False)
            if source == "specs/INDEX.md" and owner_rows:
                content = _apply_owner_navigation(content, owner_rows)
                for owner, _title, _status in owner_rows:
                    audit.record_live_link("specs/INDEX.md",
                                           f"subprojects/{owner}/specs/INDEX.md", "")
        else:
            document = parse_document_text(raw_text, Path(source))
            metadata = dict(document.metadata)
            # Immutable identity guard (FR-M04): never remint a record that
            # already declares a different Project or a conflicting owner;
            # missing/empty identity is canonicalized normally.
            declared_project = metadata.get("project_id")
            if isinstance(declared_project, str) and declared_project and declared_project != project_id:
                raise SpecError("OWNER_MISMATCH",
                                f"{source}: legacy project_id {declared_project!r} "
                                f"does not match ProjectEntry project_id {project_id!r}")
            expected_owner = row["subproject_id"] if row else None
            declared_owner = metadata.get("subproject_id")
            if isinstance(declared_owner, str) and declared_owner not in ("", "null") \
                    and declared_owner != expected_owner:
                raise SpecError("OWNER_MISMATCH",
                                f"{source}: legacy subproject_id {declared_owner!r} conflicts "
                                f"with proposed owner {expected_owner!r}")
            existing_local_id = metadata.get("local_id")
            local_id = row["local_id"] if row else (
                existing_local_id
                if isinstance(existing_local_id, str) and SLUG.fullmatch(existing_local_id)
                else Path(source).stem)
            metadata.update({"project_id": project_id,
                             "subproject_id": row["subproject_id"] if row else None,
                             "record_kind": kind,
                             "local_id": local_id})
            metadata, _replacements = _rewrite_metadata_links(
                source, destination, metadata, audit, migrated=True)
            metadata.update(dependency_updates(
                source, destination, metadata, row["subproject_id"] if row else None))
            if kind == "research" and row and not metadata.get("linked_prd"):
                metadata["linked_prd"] = os.path.relpath(root / f"subprojects/{row['subproject_id']}/specs/prd.md",
                                                        root / Path(destination).parent).replace(os.sep, "/")
            body = rewrite_body(source, destination, document.body, migrated=True)
            content = (_frontmatter(metadata).decode("utf-8") + body)
        updates.append({"source": source, "destination": destination,
                        "before_sha256": hashlib.sha256(raw).hexdigest(),
                        "after_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
                        "content": content})
        if kind == "proposal" and content != raw_text:
            updates[-1]["fingerprint_recheck_required"] = True

    # Protected trees are scanned and pinned for drift, never rewritten.
    protected_pins: dict[str, str] = {}
    for path in protected_paths:
        relative = path.relative_to(root).as_posix()
        raw = _read_bytes(root, tuple(Path(relative).parts))
        protected_pins[relative] = hashlib.sha256(raw).hexdigest()
        raw_text = raw.decode("utf-8")
        frontmatter = re.match(r"\A---\r?\n(?:.*?\r?\n)?---(?:\r?\n|\Z)", raw_text, re.S)
        if frontmatter is not None:
            try:
                metadata = parse_document_text(raw_text, Path(relative)).metadata
            except LibraryError:
                audit.report_problem(relative, "", "unparsable-document", [],
                                     protected=True)
                continue
            if metadata:
                _rewrite_metadata_links(relative, relative, metadata, audit,
                                        migrated=False, protected=True)
        rewrite_body(relative, relative,
                     raw_text[frontmatter.end():] if frontmatter else raw_text,
                     migrated=False, protected=True)
    protected_pins.update(audit.target_pins)
    return _RewriteOutcome(updates=updates, historical=audit.historical,
                           live_links=audit.live_links, corrections=audit.corrections,
                           problems=audit.problems, protected_pins=protected_pins)


# --- Story069: shared knowledge roots and owner write boundaries ---

SHARED_ROOTS = ("notes", "mathdocs", "skills")


@dataclass(frozen=True)
class WriteScope:
    """Declares whether a path falls inside the requested writer's authority."""
    path: Path
    owner: str | None
    boundary: str  # "shared" (Project-root authority) | "subproject" | "foreign"
    allowed: bool
    detail: str


def shared_root_conflicts(project_root: str | os.PathLike[str]) -> tuple[Path, ...]:
    """Return subproject-local copies of the Project-root-only knowledge roots."""
    root = Path(project_root).expanduser().resolve()
    directory = root / "subprojects"
    if directory.is_symlink() or (directory.exists() and not directory.is_dir()):
        raise SpecError("SCOPE_DENIED", str(directory))
    if not directory.exists():
        return ()
    conflicts: list[Path] = []
    for base in sorted(directory.iterdir()):
        if base.is_symlink() or not base.is_dir():
            raise SpecError("SCOPE_DENIED", str(base))
        for name in SHARED_ROOTS:
            candidate = base / name
            if candidate.is_symlink() or candidate.exists():
                conflicts.append(candidate)
    return tuple(conflicts)


def validate_shared_roots(project_root: str | os.PathLike[str]) -> None:
    """Reject per-subproject notes/, mathdocs/, or skills/ trees (AD-SW1/SW3)."""
    conflicts = shared_root_conflicts(project_root)
    if conflicts:
        raise SpecError("SHARED_ROOT_INVALID", ", ".join(item.as_posix() for item in conflicts))


def validate_project_specs(project_root: str | os.PathLike[str]) -> SpecCatalog:
    """Owner-aware validation of every spec hierarchy through the one catalog."""
    catalog = SpecCatalog(Path(project_root).expanduser().resolve())
    catalog.validate()
    return catalog


def _contained_parts(root: Path, target: Path) -> tuple[str, ...]:
    """Verify target stays inside root without symlink escape; return its parts."""
    if target == root:
        raise SpecError("SCOPE_DENIED", str(target))
    try:
        parts = target.relative_to(root).parts
    except ValueError as error:
        raise SpecError("SCOPE_DENIED", str(target)) from error
    current = root
    for part in parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise SpecError("SCOPE_DENIED", str(current))
    return parts


def classify_write_scope(project_root: str | os.PathLike[str], path: str | os.PathLike[str],
                         *, owner: str | None = None) -> WriteScope:
    """Classify a prospective write path against the declared owner's authority.

    A subproject may write only inside ``subprojects/{owner}/``; shared Project
    roots (notes/, mathdocs/, skills/) and Project-level specs need Project
    authority (owner=None). Cross-subproject reads stay allowed; writes into a
    foreign subproject are never allowed here (Stories 073/074 own expansion).
    """
    root = Path(project_root).expanduser().resolve()
    target = Path(os.path.abspath(Path(path).expanduser()))
    parts = _contained_parts(root, target)
    if owner is not None:
        base = root / "subprojects" / owner
        if base.is_symlink() or not (base / "SubprojectEntry.md").is_file():
            raise SpecError("OWNER_MISMATCH", owner)
    if parts[0] == "subprojects":
        if len(parts) < 2 or not SLUG.fullmatch(parts[1]):
            raise SpecError("OWNER_MISMATCH", str(target))
        if owner is not None and parts[1] == owner:
            return WriteScope(target, owner, "subproject", True,
                              f"inside the declared owner scope subprojects/{owner}/")
        return WriteScope(target, owner, "foreign", False,
                          f"subprojects/{parts[1]}/ is owned by another feature")
    return WriteScope(target, owner, "shared", owner is None,
                      "Project-root shared knowledge/specs need Project authority"
                      if owner is not None else "Project-root authority")


def _checked_leaf_parts(root: Path, target: Path, parts: tuple[str, ...],
                        *, leaf_must_exist: bool) -> None:
    """Descriptor-based final-component validation (STD-069-1).

    Walks the containment chain without following leaf-level symlinks
    (``O_NOFOLLOW``), then opens the final component with
    ``O_NOFOLLOW | O_NONBLOCK`` and requires it to be a regular file or a
    directory. Leaf symlinks and special files raise ``SCOPE_DENIED``.
    """
    if not parts:
        return
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for part in parts[:-1]:
            try:
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            except FileNotFoundError as error:
                if leaf_must_exist:
                    raise SpecError("SCOPE_DENIED", str(target)) from error
                return  # parents not created yet; nothing to validate
            os.close(fd)
            fd = next_fd
        try:
            leaf_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        except FileNotFoundError as error:
            return  # absent leaves are the writer's business, not a scope failure
        except OSError as error:
            raise SpecError("SCOPE_DENIED", f"{target}: {error.strerror}") from error
        try:
            mode = os.fstat(leaf_fd).st_mode
        finally:
            os.close(leaf_fd)
        if not (stat.S_ISREG(mode) or stat.S_ISDIR(mode)):
            raise SpecError("SCOPE_DENIED", str(target))
    except OSError as error:
        raise SpecError("SCOPE_DENIED", f"{target}: {error.strerror}") from error
    finally:
        os.close(fd)


def check_write_scope(project_root: str | os.PathLike[str], path: str | os.PathLike[str],
                      *, owner: str | None = None) -> WriteScope:
    """Raise WRITE_SCOPE_DENIED unless path is inside the declared writer's authority."""
    root = Path(project_root).expanduser().resolve()
    target = Path(os.path.abspath(Path(path).expanduser()))
    scope = classify_write_scope(root, target, owner=owner)
    if not scope.allowed:
        raise SpecError("WRITE_SCOPE_DENIED", scope.detail)
    _checked_leaf_parts(root, target, target.relative_to(root).parts, leaf_must_exist=False)
    return scope


def check_read_scope(project_root: str | os.PathLike[str],
                     path: str | os.PathLike[str]) -> Path:
    """Cross-subproject reads are allowed; containment, symlinks, and leaf type are checked."""
    root = Path(project_root).expanduser().resolve()
    target = Path(os.path.abspath(Path(path).expanduser()))
    parts = _contained_parts(root, target)
    _checked_leaf_parts(root, target, parts, leaf_must_exist=True)
    return target
