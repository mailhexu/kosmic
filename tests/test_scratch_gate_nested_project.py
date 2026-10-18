"""Reproduce the scratch-begin gate ValueError when --project is a nested
Project directory (its Git toplevel is an ancestor).

Run: python3 tests/test_scratch_gate_nested_project.py
Red today; green after the fix. No third-party deps; stdlib only.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "skills/scripts/kosmic_project_skills.py"


class ScratchGateNestedProjectTest(unittest.TestCase):
    """scratch begin --project <nested Project> must not crash with ValueError."""

    def test_gate_reports_typed_error_not_valueerror(self) -> None:
        with tempfile.TemporaryDirectory(prefix="scratch-gate-nested-", dir=ROOT) as tmp:
            project = Path(tmp)
            (project / "ProjectEntry.md").write_text(
                "---\nproject_id: scratchnested\n---\n\n# Scratch nested\n",
                encoding="utf-8")
            task = project / "specs/quick-tasks/scratch.md"
            task.parent.mkdir(parents=True)
            task.write_text(
                "---\nproject_id: scratchnested\nsubproject_id: null\n"
                "record_kind: quick-task\nlocal_id: scratch\nstatus: approved\n"
                "consumer_interface_change: false\n---\n\n# Scratch gate fixture\n",
                encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "scratch", "begin",
                 "--project", str(project), "--purpose", "gate-regression",
                 "--work-record", "specs/quick-tasks/scratch.md"],
                capture_output=True, text=True, cwd=ROOT, timeout=60,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertNotIn("ValueError", result.stderr, result.stderr)
            self.assertNotIn("Traceback", result.stderr, result.stderr)
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["code"], "OK")
            run_path = Path(payload["path"])
            self.assertTrue(run_path.is_relative_to(ROOT / ".tmp/kosmic/runs"), run_path)
            self.assertEqual(Path(payload["scratch_path"]), run_path / "scratch")
            self._finish(payload["handle_file"], project)

    def _finish(self, handle: str, project: Path) -> None:
        result = subprocess.run(
            [sys.executable, str(CLI), "scratch", "succeed", "--project", str(project),
             "--handle-file", handle],
            capture_output=True, text=True, cwd=ROOT, timeout=60,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_work_record_is_a_typed_error_for_nested_project(self) -> None:
        with tempfile.TemporaryDirectory(prefix="scratch-gate-no-record-", dir=ROOT) as tmp:
            project = Path(tmp)
            result = subprocess.run(
                [sys.executable, str(CLI), "scratch", "begin",
                 "--project", str(project), "--purpose", "missing-record-regression"],
                capture_output=True, text=True, cwd=ROOT, timeout=60,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("WORK_RECORD_REQUIRED", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_flattened_project_still_begins_under_its_git_root(self) -> None:
        """The fallback preserves the original flat-project path behavior."""
        with tempfile.TemporaryDirectory(prefix="scratch-gate-flat-") as tmp:
            flat = Path(tmp) / "flat-project"
            flat.mkdir()
            subprocess.run(["git", "init", "-q", str(flat)], check=True, capture_output=True)
            (flat / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
            (flat / "ProjectEntry.md").write_text(
                "---\nproject_id: scratchflat\n---\n\n# Scratch flat\n", encoding="utf-8")
            quick_task = flat / "specs/quick-tasks/scratch.md"
            quick_task.parent.mkdir(parents=True)
            quick_task.write_text(
                "---\nproject_id: scratchflat\nsubproject_id: null\n"
                "record_kind: quick-task\nlocal_id: scratch\nstatus: approved\n"
                "consumer_interface_change: false\n---\n\n# Scratch gate fixture\n",
                encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(CLI), "scratch", "begin",
                 "--project", str(flat), "--purpose", "flat-regression",
                 "--work-record", "specs/quick-tasks/scratch.md"],
                capture_output=True, text=True, cwd=ROOT, timeout=60,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["code"], "OK")
            self.assertTrue(Path(payload["path"]).is_relative_to(flat / ".tmp/kosmic/runs"))
            self._finish(payload["handle_file"], flat)


if __name__ == "__main__":
    unittest.main()
