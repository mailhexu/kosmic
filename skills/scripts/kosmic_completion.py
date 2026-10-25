"""Record completion: verified evidence, atomic publication, durable receipt.

Revision 2 (AD-SW9-R2): ``finish_work`` resolves the governing record at
invocation time, validates acceptance evidence and the pinned review, checks
the worktree diff against the declared scope, and then publishes the status
transition, the durable work receipt, and finally the STATUS reports derived
from that committed receipt. An interruption leaves the record not-done (or
fully done); the command is simply rerun — there is no recovery journal.
Unreceipted ``done`` remains pending for catalog/STATUS readers.

Revision 3: completion evidence moves into the governing record.
``validate_completion_proof`` checks embedded ``completion_observations``
(structural exact-checkbox criterion coverage only — never text parsing) and
``_checked_review`` validates the embedded structured ``completion_review``
(both review axes, fixed base, round, findings ledger) plus the
``reviewed_revision`` binding. The published receipt binds exactly the
completed record bytes (``proof == {record_path: record_sha256}``), so later
note or data-doc evolution never revokes completion while a post-receipt edit
of the work record itself breaks the receipt by design. Historical receipts
recorded against acceptance/review sidecars keep validating those recorded
originals' bytes; missing originals surface as explicit pending and changed
originals as drift — never repinned or re-blessed against current bytes.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any, Mapping

try:
    from . import kosmic_work as work
    from .kosmic_specs import (CREATE_LOCK_PARTS, SpecCatalog, SpecError,
                               _creation_lock, _read_regular_or_none,
                               _replace_regular_bytes, _table_cells, read_document)
    from .kosmic_dreams import receipt_name
except ImportError:
    import kosmic_work as work
    from kosmic_specs import (CREATE_LOCK_PARTS, SpecCatalog, SpecError,
                              _creation_lock, _read_regular_or_none,
                              _replace_regular_bytes, _table_cells, read_document)
    from kosmic_dreams import receipt_name

RECEIPT_SCHEMA = "kosmic.work-receipt/1"
RECEIPTS_RELATIVE = ".kosmic/work-receipts"
_CREATION_LOCK_RELATIVE = "/".join(CREATE_LOCK_PARTS)


def _deny(condition: bool, code: str, detail: str = "") -> None:
    if condition:
        raise work.WorkdirError(code, detail)


def _utcnow() -> str:
    import time
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _bytes(root: Path, relative: str) -> bytes | None:
    text = str(relative)
    parts = text.split("/")
    if not text or text.startswith("/") or any(part in {"", ".", ".."} for part in parts):
        raise work.WorkdirError("SCOPE_DENIED", f"unsafe Project-relative path: {relative!r}")
    directory_fd = -1
    file_fd = -1
    try:
        directory_fd = os.open(Path(root), os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        for part in parts[:-1]:
            child_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd)
            os.close(directory_fd)
            directory_fd = child_fd
        file_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
        if not stat.S_ISREG(os.fstat(file_fd).st_mode):
            raise work.WorkdirError("SCOPE_DENIED", f"not a regular Project file: {relative}")
        chunks: list[bytes] = []
        remaining = 1 << 20
        while remaining:
            chunk = os.read(file_fd, min(remaining + 1, 65536))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
            if remaining < 0:
                raise work.WorkdirError("COMPLETION_INVALID", f"Project file exceeds 1 MiB: {relative}")
        return b"".join(chunks)
    except FileNotFoundError:
        return None
    except work.WorkdirError:
        raise
    except OSError as error:
        if error.errno in (getattr(os, "ELOOP", 40),):
            raise work.WorkdirError("SCOPE_DENIED", f"symlink in Project path: {relative}") from error
        raise work.WorkdirError("COMPLETION_INVALID", f"{relative}: {error}") from error
    finally:
        if file_fd >= 0:
            os.close(file_fd)
        if directory_fd >= 0:
            os.close(directory_fd)


def _sha(data: bytes | None) -> str | None:
    return hashlib.sha256(data).hexdigest() if data is not None else None


def _json(root: Path, relative: str, code: str) -> dict[str, Any]:
    payload = _bytes(root, relative)
    try:
        parsed = json.loads(payload.decode("utf-8")) if payload is not None else None
    except (ValueError, UnicodeError, AttributeError) as error:
        raise work.WorkdirError(code, f"{relative}: invalid JSON") from error
    _deny(not isinstance(parsed, dict), code, f"{relative}: missing or invalid object")
    return parsed


def reject_retired_completion_inputs(metadata: Mapping[str, Any], name: str) -> None:
    """Reject retired completion inputs on pre-terminal records (Story 005).

    Evidence packs and actual sidecar-file declarations are retired: new
    completion binds observations and review inside the record itself. Empty
    historical placeholders (``[]``/``""``) stay tolerated; terminal records
    never reach this helper, so done records with legacy sidecars keep
    validating against their unchanged original bytes.
    """
    if "evidence_packs" in metadata:
        raise work.WorkdirError(
            "RETIRED_INPUT",
            f"{name}: unsupported input declaration 'evidence_packs': "
            "evidence packs are retired (Story 005)")
    for field in ("acceptance_evidence", "review_record"):
        value = metadata.get(field)
        if value in (None, "", []):
            continue
        raise work.WorkdirError(
            "RETIRED_INPUT",
            f"{name}: unsupported input declaration '{field}': completion "
            "binds observations and review inside the record (Story 005)")


def acceptance_criteria(root: Path, record) -> list[str]:
    """Exact acceptance-criteria checkbox text in canonical record order.

    The one shared scan behind the completion validator and the read-only
    prefill draft: the ``## Acceptance Criteria`` section's checkbox lines,
    verbatim and in record order; a record without criteria is rejected.
    """
    root = Path(root)
    canonical = record.path.relative_to(root).as_posix()
    document = read_document(root, record.path)
    section = re.search(r"^## Acceptance Criteria\s*$([\s\S]*?)(?=^## |\Z)", document.body, re.M)
    criteria = re.findall(r"^- \[[ xX]\]\s+(.+)$", section.group(1), re.M) if section else []
    _deny(not criteria, "ACCEPTANCE_INVALID", f"{canonical}: no acceptance criteria")
    return criteria


def prepare_completion(root: Path, record) -> list[dict[str, Any]]:
    """Draft embedded completion observations for an authorized record.

    Read-only companion to ``validate_completion_proof`` built on the same
    criterion scan: every criterion's exact text in canonical record order,
    each exact-matched authored entry preserved field-for-field (including
    adverse findings and extra authored fields), and a blank
    ``observation``/``source`` draft wherever no authored entry exists — a
    draft that finish still rejects. An authored entry must carry text
    fields: string ``criterion``/``observation``/``source`` with only the
    criterion required non-empty, blank observation/source text being draft
    state. Unknown, repeated, or malformed authored mappings are refused,
    never silently dropped or coerced; no outcome, reviewer, or approval
    field is generated and nothing is written.
    """
    root = Path(root)
    canonical = record.path.relative_to(root).as_posix()
    criteria = acceptance_criteria(root, record)
    seen: set[str] = set()
    for criterion in criteria:
        _deny(criterion in seen, "ACCEPTANCE_INVALID",
              f"{canonical}: duplicated criterion: {criterion!r}")
        seen.add(criterion)
    entries: dict[str, Mapping[str, Any]] = {}
    observations = record.metadata.get("completion_observations")
    if observations is not None:
        _deny(not isinstance(observations, (list, tuple)),
              "ACCEPTANCE_INVALID", f"{canonical}: invalid completion_observations")
        for observation in observations:
            _deny(not isinstance(observation, dict)
                  or not all(isinstance(observation.get(field), str)
                             for field in ("criterion", "observation", "source"))
                  or not observation["criterion"].strip(),
                  "ACCEPTANCE_INVALID",
                  f"{canonical}: malformed completion_observations entry")
            criterion = observation["criterion"]
            _deny(criterion not in criteria or criterion in entries,
                  "ACCEPTANCE_INVALID",
                  f"{canonical}: unknown or repeated criterion: {criterion!r}")
            entries[criterion] = observation
    return [dict(entries[criterion]) if criterion in entries else
            {"criterion": criterion, "observation": "", "source": ""}
            for criterion in criteria]


def validate_completion_proof(root: Path, record) -> dict[str, str]:
    """Check exact structural criterion coverage of embedded observations.

    A structural gate only: every acceptance criterion checkbox in the
    record body must be covered by exactly one ``completion_observations``
    entry carrying non-empty ``criterion``/``observation``/``source`` text.
    The sufficiency of any observation — including adverse findings — is
    judged by the recorded independent review (``_checked_review``), never
    by parsing observation or source wording here, and no outcome field is
    required. Returns the observed record binding
    ``{record_path: sha256(record bytes)}``.
    """
    root = Path(root)
    reject_retired_completion_inputs(record.metadata, record.path.name)
    canonical = record.path.relative_to(root).as_posix()
    observations = record.metadata.get("completion_observations")
    _deny(not isinstance(observations, (list, tuple)) or not observations,
          "ACCEPTANCE_INVALID", f"{canonical}: declare completion_observations")
    criteria = acceptance_criteria(root, record)
    covered: set[str] = set()
    for observation in observations:
        _deny(not isinstance(observation, dict)
              or not all(isinstance(observation.get(field), str) and observation[field].strip()
                         for field in ("criterion", "observation", "source")),
              "ACCEPTANCE_INVALID", f"{canonical}: incomplete completion_observations entry")
        criterion = observation["criterion"]
        _deny(criterion not in criteria or criterion in covered,
              "ACCEPTANCE_INVALID",
              f"{canonical}: unknown or repeated criterion: {criterion!r}")
        covered.add(criterion)
    _deny(covered != set(criteria), "ACCEPTANCE_INVALID", f"{canonical}: uncovered criteria")
    return {canonical: _sha(_bytes(root, canonical))}


def source_revision(worktree: Path, root: Path, record) -> str:
    """Bind changed source bytes, excluding Project records/projections."""
    tree = Path(worktree).expanduser().resolve()
    project = Path(root).expanduser().resolve()
    same_root = project == tree
    try:
        project_prefix = "" if same_root else project.relative_to(tree).as_posix() + "/"
    except ValueError:
        project_prefix = ""
    record_relative = record.path.relative_to(project).as_posix()
    payload: dict[str, str | None] = {}
    for relative in work.changed_worktree_paths(tree):
        project_metadata = same_root and (
            relative.startswith(("specs/", "evidence/", "log/"))
            or relative == record_relative or relative == _CREATION_LOCK_RELATIVE
        )
        if (relative == ".tmp" or relative.startswith(".tmp" + "/")
                or relative == "STATUS.md" or relative.endswith("/STATUS.md")
                or relative.startswith(".git/") or project_metadata
                or (project_prefix and relative.startswith(project_prefix))):
            continue
        path = tree / relative
        try:
            payload[relative] = _sha(path.read_bytes()) if path.is_file() else None
        except OSError as error:
            raise work.WorkdirError("REVIEW_INVALID", f"{relative}: {error}") from error
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def validate_receipt_payload(root: Path, record, receipt: dict[str, Any]) -> dict[str, Any]:
    """Validate a terminal receipt against its completed record binding.

    A current receipt binds exactly ``{record_path: record_sha256}``; only
    the unchanged completed record bytes are hashed, so later refinement of
    linked notes or data documents never revokes completion while any
    post-receipt edit of the work record itself breaks the receipt by
    design. A historical receipt recorded against acceptance/review sidecars
    classifies its originals from the completed record's own recorded
    ``acceptance_evidence``/``review_record`` references and byte-verifies
    only those originals (missing → pending, changed → drift) together with
    their schema/identity/record binding and the artifact digest maps
    recorded inside them; the recorded artifact/notes/data digests remain
    historical facts and are never opened or re-hashed against current
    bytes. Empty, incomplete, or foreign proof maps cannot complete, and
    historical receipts are never repinned or re-blessed.
    """
    root = Path(root)
    canonical = record.path.relative_to(Path(root)).as_posix()
    record_sha256 = _sha(_bytes(Path(root), canonical))
    _deny(receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("identity") != record.qualified_id
          or receipt.get("status") != "successful" or receipt.get("record_path") != canonical
          or receipt.get("record_sha256") != record_sha256,
          "COMPLETION_PENDING", f"{canonical}: no matching successful receipt")
    proof = receipt.get("proof")
    _deny(not isinstance(proof, dict), "COMPLETION_PENDING",
          f"{canonical}: receipt proof missing")
    if set(proof) == {canonical}:
        _deny(proof[canonical] != record_sha256, "COMPLETION_DRIFT",
              f"{canonical}: completed record changed after receipt")
        return receipt
    # Historical (pre-cutover) receipt: the completed record itself names the
    # acceptance and review sidecars it was finished against. Only those
    # recorded originals are byte-verified — their schema/identity/record
    # binding and the artifact digest maps recorded inside them must agree
    # with the receipt's recorded proof, but the recorded artifact/notes/data
    # digests stay historical facts: current raw files are never opened or
    # re-hashed, so later note or dataset evolution cannot revoke completion.
    # Empty or incomplete proof maps cannot complete: a legacy receipt must
    # still name every recorded original, or it stays explicitly pending.
    declaration = record.metadata.get("acceptance_evidence")
    _deny(not isinstance(declaration, (list, tuple)) or not declaration,
          "COMPLETION_PENDING",
          f"{canonical}: legacy receipt without recorded acceptance evidence")
    review_reference = record.metadata.get("review_record")
    _deny(not isinstance(review_reference, str) or not review_reference,
          "COMPLETION_PENDING",
          f"{canonical}: legacy receipt without recorded review record")
    recorded_originals = [(str(item), "kosmic.acceptance-evidence/1")
                          for item in declaration]
    recorded_originals.append((review_reference, "kosmic.work-review/1"))
    for reference, expected_schema in recorded_originals:
        digest = proof.get(reference)
        _deny(not isinstance(digest, str), "COMPLETION_PENDING",
              f"{canonical}: legacy receipt proof missing recorded original: {reference}")
        original = _bytes(root, reference)
        _deny(original is None, "COMPLETION_PENDING",
              f"{canonical}: historical receipt original missing: {reference}")
        _deny(_sha(original) != digest, "COMPLETION_DRIFT",
              f"{canonical}: historical receipt original changed: {reference}")
        document = _json(root, reference, "COMPLETION_PENDING")
        _deny(document.get("schema") != expected_schema
              or document.get("identity") != record.qualified_id
              or document.get("record_path") != canonical,
              "COMPLETION_DRIFT",
              f"{canonical}: historical receipt original foreign: {reference}")
    for reference, _ in recorded_originals[:-1]:
        document = _json(root, reference, "COMPLETION_PENDING")
        for result in document.get("results") or ():
            artifacts = result.get("artifacts") if isinstance(result, dict) else None
            for artifact in artifacts or ():
                path = str(artifact.get("path")) if isinstance(artifact, dict) else None
                recorded = proof.get(path) if path is not None else None
                _deny(path is None or not isinstance(recorded, str)
                      or artifact.get("sha256") != recorded,
                      "COMPLETION_DRIFT",
                      f"{canonical}: historical receipt artifact digest inconsistent: {path}")
    return receipt


def check_terminal_receipt(root: Path, record) -> dict[str, Any]:
    receipt = _json(Path(root),
                    f"{RECEIPTS_RELATIVE}/{receipt_name(record.qualified_id)}",
                    "COMPLETION_PENDING")
    return validate_receipt_payload(Path(root), record, receipt)


def check_finding_annotations(metadata, canonical: str) -> None:
    """Validate supplied per-finding annotations wherever review metadata
    is consulted (shared by ``_checked_review`` and the standalone
    ``check-completion`` diagnostic seam).

    Only supplied annotations are validated: absent or legacy review
    metadata passes unchanged, and no closure, proof, review-approval, or
    stable-id requirement is implied here (``_checked_review`` still owns
    the full ledger shape). Malformed shapes raise ``REVIEW_INVALID``
    naming the finding by stable id when present, otherwise by row index.
    """
    review = metadata.get("completion_review")
    if not isinstance(review, dict):
        return
    findings = review.get("findings")
    if not isinstance(findings, list):
        return
    for index, finding in enumerate(findings):
        if not isinstance(finding, dict):
            continue  # non-mapping rows stay _checked_review's business
        label = (f"finding {finding['id']}"
                 if isinstance(finding.get("id"), str) and finding["id"].strip()
                 else f"finding #{index}")
        _deny_incoherent_annotation(finding, canonical, label)


def _deny_incoherent_annotation(finding: dict, canonical: str,
                                label: str | None = None) -> None:
    finding_id = label if label is not None else f"finding {finding['id']}"
    # Optional per-finding annotations (Story 003, ADR-003): validated
    # for shape and coherence whenever supplied, before the closure
    # check so the annotation diagnostic names the actual incoherence.
    # A worker response is a claim only; it never closes a finding.
    response = finding.get("worker_response")
    # An explicit null is a SUPPLIED annotation, not an absent one: only a
    # missing key is a no-op. Null (and any non-mapping) is refused.
    _deny("worker_response" in finding
          and not isinstance(response, dict),
          "REVIEW_INVALID",
          f"{canonical}: finding {finding_id} worker_response must be a mapping")
    if isinstance(response, dict):
        kind = response.get("kind")
        _deny(kind not in ("fixed", "refuted", "blocked"), "REVIEW_INVALID",
              f"{canonical}: finding {finding_id} worker_response kind "
              f"invalid: {kind!r}")
        detail = response.get("detail")
        evidence = response.get("evidence")
        if kind == "blocked":
            _deny(not isinstance(detail, str) or not detail.strip(),
                  "REVIEW_INVALID",
                  f"{canonical}: finding {finding_id} blocked "
                  f"worker_response requires the prerequisite in detail")
            _deny(not isinstance(evidence, str) or not evidence.strip(),
                  "REVIEW_INVALID",
                  f"{canonical}: finding {finding_id} blocked "
                  f"worker_response requires the escalation rationale in evidence")
        else:
            _deny(not isinstance(detail, str) or not detail.strip(),
                  "REVIEW_INVALID",
                  f"{canonical}: finding {finding_id} {kind} "
                  f"worker_response requires non-empty detail")
            _deny(not isinstance(evidence, str) or not evidence.strip(),
                  "REVIEW_INVALID",
                  f"{canonical}: finding {finding_id} {kind} "
                  f"worker_response requires non-empty evidence")
    # Reviewer resolution vocabulary: only a resolved row may carry it.
    # An explicit null is supplied and refused; a missing key is a no-op.
    resolution = finding.get("resolution")
    _deny("resolution" in finding
          and (resolution not in ("fixed", "refuted")
               or finding.get("status") != "resolved"),
          "REVIEW_INVALID",
          f"{canonical}: finding {finding_id} resolution {resolution!r} "
          f"is coherent only on a resolved row")


def _checked_review(root: Path, worktree: Path, record, *,
                    changed_paths=None, excluded_paths=()) -> None:
    """Validate the embedded structured ``completion_review`` (ADR-B shape).

    Layout follows the accepted Architecture YAML: ``reviewer`` identity,
    nested ``axes.standards``/``axes.spec`` each with a named reviewer and
    approved decision, overall ``decision`` (``approved`` or
    ``user-accepted`` with ``approved_by``), ``review_base`` bound to the
    record metadata and ``review_round`` in 1..3, a stable findings ledger
    with ``disposition``/``status`` and explicit human risk acceptance
    fields, ``reviewed_revision`` bound to the unchanged ``source_revision``,
    and a typed ``scope`` claim list (possibly empty for record-only work).
    Optional per-finding annotations are validated for shape and coherence
    when supplied: ``worker_response`` (``kind: fixed|refuted|blocked`` with
    non-empty ``detail``/``evidence``; ``blocked`` carries the prerequisite
    in ``detail`` and the escalation rationale in ``evidence``) is a worker
    claim that never closes a finding, and ``resolution``
    (``fixed|refuted``) is reviewer vocabulary valid only on ``resolved``
    rows. Legacy closed rows without annotations stay valid unchanged.
    The root-level axes shape is not accepted on new records. When
    ``changed_paths`` is given, the actual changed work must also be covered
    by the reviewed claims, reusing the unchanged ``check_record_changes``
    algorithm with the same exemptions; uncovered reviewed scope fails as
    ``REVIEW_INVALID`` after the primary finish-claim check.
    """
    review = record.metadata.get("completion_review")
    canonical = record.path.relative_to(Path(root)).as_posix()
    _deny(not isinstance(review, dict), "REVIEW_INVALID",
          f"{canonical}: declare completion_review")
    base = record.metadata.get("review_base")
    round_number = record.metadata.get("review_round")
    _deny(not isinstance(base, str) or not base.strip()
          or type(round_number) is not int or not 1 <= round_number <= 3
          or review.get("review_base") != base,
          "REVIEW_INVALID", f"{canonical}: review base/round binding mismatch")
    _deny(not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip(),
          "REVIEW_INVALID", f"{canonical}: reviewer identity missing")
    axes = review.get("axes")
    _deny(not isinstance(axes, dict), "REVIEW_INVALID",
          f"{canonical}: completion_review axes missing")
    for axis in ("standards", "spec"):
        decision = axes.get(axis)
        _deny(not isinstance(decision, dict) or decision.get("decision") != "approved"
              or not isinstance(decision.get("reviewer"), str)
              or not decision["reviewer"].strip(),
              "REVIEW_INVALID", f"{canonical}: {axis} approval missing")
    overall = review.get("decision")
    _deny(overall not in ("approved", "user-accepted"), "REVIEW_INVALID",
          f"{canonical}: review decision blocks completion: {overall!r}")
    _deny(overall == "user-accepted"
          and (not isinstance(review.get("approved_by"), str)
               or not review["approved_by"].strip()),
          "REVIEW_INVALID", f"{canonical}: user-accepted requires approved_by")
    findings = review.get("findings")
    _deny(not isinstance(findings, list), "REVIEW_INVALID",
          f"{canonical}: findings ledger missing")
    for finding in findings:
        _deny(not isinstance(finding, dict) or not isinstance(finding.get("id"), str)
              or not finding["id"].strip(), "REVIEW_INVALID",
              f"{canonical}: finding without stable id")
        _deny_incoherent_annotation(finding, canonical)
        if finding.get("disposition") == "Blocking":
            resolved = finding.get("status") == "resolved"
            accepted = (finding.get("status") == "risk-accepted"
                        and isinstance(finding.get("risk_accepted_by"), str)
                        and bool(finding["risk_accepted_by"].strip())
                        and isinstance(finding.get("risk_acceptance_note"), str)
                        and bool(finding["risk_acceptance_note"].strip()))
            _deny(not resolved and not accepted, "REVIEW_INVALID",
                  f"{canonical}: unresolved blocking finding {finding['id']}")
    reviewed_scope = review.get("scope")
    _deny(not isinstance(reviewed_scope, list), "REVIEW_INVALID",
          f"{canonical}: completion_review scope must be a list of finish claims")
    try:
        for claim in reviewed_scope:
            work._normalize_claim(str(claim))
    except work.WorkdirError as error:
        raise work.WorkdirError(
            "REVIEW_INVALID", f"{canonical}: reviewed scope claim invalid: {error}") from error
    if changed_paths:
        # Record-only work computes an empty changed set: nothing actual to
        # cover, and the empty reviewed scope is legitimate there. Any real
        # changed path must sit inside the reviewed claims.
        try:
            work.check_record_changes(worktree, tuple(str(claim) for claim in reviewed_scope),
                                      root, excluded_paths=tuple(excluded_paths))
        except work.WorkdirError as error:
            raise work.WorkdirError(
                "REVIEW_INVALID",
                f"{record.path}: reviewed scope does not cover the actual work: {error}"
            ) from error
    _deny(review.get("reviewed_revision") != source_revision(worktree, root, record),
          "REVIEW_INVALID",
          f"{record.path}: reviewed revision differs from current work")

def _update_indexes(root: Path, record) -> None:
    """Update indexes under one creation lock; caller must not already hold it.

    Refuse detected external drift before replacement. The lock serializes
    cooperating writers; the expected-content check is not atomic CAS.
    """
    try:
        with _creation_lock(root):
            indexes = {record.path.parent.parent / "INDEX.md", Path(root) / "specs" / "INDEX.md"}
            for index in indexes:
                try:
                    relative = record.path.relative_to(index.parent).as_posix()
                except ValueError:
                    # Only the owner-local index carries an owner record's row.
                    continue
                parts = index.relative_to(root).parts
                current = _read_regular_or_none(root, parts)
                if current is None:
                    continue
                changed = False
                rows = []
                status_column: int | None = None
                for line in current.decode("utf-8").splitlines(keepends=True):
                    if not line.lstrip().startswith("|"):
                        status_column = None
                        rows.append(line)
                        continue
                    cells = _table_cells(line)
                    header = [cell.strip().casefold() for cell in cells]
                    if "status" in header:
                        status_column = header.index("status")
                    elif status_column is not None and f"]({relative})" in line:
                        if status_column < len(cells):
                            cells[status_column] = " done "
                            line = "|".join(cells) + ("\n" if line.endswith("\n") else "")
                            changed = True
                    rows.append(line)
                if changed:
                    _replace_regular_bytes(root, parts, "".join(rows).encode(), expect=current)
    except SpecError as error:
        raise work.WorkdirError(error.code, f"{record.qualified_id}: {error.detail}") from error



def _append_completion_log(root: Path, record, detail: str) -> None:
    import datetime
    day = datetime.date.today().isoformat()
    relative = f"log/{day}-work-completion.md"
    path = Path(root) / relative
    identity = record.qualified_id
    existing = path.read_text(encoding="utf-8") if path.exists() else "# Work completion\n\n"
    marker = f"- `{identity}` — "
    if marker in existing:
        return
    line = f"{marker}{record.path.relative_to(Path(root)).as_posix()}: successful receipt. {detail}\n"
    work._atomic_write(Path(root), relative, (existing + line).encode())


def _write_status_reports(root: Path, record_owner: str | None = None) -> None:
    """Regenerate only the Project's configured bound STATUS.md.

    Publication prefers the strict full-catalog projection. If the catalog
    cannot be enumerated because of an unrelated owner's defect, completion
    falls back to the record-bound view for the completed record's owner. The
    bounded report carries an explicit scope note instead of posing as a
    full-catalog audit. No registered directory is an additional destination;
    without a configured status root, completion writes no external STATUS.
    """
    if __package__:
        from . import kosmic_project_skills as cli
    else:
        import kosmic_project_skills as cli
    from dataclasses import replace
    project = cli.load_project(root)
    if project.status_root is None:
        return
    status_root = project.status_root.expanduser().resolve()
    snapshot = work._run_git(root, "rev-parse", "HEAD").strip() or "no-head"
    scoped = replace(project, status_root=status_root)
    try:
        rendered = cli.render_status(scoped, snapshot)
    except SpecError:
        configured_history = (
            project.history_integrity is not None
            and bool(project.history_integrity.records)
        )
        if configured_history:
            rendered = cli.render_status(
                scoped, snapshot,
                structural_bounded=record_owner if record_owner else True)
        else:
            rendered = cli.render_status(
                scoped, snapshot,
                catalog=SpecCatalog.bounded(root, record_owner))
    work._atomic_write(status_root, "STATUS.md", rendered)


def _completion_cli():
    if __package__:
        from . import kosmic_project_skills as cli
    else:
        import kosmic_project_skills as cli
    return cli


def _completion_precheck(root: Path):
    """Load the Project config strictly for the finish domain precheck.

    Unlike the tolerant STATUS-candidate enumeration, a missing or unreadable
    Project config is reported here, never swallowed: the shared read-only
    domain precheck cannot run without it.
    """
    cli = _completion_cli()
    try:
        return cli, cli.load_project(root)
    except (cli.KosmicError, OSError, RuntimeError, ValueError) as error:
        raise work.WorkdirError(
            "COMPLETION_PRECHECK_FAILED",
            f"Project config unavailable for the completion precheck: {error}"
        ) from error


def finish_work(project_root: Path, worktree: Path, record_ref: str,
                scope: list[str], *, detail: str = "") -> dict[str, Any]:
    """Run every completion gate, publish done, receipt, then STATUS.

    One ordinary nonterminal finish resolves authority, then validates the
    embedded proof, the primary finish-claim scope (``SCOPE_DENIED``
    precedence), the reviewed scope/source binding, and finally the complete
    shared read-only domain precheck — the same helper standalone
    ``check-completion`` runs — before an immediate-before-write freshness
    recheck and the unchanged publication order record → indexes →
    completion log → receipt → derived STATUS.

    Terminal retries are invariant: identity and approved ancestry resolve
    first; a present receipt is validated over the unchanged record bytes
    (legacy receipts byte-verify only their recorded immutable originals),
    the record's declared formal math/proposal/routine contracts are applied
    exactly as the plain done path applies them, and only the derived STATUS
    reports are repaired while the receipt is returned unchanged. Evolving
    notes, data, and the current source delta are never re-hashed, and
    historical pins are never refreshed. A present but unreadable or
    inconsistent receipt is refused without re-blessing or repinning; only
    an absent receipt falls through to the full nonterminal path, so an
    interrupted episode recovers by rerunning every gate.
    """
    root = Path(project_root).expanduser().resolve()
    tree = Path(worktree).expanduser().resolve()
    record = work.resolve_work_record(root, record_ref, allow_terminal=True)
    receipt_path = f"{RECEIPTS_RELATIVE}/{receipt_name(record.qualified_id)}"
    existing = _bytes(root, receipt_path)
    canonical = record.path.relative_to(root).as_posix()
    if existing is not None:
        # Terminal route (ADR-C): identity and approved ancestry resolved
        # above; a present receipt is the authoritative completion marker.
        # An unreadable or inconsistent receipt is refused
        # (COMPLETION_PENDING/COMPLETION_DRIFT) — never re-blessed, repinned,
        # or treated as a fresh completion attempt.
        receipt = check_terminal_receipt(root, record)
        cli, project_config = _completion_precheck(root)
        cli.check_terminal_formal_gates(project_config, record.path, tree)
        # Receipt-first publication: a valid receipt implies the record,
        # indexes, and completion log are committed; only the derived
        # STATUS projections can lag an interruption. Repair them without
        # rewriting the receipt or duplicating the completion log.
        _write_status_reports(root, record.subproject_id)
        return receipt
    # The gates validate this exact snapshot: record bytes and the review's
    # own validated source binding are captured before the first gate so any
    # later mutation — before, between, or after the gates — is observed at
    # the pre-write recheck.
    validated_record_bytes = record.path.read_bytes()
    original_review = record.metadata.get("completion_review")
    validated_revision = (original_review.get("reviewed_revision")
                          if isinstance(original_review, dict) else None)
    validate_completion_proof(root, record)
    import datetime
    candidates = [record.path.parent.parent / "INDEX.md", root / "specs" / "INDEX.md",
                  root / "log" / f"{datetime.date.today().isoformat()}-work-completion.md",
                  root.joinpath(*CREATE_LOCK_PARTS)]
    candidates.extend(Path(item["path"]) / "STATUS.md"
                      for item in work.load_registry(root)["directories"])
    cli = _completion_cli()
    # Tolerant candidate enumeration only: a config failure here must never
    # mask the primary scope or review diagnostics. The strict load that
    # feeds the shared domain precheck happens after those gates ran.
    try:
        tolerant_config = cli.load_project(root)
    except (cli.KosmicError, OSError, RuntimeError, ValueError):
        tolerant_config = None
    if tolerant_config is not None and tolerant_config.status_root:
        candidates.append(tolerant_config.status_root / "STATUS.md")
    publication_candidates = [path.relative_to(tree).as_posix() for path in candidates
                              if path.is_relative_to(tree)]
    publication_paths = publication_candidates
    scope_result = work.check_record_changes(tree, scope, root, publication_paths)
    # Primary finish-claim coverage ran first (SCOPE_DENIED precedence); the
    # reviewed claims must then cover the same actual changed work, with the
    # canonical publication outputs exempted identically.
    _checked_review(root, tree, record,
                    changed_paths=tuple(scope_result["changed"]),
                    excluded_paths=tuple(publication_candidates))
    # Complete shared read-only domain precheck (ADR-B): the same helper
    # standalone check-completion runs, placed after proof/scope/review so
    # its diagnostics never mask them. It covers depends_on, STATUS drift,
    # retired inputs/content, consumer_interface_change, math/proposal/
    # routine gates, related stable usage notes, and projection. A domain
    # failure translates to COMPLETION_PRECHECK_FAILED with the original
    # diagnostic retained; no auto STATUS/projection repair or pin refresh
    # happens here.
    cli, project_config = _completion_precheck(root)
    try:
        cli._check_existing_completion(project_config, record.path,
                                       source_root=tree, record_scoped=True,
                                       record_owner=record.subproject_id)
    except cli.KosmicError as error:
        raise work.WorkdirError("COMPLETION_PRECHECK_FAILED", str(error)) from error
    # Freshness recheck immediately before publication: the gates validated
    # the entry snapshot and the review's own validated source binding, so
    # any later record, source-binding, or authority change is observed
    # here. Detect only — a drifted record is never repaired, repinned, or
    # rebound; the caller reruns finish.
    _deny(record.path.read_bytes() != validated_record_bytes,
          "RECORD_NOT_AUTHORIZED",
          f"{canonical}: record changed after the completion gates ran; rerun finish")
    _deny(source_revision(tree, root, record) != validated_revision,
          "REVIEW_INVALID",
          f"{canonical}: reviewed source changed after the review gate ran; rerun finish")
    fresh = work.resolve_work_record(root, record_ref, allow_terminal=True)
    _deny(fresh.qualified_id != record.qualified_id or fresh.path != record.path,
          "RECORD_NOT_AUTHORIZED",
          f"{canonical}: work-record identity changed during completion")
    # Publish: record status -> done, then indexes and the completion log,
    # then the authoritative receipt; STATUS reports are derived last so they
    # are generated from the committed receipt, never describing finished
    # work as pending.
    text = record.path.read_text(encoding="utf-8")
    updated = re.sub(r"^status: .*$", "status: done", text, count=1, flags=re.M)
    if updated == text and not re.search(r"^status: done$", text, re.M):
        raise work.WorkdirError("COMPLETION_INVALID", f"{canonical}: record has no status field")
    work._atomic_write(root, canonical, updated.encode())
    _update_indexes(root, record)
    _append_completion_log(root, record, detail)
    record_sha256 = _sha(record.path.read_bytes())
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "identity": record.qualified_id,
        "status": "successful",
        "record_path": canonical,
        "record_sha256": record_sha256,
        "proof": {canonical: record_sha256},
        "completed_at": _utcnow(),
        "detail": detail,
    }
    receipt_payload = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
    work._atomic_write(root, receipt_path, receipt_payload)
    _write_status_reports(root, record.subproject_id)
    return receipt


def check_done_record_gates(catalog, project_root: Path, record) -> None:
    """Ancestry and terminal receipt gates for a canonical done record.

    Shared by ``check_completion_gates`` and the plain ``--work-item``
    completion entry: a done record always requires approved ancestry and a
    valid receipt over its unchanged bytes, so a drifted or unreceipted
    ``done`` never reports complete through either mode.
    """
    work._ancestry_approved(catalog, record)
    check_terminal_receipt(Path(project_root).expanduser().resolve(), record)


def check_completion_gates(project_root: Path, work_item: Path,
                           source_root: Path) -> None:
    """Record-level gates for check-completion after CLI authority resolution.

    The record is resolved through the record-bound bounded view when the
    whole Project catalog cannot be enumerated, so an unrelated subproject's
    defect never hides this record's own acceptance or receipt gates.
    """
    root = Path(project_root).expanduser().resolve()
    try:
        catalog = SpecCatalog(root)
        record = catalog.resolve(work_item)
    except SpecError:
        catalog = SpecCatalog.bounded_for_reference(root, str(work_item))
        record = catalog.resolve(work_item)
    if record.status == "done":
        check_done_record_gates(catalog, root, record)
        return
    if record.kind in work.IMPLEMENTATION_KINDS:
        validate_completion_proof(root, record)
        _checked_review(root, Path(source_root), record)
