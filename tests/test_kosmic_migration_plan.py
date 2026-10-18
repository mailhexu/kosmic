from __future__ import annotations

import hashlib
import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from skills.scripts import kosmic_specs
from skills.scripts.kosmic_specs import (
    SpecCatalog,
    SpecError,
    migration_plan,
    validate_migration_links,
)
from tests.test_kosmic_specs import document, project


def apply_plan(root: Path, plan: dict) -> None:
    """Stage outputs, delete obsolete paths: the parent executor contract."""
    for item in plan["outputs"]:
        target = root / item["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(item["content"], encoding="utf-8")
    for item in plan["deletions"]:
        (root / item["path"]).unlink()



class MigrationPlanTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-migration-plan-")
        self.addCleanup(self.tmp.cleanup)
        self.root = project(Path(self.tmp.name) / "Project")
        self.specs = self.root / "specs"
        (self.root / "notes").mkdir()
        (self.root / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        document(self.specs / "prd-export.md", {"status": "approved"}, "Export")
        document(self.specs / "architecture-export.md", {
            "status": "approved", "linked_prd": "prd-export.md",
        }, "Export Architecture")
        document(self.specs / "epics" / "epic-009-export.md", {
            "status": "approved", "linked_prd": "../prd-export.md",
            "linked_architecture": "../architecture-export.md",
        }, "Epic 9: Export")
        document(self.specs / "stories" / "story-031-export.md", {
            "status": "approved", "linked_prd": "../prd-export.md",
            "linked_architecture": "../architecture-export.md",
            "linked_epic": "../epics/epic-009-export.md", "depends_on": [],
        }, "Story 31: Export")
        document(self.specs / "quick-tasks" / "migrate.md", {
            "status": "approved", "consumer_interface_change": False,
        }, "Migrate")

    def test_explicit_target_only_research_is_rebased_and_pinned_without_writes(self) -> None:
        target = self.root / "research/showcase notes.md"
        target.parent.mkdir()
        original = b'# Showcase\n\n[Historical reference](../specs/not-a-record.md)\n'
        target.write_bytes(original)
        for source, reference in (
            (self.specs / "prd-export.md", "../research/showcase%20notes.md"),
            (self.specs / "epics/epic-009-export.md", "../../research/showcase%20notes.md"),
        ):
            source.write_text(source.read_text() + f'\n[Showcase]({reference}?mode=raw#diagram "Showcase title")\n')
        plan = migration_plan(self.root)
        self.assertEqual(plan["inputs"]["research/showcase notes.md"], hashlib.sha256(original).hexdigest())
        self.assertNotIn("research/showcase notes.md", {row["path"] for row in plan["outputs"]})
        self.assertNotIn("research/showcase notes.md", {row["path"] for row in plan["deletions"]})
        self.assertFalse(any(row["record"] == "research/showcase notes.md" for row in plan["link_problems"]))
        apply_plan(self.root, plan)
        for source in (
            self.root / "subprojects/export/specs/prd.md",
            self.root / "subprojects/export/specs/epics/epic-001-export.md",
        ):
            link = re.search(r'\[Showcase\]\((\S+) "Showcase title"\)', source.read_text())
            self.assertIsNotNone(link, source)
            parsed = urlsplit(link.group(1))
            self.assertEqual((source.parent / unquote(parsed.path)).resolve(), target)
            self.assertEqual((parsed.query, parsed.fragment), ("mode=raw", "diagram"))
        self.assertEqual(target.read_bytes(), original)

    def test_target_only_research_drift_changes_digest_without_enabling_filename_repair(self) -> None:
        target = self.root / "research/showcase.md"
        target.parent.mkdir()
        target.write_text("# Original\n")
        source = self.specs / "prd-export.md"
        source.write_text(source.read_text() + "\n[Valid](../research/showcase.md)\n[Broken](../missing/showcase.md)\n")
        first = migration_plan(self.root)
        broken = next(row for row in first["link_problems"] if row["reference"] == "../missing/showcase.md")
        self.assertEqual(broken["candidates"], [])
        self.assertEqual(broken["reason"], "unresolved-link")
        target.write_text("# Changed\n")
        second = migration_plan(self.root)
        self.assertNotEqual(first["digest"], second["digest"])
        self.assertNotEqual(first["inputs"]["research/showcase.md"], second["inputs"]["research/showcase.md"])

    def test_explicit_target_only_research_rejects_symlink_file_and_parent(self) -> None:
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (outside / "showcase.md").write_text("# Outside\n")
        source = self.specs / "prd-export.md"
        source.write_text(source.read_text() + "\n[Showcase](../research/showcase.md)\n")
        research = self.root / "research"
        research.mkdir()
        target = research / "showcase.md"
        target.symlink_to(outside / "showcase.md")
        with self.assertRaises(SpecError) as failure:
            migration_plan(self.root)
        self.assertEqual(failure.exception.code, "SCOPE_DENIED")
        target.unlink()
        research.rmdir()
        research.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(SpecError) as failure:
            migration_plan(self.root)
        self.assertEqual(failure.exception.code, "SCOPE_DENIED")

    def test_linked_metadata_prefers_existing_owner_local_target_only_research(self) -> None:
        from tests.test_kosmic_specs import feature
        feature(self.root, "existing")
        owner = self.root / "subprojects/existing"
        entry = owner / "SubprojectEntry.md"
        document(entry, {
            "schema": "kosmic.subproject/1", "project_id": "demo",
            "subproject_id": "existing", "title": "Existing",
            "linked_prd": "specs/prd.md", "linked_research": "research/showcase.md",
        })
        local = owner / "research/showcase.md"
        local.parent.mkdir()
        local.write_text("# Local research\n")
        namesake = self.root / "research/showcase.md"
        namesake.parent.mkdir()
        namesake.write_text("# Different Project-root research\n")
        before = entry.read_bytes()
        plan = migration_plan(self.root)
        self.assertIn("subprojects/existing/research/showcase.md", plan["inputs"])
        self.assertNotIn("research/showcase.md", plan["inputs"])
        apply_plan(self.root, plan)
        self.assertEqual(entry.read_bytes(), before)
        self.assertEqual((entry.parent / "research/showcase.md").read_text(), "# Local research\n")

    def test_moving_target_only_wikilink_rebases_without_changing_staying_wikilink(self) -> None:
        target = self.root / "research/showcase.md"
        target.parent.mkdir()
        target.write_text("# Research\n")
        link = "[[../research/showcase.md#section\\|Showcase]]"
        source = self.specs / "prd-export.md"
        source.write_text(source.read_text() + f"\n{link}\n")
        staying = self.root / "notes/reference.md"
        staying.write_text(f"# Reference\n\n{link}\n")
        before = staying.read_bytes()
        plan = migration_plan(self.root)
        apply_plan(self.root, plan)
        moved = self.root / "subprojects/export/specs/prd.md"
        self.assertIn("[[research/showcase.md#section\\|Showcase]]", moved.read_text())
        self.assertNotIn(link, moved.read_text())
        self.assertEqual(staying.read_bytes(), before)
        self.assertEqual(target.read_text(), "# Research\n")

    def test_parent_links_produce_pinned_local_owners_without_writing(self) -> None:
        before = {p.relative_to(self.root).as_posix(): p.read_bytes()
                  for p in self.root.rglob("*") if p.is_file()}
        plan = migration_plan(self.root, work_record="specs/quick-tasks/migrate.md")
        self.assertEqual(plan["ambiguities"], [])
        moved = {row["source"]: row for row in plan["records"]}
        self.assertEqual(moved["specs/prd-export.md"]["destination"],
                         "subprojects/export/specs/prd.md")
        story = moved["specs/stories/story-031-export.md"]
        self.assertEqual(story["subproject_id"], "export")
        self.assertEqual(story["qualified_id"], "demo/export/story/001")
        self.assertEqual(story["before_sha256"],
                         hashlib.sha256(before[story["source"]]).hexdigest())
        self.assertIn("specs/quick-tasks/migrate.md", plan["shared_records"])
        self.assertEqual(before, {p.relative_to(self.root).as_posix(): p.read_bytes()
                                  for p in self.root.rglob("*") if p.is_file()})
        self.assertEqual(plan["digest"],
                         migration_plan(self.root, work_record="specs/quick-tasks/migrate.md")["digest"])

    def test_same_titles_reserve_distinct_plan_owners_and_orphans_are_explicit(self) -> None:
        document(self.specs / "prd-second.md", {"status": "approved"}, "Export")
        orphan = document(self.specs / "research" / "orphan.md", {"status": "draft"}, "Orphan")
        plan = migration_plan(self.root)
        owners = {row["subproject_id"] for row in plan["records"] if row["kind"] == "prd"}
        self.assertEqual(owners, {"export", "export-2"})
        self.assertIn("specs/research/orphan.md", {row["record"] for row in plan["ambiguities"]})
        assigned = migration_plan(self.root, assignments={"specs/research/orphan.md": "specs/prd-export.md"})
        self.assertEqual(assigned["ambiguities"], [])
        row = next(row for row in assigned["records"] if row["source"] == orphan.relative_to(self.root).as_posix())
        self.assertEqual(row["subproject_id"], "export")

    def test_foreign_dependency_is_qualified_and_plan_is_pinned(self) -> None:
        document(self.specs / "prd-second.md", {"status": "approved"}, "Second")
        document(self.specs / "stories" / "story-001-second.md", {
            "status": "approved", "linked_prd": "../prd-second.md",
            "depends_on": ["../stories/story-031-export.md"],
        }, "Second Story")
        plan = migration_plan(self.root, work_record="specs/quick-tasks/migrate.md")
        second = next(row for row in plan["records"]
                      if row["source"] == "specs/stories/story-001-second.md")
        rewrite = next(row for row in plan["rewrites"] if row["source"] == second["source"])
        self.assertIn('depends_on: ["demo/export/story/001"]', rewrite["content"])
        self.assertIn('cross_subproject_dependencies: ["demo/export/story/001"]', rewrite["content"])
        self.assertEqual(plan["work_record_before_sha256"],
                         hashlib.sha256((self.specs / "quick-tasks" / "migrate.md").read_bytes()).hexdigest())
        self.assertIn("STATUS.md regeneration at the bound working directory", plan["expected_outputs"])
        self.assertEqual(plan["adapter_outputs"]["approval"], "required")

    def test_mechanical_fingerprint_mapping_is_classified_not_approved(self) -> None:
        document(self.specs / "skill-proposals" / "2026-10-01-bridge.md", {
            "status": "draft", "result": "create", "scope": "project-knowledge",
            "target": "notes/bridge.md", "related_notes": ["notes/bridge.md"],
            "evidence_packs": [], "decision": "pending", "fingerprint": "",
        }, "Bridge")
        plan = migration_plan(
            self.root,
            work_record="specs/quick-tasks/migrate.md",
            fingerprint_fn=lambda result, scope, target, artifact_role, related,
                evidence, body, routine_fields: "computed",
        )
        proposal = next(row for row in plan["rewrites"]
                        if row["source"].endswith("2026-10-01-bridge.md"))
        self.assertEqual(proposal["fingerprint_before"], "computed")
        self.assertEqual(proposal["fingerprint_after"], "computed")
        self.assertEqual(proposal["classification"], "mechanical-path-mapping")
        self.assertIn("evidence_inventory", plan)

    def test_changed_inputs_invalidate_the_plan(self) -> None:
        import unittest.mock

        real = kosmic_specs._read_bytes
        seen: dict[tuple, int] = {}

        def drifting(root, parts):
            data = real(root, parts)
            if "prd-export" in "/".join(parts):
                seen[tuple(parts)] = seen.get(tuple(parts), 0) + 1
                if seen[tuple(parts)] > 1:
                    return data + b"\n"
            return data

        with unittest.mock.patch.object(kosmic_specs, "_read_bytes", drifting):
            with self.assertRaisesRegex(SpecError, "MIGRATION_INPUT_DRIFT"):
                migration_plan(self.root)

    def test_planned_ancestors_resolve_inside_the_new_owner(self) -> None:
        from skills.scripts.kosmic_shared_library import parse_document_text

        plan = migration_plan(self.root, work_record="specs/quick-tasks/migrate.md")
        story = next(row for row in plan["records"] if row["kind"] == "story")
        rewrite = next(row for row in plan["rewrites"] if row["source"] == story["source"])
        metadata = parse_document_text(rewrite["content"], Path(story["destination"])).metadata
        self.assertEqual(metadata["subproject_id"], "export")
        self.assertEqual(metadata["status"], "approved")
        for key, kind in (("linked_prd", "prd"), ("linked_epic", "epic"), ("linked_architecture", "architecture")):
            parent = next(row for row in plan["records"] if row["kind"] == kind)
            target = (self.root / Path(story["destination"]).parent / metadata[key]).resolve()
            self.assertEqual(target, self.root / parent["destination"])

    def test_plan_two_carries_complete_inventory_outputs_and_deletions(self) -> None:
        note = document(self.root / "notes" / "linked.md", {"note_kind": "x"}, "Linked")
        with (self.root / "notes" / "linked.md").open("a", encoding="utf-8") as stream:
            stream.write("\nSee [Export](../specs/prd-export.md) and ![chart](../specs/../assets/a.png)\n")
        plan = migration_plan(self.root, work_record="specs/quick-tasks/migrate.md")
        self.assertEqual(plan["schema"], "kosmic.subproject-migration-plan/2")
        self.assertEqual(plan["existing_subprojects"], [])
        self.assertIn("ProjectEntry.md", plan["inputs"])
        self.assertIn("specs/quick-tasks/migrate.md", plan["inputs"])
        self.assertIn("notes/linked.md", plan["inputs"])
        self.assertIn("specs/prd-export.md", plan["inputs"])
        self.assertIn("specs", plan["directories"])
        output_paths = {item["path"] for item in plan["outputs"]}
        self.assertIn("subprojects/export/SubprojectEntry.md", output_paths)
        self.assertIn("subprojects/export/specs/INDEX.md", output_paths)
        self.assertIn("specs/quick-tasks/migrate.md", output_paths)  # shared canonicalized in place
        self.assertEqual({item["path"] for item in plan["deletions"]},
                         {row["source"] for row in plan["records"]})
        for item in plan["deletions"]:
            self.assertEqual(item["before_sha256"],
                             hashlib.sha256((self.root / item["path"]).read_bytes()).hexdigest())
        for item in plan["outputs"]:
            self.assertEqual(item["after_sha256"],
                             hashlib.sha256(item["content"].encode("utf-8")).hexdigest())
        self.assertTrue(all(item["path"] and not item["path"].startswith("/")
                            for item in plan["outputs"] + plan["deletions"]))

    def test_live_links_rewrite_inline_image_reference_and_skip_code(self) -> None:
        story = document(self.specs / "stories" / "story-031-export.md", {
            "status": "approved", "linked_prd": "../prd-export.md",
            "linked_architecture": "../architecture-export.md",
            "linked_epic": "../epics/epic-009-export.md", "depends_on": [],
            "related_notes": ["../../notes/linked.md"],
        }, "Story 31: Export")
        note = document(self.root / "notes" / "linked.md", {"note_kind": "x"}, "Linked")
        with note.open("a", encoding="utf-8") as stream:
            stream.write("\nSee [Export](../specs/prd-export.md)\n")
        with story.open("a", encoding="utf-8") as stream:
            stream.write(
                "\nInline [PRD](../prd-export.md#overview) and image ![a](../prd-export.md)\n"
                "Ref [PRD][prd] and def below; code untouched:\n\n"
                "[prd]: ../prd-export.md\n\n"
                "```markdown\n[fenced](../prd-export.md)\n```\n\n"
                "Backtick `[not a link](../prd-export.md)` stays.\n")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"]
                       if row["source"] == "specs/stories/story-031-export.md")
        self.assertEqual(rewrite["destination"],
                         "subprojects/export/specs/stories/story-001-export.md")
        self.assertIn("[fenced](../prd-export.md)", rewrite["content"])
        self.assertIn("`[not a link](../prd-export.md)`", rewrite["content"])
        self.assertIn("[PRD](../prd.md#overview)", rewrite["content"])
        self.assertIn("![a](../prd.md)", rewrite["content"])
        self.assertIn("[PRD][prd]", rewrite["content"])
        self.assertIn("[prd]: ../prd.md", rewrite["content"])
        note_rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/linked.md")
        self.assertEqual(
            note_rewrite["content"],
            '---\nnote_kind: "x"\n---\n\n# Linked\n\n'
            "See [Export](../subprojects/export/specs/prd.md)\n")
        targets = {link["target"] for link in plan["live_links"]}
        self.assertIn("subprojects/export/specs/prd.md", targets)
        apply_plan(self.root, plan)  # intended targets exist only in the staged view
        validate_migration_links(self.root, {**plan,
            "live_links": [link for link in plan["live_links"]
                           if link["source"] == "notes/linked.md"]})

    def test_validate_migration_links_rejects_missing_target(self) -> None:
        with self.assertRaisesRegex(SpecError, "MIGRATION_LINK_INVALID"):
            validate_migration_links(self.root, {"live_links": [
                {"source": "notes/linked.md", "target": "subprojects/missing/specs/prd.md"}]})

    def test_html_references_to_moved_records_are_rewritten(self) -> None:
        note = document(self.root / "notes" / "html.md", {}, "Html")
        with note.open("a", encoding="utf-8") as stream:
            stream.write(
                '\n<a href="../specs/prd-export.md">Export</a> and <img src="../specs/prd-export.md"/>\n'
                "<a href='../specs/prd-export.md'>single</a>\n")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/html.md")
        self.assertIn('<a href="../subprojects/export/specs/prd.md">Export</a>',
                      rewrite["content"])
        self.assertIn('<img src="../subprojects/export/specs/prd.md"/>', rewrite["content"])
        self.assertIn("<a href='../subprojects/export/specs/prd.md'>single</a>",
                      rewrite["content"])
        self.assertIn({"source": "notes/html.md", "reference": "../specs/prd-export.md",
                       "replacement": "../subprojects/export/specs/prd.md",
                       "target": "subprojects/export/specs/prd.md",
                       "basis": "mapped-path"}, plan["link_corrections"])
        targets = {link["target"] for link in plan["live_links"]
                   if link["source"] == "notes/html.md"}
        self.assertEqual(targets, {"subprojects/export/specs/prd.md"})

    def test_shared_canonical_local_id_is_preserved(self) -> None:
        document(self.specs / "quick-tasks" / "canonical.md", {
            "status": "approved", "record_kind": "quick-task", "local_id": "bridge-7",
        }, "Canonical")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"]
                       if row["source"] == "specs/quick-tasks/canonical.md")
        self.assertIn('local_id: "bridge-7"', rewrite["content"])
        self.assertNotIn("specs/quick-tasks/canonical.md",
                         {item["path"] for item in plan["deletions"]})
        self.assertNotIn("specs/quick-tasks/canonical.md",
                         {row["source"] for row in plan["records"]})

    def test_status_binding_pins_only_valid_existing_bindings(self) -> None:
        import subprocess

        def git(*arguments: str) -> str:
            completed = subprocess.run(["git", "-C", str(self.root), *arguments],
                                       check=True, capture_output=True, text=True)
            return completed.stdout.strip()

        git("init")
        git("config", "user.email", "plan@example.invalid")
        git("config", "user.name", "Plan")
        status = self.root / "STATUS.md"
        status.write_text("# Status\n", encoding="utf-8")
        unbound = migration_plan(self.root)
        self.assertEqual(unbound["status_binding"],
                         {"path": None, "before_sha256": None, "head": "unknown",
                          "disposition": "unbound"})
        entry = self.root / "ProjectEntry.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace(
            'project_id: "demo"', f'project_id: "demo"\nstatus_root: "{self.root}"'),
            encoding="utf-8")
        git("add", "-A")
        git("commit", "-m", "fixture")
        bound = migration_plan(self.root)
        self.assertEqual(bound["status_binding"]["disposition"], "bound")
        self.assertEqual(bound["status_binding"]["path"], str(status))
        self.assertEqual(bound["status_binding"]["before_sha256"],
                         hashlib.sha256(status.read_bytes()).hexdigest())
        self.assertEqual(bound["status_binding"]["head"], git("rev-parse", "HEAD"))
        # The bound plan authenticates the exact planned STATUS bytes.
        planned = bound["status_binding"]["content"]
        self.assertTrue(planned.startswith("<!-- Generated by the Kosmic Projection CLI"))
        self.assertIn(f"Vault HEAD: {bound['status_binding']['head']}", planned)
        self.assertIn("### Subproject: export", planned)
        self.assertEqual(bound["status_binding"]["after_sha256"],
                         hashlib.sha256(planned.encode("utf-8")).hexdigest())
        self.assertEqual(bound["digest"], migration_plan(self.root)["digest"])
        # A configured invalid binding fails planning instead of a silent unbound.
        outside = Path(self.tmp.name) / "not-a-worktree"
        outside.mkdir()
        (outside / "STATUS.md").write_text("# Status\n", encoding="utf-8")
        entry.write_text(entry.read_text(encoding="utf-8").replace(
            f'status_root: "{self.root}"', f'status_root: "{outside}"'), encoding="utf-8")
        with self.assertRaisesRegex(SpecError, "MIGRATION_STATUS_INVALID"):
            migration_plan(self.root)
        # A sibling Project already binding the same root is a collision failure.
        entry.write_text(entry.read_text(encoding="utf-8").replace(
            f'status_root: "{outside}"', f'status_root: "{self.root}"'), encoding="utf-8")
        sibling = Path(self.tmp.name) / "Other"
        sibling.mkdir()
        document(sibling / "ProjectEntry.md", {"project_id": "demo",
                                               "status_root": str(self.root)}, "Other")
        with self.assertRaisesRegex(SpecError, "MIGRATION_STATUS_INVALID"):
            migration_plan(self.root)
        # A non-regular STATUS.md at a configured binding fails planning.
        (sibling / "ProjectEntry.md").unlink()
        status.unlink()
        status.symlink_to(entry)
        with self.assertRaisesRegex(SpecError, "MIGRATION_STATUS_INVALID"):
            migration_plan(self.root)

    def test_malformed_assignments_are_rejected(self) -> None:
        with self.assertRaisesRegex(SpecError, "ASSIGNMENT_INVALID"):
            migration_plan(self.root, assignments={"specs/nope.md": "specs/prd-export.md"})
        with self.assertRaisesRegex(SpecError, "ASSIGNMENT_INVALID"):
            migration_plan(self.root, assignments={"specs/research/x.md": "specs/prd-export.md"})

    def test_inbound_frontmatter_paths_are_rewritten_surgically(self) -> None:
        note = self.root / "notes" / "registry.md"
        note.write_text(
            "---\n"
            "note_kind: registry\n"
            "related_specs: [specs/prd-export.md, notes/keep.md]\n"
            "custom_field:   spaced value  \n"
            "linked_prd: \"specs/architecture-export.md\"\n"
            "---\n"
            "\n# Registry\n\nBody [link](../specs/prd-export.md) stays mapped.\n",
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/registry.md")
        self.assertEqual(
            rewrite["content"],
            "---\n"
            "note_kind: registry\n"
            'related_specs: [../subprojects/export/specs/prd.md, notes/keep.md]\n'
            "custom_field:   spaced value  \n"
            'linked_prd: "../subprojects/export/specs/architecture.md"\n'
            "---\n"
            "\n# Registry\n\nBody [link](../subprojects/export/specs/prd.md) stays mapped.\n")

    def test_bracketed_destinations_are_rewritten_inside_the_brackets(self) -> None:
        note = self.root / "notes" / "angled.md"
        note.write_text(
            "# Angled\n\n"
            "See [PRD](<../specs/prd-export.md>) and [fine](../specs/prd-export.md)\n"
            '[angled]: <../specs/prd-export.md> "T"\n',
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/angled.md")
        self.assertIn("[PRD](<../subprojects/export/specs/prd.md>)", rewrite["content"])
        self.assertIn("[fine](../subprojects/export/specs/prd.md)", rewrite["content"])
        self.assertIn('[angled]: <../subprojects/export/specs/prd.md> "T"', rewrite["content"])
        self.assertEqual([row for row in plan["ambiguities"] if row.get("record") == "notes/angled.md"],
                         [])

    def test_nested_notes_are_inventoried_and_rewritten(self) -> None:
        deep = self.root / "notes" / "sub" / "deep.md"
        document(deep, {"note_kind": "deep"}, "Deep")
        with deep.open("a", encoding="utf-8") as stream:
            stream.write("\nRef [Export](../../specs/prd-export.md)\n")
        plan = migration_plan(self.root)
        self.assertIn("notes/sub/deep.md", plan["inputs"])
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/sub/deep.md")
        import re
        link = re.search(r"\[Export\]\(([^)]+)\)", rewrite["content"])
        self.assertIsNotNone(link)
        self.assertEqual((deep.parent / link.group(1)).resolve(),
                         self.root / "subprojects/export/specs/prd.md")

    def test_project_index_gain_managed_owner_navigation(self) -> None:
        index = self.root / "specs" / "INDEX.md"
        index.write_text("# Specs Index\n\nCustom hand-written notes that must survive.\n",
                         encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "specs/INDEX.md")
        self.assertIn("Custom hand-written notes that must survive.", rewrite["content"])
        self.assertIn("<!-- kosmic:migration-owners:start -->", rewrite["content"])
        self.assertIn("- [Export](../subprojects/export/specs/INDEX.md) — approved",
                      rewrite["content"])
        self.assertIn("<!-- kosmic:migration-owners:end -->", rewrite["content"])
        self.assertIn({"source": "specs/INDEX.md",
                       "target": "subprojects/export/specs/INDEX.md"}, plan["live_links"])
        apply_plan(self.root, plan)
        validate_migration_links(self.root, plan)

    def test_unsupported_legacy_filenames_are_blocked_not_omitted(self) -> None:
        document(self.specs / "epics" / "extra.md", {"status": "draft"}, "Not an epic")
        plan = migration_plan(self.root)
        self.assertIn("specs/epics/extra.md", plan["inputs"])
        self.assertIn(("specs/epics/extra.md", "unsupported-filename"),
                      {(row["record"], row["reason"]) for row in plan["ambiguities"]})

    def test_foreign_legacy_identity_metadata_is_blocked(self) -> None:
        document(self.specs / "quick-tasks" / "foreign.md", {
            "status": "approved", "project_id": "other",
        }, "Foreign task")
        with self.assertRaisesRegex(SpecError, "OWNER_MISMATCH"):
            migration_plan(self.root)
        (self.specs / "quick-tasks" / "foreign.md").unlink()
        story = document(self.specs / "stories" / "story-041-export.md", {
            "status": "approved", "project_id": "demo", "subproject_id": "elsewhere",
            "linked_prd": "../prd-export.md",
        }, "Story 41")
        with self.assertRaisesRegex(SpecError, "OWNER_MISMATCH"):
            migration_plan(self.root)
        # Missing identity metadata canonicalizes normally.
        story.unlink()
        document(self.specs / "stories" / "story-041-export.md", {
            "status": "approved", "linked_prd": "../prd-export.md",
        }, "Story 41")
        plan = migration_plan(self.root)
        moved = {row["source"]: row for row in plan["records"]}
        self.assertEqual(moved["specs/stories/story-041-export.md"]["subproject_id"], "export")

    def test_wiki_references_to_moved_records_are_rewritten_uniquely(self) -> None:
        note = self.root / "notes" / "wikilinks.md"
        note.write_text(
            "# Wiki\n\n"
            "[[prd-export]] and ![[specs/prd-export.md]] and [[prd-export.md|alias]]\n"
            "Unmapped [[notes/keep]] stays; fenced `[[prd-export]]` is code.\n",
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/wikilinks.md")
        self.assertEqual(
            rewrite["content"],
            "# Wiki\n\n"
            "[[subprojects/export/specs/prd.md]] and ![[subprojects/export/specs/prd.md]]"
            " and [[subprojects/export/specs/prd.md|alias]]\n"
            "Unmapped [[notes/keep]] stays; fenced `[[prd-export]]` is code.\n")
        problems = [row for row in plan["link_problems"]
                    if row["record"] == "notes/wikilinks.md"]
        self.assertEqual([(row["reference"], row["reason"], row["candidates"], row["protected"])
                          for row in problems],
                         [("notes/keep", "unresolved-link", [], False)])

    def test_destination_variants_preserve_query_fragment_encoding_and_titles(self) -> None:
        note = self.root / "notes" / "variants.md"
        note.write_text(
            "# Variants\n\n"
            "[plain](../specs/prd-export.md#overview)\n"
            "[encoded](../specs/prd%2Dexport.md#overview)\n"
            "[query](../specs/prd-export.md?view=full#overview)\n"
            '[titled](../specs/prd-export.md "PRD title")\n'
            "[web](HTTPS://example.org/docs?q=1#overview)\n"
            "[remote](//cdn.example.org/image.png)\n"
            "[anchor](#overview)\n",
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/variants.md")
        for label in ("plain", "encoded", "query", "titled"):
            match = re.search(r"\[" + label + r"\]\(([^)]+)\)", rewrite["content"])
            self.assertIsNotNone(match, label)
            destination = match.group(1).split(' "', 1)[0]
            parsed = urlsplit(destination)
            self.assertEqual((self.root / "notes" / unquote(parsed.path)).resolve(),
                             self.root / "subprojects/export/specs/prd.md", label)
        self.assertIn('[titled](../subprojects/export/specs/prd.md "PRD title")',
                      rewrite["content"])
        self.assertIn("[query](../subprojects/export/specs/prd.md?view=full#overview)",
                      rewrite["content"])
        self.assertIn("[web](HTTPS://example.org/docs?q=1#overview)", rewrite["content"])
        self.assertIn("[remote](//cdn.example.org/image.png)", rewrite["content"])
        self.assertIn("[anchor](#overview)", rewrite["content"])

    def test_inbound_url_leaves_are_rewritten_and_nested_values_kept(self) -> None:
        note = self.root / "notes" / "sourced.md"
        note.write_text(
            "---\n"
            "note_kind: source-audit\n"
            'url: "../specs/prd-export.md?view=full#overview"\n'
            "sources:\n"
            "  - path: paper-a.md\n"
            "    title: Paper A\n"
            '    url: "https://example.org/a?q=1#section"\n'
            "  - path: paper-b.md\n"
            "    title: Paper B\n"
            "---\n"
            "\n# Sourced\n",
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/sourced.md")
        self.assertEqual(
            rewrite["content"],
            "---\n"
            "note_kind: source-audit\n"
            'url: "../subprojects/export/specs/prd.md?view=full#overview"\n'
            "sources:\n"
            "  - path: paper-a.md\n"
            "    title: Paper A\n"
            '    url: "https://example.org/a?q=1#section"\n'
            "  - path: paper-b.md\n"
            "    title: Paper B\n"
            "---\n"
            "\n# Sourced\n")

    def test_wrong_directory_references_repair_on_unique_filenames_only(self) -> None:
        (self.root / "mathdocs").mkdir()
        audit = self.root / "mathdocs" / "audit.md"
        audit.write_text("# Audit\n\n[Export](wrong/folder/prd-export.md#overview)\n",
                         encoding="utf-8")
        for folder in ("one", "two"):
            path = self.root / "notes" / folder / "same.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"# {folder}\n", encoding="utf-8")
        live = self.root / "notes" / "live.md"
        live.write_text("# Live\n\n[Ambiguous](missing/same.md)\n", encoding="utf-8")
        (self.root / "evidence").mkdir()
        historical = self.root / "evidence" / "historical.md"
        historical.write_text("[Old](../specs/prd-export.md) and [miss](missing/prd-export.md)\n",
                              encoding="utf-8")
        before = historical.read_bytes()
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "mathdocs/audit.md")
        self.assertIn("[Export](../subprojects/export/specs/prd.md#overview)",
                      rewrite["content"])
        correction = next(row for row in plan["link_corrections"]
                          if row["source"] == "mathdocs/audit.md")
        self.assertEqual(correction["basis"], "moved-alias")
        self.assertEqual(correction["target"], "subprojects/export/specs/prd.md")
        self.assertEqual(correction["reference"], "wrong/folder/prd-export.md#overview")
        self.assertIn("mathdocs/audit.md", plan["inputs"])
        # Protected evidence is pinned and reported, never rewritten.
        self.assertEqual(historical.read_bytes(), before)
        self.assertIn("evidence/historical.md", plan["inputs"])
        protected = [row for row in plan["link_problems"]
                     if row["record"] == "evidence/historical.md"]
        self.assertEqual([row["reason"] for row in protected],
                         ["moved-reference", "unresolved-link"])
        self.assertTrue(all(row["protected"] for row in protected))
        # Ambiguous basenames surface as blockers and the reference stays untouched.
        self.assertIn({"record": "notes/live.md", "reason": "ambiguous-link",
                       "reference": "missing/same.md",
                       "candidates": ["notes/one/same.md", "notes/two/same.md"]},
                      plan["ambiguities"])
        problem = next(row for row in plan["link_problems"]
                       if row["record"] == "notes/live.md")
        self.assertEqual(problem["candidates"], ["notes/one/same.md", "notes/two/same.md"])
        self.assertFalse(problem["protected"])
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/live.md")
        self.assertEqual(rewrite["content"], "# Live\n\n[Ambiguous](missing/same.md)\n")

    def test_nested_flow_and_sequence_url_leaves_are_rewritten_in_place(self) -> None:
        note = self.root / "notes" / "nested.md"
        note.write_text(
            "---\n"
            "note_kind: nested\n"
            'sources: [{path: paper.md, url: missing/prd-export.md},'
            ' {title: "missing/prd-export.md", url: "missing/prd-export.md"}]\n'
            "extra:\n"
            "  - url: wrong/dir/prd-export.md\n"
            "    title: missing/prd-export.md\n"
            "related_specs:\n"
            "  - also/wrong/prd-export.md\n"
            "plain: untouched prd-export.md text\n"
            "# comment mentioning missing/prd-export.md stays\n"
            "---\n"
            "\n# Nested\n",
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/nested.md")
        self.assertEqual(
            rewrite["content"],
            "---\n"
            "note_kind: nested\n"
            "sources: [{path: paper.md, url: ../subprojects/export/specs/prd.md},"
            " {title: \"missing/prd-export.md\", url: \"../subprojects/export/specs/prd.md\"}]\n"
            "extra:\n"
            "  - url: ../subprojects/export/specs/prd.md\n"
            "    title: missing/prd-export.md\n"
            "related_specs:\n"
            "  - ../subprojects/export/specs/prd.md\n"
            "plain: untouched prd-export.md text\n"
            "# comment mentioning missing/prd-export.md stays\n"
            "---\n"
            "\n# Nested\n")
        corrected = {row["reference"]: row for row in plan["link_corrections"]
                     if row["source"] == "notes/nested.md"}
        self.assertEqual(sorted(corrected),
                         ["also/wrong/prd-export.md", "missing/prd-export.md",
                          "wrong/dir/prd-export.md"])
        self.assertEqual({row["target"] for row in corrected.values()},
                         {"subprojects/export/specs/prd.md"})
        self.assertEqual([row for row in plan["link_problems"]
                          if row["record"] == "notes/nested.md"], [])

    def test_json_style_flow_keys_and_multiline_flow_are_rewritten(self) -> None:
        from skills.scripts.kosmic_shared_library import parse_document_text

        note = self.root / "notes" / "jsonflow.md"
        note.write_text(
            "---\n"
            'sources: [{"url":"missing/prd-export.md"}, {url:"wrong/dir/prd-export.md"}]\n'
            "extra: [\n"
            "  {\n"
            "    'url': 'also/wrong/prd-export.md',\n"
            "    title: kept missing/prd-export.md\n"
            "  }\n"
            "]\n"
            "split: [\n"
            "  {url:\n"
            "    missing/prd-export.md}\n"
            "]\n"
            "---\n"
            "\n# Jsonflow\n",
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/jsonflow.md")
        doc = parse_document_text(rewrite["content"], Path("notes/jsonflow.md"))
        expected = "../subprojects/export/specs/prd.md"
        self.assertEqual([row["url"] for row in doc.metadata["sources"]],
                         [expected, expected])
        self.assertEqual([row["url"] for row in doc.metadata["extra"]],
                         [expected])
        self.assertEqual(doc.metadata["extra"][0]["title"], "kept missing/prd-export.md")
        self.assertEqual([row["url"] for row in doc.metadata["split"]],
                         [expected])
        self.assertIn('{"url":"../subprojects/export/specs/prd.md"}', rewrite["content"])
        corrected = {row["reference"] for row in plan["link_corrections"]
                     if row["source"] == "notes/jsonflow.md"}
        self.assertEqual(corrected, {"missing/prd-export.md",
                                     "wrong/dir/prd-export.md",
                                     "also/wrong/prd-export.md"})

    def test_unplaceable_json_references_keep_visible_diagnostics(self) -> None:
        note = self.root / "notes" / "silent.md"
        note.write_text(
            "---\n"
            'sources: [{"url":"totally/missing/nowhere.md"}]\n'
            "---\n"
            "\n# Silent\n",
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/silent.md")
        self.assertEqual(rewrite["content"], note.read_text(encoding="utf-8"))
        problems = [row for row in plan["link_problems"]
                    if row["record"] == "notes/silent.md"]
        self.assertEqual([(row["reference"], row["reason"], row["candidates"],
                           row["protected"]) for row in problems],
                         [("totally/missing/nowhere.md", "unresolved-link", [], False)])
        self.assertEqual([row for row in plan["link_corrections"]
                          if row["source"] == "notes/silent.md"], [])

    def test_valid_encoded_urls_in_staying_documents_keep_their_bytes(self) -> None:
        (self.root / "notes" / "deep").mkdir(parents=True)
        target = self.root / "notes" / "deep" / "my note.md"
        target.write_text("# Target\n", encoding="utf-8")
        note = self.root / "notes" / "encoded.md"
        note.write_text(
            "---\n"
            'url: "./deep/my%20note.md"\n'
            'related_notes: ["../notes/deep/my%20note.md"]\n'
            "---\n"
            "\n# Encoded\n\n[body](./deep/my%20note.md)\n",
            encoding="utf-8")
        before = note.read_bytes()
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/encoded.md")
        self.assertEqual(rewrite["content"], before.decode("utf-8"))
        self.assertEqual([row for row in plan["link_corrections"]
                          if row["source"] == "notes/encoded.md"], [])

    def test_inline_titles_with_parentheses_are_rewritten(self) -> None:
        note = self.root / "notes" / "titled.md"
        note.write_text(
            '# Titled\n\n[PRD](../specs/prd-export.md "Background (reviewed)") and'
            " [plain](../specs/prd-export.md)\n",
            encoding="utf-8")
        plan = migration_plan(self.root)
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/titled.md")
        self.assertIn('[PRD](../subprojects/export/specs/prd.md "Background (reviewed)")',
                      rewrite["content"])
        self.assertIn("[plain](../subprojects/export/specs/prd.md)", rewrite["content"])

    def test_symlinked_protected_root_is_a_typed_error(self) -> None:
        (self.root / "elsewhere").mkdir()
        (self.root / "evidence").symlink_to(self.root / "elsewhere")
        with self.assertRaisesRegex(SpecError, "SCOPE_DENIED"):
            migration_plan(self.root)

    def test_symlinked_root_markdown_is_a_typed_error(self) -> None:
        entry = self.root / "ProjectEntry.md"
        (self.root / "linked-entry.md").symlink_to(entry)
        with self.assertRaisesRegex(SpecError, "SCOPE_DENIED"):
            migration_plan(self.root)

    def test_bound_directory_without_status_md_plans_creation(self) -> None:
        import subprocess

        def git(*arguments: str) -> str:
            completed = subprocess.run(["git", "-C", str(self.root), *arguments],
                                       check=True, capture_output=True, text=True)
            return completed.stdout.strip()

        git("init")
        git("config", "user.email", "plan@example.invalid")
        git("config", "user.name", "Plan")
        entry = self.root / "ProjectEntry.md"
        entry.write_text(entry.read_text(encoding="utf-8").replace(
            'project_id: "demo"', f'project_id: "demo"\nstatus_root: "{self.root}"'),
            encoding="utf-8")
        git("add", "-A")
        git("commit", "-m", "fixture")
        self.assertFalse((self.root / "STATUS.md").exists())
        plan = migration_plan(self.root)
        binding = plan["status_binding"]
        self.assertEqual(binding["disposition"], "bound")
        self.assertEqual(binding["path"], str(self.root / "STATUS.md"))
        self.assertIsNone(binding["before_sha256"])
        self.assertEqual(binding["head"], git("rev-parse", "HEAD"))
        self.assertEqual(binding["after_sha256"],
                         hashlib.sha256(binding["content"].encode("utf-8")).hexdigest())
        self.assertEqual(plan["digest"], migration_plan(self.root)["digest"])

    def test_applied_plan_validates_and_replans_as_noop(self) -> None:
        plan = migration_plan(self.root, work_record="specs/quick-tasks/migrate.md")
        self.assertEqual(plan["ambiguities"], [])
        apply_plan(self.root, plan)
        catalog = SpecCatalog(self.root)
        catalog.validate()
        again = migration_plan(self.root, work_record="specs/quick-tasks/migrate.md")
        self.assertEqual(again["records"], [])
        self.assertEqual(again["outputs"], [])
        self.assertEqual(again["deletions"], [])
        self.assertEqual(again["existing_subprojects"], ["export"])
        self.assertEqual(again["digest"],
                         migration_plan(self.root, work_record="specs/quick-tasks/migrate.md")["digest"])

