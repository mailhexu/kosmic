"""Record-scoped completion regression scenarios driven only through the CLI.

Completion must validate the active record's declared knowledge, math, and
Consumer projection without coupling to unrelated legacy notes, while full
``validate`` stays a strict whole-vault audit.
"""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

try:
    from tests.scoped_completion_support import (
        ScopedProjectCase,
        commit_baseline,
        write_document,
    )
except ImportError:  # direct test-directory execution
    from scoped_completion_support import (
        ScopedProjectCase,
        commit_baseline,
        write_document,
    )

import hashlib
import json

from skills.scripts import kosmic_completion, kosmic_work
from skills.scripts.kosmic_dreams import receipt_name

USAGE_BODY = "# Use Demo\n\nRun `demo`.\n"
DEVELOPMENT_BODY = "# Develop Demo\n\nRun contributor checks.\n"
WORK_RECORD = "scope-demo/quick-task/fixture-task"


class RecordScopedCompletionTest(ScopedProjectCase):
    """Public check-completion / validate behavior for record-scoped gates."""

    def cli(self, *arguments: object, expected: int = 0) -> subprocess.CompletedProcess:
        result = self.run_cli(*arguments)
        self.assertEqual(
            expected,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def completion(self, item: Path, expected: int = 0) -> subprocess.CompletedProcess:
        return self.cli(
            "check-completion",
            "--project",
            self.project,
            "--work-item",
            item,
            expected=expected,
        )

    def seed_pair(self) -> None:
        """Publish a real valid Skill Pair under the fixture-task authority."""
        self.note("using.md", USAGE_BODY)
        self.note("developing.md", DEVELOPMENT_BODY)
        self.cli(
            "generate",
            "--project",
            self.project,
            "--work-record",
            WORK_RECORD,
        )

    def consumer_item(self) -> Path:
        return self.item(
            "consumer_interface_change: true\nrelated_notes: [using]\n"
        )

    def write_unmarked_math_note(self, name: str = "afm_report") -> Path:
        return self.note(
            f"{name}.md",
            "# AFM Report\n\n$$\nE = mc^2\n$$\n",
        )

    def write_malformed_note(self, name: str = "malformed_legacy") -> Path:
        path = self.project / "notes" / f"{name}.md"
        path.write_text(
            "---\ntype: reference\nstatus: archived\naudience: both\n"
            "artifact_role: knowledge\n---\n\n# Legacy\n",
            encoding="utf-8",
        )
        return path

    def test_unrelated_defects_do_not_block_noninterface_completion(self) -> None:
        self.write_unmarked_math_note()
        self.write_malformed_note()
        item = self.item()
        self.completion(item)

    def test_declared_unmarked_math_blocks_noninterface_completion(self) -> None:
        self.write_unmarked_math_note()
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [afm_report]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("afm_report", result.stderr)

    def test_declared_malformed_note_blocks_noninterface_completion(self) -> None:
        self.write_malformed_note()
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [malformed_legacy]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("malformed_legacy", result.stderr)

    def test_declared_expired_or_deprecated_knowledge_blocks_noninterface(self) -> None:
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [required]\n"
        )
        for metadata in ("stale_after: 2000-01-01\n", "usage_stale: true\n"):
            with self.subTest(metadata=metadata):
                self.note("required.md", metadata=metadata)
                result = self.completion(item, expected=2)
                self.assertIn("required", result.stderr)
        note = self.note("required.md")
        note.write_text(note.read_text().replace("status: stable", "status: deprecated"))
        result = self.completion(item, expected=2)
        self.assertIn("required", result.stderr)

    def test_missing_declared_note_blocks_noninterface_completion(self) -> None:
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [ghost]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("ghost", result.stderr)

    def test_escaping_declared_note_is_rejected(self) -> None:
        outside = self.project.parent / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [../outside]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("outside", result.stderr)

    def test_nonmath_record_completes_without_mathdocs_registry(self) -> None:
        shutil.rmtree(self.project / "mathdocs")
        item = self.item()
        self.completion(item)

    def test_full_validate_still_rejects_unrelated_defects(self) -> None:
        self.seed_pair()
        self.cli("validate", "--project", self.project)
        math_note = self.write_unmarked_math_note()
        result = self.cli("validate", "--project", self.project, expected=2)
        self.assertIn("afm_report", result.stderr)
        math_note.unlink()
        self.write_malformed_note()
        result = self.cli("validate", "--project", self.project, expected=2)
        self.assertIn("malformed_legacy", result.stderr)
        (self.project / "notes" / "malformed_legacy.md").unlink()
        self.cli("validate", "--project", self.project)

    def test_consumer_completion_ignores_unrelated_source_staleness(self) -> None:
        self.seed_pair()
        item = self.consumer_item()
        self.completion(item)
        developing = self.project / "notes" / "developing.md"
        developing.write_text(
            developing.read_text(encoding="utf-8") + "Unrelated follow-up.\n",
            encoding="utf-8",
        )
        self.completion(item)

    def test_consumer_completion_requires_stable_fresh_declared_note(self) -> None:
        self.seed_pair()
        item = self.consumer_item()
        self.completion(item)
        note = self.project / "notes" / "using.md"
        variants = (
            ("status: draft",
             "---\ntype: reference\nstatus: draft\naudience: both\n"
             "artifact_role: knowledge\n---\n\n" + USAGE_BODY),
            ("stale_after",
             "---\ntype: reference\nstatus: stable\naudience: both\n"
             "artifact_role: knowledge\nstale_after: '2020-01-01'\n---\n\n"
             + USAGE_BODY),
            ("usage_stale",
             "---\ntype: reference\nstatus: stable\naudience: both\n"
             "artifact_role: knowledge\nusage_stale: true\n---\n\n" + USAGE_BODY),
        )
        for label, frontmatter in variants:
            with self.subTest(defect=label):
                note.write_text(frontmatter, encoding="utf-8")
                result = self.completion(item, expected=2)
                self.assertIn("using", result.stderr)
                self.note("using.md", USAGE_BODY)
                self.completion(item)

    def test_consumer_completion_requires_current_declared_projection(self) -> None:
        self.seed_pair()
        item = self.consumer_item()
        using = self.project / "notes" / "using.md"
        using.write_text(
            using.read_text(encoding="utf-8") + "New interface behavior.\n",
            encoding="utf-8",
        )
        result = self.completion(item, expected=2)
        self.assertIn("using", result.stderr)
        self.cli("generate", "--project", self.project, "--work-record", WORK_RECORD)
        self.completion(item)
        (self.project / "skills").rename(self.project / "skills-pair")
        result = self.completion(item, expected=2)
        self.assertIn("Skill Pair", result.stderr)

    def test_consumer_completion_rejects_pair_byte_corruption(self) -> None:
        self.seed_pair()
        item = self.consumer_item()
        self.completion(item)
        development_skill = (
            self.project / "skills" / "scope-demo-development" / "SKILL.md"
        )
        development_skill.write_text(
            development_skill.read_text(encoding="utf-8") + "<!-- tampered -->\n",
            encoding="utf-8",
        )
        # The refusal itself is the consumer-integrity invariant; error
        # wording is incidental and never asserted.
        self.completion(item, expected=2)


