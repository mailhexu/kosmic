"""Optional, explicitly scoped historical inspection for one Project (Story 001).

``history_integrity`` selects exact canonical Project-relative spec records
whose retrospective integrity — completion receipts, curated input-manifest
pins, and recorded proposal fingerprints — is reported read-only instead of
audited. Warn mode (the default) resolves the selection before the
reporting settlement calls it controls, excludes selected records from
those calls, and reports each selected record's claimed lifecycle as
``unverified — not audited``. Configured ``strict`` mode additionally runs
the narrow integrity readers over selected records — receipt integrity for
claimed ``done`` records, curated-manifest pins and recorded-fingerprint
consistency for proposal records, mirroring the existing rules for each
claimed status — and fails validation on actual missing or mismatched
proof. Neither mode ever rewrites lifecycle, receipt, or pin bytes, and no
diagnostic claims verified completion.

Strict ``SpecCatalog`` construction is untouched: the operational
constructors keep settling every receipt with no skip flag, and no function
here returns or accepts a catalog-shaped authority object — selection is
carried as plain ``HistorySubject`` reports. Bootstrap-flat Projects (the
sanctioned pre-migration state) are supported: on ``MIGRATION_REQUIRED`` the
selection resolves against the flat record discovery directly, using the
Project-relative path as the record identity. Malformed values, unknown
keys, unknown or stale paths, duplicates, noncanonical or uncontained paths,
and wrong-owner references are hard :class:`HistoryConfigError` failures
that the CLI adapts to its own error type at narrow boundaries; this module
imports the CLI only lazily and never at module initialization.
"""
from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    from .kosmic_dreams import StructuralRecordFacts, structural_receipt_pendencies
    from .kosmic_specs import (
        SpecError,
        SpecRef,
        _SHARED_ONLY,
        _SpecStructure,
        _collect_spec_structure,
        read_document,
    )
except ImportError:
    from kosmic_dreams import StructuralRecordFacts, structural_receipt_pendencies
    from kosmic_specs import (
        SpecError,
        SpecRef,
        _SHARED_ONLY,
        _SpecStructure,
        _collect_spec_structure,
        read_document,
    )

if TYPE_CHECKING:
    from .kosmic_project_skills import Project

HISTORY_MODES = ("warn", "strict")
HISTORY_POLICY_KEYS = frozenset({"mode", "records"})


class HistoryConfigError(RuntimeError):
    """Hard, specific historical-configuration failure; CLI adapts to its error."""


def _config_error(message: str) -> None:
    raise HistoryConfigError(message)


@dataclass(frozen=True)
class HistoryPolicy:
    """Immutable optional Project policy: audit mode plus exact record scope."""

    mode: str = "warn"
    records: tuple[str, ...] = ()


