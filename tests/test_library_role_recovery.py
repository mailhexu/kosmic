from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from tests import test_shared_library as fixture


CLI = Path(__file__).resolve().parents[1] / "skills/scripts/kosmic_project_skills.py"


class LegacyRoleRecoveryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = fixture.SharedLibraryTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.project = self.fixture.vault / "Projects/demo-proj"
        self.topic = self.fixture.skills / "kosmic/development/atomic-skill-publication.md"
        self.body = "\n# Atomic publication state\n\nOnly one complete tree is visible.\n"
        self.topic.write_text(
            "---\ntype: Skill Topic\nid: kosmic/development/atomic-skill-publication\n"
            "domain: kosmic\naudience: development\nstatus: stable\n"
            "summary: Atomic publication state\ntriggers: [publication state]\n"
            "aliases: []\nrequires: []\nevidence: []\nsource_project: demo-proj\n"
            "source_sha256: " + "0" * 64 + "\n---\n" + self.body,
            encoding="utf-8",
        )
        self.assignment = {
            "source": "kosmic/development/atomic-skill-publication.md",
            "target_id": "kosmic/development/atomic-skill-publication",
            "artifact_role": "knowledge",
            "requires_procedures": [],
            "governed_by": [],
            "uses_knowledge": [],
            "supported_by": [],
            "supersedes": [],
        }
        self.mapping = Path(self.fixture.temp.name) / "roles.json"

    def migrate(self, rows=None):
        self.mapping.write_text(json.dumps({
            "schema": "kosmic.semantic-role-classification/v1",
            "topics": [self.assignment] if rows is None else rows,
        }), encoding="utf-8")
        return subprocess.run([
            sys.executable, str(CLI), "migrate-library",
            "--vault", str(self.fixture.vault), "--project", str(self.project),
            "--assignments", str(self.mapping), "--work-record", self.fixture.work_record,
        ], capture_output=True, text=True)

    def resolve(self, intent):
        return subprocess.run([
            sys.executable, str(CLI), "resolve-library",
            "--vault", str(self.fixture.vault),
            "--route", "kosmic/development/atomic-skill-publication", "--role", "development",
            "--intent", intent,
        ], capture_output=True, text=True)

    def test_cross_project_recovery_requires_matching_explicit_provenance(self) -> None:
        self.topic.write_text(self.topic.read_text().replace(
            "source_project: demo-proj", "source_project: foreign-project"
        ))
        before = self.topic.read_bytes()
        rejected = self.migrate()
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(self.topic.read_bytes(), before)
        rejected = self.migrate([dict(self.assignment, source_project="wrong-project")])
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(self.topic.read_bytes(), before)
        accepted = self.migrate([dict(self.assignment, source_project="foreign-project")])
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertIn("source_project: foreign-project", self.topic.read_text())
        self.assertEqual(self.topic.read_text().split("---\n", 2)[2], self.body)

    def test_recovers_knowledge_without_making_it_executable(self) -> None:
        completed = self.migrate()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(self.topic.read_text().split("---\n", 2)[2], self.body)
        understood = self.resolve("understand")
        self.assertEqual(understood.returncode, 0, understood.stderr)
        topic = next(row for row in json.loads(understood.stdout)["topics"]
                     if row["id"] == "kosmic/development/atomic-skill-publication")
        self.assertEqual(topic["artifact_role"], "knowledge")
        execution = self.resolve("do")
        self.assertNotEqual(execution.returncode, 0)
        self.assertIn("NO_EXECUTABLE_MATCH", execution.stderr)

    def test_conflicting_or_incomplete_assignments_preserve_source(self) -> None:
        before = self.topic.read_bytes()
        incomplete = dict(self.assignment)
        del incomplete["uses_knowledge"]
        escaped = dict(self.assignment, source="../outside.md")
        mismatched = dict(self.assignment, target_id="kosmic/development/other")
        for row in (incomplete, escaped, mismatched):
            with self.subTest(row=row):
                completed = self.migrate([row])
                self.assertNotEqual(completed.returncode, 0)
                self.assertEqual(self.topic.read_bytes(), before)
        recovered = self.migrate()
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        before = self.topic.read_bytes()
        reclassified = dict(self.assignment, artifact_role="procedure", outcome="Publish")
        rejected = self.migrate([reclassified])
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(self.topic.read_bytes(), before)

    def test_unicode_crlf_body_is_preserved_byte_for_byte(self) -> None:
        header = self.topic.read_bytes().split(b"---\n", 2)[1]
        body = "\r\n# Publication α\r\n\r\nKeep π and every line ending.\r\n".encode("utf-8")
        self.topic.write_bytes(b"---\r\n" + header.replace(b"\n", b"\r\n") + b"---\r\n" + body)
        completed = self.migrate()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(self.topic.read_bytes().split(b"---\n", 2)[2], body)

    def test_later_assignment_failure_cannot_publish_an_earlier_topic(self) -> None:
        self.fixture.write_topic(
            "tb2j/development/debug-exchange", audience="development",
            artifact_role="procedure", source_project="demo-proj",
            body=self.fixture.procedure_body("Debug exchange."),
        )
        before = {p.relative_to(self.fixture.skills): p.read_bytes()
                  for p in self.fixture.skills.rglob("*") if p.is_file()}
        conflict = dict(
            self.assignment, source="tb2j/development/debug-exchange.md",
            target_id="tb2j/development/debug-exchange", artifact_role="knowledge",
        )
        completed = self.migrate([self.assignment, conflict])
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(
            {p.relative_to(self.fixture.skills): p.read_bytes()
             for p in self.fixture.skills.rglob("*") if p.is_file()}, before,
        )

    def test_in_scope_symlink_is_not_a_classification_source(self) -> None:
        target = self.topic.parent / "saved-source.md"
        self.topic.rename(target)
        self.topic.symlink_to(target.name)
        before = target.read_bytes()
        completed = self.migrate()
        self.assertNotEqual(completed.returncode, 0)
        self.assertTrue(self.topic.is_symlink())
        self.assertEqual(target.read_bytes(), before)

    def test_generated_output_symlink_cannot_modify_external_file(self) -> None:
        external = self.fixture.skills.parent / "external-catalog.json"
        external.write_bytes(b"external content must remain intact")
        generated = self.fixture.skills / ".kosmic/catalog.json"
        generated.parent.mkdir(exist_ok=True)
        generated.unlink(missing_ok=True)
        generated.symlink_to(external)
        before = self.topic.read_bytes()
        completed = self.migrate()
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(external.read_bytes(), b"external content must remain intact")
        self.assertEqual(self.topic.read_bytes(), before)
        self.assertTrue(generated.is_symlink())


if __name__ == "__main__":
    unittest.main()
