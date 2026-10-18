from __future__ import annotations

import unittest

from skills.scripts.kosmic_migration import apply_migration
from skills.scripts.kosmic_shared_library import parse_document_text
from skills.scripts.kosmic_specs import SpecCatalog
from tests import test_kosmic_migration_apply as fixture
from tests.test_kosmic_specs import document, feature


class OwnerAncestryMigrationTest(unittest.TestCase):
    def test_owner_local_ancestry_wins_over_a_moving_project_root_namesake(self) -> None:
        case = fixture.MigrationApplyTest()
        case.setUp()
        self.addCleanup(case.doCleanups)
        root = case.root
        document(root / "specs/prd.md", {"status": "approved"}, "Root Feature")
        existing_specs = feature(root, "existing")
        owner_entry = existing_specs.parent / "SubprojectEntry.md"
        before = owner_entry.read_bytes()
        note = root / "notes/root-reference.md"
        note.write_text('---\ntitle: Root reference\nlinked_prd: "specs/prd-export.md"\n---\n')
        plan = case.plan()
        receipt = apply_migration(root, case.plan_path, plan["digest"], case.reference)
        self.assertEqual(receipt["status"], "successful")
        catalog = SpecCatalog(root)
        catalog.validate()
        self.assertEqual(owner_entry.read_bytes(), before)
        self.assertEqual(catalog.resolve("demo/existing/prd/prd").path,
                         existing_specs / "prd.md")
        metadata = parse_document_text(note.read_text(), note).metadata
        self.assertEqual((note.parent / metadata["linked_prd"]).resolve(),
                         root / "subprojects/export/specs/prd.md")


if __name__ == "__main__":
    unittest.main()