def parse_history_policy(value: Any) -> HistoryPolicy | None:
    """Parse ProjectEntry ``history_integrity``; None when absent or empty.

    An absent policy or an empty record list preserves current behavior
    exactly. Malformed values are hard configuration errors: non-mapping
    values, unknown keys, invalid modes, non-string or noncanonical record
    paths, and duplicates are rejected with a specific diagnostic; scope is
    never silently dropped or broadened.
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if not isinstance(value, Mapping):
        _config_error(
            "history_integrity must be a mapping with optional 'mode' "
            "(warn|strict) and 'records'"
        )
    unknown = sorted(str(key) for key in value.keys() if key not in HISTORY_POLICY_KEYS)
    if unknown:
        _config_error(f"history_integrity has unknown keys: {', '.join(unknown)}")
    if "mode" in value:
        mode = value["mode"]
        if mode not in HISTORY_MODES:
            _config_error(
                f"history_integrity mode must be one of warn, strict: {mode!r}"
            )
    else:
        mode = "warn"
    records: list[str] = []
    if "records" in value:
        raw = value["records"]
        if not isinstance(raw, (list, tuple)):
            _config_error(
                "history_integrity records must be a list of canonical "
                "Project-relative record paths"
            )
        seen: set[str] = set()
        for item in raw:
            if not isinstance(item, str) or not item or item != item.strip():
                _config_error(
                    "history_integrity record paths must be exact non-empty "
                    f"strings: {item!r}"
                )
            if item.startswith("/") or Path(item).is_absolute():
                _config_error(
                    f"history_integrity record path must be Project-relative: {item}"
                )
            parts = Path(item).parts
            if (not parts or item != "/".join(parts)
                    or any(part in {"", ".", ".."} for part in parts)):
                _config_error(
                    f"history_integrity record path is not canonical: {item}"
                )
            if not item.startswith(("specs/", "subprojects/")):
                _config_error(
                    "history_integrity record path must name a spec record "
                    f"(specs/... or subprojects/<owner>/specs/...): {item}"
                )
            if item in seen:
                _config_error(f"history_integrity records duplicates a path: {item}")
            seen.add(item)
            records.append(item)
    if not records:
        return None
    return HistoryPolicy(mode=mode, records=tuple(records))


@dataclass(frozen=True)
class HistorySubject:
    """One selected record's claimed facts; retrospective proof is not read."""

    path: str
    qualified_id: str
    kind: str
    owner: str | None
    title: str
    claimed_status: str


@dataclass(frozen=True)
class HistoryReport:
    """Display rows and diagnostics only; never an operational object."""

    policy: HistoryPolicy
    subjects: tuple[HistorySubject, ...]
    diagnostics: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()


def _structure_subjects(structure: _SpecStructure,
                        policy: HistoryPolicy) -> tuple[HistorySubject, ...]:
    """Resolve every configured path against the structural inventory."""
    subjects: list[HistorySubject] = []
    for record in policy.records:
        ref: SpecRef | None = structure.by_path.get(structure.root / record)
        if ref is None:
            _config_error(
                f"history_integrity record is unknown or stale: {record}; configure "
                "the exact canonical Project-relative path of an existing spec record"
            )
        subjects.append(HistorySubject(
            path=record,
            qualified_id=ref.qualified_id,
            kind=ref.kind,
            owner=ref.subproject_id,
            title=ref.title,
            claimed_status=ref.status,
        ))
    return tuple(subjects)


def _flat_record_kind(relative: Path) -> str | None:
    """Bootstrap-flat record classification mirroring the flat STATUS scan."""
    parts = relative.parts
    if not parts or parts[0] != "specs":
        return None
    tail = parts[1:]
    if not tail:
        return None
    name = tail[-1]
    if len(tail) == 1:
        if name == "index.md":
            return None
        if name.startswith("prd"):
            return "prd"
        if name.startswith("architecture"):
            return "architecture"
        return None
    if len(tail) == 2:
        directory = tail[0]
        if directory == "epics" and re.fullmatch(r"epic-.+\.md", name):
            return "epic"
        if directory == "stories" and re.fullmatch(r"story-.+\.md", name):
            return "story"
        if directory == "quick-tasks" and name != "index.md":
            return "quick-task"
        if directory == "skill-proposals" and name != "index.md":
            return "proposal"
    return None


def _flat_entries(project_root: Path,
                  policy: HistoryPolicy) -> list[tuple[HistorySubject, Mapping[str, Any]]]:
    """Resolve configured paths in the sanctioned bootstrap-flat state.

    The Project-relative path is the record identity, matching the flat
    STATUS rows and the flat-bootstrap receipt convention. Discovery mirrors
    the flat STATUS scan exactly; reads are no-follow and fail-closed. Each
    entry pairs the report subject with the frontmatter metadata facts the
    narrow receipt-integrity reader needs for a strict selected audit.
    """
    root = Path(project_root).expanduser().resolve()
    entries: list[tuple[HistorySubject, Mapping[str, Any]]] = []
    for record in policy.records:
        candidate = (root / record).resolve()
        try:
            relative = candidate.relative_to(root)
        except ValueError:
            _config_error(f"history_integrity record path escapes the Project: {record}")
        kind = _flat_record_kind(relative)
        if kind is None or not candidate.is_file():
            _config_error(
                f"history_integrity record is unknown or stale: {record}; configure "
                "the exact canonical Project-relative path of an existing spec record"
            )
        document = read_document(root, root / record)
        title = next(
            (line[2:].strip() for line in document.body.splitlines()
             if line.startswith("# ")),
            Path(record).stem,
        )
        entries.append((
            HistorySubject(
                path=record,
                qualified_id=record,
                kind=kind,
                owner=None,
                title=title,
                claimed_status=str(document.metadata.get("status") or "?"),
            ),
            document.metadata,
        ))
    return entries


