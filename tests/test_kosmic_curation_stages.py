"""Story 004 curation stage regressions: persisted cursor, scoped subtrees,
managed-run coordination, review coverage, and drift (fixed clock via the
public ``now`` injection; the CLI passes real time and there is no production
clock backdoor).

Assertions are behavioral: coordination state lives in the EXISTING managed
run lifecycle (never a project-side pointer), and the Project checkpoint
appears only after a successful full-scope finalize.
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
    CURATION_ROOT_SCOPE,
    CurationError,
    finalize_curation,
    normalize_scope,
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
        updated: str | None,
        *,
        created: str | None = None,
        candidate: bool | None = None,
        resources: list[str] | None = None,
        body: str = "body",
    ) -> Path:
        parts = [part for part in name.split("/") if part]
        path = self.project.joinpath("notes", *parts)
        path.parent.mkdir(parents=True, exist_ok=True)
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
        title = parts[-1][:-3].replace("-", " ").title()
        lines.extend(["---", "", f"# {title}", "", body, ""])
        path.write_text("\n".join(lines), encoding="utf-8")
        return path

    # -- helpers ---------------------------------------------------------

    @property
    def first_bound(self) -> str:
        return _utc(self.now - timedelta(days=30))

    def prepare(self, **kwargs) -> dict:
        arguments = {"scope": CURATION_ROOT_SCOPE, "from_instant": self.first_bound, "now": self.now}
        arguments.update(kwargs)
        if "note" in arguments:
            arguments["subset"] = arguments.pop("note")
        payload = prepare_curation(self.project, work_record=RECORD_REF, **arguments)
        self.handles.append(payload["handle_file"])
        return payload

    def finalize(self, payload: dict, **kwargs) -> dict:
        arguments = {
            "scope": payload["scope"],
            "now": self.now,
            "work_record": RECORD_REF,
        }
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

    def run_state(self, payload: dict) -> str:
        from skills.scripts.kosmic_runs import run_live_status

        return str(run_live_status(self.project, payload["run_id"])["state"])

    def cursor(self, scope: str = CURATION_ROOT_SCOPE) -> str | None:
        digest = None if scope == "notes" else __import__("hashlib").sha256(
            scope.encode("utf-8")
        ).hexdigest()[:16]
        name = "notes.json" if digest is None else f"scope-{digest}.json"
        path = self.project / ".kosmic" / "curation" / name
        try:
            return json.loads(path.read_text(encoding="utf-8"))["last_successful"]
        except FileNotFoundError:
            return None

    def assert_fails(self, callable_, code: str) -> None:
        try:
            callable_()
        except CurationError as caught:
            self.assertIn(code, str(caught))
        else:
            self.fail(f"expected CurationError {code}")

    # -- cursor lifecycle (STD-004-1) --------------------------------------

    def test_unbounded_prepare_requires_the_typed_first_bound(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        self.assert_fails(
            lambda: self.prepare(from_instant=None), "CURATION_LOWER_BOUND_REQUIRED"
        )

    def test_second_full_prepare_uses_the_persisted_cursor(self) -> None:
        first = self.prepare(from_instant=self.first_bound)
        self.record_review(first, self.review_entries(first))
        self.finalize(first)
        cursor = self.cursor()
        self.assertEqual(cursor, first["window"]["until"])
        self.now += timedelta(days=2)
        self.write_note("intervening.md", _utc(self.now - timedelta(days=1)))
        second = self.prepare(from_instant=None)
        self.assertEqual(second["window"]["from"], cursor)
        self.assertEqual(
            ["notes/intervening.md"], [note["path"] for note in second["notes"]]
        )
        self.record_review(second, self.review_entries(second))
        self.finalize(second)
        self.assertEqual(self.cursor(), second["window"]["until"])
        # A provided bound after initialization can never rewind or skip.
        self.assert_fails(
            lambda: self.prepare(from_instant=_utc(self.now - timedelta(days=40))),
            "CURATION_CURSOR_INITIALIZED",
        )
        self.assert_fails(
            lambda: self.prepare(baseline=True, from_instant=None),
            "CURATION_CURSOR_INITIALIZED",
        )

    # -- window semantics (fixed clock) -----------------------------------

    def test_window_bounds_follow_l_exclusive_u_inclusive(self) -> None:
        lower = self.now - timedelta(days=30)
        upper = self.now
        self.write_note("at-lower.md", _utc(lower))
        self.write_note("at-upper.md", _utc(upper))
        self.write_note("inside.md", _utc(self.now - timedelta(days=1)))
        self.write_note("after-upper.md", _utc(upper + timedelta(microseconds=1)))
        payload = self.prepare()
        self.assertEqual(
            sorted(["notes/at-upper.md", "notes/inside.md"]),
            sorted(note["path"] for note in payload["notes"]),
        )
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
        os.utime(note, (stamp, stamp))
        payload = self.prepare()
        self.assertEqual([], payload["notes"])

    def test_missing_timestamp_fails_closed(self) -> None:
        self.write_note("undated.md", None)
        self.assert_fails(self.prepare, "CURATION_TIMESTAMP_UNKNOWN")

    def test_date_only_day_wholly_inside_is_reviewed_with_uncertainty(self) -> None:
        self.write_note("legacy-inside.md", "2026-10-05")
        payload = self.prepare()
        self.assertEqual(["notes/legacy-inside.md"], [note["path"] for note in payload["notes"]])
        self.assertIs(True, payload["notes"][0]["uncertain"])

    def test_date_only_day_overlapping_boundary_blocks_advancement(self) -> None:
        lower_day = (self.now - timedelta(days=30)).date().isoformat()
        self.write_note("legacy-boundary.md", lower_day)
        payload = self.prepare()
        self.assertEqual([], payload["notes"])
        self.assertEqual(1, len(payload["ambiguous"]))
        self.record_review(payload, [])
        self.assert_fails(lambda: self.finalize(payload), "CURATION_AMBIGUOUS_BOUNDARY")
        self.assertIsNone(self.cursor())

    def test_baseline_window_is_empty_and_advances_on_explicit_review(self) -> None:
        self.write_note("older.md", _utc(self.now - timedelta(days=400)))
        payload = self.prepare(baseline=True, from_instant=None)
        self.assertEqual([], payload["notes"])
        self.assertEqual(payload["window"]["from"], payload["window"]["until"])
        self.record_review(payload, [])
        result = self.finalize(payload)
        self.assertTrue(result["advanced"])
        self.assertEqual(self.cursor(), payload["window"]["until"])

    # -- managed-run coordination (no project-side pointer) ------------------

    def test_prepare_writes_no_project_checkpoint(self) -> None:
        # AC15: prepare coordinates only through the managed run; the Project
        # checkpoint appears only after a successful full-scope finalize.
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        self.assertIsNone(self.cursor())
        self.assertFalse((self.project / ".kosmic" / "curation").exists())
        self.record_review(payload, self.review_entries(payload))
        self.finalize(payload)
        self.assertIsNotNone(self.cursor())

    def test_second_prepare_observes_active_run_as_busy(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        first = self.prepare()
        self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")
        self.assertEqual("active", self.run_state(first))
        self.assertIsNone(self.cursor())

    def test_unresolved_reservation_is_never_retired_by_guessing(self) -> None:
        # STD-004-3: an unreadable live status must classify busy, never stale;
        # the lease survives and the scope stays busy afterwards.
        from skills.scripts import kosmic_runs

        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        real_status = kosmic_runs.run_live_status

        def unresolved(worktree, run_id):
            raise kosmic_runs.RunError("RUN_OPEN_FAILED", "fault injected")

        try:
            kosmic_runs.run_live_status = unresolved
            self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")
        finally:
            kosmic_runs.run_live_status = real_status
        self.assertEqual("active", self.run_state(payload))
        self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")

    def test_unresolvable_abandon_keeps_the_scope_busy(self) -> None:
        # STD-004-2: a refused closure must not free the scope; checkpoint
        # unchanged, native lease still serializing.
        from skills.scripts import kosmic_runs

        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        self.record_review(payload, [])
        real_finish = kosmic_runs.finish_run

        def refusing(handle_file, outcome, detail=""):
            raise kosmic_runs.RunError("HOLDER_REFUSED", "fault injected")

        try:
            kosmic_runs.finish_run = refusing
            self.assert_fails(lambda: self.finalize(payload), "CURATION_ABANDON_REFUSED")
        finally:
            kosmic_runs.finish_run = real_finish
        self.assertIsNone(self.cursor())
        self.assertEqual("active", self.run_state(payload))
        self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")

    def test_terminal_predecessor_never_blocks_a_fresh_run(self) -> None:
        from skills.scripts.kosmic_runs import finish_run

        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        first = self.prepare()
        finish_run(first["handle_file"], "failed", detail="abandoned review")
        second = self.prepare()
        self.assertNotEqual(first["run_id"], second["run_id"])
        self.assertIsNone(self.cursor())

    # -- work-record authority and review coverage --------------------------

    def test_foreign_work_record_finalize_never_touches_the_lease(self) -> None:
        from skills.scripts.kosmic_work import WorkdirError

        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        with self.assertRaises(WorkdirError) as caught:
            self.finalize(payload, work_record=f"{PROJECT_ID}/quick-task/other")
        self.assertIn("RECORD_INVALID", str(caught.exception))
        self.assertEqual("active", self.run_state(payload))
        self.record_review(payload, self.review_entries(payload))
        result = self.finalize(payload)
        self.assertTrue(result["advanced"])

    def test_missing_disposition_leaves_checkpoint_unchanged(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        self.record_review(payload, [])
        self.assert_fails(lambda: self.finalize(payload), "CURATION_REVIEW_INCOMPLETE")
        self.assertIsNone(self.cursor())
        self.assertIn(self.run_state(payload), ("failed", "succeeded"))

    def test_stale_revision_disposition_is_rejected(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        entries = self.review_entries(
            payload, **{"notes/inside.md": {"revision": "0" * 64}}
        )
        self.record_review(payload, entries)
        self.assert_fails(lambda: self.finalize(payload), "CURATION_REVIEW_STALE")
        self.assertIsNone(self.cursor())

    def test_disposition_for_out_of_snapshot_note_is_rejected(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        entries = self.review_entries(payload) + [
            {"path": "notes/outside.md", "revision": "1", "disposition": "reviewed"}
        ]
        self.record_review(payload, entries)
        self.assert_fails(lambda: self.finalize(payload), "CURATION_REVIEW_OUTSIDE_SNAPSHOT")

    def test_skipping_a_candidate_note_is_structurally_invalid(self) -> None:
        # SPEC-004-2: only candidate-false, resource-empty notes may skip.
        self.write_note(
            "flagged.md", _utc(self.now - timedelta(days=3)), candidate=True
        )
        payload = self.prepare()
        entries = [
            {
                "path": "notes/flagged.md",
                "revision": payload["notes"][0]["revision"],
                "disposition": "skipped",
                "reason": "arbitrary",
            }
        ]
        self.record_review(payload, entries)
        self.assert_fails(lambda: self.finalize(payload), "CURATION_REVIEW_INVALID")
        self.assertIsNone(self.cursor())

    def test_skipping_a_live_resource_note_is_structurally_invalid(self) -> None:
        self.write_note(
            "wired.md",
            _utc(self.now - timedelta(days=3)),
            candidate=False,
            resources=["kosmic-usage"],
        )
        payload = self.prepare()
        entries = [
            {
                "path": "notes/wired.md",
                "revision": payload["notes"][0]["revision"],
                "disposition": "skipped",
                "reason": "arbitrary",
            }
        ]
        self.record_review(payload, entries)
        self.assert_fails(lambda: self.finalize(payload), "CURATION_REVIEW_INVALID")

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

    # -- drift, evolution, and post-cutoff revisions -------------------------

    def test_in_window_revision_after_prepare_blocks_advancement(self) -> None:
        note = self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        note.write_text(
            note.read_text(encoding="utf-8").replace("body", "revised body"),
            encoding="utf-8",
        )
        self.record_review(payload, self.review_entries(payload))
        self.assert_fails(lambda: self.finalize(payload), "CURATION_DRIFT")
        self.assertIsNone(self.cursor())

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
        self.assertEqual(self.cursor(), payload["window"]["until"])

    def test_note_newly_eligible_after_prepare_blocks_the_cursor(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        self.write_note("late.md", _utc(self.now - timedelta(days=1)))
        self.record_review(payload, self.review_entries(payload))
        self.assert_fails(lambda: self.finalize(payload), "CURATION_WINDOW_EVOLVED")
        self.assertIsNone(self.cursor())
        second = self.prepare()
        self.assertEqual(
            sorted(["notes/inside.md", "notes/late.md"]),
            sorted(note["path"] for note in second["notes"]),
        )

    def test_post_cutoff_note_defers_without_blocking_the_cursor(self) -> None:
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        self.write_note("later.md", _utc(self.now + timedelta(days=1)))
        self.record_review(payload, self.review_entries(payload))
        result = self.finalize(payload)
        self.assertTrue(result["advanced"])
        self.assertEqual(self.cursor(), payload["window"]["until"])

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
        self.assertIsNone(self.cursor())

    def test_subset_entry_outside_window_is_rejected(self) -> None:
        self.write_note("first.md", _utc(self.now - timedelta(days=3)))
        self.write_note("before.md", _utc(self.now - timedelta(days=60)))
        self.assert_fails(
            lambda: self.prepare(note=["notes/before.md"]),
            "CURATION_NOTE_OUT_OF_WINDOW",
        )

    def test_scoped_subtrees_keep_independent_checkpoints(self) -> None:
        # SPEC-004-3 / AC6: real second-scope consumer example. The root
        # scope stays recursive; the subtree scope never leaks into it.
        self.assertEqual("notes", normalize_scope("notes"))
        self.assertEqual("notes/theory", normalize_scope("theory"))
        self.write_note("theory/topic.md", _utc(self.now - timedelta(days=3)))
        self.write_note("root-note.md", _utc(self.now - timedelta(days=3)))
        theory = self.prepare(scope="notes/theory")
        self.assertEqual(["notes/theory/topic.md"], [note["path"] for note in theory["notes"]])
        self.record_review(theory, self.review_entries(theory))
        self.finalize(theory)
        self.assertIsNotNone(self.cursor("notes/theory"))
        self.assertIsNone(self.cursor("notes"))
        root = self.prepare()  # root cursor still uninitialized: bound applies
        self.assertEqual(
            ["notes/root-note.md", "notes/theory/topic.md"],
            sorted(note["path"] for note in root["notes"]),
        )
        self.record_review(root, self.review_entries(root))
        self.finalize(root)
        self.assertIsNotNone(self.cursor("notes"))
        self.assert_fails(
            lambda: self.prepare(scope="notes/theory", from_instant=self.first_bound),
            "CURATION_CURSOR_INITIALIZED",
        )

    def test_scope_paths_are_bounded(self) -> None:
        for bad in ("/etc", "../escape", "notes/../secrets", "notes/", "notes/.."):
            with self.subTest(scope=bad):
                self.assert_fails(
                    lambda bound=bad: self.prepare(scope=bound), "CURATION_SCOPE_INVALID"
                )

    # -- Round 2: transaction-entry cursor, honest busy, bounded walks ------

    def test_concurrent_finalize_at_transaction_entry_rejects_baseline(self) -> None:
        # 04STD-001/04SPEC-4: the checkpoint read and window derivation must
        # happen INSIDE the run-root transaction. The concurrent finalize is
        # injected AT TRANSACTION ENTRY (before this prepare's original
        # acquisition): it runs the REAL finalize to completion, then this
        # prepare reads the cursor INSIDE the transaction — baseline must be
        # refused as cursor-initialized, never treated as a stale first run.
        import skills.scripts.kosmic_curation as curation_module

        self.write_note("first.md", _utc(self.now - timedelta(days=3)))
        first = self.prepare()
        # Legitimate consumer state: run1's recorded review must exist before
        # the injected concurrent finalize can legitimately publish.
        self.record_review(first, self.review_entries(first))
        # The clock moves on after U1; the genuine intervening note then lies
        # inside (U1, U2], never in the first window.
        self.now += timedelta(days=2)
        self.write_note("intervening.md", _utc(self.now - timedelta(days=1)))
        original_transaction = curation_module._scope_transaction
        state = {"raced": False}

        def racing_transaction(worktree):
            if not state["raced"]:
                state["raced"] = True
                # The concurrent finalize enters the ORIGINAL transaction
                # (guard set) and completes before this prepare proceeds.
                result = self.finalize(first)
                self.assertTrue(result["advanced"])
            return original_transaction(worktree)

        try:
            curation_module._scope_transaction = racing_transaction
            self.assert_fails(
                lambda: self.prepare(baseline=True, from_instant=None),
                "CURATION_CURSOR_INITIALIZED",
            )
        finally:
            curation_module._scope_transaction = original_transaction
        # The concurrent cursor won: a bound-less prepare starts exactly at
        # U1 and selects the intervening note; history is never skipped.
        second = self.prepare(from_instant=None)
        self.assertEqual(first["window"]["until"], second["window"]["from"])
        self.assertEqual(
            ["notes/intervening.md"], [note["path"] for note in second["notes"]]
        )

    def test_simultaneous_bounds_are_rejected(self) -> None:
        # Exactly one FIRST bound: --from AND --baseline together is refused
        # instead of silently preferring baseline.
        self.assert_fails(
            lambda: self.prepare(from_instant=self.first_bound, baseline=True),
            "CURATION_LOWER_BOUND_REQUIRED",
        )

    def test_active_run_with_unreadable_snapshot_is_busy(self) -> None:
        # 04STD-002/04SPEC-5: a relevant active run whose snapshot is missing
        # (crash between begin and publish) must block as busy — identified
        # via the native RUN manifest, never skipped, never killed.
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        Path(payload["snapshot_file"]).unlink()
        self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")
        self.assertEqual("active", self.run_state(payload))

    def test_snapshot_loss_is_scoped_to_its_own_scope(self) -> None:
        # 04SPEC-5: a lost snapshot holds ONLY its own scope; the native
        # purpose names the exact scope, so sibling scopes proceed and the
        # damaged scope itself stays busy.
        self.write_note("theory/topic.md", _utc(self.now - timedelta(days=3)))
        self.write_note("software/lib.md", _utc(self.now - timedelta(days=3)))
        theory = self.prepare(scope="notes/theory")
        Path(theory["snapshot_file"]).unlink()
        software = self.prepare(scope="notes/software")
        self.assertEqual(
            ["notes/software/lib.md"], [note["path"] for note in software["notes"]]
        )
        self.record_review(software, self.review_entries(software))
        result = self.finalize(software)
        self.assertTrue(result["advanced"])
        self.assert_fails(lambda: self.prepare(scope="notes/theory"), "CURATION_BUSY")

    def test_finalizing_manifest_state_is_busy(self) -> None:
        # Native "finalizing" is non-terminal (the holder still owns it).
        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        manifest = Path(payload["snapshot_file"]).parent.parent / "RUN.json"
        data = json.loads(manifest.read_text(encoding="utf-8"))
        data["state"] = "finalizing"
        manifest.write_text(json.dumps(data), encoding="utf-8")
        self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")

    def test_partial_run_report_cannot_prove_absence(self) -> None:
        # A report that errors (or carries unresolved run entries) cannot
        # prove no relevant run is active: fail closed as busy.
        from skills.scripts import kosmic_runs

        self.write_note("inside.md", _utc(self.now - timedelta(days=3)))
        payload = self.prepare()
        real_report = kosmic_runs.report_runs

        def truncated(worktree, action="status", run_id=None):
            raise kosmic_runs.RunError("STATUS_TRUNCATED", "fault injected")

        try:
            kosmic_runs.report_runs = truncated
            self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")
        finally:
            kosmic_runs.report_runs = real_report
        # A malformed runs/ entry likewise cannot prove absence.
        from skills.scripts.kosmic_runs import RunEntry, RunReport

        def malformed(worktree, action="status", run_id=None):
            return RunReport(
                entries=(
                    RunEntry(None, "malformed", None, Path("runs") / "broken", 0, None, "fault"),
                ),
                counts={},
                total_bytes=0,
                selected_bytes=0,
                action="status",
                code="PARTIAL",
            )

        try:
            kosmic_runs.report_runs = malformed
            self.assert_fails(lambda: self.prepare(), "CURATION_BUSY")
        finally:
            kosmic_runs.report_runs = real_report
        self.assertEqual("active", self.run_state(payload))

    def test_symlinked_scope_component_is_refused(self) -> None:
        # 04STD-005: intermediate scope components are walked with O_NOFOLLOW
        # BEFORE enumeration; a symlinked component never resolves outside.
        external = self.root / "outside" / "deep"
        external.mkdir(parents=True, exist_ok=True)
        (external / "planted.md").write_text("external", encoding="utf-8")
        notes = self.project / "notes"
        (notes / "mid").symlink_to(external.parent, target_is_directory=True)
        self.assert_fails(
            lambda: self.prepare(scope="notes/mid/deep"), "CURATION_SCOPE_INVALID"
        )

    def test_symlinked_checkpoint_dir_is_refused_without_external_touch(self) -> None:
        # 04STD-006: the whole .kosmic/curation path is verified component by
        # component; a symlinked directory is refused, never followed.
        real_dir = self.root / "outside-checkpoint"
        real_dir.mkdir(parents=True, exist_ok=True)
        link = self.project / ".kosmic" / "curation"
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(real_dir, target_is_directory=True)
        self.assert_fails(
            lambda: self.prepare(from_instant=self.first_bound),
            "CURATION_CHECKPOINT_INVALID",
        )
        self.assertEqual([], list(real_dir.iterdir()))

    def test_foreign_or_unopenable_run_is_typed_not_a_traceback(self) -> None:
        # 04STD-007: a handle naming an unopenable/foreign run surfaces as a
        # typed CurationError before any mutation; native errors are caught
        # at that boundary only.
        fake = self.project / ".kosmic" / "foreign-handle.json"
        fake.parent.mkdir(parents=True, exist_ok=True)
        fake.write_text(
            json.dumps({"kind": "handle", "run_id": "20261018T999999Z-foreign-" + "0" * 32}),
            encoding="utf-8",
        )
        payload = {"handle_file": str(fake), "scope": "notes"}
        self.assert_fails(
            lambda: self.finalize(payload), "CURATION_RUN_MISMATCH"
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
