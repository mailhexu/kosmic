"""Unified safe completion regressions for one ordinary ``work finish``.

Story 001 (workflow-efficiency-and-selective-delegation): a single finish
invocation must run every completion gate — embedded proof, primary scope,
reviewed scope/source binding, the complete shared read-only domain precheck
(the same helper standalone ``check-completion`` runs), and an
immediate-before-write freshness recheck — and terminal retries must verify
only the unchanged receipt record, its immutable originals, and the declared
formal contracts.

Scenario to acceptance mapping:
- test_finish_refuses_undone_dependency_without_receipt:
  AC2 (invalid dependency) + AC3 (``COMPLETION_PRECHECK_FAILED`` with the
  original diagnostic retained); before the unified precheck lands, finish
  publishes the record despite the unfinished declared dependency, so this
  scenario fails first.
- test_unified_finish_publishes_receipt_through_full_precheck:
  AC1 (one ordinary invocation passes every gate and publishes the
  unchanged receipt schema, idempotently).
- test_finish_refuses_retired_input_declaration / missing consumer
  declaration / stale related knowledge / stale declared projection /
  STATUS drift / undeclared math closure / missing proposal declaration:
  AC2 (each domain gate refuses individually before any publication).
- test_scope_denied_takes_precedence_over_review:
  AC4 (``SCOPE_DENIED`` before review validation is consulted).
- test_review_refused_before_domain_precheck:
  AC4 (precheck diagnostics never mask review validation).
- test_malformed_completion_review_refused_after_proof_and_scope:
  repair-malformed-completion-review-gate-precedence (a truthy
  non-mapping completion_review is refused REVIEW_INVALID after the proof
  and primary scope gates — ACCEPTANCE_INVALID/SCOPE_DENIED precedence
  preserved — without crashing the entry snapshot or publishing).
- test_missing_project_config_is_reported_not_swallowed:
  AC3 (config failure reported on the finish path).
- test_record_changed_after_gates_rejects_publication /
  test_source_changed_after_review_rejects_without_repin:
  AC5 (pre-write freshness rechecks detect record/source drift; nothing is
  repinned, rebound, or partially published).
- test_terminal_retry_tolerates_evolution_repairing_status_only /
  tampered record / unreadable receipt / absent receipt:
  AC6-AC8 (terminal invariance, refusal without re-blessing, full-gate
  recovery only through the nonterminal path).
- test_terminal_formal_failure_rejects_retry_and_check_completion:
  AC6 (declared formal math contracts hold on the terminal route through
  both check-completion entry modes).

Story 003 (review-convergence-and-optional-historical-validation): optional
finding annotations are validated for shape and coherence at the same seam.
- test_fixed_response_with_empty_detail_refuses /
  test_refuted_response_with_empty_evidence_refuses /
  test_worker_response_unknown_kind_refuses:
  Story003 AC2 (incomplete worker_response refused REVIEW_INVALID, finding
  named).
- test_blocked_response_requires_prerequisite_and_escalation:
  Story003 AC3 (blocked needs detail=prerequisite + evidence=escalation;
  complete form publishes).
- test_worker_response_fixed_leaves_finding_blocking:
  Story003 AC4 (a worker claim never closes a finding).
- test_resolved_row_accepts_resolution_fixed /
  test_resolved_row_accepts_resolution_refuted /
  test_resolution_on_open_row_refuses:
  Story003 AC5 (resolution fixed|refuted only on resolved rows).
Story003 AC1 (legacy closed rows without annotations stay valid) and AC6
(existing gate precedence/freshness) remain protected by the pre-existing
guards above and in tests/test_record_scoped_completion.py; no duplicates.
"""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import unittest
from unittest.mock import patch

import sympy

try:
    from tests.scoped_completion_support import ScopedProjectCase, commit_baseline, write_document
except ImportError:  # direct test-directory execution
    from scoped_completion_support import ScopedProjectCase, commit_baseline, write_document

try:
    from tests.test_record_scoped_math import (
        derivative_results,
        derivative_script,
        implementation_source,
    )
except ImportError:  # direct test-directory execution
    from test_record_scoped_math import (
        derivative_results,
        derivative_script,
        implementation_source,
    )

from skills.scripts import kosmic_completion, kosmic_project_skills, kosmic_work
from skills.scripts.kosmic_dreams import receipt_name

