from __future__ import annotations

import unittest
from pathlib import Path

from skills.scripts.kosmic_project_skills import KosmicError, parse_markdown, update_markdown_metadata
from skills.scripts.kosmic_shared_library import LibraryError, parse_document_text
from skills.scripts.kosmic_yaml import YAMLParseError, parse_mapping, parse_scalar, render_entry


class StructuredHeaderTest(unittest.TestCase):
    def test_nested_sources_titles_belong_to_their_own_mappings(self) -> None:
        text = '''---
title: Document title
sources:
  - path: first.md
    title: First source
    url: "https://example.org/a?q=1#section"
    authors: ["Last, First", "Second Author"]
  - path: second.md
    title: Second source
    details:
      title: Nested detail
      verified: true
---

# Body
'''
        expected = {'title': 'Document title', 'sources': [
            {'path': 'first.md', 'title': 'First source',
             'url': 'https://example.org/a?q=1#section',
             'authors': ['Last, First', 'Second Author']},
            {'path': 'second.md', 'title': 'Second source',
             'details': {'title': 'Nested detail', 'verified': True}}]}
        library = parse_document_text(text, Path('note.md'))
        cli = parse_markdown(text)
        self.assertEqual(library.metadata, expected)
        self.assertEqual(cli.metadata, expected)
        self.assertEqual(library.body, '\n# Body\n')
        changed = update_markdown_metadata(text, {'status': 'approved'})
        self.assertEqual(parse_document_text(changed, Path('note.md')).metadata['sources'],
                         expected['sources'])

    def test_real_duplicate_keys_within_one_mapping_still_fail(self) -> None:
        for header in ('title: First\ntitle: Second\n',
                       'sources:\n  - title: First\n    title: Second\n'):
            with self.subTest(header=header):
                with self.assertRaises(LibraryError):
                    parse_document_text('---\n' + header + '---\n', Path('note.md'))

    def test_json_nested_values_and_quoted_commas_round_trip(self) -> None:
        text = '---\ntitle: "Outer"\nsources: [{"title": "Inner", "authors": ["One, Two", "Three"]}]\n---\n'
        expected = [{'title': 'Inner', 'authors': ['One, Two', 'Three']}]
        self.assertEqual(parse_document_text(text, Path('note.md')).metadata['sources'], expected)
        self.assertEqual(parse_markdown(text).metadata['sources'], expected)

    def test_scalars_keep_quoted_ids_dates_and_legacy_null_spellings(self) -> None:
        text = (
            '---\n'
            "local_id: '001'\n"
            'count: 12\n'
            'ratio: 1.5\n'
            'created: 2026-01-15\n'
            "updated: '2026-01-16'\n"
            'verified: true\n'
            'missing: null\n'
            'legacy: ~\n'
            'empty:\n'
            '---\n'
        )
        expected = {
            'local_id': '001', 'count': 12, 'ratio': 1.5,
            'created': '2026-01-15', 'updated': '2026-01-16',
            'verified': True, 'missing': None, 'legacy': None, 'empty': None,
        }
        self.assertEqual(parse_document_text(text, Path('note.md')).metadata, expected)
        cli_expected = dict(expected, empty='')
        self.assertEqual(parse_markdown(text).metadata, cli_expected)

    def test_unsafe_yaml_constructs_are_rejected(self) -> None:
        headers = (
            'tagged: !!python/object:os.system\n',
            'anchor: &a value\n',
            'alias: *a\n',
            '- root\n- sequence\n',
            'merged:\n  <<: *base\n',
            'key:\n\t- tabbed\n',
        )
        for header in headers:
            with self.subTest(header=header):
                with self.assertRaises(LibraryError):
                    parse_document_text('---\n' + header + '---\n', Path('note.md'))
                with self.assertRaises(KosmicError):
                    parse_markdown('---\n' + header + '---\n')

    def test_tagged_anchored_and_complex_keys_are_rejected(self) -> None:
        for header in (
            '!tag key: value\n',
            '&anchor key: value\n',
            '*alias: value\n',
            '? complex\n',
            '? a: b\n',
            'sources: [{? a: b}]\n',
        ):
            with self.subTest(header=header):
                with self.assertRaises(YAMLParseError):
                    parse_mapping(header)
                with self.assertRaises(LibraryError):
                    parse_document_text('---\n' + header + '---\n', Path('note.md'))

    def test_plain_keys_with_later_indicator_characters_stay_valid(self) -> None:
        self.assertEqual(
            parse_mapping('?foo: v\nfoo!bar: v\na&b: c\n'),
            {'?foo': 'v', 'foo!bar': 'v', 'a&b': 'c'})

    def test_invalid_double_quoted_hex_escapes_fail_as_parse_errors(self) -> None:
        for header in ('bad: "\\xzz"\n', 'bad: "\\uZZZZ"\n', 'bad: "\\UFFFFFFFF"\n'):
            with self.subTest(header=header):
                with self.assertRaises(YAMLParseError):
                    parse_mapping(header)
                with self.assertRaises(LibraryError):
                    parse_document_text('---\n' + header + '---\n', Path('note.md'))
                with self.assertRaises(KosmicError):
                    parse_markdown('---\n' + header + '---\n')
        self.assertEqual(parse_mapping('ok: "\\x41\\u00e9"\n')['ok'], 'A\u00e9')

    def test_comments_and_block_scalars_parse(self) -> None:
        text = (
            '---\n'
            '# leading comment\n'
            'title: Notes # trailing comment\n'
            'description: |\n'
            '  line one\n'
            '  line two\n'
            'folded: >\n'
            '  folded text\n'
            '  joins lines\n'
            '---\n'
        )
        expected = {'title': 'Notes', 'description': 'line one\nline two\n',
                    'folded': 'folded text joins lines\n'}
        self.assertEqual(parse_document_text(text, Path('note.md')).metadata, expected)
        self.assertEqual(parse_markdown(text).metadata, expected)

    def test_multiline_json_header_spans_lines(self) -> None:
        text = (
            '---\n'
            'title: Doc\n'
            'sources: [\n'
            '  {"path": "a.md", "authors": ["One, Two"]},\n'
            '  {"path": "b.md"}\n'
            ']\n'
            '---\n'
        )
        expected = [{'path': 'a.md', 'authors': ['One, Two']}, {'path': 'b.md'}]
        self.assertEqual(parse_document_text(text, Path('note.md')).metadata['sources'], expected)
        self.assertEqual(parse_markdown(text).metadata['sources'], expected)

    def test_entries_after_multiline_flow_are_not_swallowed(self) -> None:
        text = (
            '---\n'
            'title: Doc\n'
            'sources: [\n'
            '  {"path": "a.md"},\n'
            '  {"path": "b.md"}\n'
            ']\n'
            'status: draft\n'
            'updated: 2026-01-15\n'
            '---\n'
        )
        expected = {'title': 'Doc', 'sources': [{'path': 'a.md'}, {'path': 'b.md'}],
                    'status': 'draft', 'updated': '2026-01-15'}
        self.assertEqual(parse_document_text(text, Path('note.md')).metadata, expected)
        self.assertEqual(parse_markdown(text).metadata, expected)

    def test_duplicate_keys_inside_one_flow_mapping_fail(self) -> None:
        for header in (
            'sources: [{"title": "A", "title": "B"}]\n',
            'sources: [{title: A, title: B}]\n',
            'details: {title: A, title: B}\n',
            'sources: [{"title": "A", "path": "x"}, {"title": "B", "title": "C"}]\n',
        ):
            with self.subTest(header=header):
                with self.assertRaises(YAMLParseError):
                    parse_mapping(header)
                with self.assertRaises(LibraryError):
                    parse_document_text('---\n' + header + '---\n', Path('note.md'))

    def test_repeated_titles_across_separate_flow_elements_stay_valid(self) -> None:
        text = '---\nsources: [{title: A, path: a.md}, {title: B, path: b.md}]\n---\n'
        expected = [{'title': 'A', 'path': 'a.md'}, {'title': 'B', 'path': 'b.md'}]
        self.assertEqual(parse_document_text(text, Path('note.md')).metadata['sources'], expected)
        self.assertEqual(parse_markdown(text).metadata['sources'], expected)
        self.assertEqual(
            parse_mapping('sources: [{title: A}, {title: A}]')['sources'],
            [{'title': 'A'}, {'title': 'A'}])

    def test_legacy_bare_key_block_list_survives(self) -> None:
        text = '---\ntype: Domain Topic\ntriggers:\n- build it\n- test it\n---\n'
        metadata = parse_document_text(text, Path('note.md')).metadata
        self.assertEqual(metadata['triggers'], ['build it', 'test it'])
        self.assertEqual(parse_markdown(text).metadata['triggers'], ['build it', 'test it'])

    def test_bare_key_is_blank_for_cli_and_null_for_library(self) -> None:
        text = '---\ntarget:\nnote: x\n---\n'
        self.assertEqual(parse_markdown(text).metadata['target'], '')
        self.assertIsNone(parse_document_text(text, Path('note.md')).metadata['target'])

    def test_update_keeps_untouched_blocks_byte_identical(self) -> None:
        text = '''---
title: Document title
sources:
  - path: first.md
    title: First source
status: draft
---

# Body
'''
        changed = update_markdown_metadata(text, {'status': 'approved'})
        for line in ('title: Document title\n', 'sources:\n', '  - path: first.md\n',
                     '    title: First source\n'):
            self.assertIn(line, changed.splitlines(keepends=True))
        metadata = parse_document_text(changed, Path('note.md')).metadata
        self.assertEqual(metadata['status'], 'approved')
        self.assertEqual(metadata['sources'], [{'path': 'first.md', 'title': 'First source'}])

    def test_update_never_rewrites_nested_title_as_root_title(self) -> None:
        text = '---\ntitle: Root\nsources:\n- title: Nested\n  path: a.md\n---\n\n# Body\n'
        changed = update_markdown_metadata(text, {'title': 'New Root', 'status': 'stable'})
        metadata = parse_document_text(changed, Path('note.md')).metadata
        self.assertEqual(metadata['title'], 'New Root')
        self.assertEqual(metadata['sources'], [{'title': 'Nested', 'path': 'a.md'}])
        self.assertEqual(parse_markdown(changed).metadata, metadata)

    def test_update_serializes_nested_values_structured_for_reload(self) -> None:
        text = '---\ntitle: Doc\nstatus: draft\n---\n\n# Body\n'
        sources = [
            {'path': 'first.md', 'title': 'First source',
             'url': 'https://example.org/a?q=1#section'},
            {'path': 'second.md', 'title': 'Second, comma source', 'verified': True},
        ]
        changed = update_markdown_metadata(text, {'sources': sources})
        metadata = parse_document_text(changed, Path('note.md')).metadata
        self.assertEqual(metadata['sources'], sources)
        self.assertEqual(parse_markdown(changed).metadata['sources'], sources)

    def test_render_entry_output_round_trips_through_parse_mapping(self) -> None:
        value = {'sources': [
            {'path': 'a.md', 'authors': ['One, Two'], 'tags': ['x', 'y']},
            {'path': 'b.md', 'details': {'title': 'Inner', 'n': 3}},
        ]}
        rendered = ''.join(
            ''.join(render_entry(key, item)) for key, item in value.items()
        )
        self.assertEqual(parse_mapping(rendered), value)

    def test_parse_scalar_keeps_legacy_cli_semantics(self) -> None:
        self.assertEqual(parse_scalar(''), '')
        self.assertEqual(parse_scalar("'001'"), '001')
        self.assertIs(parse_scalar('true'), True)
        self.assertIsNone(parse_scalar('null'))
        self.assertEqual(parse_scalar('2026-01-15'), '2026-01-15')
        self.assertEqual(parse_scalar('[a, b]'), ['a', 'b'])
        self.assertEqual(parse_scalar('"Last, First"'), 'Last, First')


if __name__ == '__main__':
    unittest.main()