def _flat_subjects(project_root: Path,
                   policy: HistoryPolicy) -> tuple[HistorySubject, ...]:
    return tuple(subject for subject, _ in _flat_entries(project_root, policy))


def selection(project_root: Path, policy: HistoryPolicy) -> tuple[HistorySubject, ...]:
    """Configured subjects from current bytes, before any retrospective read.

    Owner-aware Projects resolve through the shared structural scanner;
    sanctioned bootstrap-flat Projects resolve through the flat record
    discovery. Unknown or stale configured paths fail with their own
    specific configuration error; catalog scan defects surface as
    :class:`SpecError` exactly like strict catalog enumeration, so degraded
    bounded fallbacks keep their trigger semantics (the validate entry
    point adapts them to configuration errors at its own boundary).
    """
    try:
        structure = _collect_spec_structure(project_root)
    except SpecError as error:
        if error.code == "MIGRATION_REQUIRED":
            return _flat_subjects(project_root, policy)
        raise
    return _structure_subjects(structure, policy)


def structure_subjects(structure: _SpecStructure,
                       policy: HistoryPolicy) -> tuple[HistorySubject, ...]:
    """Configured subjects within one structural snapshot (selection only)."""
    return _structure_subjects(structure, policy)


def flat_selection(project_root: Path, policy: HistoryPolicy) -> tuple[HistorySubject, ...]:
    """Configured subjects in the sanctioned bootstrap-flat state."""
    return _flat_subjects(project_root, policy)


def bounded_policy(policy: HistoryPolicy, owner: str | None) -> HistoryPolicy:
    """Restrict configured paths to a bounded reporting scope before lookup.

    Shared ``specs/`` records are in every bounded view. A subproject view
    additionally includes only that owner's ``subprojects/<owner>/specs/``
    tree; a shared-only view excludes all owner paths. Filtering by canonical
    path scope before resolving identities avoids discovering unrelated
    owners and still leaves missing paths inside the selected scope as hard
    configuration errors during structural subject lookup.
    """
    prefix = f"subprojects/{owner}/specs/" if owner is not None else None
    records = tuple(
        record for record in policy.records
        if record.startswith("specs/")
        or (prefix is not None and record.startswith(prefix))
    )
    return HistoryPolicy(mode=policy.mode, records=records)


def bounded_subjects(project_root: Path, policy: HistoryPolicy,
                     owner: str | None) -> tuple[HistorySubject, ...]:
    """Resolve only the configured subjects in one bounded scope."""
    scoped = bounded_policy(policy, owner)
    try:
        structure = _collect_spec_structure(
            project_root, _SHARED_ONLY if owner is None else owner)
    except SpecError as error:
        if error.code == "MIGRATION_REQUIRED":
            return _flat_subjects(project_root, scoped)
        raise
    return _structure_subjects(structure, scoped)


def bounded_selection(project_root: Path, policy: HistoryPolicy,
                      owner: str | None) -> frozenset[str]:
    """Selected identities within a bounded owner scope's intersection.

    Configured paths outside the bounded scope are excluded before lookup;
    missing configured records within the scope remain hard errors.
    """
    return frozenset(
        subject.qualified_id
        for subject in bounded_subjects(project_root, policy, owner)
    )


