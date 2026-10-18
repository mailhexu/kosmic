from __future__ import annotations

import hashlib
import re
import unittest
from urllib.parse import unquote

from skills.scripts.kosmic_specs import migration_plan, validate_migration_links
from tests import test_kosmic_migration_plan as fixture


class LinkAuditTargetTest(unittest.TestCase):
    def setUp(self) -> None:
        self.case = fixture.MigrationPlanTest()
        self.case.setUp()
        self.addCleanup(self.case.doCleanups)
        self.root = self.case.root

    def test_protected_targets_resolve_but_are_not_repair_candidates(self) -> None:
        evidence = self.root / "evidence/pack"
        evidence.mkdir(parents=True)
        memo = evidence / "memo.md"
        memo.write_text("# Memo\n")
        duplicate = evidence / "same.md"
        duplicate.write_text("# Historical same\n")
        (self.root / "notes/same.md").write_text("# Authoritative same\n")
        note = self.root / "notes/source.md"
        original = "[Memo](../evidence/pack/memo.md)\n[Same](missing/same.md)\n"
        note.write_text(original)
        story = self.root / "specs/stories/story-031-export.md"
        story.write_text(story.read_text() + "\n[Memo](../../evidence/pack/memo.md)\n")
        before = memo.read_bytes()
        plan = migration_plan(self.root)
        self.assertEqual(plan["ambiguities"], [])
        self.assertFalse(any(row["record"] == "notes/source.md"
                             for row in plan["link_problems"]))
        self.assertEqual(plan["inputs"]["evidence/pack/memo.md"],
                         hashlib.sha256(before).hexdigest())
        self.assertFalse(any(row["source"].startswith("evidence/")
                             for row in plan["rewrites"]))
        correction = next(row for row in plan["link_corrections"]
                          if row["source"] == "notes/source.md")
        self.assertEqual(correction["target"], "notes/same.md")
        fixture.apply_plan(self.root, plan)
        validate_migration_links(self.root, plan)
        self.assertEqual(note.read_text(), "[Memo](../evidence/pack/memo.md)\n[Same](same.md)\n")
        moved = next(row["destination"] for row in plan["records"]
                     if row["source"] == "specs/stories/story-031-export.md")
        destination = self.root / moved
        reference = re.search(r"\[Memo\]\(([^)]+)\)", destination.read_text()).group(1)
        self.assertEqual((destination.parent / unquote(reference)).resolve(), memo)
        self.assertEqual(memo.read_bytes(), before)

    def test_escaped_table_wikilink_alias_preserves_fragment_and_display(self) -> None:
        note = self.root / "notes/table.md"
        note.write_text("| Story |\n| --- |\n| [[../specs/stories/story-031-export\\|Story 31]] |\n| [[../specs/stories/story-031-export#acceptance\\|Acceptance]] |\n")
        plan = migration_plan(self.root)
        self.assertFalse(any(row["record"] == "notes/table.md"
                             for row in plan["link_problems"]))
        target = next(row["destination"] for row in plan["records"]
                      if row["source"] == "specs/stories/story-031-export.md")
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/table.md")
        self.assertEqual(rewrite["content"],
                         "| Story |\n| --- |\n| [[" + target + "\\|Story 31]] |\n| [[" + target + "#acceptance\\|Acceptance]] |\n")
        self.assertIn({"source": "notes/table.md", "target": target, "fragment": "acceptance"},
                      plan["live_links"])
        fixture.apply_plan(self.root, plan)
        self.assertTrue((self.root / target).is_file())

    def test_prose_citations_are_not_definitions_but_line_start_definitions_rewrite(self) -> None:
        note = self.root / "notes/citations.md"
        prose = ("Open descriptors are unaffected [rename(2) DESCRIPTION]: concurrent writers continue.\n"
                 "`rename` [rename(2) ERRORS]: treat it as retryable.\n")
        note.write_text(prose + '[prd]: ../specs/prd-export.md "PRD"\n')
        plan = migration_plan(self.root)
        self.assertFalse(any(row["record"] == "notes/citations.md"
                             for row in plan["link_problems"]))
        rewrite = next(row for row in plan["rewrites"] if row["source"] == "notes/citations.md")
        self.assertEqual(rewrite["content"], prose + '[prd]: ../subprojects/export/specs/prd.md "PRD"\n')


if __name__ == "__main__":
    unittest.main()
