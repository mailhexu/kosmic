from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skills.scripts import kosmic_work
from skills.scripts.kosmic_work import WorkdirError
from tests.test_kosmic_navigation import build_two_feature_project


class WorkRecordProvenanceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-record-provenance-")
        self.addCleanup(self.tmp.cleanup)
        self.tree, self.root = build_two_feature_project(Path(self.tmp.name))
        epic = self.root / "subprojects/alpha/specs/epics/epic-001.md"
        epic.write_text(epic.read_text().replace('status: "done"', 'status: "approved"'))
        self.record = "nav/alpha/story/001"
    def test_managed_run_provenance_is_record_bound(self):
        payload = kosmic_work.record_run_provenance(self.root, self.record, self.tree)
        self.assertEqual(payload["project_id"], "nav")
        self.assertEqual(payload["governing_record"], self.record)
        self.assertEqual(payload["record_path"],
                         "subprojects/alpha/specs/stories/story-001.md")
        resolved = kosmic_work.authorize_run_record(self.root, self.tree, payload)
        self.assertEqual(resolved.qualified_id, self.record)

    def test_foreign_record_project_binding_is_rejected(self):
        payload = {"project_id": "foreign", "governing_record": self.record}
        with self.assertRaises(WorkdirError) as caught:
            kosmic_work.authorize_run_record(self.root, self.tree, payload)
        self.assertEqual(caught.exception.code, "RUN_IDENTITY_MISMATCH")


if __name__ == "__main__":
    unittest.main()