def selected_proposal_paths(project: "Project") -> frozenset[Path]:
    """Absolute paths of selected skill proposals; empty when unconfigured.

    The strict proposal scan skips exactly these paths, so warn mode never
    invokes the operational proposal loader for a selected record; every
    other proposal keeps its existing strict loader semantics.
    """
    policy = project.history_integrity
    if policy is None or not policy.records:
        return frozenset()
    root = Path(project.root).expanduser().resolve()
    return frozenset(
        root / subject.path
        for subject in selection(project.root, policy)
        if subject.kind == "proposal"
    )


def resolve_history_policy(project: "Project") -> None:
    """Fail fast on an unresolvable configured scope; no-op when unconfigured.

    Validate's own configuration boundary: catalog scan defects on the
    configured Project surface here as hard configuration errors carrying
    the underlying identity/containment diagnostic, so the command exits
    cleanly before any other check.
    """
    policy = project.history_integrity
    if policy is None or not policy.records:
        return
    try:
        selection(project.root, policy)
    except SpecError as error:
        _config_error(f"history_integrity scope cannot be resolved: {error}")


UNAUDITED_MARKER = "unverified — not audited"
AUDITED_CLEAN_MARKER = "strict audit clean"
AUDITED_FAILURE_MARKER = "strict audit failure"


def _require_proposal_facts(metadata: Mapping[str, Any]) -> None:
    """Raise the typed integrity error when declared proposal facts are missing.

    The existing proposal contract indexes these frontmatter facts
    unconditionally; the narrow audit pre-validates exactly that set so the
    manifest/fingerprint readers never trip a foreign exception identity on
    malformed records. No other schema is required or invented.
    """
    try:
        from .kosmic_project_skills import CuratedManifestIntegrityError
    except ImportError:
        from kosmic_project_skills import CuratedManifestIntegrityError
    missing = sorted(
        key for key in ("decision", "fingerprint", "related_notes", "result", "scope", "target")
        if key not in metadata
    )
    if missing:
        raise CuratedManifestIntegrityError(
            "declared proposal facts are incomplete: missing " + ", ".join(missing)
        )


def _proposal_pin_outcomes(root: Path,
                           subjects: list[HistorySubject]) -> tuple[dict[str, list[str]], set[str]]:
    """Narrow retrospective integrity read for selected proposal records.

    Known existing rules only: the curated input-manifest pins (via the
    neutral shared manifest reader, historical semantics mirroring the
    record's claimed status) and the recorded fingerprint consistency where
    the existing rules require it (decided proposals). Never invokes the
    operational proposal loader, rejection-equivalence, admission, or
    target-eligibility logic. Declared fact presence is pre-validated with
    the typed manifest integrity error, so only known integrity failures and
    unreadable records reach the report. Returns failure details per
    qualified identity (without the ``HISTORY_INTEGRITY`` prefix) plus the
    audited identities.
    """
    try:
        from .kosmic_project_skills import (
            CuratedManifestIntegrityError,
            as_string_list,
            proposal_fingerprint,
            read_curated_manifest_pins,
        )
    except ImportError:
        from kosmic_project_skills import (
            CuratedManifestIntegrityError,
            as_string_list,
            proposal_fingerprint,
            read_curated_manifest_pins,
        )
    failures: dict[str, list[str]] = {}
    audited: set[str] = set()
    for subject in subjects:
        try:
            document = read_document(root, root / subject.path)
        except SpecError as error:
            failures[subject.qualified_id] = [f"record is unreadable: {error}"]
            audited.add(subject.qualified_id)
            continue
        metadata = document.metadata
        details: list[str] = []
        try:
            _require_proposal_facts(metadata)
            read_curated_manifest_pins(
                root,
                as_string_list(metadata.get("input_manifest")),
                historical=subject.claimed_status == "done",
            )
            if str(metadata["decision"]) != "pending":
                routine_fields = None
                if "target_kind" in metadata:
                    routine_fields = {
                        "target_kind": str(metadata.get("target_kind") or ""),
                        "routine_action": str(metadata.get("routine_action") or ""),
                        "routine_id": str(metadata.get("routine_id") or ""),
                        "linked_proposals": sorted(as_string_list(metadata.get("linked_proposals"))),
                        "consumer_approvals": sorted(as_string_list(metadata.get("consumer_approvals"))),
                    }
                computed = proposal_fingerprint(
                    str(metadata["result"]),
                    str(metadata["scope"]),
                    str(metadata["target"]),
                    str(metadata["artifact_role"]) if "artifact_role" in metadata else None,
                    as_string_list(metadata["related_notes"]),
                    as_string_list(metadata.get("evidence_packs")),
                    document.body,
                    routine_fields,
                )
                recorded = str(metadata["fingerprint"]).strip()
                if recorded != computed:
                    details.append(
                        f"Skill Proposal fingerprint mismatch; expected {computed}"
                    )
        except CuratedManifestIntegrityError as error:
            details.append(str(error))
        failures[subject.qualified_id] = details
        audited.add(subject.qualified_id)
    return failures, audited


