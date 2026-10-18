"""Story069: Project-root-only shared knowledge and owner write boundaries."""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from skills.scripts.kosmic_specs import (
    SHARED_ROOTS,
    SpecCatalog,
    SpecError,
    check_read_scope,
    check_write_scope,
    classify_write_scope,
    shared_root_conflicts,
    validate_project_specs,
    validate_shared_roots,
)


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


class SharedRootsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-shared-roots-")
        self.addCleanup(self.tmp.cleanup)
        self.root = project(Path(self.tmp.name) / "Project")
        feature(self.root, "left")
        feature(self.root, "right")
        (self.root / "notes").mkdir()
        document(self.root / "notes" / "shared-topic.md",
                 {"type": "concept", "status": "stable"}, "Shared Topic")

    def test_project_roots_alone_validate(self) -> None:
        validate_shared_roots(self.root)
        self.assertEqual(shared_root_conflicts(self.root), ())
        catalog = validate_project_specs(self.root)
        self.assertEqual(len(catalog.records), 8)

    def test_local_knowledge_copies_are_rejected(self) -> None:
        for name in SHARED_ROOTS:
            with self.subTest(root=name):
                target = self.root / "subprojects" / "left" / name
                target.mkdir()
                try:
                    with self.assertRaises(SpecError) as caught:
                        validate_shared_roots(self.root)
                    self.assertEqual(caught.exception.code, "SHARED_ROOT_INVALID")
                    with self.assertRaises(SpecError) as caught:
                        validate_project_specs(self.root)
                    self.assertEqual(caught.exception.code, "SHARED_ROOT_INVALID")
                finally:
                    for child in sorted(target.rglob("*"), reverse=True):
                        child.unlink()
                    target.rmdir()
                validate_shared_roots(self.root)

    def test_local_knowledge_symlinks_are_rejected(self) -> None:
        target = self.root / "subprojects" / "right" / "mathdocs"
        target.symlink_to(self.root / "notes")
        with self.assertRaises(SpecError) as caught:
            validate_shared_roots(self.root)
        self.assertEqual(caught.exception.code, "SHARED_ROOT_INVALID")
        self.assertIn("subprojects/right/mathdocs", caught.exception.detail)
        target.unlink()

    def test_non_knowledge_directories_stay_allowed(self) -> None:
        (self.root / "subprojects" / "left" / "build").mkdir()
        validate_shared_roots(self.root)

    def test_unsafe_subprojects_entries_fail_closed(self) -> None:
        entry = self.root / "subprojects" / "left"
        shadow = entry.rename(entry.with_name("left-real"))
        entry.symlink_to(shadow)
        try:
            with self.assertRaises(SpecError) as caught:
                shared_root_conflicts(self.root)
            self.assertEqual(caught.exception.code, "SCOPE_DENIED")
            with self.assertRaises(SpecError) as caught:
                validate_shared_roots(self.root)
            self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        finally:
            entry.unlink()
            shadow.rename(entry)
        validate_shared_roots(self.root)

    def test_non_directory_subprojects_entry_fails_closed(self) -> None:
        stray = self.root / "subprojects" / "stray.txt"
        stray.write_text("not a subproject\n", encoding="utf-8")
        try:
            with self.assertRaises(SpecError) as caught:
                validate_shared_roots(self.root)
            self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        finally:
            stray.unlink()
        validate_shared_roots(self.root)

    def test_symlinked_subprojects_root_fails_closed(self) -> None:
        directory = self.root / "subprojects"
        shadow = directory.rename(directory.with_name("subprojects-real"))
        directory.symlink_to(shadow)
        try:
            with self.assertRaises(SpecError) as caught:
                shared_root_conflicts(self.root)
            self.assertEqual(caught.exception.code, "SCOPE_DENIED")
            with self.assertRaises(SpecError) as caught:
                validate_shared_roots(self.root)
            self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        finally:
            directory.unlink()
            shadow.rename(directory)
        validate_shared_roots(self.root)


class WriteScopeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-write-scope-")
        self.addCleanup(self.tmp.cleanup)
        self.root = project(Path(self.tmp.name) / "Project")
        feature(self.root, "left")
        feature(self.root, "right")
        (self.root / "notes").mkdir()
        (self.root / "mathdocs").mkdir()
        (self.root / "skills").mkdir()

    def test_owner_writes_inside_own_scope_are_allowed(self) -> None:
        target = self.root / "subprojects" / "left" / "specs" / "stories" / "story-002.md"
        scope = classify_write_scope(self.root, target, owner="left")
        self.assertEqual((scope.boundary, scope.allowed), ("subproject", True))
        self.assertEqual(check_write_scope(self.root, target, owner="left").path, target)

    def test_owner_cannot_write_foreign_specs_or_shared_roots(self) -> None:
        for target in (self.root / "subprojects" / "right" / "specs" / "prd.md",
                       self.root / "notes" / "shared-topic.md",
                       self.root / "mathdocs" / "identity.md",
                       self.root / "skills" / "demo-usage" / "SKILL.md"):
            with self.subTest(target=target.relative_to(self.root).as_posix()):
                scope = classify_write_scope(self.root, target, owner="left")
                self.assertEqual(scope.boundary, "foreign" if "right" in scope.detail else "shared")
                self.assertFalse(scope.allowed)
                with self.assertRaises(SpecError) as caught:
                    check_write_scope(self.root, target, owner="left")
                self.assertEqual(caught.exception.code, "WRITE_SCOPE_DENIED")

    def test_project_authority_cannot_write_into_any_subproject(self) -> None:
        scope = classify_write_scope(self.root, self.root / "subprojects" / "left" / "specs" / "prd.md")
        self.assertEqual((scope.boundary, scope.allowed), ("foreign", False))
        with self.assertRaises(SpecError) as caught:
            check_write_scope(self.root, self.root / "subprojects" / "left" / "specs" / "prd.md")
        self.assertEqual(caught.exception.code, "WRITE_SCOPE_DENIED")

    def test_project_authority_writes_shared_roots(self) -> None:
        for target in (self.root / "notes" / "new-topic.md",
                       self.root / "specs" / "INDEX.md",
                       self.root / "mathdocs" / "identity.md"):
            scope = check_write_scope(self.root, target)
            self.assertEqual((scope.boundary, scope.allowed), ("shared", True))

    def test_unknown_owner_is_rejected(self) -> None:
        with self.assertRaises(SpecError) as caught:
            classify_write_scope(self.root, self.root / "notes" / "x.md", owner="ghost")
        self.assertEqual(caught.exception.code, "OWNER_MISMATCH")

    def test_symlink_escape_is_scope_denied(self) -> None:
        escape = self.root / "subprojects" / "left" / "escape"
        escape.symlink_to(self.root / "subprojects" / "right" / "specs")
        with self.assertRaises(SpecError) as caught:
            check_write_scope(self.root, escape / "prd.md", owner="left")
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        with self.assertRaises(SpecError) as caught:
            check_read_scope(self.root, escape / "prd.md")
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        escape.unlink()

    def test_outside_project_is_scope_denied(self) -> None:
        outside = Path(self.tmp.name) / "Elsewhere" / "prd.md"
        with self.assertRaises(SpecError) as caught:
            check_write_scope(self.root, outside, owner="left")
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")

    def test_cross_subproject_reads_are_allowed(self) -> None:
        foreign = self.root / "subprojects" / "right" / "specs" / "prd.md"
        self.assertEqual(check_read_scope(self.root, foreign), foreign)
        self.assertEqual(check_read_scope(self.root, self.root / "notes"), self.root / "notes")

    def test_leaf_symlink_is_rejected_for_write_and_read(self) -> None:
        leaf = self.root / "subprojects" / "left" / "specs" / "prd.md"
        backup = leaf.read_bytes()
        leaf.unlink()
        leaf.symlink_to(self.root / "subprojects" / "right" / "specs" / "prd.md")
        with self.assertRaises(SpecError) as caught:
            check_write_scope(self.root, leaf, owner="left")
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        with self.assertRaises(SpecError) as caught:
            check_read_scope(self.root, leaf)
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        leaf.unlink()
        leaf.write_bytes(backup)

    def test_special_file_leaf_is_rejected_for_write_and_read(self) -> None:
        fifo = self.root / "subprojects" / "right" / "specs" / "fifo"
        os.mkfifo(fifo)
        with self.assertRaises(SpecError) as caught:
            check_write_scope(self.root, fifo, owner="right")
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        with self.assertRaises(SpecError) as caught:
            check_read_scope(self.root, fifo)
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        fifo.unlink()

    def test_new_leaf_in_owner_scope_still_writeable(self) -> None:
        target = self.root / "subprojects" / "left" / "specs" / "stories" / "story-009.md"
        self.assertFalse(target.exists())
        check_write_scope(self.root, target, owner="left")


class OwnerHierarchyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-owner-hierarchy-")
        self.addCleanup(self.tmp.cleanup)
        self.root = project(Path(self.tmp.name) / "Project")
        feature(self.root, "left")
        feature(self.root, "right")

    def test_declared_cross_subproject_dependency_stays_read_only(self) -> None:
        story = self.root / "subprojects" / "right" / "specs" / "stories" / "story-001.md"
        text = story.read_text(encoding="utf-8")
        story.write_text(text.replace(
            "depends_on: []",
            'depends_on: ["demo/left/story/001"]\ncross_subproject_dependencies: ["demo/left/story/001"]',
        ), encoding="utf-8")
        catalog = validate_project_specs(self.root)
        right_story = catalog.resolve("demo/right/story/001")
        deps = catalog.dependencies(right_story)
        self.assertEqual([item.qualified_id for item in deps], ["demo/left/story/001"])
        # The dependency resolves for reading, but grants no write authority.
        with self.assertRaises(SpecError) as caught:
            check_write_scope(self.root, deps[0].path, owner="right")
        self.assertEqual(caught.exception.code, "WRITE_SCOPE_DENIED")

    def test_forged_owner_ancestry_is_rejected_by_hierarchy_validation(self) -> None:
        story = self.root / "subprojects" / "right" / "specs" / "stories" / "story-001.md"
        story.write_text(story.read_text(encoding="utf-8").replace(
            'linked_epic: "../epics/epic-001.md"',
            'linked_epic: "../../left/specs/epics/epic-001.md"',
        ), encoding="utf-8")
        with self.assertRaises(SpecError) as caught:
            validate_project_specs(self.root)
        self.assertEqual(caught.exception.code, "ANCESTRY_INVALID")

    def test_resolvable_foreign_parent_is_owner_rejected(self) -> None:
        story = self.root / "subprojects" / "right" / "specs" / "stories" / "story-001.md"
        story.write_text(story.read_text(encoding="utf-8").replace(
            'linked_epic: "../epics/epic-001.md"',
            'linked_epic: "../../../left/specs/epics/epic-001.md"',
        ), encoding="utf-8")
        with self.assertRaises(SpecError) as caught:
            validate_project_specs(self.root)
        self.assertEqual(caught.exception.code, "ANCESTRY_INVALID")
        self.assertIn("OWNER_MISMATCH: demo/left/epic/001", caught.exception.detail)


if __name__ == "__main__":
    unittest.main()
