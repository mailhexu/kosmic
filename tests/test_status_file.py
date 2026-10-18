from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from skills.scripts import kosmic_project_skills
from skills.scripts.kosmic_project_skills import (
    assign_project_id,
    generate_status,
    load_project,
    render_status,
    resolve_status_root,
    status_drift,
    update_markdown_metadata,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def build_project(base: Path) -> tuple[Path, Path]:
    worktree = base / "worktree"
    worktree.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=str(worktree), check=True)
    (worktree / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
    vault = worktree / "vault"
    project_root = vault / "Projects" / "foo"
    project_root.mkdir(parents=True)
    entry = project_root / "ProjectEntry.md"
    entry.write_text(
        "---\nproject_id: foo\nworking_state: working-tree\n---\n\n# foo\n", encoding="utf-8"
    )
    (project_root / "notes").mkdir()
    (project_root / "notes" / "index.md").write_text("# Index\n", encoding="utf-8")
    (project_root / "notes" / "stable.md").write_text(
        "---\ntype: Project Knowledge\nstatus: stable\ncreated: 2026-09-27\nupdated: 2026-09-27\naudience: usage\n---\n\n# Stable\n\ntext\n",
        encoding="utf-8",
    )
    specs = project_root / "specs"
    specs.mkdir()
    (specs / "prd-x.md").write_text(
        "---\nstatus: approved\nupdated: 2026-09-20\n---\n\n# PRD X\n", encoding="utf-8"
    )
    (specs / "prd-y.md").write_text(
        "---\nstatus: draft\nupdated: 2026-09-21\n---\n\n# PRD Y\n", encoding="utf-8"
    )
    (specs / "epics").mkdir()
    (specs / "epics" / "epic-1-a.md").write_text(
        "---\nstatus: done\nupdated: 2026-09-22\n---\n\n# Epic 1\n", encoding="utf-8"
    )
    (specs / "stories").mkdir()
    (specs / "stories" / "story-001-a.md").write_text(
        "---\nstatus: in_progress\nupdated: 2026-09-23\n---\n\n# Story 1\n", encoding="utf-8"
    )
    (specs / "quick-tasks").mkdir()
    (specs / "quick-tasks" / "2026-09-01-q.md").write_text(
        "---\nproject_id: foo\nrecord_kind: quick-task\nlocal_id: q\nsubproject_id: null\nstatus: approved\nupdated: 2026-09-23\n---\n\n# Quick\n", encoding="utf-8"
    )
    (specs / "skill-proposals").mkdir()
    (specs / "skill-proposals" / "2026-09-02-p.md").write_text(
        "---\nstatus: approved\ndecision: pending\nupdated: 2026-09-24\n---\n\n# Proposal\n", encoding="utf-8"
    )
    (worktree / "STATUS.md").write_text("stale\n", encoding="utf-8")
    return worktree, project_root


class StatusCoreTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-status-")
        self.worktree, self.project_root = build_project(Path(self.tmp.name))
        self.project = load_project(self.project_root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_render_is_deterministic_and_complete(self) -> None:
        entry = self.project_root / "ProjectEntry.md"
        entry.write_text(
            update_markdown_metadata(
                entry.read_text(encoding="utf-8"), {"status_root": str(self.worktree.resolve())}
            ),
            encoding="utf-8",
        )
        self.project = load_project(self.project_root)
        first = render_status(self.project, "head0")
        second = render_status(self.project, "head0")
        self.assertEqual(first, second)
        text = first.decode("utf-8")
        self.assertIn("# Status: foo", text)
        self.assertIn("Vault HEAD: head0", text)
        self.assertIn("| [PRD X](vault/Projects/foo/specs/prd-x.md) | approved | 2026-09-20 |", text)
        self.assertIn("| [PRD Y](vault/Projects/foo/specs/prd-y.md) | draft | 2026-09-21 |", text)
        self.assertNotIn("INDEX", text)
        self.assertIn("- 4 open item(s)", text)
        self.assertIn("[Story 1](vault/Projects/foo/specs/stories/story-001-a.md) - in_progress", text)
        self.assertIn("[PRD Y]", text)
        open_section = text.split("## Open Work", 1)[1]
        self.assertIn("[Story 1]", open_section)
        self.assertIn("[PRD Y]", open_section)
        self.assertIn("[Proposal]", open_section)
        self.assertNotIn("[Epic 1]", open_section)
        self.assertIn("[Quick]", open_section)

    def test_generate_writes_bound_root_and_drift_detection(self) -> None:
        binding = self.worktree
        entry = self.project_root / "ProjectEntry.md"
        entry.write_text(
            update_markdown_metadata(
                entry.read_text(encoding="utf-8"), {"status_root": str(binding)}
            ),
            encoding="utf-8",
        )
        project = load_project(self.project_root)
        self.assertTrue(status_drift(project))
        path = generate_status(project, work_record="foo/quick-task/q")
        self.assertEqual(path, binding / "STATUS.md")
        self.assertFalse(status_drift(project))
        (self.project_root / "specs" / "stories" / "story-001-a.md").write_text(
            "---\nstatus: done\nupdated: 2026-09-25\n---\n\n# Story 1\n", encoding="utf-8"
        )
        self.assertTrue(status_drift(project))

    def test_unbound_fails_closed(self) -> None:
        with self.assertRaises(kosmic_project_skills.KosmicError) as ctx:
            generate_status(load_project(self.project_root), work_record="foo/quick-task/q")
        self.assertIn("STATUS_ROOT_UNBOUND", str(ctx.exception))

    def test_binding_resolution_and_collision(self) -> None:
        resolved = resolve_status_root(self.worktree, project=self.project_root)
        self.assertEqual(resolved, self.worktree.resolve())
        entry = self.project_root / "ProjectEntry.md"
        entry.write_text(
            update_markdown_metadata(
                entry.read_text(encoding="utf-8"), {"status_root": str(self.worktree.resolve())}
            ),
            encoding="utf-8",
        )
        sibling_root = self.project_root.parent / "bar"
        sibling_root.mkdir()
        (sibling_root / "ProjectEntry.md").write_text(
            "---\nproject_id: bar\nworking_state: working-tree\nstatus_root: %s\n---\n" % self.worktree.resolve(),
            encoding="utf-8",
        )
        with self.assertRaises(kosmic_project_skills.KosmicError) as ctx:
            resolve_status_root(self.worktree, project=sibling_root)
        self.assertIn("STATUS_ROOT_COLLISION", str(ctx.exception))


class AssignMigrationTest(unittest.TestCase):
    def test_assign_project_id_with_status_root(self) -> None:
        tmp = tempfile.TemporaryDirectory(prefix="kosmic-status-")
        try:
            worktree = Path(tmp.name) / "wt"
            worktree.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=str(worktree), check=True)
            root = worktree / "vault" / "Projects" / "foo"
            root.mkdir(parents=True)
            (root / "notes").mkdir()
            (root / "notes" / "index.md").write_text("# Index\n", encoding="utf-8")
            (root / "notes" / "stable.md").write_text(
                "---\ntype: Project Knowledge\nstatus: stable\ncreated: 2026-09-27\nupdated: 2026-09-27\naudience: usage\n---\n\n# Stable\n\ntext\n",
                encoding="utf-8",
            )
            project = assign_project_id(root, "foo", status_root=worktree)
            self.assertEqual(project.status_root, worktree.resolve())
            entry = root / "ProjectEntry.md"
            self.assertIn(f"status_root: {worktree.resolve()}", entry.read_text())
        finally:
            tmp.cleanup()


if __name__ == "__main__":
    unittest.main()


class GateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-status-")
        self.worktree, self.project_root = build_project(Path(self.tmp.name))
        entry = self.project_root / "ProjectEntry.md"
        entry.write_text(
            update_markdown_metadata(
                entry.read_text(encoding="utf-8"), {"status_root": str(self.worktree.resolve())}
            ),
            encoding="utf-8",
        )
        self.project = load_project(self.project_root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_completion_gate_blocks_on_drift_for_non_interface_work(self) -> None:
        work_item = self.project_root / "specs" / "stories" / "story-001-a.md"
        with self.assertRaises(kosmic_project_skills.KosmicError) as ctx:
            kosmic_project_skills.check_completion(self.project, work_item)
        self.assertIn("STATUS_STALE", str(ctx.exception))
        generate_status(self.project, work_record="foo/quick-task/q")
        try:
            kosmic_project_skills.check_completion(self.project, work_item)
        except kosmic_project_skills.KosmicError as error:
            self.assertNotIn("STATUS_STALE", str(error))

    def test_validate_collision_scan(self) -> None:
        sibling = self.project_root.parent / "bar"
        sibling.mkdir()
        (sibling / "ProjectEntry.md").write_text(
            "---\nproject_id: bar\nworking_state: working-tree\nstatus_root: %s\n---\n"
            % self.worktree.resolve(),
            encoding="utf-8",
        )
        collisions = kosmic_project_skills.status_root_collisions(self.project)
        self.assertEqual(len(collisions), 1)
        self.assertIn("foo", collisions[0] + "bar")

    def test_write_failure_code(self) -> None:
        locked = self.worktree / "locked"
        locked.mkdir()
        entry = self.project_root / "ProjectEntry.md"
        entry.write_text(
            update_markdown_metadata(
                entry.read_text(encoding="utf-8"), {"status_root": str(locked)}
            ),
            encoding="utf-8",
        )
        locked.chmod(0o555)
        try:
            with self.assertRaises(kosmic_project_skills.KosmicError) as ctx:
                kosmic_project_skills.generate_status(load_project(self.project_root), work_record="foo/quick-task/q")
        finally:
            locked.chmod(0o755)
        self.assertIn("STATUS_WRITE_FAILED", str(ctx.exception))