def _strict_outcomes(root: Path, subjects: tuple[HistorySubject, ...],
                     facts: Mapping[str, StructuralRecordFacts] | None,
                     ) -> tuple[dict[str, list[str]], set[str]]:
    """Run the narrow selected-record integrity readers once.

    Done records go through the structural receipt-integrity reader (a
    missing or unsafe store is itself missing claimed completion proof,
    irrespective of the bootstrap-flat exemption that only ever applies to
    normal unselected reporting); proposal records through the curated-manifest
    pin and recorded-fingerprint reader. Returns failure details per
    qualified identity (without the ``HISTORY_INTEGRITY`` prefix) and the
    identities actually audited; records with no existing integrity contract
    are never given invented requirements.
    """
    failures: dict[str, list[str]] = {}
    audited: set[str] = set()
    if not subjects:
        return failures, audited
    known = facts or {}
    done = [subject for subject in subjects if subject.claimed_status == "done"]
    if done:
        resolved = [
            known.get(subject.qualified_id)
            or StructuralRecordFacts(
                subject.qualified_id, root / subject.path,
                {"status": subject.claimed_status})
            for subject in done
        ]
        pending = structural_receipt_pendencies(root, resolved, strict_absence=True)
        for subject in done:
            expected = pending.get(subject.qualified_id)
            if expected is not None:
                failures.setdefault(subject.qualified_id, []).append(
                    "claims done but its terminal receipt is missing or does not "
                    f"match the record (expected {expected})"
                )
            audited.add(subject.qualified_id)
    proposals = [subject for subject in subjects if subject.kind == "proposal"]
    if proposals:
        proposal_failures, proposal_audited = _proposal_pin_outcomes(root, proposals)
        for identity, details in proposal_failures.items():
            if details:
                failures.setdefault(identity, []).extend(details)
        audited.update(proposal_audited)
    return failures, audited


def strict_history_markers(project_root: Path, policy: HistoryPolicy,
                           subjects: tuple[HistorySubject, ...],
                           facts: Mapping[str, StructuralRecordFacts] | None = None,
                           ) -> dict[str, str]:
    """Standing view marker per selected identity, coherent with the mode.

    Warn canonical views (and unaudited records) render the standing
    ``unverified — not audited`` marker and skip readers entirely. A
    configured strict canonical view actually audits the selected records
    with existing integrity rules and renders ``strict audit clean`` or
    ``strict audit failure`` per audited identity — claimed lifecycle is
    never rewritten and failure diagnostics stay separate. A forced audit on
    a warn policy (Story 002) never alters these canonical markers, and no
    audit result is cached or persisted.
    """
    markers = {subject.qualified_id: UNAUDITED_MARKER for subject in subjects}
    if policy.mode != "strict" or not subjects:
        return markers
    root = Path(project_root).expanduser().resolve()
    failures, audited = _strict_outcomes(root, subjects, facts)
    for identity in audited:
        markers[identity] = (
            AUDITED_FAILURE_MARKER if failures.get(identity) else AUDITED_CLEAN_MARKER
        )
    return markers


