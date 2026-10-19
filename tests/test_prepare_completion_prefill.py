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
"""

from __future__ import annotations

import hashlib
import json
import unittest

try:
    from tests.scoped_completion_support import ScopedProjectCase, write_document
except ImportError:  # direct test-directory execution
    from scoped_completion_support import ScopedProjectCase, write_document

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

    def project_snapshot(self) -> dict[str, str]:
        return {
            str(path.relative_to(self.project)):
                hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(self.project.rglob("*")) if path.is_file()
        }

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
