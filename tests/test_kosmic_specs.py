from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from skills.scripts.kosmic_specs import SpecCatalog, SpecError


def document(path: Path, metadata: dict, title: str = "Specification") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n" + "".join(f"{key}: {json.dumps(value)}\n" for key, value in metadata.items())
        + f"---\n\n# {title}\n", encoding="utf-8",
    )
    return path


def project(root: Path) -> Path:
    document(root / "ProjectEntry.md", {"project_id": "demo"}, "Demo")
    return root


def feature(root: Path, owner: str) -> Path:
    base = root / "subprojects" / owner
    document(base / "SubprojectEntry.md", {
        "schema": "kosmic.subproject/1", "project_id": "demo", "subproject_id": owner,
        "title": owner, "linked_prd": "specs/prd.md",
    })
    specs = base / "specs"
    common = {"project_id": "demo", "subproject_id": owner, "status": "approved"}
    document(specs / "prd.md", {**common, "record_kind": "prd", "local_id": "prd"})
    document(specs / "architecture.md", {
        **common, "record_kind": "architecture", "local_id": "architecture", "linked_prd": "prd.md",
    })
    document(specs / "epics" / "epic-001.md", {
        **common, "record_kind": "epic", "local_id": "001",
        "linked_architecture": "../architecture.md", "linked_prd": "../prd.md",
    })
    document(specs / "stories" / "story-001.md", {
        **common, "record_kind": "story", "local_id": "001", "depends_on": [],
        "linked_epic": "../epics/epic-001.md", "linked_architecture": "../architecture.md",
        "linked_prd": "../prd.md",
    })
    return specs


class SpecCatalogTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-specs-")
        self.addCleanup(self.tmp.cleanup)
        self.root = project(Path(self.tmp.name) / "Project")
        self.left = feature(self.root, "left")
        self.right = feature(self.root, "right")

    def test_repeated_local_ids_require_the_correct_owner(self) -> None:
        catalog = SpecCatalog(self.root)
        left = catalog.resolve("demo/left/story/001")
        right = catalog.resolve("demo/right/story/001")
        self.assertEqual(left.path, self.left / "stories" / "story-001.md")
        self.assertEqual(right.path, self.right / "stories" / "story-001.md")
        self.assertEqual(catalog.resolve("001", owner="left", kind="story"), left)
        self.assertEqual(left.qualified_id, "demo/left/story/001")
        with self.assertRaisesRegex(SpecError, "OWNER_REQUIRED"):
            catalog.resolve("001", kind="story")
        with self.assertRaisesRegex(SpecError, "OWNER_MISMATCH"):
            catalog.resolve("demo/right/story/001", owner="left")

    def test_foreign_parent_and_inconsistent_ancestry_are_rejected(self) -> None:
        catalog = SpecCatalog(self.root)
        catalog.validate()
        story = catalog.resolve("demo/left/story/001")
        document(story.path, {**story.metadata, "linked_epic": "demo/right/epic/001"})
        with self.assertRaisesRegex(SpecError, "ANCESTRY_INVALID"):
            SpecCatalog(self.root).validate()
        document(story.path, {**story.metadata, "linked_epic": "../epics/missing.md"})
        with self.assertRaisesRegex(SpecError, "ANCESTRY_INVALID"):
            SpecCatalog(self.root).validate()

    def test_foreign_dependencies_are_declared_and_cycles_fail(self) -> None:
        original = SpecCatalog(self.root).resolve("demo/left/story/001")
        foreign = "demo/right/story/001"
        document(original.path, {**original.metadata, "depends_on": [foreign]})
        with self.assertRaisesRegex(SpecError, "DEPENDENCY_INVALID"):
            SpecCatalog(self.root).validate()
        document(original.path, {**original.metadata, "depends_on": [foreign],
                                 "cross_subproject_dependencies": [foreign]})
        catalog = SpecCatalog(self.root)
        catalog.validate()
        current = catalog.resolve("demo/left/story/001")
        self.assertEqual([ref.qualified_id for ref in catalog.dependencies(current)], [foreign])
        other = catalog.resolve(foreign)
        document(other.path, {**other.metadata, "depends_on": [current.qualified_id],
                              "cross_subproject_dependencies": [current.qualified_id]})
        with self.assertRaisesRegex(SpecError, "DEPENDENCY_CYCLE"):
            SpecCatalog(self.root).validate()

    def test_spoofed_owner_and_symlink_escape_fail(self) -> None:
        story = SpecCatalog(self.root).resolve("demo/left/story/001")
        document(story.path, {**story.metadata, "subproject_id": "right"})
        with self.assertRaisesRegex(SpecError, "OWNER_MISMATCH"):
            SpecCatalog(self.root)
        document(story.path, story.metadata)
        catalog = SpecCatalog(self.root)
        outside = Path(self.tmp.name) / "outside.md"
        document(outside, story.metadata)
        with self.assertRaisesRegex(SpecError, "SCOPE_DENIED"):
            catalog.resolve(outside)
        story.path.unlink()
        story.path.symlink_to(outside)
        with self.assertRaisesRegex(SpecError, "SCOPE_DENIED"):
            SpecCatalog(self.root)

    def test_allocation_is_owner_local_and_shared_records_are_distinct(self) -> None:
        common = {"project_id": "demo", "subproject_id": None, "status": "approved"}
        shared = document(self.root / "specs" / "quick-tasks" / "repair.md",
                          {**common, "record_kind": "quick-task", "local_id": "repair"})
        proposal = document(self.root / "specs" / "skill-proposals" / "proposal.md",
                            {**common, "record_kind": "proposal", "local_id": "repair"})
        catalog = SpecCatalog(self.root)
        self.assertEqual(catalog.resolve("demo/quick-task/repair").path, shared)
        self.assertEqual(catalog.resolve("demo/proposal/repair").path, proposal)
        self.assertEqual(catalog.next_local_id("story", "left"), "002")
        document(self.left / "stories" / "story-009.md",
                 {**catalog.resolve("demo/left/story/001").metadata, "local_id": "009"})
        newer = SpecCatalog(self.root)
        self.assertEqual(newer.next_local_id("story", "left"), "010")
        self.assertEqual(newer.next_local_id("story", "right"), "002")
        self.assertEqual([ref.qualified_id for ref in newer.records],
                         [ref.qualified_id for ref in SpecCatalog(self.root).records])

    def test_ambiguous_local_references_require_kind(self) -> None:
        with self.assertRaisesRegex(SpecError, "REFERENCE_AMBIGUOUS"):
            SpecCatalog(self.root).resolve("001", owner="left")
        common = {"project_id": "demo", "subproject_id": None, "status": "approved"}
        for kind, folder in (("quick-task", "quick-tasks"), ("proposal", "skill-proposals")):
            document(self.root / "specs" / folder / "repair.md",
                     {**common, "record_kind": kind, "local_id": "repair"})
        catalog = SpecCatalog(self.root)
        with self.assertRaisesRegex(SpecError, "REFERENCE_AMBIGUOUS"):
            catalog.resolve("repair")
        self.assertEqual(catalog.resolve("repair", kind="quick-task").kind, "quick-task")

    def test_occupied_numeric_filename_cannot_spoof_another_id(self) -> None:
        original = self.left / "stories" / "story-001.md"
        original.rename(self.left / "stories" / "story-002.md")
        with self.assertRaisesRegex(SpecError, "LOCAL_ID_INVALID"):
            SpecCatalog(self.root).next_local_id("story", "left")

    def test_record_objects_cannot_bypass_catalog_ownership(self) -> None:
        from dataclasses import replace

        catalog = SpecCatalog(self.root)
        record = catalog.resolve("demo/left/story/001")
        forged = replace(record, project_id="foreign", subproject_id="right",
                         kind="quick-task", metadata={})
        for action in (catalog.ancestry, catalog.dependencies):
            with self.assertRaisesRegex(SpecError, "OWNER_MISMATCH"):
                action(forged)
        with self.assertRaises(TypeError):
            record.metadata["subproject_id"] = "right"
        self.assertEqual([parent.subproject_id for parent in catalog.ancestry(record)],
                         ["left", "left", "left"])
