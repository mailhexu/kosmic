from __future__ import annotations

import hashlib
import unittest

from skills.scripts.kosmic_specs import migration_plan
from tests import test_kosmic_migration_plan as fixture


class CuratedInputTest(unittest.TestCase):
    def test_proposal_inputs_are_pinned_report_only_even_with_template_headers(self) -> None:
        case = fixture.MigrationPlanTest()
        case.setUp()
        self.addCleanup(case.doCleanups)
        root = case.root
        inputs = root / "specs/skill-proposals/inputs"
        curated = inputs / "curated"
        curated.mkdir(parents=True)
        template = curated / "template.md"
        template.write_text("---\ninput_manifest: [specs/inputs/{slug}.md]\n---\n# Template\n")
        snapshot = curated / "source.md"
        snapshot.write_text("[Export](../../../prd-export.md)\n")
        manifest = inputs / "manifest.md"
        manifest.write_text("- specs/skill-proposals/inputs/curated/source.md: "
                            + hashlib.sha256(snapshot.read_bytes()).hexdigest() + "\n")
        before = {path.relative_to(root).as_posix(): path.read_bytes()
                  for path in (template, snapshot, manifest)}
        live = root / "notes/live.md"
        live.write_text("[Export](../specs/prd-export.md)\n")
        plan = migration_plan(root)
        for relative, raw in before.items():
            self.assertEqual(plan["inputs"][relative], hashlib.sha256(raw).hexdigest())
            self.assertFalse(any(row["source"] == relative for row in plan["rewrites"]))
            self.assertFalse(any(row["path"] == relative for row in plan["outputs"]))
        problems = [row for row in plan["link_problems"]
                    if row["record"] in before]
        self.assertEqual({(row["record"], row["reason"], row["protected"])
                          for row in problems}, {
            (template.relative_to(root).as_posix(), "unparsable-document", True),
            (snapshot.relative_to(root).as_posix(), "moved-reference", True),
        })
        fixture.apply_plan(root, plan)
        self.assertEqual(before, {relative: (root / relative).read_bytes()
                                  for relative in before})
        self.assertEqual(live.read_text(),
                         "[Export](../subprojects/export/specs/prd.md)\n")


if __name__ == "__main__":
    unittest.main()
