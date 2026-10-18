"""Story 004 curation stage regressions: fixed-clock windows, serialization,
review-record authority, coverage, and drift (API level with injected clocks).

These regressions exercise the public curation functions directly so the
frozen cutoff can be pinned deterministically (``now`` injection is a test
seam on the public function only — the CLI passes real time and there is no
production clock backdoor). The consumer CLI behavior is covered separately
in ``test_kosmic_curation_prepare.py``.
"""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from skills.scripts.kosmic_curation import (
    CURATION_SCOPES,
    CurationError,
    finalize_curation,
    prepare_curation,
)
from skills.scripts.kosmic_project_skills import (
    update_markdown_metadata,
)

PROJECT_ID = "curation-demo"
RECORD_REF = f"{PROJECT_ID}/quick-task/fixture-task"


def _utc(moment: datetime) -> str:
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class CurationStageCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.now = datetime(2026, 10, 18, 12, 0, 0, tzinfo=timezone.utc)
        self.project = self._make_fixture_project()
        self.handles: list[str] = []

    def tearDown(self) -> None:
        # Close any run this test left leased, through the public lifecycle,
        # so the in-process holder releases before the fixture tree vanishes.
        from skills.scripts.kosmic_runs import finish_run

        for handle in self.handles:
            try:
                finish_run(Path(handle), "failed", detail="test teardown")
            except Exception:
                pass
        self.temporary.cleanup()

    # -- fixture ---------------------------------------------------------

    def _make_fixture_project(self) -> Path:
        project = self.root / "vault" / "Projects" / "demo"
        notes = project / "notes"
        notes.mkdir(parents=True, exist_ok=True)
        (notes / "index.md").write_text(
            '---\nokf_version: "0.2"\n---\n\n# Project Knowledge\n', encoding="utf-8"
        )
        (project / "ProjectEntry.md").write_text(
            "---\n"
            f"project_id: {PROJECT_ID}\n"
            "working_state: working-tree\n"
            "---\n\n# Curation Demo\n",
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
            f"project_id: {PROJECT_ID}\n"
            "record_kind: quick-task\nlocal_id: fixture-task\n"
            "subproject_id: null\nstatus: approved\n"
            "curation_review: null\n---\n\n"
            "# Fixture Task\n\n## Acceptance Criteria\n\n- [ ] curation window\n",
            encoding="utf-8",
        )
        (project.parents[1] / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        subprocess.run(
            ["git", "init", "-q", str(project.parents[1])], check=True, capture_output=True
        )
        return project

    def write_note(
        self,
        name: str,
        updated: str,
        *,
        created: str | None = None,
        candidate: bool | None = None,
        resources: list[str] | None = None,
        body: str = "body",
    ) -> Path:
        lines = ["---", "type: Project Knowledge", "status: stable"]
        if updated is not None:
            lines.append(f"updated: {updated}")
        if created is not None:
            lines.append(f"created: {created}")
        if candidate is not None:
            lines.append(f"skill_candidate: {str(candidate).lower()}")
        if resources:
            lines.append("skill_resources:")
            lines.extend(f"  - {item}" for item in resources)
        lines.extend(["---", "", f"# {name[:-3]}", "", body, ""])
        path = self.project / "notes" / name
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    # -- helpers ---------------------------------------------------------

    @property
    def from_text(self) -> str:
        return _utc(self.now - timedelta(days=30))

    def prepare(self, **kwargs) -> dict:
        arguments = {"scope": "notes", "from_instant": self.from_text, "now": self.now}
        arguments.update(kwargs)
        if "note" in arguments:
            arguments["subset"] = arguments.pop("note")
        payload = prepare_curation(self.project, work_record=RECORD_REF, **arguments)
        self.handles.append(payload["handle_file"])
        return payload

    def finalize(self, payload: dict, **kwargs) -> dict:
        arguments = {"scope": "notes", "now": self.now, "work_record": RECORD_REF}
        arguments.update(kwargs)
        return finalize_curation(self.project, run=payload["handle_file"], **arguments)

    def record_review(self, payload: dict, entries: list[dict]) -> None:
        record = self.record_path
        text = record.read_text(encoding="utf-8")
        review = {"run_id": payload["run_id"], "reviewer": "regression", "notes": entries}
        record.write_text(
            update_markdown_metadata(text, {"curation_review": review}), encoding="utf-8"
        )

    def review_entries(self, payload: dict, **overrides) -> list[dict]:
        entries = [
            {"path": note["path"], "revision": note["revision"], "disposition": "no-action"}
            for note in payload["notes"]
        ]
        for path, changes in overrides.items():
            for entry in entries:
                if entry["path"] == path:
                    entry.update(changes)
        return entries

    @property
    def record_path(self) -> Path:
        return self.project / "specs" / "quick-tasks" / "2026-10-18-fixture-task.md"

    def checkpoint(self) -> dict:
        return json.loads(
            (self.project / ".kosmic" / "curation" / "notes.json").read_text(encoding="utf-8")
        )

    def assert_fails(self, callable_, code: str) -> None:
        try:
            callable_()
        except CurationError as caught:
            self.assertIn(code, str(caught))
        else:
            self.fail(f"expected CurationError {code}")

    # -- window semantics (fixed clock) -----------------------------------

    def test_window_bounds_follow_l_exclusive_u_inclusive(self) -> None:
        lower = self.now - timedelta(days=30)
        upper = self.now
        self.write_note("at-lower.md", _utc(lower))
        self.write_note("at-upper.md", _utc(upper))
        self.write_note("inside.md", _utc(self.now - timedelta(days=1)))
        self.write_note("after-upper.md", _utc(upper + timedelta(microseconds=1)))
        payload = self.prepare()
        selected = sorted(note["path"] for note in payload["notes"])
        self.assertEqual(sorted(["notes/inside.md", "notes/at-upper.md"]), selected)
        self.assertEqual(payload["window"]["until"], _utc(upper))

    def test_created_fallback_selects_never_updated_notes(self) -> None:
        self.write_note("never-updated.md", None, created=_utc(self.now - timedelta(days=2)))
        payload = self.prepare()
        self.assertEqual(
            ["notes/never-updated.md"], [note["path"] for note in payload["notes"]]
        )

    def test_filesystem_mtime_is_never_consulted(self) -> None:
        note = self.write_note(
            "never-updated-old.md", None, created=_utc(self.now - timedelta(days=60))
        )
        stamp = (self.now + timedelta(days=5)).timestamp()
        os.utime(note, (stamp, stamp))  # fresh mtime outside the semantic instant
        payload = self.prepare()
        self.assertEqual([], payload["notes"])

    def test_missing_timestamp_fails_closed(self) -> None:
        self.write_note("undated.md", None)
        self.assert_fails(self.prepare, "CURATION_TIMESTAMP_UNKNOWN")

    def test_date_only_day_wholly_inside_is_reviewed_with_uncertainty(self) -> None:
        self.write_note("legacy-inside.md", "2026-10-05")
        payload = self.prepare()
        self.assertEqual(["notes/legacy-inside.md"], [n["path"] for n in payload["notes"]])
        self.assertIs(True, payload["notes"][0]["uncertain"])

    def test_date_only_day_overlapping_boundary_blocks_advancement(self) -> None:
        lower_day = (self.now - timedelta(days=30)).date().isoformat()
        self.write_note("legacy-boundary.md", lower_day)
        payload = self.prepare()
        self.assertEqual([], payload["notes"])
        self.assertEqual(1, len(payload["ambiguous"]))
        self.record_review(payload, [])
        self.assert_fails(lambda: self.finalize(payload), "CURATION_AMBIGUOUS_BOUNDARY")

    def test_baseline_window_is_empty_and_advances_on_explicit_review(self) -> None:
        self.write_note("older.md", _utc(self.now - timedelta(days=400)))
        payload = self.prepare(baseline=True, from_instant=None)
        self.assertEqual([], payload["notes"])
        self.assertEqual(payload["window"]["from"], payload["window"]["until"])
        self.record_review(payload, [])
        result = self.finalize(payload)
        self.assertTrue(result["advanced"])
        self.assertEqual(self.checkpoint()["last_successful"], payload["window"]["until"])

    # -- serialization and stale reservations ------------------------------

    def test_second_prepare_observes_active_run_as_busy(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        first = self.prepare()
        self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")
        self.assertEqual(
            first["run_id"], self.checkpoint()["active_run"]["run_id"]
        )

    def test_terminal_predecessor_is_cleared_without_touching_checkpoint(self) -> None:
        from skills.scripts import kosmic_runs

        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        first = self.prepare()
        kosmic_runs.finish_run(first["handle_file"], "failed", detail="abandoned review")
        second = self.prepare()
        self.assertNotEqual(first["run_id"], second["run_id"])
        self.assertIsNone(self.checkpoint()["last_successful"])

    def test_unbounded_prepare_requires_the_typed_lower_bound(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        self.assert_fails(
            lambda: self.prepare(from_instant=None), "CURATION_LOWER_BOUND_REQUIRED"
        )

    # -- work-record authority and review coverage --------------------------

    def test_foreign_work_record_finalize_never_touches_the_lease(self) -> None:
        from skills.scripts.kosmic_work import WorkdirError

        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        with self.assertRaises(WorkdirError) as caught:
            self.finalize(payload, work_record=f"{PROJECT_ID}/quick-task/other")
        self.assertIn("RECORD_INVALID", str(caught.exception))
        # The legitimate lease survived the foreign attempt untouched.
        self.assertEqual(payload["run_id"], self.checkpoint()["active_run"]["run_id"])
        self.record_review(payload, self.review_entries(payload))
        result = self.finalize(payload)
        self.assertTrue(result["advanced"])

    def test_missing_disposition_leaves_checkpoint_unchanged(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        self.record_review(payload, [])
        self.assert_fails(lambda: self.finalize(payload), "CURATION_REVIEW_INCOMPLETE")
        self.assertIsNone(self.checkpoint()["last_successful"])
        self.assertIsNone(self.checkpoint()["active_run"])

    def test_stale_revision_disposition_is_rejected(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        entries = self.review_entries(
            payload, **{"notes/inside.md": {"revision": "0" * 64}}
        )
        self.record_review(payload, entries)
        self.assert_fails(lambda: self.finalize(payload), "CURATION_REVIEW_STALE")
        self.assertIsNone(self.checkpoint()["last_successful"])

    def test_disposition_for_out_of_snapshot_note_is_rejected(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        entries = self.review_entries(payload) + [
            {"path": "notes/outside.md", "revision": "1", "disposition": "reviewed"}
        ]
        self.record_review(payload, entries)
        self.assert_fails(
            lambda: self.finalize(payload), "CURATION_REVIEW_OUTSIDE_SNAPSHOT"
        )

    def test_skipped_without_reason_is_structurally_invalid(self) -> None:
        self.write_note(
            "legacy-candidate.md", _utc(self.now - timedelta(days=3)), candidate=False
        )
        payload = self.prepare()
        entries = [
            {
                "path": "notes/legacy-candidate.md",
                "revision": payload["notes"][0]["revision"],
                "disposition": "skipped",
            }
        ]
        self.record_review(payload, entries)
        self.assert_fails(lambda: self.finalize(payload), "CURATION_REVIEW_INVALID")

    def test_explicit_skip_with_reason_is_a_valid_disposition(self) -> None:
        self.write_note(
            "legacy-candidate.md", _utc(self.now - timedelta(days=3)), candidate=False
        )
        payload = self.prepare()
        self.assertEqual(
            ["notes/legacy-candidate.md"], [note["path"] for note in payload["notes"]]
        )
        entries = [
            {
                "path": "notes/legacy-candidate.md",
                "revision": payload["notes"][0]["revision"],
                "disposition": "skipped",
                "reason": "creation-time-false candidate",
            }
        ]
        self.record_review(payload, entries)
        result = self.finalize(payload)
        self.assertTrue(result["advanced"])

    # -- drift and post-cutoff revisions -------------------------------------

    def test_in_window_revision_after_prepare_blocks_advancement(self) -> None:
        note = self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        note.write_text(
            note.read_text(encoding="utf-8").replace("body", "revised body"),
            encoding="utf-8",
        )
        self.record_review(payload, self.review_entries(payload))
        self.assert_fails(lambda: self.finalize(payload), "CURATION_DRIFT")
        self.assertIsNone(self.checkpoint()["last_successful"])

    def test_post_cutoff_revision_defers_to_the_next_window(self) -> None:
        note = self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        text = note.read_text(encoding="utf-8").replace("body", "later body")
        text = update_markdown_metadata(
            text, {"updated": _utc(self.now + timedelta(days=2))}
        )
        note.write_text(text, encoding="utf-8")
        self.record_review(payload, self.review_entries(payload))
        result = self.finalize(payload)
        self.assertTrue(result["advanced"])
        self.assertEqual(self.checkpoint()["last_successful"], payload["window"]["until"])

    # -- subset and scope isolation -------------------------------------------

    def test_subset_run_never_advances_the_checkpoint(self) -> None:
        self.write_note("first.md", _utc(self.now - timedelta(days=3)))
        self.write_note("second.md", _utc(self.now - timedelta(days=2)))
        payload = self.prepare(note=["notes/first.md"])
        self.assertEqual(["notes/first.md"], [note["path"] for note in payload["notes"]])
        self.assertEqual("subset", payload["mode"])
        self.record_review(payload, self.review_entries(payload))
        result = self.finalize(payload)
        self.assertFalse(result["advanced"])
        self.assertIsNone(self.checkpoint()["last_successful"])
        self.assertIsNone(self.checkpoint()["active_run"])

    def test_subset_entry_outside_window_is_rejected(self) -> None:
        self.write_note("first.md", _utc(self.now - timedelta(days=3)))
        self.write_note("before.md", _utc(self.now - timedelta(days=60)))
        self.assert_fails(
            lambda: self.prepare(note=["notes/before.md"]),
            "CURATION_NOTE_OUT_OF_WINDOW",
        )

    def test_scopes_keep_independent_checkpoints(self) -> None:
        self.assertEqual(("notes",), CURATION_SCOPES)
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        self.record_review(payload, self.review_entries(payload))
        self.finalize(payload)
        self.assertIsNotNone(self.checkpoint()["last_successful"])
        self.assertTrue((self.project / ".kosmic" / "curation" / "notes.lock").exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