class EmbeddedCompletionFinishTest(ScopedProjectCase):
    """Story 003 tracer: embedded observations + review finish with a record-bound receipt.

    The ``fixture-*`` reviewer identities below are synthetic test fixtures;
    they never represent actual feature approval.
    """

    REVIEW_BASE = "fixture-completion-base"
    CRITERION = "Fixture behavior verified"
    REVIEWER = "fixture-reviewer"
    SOURCE = "tests/test_record_scoped_completion.py::EmbeddedCompletionFinishTest"

    def setUp(self):
        super().setUp()
        commit_baseline(self.root)
        self.record_path = self.project / "specs/quick-tasks/fixture-task.md"
        self.write_record()

    def resolve_record(self):
        return kosmic_work.resolve_work_record(self.project, WORK_RECORD)

    def default_observations(self, *criteria):
        return [{"criterion": criterion,
                 "observation": "The fixture quick-task behavior was exercised through "
                                "the record-scoped completion CLI and behaved as documented.",
                 "source": self.SOURCE}
                for criterion in (criteria or (self.CRITERION,))]

    def review_fields(self, **overrides):
        review = {
            "reviewer": self.REVIEWER,
            "axes": {
                "standards": {"reviewer": "fixture-standards-reviewer",
                              "decision": "approved"},
                "spec": {"reviewer": "fixture-spec-reviewer", "decision": "approved"},
            },
            "decision": "approved",
            "review_base": self.REVIEW_BASE,
            "reviewed_revision": kosmic_completion.source_revision(
                self.root, self.project, self.resolve_record()),
            "findings": [],
            "scope": ["project:specs/"],
        }
        review.update(overrides)
        return review

    def write_record(self, *, criteria=None, observations=None, review=None):
        criteria = list(criteria or (self.CRITERION,))
        write_document(
            self.record_path,
            {
                "project_id": "scope-demo",
                "subproject_id": None,
                "record_kind": "quick-task",
                "local_id": "fixture-task",
                "status": "approved",
                "consumer_interface_change": False,
                "review_base": self.REVIEW_BASE,
                "review_round": 1,
                "completion_observations":
                    self.default_observations(*criteria) if observations is None else observations,
                "completion_review": self.review_fields() if review is None else review,
            },
            "Fixture",
            "## Acceptance Criteria\n\n"
            + "".join(f"- [ ] {criterion}\n" for criterion in criteria))

    def run_finish(self):
        return self.run_cli(
            "work", "finish",
            "--project", self.project,
            "--worktree", self.root,
            "--work-record", WORK_RECORD,
            "--scope", "project:specs/",
            "--detail", "embedded completion tracer",
        )

    def finish(self) -> subprocess.CompletedProcess:
        result = self.run_finish()
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def refusal(self, *, criteria=None, observations=None, review=None,
                code=None) -> subprocess.CompletedProcess:
        """Rewrite the record with overridden embedded fields; expect refusal."""
        self.write_record(criteria=criteria, observations=observations, review=review)
        result = self.run_finish()
        self.assertEqual(
            2,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())
        if code is not None:
            self.assertIn(code, result.stderr)
        return result

    def test_embedded_completion_finish_binds_receipt_to_completed_record(self) -> None:
        receipt = json.loads(self.finish().stdout)
        canonical = self.record_path.relative_to(self.project).as_posix()
        record_sha256 = hashlib.sha256(self.record_path.read_bytes()).hexdigest()
        self.assertEqual(receipt["schema"], "kosmic.work-receipt/1")
        self.assertEqual(receipt["identity"], WORK_RECORD)
        self.assertEqual(receipt["status"], "successful")
        self.assertEqual(receipt["record_path"], canonical)
        self.assertEqual(receipt["record_sha256"], record_sha256)
        # The proof binds exactly the completed record bytes: no evidence
        # sidecars, no artifact map, no manufactured note.
        self.assertEqual(receipt["proof"], {canonical: record_sha256})
        stored = self.project / ".kosmic/work-receipts" / receipt_name(WORK_RECORD)
        self.assertEqual(json.loads(stored.read_text(encoding="utf-8")), receipt)
        self.assertIn("status: done", self.record_path.read_text(encoding="utf-8"))
        self.assertFalse((self.project / "evidence").exists())
        self.assertEqual(
            sorted(path.name for path in (self.project / "specs/quick-tasks").iterdir()),
            ["fixture-task.md"],
        )
        self.assertEqual(
            sorted(path.name for path in (self.project / "notes").iterdir()),
            ["index.md"],
        )
        # Terminal receipt validation stays green on the completed record.
        checked = self.run_cli(
            "check-completion",
            "--project", self.project,
            "--work-item", self.record_path,
        )
        self.assertEqual(
            0,
            checked.returncode,
            msg=f"stdout:\n{checked.stdout}\nstderr:\n{checked.stderr}",
        )

    def test_missing_criterion_coverage_refuses_without_receipt(self) -> None:
        result = self.refusal(
            criteria=(self.CRITERION, "Fixture follow-up verified"),
            observations=self.default_observations(self.CRITERION),
            code="ACCEPTANCE_INVALID",
        )
        self.assertIn("uncovered", result.stderr)

    def test_mismatched_criterion_text_refuses(self) -> None:
        observations = self.default_observations()
        observations[0]["criterion"] = "fixture behavior verified"
        self.refusal(observations=observations, code="ACCEPTANCE_INVALID")

    def test_repeated_criterion_refuses(self) -> None:
        repeated = self.default_observations(self.CRITERION) * 2
        self.refusal(observations=repeated, code="ACCEPTANCE_INVALID")

    def test_changes_requested_review_blocks_receipt(self) -> None:
        self.refusal(review=self.review_fields(decision="changes-requested"),
                     code="REVIEW_INVALID")

    def test_missing_axis_approval_refuses(self) -> None:
        self.refusal(review=self.review_fields(axes={
            "standards": {"reviewer": "fixture-standards-reviewer",
                          "decision": "approved"},
            "spec": {"reviewer": "fixture-spec-reviewer",
                     "decision": "changes-requested"}}),
            code="REVIEW_INVALID")

    def test_root_axes_shape_is_rejected(self) -> None:
        review = self.review_fields()
        review["standards"] = review.pop("axes")["standards"]
        self.refusal(review=review, code="REVIEW_INVALID")

    def test_missing_reviewer_identity_refuses(self) -> None:
        self.refusal(review=self.review_fields(reviewer="   "), code="REVIEW_INVALID")

    def test_unresolved_blocking_finding_refuses(self) -> None:
        self.refusal(review=self.review_fields(findings=[
            {"id": "KF-1", "disposition": "Blocking", "status": "open"},
        ]), code="REVIEW_INVALID")

    def test_risk_accepted_blocking_finding_finishes(self) -> None:
        review = self.review_fields(
            decision="user-accepted",
            approved_by="fixture-user",
            findings=[{"id": "KF-1", "disposition": "Blocking",
                       "status": "risk-accepted",
                       "risk_accepted_by": "fixture-user",
                       "risk_acceptance_note": "Bounded fixture trade-off accepted by a named human."}],
        )
        self.write_record(review=review)
        receipt = json.loads(self.finish().stdout)
        self.assertEqual(receipt["status"], "successful")

    def test_reviewed_scope_must_cover_actual_work(self) -> None:
        self.refusal(review=self.review_fields(scope=[]), code="REVIEW_INVALID")

    def test_broader_reviewed_scope_allows_narrow_finish_claims(self) -> None:
        review = self.review_fields(
            scope=["project:specs/", "project:notes/"])
        self.write_record(review=review)
        receipt = json.loads(self.finish().stdout)
        self.assertEqual(receipt["status"], "successful")

    def test_reviewed_revision_drift_refuses(self) -> None:
        result = self.refusal(
            review=self.review_fields(reviewed_revision="0" * 64),
            code="REVIEW_INVALID",
        )
        self.assertIn("reviewed revision differs", result.stderr)

    def test_receipt_survives_note_evolution_but_not_record_edit(self) -> None:
        json.loads(self.finish().stdout)
        notes = self.project / "notes/index.md"
        notes.write_text(
            notes.read_text(encoding="utf-8")
            + "Later refinement that must never revoke completion.\n",
            encoding="utf-8",
        )
        kept = self.run_cli(
            "check-completion",
            "--project", self.project,
            "--work-item", self.record_path,
        )
        self.assertEqual(
            0,
            kept.returncode,
            msg=f"stdout:\n{kept.stdout}\nstderr:\n{kept.stderr}",
        )
        record = self.record_path
        baseline = record.read_bytes()
        record.write_text(
            record.read_text(encoding="utf-8") + "\nPost-receipt record edit.\n",
            encoding="utf-8",
        )
        broken = self.run_cli(
            "check-completion",
            "--project", self.project,
            "--work-item", self.record_path,
        )
        self.assertEqual(2, broken.returncode)
        self.assertIn("COMPLETION_PENDING", broken.stderr)
        # Restoring the bytes is not enough: a canonical done record without
        # its receipt can never report complete through the plain
        # --work-item entry either.
        record.write_bytes(baseline)
        (self.project / ".kosmic/work-receipts" / receipt_name(WORK_RECORD)).unlink()
        unreceipted = self.run_cli(
            "check-completion",
            "--project", self.project,
            "--work-item", self.record_path,
        )
        self.assertEqual(2, unreceipted.returncode)
        self.assertIn("COMPLETION_PENDING", unreceipted.stderr)

    def test_retried_finish_keeps_receipt_without_duplicating_log(self) -> None:
        receipt = json.loads(self.finish().stdout)
        stored = self.project / ".kosmic/work-receipts" / receipt_name(WORK_RECORD)
        receipt_bytes = stored.read_bytes()
        logs = sorted((self.project / "log").glob("*-work-completion.md"))
        self.assertEqual(len(logs), 1)
        rerun = json.loads(self.finish().stdout)
        self.assertEqual(rerun, receipt)
        self.assertEqual(stored.read_bytes(), receipt_bytes)
        self.assertEqual(sorted((self.project / "log").glob("*-work-completion.md")), logs)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
