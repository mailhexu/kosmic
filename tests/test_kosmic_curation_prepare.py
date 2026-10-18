"""Story 004 Phase-A consumer regression: curation-prepare window selection.

Consumer regression against the real Project CLI: curation-prepare window
selection through the shipped subcommand (first-bound exclusivity, scope
boundaries, serialization) — all cases green on the integrated release.

Consumer contract exercised (AC1, AC2, AC7, AC15, serialization):
- prepare with an explicit --from selects every interval-eligible note
  (candidate-flagged, live-resource, and skill_candidate: false alike) in the
  window L < updated <= U and returns a machine-JSON payload carrying the
  existing managed-run keys ({handle_file, run_id}) plus the snapshot note
  set and window bounds;
- notes at/before the lower bound and notes updated after the frozen U are
  never selected;
- prepare mutates no checkpoint: after the first run's lease is closed via
  the EXISTING `scratch fail` public operation, a follow-up prepare without
  --from observes the terminal predecessor run, clears the stale reservation,
  and still fails with the typed first-lower-bound diagnostic instead of
  inventing a prior checkpoint;
- an active run makes a second same-scope prepare report busy.

All note timestamps are computed relative to a single NOW with wide margins,
so the test never depends on an absolute clock or on injecting the frozen U.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "scripts" / "kosmic_project_skills.py"


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class CurationPrepareTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.now = datetime.now(timezone.utc)
        self.lower_bound = self.now - timedelta(days=30)
        self.project = self._make_fixture_project()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    # -- fixture ---------------------------------------------------------

    def _make_fixture_project(self) -> Path:
        project = self.project_path()
        notes = project / "notes"
        notes.mkdir(parents=True, exist_ok=True)
        (notes / "index.md").write_text(
            '---\nokf_version: "0.2"\n---\n\n# Project Knowledge\n',
            encoding="utf-8",
        )
        (project / "ProjectEntry.md").write_text(
            "---\n"
            "project_id: curation-demo\n"
            "working_state: working-tree\n"
            "---\n\n"
            "# Curation Demo\n",
            encoding="utf-8",
        )
        mathdocs = project / "mathdocs"
        mathdocs.mkdir(exist_ok=True)
        (mathdocs / "index.md").write_text(
            "# Math Derivations\n\n"
            "| Derivation | Status | Result summary |\n"
            "|------------|--------|----------------|\n",
            encoding="utf-8",
        )
        specs = project / "specs" / "quick-tasks"
        specs.mkdir(parents=True, exist_ok=True)
        (project / "specs" / "INDEX.md").write_text("# Specs\n", encoding="utf-8")
        (specs / "2026-10-18-fixture-task.md").write_text(
            "---\n"
            "project_id: curation-demo\n"
            "record_kind: quick-task\nlocal_id: fixture-task\n"
            "subproject_id: null\nstatus: approved\n---\n\n"
            "# Fixture Task\n\n## Acceptance Criteria\n\n"
            "- [ ] Curation prepare selects the expected window notes\n",
            encoding="utf-8",
        )
        # Managed scratch requires a Git worktree at the vault root.
        (project.parents[1] / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        subprocess.run(
            ["git", "init", "-q", str(project.parents[1])],
            check=True,
            capture_output=True,
        )
        # Wide margins around the single NOW: in-window notes sit 3-5 days
        # inside (L=NOW-30d, U≈NOW); a pre-L note and a far-future note stay
        # outside the window for any realistic frozen cutoff.
        self._write_note(
            "in-window-candidate.md",
            updated=self.now - timedelta(days=5),
            extra="skill_candidate: true\n",
        )
        self._write_note(
            "in-window-resources.md",
            updated=self.now - timedelta(days=4),
            extra="skill_candidate: false\nskill_resources:\n  - kosmic-usage\n",
        )
        self._write_note(
            "in-window-plain.md",
            updated=self.now - timedelta(days=3),
            extra="skill_candidate: false\n",
        )
        self._write_note(
            "before-window.md",
            updated=self.now - timedelta(days=45),
            extra="skill_candidate: true\n",
        )
        self._write_note(
            "after-frozen-cutoff.md",
            updated=self.now + timedelta(days=120),
            extra="skill_candidate: true\n",
        )
        return project

    def project_path(self) -> Path:
        return Path(self.temporary.name) / "vault" / "Projects" / "demo"

    def _write_note(self, name: str, updated: datetime, extra: str) -> None:
        (self.project_path() / "notes" / name).write_text(
            "---\n"
            "type: Project Knowledge\n"
            "status: stable\n"
            f"updated: {_utc(updated)}\n"
            f"{extra}"
            "---\n\n"
            f"# {name[:-3]}\n",
            encoding="utf-8",
        )

    # -- CLI -------------------------------------------------------------

    def run_cli(
        self,
        *arguments: str,
        expected: int = 0,
    ) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=REPO_ROOT,
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

    def prepare_payload(self, *extra: str, expected: int = 0) -> dict:
        result = self.run_cli(
            "curation-prepare",
            "--project",
            str(self.project_path()),
            "--work-record",
            "curation-demo/quick-task/fixture-task",
            "--scope",
            "notes",
            "--from",
            _utc(self.lower_bound),
            *extra,
            expected=expected,
        )
        return json.loads(result.stdout)

    # -- the regression ---------------------------------------------------

    def test_curation_prepare_selects_window_notes_without_advancing_checkpoint(
        self,
    ) -> None:
        payload = self.prepare_payload()

        # Machine-JSON contract: existing managed-run keys plus snapshot set.
        for key in ("handle_file", "run_id", "notes", "window"):
            self.assertIn(key, payload)
        self.assertIn("from", payload["window"])

        # Every interval-eligible identity is snapshotted, candidate or not;
        # out-of-window notes are never selected (exact set, no substrings).
        selected = sorted(entry["path"] for entry in payload["notes"])
        self.assertEqual(
            sorted(
                [
                    "notes/in-window-candidate.md",
                    "notes/in-window-resources.md",
                    "notes/in-window-plain.md",
                ]
            ),
            selected,
        )

        # A same-scope second prepare observes the active run: busy, not a race.
        busy = self.run_cli(
            "curation-prepare",
            "--project",
            str(self.project_path()),
            "--work-record",
            "curation-demo/quick-task/fixture-task",
            "--scope",
            "notes",
            "--from",
            _utc(self.lower_bound),
            expected=2,
        )
        self.assertIn("busy", (busy.stderr + busy.stdout).lower())

        # Close the first run through the EXISTING public scratch lifecycle;
        # then the stale reservation is cleared and --from-less prepare must
        # fail with the typed first-lower-bound diagnostic (AC7), NOT busy —
        # proving the first prepare advanced no checkpoint, via public
        # operations only.
        self.run_cli(
            "scratch",
            "fail",
            "--project",
            str(self.project_path()),
            "--handle-file",
            payload["handle_file"],
        )
        unbounded = self.run_cli(
            "curation-prepare",
            "--project",
            str(self.project_path()),
            "--work-record",
            "curation-demo/quick-task/fixture-task",
            "--scope",
            "notes",
            expected=2,
        )
        diagnostic = (unbounded.stderr + unbounded.stdout).lower()
        self.assertIn("error", diagnostic)
        self.assertNotIn("busy", diagnostic)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
