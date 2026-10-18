"""Story 001 consumer regressions: bounded planning-phase STATUS rendering.

Consumer surface = the real generate-status CLI seam (ADR-E) plus the
unchanged authority boundary (work start/finish, default resolve_work_record
kinds). Every assertion is wording-pin-free: renderer output is judged only
through fixture-owned record identity (vault paths, titles, the status
vocabulary itself) and whole-sandbox mutation digests — never through
expected-render self-comparison, marker pins, or suffix pins.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

from skills.scripts import kosmic_completion, kosmic_dreams, kosmic_work
from skills.scripts.kosmic_project_skills import load_project, status_drift

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "scripts" / "kosmic_project_skills.py"
TODAY = "2026-10-18"
STALE_CONTENT = "stale hand edit\n"


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def _write_notes(project_root: Path) -> None:
    _write(project_root / "notes" / "index.md", "# Index\n")
    _write(
        project_root / "notes" / "stable.md",
        "---\ntype: Project Knowledge\nstatus: stable\ncreated: " + TODAY + "\n"
        "updated: " + TODAY + "\naudience: usage\n---\n\n# Stable\n\ntext\n",
    )


def _bind_entry(project_root: Path, status_root: Path | None) -> None:
    binding = "" if status_root is None else f"status_root: {status_root.resolve()}\n"
    _write(
        project_root / "ProjectEntry.md",
        "---\nproject_id: foo\nworking_state: working-tree\n" + binding + "---\n\n# foo\n",
    )


def _write_subproject(
    project_root: Path, sub_id: str, *, prd_status: str,
    architecture_status: str | None = None, epic_status: str | None = None,
) -> None:
    base = project_root / "subprojects" / sub_id
    _write(
        base / "SubprojectEntry.md",
        "---\nschema: kosmic.subproject/1\nproject_id: foo\nsubproject_id: " + sub_id + "\n"
        "title: " + sub_id + "\nlinked_prd: specs/prd.md\nstatus: draft\n---\n\n# " + sub_id + "\n",
    )
    _write(base / "specs" / "INDEX.md", "# " + sub_id + " Specs\n\n- [PRD](prd.md)\n")
    _write(
        base / "specs" / "prd.md",
        "---\nproject_id: foo\nsubproject_id: " + sub_id + "\nrecord_kind: prd\n"
        "local_id: prd\nstatus: " + prd_status + "\nupdated: " + TODAY + "\n---\n\n"
        "# " + sub_id + " PRD\n\nPlanning authority body.\n",
    )
    if architecture_status is not None:
        _write(
            base / "specs" / "architecture.md",
            "---\nproject_id: foo\nsubproject_id: " + sub_id + "\n"
            "record_kind: architecture\nlocal_id: architecture\nlinked_prd: prd.md\n"
            "status: " + architecture_status + "\nupdated: " + TODAY + "\n---\n\n"
            "# " + sub_id + " Architecture\n\nStructure follows the PRD.\n",
        )
    if epic_status is not None:
        _write(
            base / "specs" / "epics" / "epic-001.md",
            "---\nproject_id: foo\nsubproject_id: " + sub_id + "\nrecord_kind: epic\n"
            "local_id: 001\n"
            "linked_architecture: foo/" + sub_id + "/architecture/architecture\n"
            "linked_prd: foo/" + sub_id + "/prd/prd\n"
            "status: " + epic_status + "\nupdated: " + TODAY + "\n---\n\n"
            "# " + sub_id + " Epic\n\nCohere slice of the PRD.\n",
        )


def _write_quick_task(
    project_root: Path, sub_id: str, local_id: str, *, status: str = "approved",
) -> None:
    _write(
        project_root / "subprojects" / sub_id / "specs" / "quick-tasks" / (local_id + ".md"),
        "---\nproject_id: foo\nsubproject_id: " + sub_id + "\nrecord_kind: quick-task\n"
        "local_id: " + local_id + "\nstatus: " + status + "\nupdated: " + TODAY + "\n---\n\n"
        "# Quick Task " + local_id + "\n\nBounded small work.\n",
    )


def _write_story(
    project_root: Path, sub_id: str, local_id: str, status: str,
    *, receipted: bool = False, chained: bool = False,
) -> str:
    qualified = f"foo/{sub_id}/story/{local_id}"
    relative = f"subprojects/{sub_id}/specs/stories/story-{local_id}.md"
    completion = ""
    if receipted:
        completion = (
            f"acceptance_evidence: [evidence/story-{local_id}.json]\n"
            f"review_record: evidence/story-{local_id}-review.json\n"
            "review_base: 0b29a99\n"
        )
    if chained:
        completion += (
            f"linked_epic: foo/{sub_id}/epic/001\n"
            f"linked_architecture: foo/{sub_id}/architecture/architecture\n"
            f"linked_prd: foo/{sub_id}/prd/prd\n"
        )
    _write(
        project_root / relative,
        "---\nproject_id: foo\nsubproject_id: " + sub_id + "\nrecord_kind: story\n"
        "local_id: " + local_id + "\nstatus: " + status + "\nupdated: " + TODAY + "\n"
        + completion + "---\n\n# Story " + local_id + "\n\n"
        + ("## Acceptance Criteria\n\n- [x] recorded behavior holds\n" if receipted
           else "Work item body.\n"),
    )
    return qualified


def _write_successful_receipt(project_root: Path, qualified: str, relative: str) -> None:
    """Fixture a real successful receipt for one done record (ADR-E data)."""
    record = kosmic_work.SpecCatalog(project_root).resolve(qualified)
    # acceptance/review artifacts the proof validator hashes; schemas
    # are the validator's own constants so the receipt stays truthful
    stem = Path(relative).stem
    _write(
        project_root / "evidence" / (stem + ".json"),
        json.dumps({
            "schema": 'kosmic.acceptance-evidence/1',
            "identity": qualified,
            "record_path": relative,
            "results": [
                {"criterion": "recorded behavior holds", "outcome": "passed"},
            ],
        }, indent=2),
    )
    _write(
        project_root / "evidence" / (stem + "-review.json"),
        json.dumps({
            "schema": 'kosmic.work-review/1',
            "identity": qualified,
            "record_path": relative,
            "review_base": "0b29a99",
            "round": 1,
            "standards": {"decision": "approved", "reviewer": "fixture-reviewer"},
            "spec": {"decision": "approved", "reviewer": "fixture-reviewer"},
            "decision": "approved",
            "findings": [],
        }, indent=2),
    )
    proof = kosmic_completion.validate_completion_proof(project_root, record)
    receipt = {
        "schema": "kosmic.work-receipt/1",
        "identity": qualified,
        "status": "successful",
        "record_path": relative,
        "record_sha256": _sha(record.path.read_bytes()),
        "proof": proof,
    }
    store = project_root / ".kosmic" / "work-receipts"
    store.mkdir(parents=True, exist_ok=True)
    (store / kosmic_dreams.receipt_name(qualified)).write_text(
        json.dumps(receipt, indent=2), encoding="utf-8")
    # fixture self-check: raises unless the receipt validates end to end
    kosmic_completion.check_terminal_receipt(project_root, record)


def _write_fixed_binding(project_root: Path, status_root: Path, sub_id: str) -> None:
    """Registry entry binding the status root to one fixed subproject."""
    resolved = str(status_root.resolve())
    entry = {
        "schema": "kosmic.workdir/1",
        "path": resolved,
        "directory_id": "wd-" + hashlib.sha256(resolved.encode()).hexdigest()[:16],
        "fixed_subproject_id": sub_id,
        "authority": {"record": f"foo/{sub_id}/prd/prd", "run_id": "run-fixture"},
    }
    registry = {
        "schema": "kosmic.workdirs/1",
        "project_id": "foo",
        "sequence": 1,
        "directories": [entry],
    }
    _write(
        project_root / ".kosmic" / "working-directories.json",
        json.dumps(registry, indent=2),
    )


def tree_digest(root: Path, skip: Path) -> dict[str, str]:
    """SHA-256 map of every sandbox file except the derived STATUS target."""
    digest: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink() or not path.is_file() or path == skip:
            continue
        if ".git" in path.relative_to(root).parts:
            continue
        digest[path.relative_to(root).as_posix()] = _sha(path.read_bytes())
    return digest


def status_column(row_line: str) -> str:
    """Rendered status cell of one catalog table row (structural access)."""
    return [cell.strip() for cell in row_line.split("|")][2]


class StatusPlanningAuthorityTest(unittest.TestCase):
    def run_cli(self, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=str(REPO_ROOT),
            env=os.environ.copy(),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            expected,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    @contextmanager
    def sandbox(self, *, bound: bool = True, root_exists: bool = True):
        tmp = tempfile.TemporaryDirectory(prefix="kosmic-status-planning-")
        self.addCleanup(tmp.cleanup)
        worktree = _write_base(Path(tmp.name))
        project_root = worktree / "vault" / "Projects" / "foo"
        project_root.mkdir(parents=True)
        _write_notes(project_root)
        status_root = worktree / "status"
        if root_exists:
            status_root.mkdir()
        if bound:
            _bind_entry(project_root, status_root)
            if root_exists:
                _write(status_root / "STATUS.md", STALE_CONTENT)
        else:
            _bind_entry(project_root, None)
        yield worktree, project_root, status_root

    def refresh(self, project_root: Path, work_record: str,
                expected: int = 0) -> subprocess.CompletedProcess[str]:
        return self.run_cli(
            "generate-status",
            "--project", str(project_root),
            "--work-record", work_record,
            expected=expected,
        )

    def assert_refreshed(self, worktree: Path, project_root: Path,
                         status_root: Path) -> str:
        target = status_root / "STATUS.md"
        before = tree_digest(worktree, target)
        text = target.read_text(encoding="utf-8")
        self.assertNotIn("stale hand edit", text)
        self.assertFalse(status_drift(load_project(project_root)))
        self.assertEqual(before, tree_digest(worktree, target))
        return text

    def row(self, text: str, needle: str) -> str:
        lines = [line for line in text.splitlines()
                 if needle in line and line.lstrip().startswith("|")]
        self.assertEqual(1, len(lines), f"expected exactly one row naming {needle}")
        return lines[0]

    def test_approved_owner_prd_refreshes_bound_status_only(self) -> None:
        """AC1: approved owner PRD drives the ordinary derived STATUS refresh."""
        with self.sandbox() as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="approved")
            self.refresh(project_root, "foo/sub/prd/prd")
            text = self.assert_refreshed(worktree, project_root, status_root)
            # record link identity + recorded status; no title/casing pins
            self.assertIn("subprojects/sub/specs/prd.md", text)
            self.assertEqual(
                "approved", status_column(self.row(text, "subprojects/sub/specs/prd.md")))

    def test_approved_owner_architecture_refreshes_bound_status_only(self) -> None:
        """AC2: an approved Architecture record grants the same single-target refresh."""
        with self.sandbox() as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="approved",
                              architecture_status="approved")
            self.refresh(project_root, "foo/sub/architecture/architecture")
            text = self.assert_refreshed(worktree, project_root, status_root)
            # record link identity + recorded status; no title/casing pins
            self.assertIn("subprojects/sub/specs/architecture.md", text)
            self.assertEqual(
                "approved",
                status_column(self.row(text, "subprojects/sub/specs/architecture.md")))

    def test_draft_record_refreshes_project_wide_render(self) -> None:
        """AC3: a draft planning record authorizes the existing Project-wide
        render through unchanged status-root semantics — its own hierarchy is
        included, other subprojects' rows are not dropped, and a fixed
        subproject binding for its own owner is preserved."""
        with self.sandbox() as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="draft")
            _write_subproject(project_root, "other", prd_status="approved")
            _write_fixed_binding(project_root, status_root, "sub")
            self.refresh(project_root, "foo/sub/prd/prd")
            text = self.assert_refreshed(worktree, project_root, status_root)
            # the record's own hierarchy governs the refresh...
            self.assertIn("sub PRD", text)
            self.assertIn("subprojects/sub/specs/prd.md", text)
            # ...without narrowing the Project-wide derived render
            self.assertIn("other PRD", text)
            self.assertIn("subprojects/other/specs/prd.md", text)

    def test_foreign_planning_record_against_fixed_directory_denied(self) -> None:
        """AC4: a planning record whose ancestry does not govern the bound
        directory (fixed to another subproject) refuses with WORK_PHASE_DENIED
        and writes nothing — draft and approved alike."""
        with self.sandbox() as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="approved")
            _write_subproject(project_root, "other", prd_status="approved")
            _write(
                project_root / "subprojects" / "other" / "specs" / "architecture.md",
                "---\nproject_id: foo\nsubproject_id: other\nrecord_kind: architecture\n"
                "local_id: architecture\nlinked_prd: prd.md\nstatus: approved\n"
                "updated: " + TODAY + "\n---\n\n# other Architecture\n\nBody.\n",
            )
            _write_fixed_binding(project_root, status_root, "sub")
            target = status_root / "STATUS.md"
            before = tree_digest(worktree, target)
            for record in ("foo/other/prd/prd",
                           "foo/other/architecture/architecture"):
                result = self.refresh(project_root, record, expected=2)
                self.assertIn("WORK_PHASE_DENIED", result.stderr)
                self.assertIn("bound to subproject sub", result.stderr)
            self.assertEqual(before, tree_digest(worktree, target))
            self.assertIn("stale hand edit", target.read_text(encoding="utf-8"))

    def test_planning_refresh_requires_bound_status_root(self) -> None:
        """AC5: without a bound status root the refresh refuses and planning
        authority never creates or silently drops a status-root binding."""
        with self.sandbox(bound=False) as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="approved")
            before = tree_digest(worktree, worktree / "nonexistent-target")
            result = self.refresh(project_root, "foo/sub/prd/prd", expected=2)
            self.assertIn("STATUS_ROOT_UNBOUND", result.stderr)
            self.assertEqual(before, tree_digest(worktree, worktree / "nonexistent-target"))
            self.assertFalse((worktree / "status" / "STATUS.md").exists())

    def test_planning_refresh_requires_existing_status_root_directory(self) -> None:
        """AC5: a bound root that is not a directory refuses for any planning
        record; the binding itself is never replaced by the refresh."""
        with self.sandbox(root_exists=False) as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="approved")
            before = tree_digest(worktree, status_root / "STATUS.md")
            result = self.refresh(project_root, "foo/sub/prd/prd", expected=2)
            self.assertIn("STATUS_ROOT_MISSING", result.stderr)
            self.assertEqual(before, tree_digest(worktree, status_root / "STATUS.md"))
            self.assertFalse(status_root.exists())

    def test_implementation_authority_boundary_unchanged(self) -> None:
        """AC6: work start/finish still refuse planning records; the default
        resolve_work_record kinds/statuses are untouched for every other
        caller (quick-task still resolves); no receipt is written or validated
        for a planning record."""
        with self.sandbox() as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="approved")
            _write_quick_task(project_root, "sub", "task")
            result = self.run_cli(
                "work", "start",
                "--project", str(project_root),
                "--worktree", str(worktree),
                "--work-record", "foo/sub/prd/prd",
                expected=2,
            )
            self.assertIn("WORK_PHASE_DENIED", result.stderr)
            result = self.run_cli(
                "work", "finish",
                "--project", str(project_root),
                "--worktree", str(worktree),
                "--work-record", "foo/sub/prd/prd",
                "--scope", f"worktree:{worktree}",
                expected=2,
            )
            self.assertIn("WORK_PHASE_DENIED", result.stderr)
            with self.assertRaises(kosmic_work.WorkdirError) as ctx:
                kosmic_work.resolve_work_record(project_root, "foo/sub/prd/prd")
            self.assertIn("WORK_PHASE_DENIED", str(ctx.exception))
            # positive control: default implementation authorization intact
            resolved = kosmic_work.resolve_work_record(project_root, "foo/sub/quick-task/task")
            self.assertEqual("foo/sub/quick-task/task", resolved.qualified_id)
            # selective matrix: draft quick-task and in-progress prd deny even
            # though the union resolve accepted them
            _write_quick_task(project_root, "sub", "pending", status="draft")
            result = self.refresh(project_root, "foo/sub/quick-task/pending", expected=2)
            self.assertIn("WORK_PHASE_DENIED", result.stderr)
            _write_subproject(project_root, "wip", prd_status="in_progress")
            result = self.refresh(project_root, "foo/wip/prd/prd", expected=2)
            self.assertIn("WORK_PHASE_DENIED", result.stderr)
            # legacy implementation authority still refreshes through this seam
            self.refresh(project_root, "foo/sub/quick-task/task")
            self.assert_refreshed(worktree, project_root, status_root)
            self.assertFalse((project_root / ".kosmic" / "work-receipts").exists())

    def test_receipted_and_unreceipted_rows_render_recorded_state(self) -> None:
        """AC7: with a mixed catalog the regenerated STATUS shows each row's
        actual recorded state — receipted done renders the plain terminal
        status while unreceipted done renders that status plus the pending
        marker (the renderer's open-counting mechanism for pending rows), and
        only the bound STATUS.md is mutated."""
        with self.sandbox() as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="approved",
                              architecture_status="approved", epic_status="approved")
            received = _write_story(project_root, "sub", "002", "done",
                                    receipted=True, chained=True)
            _write_successful_receipt(
                project_root, received, "subprojects/sub/specs/stories/story-002.md")
            _write_story(project_root, "sub", "003", "done", chained=True)
            _write_story(project_root, "sub", "004", "draft", chained=True)
            self.refresh(project_root, "foo/sub/prd/prd")
            text = self.assert_refreshed(worktree, project_root, status_root)
            self.assertEqual("done", status_column(self.row(text, "story-002.md")))
            pending = status_column(self.row(text, "story-003.md"))
            self.assertTrue(pending.startswith("done"))
            self.assertNotEqual("done", pending)
            self.assertEqual("draft", status_column(self.row(text, "story-004.md")))
            self.assertEqual("approved", status_column(self.row(text, "specs/prd.md")))


    def test_draft_hierarchy_records_refresh_through_valid_ancestry(self) -> None:
        """AC3 converse: draft epic and draft story records refresh the
        ordinary derived render through the real CLI when their ancestry chain
        is valid (approved ancestors for stories); an approved epic is NOT a
        grant at this seam, pinning the selective matrix."""
        with self.sandbox() as (worktree, project_root, status_root):
            _write_subproject(project_root, "sub", prd_status="approved",
                              architecture_status="approved", epic_status="approved")
            _write_story(project_root, "sub", "005", "draft", chained=True)
            # a second, draft epic exercises the planning-hierarchy grant
            _write(
                project_root / "subprojects" / "sub" / "specs" / "epics" / "epic-002.md",
                "---\nproject_id: foo\nsubproject_id: sub\nrecord_kind: epic\n"
                "local_id: 002\n"
                "linked_architecture: foo/sub/architecture/architecture\n"
                "linked_prd: foo/sub/prd/prd\n"
                "status: draft\nupdated: " + TODAY + "\n---\n\n"
                "# Sub Draft Epic\n\nDraft hierarchy grant.\n",
            )
            # draft epic: planning-hierarchy grant, no ancestry approval gate
            self.refresh(project_root, "foo/sub/epic/002")
            text = self.assert_refreshed(worktree, project_root, status_root)
            # draft story row present at its recorded status; no title pins
            self.assertIn("subprojects/sub/specs/stories/story-005.md", text)
            self.assertEqual(
                "draft", status_column(self.row(text, "story-005.md")))
            # draft story: planning-hierarchy grant through approved ancestry
            _write(status_root / "STATUS.md", STALE_CONTENT)
            self.refresh(project_root, "foo/sub/story/005")
            self.assert_refreshed(worktree, project_root, status_root)
            # approved epic is not a grant at this seam (selective matrix)
            result = self.refresh(project_root, "foo/sub/epic/001", expected=2)
            self.assertIn("WORK_PHASE_DENIED", result.stderr)


def _write_base(base: Path) -> Path:
    worktree = base / "worktree"
    worktree.mkdir(parents=True)
    subprocess.run(
        ["git", "init", "-q"], cwd=str(worktree), check=True, capture_output=True
    )
    _write(worktree / ".gitignore", ".tmp/\n")
    return worktree


if __name__ == "__main__":
    unittest.main()
