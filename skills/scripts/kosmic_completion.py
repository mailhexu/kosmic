"""Record completion: verified evidence, atomic publication, durable receipt.

Revision 2 (AD-SW9-R2): ``finish_work`` resolves the governing record at
invocation time, validates acceptance evidence and the pinned review, checks
the worktree diff against the declared scope, and then publishes the status
transition, the durable work receipt, and finally the STATUS reports derived
from that committed receipt. An interruption leaves the record not-done (or
fully done); the command is simply rerun — there is no recovery journal.
Unreceipted ``done`` remains pending for catalog/STATUS readers.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any

try:
    from . import kosmic_work as work
    from .kosmic_specs import SpecCatalog, SpecError, read_document
    from .kosmic_dreams import receipt_name
except ImportError:
    import kosmic_work as work
    from kosmic_specs import SpecCatalog, SpecError, read_document
    from kosmic_dreams import receipt_name

RECEIPT_SCHEMA = "kosmic.work-receipt/1"
RECEIPTS_RELATIVE = ".kosmic/work-receipts"


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


def validate_completion_proof(root: Path, record) -> dict[str, str]:
    """Check identity and observed artifacts; independent review judges sufficiency."""
    root = Path(root)
    canonical = record.path.relative_to(root).as_posix()
    declaration = record.metadata.get("acceptance_evidence")
    _deny(not isinstance(declaration, (list, tuple)) or not declaration,
          "ACCEPTANCE_INVALID", f"{canonical}: declare acceptance_evidence")
    document = read_document(root, record.path)
    section = re.search(r"^## Acceptance Criteria\s*$([\s\S]*?)(?=^## |\Z)", document.body, re.M)
    criteria = re.findall(r"^- \[[ xX]\]\s+(.+)$", section.group(1), re.M) if section else []
    _deny(not criteria, "ACCEPTANCE_INVALID", f"{canonical}: no acceptance criteria")
    hashes: dict[str, str] = {}
    outcomes: dict[str, dict[str, Any]] = {}
    for reference in declaration:
        _deny(not isinstance(reference, str), "ACCEPTANCE_INVALID", canonical)
        evidence = _json(root, reference, "ACCEPTANCE_INVALID")
        _deny(evidence.get("schema") != "kosmic.acceptance-evidence/1"
              or evidence.get("identity") != record.qualified_id
              or evidence.get("record_path") != canonical,
              "ACCEPTANCE_INVALID", f"{canonical}: foreign evidence {reference}")
        hashes[reference] = _sha(_bytes(root, reference))
        results = evidence.get("results")
        _deny(not isinstance(results, list) or not results, "ACCEPTANCE_INVALID", reference)
        for result in results:
            _deny(not isinstance(result, dict), "ACCEPTANCE_INVALID", reference)
            criterion = result.get("criterion")
            _deny(criterion not in criteria or criterion in outcomes,
                  "ACCEPTANCE_INVALID", f"{reference}: unknown or repeated criterion")
            _deny(result.get("outcome") != "passed", "ACCEPTANCE_INVALID",
                  f"{reference}: criterion not passed: {criterion!r}")
            for artifact in result.get("artifacts") or ():
                _deny(not isinstance(artifact, dict), "ACCEPTANCE_INVALID", reference)
                path = artifact.get("path")
                observed = _sha(_bytes(root, str(path))) if path else None
                _deny(observed is None or artifact.get("sha256") != observed,
                      "ACCEPTANCE_INVALID",
                      f"{canonical}: missing or stale artifact {path}")
                hashes[str(path)] = observed
            outcomes[criterion] = result
    _deny(set(outcomes) != set(criteria), "ACCEPTANCE_INVALID", f"{canonical}: uncovered criteria")
    reference = record.metadata.get("review_record")
    _deny(not isinstance(reference, str) or not reference, "REVIEW_INVALID",
          f"{canonical}: missing review_record")
    review = _json(root, reference, "REVIEW_INVALID")
    base = record.metadata.get("review_base")
    _deny(not isinstance(base, str) or not base.strip()
          or review.get("schema") != "kosmic.work-review/1"
          or review.get("identity") != record.qualified_id
          or review.get("record_path") != canonical
          or review.get("review_base") != base
          or type(review.get("round")) is not int or not 1 <= review["round"] <= 3,
          "REVIEW_INVALID", f"{canonical}: review identity/base/round mismatch")
    for axis in ("standards", "spec"):
        decision = review.get(axis)
        _deny(not isinstance(decision, dict) or decision.get("decision") != "approved"
              or not isinstance(decision.get("reviewer"), str) or not decision["reviewer"].strip(),
              "REVIEW_INVALID", f"{canonical}: {axis} approval missing")
    findings = review.get("findings")
    _deny(not isinstance(findings, list) or review.get("decision") not in ("approved", "user-accepted"),
          "REVIEW_INVALID", canonical)
    for finding in findings:
        _deny(not isinstance(finding, dict) or not finding.get("id"), "REVIEW_INVALID", canonical)
        if finding.get("disposition") == "Blocking":
            accepted = review["decision"] == "user-accepted" and review.get("approved_by")
            _deny(finding.get("status") != "resolved" and not accepted,
                  "REVIEW_INVALID", f"{canonical}: unresolved {finding['id']}")
    hashes[reference] = _sha(_bytes(root, reference))
    return hashes


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
            relative.startswith(("specs/", "evidence/", "log/")) or relative == record_relative
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
    canonical = record.path.relative_to(Path(root)).as_posix()
    _deny(receipt.get("schema") != RECEIPT_SCHEMA or receipt.get("identity") != record.qualified_id
          or receipt.get("status") != "successful" or receipt.get("record_path") != canonical
          or receipt.get("record_sha256") != _sha(_bytes(Path(root), canonical)),
          "COMPLETION_PENDING", f"{canonical}: no matching successful receipt")
    proof = validate_completion_proof(Path(root), record)
    _deny(proof != receipt.get("proof"), "COMPLETION_DRIFT", f"{canonical}: evidence/review drift")
    return receipt


def check_terminal_receipt(root: Path, record) -> dict[str, Any]:
    receipt = _json(Path(root),
                    f"{RECEIPTS_RELATIVE}/{receipt_name(record.qualified_id)}",
                    "COMPLETION_PENDING")
    return validate_receipt_payload(Path(root), record, receipt)


def _checked_review(root: Path, worktree: Path, record) -> dict[str, str]:
    review = _json(root, str(record.metadata["review_record"]), "REVIEW_INVALID")
    _deny(review.get("reviewed_revision") != source_revision(worktree, root, record),
          "REVIEW_INVALID",
          f"{record.path}: reviewed revision differs from current work")
    return review

def _update_indexes(root: Path, record) -> None:
    indexes = {record.path.parent.parent / "INDEX.md", Path(root) / "specs" / "INDEX.md"}
    for index in indexes:
        if not index.is_file():
            continue
        try:
            relative = record.path.relative_to(index.parent).as_posix()
        except ValueError:
            # The Project-wide specs index is not an ancestor of owner-local
            # records; only the corresponding owner index carries this row.
            continue
        text = index.read_text(encoding="utf-8")
        changed = False
        rows = []
        status_column: int | None = None
        for line in text.splitlines(keepends=True):
            if not line.lstrip().startswith("|"):
                status_column = None
                rows.append(line)
                continue
            cells = line.rstrip("\n").split("|")
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
            work._atomic_write(index.parent, index.name, "".join(rows).encode())


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
    """Regenerate STATUS.md for the Project and every registered directory.

    Publication prefers the strict full-catalog projection. When the whole
    catalog cannot be enumerated (for example an unrelated subproject entry
    is broken), completion falls back to the record-bound bounded view for
    the completed record's owner: the bounded report carries an explicit
    scope note instead of posing as a full-catalog audit, and a directory
    fixed to an unrelated subproject keeps its own report bytes untouched.
    """
    if __package__:
        from . import kosmic_project_skills as cli
    else:
        import kosmic_project_skills as cli
    from dataclasses import replace
    project = cli.load_project(root)
    entries = {str(Path(item["path"])): item
               for item in work.load_registry(root)["directories"]}
    directories = set(entries)
    if project.status_root:
        directories.add(str(project.status_root))
    snapshot = work._run_git(root, "rev-parse", "HEAD").strip() or "no-head"
    bounded = None
    for base in sorted(directories):
        scoped = replace(project, status_root=Path(base))
        try:
            rendered = cli.render_status(scoped, snapshot)
        except SpecError:
            # The full-catalog outcome is identical for every output
            # directory, so the bounded fallback is decided once and reused.
            if bounded is None:
                bounded = SpecCatalog.bounded(root, record_owner)
            fixed = entries.get(base, {}).get("fixed_subproject_id")
            if fixed is not None and fixed != record_owner:
                # This completion never deletes an unrelated directory's report.
                continue
            rendered = cli.render_status(scoped, snapshot, catalog=bounded)
        work._atomic_write(Path(base), "STATUS.md", rendered)


def finish_work(project_root: Path, worktree: Path, record_ref: str,
                scope: list[str], *, detail: str = "") -> dict[str, Any]:
    """Verify evidence/review/scope, publish done, receipt, then STATUS.

    Idempotent: a valid existing receipt is returned unchanged after
    regenerating only the derived STATUS reports, repairing interrupted
    publication without rewriting the receipt or duplicating the completion
    log. An interruption before the receipt leaves the record's previous
    lifecycle state (possibly already ``done`` but pending); rerunning
    completes it.
    """
    root = Path(project_root).expanduser().resolve()
    tree = Path(worktree).expanduser().resolve()
    record = work.resolve_work_record(root, record_ref, allow_terminal=True)
    receipt_path = f"{RECEIPTS_RELATIVE}/{receipt_name(record.qualified_id)}"
    existing = _bytes(root, receipt_path)
    canonical = record.path.relative_to(root).as_posix()
    if existing is not None:
        try:
            receipt = validate_receipt_payload(root, record, json.loads(existing.decode("utf-8")))
        except (ValueError, UnicodeError):
            pass  # unreadable receipt: republish below
        else:
            # Receipt-first publication: a valid receipt implies the record,
            # indexes, and completion log are committed; only the derived
            # STATUS projections can lag an interruption. Repair them without
            # rewriting the receipt or duplicating the completion log.
            _write_status_reports(root, record.subproject_id)
            return receipt
    proof = validate_completion_proof(root, record)
    _checked_review(root, tree, record)
    publication_paths = []
    if record.status == "done":
        import datetime
        candidates = [record.path.parent.parent / "INDEX.md", root / "specs" / "INDEX.md",
                      root / "log" / f"{datetime.date.today().isoformat()}-work-completion.md"]
        candidates.extend(Path(item["path"]) / "STATUS.md"
                          for item in work.load_registry(root)["directories"])
        try:
            if __package__:
                from . import kosmic_project_skills as cli
            else:
                import kosmic_project_skills as cli
            project_config = cli.load_project(root)
        except (OSError, RuntimeError, ValueError):
            project_config = None
        if project_config is not None and project_config.status_root:
            candidates.append(project_config.status_root / "STATUS.md")
        publication_paths = [path.relative_to(tree).as_posix() for path in candidates
                             if path.is_relative_to(tree)]
    work.check_record_changes(tree, scope, root, publication_paths)
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
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "identity": record.qualified_id,
        "status": "successful",
        "record_path": canonical,
        "record_sha256": _sha(record.path.read_bytes()),
        "proof": proof,
        "completed_at": _utcnow(),
        "detail": detail,
    }
    receipt_payload = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
    work._atomic_write(root, receipt_path, receipt_payload)
    _write_status_reports(root, record.subproject_id)
    return receipt


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
        work._ancestry_approved(catalog, record)
        check_terminal_receipt(root, record)
        return
    if record.kind in work.IMPLEMENTATION_KINDS:
        validate_completion_proof(root, record)
        _checked_review(root, Path(source_root), record)
