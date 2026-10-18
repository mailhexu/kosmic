"""ADR-F curation metadata regression tests (Story 002)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from skills.scripts.kosmic_project_skills import (
    KosmicError,
    load_project,
    note_skill_candidate,
    note_skill_resources,
    validate_project_content,
)

MATH_INDEX = (
    "# Math Derivations\n\n"
    "| Derivation | Status | Result summary |\n"
    "|------------|--------|----------------|\n"
)


class CurationMetadataCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.project = self.root / "vault/Projects/demo"
        self.project.mkdir(parents=True)
        (self.project / "ProjectEntry.md").write_text(
            "---\nproject_id: demo\nworking_state: working-tree\n---\n# Demo\n",
            encoding="utf-8",
        )
        (self.project / "notes").mkdir()
        (self.project / "notes/index.md").write_text(
            '---\nokf_version: "0.2"\n---\n# Knowledge\n', encoding="utf-8"
        )
        (self.project / "mathdocs").mkdir()
        (self.project / "mathdocs/index.md").write_text(MATH_INDEX, encoding="utf-8")

    def note(self, name: str, metadata: str, body: str = "") -> Path:
        path = self.project / "notes" / name
        path.write_text(
            "---\ntype: reference\nstatus: stable\naudience: both\n"
            "artifact_role: knowledge\n" + metadata + "---\n\n"
            + (body or "# Concept note\n\nA documented convention.\n"),
            encoding="utf-8",
        )
        return path

    def validated(self, metadata: str) -> None:
        self.note("concept.md", metadata)
        validate_project_content(load_project(self.project))

    def test_skill_candidate_must_be_boolean_shape(self) -> None:
        # A legacy note without the ADR-F fields stays valid (absent = false/[]).
        self.validated("")
        # A quoted non-boolean skill_candidate is a malformed declared shape
        # and must be rejected instead of silently accepted.
        with self.assertRaises(KosmicError) as caught:
            self.validated('skill_candidate: "yes"\nskill_resources: []\n')
        self.assertIn("skill_candidate", str(caught.exception))

    def test_skill_resources_must_be_list_of_stable_ids(self) -> None:
        self.validated("skill_candidate: false\nskill_resources: []\n")
        for malformed in (
            "skill_resources: kosmic-usage\n",        # scalar, not a list
            "skill_resources: [3]\n",                 # non-string entry
            'skill_resources: [""]\n',                # empty id
            'skill_resources: ["kosmic usage"]\n',    # whitespace, not a stable id
        ):
            with self.assertRaises(KosmicError) as caught:
                self.validated(malformed)
            self.assertIn("skill_resources", str(caught.exception))

    def test_curation_metadata_readers_follow_the_adr_f_contract(self) -> None:
        # Absent fields read as the defaults; legacy notes need no rewrite.
        self.assertIs(note_skill_candidate({}, "n.md"), False)
        self.assertEqual(note_skill_resources({}, "n.md"), [])
        # Declared shapes parse typed, and independent fields stay independent.
        self.assertIs(
            note_skill_candidate({"skill_candidate": True}, "n.md"), True
        )
        self.assertEqual(
            note_skill_resources(
                {"skill_resources": ["kosmic-usage", "tb2j-dev"]}, "n.md"
            ),
            ["kosmic-usage", "tb2j-dev"],
        )
        with self.assertRaises(KosmicError):
            note_skill_candidate({"skill_candidate": "no"}, "n.md")
        with self.assertRaises(KosmicError):
            note_skill_resources({"skill_resources": "kosmic-usage"}, "n.md")

    def test_note_updated_accepts_aware_utc_instants(self) -> None:
        self.validated("updated: 2026-10-18T09:30:00Z\n")
        self.validated("updated: 2026-10-18T09:30:00.123456Z\n")

    def test_note_updated_preserves_legacy_dates(self) -> None:
        self.validated("updated: 2026-09-01\n")

    def test_note_updated_rejects_naive_or_offset_timestamps(self) -> None:
        for invalid in (
            "updated: 2026-10-18T09:30:00\n",          # naive, not UTC-aware
            "updated: 2026-10-18T09:30:00+02:00\n",    # offset, not UTC-Z
            "updated: 2026-10-18 09:30:00\n",          # space separator
            "updated: 18-10-2026\n",
        ):
            with self.assertRaises(KosmicError):
                self.validated(invalid)

    def test_skill_resources_rejects_whitespace_in_original_id(self) -> None:
        for malformed in (
            'skill_resources: [" kosmic-usage"]',   # leading whitespace
            'skill_resources: ["kosmic-usage "]',   # trailing whitespace
            'skill_resources: ["kosmic\\tusage"]',  # internal whitespace
        ):
            with self.assertRaises(KosmicError) as caught:
                self.validated(malformed + "\n")
            self.assertIn("skill_resources", str(caught.exception))

    def test_note_updated_rejects_impossible_utc_instants(self) -> None:
        for invalid in (
            'updated: "2026-13-45T99:99:99Z"',   # impossible calendar and clock
            'updated: "2026-02-30T00:00:00Z"',   # impossible calendar day
            'updated: "2026-10-18T25:00:00Z"',   # impossible hour
            'updated: "2026-10-18T09:61:00Z"',   # impossible minute
        ):
            with self.assertRaises(KosmicError):
                self.validated(invalid + "\n")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