def _subject_report(subjects: tuple[HistorySubject, ...], policy: HistoryPolicy, *,
                    strict_audit: bool, root: Path,
                    facts: Mapping[str, StructuralRecordFacts] | None = None) -> HistoryReport:
    """Build the display report; the strict inspection is the only retrospective read.

    Warn display never invokes a reader. Under the effective strict
    inspection the narrow integrity readers run for exactly the selected
    records with existing rules; failures stay report diagnostics (only
    validate/audit turns them into exit failures), audited-clean records
    stop producing the standing unaudited diagnostic, and claimed lifecycle,
    receipts, and pins remain untouched.
    """
    diagnostics = [
        f"history: {subject.path}: claimed {subject.claimed_status or 'unknown'} "
        f"{subject.kind} is unverified — not audited"
        for subject in subjects
    ]
    failures: list[str] = []
    if strict_audit:
        failure_map, audited = _strict_outcomes(root, subjects, facts)
        for subject in subjects:
            for detail in failure_map.get(subject.qualified_id, ()):
                failures.append(f"HISTORY_INTEGRITY: {subject.path}: {detail}")
        diagnostics = [
            text for text, subject in zip(diagnostics, subjects)
            if subject.qualified_id not in audited
        ]
    return HistoryReport(
        policy=policy, subjects=subjects,
        diagnostics=tuple(diagnostics), failures=tuple(failures),
    )


def inspect_history(structure: _SpecStructure, policy: HistoryPolicy, *,
                    strict_audit: bool = False) -> HistoryReport:
    """Report selected records' claimed lifecycle and configured integrity.

    Display never depends on a retrospective reader: selected records are
    skipped, not audited and downgraded. The effective strict inspection is
    ``strict_audit or policy.mode == "strict"`` — the configured strict mode
    is respected without any caller passing an override, ``strict_audit``
    merely forces the inspection (Story 002's read-only audit override), and
    ``False`` is no override, never a force-warn. Audited-clean records stop
    producing the standing unaudited diagnostic; claimed lifecycle,
    receipts, and pins remain untouched.
    """
    facts = {
        ref.qualified_id: StructuralRecordFacts(ref.qualified_id, ref.path, ref.metadata)
        for ref in structure.records
    }
    return _subject_report(
        _structure_subjects(structure, policy), policy,
        strict_audit=strict_audit or policy.mode == "strict",
        root=structure.root, facts=facts,
    )


def audit_history(project: "Project", *, strict_audit: bool = False) -> HistoryReport | None:
    """Validate-time report for ``project``; None when unconfigured.

    Selection is resolved again from current bytes at the reporting
    boundary. The effective strict inspection is
    ``strict_audit or policy.mode == "strict"``: the configured mode always
    applies, and the override only forces the read-only inspection (Story
    002) — it is never passed into the canonical renderer or STATUS.
    """
    policy = project.history_integrity
    if policy is None or not policy.records:
        return None
    effective = strict_audit or policy.mode == "strict"
    try:
        structure = _collect_spec_structure(project.root)
    except SpecError as error:
        if error.code != "MIGRATION_REQUIRED":
            raise
        root = Path(project.root).expanduser().resolve()
        entries = _flat_entries(root, policy)
        facts = {
            subject.qualified_id: StructuralRecordFacts(
                subject.qualified_id, root / subject.path, metadata)
            for subject, metadata in entries
        }
        return _subject_report(
            tuple(subject for subject, _ in entries), policy,
            strict_audit=effective, root=root, facts=facts,
        )
    return inspect_history(structure, policy, strict_audit=effective)
