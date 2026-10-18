from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from skills.scripts.kosmic_specs import read_document
from tests import test_kosmic_migration_apply as migration_fixture

CLI = migration_fixture.CLI

class LinkCorrectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = migration_fixture.MigrationApplyTest()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.root = self.fixture.root

    def apply(self) -> dict:
        planned = subprocess.run([sys.executable, str(CLI), 'migrate-subprojects-plan',
            '--project', str(self.root), '--output', str(self.fixture.plan_path)],
            capture_output=True, text=True, timeout=15)
        self.assertEqual(planned.returncode, 0, planned.stderr)
        plan = json.loads(self.fixture.plan_path.read_text())
        applied = self.fixture.cli('migrate-subprojects-apply', plan)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        return plan

    def test_nested_header_and_local_url_variants_survive_actual_cli_migration(self) -> None:
        source = self.root / 'specs/stories/story-01-export.md'
        text = source.read_text().replace('depends_on: []', '''depends_on: []
url: "../prd-export.md?view=full#overview"
sources:
  - path: paper-a.md
    title: Paper A
    url: "https://example.org/a?q=1#section"
  - path: paper-b.md
    title: Paper B''')
        text += '''
[plain](../prd-export.md#overview)
[encoded](../prd%2Dexport.md#overview)
[query](../prd-export.md?view=full#overview)
[titled](../prd-export.md "PRD title")
[web](HTTPS://example.org/docs?q=1#overview)
[remote](//cdn.example.org/image.png)
'''
        source.write_text(text)
        self.apply()
        target = self.root / 'subprojects/export/specs/stories/story-001-export.md'
        doc = read_document(self.root, target)
        self.assertEqual([row['title'] for row in doc.metadata['sources']], ['Paper A', 'Paper B'])
        self.assertEqual(doc.metadata['sources'][0]['url'], 'https://example.org/a?q=1#section')
        header = urlsplit(doc.metadata['url'])
        self.assertEqual((target.parent / unquote(header.path)).resolve(),
                         self.root / 'subprojects/export/specs/prd.md')
        self.assertEqual((header.query, header.fragment), ('view=full', 'overview'))
        for label in ('plain', 'encoded', 'query', 'titled'):
            match = re.search(r'\[' + label + r'\]\(([^)]+)\)', doc.body)
            self.assertIsNotNone(match)
            destination = match.group(1).split(' "', 1)[0]
            parsed = urlsplit(destination)
            self.assertEqual((target.parent / unquote(parsed.path)).resolve(),
                             self.root / 'subprojects/export/specs/prd.md')
        self.assertIn('"PRD title"', doc.body)
        self.assertIn('[web](HTTPS://example.org/docs?q=1#overview)', doc.body)
        self.assertIn('[remote](//cdn.example.org/image.png)', doc.body)

    def test_broken_filename_links_are_repaired_in_authoritative_files_only(self) -> None:
        (self.root / 'mathdocs').mkdir()
        note = self.root / 'mathdocs/audit.md'
        note.write_text('# Audit\n\n[Export](wrong/folder/prd-export.md#overview)\n')
        historical = self.root / 'evidence/historical.md'
        historical.write_text('[Export](missing/prd-export.md#overview)\n')
        before = historical.read_bytes()
        plan = self.apply()
        match = re.search(r'\[Export\]\(([^)]+)\)', note.read_text())
        parsed = urlsplit(match.group(1))
        self.assertEqual((note.parent / unquote(parsed.path)).resolve(),
                         self.root / 'subprojects/export/specs/prd.md')
        self.assertEqual(parsed.fragment, 'overview')
        self.assertEqual(historical.read_bytes(), before)
        self.assertIn('mathdocs/audit.md', plan['inputs'])

    def test_ambiguous_basenames_are_reported_and_not_guessed(self) -> None:
        for folder in ('one', 'two'):
            path = self.root / 'notes' / folder / 'same.md'
            path.parent.mkdir()
            path.write_text('# ' + folder + '\n')
        note = self.root / 'notes/live.md'
        note.write_text('# Live\n\n[Ambiguous](missing/same.md)\n')
        planned = subprocess.run([sys.executable, str(CLI), 'migrate-subprojects-plan',
            '--project', str(self.root)], capture_output=True, text=True, timeout=15)
        self.assertEqual(planned.returncode, 0, planned.stderr)
        plan = json.loads(planned.stdout)
        self.assertTrue(any(row.get('record') == 'notes/live.md'
                            and row.get('reason') == 'ambiguous-link'
                            for row in plan['ambiguities']), plan['ambiguities'])
        self.assertEqual(note.read_text(), '# Live\n\n[Ambiguous](missing/same.md)\n')

    def test_nested_block_and_flow_url_repair_changes_the_actual_header(self) -> None:
        flow = self.root / 'notes/flow.md'
        flow.write_text('---\ntitle: Flow\nsources: [{title: Paper, url: missing/prd-export.md#overview}]\ncustom: unchanged\n---\n\n# Flow\n')
        block = self.root / 'notes/block.md'
        block.write_text('---\ntitle: Block\nsources:\n  - title: Paper\n    url: missing/prd-export.md#overview\n  - url: missing/prd-export.md#overview\n    title: Other\ncustom: unchanged\n---\n\n# Block\n')
        self.apply()
        for path in (flow, block):
            doc = read_document(self.root, path)
            for source in doc.metadata['sources']:
                parsed = urlsplit(source['url'])
                self.assertEqual((path.parent / unquote(parsed.path)).resolve(),
                                 self.root / 'subprojects/export/specs/prd.md')
                self.assertEqual(parsed.fragment, 'overview')
            self.assertIn('custom: unchanged\n', path.read_text())

    def test_valid_encoded_yaml_url_is_byte_identical_when_file_stays_put(self) -> None:
        (self.root / 'notes/target.md').write_text('# Target\n')
        note = self.root / 'notes/valid.md'
        original = '---\ntitle: Valid\nurl: "../notes/target%2Emd?q=1#section"\n---\n\n# Valid\n'
        note.write_text(original)
        self.apply()
        self.assertEqual(note.read_text(), original)

    def test_parentheses_inside_link_title_do_not_hide_the_moved_destination(self) -> None:
        note = self.root / 'notes/titled.md'
        note.write_text('[PRD](../specs/prd-export.md "Background (reviewed)")\n')
        self.apply()
        self.assertEqual(note.read_text(),
                         '[PRD](../subprojects/export/specs/prd.md "Background (reviewed)")\n')

    def test_symlinked_authoritative_root_or_protected_root_is_not_silently_omitted(self) -> None:
        from skills.scripts.kosmic_specs import SpecError, migration_plan
        outside = Path(self.fixture.tmp.name) / 'outside'
        outside.mkdir()
        (outside / 'document.md').write_text('# Outside\n')
        link = self.root / 'README.md'
        link.symlink_to(outside / 'document.md')
        with self.assertRaisesRegex(SpecError, 'SCOPE_DENIED'):
            migration_plan(self.root)
        link.unlink()
        (self.root / 'logs').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(SpecError, 'SCOPE_DENIED'):
            migration_plan(self.root)
        self.assertEqual((outside / 'document.md').read_text(), '# Outside\n')

    def test_unplaceable_resolved_yaml_scalar_blocks_apply_without_silent_diagnostics(self) -> None:
        from skills.scripts.kosmic_specs import migration_plan
        note = self.root / 'notes/escaped.md'
        original = '---\ntitle: Escaped\nurl: "missing\\x2fprd-export.md"\n---\n'
        note.write_text(original)
        plan = migration_plan(self.root)
        rows = [row for row in plan['link_problems'] if row['record'] == 'notes/escaped.md']
        self.assertEqual(rows, [{
            'record': 'notes/escaped.md', 'reference': 'missing/prd-export.md',
            'reason': 'unsupported-link-rewrite',
            'candidates': ['subprojects/export/specs/prd.md'], 'protected': False,
        }])
        self.assertTrue(any(row.get('record') == 'notes/escaped.md'
                            and row.get('reason') == 'unsupported-link-rewrite'
                            for row in plan['ambiguities']))
        self.assertEqual(note.read_text(), original)


if __name__ == '__main__':
    unittest.main()
