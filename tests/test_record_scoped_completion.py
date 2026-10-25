"""Record-scoped completion regression scenarios driven only through the CLI.

Completion must validate the active record's declared knowledge, math, and
Consumer projection without coupling to unrelated legacy notes, while full
``validate`` stays a strict whole-vault audit.
"""

from __future__ import annotations
import concurrent.futures
import contextlib
import os
import fcntl

import shutil
import subprocess
import unittest
from pathlib import Path
from unittest import mock

try:
    from tests.scoped_completion_support import (
        ScopedProjectCase,
        MATH_INDEX,
        commit_baseline,
        write_document,
    )
except ImportError:  # direct test-directory execution
    from scoped_completion_support import (
        ScopedProjectCase,
        MATH_INDEX,
        commit_baseline,
        write_document,
    )

import hashlib
import json

from skills.scripts import kosmic_completion, kosmic_project_skills, kosmic_work
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

    def write_record(self, *, criteria=None, observations=None, review=None,
                     extra=None):
        criteria = list(criteria or (self.CRITERION,))
        fields = {
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
        }
        if extra:
            fields.update(extra)
        write_document(
            self.record_path,
            fields,
            "Fixture",
            "## Acceptance Criteria\n\n"
            + "".join(f"- [ ] {criterion}\n" for criterion in criteria))

    def run_finish(self, *scope_claims: str):
        claims = scope_claims or ("project:specs/",)
        arguments = [
            "work", "finish",
            "--project", self.project,
            "--worktree", self.root,
            "--work-record", WORK_RECORD,
        ]
        for claim in claims:
            arguments.extend(["--scope", claim])
        arguments.extend(["--detail", "embedded completion tracer"])
        return self.run_cli(*arguments)

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

    def native_indexed_record(self):
        review = self.review_fields()
        self.record_path.unlink()
        created = self.run_cli("spec-create", "--project", self.project,
                               "--kind", "quick-task", "--title", "Fixture task")
        self.assertEqual(created.returncode, 0, created.stderr)
        result = json.loads(created.stdout)
        self.record_path = self.project / result["record_path"]
        self.write_record(review=review)
        commit_baseline(self.root)
        return self.project / result["index_path"]

    def test_creation_lock_exemption_does_not_hide_other_project_metadata(self) -> None:
        self.native_indexed_record()
        metadata = self.project / ".kosmic/source-context.txt"
        metadata.write_text("Unreviewed measurement context.\n", encoding="utf-8")
        record_bytes = self.record_path.read_bytes()
        result = self.run_finish()
        self.assertEqual(2, result.returncode, result.stderr)
        self.assertIn("SCOPE_DENIED", result.stderr)
        self.assertIn("source-context.txt", result.stderr)
        self.assertEqual(record_bytes, self.record_path.read_bytes())
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())

    def test_finish_and_native_creation_preserve_interleaved_rows(self) -> None:
        index = self.native_indexed_record()
        context = "\nUnrelated experiment context.\n"
        index.write_text(index.read_text() + context)
        lock = self.project / ".kosmic/create.lock"
        with lock.open("rb") as stream, concurrent.futures.ThreadPoolExecutor(2) as pool:
            fcntl.flock(stream, fcntl.LOCK_EX)
            finishing = pool.submit(self.run_finish)
            creating = pool.submit(self.run_cli, "spec-create", "--project", self.project,
                                   "--kind", "quick-task", "--title", "Neighbor [A] | context")
            waited_for_writer = False
            try:
                finishing.result(timeout=1)
            except concurrent.futures.TimeoutError:
                waited_for_writer = True
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)
            finished = finishing.result(timeout=20)
            neighbor = creating.result(timeout=20)
        self.assertEqual(finished.returncode, 0, finished.stderr)
        self.assertEqual(neighbor.returncode, 0, neighbor.stderr)
        self.assertTrue(waited_for_writer, "finish bypassed the active index writer")
        self.assertEqual(json.loads(finished.stdout)["identity"], WORK_RECORD)
        neighbor_result = json.loads(neighbor.stdout)
        text = index.read_text()
        self.assertIn(context, text)
        self.assertIn("[Fixture task](quick-tasks/fixture-task.md) | done |", text)
        relative = (self.project / neighbor_result["record_path"]).relative_to(index.parent)
        self.assertIn(f"]({relative.as_posix()}) | draft |", text)
        self.assertIn(r"[Neighbor \[A\] \| context]", text)


    def test_finish_refuses_external_index_divergence_and_recovers(self) -> None:
        index = self.native_indexed_record()
        external = index.read_bytes() + b"\nExternal measurement context.\n"
        identity = index.stat()
        real_read_text, real_fdopen = Path.read_text, os.fdopen
        injected = False

        def external_edit():
            nonlocal injected
            if not injected and "\nstatus: done\n" in real_read_text(self.record_path):
                injected = True
                index.write_bytes(external)

        def read_text(path, *args, **kwargs):
            text = real_read_text(path, *args, **kwargs)
            if path == index:
                external_edit()
            return text

        @contextlib.contextmanager
        def fdopen(fd, mode="r", *args, **kwargs):
            info = os.fstat(fd)
            is_index = (info.st_dev, info.st_ino) == (identity.st_dev, identity.st_ino)
            with real_fdopen(fd, mode, *args, **kwargs) as stream:
                if not is_index or "r" not in mode:
                    yield stream
                else:
                    class Snapshot:
                        def read(self, *read_args, **read_kwargs):
                            data = stream.read(*read_args, **read_kwargs)
                            external_edit()
                            return data
                    yield Snapshot()

        failure = None
        with mock.patch.object(Path, "read_text", read_text), mock.patch.object(os, "fdopen", fdopen):
            try:
                kosmic_completion.finish_work(self.project, self.root, WORK_RECORD,
                                              ["project:specs/"])
            except kosmic_work.WorkdirError as error:
                failure = error
        self.assertTrue(injected, "external edit must occur after the index snapshot")
        self.assertEqual(index.read_bytes(), external)
        self.assertIsInstance(failure, kosmic_work.WorkdirError)
        self.assertEqual(failure.code, "RESERVATION_CONFLICT")
        self.assertIn("specs/INDEX.md", str(failure))
        stored = self.project / ".kosmic/work-receipts" / receipt_name(WORK_RECORD)
        self.assertFalse(stored.exists())
        receipt = json.loads(self.finish().stdout)
        self.assertEqual(receipt["identity"], WORK_RECORD)
        self.assertIn("External measurement context.", index.read_text())
        self.assertIn("[Fixture task](quick-tasks/fixture-task.md) | done |", index.read_text())


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

    def test_finish_publishes_on_cli_prepared_matching_revision(self) -> None:
        """Story 003: the reviewer pin comes from the public preparation CLI;
        the actual reviewed delta publishes a real receipt."""
        source = self.root / "src/tool.py"
        source.parent.mkdir(parents=True)
        source.write_text("VALUE = 1\n")
        prepared_result = self.run_cli(
            "work", "prepare-completion",
            "--project", self.project,
            "--work-record", WORK_RECORD,
            "--worktree", self.root,
        )
        self.assertEqual(
            0,
            prepared_result.returncode,
            msg=f"stdout:\n{prepared_result.stdout}\nstderr:\n{prepared_result.stderr}",
        )
        prepared = json.loads(prepared_result.stdout)
        review = self.review_fields(
            reviewed_revision=prepared["source_revision"],
            scope=["project:specs/", "worktree:src/"],
        )
        self.write_record(review=review)
        result = self.run_finish("project:specs/", "worktree:src/")
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertEqual("successful", json.loads(result.stdout)["status"])
        self.assertTrue(
            (self.project / ".kosmic/work-receipts" / receipt_name(WORK_RECORD)).exists())
        self.assertIn("status: done", self.record_path.read_text(encoding="utf-8"))

    def test_finish_refuses_source_drift_after_cli_prepared_pin(self) -> None:
        """Story 003: real source drift after the CLI-prepared review pin
        refuses completion and publishes nothing."""
        source = self.root / "src/tool.py"
        source.parent.mkdir(parents=True)
        source.write_text("VALUE = 1\n")
        prepared_result = self.run_cli(
            "work", "prepare-completion",
            "--project", self.project,
            "--work-record", WORK_RECORD,
            "--worktree", self.root,
        )
        self.assertEqual(
            0,
            prepared_result.returncode,
            msg=f"stdout:\n{prepared_result.stdout}\nstderr:\n{prepared_result.stderr}",
        )
        prepared = json.loads(prepared_result.stdout)
        source.write_text("VALUE = 2\n")
        review = self.review_fields(
            reviewed_revision=prepared["source_revision"],
            scope=["project:specs/", "worktree:src/"],
        )
        self.write_record(review=review)
        record_bytes = self.record_path.read_bytes()
        result = self.run_finish("project:specs/", "worktree:src/")
        self.assertEqual(
            2,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("REVIEW_INVALID", result.stderr)
        self.assertIn("reviewed revision differs", result.stderr)
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())
        self.assertEqual(record_bytes, self.record_path.read_bytes())

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
        # The empty reviewed scope is legitimate only when there is no actual
        # changed work; here the record edit itself is real uncovered work,
        # so coverage must refuse even though finish claims would cover it.
        self.refusal(review=self.review_fields(scope=[]), code="REVIEW_INVALID")

    def test_plain_done_entry_ignores_later_note_deprecation(self) -> None:
        """Terminal invariance edge (03STD-03/03SPEC-2): a record that
        DECLARES related_notes and finished with a valid receipt keeps
        completing through the plain entry after a later note deprecation or
        merge — no record byte mutation, direct terminal receipt still
        valid. The pre-finish path still rejects stale/deprecated declared
        notes (existing coverage)."""
        self.note("linked.md")
        commit_baseline(self.root, "declare linked knowledge note")
        self.write_record(extra={"related_notes": ["notes/linked.md"]},
                          review=self.review_fields())
        pre = self.run_cli("check-completion", "--project", self.project,
                           "--work-item", self.record_path)
        self.assertEqual(
            0,
            pre.returncode,
            msg=f"stdout:\n{pre.stdout}\nstderr:\n{pre.stderr}",
        )
        result = self.run_finish("project:specs/")
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        record = kosmic_work.resolve_work_record(
            self.project, WORK_RECORD, allow_terminal=True)
        validated = kosmic_completion.check_terminal_receipt(
            self.project, record)
        self.assertEqual(validated["status"], "successful")
        note = self.project / "notes/linked.md"
        note.write_text(
            "---\ntype: reference\nstatus: deprecated\naudience: both\n"
            "artifact_role: knowledge\n---\n\n# Linked\n\nMerged elsewhere.\n",
            encoding="utf-8")
        record_bytes = self.record_path.read_bytes()
        after = self.run_cli("check-completion", "--project", self.project,
                             "--work-item", self.record_path)
        self.assertEqual(
            0,
            after.returncode,
            msg=f"stdout:\n{after.stdout}\nstderr:\n{after.stderr}",
        )
        self.assertEqual(self.record_path.read_bytes(), record_bytes)
        still_valid = kosmic_completion.check_terminal_receipt(
            self.project, record)
        self.assertEqual(still_valid["status"], "successful")

    def test_record_only_empty_reviewed_scope_finishes(self) -> None:
        """Record-only work (everything committed, only canonical publication
        outputs derived afterwards) with an empty reviewed scope must finish:
        coverage is skipped because the computed changed path set is empty,
        while the finish still requires its own scope claims."""
        entry = self.project / "ProjectEntry.md"
        entry.write_text(
            "---\nproject_id: scope-demo\nworking_state: working-tree\n"
            f"status_root: {self.root}\n---\n\n# Demo\n",
            encoding="utf-8")
        self.write_record(review=self.review_fields(scope=[]))
        commit_baseline(self.root, "record-only completion state")
        self.run_cli("generate-status", "--project", self.project,
                     "--work-record", WORK_RECORD)
        self.assertTrue((self.root / "STATUS.md").exists())
        result = self.run_finish("project:specs/")
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        receipt = json.loads(result.stdout)
        self.assertEqual(receipt["status"], "successful")

    def test_plain_check_refuses_broken_math_contract_after_receipt(self) -> None:
        """A finished record with a valid receipt must still be refused by
        the plain --work-item entry when the CURRENT math contract breaks
        (source script bytes drift from the recorded derivation checksum):
        the specific math gate fires on the plain entry while the direct
        terminal receipt stays valid, and the completed record is never
        edited."""
        source = self.root / "src/behavior.txt"
        source.parent.mkdir(parents=True)
        source.write_text(
            "# fixture behavior\n\nMathDoc: scope-demo/triple-output\n",
            encoding="utf-8")
        script = self.project / "mathdocs/triple-output.py"
        script.parent.mkdir(parents=True, exist_ok=True)
        script.write_text("def triple_output(value):\n    return 3 * value\n",
                          encoding="utf-8")
        results = kosmic_project_skills.render_math_results(
            "scope-demo", "triple-output",
            [kosmic_project_skills.MathResult(
                name="verified_triple", latex="6", srepr="6")])
        note = self.project / "mathdocs/triple-output.md"
        note.write_text(
            "---\ntype: Math Derivation\nderivation: triple-output.py\n"
            "status: stable\nsource_sha256: "
            + hashlib.sha256(script.read_bytes()).hexdigest()
            + "\npython_version: 3.11\nsympy_version: 1.13\n"
            "verified_at: 2026-10-18T00:00:00Z\nverified_host: fixture-host\n"
            f"verified_directory: {self.project / 'mathdocs'}\n---\n\n"
            "# Triple output derivation\n\n" + results,
            encoding="utf-8")
        index = self.project / "mathdocs/index.md"
        index.write_text(MATH_INDEX
                         + "| [triple-output](triple-output.md) | stable | "
                         "Verified fixture derivation |\n", encoding="utf-8")
        commit_baseline(self.root, "math contract baseline")
        # Binding happens after every source file is in its reviewed state
        # (the drift below happens strictly after the receipt).
        self.write_record(
            extra={
                "derivations": ["triple-output"],
                "math_implementation_files": ["src/behavior.txt"],
            },
            review=self.review_fields(
                scope=["worktree:src/", "project:mathdocs/", "project:specs/"]))
        self.run_cli("generate-status", "--project", self.project,
                     "--work-record", WORK_RECORD)
        result = self.run_finish(
            "worktree:src/", "project:mathdocs/", "project:specs/")
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        record = kosmic_work.resolve_work_record(
            self.project, WORK_RECORD, allow_terminal=True)
        validated = kosmic_completion.check_terminal_receipt(
            self.project, record)
        self.assertEqual(validated["status"], "successful")
        record_bytes = self.record_path.read_bytes()
        script.write_text("def triple_output(value):\n    return 4 * value\n",
                          encoding="utf-8")
        self.assertEqual(self.record_path.read_bytes(), record_bytes)
        broken = self.run_cli(
            "check-completion", "--project", self.project, "--work-item", self.record_path)
        self.assertEqual(2, broken.returncode)
        self.assertIn("source_sha256 does not match", broken.stderr)
        still_valid = kosmic_completion.check_terminal_receipt(
            self.project, record)
        self.assertEqual(still_valid["status"], "successful")

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

    def test_derived_status_before_finish_does_not_self_block(self) -> None:
        """Plausible flow regression: a fresh ``generate-status`` under the
        approved record leaves the derived STATUS.md dirty at the worktree
        root, and finish with real source + record scope claims must not
        self-block on that canonical publication output. Genuinely outside
        work still refuses (out-of-scope boundary coverage)."""
        entry = self.project / "ProjectEntry.md"
        entry.write_text(
            "---\nproject_id: scope-demo\nworking_state: working-tree\n"
            f"status_root: {self.root}\n---\n\n# Demo\n",
            encoding="utf-8")
        commit_baseline(self.root, "bind STATUS root for derived reports")
        source = self.root / "src/behavior.txt"
        source.parent.mkdir(parents=True)
        source.write_text("fixture behavior output: verified\n", encoding="utf-8")
        # Real flow: reviewers see the actual dirty delta, so the review is
        # embedded AFTER the source edit exists and binds the resulting
        # revision.
        self.write_record(review=self.review_fields(
            scope=["worktree:src/", "project:specs/"]))
        generated = self.run_cli("generate-status", "--project", self.project,
                                 "--work-record", WORK_RECORD)
        self.assertEqual(
            0,
            generated.returncode,
            msg=f"stdout:\n{generated.stdout}\nstderr:\n{generated.stderr}",
        )
        self.assertTrue((self.root / "STATUS.md").exists())
        result = self.run_finish("worktree:src/", "project:specs/")
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        receipt = json.loads(result.stdout)
        canonical = self.record_path.relative_to(self.project).as_posix()
        record_sha256 = hashlib.sha256(self.record_path.read_bytes()).hexdigest()
        self.assertEqual(receipt["status"], "successful")
        self.assertEqual(receipt["record_path"], canonical)
        self.assertEqual(receipt["proof"], {canonical: record_sha256})

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
        entry = self.project / "ProjectEntry.md"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace(
                "working_state: working-tree\n",
                f"working_state: working-tree\nstatus_root: {self.root.resolve()}\n"),
            encoding="utf-8")
        foreign_status = {}
        entries = []
        for index in range(2):
            directory = self.root / f"registered-status-{index}"
            directory.mkdir()
            status_path = directory / "STATUS.md"
            sentinel = f"foreign status sentinel {index}\n".encode("utf-8")
            status_path.write_bytes(sentinel)
            foreign_status[status_path] = sentinel
            entries.append({
                "schema": "kosmic.workdir/1",
                "path": str(directory.resolve()),
                "directory_id": kosmic_work.directory_id(directory),
                "fixed_subproject_id": None,
                "authority": {"record": WORK_RECORD, "run_id": f"status-fixture-{index}"},
            })
        registry = {
            "schema": "kosmic.workdirs/1",
            "project_id": "scope-demo",
            "sequence": len(entries),
            "directories": entries,
        }
        registry_path = self.project / ".kosmic" / "working-directories.json"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(json.dumps(registry, sort_keys=True), encoding="utf-8")
        commit_baseline(self.root, "fixture bound status and registered directories")
        self.write_record()
        generated = self.run_cli(
            "generate-status", "--project", self.project, "--work-record", WORK_RECORD)
        self.assertEqual(
            0, generated.returncode,
            msg=f"stdout:\n{generated.stdout}\nstderr:\n{generated.stderr}")
        self.assertTrue((self.root / "STATUS.md").is_file())
        for status_path, sentinel in foreign_status.items():
            self.assertEqual(sentinel, status_path.read_bytes())

        receipt = json.loads(self.finish().stdout)
        self.assertTrue((self.root / "STATUS.md").is_file())
        for status_path, sentinel in foreign_status.items():
            self.assertEqual(sentinel, status_path.read_bytes())
        stored = self.project / ".kosmic/work-receipts" / receipt_name(WORK_RECORD)
        receipt_bytes = stored.read_bytes()
        logs = sorted((self.project / "log").glob("*-work-completion.md"))
        self.assertEqual(len(logs), 1)
        rerun = json.loads(self.finish().stdout)
        self.assertEqual(rerun, receipt)
        for status_path, sentinel in foreign_status.items():
            self.assertEqual(sentinel, status_path.read_bytes())
        self.assertEqual(stored.read_bytes(), receipt_bytes)
        self.assertEqual(sorted((self.project / "log").glob("*-work-completion.md")), logs)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
