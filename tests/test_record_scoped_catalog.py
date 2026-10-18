"""Record-bound SpecCatalog resolution and bounded STATUS publication.

The work-record seam authorizes one record from its owner subproject plus
the shared records; an unrelated subproject with a missing SubprojectEntry
must never block record-bound commands, while every full-catalog audit
(valid, unscoped render/generate-status) stays strict and still fails on
the same defect.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import unittest
from pathlib import Path

try:
    from skills.scripts import kosmic_completion
    from skills.scripts import kosmic_project_skills as cli
    from skills.scripts import kosmic_work
    from skills.scripts.kosmic_specs import SpecCatalog, SpecError
except ImportError:  # direct test-directory execution
    import kosmic_completion
    import kosmic_project_skills as cli
    import kosmic_work
    from kosmic_specs import SpecCatalog, SpecError

try:
    from tests.scoped_completion_support import ScopedProjectCase
except ImportError:  # direct test-directory execution
    from scoped_completion_support import ScopedProjectCase

PROJECT_ID = "scope-demo"
OWNER = "siesta"
UNRELATED = "abinit"
STORY = f"{PROJECT_ID}/{OWNER}/story/009"
SHARED_TASK = f"{PROJECT_ID}/quick-task/fixture-task"
STORY_RELATIVE = f"subprojects/{OWNER}/specs/stories/story-009.md"
RECEIPTS = ".kosmic/work-receipts"


def write_document(path: Path, metadata: dict, title: str = "Record") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n" + "".join(f"{key}: {json.dumps(value)}\n" for key, value in metadata.items())
        + f"---\n\n# {title}\n", encoding="utf-8",
    )
    return path


def feature(root: Path, project_id: str, owner: str, number: str = "009",
            status: str = "approved") -> Path:
    """One valid owned subproject: entry plus prd/architecture/epic/story."""
    base = root / "subprojects" / owner
    write_document(base / "SubprojectEntry.md", {
        "schema": "kosmic.subproject/1", "project_id": project_id,
        "subproject_id": owner, "title": owner, "linked_prd": "specs/prd.md",
    })
    common = {"project_id": project_id, "subproject_id": owner, "status": status}
    specs = base / "specs"
    write_document(specs / "prd.md",
                   {**common, "record_kind": "prd", "local_id": "prd"}, f"{owner} PRD")
    write_document(specs / "architecture.md",
                   {**common, "record_kind": "architecture", "local_id": "architecture",
                    "linked_prd": "prd.md"}, f"{owner} Architecture")
    write_document(specs / "epics" / f"epic-{number}.md",
                   {**common, "record_kind": "epic", "local_id": number,
                    "linked_architecture": "../architecture.md", "linked_prd": "../prd.md"},
                   f"{owner} Epic")
    story = write_document(specs / "stories" / f"story-{number}.md",
                           {**common, "record_kind": "story", "local_id": number,
                            "depends_on": [], "linked_epic": f"../epics/epic-{number}.md",
                            "linked_architecture": "../architecture.md",
                            "linked_prd": "../prd.md"}, f"{owner} Story")
    return story


def broken_vault(case) -> None:
    """Two valid owned subprojects plus one unrelated missing entry."""
    (case.project / "subprojects" / UNRELATED).mkdir(parents=True)
    case.story = feature(case.project, PROJECT_ID, OWNER)
    case.quantum_story = feature(case.project, PROJECT_ID, "quantum", number="001")
    subprocess.run(["git", "add", "-A"], cwd=str(case.root), check=True,
                   capture_output=True)
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t",
                    "commit", "-qm", "fixture"], cwd=str(case.root), check=True,
                   capture_output=True)


def bind_status_root(case) -> Path:
    """Bind an absolute status_root output directory on the Project entry."""
    output = case.root / "status-output"
    output.mkdir(exist_ok=True)
    entry = case.project / "ProjectEntry.md"
    entry.write_text(
        f"---\nproject_id: {PROJECT_ID}\nworking_state: working-tree\n"
        f"status_root: {output.as_posix()}\n---\n# Demo\n", encoding="utf-8",
    )
    return output


class RecordScopedCatalogTest(ScopedProjectCase):
    """Bounded record resolution and STATUS publication on a broken vault."""

    def setUp(self):
        super().setUp()
        broken_vault(self)

    def bind_status_root(self):
        self.output = bind_status_root(self)

    def set_story_status(self, status: str):
        text = self.story.read_text(encoding="utf-8")
        self.story.write_text(
            text.replace(f"status: \"approved\"", f"status: \"{status}\"", 1),
            encoding="utf-8",
        )

    def test_bounded_resolution_ignores_unrelated_missing_subproject_entry(self):
        record = kosmic_work.resolve_work_record(self.project, STORY)
        self.assertEqual(record.qualified_id, STORY)
        self.assertEqual(record.kind, "story")
        by_path = kosmic_work.resolve_work_record(self.project, STORY_RELATIVE)
        self.assertEqual(by_path.qualified_id, STORY)
        bounded = SpecCatalog.bounded(self.project, OWNER)
        identities = {item.qualified_id for item in bounded.records}
        self.assertIn(STORY, identities)
        self.assertIn(f"{PROJECT_ID}/quick-task/fixture-task", identities)
        self.assertTrue(all(item.subproject_id in (None, OWNER) for item in bounded.records))
        shared = SpecCatalog.bounded(self.project, None)
        self.assertTrue(all(item.subproject_id is None for item in shared.records))

    def test_bounded_view_surfaces_owner_entry_defects_without_swallowing(self):
        with self.assertRaises(SpecError) as caught:
            SpecCatalog.bounded(self.project, UNRELATED)
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        self.assertIn(UNRELATED, caught.exception.detail)
        unknown = SpecCatalog.bounded(self.project, "missing-owner")
        self.assertNotIn(STORY, {item.qualified_id for item in unknown.records})

    def test_full_validate_and_unscoped_render_stay_strict(self):
        with self.assertRaises(SpecError) as caught:
            SpecCatalog(self.project)
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        self.assertIn(UNRELATED, caught.exception.detail)
        with self.assertRaises(SpecError):
            cli.render_status(cli.load_project(self.project), "head0")

    def test_bounded_status_publication_marks_scope_honestly(self):
        self.bind_status_root()
        kosmic_completion._write_status_reports(self.project, OWNER)
        text = (self.output / "STATUS.md").read_text(encoding="utf-8")
        self.assertIn("bounded active-record view", text)
        self.assertIn("not a full-catalog audit", text)
        self.assertNotIn("Project-wide", text)
        self.assertIn("### Subproject: siesta", text)
        self.assertIn("siesta Story", text)
        self.assertIn("### Project", text)
        self.assertIn("Fixture", text)
        self.assertNotIn("quantum Story", text)

    def test_full_status_publication_unchanged_when_catalog_healthy(self):
        self.bind_status_root()
        (self.project / "subprojects" / UNRELATED).rmdir()
        kosmic_completion._write_status_reports(self.project, OWNER)
        text = (self.output / "STATUS.md").read_text(encoding="utf-8")
        self.assertIn("Project-wide", text)
        self.assertNotIn("bounded active-record view", text)
        self.assertIn("quantum Story", text)
        self.assertIn("siesta Story", text)

    def test_bounded_publication_keeps_unrelated_fixed_directory_report(self):
        self.bind_status_root()
        quantum_tree = self.root / "quantum-worktree"
        quantum_tree.mkdir()
        (quantum_tree / "STATUS.md").write_text("quantum report\n", encoding="utf-8")
        registry = {
            "schema": "kosmic.workdirs/1",
            "project_id": PROJECT_ID,
            "sequence": 1,
            "directories": [{
                "schema": "kosmic.workdir/1",
                "path": str(quantum_tree),
                "directory_id": "wd-" + hashlib.sha256(str(quantum_tree).encode()).hexdigest()[:16],
                "fixed_subproject_id": "quantum",
                "registered_at": "2026-10-15T00:00:00Z",
                "authority": {"record": STORY, "run_id": "run-fixture"},
            }],
        }
        control = self.project / ".kosmic"
        control.mkdir(exist_ok=True)
        (control / "working-directories.json").write_text(
            json.dumps(registry, indent=2) + "\n", encoding="utf-8")
        kosmic_completion._write_status_reports(self.project, OWNER)
        self.assertEqual((quantum_tree / "STATUS.md").read_text(encoding="utf-8"),
                         "quantum report\n")
        self.assertIn("bounded active-record view",
                      (self.output / "STATUS.md").read_text(encoding="utf-8"))

    def test_bounded_ancestry_violations_still_refused(self):
        text = self.story.read_text(encoding="utf-8")
        self.story.write_text(
            text.replace('linked_epic: "../epics/epic-009.md"',
                         'linked_epic: "../epics/epic-404.md"'), encoding="utf-8")
        with self.assertRaises((kosmic_work.WorkdirError, SpecError)) as caught:
            kosmic_work.resolve_work_record(self.project, STORY)
        self.assertEqual(caught.exception.code, "ANCESTRY_INVALID")
        result = self.run_cli("work", "start", "--project", self.project,
                              "--worktree", self.root / "tree",
                              "--work-record", STORY)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ANCESTRY_INVALID", result.stderr)

    def test_bounded_duplicate_detection_is_preserved(self):
        write_document(self.story.parent / "story-009-followup.md",
                       {"project_id": PROJECT_ID, "subproject_id": OWNER,
                        "status": "approved", "record_kind": "story", "local_id": "009",
                        "depends_on": [], "linked_epic": "../epics/epic-009.md",
                        "linked_architecture": "../architecture.md",
                        "linked_prd": "../prd.md"})
        with self.assertRaises(kosmic_work.WorkdirError) as caught:
            kosmic_work.resolve_work_record(self.project, STORY)
        self.assertEqual(caught.exception.code, "RECORD_INVALID")
        self.assertIn("DUPLICATE_RECORD", str(caught.exception))

    def test_done_refusal_for_work_start_is_preserved(self):
        self.set_story_status("done")
        with self.assertRaises(kosmic_work.WorkdirError) as caught:
            kosmic_work.resolve_work_record(self.project, STORY)
        self.assertEqual(caught.exception.code, "WORK_PHASE_DENIED")
        repaired = kosmic_work.resolve_work_record(self.project, STORY, allow_terminal=True)
        self.assertEqual(repaired.status, "done")
        result = self.run_cli("work", "start", "--project", self.project,
                              "--worktree", self.root / "tree",
                              "--work-record", STORY)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("WORK_PHASE_DENIED", result.stderr)

    def test_check_math_update_reaches_phase_gate_not_record_invalid(self):
        self.set_story_status("done")
        result = self.run_cli("check-math", "--project", self.project, "--update",
                              "--work-record", STORY)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("WORK_PHASE_DENIED", result.stderr)
        self.assertNotIn("RECORD_INVALID", result.stderr)
        self.assertNotIn("SCOPE_DENIED", result.stderr)


class RecordBoundCompletionTest(ScopedProjectCase):
    """Record-bound completion gates and STATUS drift on the broken vault."""

    def setUp(self):
        super().setUp()
        broken_vault(self)
        self.work_item = (self.project / "subprojects" / OWNER
                          / "specs/stories/story-009.md")

    def set_record_status(self, status: str):
        text = self.work_item.read_text(encoding="utf-8")
        self.work_item.write_text(
            text.replace('status: "approved"', f'status: "{status}"', 1),
            encoding="utf-8",
        )

    def test_check_completion_reaches_acceptance_gate(self):
        result = self.run_cli("check-completion", "--project", self.project,
                              "--work-item", self.work_item,
                              "--work-record", STORY)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ACCEPTANCE_INVALID", result.stderr)
        self.assertNotIn("SCOPE_DENIED", result.stderr)
        self.assertNotIn("RECORD_INVALID", result.stderr)

    def test_done_record_gates_resolve_to_receipt_check(self):
        self.set_record_status("done")
        with self.assertRaises(kosmic_completion.work.WorkdirError) as caught:
            kosmic_completion.check_completion_gates(self.project, self.work_item,
                                                     self.root)
        self.assertEqual(caught.exception.code, "COMPLETION_PENDING")

    def test_record_bound_drift_uses_bounded_publication_view(self):
        output = bind_status_root(self)
        kosmic_completion._write_status_reports(self.project, OWNER)
        project = cli.load_project(self.project)
        self.assertFalse(cli.status_drift(project, record_scoped=True,
                                          record_owner=OWNER))
        text = self.work_item.read_text(encoding="utf-8")
        self.work_item.write_text(
            text.replace('status: "approved"', 'status: "in_progress"'), encoding="utf-8")
        self.assertTrue(cli.status_drift(project, record_scoped=True,
                                         record_owner=OWNER))
        (output / "STATUS.md").unlink()
        self.assertTrue(cli.status_drift(project, record_scoped=True,
                                         record_owner=OWNER))
        with self.assertRaises(SpecError):
            cli.status_drift(project)

    def test_record_bound_completion_passes_drift_to_record_checks(self):
        bind_status_root(self)
        kosmic_completion._write_status_reports(self.project, OWNER)
        project = cli.load_project(self.project)
        with self.assertRaises(cli.KosmicError) as caught:
            cli._check_existing_completion(project, self.work_item, self.root,
                                           record_scoped=True, record_owner=OWNER)
        message = str(caught.exception)
        self.assertNotIn("STATUS_STALE", message)
        self.assertNotIn("SCOPE_DENIED", message)
        with self.assertRaises(SpecError):
            cli._check_existing_completion(project, self.work_item, self.root)

    def test_shared_record_drift_uses_shared_bounded_view(self):
        output = bind_status_root(self)
        shared_item = self.project / "specs/quick-tasks/fixture-task.md"
        kosmic_completion._write_status_reports(self.project, None)
        project = cli.load_project(self.project)
        self.assertFalse(cli.status_drift(project, record_scoped=True, record_owner=None))
        text = shared_item.read_text(encoding="utf-8")
        shared_item.write_text(
            text.replace("status: approved\n", "status: in_progress\n"), encoding="utf-8")
        self.assertTrue(cli.status_drift(project, record_scoped=True, record_owner=None))
        (output / "STATUS.md").unlink()
        self.assertTrue(cli.status_drift(project, record_scoped=True, record_owner=None))
        with self.assertRaises(SpecError):
            cli.status_drift(project)

    def test_shared_record_completion_refuses_on_own_gates(self):
        bind_status_root(self)
        kosmic_completion._write_status_reports(self.project, None)
        shared_item = self.project / "specs/quick-tasks/fixture-task.md"
        project = cli.load_project(self.project)
        with self.assertRaises(cli.KosmicError) as caught:
            cli._check_existing_completion(project, shared_item, self.root,
                                           record_scoped=True, record_owner=None)
        message = str(caught.exception)
        self.assertNotIn("STATUS_STALE", message)
        self.assertNotIn("SCOPE_DENIED", message)
        result = self.run_cli("check-completion", "--project", self.project,
                              "--work-item", shared_item,
                              "--work-record", SHARED_TASK)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ACCEPTANCE_INVALID", result.stderr)
        self.assertNotIn("SCOPE_DENIED", result.stderr)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
