"""Read-only ``work prepare-completion`` regressions (Story 002, ADR-D/FR-005).

Driven only through the public CLI, never source text or imports:

- AC1 canonical order with exact verbatim criterion text, record identity
  and canonical record path, exact JSON payload keys (no outcome, reviewer,
  or approval field).
- AC2 authored entries preserved field-for-field including adverse findings
  and extra authored fields; criteria without an authored entry come back
  as blank ``observation``/``source`` drafts that ``work finish`` still
  rejects.
- AC3 wrong status, terminal records, and unknown record references are
  refused with the existing authorization error codes.
- AC4 missing criteria, duplicated criterion text, and unknown, repeated,
  or structurally malformed authored mappings are each refused; an absent
  authored entry is a blank draft, never a mapping error.
- AC5 a successful prepare provably writes nothing: before/after byte
  snapshots over the whole Project stay identical.

Story 003 adds the explicit-writer path: ``--worktree`` returns top-level
``source_revision`` bound to the writer's real source while the default
no-writer payload stays unchanged.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.scoped_completion_support import (
        CLI,
        ScopedProjectCase,
        commit_baseline,
        write_document,
    )
except ImportError:  # direct test-directory execution
    from scoped_completion_support import (
        CLI,
        ScopedProjectCase,
        commit_baseline,
        write_document,
    )

WORK_RECORD = "scope-demo/quick-task/fixture-task"
RECORD_RELATIVE = "specs/quick-tasks/fixture-task.md"
SOURCE = "tests/test_prepare_completion_prefill.py::PrepareCompletionPrefillTest"

CRITERIA = (
    "Canonical criteria are listed in record order",
    "Authored adverse findings survive field-for-field",
    "Criteria without an authored entry yield blank drafts",
)

NORMAL_ENTRY = {
    "criterion": CRITERIA[0],
    "observation": "The CLI listed every criterion in record order.",
    "source": SOURCE,
}

ADVERSE_ENTRY = {
    "criterion": CRITERIA[1],
    "observation": "Adverse finding: the first smoke run failed before the fix.",
    "source": SOURCE,
    "severity": "adverse",
}


class PrepareCompletionPrefillTest(ScopedProjectCase):
    """Story 002: read-only criterion prefill over an authorized record."""

    def setUp(self):
        super().setUp()
        self.record_path = self.project / RECORD_RELATIVE
        self.write_record()

    def write_record(self, *, criteria=CRITERIA, observations=None, fields=None,
                     body=None):
        entries = [NORMAL_ENTRY, ADVERSE_ENTRY] if observations is None else observations
        values = {
            "project_id": "scope-demo",
            "subproject_id": None,
            "record_kind": "quick-task",
            "local_id": "fixture-task",
            "status": "approved",
            "consumer_interface_change": False,
            "completion_observations": entries,
        }
        values.update(fields or {})
        if body is None:
            body = ("## Acceptance Criteria\n\n"
                    + "".join(f"- [ ] {criterion}\n" for criterion in criteria))
        write_document(self.record_path, values, "Fixture", body)

    def prepare(self):
        return self.run_cli(
            "work", "prepare-completion",
            "--project", self.project,
            "--work-record", WORK_RECORD,
        )

    def refusal(self, code, **overrides):
        self.write_record(**overrides)
        result = self.prepare()
        self.assertEqual(
            2,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn(code, result.stderr)
        return result

    def snapshot(self, root) -> dict[str, str]:
        return {
            str(path.relative_to(root)):
                hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(root.rglob("*")) if path.is_file()
        }

    def project_snapshot(self) -> dict[str, str]:
        return self.snapshot(self.project)

    def test_prepare_completion_lists_exact_criteria_with_authored_entries(self) -> None:
        result = self.prepare()
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(
            {"identity", "record_path", "completion_observations"},
            set(payload),
        )
        self.assertEqual(WORK_RECORD, payload["identity"])
        self.assertEqual(RECORD_RELATIVE, payload["record_path"])
        self.assertEqual(
            [
                NORMAL_ENTRY,
                ADVERSE_ENTRY,
                {"criterion": CRITERIA[2], "observation": "", "source": ""},
            ],
            payload["completion_observations"],
        )

    def test_prepare_completion_with_explicit_worktree_binds_real_source(self) -> None:
        """Story 003: ``--worktree`` adds only top-level ``source_revision``,
        bound to the independent writer's real changed source, while the
        no-writer invocation keeps the exact existing payload."""
        writer = self.root / "external-writer"
        (writer / "src").mkdir(parents=True)
        (writer / "src/engine.py").write_text("VALUE = 1\n")
        subprocess.run(["git", "init", "-q", str(writer)], check=True,
                       capture_output=True)
        head = commit_baseline(writer)
        (writer / "src/engine.py").write_text("VALUE = 2\n")
        (writer / "src/notes.txt").write_text("untracked\n")

        def prepare_with_writer():
            return self.run_cli(
                "work", "prepare-completion",
                "--project", self.project,
                "--work-record", WORK_RECORD,
                "--worktree", writer,
            )

        result = prepare_with_writer()
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        payload = json.loads(result.stdout)
        self.assertEqual(
            {"identity", "record_path", "completion_observations", "source_revision"},
            set(payload),
        )
        self.assertEqual(
            [
                NORMAL_ENTRY,
                ADVERSE_ENTRY,
                {"criterion": CRITERIA[2], "observation": "", "source": ""},
            ],
            payload["completion_observations"],
        )
        revision = payload["source_revision"]
        self.assertRegex(revision, r"^[0-9a-f]{64}$")
        self.assertNotEqual(head, revision)
        (writer / "src/late.txt").write_text("changed after the first digest\n")
        rerun = json.loads(prepare_with_writer().stdout)
        self.assertNotEqual(revision, rerun["source_revision"])

        default = json.loads(self.prepare().stdout)
        self.assertEqual(
            {"identity", "record_path", "completion_observations"},
            set(default),
        )
        self.assertEqual(
            payload["completion_observations"],
            default["completion_observations"],
        )

    def test_prepare_completion_same_root_exclusions_match_existing_algorithm(self) -> None:
        """Story 003: same-root preparation excludes Project metadata exactly
        as the unchanged algorithm dictates; real staged, deleted and
        untracked source changes each move the digest."""
        subprocess.run(["git", "init", "-q", str(self.project)], check=True,
                       capture_output=True)
        (self.project / "src").mkdir()
        (self.project / "src/tool.py").write_text("VALUE = 1\n")
        (self.project / "src/gone.py").write_text("GONE = 1\n")
        commit_baseline(self.project)

        def prepared_revision() -> str:
            result = self.run_cli(
                "work", "prepare-completion",
                "--project", self.project,
                "--work-record", WORK_RECORD,
                "--worktree", self.project,
            )
            self.assertEqual(
                0,
                result.returncode,
                msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )
            return json.loads(result.stdout)["source_revision"]

        revision = prepared_revision()
        # Excluded Project metadata: the record bytes themselves, sibling
        # Project metadata directories, STATUS and .tmp scratch.
        self.write_record(
            body="## Acceptance Criteria\n\n"
                 + "".join(f"- [ ] {criterion}\n" for criterion in CRITERIA)
                 + "\nExtra recorded context that only changes record bytes.\n")
        (self.project / "STATUS.md").write_text("# STATUS\n")
        (self.project / "log").mkdir()
        (self.project / "log/note.md").write_text("log\n")
        (self.project / "evidence").mkdir()
        (self.project / "evidence/finding.txt").write_text("evidence\n")
        (self.project / ".tmp/kosmic/scratch").mkdir(parents=True)
        (self.project / ".tmp/kosmic/scratch/disposable.txt").write_text("tmp\n")
        self.assertEqual(revision, prepared_revision())
        # A staged modification of real source changes the digest.
        (self.project / "src/tool.py").write_text("VALUE = 2\n")
        subprocess.run(["git", "add", "src/tool.py"], cwd=str(self.project),
                       check=True, capture_output=True)
        staged = prepared_revision()
        self.assertNotEqual(revision, staged)
        # A tracked deletion contributes its deletion marker.
        (self.project / "src/gone.py").unlink()
        deleted = prepared_revision()
        self.assertNotEqual(staged, deleted)
        # Untracked source counts too.
        (self.project / "src/added.txt").write_text("added\n")
        self.assertNotEqual(deleted, prepared_revision())

    def test_prepare_completion_nested_project_prefix_is_excluded(self) -> None:
        """Story 003: with the Project nested in the writer, every path under
        the Project prefix is excluded — including Project-local source —
        while writer-level source outside the Project moves the digest."""
        commit_baseline(self.root)

        def prepared_revision() -> str:
            result = self.run_cli(
                "work", "prepare-completion",
                "--project", self.project,
                "--work-record", WORK_RECORD,
                "--worktree", self.root,
            )
            self.assertEqual(
                0,
                result.returncode,
                msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
            )
            return json.loads(result.stdout)["source_revision"]

        revision = prepared_revision()
        nested_source = self.project / "src/tool.py"
        nested_source.parent.mkdir(parents=True)
        nested_source.write_text("LOCAL = 1\n")
        self.assertEqual(revision, prepared_revision())
        (self.root / "src").mkdir()
        (self.root / "src/engine.py").write_text("VALUE = 1\n")
        with_source = prepared_revision()
        self.assertNotEqual(revision, with_source)
        (self.root / ".gitignore").unlink()
        self.assertNotEqual(with_source, prepared_revision())

    def test_prepare_completion_with_worktree_writes_nothing_on_success_or_refusal(self) -> None:
        """Story 003: explicit-writer preparation is read-only — Project and
        writer bytes survive both success and an authorization refusal."""
        writer = self.root / "external-writer"
        (writer / "src").mkdir(parents=True)
        (writer / "src/engine.py").write_text("VALUE = 1\n")
        subprocess.run(["git", "init", "-q", str(writer)], check=True,
                       capture_output=True)
        commit_baseline(writer)
        (writer / "src/engine.py").write_text("VALUE = 2\n")
        arguments = (
            "work", "prepare-completion",
            "--project", self.project,
            "--work-record", WORK_RECORD,
            "--worktree", writer,
        )
        before = (self.project_snapshot(), self.snapshot(writer))
        success = self.run_cli(*arguments)
        self.assertEqual(
            0,
            success.returncode,
            msg=f"stdout:\n{success.stdout}\nstderr:\n{success.stderr}",
        )
        self.assertEqual(before, (self.project_snapshot(), self.snapshot(writer)))
        self.write_record(fields={"status": "done"})
        refused_before = (self.project_snapshot(), self.snapshot(writer))
        refused = self.run_cli(*arguments)
        self.assertEqual(
            2,
            refused.returncode,
            msg=f"stdout:\n{refused.stdout}\nstderr:\n{refused.stderr}",
        )
        self.assertIn("WORK_PHASE_DENIED", refused.stderr)
        self.assertEqual(refused_before,
                         (self.project_snapshot(), self.snapshot(writer)))

    def test_prepare_completion_reports_invalid_writer_with_existing_diagnostic(self) -> None:
        with tempfile.TemporaryDirectory() as outside:
            invalid = Path(outside) / "not-a-git-worktree"
            invalid.mkdir()
            before = self.project_snapshot()
            result = subprocess.run(
                [sys.executable, str(CLI), "work", "prepare-completion",
                 "--project", str(self.project), "--work-record", WORK_RECORD,
                 "--worktree", str(invalid)],
                capture_output=True, text=True,
                env={**os.environ, "GIT_CEILING_DIRECTORIES": outside})
            self.assertEqual(2, result.returncode)
            self.assertIn("WORKTREE_INVALID", result.stderr)
            self.assertNotIn("Traceback", result.stderr)
            self.assertEqual(before, self.project_snapshot())

    def test_prepare_completion_refuses_unauthorized_records(self) -> None:
        self.refusal("WORK_PHASE_DENIED", fields={"status": "done"})
        self.refusal("WORK_PHASE_DENIED", fields={"status": "draft"})
        result = self.run_cli(
            "work", "prepare-completion",
            "--project", self.project,
            "--work-record", "scope-demo/quick-task/absent-task",
        )
        self.assertEqual(
            2,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("RECORD_INVALID", result.stderr)

    def test_prepare_completion_rejects_criteria_and_mapping_defects(self) -> None:
        self.refusal("ACCEPTANCE_INVALID", body="# Fixture\n\nNo criteria section.\n")
        self.refusal("ACCEPTANCE_INVALID",
                     criteria=("Repeated criterion text", "Repeated criterion text"))
        self.refusal("ACCEPTANCE_INVALID",
                     observations=[NORMAL_ENTRY,
                                   {"criterion": "Not a criterion",
                                    "observation": "drift", "source": SOURCE}])
        self.refusal("ACCEPTANCE_INVALID",
                     observations=[NORMAL_ENTRY, dict(NORMAL_ENTRY)])
        self.refusal("ACCEPTANCE_INVALID", observations=["not-a-mapping"])
        self.refusal("ACCEPTANCE_INVALID",
                     observations=[{"criterion": 7, "observation": "x", "source": "y"}])
        self.refusal("ACCEPTANCE_INVALID", fields={"completion_observations": "oops"})

    def test_prepare_completion_refuses_non_text_observation_or_source(self) -> None:
        for field, value in (("observation", ["run", "failed"]),
                             ("observation", {"detail": "interrupted"}),
                             ("observation", 7),
                             ("observation", None),
                             ("source", ["records", "smoke"]),
                             ("source", {"path": "x"}),
                             ("source", 3),
                             ("source", None)):
            entry = dict(NORMAL_ENTRY)
            entry[field] = value
            self.refusal("ACCEPTANCE_INVALID", observations=[entry])
        self.refusal("ACCEPTANCE_INVALID",
                     observations=[{"criterion": CRITERIA[0], "source": SOURCE}])
        self.refusal("ACCEPTANCE_INVALID",
                     observations=[{"criterion": CRITERIA[0], "observation": "text"}])
        self.write_record(observations=[
            {"criterion": CRITERIA[0], "observation": "", "source": ""},
            ADVERSE_ENTRY,
        ])
        result = self.prepare()
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertEqual(
            {"criterion": CRITERIA[0], "observation": "", "source": ""},
            json.loads(result.stdout)["completion_observations"][0],
        )

    def test_prepare_completion_reports_absent_entries_as_blank_drafts(self) -> None:
        self.write_record(observations=[])
        payload = json.loads(self.prepare().stdout)
        self.assertEqual(
            [{"criterion": criterion, "observation": "", "source": ""}
             for criterion in CRITERIA],
            payload["completion_observations"],
        )

    def test_prepare_completion_writes_nothing(self) -> None:
        before = self.project_snapshot()
        result = self.prepare()
        self.assertEqual(
            0,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertEqual(before, self.project_snapshot())

    def test_finish_still_rejects_the_prefilled_incomplete_draft(self) -> None:
        self.write_record(observations=[])
        result = self.run_cli(
            "work", "finish",
            "--project", self.project,
            "--worktree", self.root,
            "--work-record", WORK_RECORD,
            "--scope", "project:specs/",
        )
        self.assertEqual(
            2,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        self.assertIn("ACCEPTANCE_INVALID", result.stderr)
        self.assertFalse((self.project / ".kosmic/work-receipts").exists())


if __name__ == "__main__":
    unittest.main()