PROJECT_ID = "scope-demo"
WORK_RECORD = PROJECT_ID + "/quick-task/fixture-task"
DEPENDENCY_NAME = "blocked-dependency.md"
USAGE_BODY = "# Use Demo\n\nRun `demo`.\n"
DEVELOPMENT_BODY = "# Develop Demo\n\nRun contributor checks.\n"


class UnifiedFinishCompletionTest(ScopedProjectCase):
    """One ordinary ``work finish`` runs every completion gate.

    The ``fixture-*`` reviewer identities below are synthetic test fixtures;
    they never represent actual feature approval.
    """

    REVIEW_BASE = "fixture-completion-base"
    CRITERION = "Fixture behavior verified"
    SOURCE = "tests/test_unified_finish_completion.py::UnifiedFinishCompletionTest"

    def setUp(self):
        super().setUp()
        self.dependency_path = self.project / "specs/quick-tasks" / DEPENDENCY_NAME
        write_document(
            self.dependency_path,
            {
                "project_id": PROJECT_ID,
                "subproject_id": None,
                "record_kind": "quick-task",
                "local_id": "blocked-dependency",
                "status": "approved",
                "consumer_interface_change": False,
            },
            "Blocked dependency",
            "## Acceptance Criteria\n\n- [ ] Blocked dependency behavior verified\n",
        )
        commit_baseline(self.root)
        self.record_path = self.project / "specs/quick-tasks/fixture-task.md"
        self.write_record()

    def resolve_record(self):
        return kosmic_work.resolve_work_record(self.project, WORK_RECORD)

    def default_observations(self, *criteria):
        return [{"criterion": criterion,
                 "observation": "The fixture quick-task behavior was exercised through "
                                "the unified completion CLI and behaved as documented.",
                 "source": self.SOURCE}
                for criterion in (criteria or (self.CRITERION,))]

    def review_fields(self, **overrides):
        review = {
            "reviewer": "fixture-reviewer",
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

    def write_record(self, *, criteria=None, observations=None, review=None,
                     extra=None):
        criteria = list(criteria or (self.CRITERION,))
        fields = {
            "project_id": PROJECT_ID,
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
        }
        if extra:
            fields.update(extra)
        write_document(
            self.record_path,
            fields,
            "Fixture",
            "## Acceptance Criteria\n\n"
            + "".join(f"- [ ] {criterion}\n" for criterion in criteria))

    def run_finish(self, *scope_claims: str) -> subprocess.CompletedProcess:
        claims = scope_claims or ("project:specs/",)
        arguments = [
            "work", "finish",
            "--project", self.project,
            "--worktree", self.root,
            "--work-record", WORK_RECORD,
        ]
        for claim in claims:
            arguments.extend(["--scope", claim])
        arguments.extend(["--detail", "unified completion tracer"])
        return self.run_cli(*arguments)

    def finish(self, *scope_claims: str) -> subprocess.CompletedProcess:
        result = self.run_finish(*scope_claims)
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def assert_precheck_refusal(self, result, *retained: str) -> None:
        """The unified precheck refused: no publication, cause retained."""
        self.assertNotEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("COMPLETION_PRECHECK_FAILED", result.stderr)
        for fragment in retained:
            self.assertIn(fragment, result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def bind_status_root(self) -> None:
        entry = self.project / "ProjectEntry.md"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace(
                "working_state: working-tree\n",
                f"working_state: working-tree\nstatus_root: {self.root}\n"),
            encoding="utf-8")
        commit_baseline(self.root, "bind STATUS root for derived reports")

    def write_derivative_pair(self, slug="derivative", power=2):
        script = self.project / "mathdocs" / f"{slug}.py"
        script_text = derivative_script(power)
        script.write_text(script_text, encoding="utf-8")
        srepr, latex = derivative_results(power)
        (self.project / "mathdocs" / f"{slug}.md").write_text(
            "---\n"
            "type: Math Derivation\n"
            "status: stable\n"
            f"derivation: {slug}.py\n"
            f"source_sha256: {hashlib.sha256(script_text.encode()).hexdigest()}\n"
            f"python_version: {platform.python_version()}\n"
            f"sympy_version: {sympy.__version__}\n"
            "verified_at: 2026-09-05T12:00:00Z\n"
            "verified_host: test-host\n"
            f"verified_directory: {self.root.resolve()}\n"
            "---\n"
            "\n"
            f"# {slug.title()}\n"
            "\n"
            "<!-- KOSMIC-MATH-RESULTS:START -->\n"
            "## Verified Results\n"
            "\n"
            f"<!-- MathDoc: {PROJECT_ID}/{slug}#derivative -->\n"
            "$$\n"
            f"{latex}\n"
            "$$\n"
            f"<!-- KOSMIC-SREPR: {srepr} -->\n"
            "<!-- KOSMIC-MATH-RESULTS:END -->\n",
            encoding="utf-8")
        with (self.project / "mathdocs" / "index.md").open("a", encoding="utf-8") as handle:
            handle.write(f"| [{slug}]({slug}.md) | stable | {slug} derivative |\n")
        implementation = self.root / "src/behavior.py"
        implementation.parent.mkdir(parents=True, exist_ok=True)
        implementation.write_text(implementation_source([slug]), encoding="utf-8")
        return implementation

    def stored_receipt_path(self):
        return self.project / ".kosmic/work-receipts" / receipt_name(WORK_RECORD)

    def record_status(self) -> str:
        """Re-resolve the record through the public seam for its lifecycle."""
        return kosmic_work.resolve_work_record(
            self.project, WORK_RECORD, allow_terminal=True).status

    def sibling_project_collision(self) -> None:
        """A vault sibling claiming the same project_id makes the Project
        config unloadable only at load time — the record itself resolves."""
        sibling = self.root / "vault/Projects/collision"
        sibling.mkdir(parents=True)
        (sibling / "ProjectEntry.md").write_text(
            '---\nproject_id: "scope-demo"\nworking_state: working-tree\n'
            "---\n# Collision\n", encoding="utf-8")

    # -- AC1/AC2: one invocation, every gate ---------------------------------

    def test_finish_refuses_undone_dependency_without_receipt(self) -> None:
        """AC2/AC3: finish rejects a declared-but-unfinished dependency.

        Proof, primary scope, and review are valid, so only the shared
        domain precheck can refuse; the record must stay ``approved`` and
        no receipt may exist.
        """
        self.write_record(extra={"depends_on": [DEPENDENCY_NAME]})
        self.assert_precheck_refusal(self.run_finish(), DEPENDENCY_NAME)

    def test_unified_finish_publishes_receipt_through_full_precheck(self) -> None:
        """AC1: a fully valid record publishes the unchanged receipt schema."""
        result = self.finish()
        receipt = json.loads(result.stdout)
        canonical = self.record_path.relative_to(self.project).as_posix()
        record_sha256 = hashlib.sha256(self.record_path.read_bytes()).hexdigest()
        self.assertEqual(receipt["schema"], "kosmic.work-receipt/1")
        self.assertEqual(receipt["identity"], WORK_RECORD)
        self.assertEqual(receipt["status"], "successful")
        self.assertEqual(receipt["record_path"], canonical)
        self.assertEqual(receipt["record_sha256"], record_sha256)
        self.assertEqual(receipt["proof"], {canonical: record_sha256})
        self.assertEqual(json.loads(self.stored_receipt_path().read_text(encoding="utf-8")),
                         receipt)
        self.assertEqual("done", self.record_status())
        repeated = self.finish()
        self.assertEqual(json.loads(repeated.stdout)["identity"], WORK_RECORD)
        checked = self.run_cli("check-completion", "--project", self.project,
                               "--work-item", self.record_path)
        self.assertEqual(
            0,
            checked.returncode,
            msg=f"stdout:\n{checked.stdout}\nstderr:\n{checked.stderr}",
        )

    def test_finish_refuses_retired_input_declaration(self) -> None:
        self.write_record(extra={"acceptance_evidence": ["evidence/old.json"]})
        result = self.run_finish()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("RETIRED_INPUT", result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_finish_refuses_missing_consumer_declaration(self) -> None:
        fields = {
            "project_id": PROJECT_ID,
            "subproject_id": None,
            "record_kind": "quick-task",
            "local_id": "fixture-task",
            "status": "approved",
            "review_base": self.REVIEW_BASE,
            "review_round": 1,
            "completion_observations": self.default_observations(),
            "completion_review": self.review_fields(),
        }
        write_document(self.record_path, fields, "Fixture",
                       "## Acceptance Criteria\n\n"
                       f"- [ ] {self.CRITERION}\n")
        self.assert_precheck_refusal(self.run_finish(), "consumer_interface_change")

    def test_finish_refuses_stale_related_knowledge(self) -> None:
        self.note("using.md", metadata="stale_after: 2000-01-01\n")
        commit_baseline(self.root, "fixture related knowledge baseline")
        self.write_record(extra={"consumer_interface_change": True,
                                 "related_notes": ["using"]})
        self.assert_precheck_refusal(self.run_finish(), "using")

    def test_finish_refuses_stale_declared_projection(self) -> None:
        self.note("using.md", USAGE_BODY)
        self.note("developing.md", DEVELOPMENT_BODY)
        generated = self.run_cli("generate", "--project", self.project,
                                 "--work-record", WORK_RECORD)
        self.assertEqual(
            0,
            generated.returncode,
            msg=f"stdout:\n{generated.stdout}\nstderr:\n{generated.stderr}",
        )
        using = self.project / "notes" / "using.md"
        using.write_text(
            using.read_text(encoding="utf-8") + "New interface behavior.\n",
            encoding="utf-8")
        claims = ("project:specs/", "project:notes/", "project:skills/")
        self.write_record(
            extra={"consumer_interface_change": True, "related_notes": ["using"]},
            review=self.review_fields(scope=list(claims)))
        self.assert_precheck_refusal(self.run_finish(*claims), "using")
        # Positive control: a regenerated projection lets the same record finish.
        regenerated = self.run_cli("generate", "--project", self.project,
                                   "--work-record", WORK_RECORD)
        self.assertEqual(0, regenerated.returncode, msg=regenerated.stderr)
        self.assertEqual(0, self.run_finish(*claims).returncode)

    def test_finish_refuses_status_drift(self) -> None:
        self.bind_status_root()
        (self.root / "STATUS.md").write_text("hand-edited stale projection\n",
                                             encoding="utf-8")
        self.assert_precheck_refusal(self.run_finish(), "STATUS_STALE")
        # Positive control: current derived STATUS lets the same record finish.
        kosmic_completion._write_status_reports(self.project, None)
        self.assertEqual(0, self.finish().returncode)

    def test_finish_refuses_undeclared_math_closure(self) -> None:
        self.write_record(extra={"derivations": ["ghost"]})
        self.assert_precheck_refusal(self.run_finish(), "ghost")

    def test_finish_refuses_missing_proposal_declaration(self) -> None:
        self.write_record(extra={"proposal_required": True})
        self.assert_precheck_refusal(self.run_finish(), "skill_proposal")

    # -- AC3/AC4: precedence, translation, config ---------------------------

    def test_scope_denied_takes_precedence_over_review(self) -> None:
        self.write_record(review=self.review_fields(decision="changes-requested"))
        result = self.run_finish("worktree:src/")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SCOPE_DENIED", result.stderr)
        self.assertNotIn("REVIEW_INVALID", result.stderr)
        self.assertNotIn("COMPLETION_PRECHECK_FAILED", result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_review_refused_before_domain_precheck(self) -> None:
        self.write_record(review=self.review_fields(decision="changes-requested"),
                          extra={"depends_on": [DEPENDENCY_NAME]})
        result = self.run_finish()
        self.assertNotEqual(0, result.returncode)
        self.assertIn("REVIEW_INVALID", result.stderr)
        self.assertNotIn("COMPLETION_PRECHECK_FAILED", result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_malformed_completion_review_refused_after_proof_and_scope(self) -> None:
        """A truthy non-mapping completion_review is refused, never crashed.

        The entry snapshot must stay safe for non-mapping review metadata:
        the malformed value reaches the existing ordered review gate and
        fails as ``REVIEW_INVALID`` only after the proof and primary scope
        gates, so earlier invalid states keep their precedence. No refusal
        publishes anything or mutates the record bytes.
        """
        for malformed in (["legacy list review"], "legacy text review", 20260101):
            with self.subTest(review=malformed):
                self.write_record(review=malformed)
                record_bytes = self.record_path.read_bytes()
                result = self.run_finish()
                self.assertNotEqual(
                    0,
                    result.returncode,
                    msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
                )
                self.assertIn("REVIEW_INVALID", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(record_bytes, self.record_path.read_bytes())
                self.assertEqual("approved", self.record_status())
                self.assertFalse((self.project / ".kosmic/work-receipts").exists())
        # Precedence: an invalid proof refuses as ACCEPTANCE_INVALID before
        # the malformed review is consulted.
        self.write_record(observations=[], review=["legacy list review"])
        proof = self.run_finish()
        self.assertNotEqual(0, proof.returncode, msg=proof.stderr)
        self.assertIn("ACCEPTANCE_INVALID", proof.stderr)
        self.assertNotIn("REVIEW_INVALID", proof.stderr)
        # Precedence: an uncovered primary finish claim refuses as
        # SCOPE_DENIED before the malformed review is consulted.
        self.write_record(review="legacy text review")
        scope = self.run_finish("worktree:src/")
        self.assertNotEqual(0, scope.returncode, msg=scope.stderr)
        self.assertIn("SCOPE_DENIED", scope.stderr)
        self.assertNotIn("REVIEW_INVALID", scope.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_unloadable_project_config_is_reported_not_swallowed(self) -> None:
        """AC3: a real config failure after record resolution is reported.

        The vault sibling claims the same project_id, so the record resolves
        and every earlier gate passes, but the strict Project load feeding
        the shared precheck fails and must surface as
        ``COMPLETION_PRECHECK_FAILED``, never a silent success.
        """
        self.sibling_project_collision()
        # Commit the collision input so nothing is unclaimed: the record and
        # scope gates pass cleanly and only the strict Project load fails.
        commit_baseline(self.root, "fixture config collision baseline")
        self.assert_precheck_refusal(self.run_finish())

    def test_config_failure_does_not_mask_scope_denial(self) -> None:
        self.sibling_project_collision()
        result = self.run_finish("worktree:src/")
        self.assertNotEqual(0, result.returncode)
        self.assertIn("SCOPE_DENIED", result.stderr)
        self.assertNotIn("COMPLETION_PRECHECK_FAILED", result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    # -- AC5: pre-write freshness rechecks ----------------------------------

    def test_record_changed_after_gates_rejects_publication(self) -> None:
        original = kosmic_project_skills._check_existing_completion

        def mutate_then_precheck(project, work_item, **kwargs):
            original(project, work_item, **kwargs)
            with self.record_path.open("a", encoding="utf-8") as handle:
                handle.write("<!-- drifted after the gates -->\n")

        with patch.object(kosmic_project_skills, "_check_existing_completion",
                          side_effect=mutate_then_precheck):
            with self.assertRaises(kosmic_work.WorkdirError) as caught:
                kosmic_completion.finish_work(
                    self.project, self.root, WORK_RECORD, ["project:specs/"])
        self.assertEqual(caught.exception.code, "RECORD_NOT_AUTHORIZED")
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_source_changed_after_gates_rejects_publication(self) -> None:
        """A real source-file mutation after the review gate is detected.

        The patch only injects timing at the shared-precheck boundary; the
        mutation, both gates, and the compared revision are all real. The
        review binding in the record is never repinned.
        """
        source = self.root / "src/behavior.txt"
        record = self.resolve_record()
        revision = kosmic_completion.source_revision(self.root, self.project, record)
        original = kosmic_project_skills._check_existing_completion

        def mutate_source_then_precheck(project, work_item, **kwargs):
            original(project, work_item, **kwargs)
            source.parent.mkdir(parents=True, exist_ok=True)
            source.write_text("drifted after review\n", encoding="utf-8")

        with patch.object(kosmic_project_skills, "_check_existing_completion",
                          side_effect=mutate_source_then_precheck):
            with self.assertRaises(kosmic_work.WorkdirError) as caught:
                kosmic_completion.finish_work(
                    self.project, self.root, WORK_RECORD, ["project:specs/"])
        self.assertEqual(caught.exception.code, "REVIEW_INVALID")
        self.assertIn(f'"reviewed_revision": "{revision}"',
                      self.record_path.read_text(encoding="utf-8"))
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    # -- AC6-AC8: terminal route invariance ---------------------------------

    def test_terminal_retry_tolerates_evolution_repairing_status_only(self) -> None:
        self.bind_status_root()
        kosmic_completion._write_status_reports(self.project, None)
        receipt = json.loads(self.finish().stdout)
        receipt_path = self.stored_receipt_path()
        receipt_bytes = receipt_path.read_bytes()
        logs = sorted(self.project.glob("log/*-work-completion.md"))
        self.assertEqual(len(logs), 1)
        log_bytes = logs[0].read_bytes()
        # Ordinary linked-note evolution plus a hand-edited derived STATUS:
        # the retry must neither re-bless nor repin anything immutable, and
        # must repair only the derived STATUS reports.
        (self.project / "notes" / "index.md").write_text(
            "# Knowledge\n\nA later documented convention.\n", encoding="utf-8")
        (self.root / "STATUS.md").write_text("hand-edited stale projection\n",
                                             encoding="utf-8")
        repaired = self.finish()
        self.assertEqual(json.loads(repaired.stdout), receipt)
        self.assertEqual(receipt_path.read_bytes(), receipt_bytes)
        self.assertEqual(logs[0].read_bytes(), log_bytes)
        status_text = (self.root / "STATUS.md").read_text(encoding="utf-8")
        self.assertNotIn("hand-edited stale projection", status_text)

    def test_terminal_retry_rejects_tampered_record_bytes(self) -> None:
        self.finish()
        receipt_path = self.stored_receipt_path()
        receipt_bytes = receipt_path.read_bytes()
        self.record_path.write_text(
            self.record_path.read_text(encoding="utf-8") + "\nPost-receipt drift.\n",
            encoding="utf-8")
        result = self.run_finish()
        self.assertNotEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("COMPLETION_", result.stderr)
        self.assertEqual(receipt_path.read_bytes(), receipt_bytes)

    def test_terminal_retry_rejects_unreadable_receipt(self) -> None:
        self.finish()
        receipt_path = self.stored_receipt_path()
        receipt_path.write_text("not json\n", encoding="utf-8")
        logs = sorted(self.project.glob("log/*-work-completion.md"))
        result = self.run_finish()
        self.assertNotEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("COMPLETION_PENDING", result.stderr)
        # Never re-blessed: the unreadable receipt bytes are untouched and no
        # second completion-log line appeared.
        self.assertEqual(receipt_path.read_text(encoding="utf-8"), "not json\n")
        self.assertEqual(sorted(self.project.glob("log/*-work-completion.md")), logs)

    def test_absent_receipt_reruns_every_gate(self) -> None:
        self.finish()
        receipt_path = self.stored_receipt_path()
        logs = sorted(self.project.glob("log/*-work-completion.md"))
        receipt_path.unlink()
        recovered = self.finish()
        self.assertEqual(json.loads(recovered.stdout)["status"], "successful")
        self.assertTrue(receipt_path.is_file())
        self.assertEqual(sorted(self.project.glob("log/*-work-completion.md")), logs)
        self.assertEqual("done", self.record_status())

    def test_terminal_formal_failure_rejects_retry_and_check_completion(self) -> None:
        implementation = self.write_derivative_pair()
        claims = ("project:specs/", "project:mathdocs/", "worktree:src/")
        self.write_record(
            extra={"derivations": ["derivative"],
                   "math_implementation_files": [
                       implementation.relative_to(self.root).as_posix()]},
            review=self.review_fields(scope=list(claims)))
        self.assertEqual(0, self.run_finish(*claims).returncode)
        receipt_path = self.stored_receipt_path()
        receipt_bytes = receipt_path.read_bytes()
        # The declared math closure breaks after the receipt: the terminal
        # retry and the plain check-completion entry must both reject through
        # the same shared formal helper, without touching the receipt.
        (self.project / "mathdocs" / "derivative.md").unlink()
        retry = self.run_finish(*claims)
        self.assertNotEqual(
            0,
            retry.returncode,
            msg=f"stdout:\n{retry.stdout}\nstderr:\n{retry.stderr}",
        )
        self.assertIn("derivative", retry.stderr)
        checked = self.run_cli("check-completion", "--project", self.project,
                               "--work-item", self.record_path)
        self.assertNotEqual(0, checked.returncode)
        self.assertIn("derivative", checked.stderr)
        checked_record = self.run_cli(
            "check-completion", "--project", self.project,
            "--work-item", self.record_path, "--work-record", WORK_RECORD)
        self.assertNotEqual(0, checked_record.returncode, checked_record.stdout)
        self.assertIn("derivative", checked_record.stderr)
        self.assertEqual(receipt_path.read_bytes(), receipt_bytes)

    # -- Story 003: compatible finding-response and refutation annotations ----

    def test_fixed_response_with_empty_detail_refuses(self) -> None:
        """Story003 AC2: an incomplete worker claim is structurally refused.

        ``worker_response`` with ``kind: fixed`` but empty ``detail`` fails
        as ``REVIEW_INVALID`` naming the finding, at the ordinary finish
        seam, without publishing anything.
        """
        self.write_record(review=self.review_fields(findings=[
            {"id": "KF-1", "disposition": "Blocking", "status": "open",
             "worker_response": {"kind": "fixed", "detail": "   ",
                                 "evidence": "Fixture evidence text."}},
        ]))
        result = self.run_finish()
        self.assertNotEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("REVIEW_INVALID", result.stderr)
        self.assertIn("KF-1", result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_refuted_response_with_empty_evidence_refuses(self) -> None:
        """Story003 AC2: ``refuted`` without evidence is refused, named."""
        self.write_record(review=self.review_fields(findings=[
            {"id": "KF-2", "disposition": "Blocking", "status": "open",
             "worker_response": {"kind": "refuted",
                                 "detail": "Fixture refutation rationale.",
                                 "evidence": ""}},
        ]))
        result = self.run_finish()
        self.assertNotEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("REVIEW_INVALID", result.stderr)
        self.assertIn("KF-2", result.stderr)
        self.assertIn("evidence", result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_worker_response_unknown_kind_refuses(self) -> None:
        """Story003 AC2: only fixed/refuted/blocked kinds are accepted."""
        self.write_record(review=self.review_fields(findings=[
            {"id": "KF-3", "disposition": "Blocking", "status": "open",
             "worker_response": {"kind": "wontfix", "detail": "x",
                                 "evidence": "y"}},
        ]))
        result = self.run_finish()
        self.assertNotEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("REVIEW_INVALID", result.stderr)
        self.assertIn("KF-3", result.stderr)

    def test_blocked_response_requires_prerequisite_and_escalation(self) -> None:
        """Story003 AC3: blocked needs detail (prerequisite) + evidence
        (escalation rationale); a complete claim passes annotation
        validation yet still never closes the finding."""
        blocked_missing_prerequisite = self.review_fields(findings=[
            {"id": "KF-4", "disposition": "Blocking", "status": "open",
             "worker_response": {"kind": "blocked", "detail": "",
                                 "evidence": "Escalated to the maintainer."}},
        ])
        self.write_record(review=blocked_missing_prerequisite)
        missing = self.run_finish()
        self.assertNotEqual(
            0,
            missing.returncode,
            msg=f"stdout:\n{missing.stdout}\nstderr:\n{missing.stderr}",
        )
        self.assertIn("REVIEW_INVALID", missing.stderr)
        self.assertIn("KF-4", missing.stderr)
        self.assertIn("prerequisite", missing.stderr)

        blocked_missing_escalation = self.review_fields(findings=[
            {"id": "KF-4", "disposition": "Blocking", "status": "open",
             "worker_response": {"kind": "blocked",
                                 "detail": "Prerequisite: upstream parser fix.",
                                 "evidence": "   "}},
        ])
        self.write_record(review=blocked_missing_escalation)
        missing_escalation = self.run_finish()
        self.assertNotEqual(
            0,
            missing_escalation.returncode,
            msg=f"stdout:\n{missing_escalation.stdout}\n"
                f"stderr:\n{missing_escalation.stderr}",
        )
        self.assertIn("REVIEW_INVALID", missing_escalation.stderr)
        self.assertIn("escalation", missing_escalation.stderr)

        blocked_complete = self.review_fields(findings=[
            {"id": "KF-4", "disposition": "Blocking", "status": "open",
             "worker_response": {
                 "kind": "blocked",
                 "detail": "Prerequisite: upstream parser fix is pending.",
                 "evidence": "Escalated to the maintainer with the failing case."}},
        ])
        self.write_record(review=blocked_complete)
        complete = self.run_finish()
        # The complete blocked claim passes annotation validation (no
        # prerequisite/escalation diagnostic), but a worker claim never
        # closes the finding: the open Blocking row still refuses finish.
        self.assertNotEqual(
            0,
            complete.returncode,
            msg=f"stdout:\n{complete.stdout}\nstderr:\n{complete.stderr}",
        )
        self.assertIn("REVIEW_INVALID", complete.stderr)
        self.assertIn("unresolved blocking finding KF-4", complete.stderr)
        self.assertNotIn("prerequisite", complete.stderr)
        self.assertNotIn("escalation", complete.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_worker_response_fixed_leaves_finding_blocking(self) -> None:
        """Story003 AC4: a worker claim alone never closes a finding.

        A complete ``fixed`` response on an open Blocking row keeps the row
        unresolved, so finish is refused exactly as without the annotation.
        """
        self.write_record(review=self.review_fields(findings=[
            {"id": "KF-5", "disposition": "Blocking", "status": "open",
             "worker_response": {
                 "kind": "fixed",
                 "detail": "Guard applied; awaiting reviewer verification.",
                 "evidence": "Malformed-review CLI case returned REVIEW_INVALID."}},
        ]))
        result = self.run_finish()
        self.assertNotEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("REVIEW_INVALID", result.stderr)
        self.assertIn("unresolved blocking finding KF-5", result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_resolved_row_accepts_resolution_fixed(self) -> None:
        """Story003 AC5: reviewer closure with resolution: fixed is valid."""
        self.write_record(review=self.review_fields(findings=[
            {"id": "KF-6", "disposition": "Blocking", "status": "resolved",
             "resolution": "fixed",
             "resolution_note": "Fixture reviewer judgment retained."},
        ]))
        receipt = json.loads(self.finish().stdout)
        self.assertEqual(receipt["status"], "successful")

    def test_resolved_row_accepts_resolution_refuted(self) -> None:
        """Story003 AC5: resolution: refuted keeps the rationale inspectable."""
        note = "Fixture refutation rationale retained on the row."
        self.write_record(review=self.review_fields(findings=[
            {"id": "KF-6", "disposition": "Blocking", "status": "resolved",
             "resolution": "refuted", "resolution_note": note},
        ]))
        receipt = json.loads(self.finish().stdout)
        self.assertEqual(receipt["status"], "successful")
        self.assertIn(note, self.record_path.read_text(encoding="utf-8"))

    def test_standalone_check_completion_refuses_malformed_annotation(self) -> None:
        """Story003 AC2/AC3/AC5: standalone ``check-completion`` validates
        supplied annotations without demanding the full modern review.

        The diagnostic-only work-item entry must refuse a malformed
        ``worker_response`` by name even though it deliberately does not
        require review approval, proof, or Blocking closure. Legacy records
        without annotations keep passing unchanged.
        """
        self.write_record(review=self.review_fields(findings=[
            {"id": "A-1", "disposition": "Blocking", "status": "open",
             "worker_response": {"kind": "fixed", "detail": "",
                                 "evidence": "Fixture evidence text."}},
        ]))
        checked = self.run_cli("check-completion", "--project", self.project,
                               "--work-item", self.record_path)
        self.assertNotEqual(
            0,
            checked.returncode,
            msg=f"stdout:\n{checked.stdout}\nstderr:\n{checked.stderr}",
        )
        self.assertIn("REVIEW_INVALID", checked.stderr)
        self.assertIn("A-1", checked.stderr)
        self.assertIn("non-empty detail", checked.stderr)

    def test_resolution_on_open_row_refuses(self) -> None:
        """Story003 AC5: resolution is reviewer-only closure vocabulary.

        ``resolution`` on a row that is not ``resolved`` — here an accepted
        non-blocking follow-up — is incoherent and refused by name.
        """
        self.write_record(review=self.review_fields(findings=[
            {"id": "KF-7", "disposition": "Follow-up", "status": "open",
             "resolution": "fixed"},
        ]))
        result = self.run_finish()
        self.assertNotEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("REVIEW_INVALID", result.stderr)
        self.assertIn("KF-7", result.stderr)
        self.assertEqual("approved", self.record_status())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
