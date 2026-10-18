"""Record-scoped completion regression scenarios driven only through the CLI.

Completion must validate the active record's declared knowledge, math, and
Consumer projection without coupling to unrelated legacy notes, while full
``validate`` stays a strict whole-vault audit.
"""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

try:
    from tests.scoped_completion_support import ScopedProjectCase
except ImportError:  # direct test-directory execution
    from scoped_completion_support import ScopedProjectCase

USAGE_BODY = "# Use Demo\n\nRun `demo`.\n"
DEVELOPMENT_BODY = "# Develop Demo\n\nRun contributor checks.\n"
WORK_RECORD = "scope-demo/quick-task/fixture-task"


class RecordScopedCompletionTest(ScopedProjectCase):
    """Public check-completion / validate behavior for record-scoped gates."""

    def cli(self, *arguments: object, expected: int = 0) -> subprocess.CompletedProcess:
        result = self.run_cli(*arguments)
        self.assertEqual(
            expected,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def completion(self, item: Path, expected: int = 0) -> subprocess.CompletedProcess:
        return self.cli(
            "check-completion",
            "--project",
            self.project,
            "--work-item",
            item,
            expected=expected,
        )

    def seed_pair(self) -> None:
        """Publish a real valid Skill Pair under the fixture-task authority."""
        self.note("using.md", USAGE_BODY)
        self.note("developing.md", DEVELOPMENT_BODY)
        self.cli(
            "generate",
            "--project",
            self.project,
            "--work-record",
            WORK_RECORD,
        )

    def consumer_item(self) -> Path:
        return self.item(
            "consumer_interface_change: true\nrelated_notes: [using]\n"
        )

    def write_unmarked_math_note(self, name: str = "afm_report") -> Path:
        return self.note(
            f"{name}.md",
            "# AFM Report\n\n$$\nE = mc^2\n$$\n",
        )

    def write_malformed_note(self, name: str = "malformed_legacy") -> Path:
        path = self.project / "notes" / f"{name}.md"
        path.write_text(
            "---\ntype: reference\nstatus: archived\naudience: both\n"
            "artifact_role: knowledge\n---\n\n# Legacy\n",
            encoding="utf-8",
        )
        return path

    def test_unrelated_defects_do_not_block_noninterface_completion(self) -> None:
        self.write_unmarked_math_note()
        self.write_malformed_note()
        item = self.item()
        self.completion(item)

    def test_declared_unmarked_math_blocks_noninterface_completion(self) -> None:
        self.write_unmarked_math_note()
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [afm_report]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("afm_report", result.stderr)

    def test_declared_malformed_note_blocks_noninterface_completion(self) -> None:
        self.write_malformed_note()
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [malformed_legacy]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("malformed_legacy", result.stderr)

    def test_declared_expired_or_deprecated_knowledge_blocks_noninterface(self) -> None:
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [required]\n"
        )
        for metadata in ("stale_after: 2000-01-01\n", "usage_stale: true\n"):
            with self.subTest(metadata=metadata):
                self.note("required.md", metadata=metadata)
                result = self.completion(item, expected=2)
                self.assertIn("required", result.stderr)
        note = self.note("required.md")
        note.write_text(note.read_text().replace("status: stable", "status: deprecated"))
        result = self.completion(item, expected=2)
        self.assertIn("required", result.stderr)

    def test_missing_declared_note_blocks_noninterface_completion(self) -> None:
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [ghost]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("ghost", result.stderr)

    def test_escaping_declared_note_is_rejected(self) -> None:
        outside = self.project.parent / "outside.md"
        outside.write_text("# Outside\n", encoding="utf-8")
        item = self.item(
            "consumer_interface_change: false\nrelated_notes: [../outside]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("outside", result.stderr)

    def test_nonmath_record_completes_without_mathdocs_registry(self) -> None:
        shutil.rmtree(self.project / "mathdocs")
        item = self.item()
        self.completion(item)

    def test_full_validate_still_rejects_unrelated_defects(self) -> None:
        self.seed_pair()
        self.cli("validate", "--project", self.project)
        math_note = self.write_unmarked_math_note()
        result = self.cli("validate", "--project", self.project, expected=2)
        self.assertIn("afm_report", result.stderr)
        math_note.unlink()
        self.write_malformed_note()
        result = self.cli("validate", "--project", self.project, expected=2)
        self.assertIn("malformed_legacy", result.stderr)
        (self.project / "notes" / "malformed_legacy.md").unlink()
        self.cli("validate", "--project", self.project)

    def test_consumer_completion_ignores_unrelated_source_staleness(self) -> None:
        self.seed_pair()
        item = self.consumer_item()
        self.completion(item)
        developing = self.project / "notes" / "developing.md"
        developing.write_text(
            developing.read_text(encoding="utf-8") + "Unrelated follow-up.\n",
            encoding="utf-8",
        )
        self.completion(item)

    def test_consumer_completion_requires_stable_fresh_declared_note(self) -> None:
        self.seed_pair()
        item = self.consumer_item()
        self.completion(item)
        note = self.project / "notes" / "using.md"
        variants = (
            ("status: draft",
             "---\ntype: reference\nstatus: draft\naudience: both\n"
             "artifact_role: knowledge\n---\n\n" + USAGE_BODY),
            ("stale_after",
             "---\ntype: reference\nstatus: stable\naudience: both\n"
             "artifact_role: knowledge\nstale_after: '2020-01-01'\n---\n\n"
             + USAGE_BODY),
            ("usage_stale",
             "---\ntype: reference\nstatus: stable\naudience: both\n"
             "artifact_role: knowledge\nusage_stale: true\n---\n\n" + USAGE_BODY),
        )
        for label, frontmatter in variants:
            with self.subTest(defect=label):
                note.write_text(frontmatter, encoding="utf-8")
                result = self.completion(item, expected=2)
                self.assertIn("using", result.stderr)
                self.note("using.md", USAGE_BODY)
                self.completion(item)

    def test_consumer_completion_requires_current_declared_projection(self) -> None:
        self.seed_pair()
        item = self.consumer_item()
        using = self.project / "notes" / "using.md"
        using.write_text(
            using.read_text(encoding="utf-8") + "New interface behavior.\n",
            encoding="utf-8",
        )
        result = self.completion(item, expected=2)
        self.assertIn("using", result.stderr)
        self.cli("generate", "--project", self.project, "--work-record", WORK_RECORD)
        self.completion(item)
        (self.project / "skills").rename(self.project / "skills-pair")
        result = self.completion(item, expected=2)
        self.assertIn("Skill Pair", result.stderr)

    def test_consumer_completion_rejects_pair_byte_corruption(self) -> None:
        self.seed_pair()
        item = self.consumer_item()
        self.completion(item)
        development_skill = (
            self.project / "skills" / "scope-demo-development" / "SKILL.md"
        )
        development_skill.write_text(
            development_skill.read_text(encoding="utf-8") + "<!-- tampered -->\n",
            encoding="utf-8",
        )
        result = self.completion(item, expected=2)
        self.assertIn("development", result.stderr)

    def test_unrelated_unparseable_note_does_not_poison_evidence_link(self) -> None:
        pack = self.project / "evidence/2026-10-12-scope"
        pack.mkdir(parents=True)
        (pack / "MANIFEST.md").write_text("# Recorded evidence\n", encoding="utf-8")
        linked = self.note(
            "zzz-linked.md",
            metadata="evidence: [evidence/2026-10-12-scope/MANIFEST.md]\n",
        )
        (self.project / "notes/aaa-broken.md").write_text(
            "---\nstatus: stable\nstatus: draft\n---\n# Unrelated\n", encoding="utf-8"
        )
        item = self.item(
            "consumer_interface_change: false\n"
            "related_notes: [notes/zzz-linked.md]\n"
            "evidence_packs: [2026-10-12-scope]\n"
        )
        self.completion(item)
        linked.unlink()
        # A missing declared dependency must still reject the same record.
        result = self.completion(item, expected=2)
        self.assertIn("zzz-linked", result.stderr)

    def test_malformed_only_evidence_link_cannot_satisfy_pack(self) -> None:
        pack = self.project / "evidence/2026-10-12-scope"
        pack.mkdir(parents=True)
        (pack / "MANIFEST.md").write_text("# Recorded evidence\n", encoding="utf-8")
        # The only note naming the pack lacks the required type: discovery
        # must not accept it as the evidence link (full validate rejects it).
        (self.project / "notes/only-link.md").write_text(
            "---\nstatus: draft\n"
            "evidence: [evidence/2026-10-12-scope/MANIFEST.md]\n---\n# Link\n",
            encoding="utf-8",
        )
        item = self.item(
            "consumer_interface_change: false\n"
            "evidence_packs: [2026-10-12-scope]\n"
        )
        result = self.completion(item, expected=2)
        self.assertIn("2026-10-12-scope", result.stderr)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
