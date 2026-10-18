"""Story005 FR010: consumer regression through the existing generate_library flow.

Real notes, real pair publisher, real library publisher, real consumer
(resolve_library + load_recipe_packet). No standalone helper API, no mocked
publication, no wording/copy assertions.
"""

from __future__ import annotations

import hashlib
import json
import re
import tempfile
import unittest
from unittest import mock
from pathlib import Path

from skills.scripts.kosmic_project_skills import generate as generate_pair, load_project
from skills.scripts.kosmic_shared_library import (
    LibraryError,
    generate_library,
    load_recipe_packet,
    migrate_assignments,
    resolve_library,
    validate_library,
)


ROUTER = """---
type: Shared Skill Router
id: memnotes-skills
status: stable
description: Shared technical procedures
max_packet_bytes: 32768
max_domains: 4
max_topics: 8
---
# Shared Skills
"""

DOMAIN = """---
type: Domain Skill
id: kosmic
status: stable
description: kosmic procedures
maintainers: [hexu]
triggers: [kosmic]
aliases: []
---
# KOSMIC
"""

TOPIC = """---
type: Domain Topic
id: {id}
domain: {domain}
audience: {audience}
artifact_role: knowledge
status: stable
summary: {summary}
triggers: [{triggers}]
aliases: []
requires_procedures: []
governed_by: []
uses_knowledge: {uses_knowledge}
supported_by: []
supersedes: []
evidence: []
source_project: {source_project}
source_sha256: {source_sha256}
---
# {slug}

{body}
"""


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


class SkillResourcePublicationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.vault = Path(self.temp.name) / "vault"
        self.skills = self.vault / "Skills"
        (self.skills / "kosmic" / "usage").mkdir(parents=True)
        (self.skills / "kosmic" / "development").mkdir()
        (self.skills / "SKILL.md").write_text(ROUTER, encoding="utf-8")
        (self.skills / "kosmic" / "SKILL.md").write_text(DOMAIN, encoding="utf-8")
        self.project = self.vault / "Projects" / "demo"
        (self.project / "notes").mkdir(parents=True)
        (self.project / "notes" / "index.md").write_text(
            "---\nokf_version: \"0.2\"\n---\n\n# Project Knowledge\n",
            encoding="utf-8",
        )
        mathdocs = self.project / "mathdocs"
        mathdocs.mkdir()
        (mathdocs / "index.md").write_text(
            "# Math Derivations\n\n"
            "| Derivation | Status | Result summary |\n"
            "|------------|--------|----------------|\n",
            encoding="utf-8",
        )
        (self.project / "ProjectEntry.md").write_text(
            "---\nproject_id: demo\nworking_state: working-tree\n---\n\n# Demo\n",
            encoding="utf-8",
        )
        record = self.project / "specs" / "quick-tasks" / "fixture-task.md"
        record.parent.mkdir(parents=True)
        record.write_text(
            "---\nproject_id: demo\nrecord_kind: quick-task\nlocal_id: fixture-task\n"
            "subproject_id: null\nstatus: approved\n---\n\n# Fixture Task\n",
            encoding="utf-8",
        )
        self.work_record = "demo/quick-task/fixture-task"
        self.note_v1 = (
            "---\ntype: Project Knowledge\nstatus: stable\naudience: usage\n---\n\n"
            "# Demo guide\n\nOriginal published guidance.\n"
        )
        self.note_path = self.project / "notes" / "guide.md"
        self.note_path.write_text(self.note_v1, encoding="utf-8")
        # Approved prior publication: pair from the publisher, topic pinned to
        # the note bytes the pair was generated from.
        generate_pair(load_project(self.project), work_record=self.work_record)
        prior_manifest = json.loads(
            (self.project / "skills" / "demo-usage" / ".kosmic-projection.json")
            .read_text(encoding="utf-8")
        )
        self.prior_pin = prior_manifest["sources"][0]["sha256"]
        self.topic_id = "kosmic/usage/demo-guide"
        self.native_id = "kosmic/usage/native-reference"
        self.write_topic(self.topic_id, source_project="demo", source_sha256=self.prior_pin,
                         body="Original published guidance.")
        self.native_path = self.write_topic(self.native_id, source_project="native",
                                            source_sha256="empty", body="Native reference body.")
        generate_library(self.vault, work_record=self.work_record)

    def write_topic(self, topic_id: str, *, source_project: str, source_sha256: str,
                    body: str, summary: str = "Demo guide", triggers: str = "demo guide") -> Path:
        domain, audience, slug = topic_id.split("/")
        path = self.skills / domain / audience / f"{slug}.md"
        path.write_text(
            TOPIC.format(id=topic_id, domain=domain, audience=audience,
                         source_project=source_project, source_sha256=source_sha256,
                         slug=slug, body=body, summary=summary, triggers=triggers,
                         uses_knowledge="[]"),
            encoding="utf-8",
        )
        return path

    def consumer_packet(self, route: str) -> str:
        return load_recipe_packet(self.vault, resolve_library(self.vault, route=route))

    def catalog_row(self, topic_id: str) -> dict | None:
        catalog = json.loads(
            (self.skills / ".kosmic" / "catalog.json").read_text(encoding="utf-8")
        )
        return next((row for row in catalog["topics"] if row["id"] == topic_id), None)

    def snapshot(self, root: Path) -> dict[str, bytes]:
        return {
            path.relative_to(root).as_posix(): path.read_bytes()
            for path in sorted(root.rglob("*")) if path.is_file()
        }

    def test_refresh_syncs_note_and_consumer_loads_final(self) -> None:
        note_v2 = self.note_v1.replace("Original published guidance.", "Final corrected guidance.")
        self.note_path.write_text(note_v2, encoding="utf-8")
        generate_library(self.vault, work_record=self.work_record)
        note_text = self.note_path.read_text(encoding="utf-8")
        self.assertIn("skill_resources: [kosmic/usage/demo-guide]", note_text)
        self.assertNotIn("updated:", note_text)
        final_hash = sha(self.note_path.read_bytes())
        packet = self.consumer_packet(self.topic_id)
        self.assertIn("Final corrected guidance.", packet)
        self.assertIn(f"topic:{self.topic_id}", packet)
        self.assertNotIn("Original published guidance.", packet)
        row = self.catalog_row(self.topic_id)
        self.assertEqual(row["source_sha256"], final_hash)
        pair_reference = self.project / "skills" / "demo-usage" / "references" / "guide.md"
        self.assertIn("Final corrected guidance.", pair_reference.read_text(encoding="utf-8"))
        self.assertIn(f"source_sha256: {final_hash}", pair_reference.read_text(encoding="utf-8"))
        validate_library(self.vault)
        native_text = self.native_path.read_text(encoding="utf-8")
        self.assertIn("source_project: native", native_text)
        self.assertIn("Native reference body.", native_text)

    def test_explicit_source_survives_pair_first_republication(self) -> None:
        """User edits note, regenerates the Project pair BEFORE the library
        refresh: the prior pair pins are lost, so the persisted explicit
        topic `source:` identity maps. Consumer loads the final body/hash
        under the same stable ID, source line retained."""
        # setUp's approved publication already persisted source: notes/guide.md.
        topic_file = self.skills / "kosmic" / "usage" / "demo-guide.md"
        self.assertIn("source: notes/guide.md", topic_file.read_text(encoding="utf-8"))
        # Semantic note edit + ordinary Project pair regeneration FIRST.
        note_v2 = self.note_v1.replace(
            "Original published guidance.", "Final corrected guidance body."
        )
        self.note_path.write_text(note_v2, encoding="utf-8")
        generate_pair(load_project(self.project), work_record=self.work_record)
        # Library refresh must still map via the persisted explicit source.
        generate_library(self.vault, work_record=self.work_record)
        final_hash = sha(self.note_path.read_bytes())
        text = topic_file.read_text(encoding="utf-8")
        self.assertIn("source: notes/guide.md", text)
        self.assertIn(f"source_sha256: {final_hash}", text)
        row = self.catalog_row(self.topic_id)
        self.assertEqual(row["source_sha256"], final_hash)
        packet = self.consumer_packet(self.topic_id)
        self.assertIn("Final corrected guidance body.", packet)
        self.assertNotIn("Original published guidance.", packet)
        self.assertNotIn("updated:", self.note_path.read_text(encoding="utf-8"))
        validate_library(self.vault)

    def test_lost_pin_recovers_via_actual_use_backlink(self) -> None:
        """Legacy published topic: no explicit source, pin matches neither
        current note nor regenerated pair manifests, but the owning note's
        actual-use backlink names this already-published topic ID. The
        ordinary flow must rebuild final content, never the old body, and
        persist the resolved identity."""
        topic_file = self.skills / "kosmic" / "usage" / "demo-guide.md"
        original_pin = re.search(
            r"source_sha256: ([0-9a-f]{64})",
            topic_file.read_text(encoding="utf-8"),
        ).group(1)
        legacy = "\n".join(
            line for line in topic_file.read_text(encoding="utf-8").splitlines()
            if not line.startswith("source:")
        )
        legacy = re.sub(
            r"source_sha256: [0-9a-f]{64}", f"source_sha256: {'e' * 64}", legacy
        ) + "\n"
        topic_file.write_text(legacy, encoding="utf-8")
        self.assertNotIn(original_pin, legacy)
        self.assertIn(
            "skill_resources: [kosmic/usage/demo-guide]",
            self.note_path.read_text(encoding="utf-8"),
        )
        # Semantic body edit that KEEPS the note's frontmatter actual-use
        # backlink intact (frontmatter is never reset by the edit).
        note_v2 = self.note_path.read_text(encoding="utf-8").replace(
            "Original published guidance.", "Backlink-recovered final guidance body."
        )
        self.note_path.write_text(note_v2, encoding="utf-8")
        self.assertIn(
            "skill_resources: [kosmic/usage/demo-guide]",
            self.note_path.read_text(encoding="utf-8"),
        )
        generate_library(self.vault, work_record=self.work_record)
        final_hash = sha(self.note_path.read_bytes())
        text = topic_file.read_text(encoding="utf-8")
        self.assertIn("source: notes/guide.md", text)
        self.assertIn(f"source_sha256: {final_hash}", text)
        packet = self.consumer_packet(self.topic_id)
        self.assertIn("Backlink-recovered final guidance body.", packet)
        self.assertNotIn("Original published guidance.", packet)
        self.assertEqual(self.catalog_row(self.topic_id)["source_sha256"], final_hash)
        validate_library(self.vault)

    def test_ambiguous_backlinks_fail_closed_without_invention(self) -> None:
        legacy = "\n".join(
            line for line in (self.skills / "kosmic" / "usage" / "demo-guide.md")
            .read_text(encoding="utf-8").splitlines()
            if not line.startswith("source:")
        )
        legacy = re.sub(
            r"source_sha256: [0-9a-f]{64}", f"source_sha256: {'e' * 64}", legacy
        ) + "\n"
        (self.skills / "kosmic" / "usage" / "demo-guide.md").write_text(legacy, encoding="utf-8")
        second = self.project / "notes" / "second.md"
        second.write_text(
            "---\ntype: Project Knowledge\nstatus: stable\naudience: usage\n"
            "skill_resources: [kosmic/usage/demo-guide]\n---\n\n# Second\n\nOther body.\n",
            encoding="utf-8",
        )
        before_skills = self.snapshot(self.skills)
        before_project = self.snapshot(self.project)
        with self.assertRaises(LibraryError):
            generate_library(self.vault, work_record=self.work_record)
        self.assertEqual(self.snapshot(self.skills), before_skills)
        self.assertEqual(self.snapshot(self.project), before_project)

    def test_removal_clears_id_and_syncs_actual_use_to_empty(self) -> None:
        (self.skills / "kosmic" / "usage" / "demo-guide.md").unlink()
        generate_library(self.vault, work_record=self.work_record)
        self.assertIsNone(self.catalog_row(self.topic_id))
        with self.assertRaises(LibraryError):
            resolve_library(self.vault, route=self.topic_id)
        note_text = self.note_path.read_text(encoding="utf-8")
        self.assertIn("skill_resources: []", note_text)
        self.assertNotIn(self.topic_id, note_text)
        validate_library(self.vault)
        self.assertIn("Native reference body.", self.consumer_packet(self.native_id))

    def test_new_topic_first_publication_maps_by_unique_current_hash(self) -> None:
        note_v2 = self.note_v1.replace("Original published guidance.", "Final corrected guidance.")
        self.note_path.write_text(note_v2, encoding="utf-8")
        candidate_pin = sha(note_v2.encode("utf-8"))
        self.write_topic("kosmic/usage/demo-guide", source_project="demo",
                         source_sha256=candidate_pin, body="Final corrected guidance.")
        generate_library(self.vault, work_record=self.work_record)
        final_hash = sha(self.note_path.read_bytes())
        self.assertNotEqual(final_hash, candidate_pin)  # bookkeeping changed the bytes
        note_text = self.note_path.read_text(encoding="utf-8")
        self.assertIn("skill_resources: [kosmic/usage/demo-guide]", note_text)
        row = self.catalog_row(self.topic_id)
        self.assertEqual(row["source_sha256"], final_hash)
        self.assertIn("Final corrected guidance.", self.consumer_packet(self.topic_id))

    def test_unstable_note_with_live_topic_fails_closed_and_restores(self) -> None:
        note_draft = self.note_v1.replace("status: stable", "status: draft")
        self.note_path.write_text(note_draft, encoding="utf-8")
        before_library = self.snapshot(self.skills)
        before_project = self.snapshot(self.project)
        with self.assertRaises(LibraryError):
            generate_library(self.vault, work_record=self.work_record)
        self.assertEqual(self.snapshot(self.skills), before_library)
        self.assertEqual(self.snapshot(self.project), before_project)
        note_text = self.note_path.read_text(encoding="utf-8")
        self.assertNotIn("skill_resources", note_text)

    def test_unrelated_notes_and_native_topics_stay_untouched(self) -> None:
        unrelated = self.project / "notes" / "other.md"
        unrelated.write_text(
            "---\ntype: Project Knowledge\nstatus: stable\naudience: usage\n---\n\n"
            "# Other\n\nUnrelated body.\n",
            encoding="utf-8",
        )
        before = self.snapshot(self.skills)
        before_note = unrelated.read_bytes()
        generate_library(self.vault, work_record=self.work_record)
        self.assertEqual(unrelated.read_bytes(), before_note)
        self.assertIn("Native reference body.", self.native_path.read_text(encoding="utf-8"))
        self.assertNotIn("skill_resources", unrelated.read_text(encoding="utf-8"))
        after = self.snapshot(self.skills)
        self.assertEqual(after.pop(".kosmic/catalog.json"), before.pop(".kosmic/catalog.json"))


    def migration_fixture(self) -> tuple[Path, dict]:
        """Fixture on the REAL current pair reference (the approved publisher's
        own artifact), never a fabricated second reference tree."""
        reference = self.project / "skills" / "demo-usage" / "references" / "guide.md"
        assignments = {
            "demo-usage/references/guide.md": {
                "target_id": self.topic_id,
                "artifact_role": "knowledge",
                "requires_procedures": [],
                "governed_by": [],
                "uses_knowledge": [],
                "supported_by": [],
                "supersedes": [],
            }
        }
        return reference, assignments

    def test_first_migration_syncs_actual_use_and_final_source_pins(self) -> None:
        reference, assignments = self.migration_fixture()
        self.assertTrue(reference.is_file())  # real publisher artifact under migration
        # Clean slate: retire the setup topic so migration is the first publication.
        (self.skills / "kosmic" / "usage" / "demo-guide.md").unlink()
        # Change the note body first; the approved generate-library flow must
        # re-pin the pair to the final bytes so the migration renders the
        # final source, never the pre-edit body.
        note_v2 = self.note_v1.replace(
            "Original published guidance.", "Migration-corrected final guidance body."
        )
        self.note_path.write_text(note_v2, encoding="utf-8")
        generate_library(self.vault, work_record=self.work_record)
        self.assertIn(
            "Migration-corrected final guidance body.",
            reference.read_text(encoding="utf-8"),
        )
        result = migrate_assignments(
            self.vault, self.project, assignments, work_record=self.work_record
        )
        final_hash = sha(self.note_path.read_bytes())
        note_text = self.note_path.read_text(encoding="utf-8")
        self.assertIn("skill_resources: [kosmic/usage/demo-guide]", note_text)
        row = self.catalog_row(self.topic_id)
        self.assertEqual(row["source_sha256"], final_hash)
        self.assertEqual(result["migrations"][0]["source_sha256"], final_hash)
        packet = self.consumer_packet(self.topic_id)
        self.assertIn("Migration-corrected final guidance body.", packet)
        self.assertNotIn("Original published guidance.", packet)
        validate_library(self.vault)
        # Historical publisher artifact stays untouched (source line only).
        self.assertIn("source: notes/guide.md", reference.read_text(encoding="utf-8"))

    def test_post_publication_validation_failure_restores_published_library(self) -> None:
        """A final published-validation failure must restore the ORIGINAL
        published library from the retained backup — never bless the staged
        tree against reverted note bytes. Fault is injected at the existing
        transactional boundary: the REAL validate_library still runs against
        the published vault, then raises for that vault only (no call-count,
        no production guard)."""
        import skills.scripts.kosmic_shared_library as library_module

        before_skills = self.snapshot(self.skills)
        pre_call_pin = self.catalog_row(self.topic_id)["source_sha256"]
        note_v2 = self.note_path.read_text(encoding="utf-8").replace(
            "Original published guidance.", "Final corrected guidance body."
        )
        self.note_path.write_text(note_v2, encoding="utf-8")
        before_project = self.snapshot(self.project)
        real_validation = library_module.validate_library

        def published_vault_fails(vault_path: Path, *args, **kwargs) -> None:
            real_validation(vault_path, *args, **kwargs)
            if Path(vault_path).resolve() == self.vault.resolve():
                raise LibraryError("post-publication validation fault (test)")

        with mock.patch.object(
            library_module, "validate_library", published_vault_fails
        ):
            with self.assertRaises(LibraryError):
                generate_library(self.vault, work_record=self.work_record)
        self.assertEqual(self.snapshot(self.skills), before_skills)
        self.assertEqual(self.snapshot(self.project), before_project)
        packet = self.consumer_packet(self.topic_id)
        self.assertIn("Original published guidance.", packet)
        self.assertNotIn("Final corrected guidance body.", packet)
        self.assertEqual(self.catalog_row(self.topic_id)["source_sha256"], pre_call_pin)
        self.assertNotIn("updated:", self.note_path.read_text(encoding="utf-8"))

    def test_sync_preserves_unrelated_actual_use_ids(self) -> None:
        """Actual-use is per-note state: reconciling OUR topic IDs must not
        discard stable external IDs the note already declares. When our own
        topic is removed, the external stable ID survives."""
        note = self.note_path.read_text(encoding="utf-8")
        self.assertIn(
            "skill_resources: [kosmic/usage/demo-guide]", note
        )
        note = note.replace(
            "skill_resources: [kosmic/usage/demo-guide]",
            "skill_resources: [kosmic/usage/demo-guide, kosmic/usage/native-reference]",
            1,
        )
        self.note_path.write_text(note, encoding="utf-8")
        # Approved removal of OUR topic.
        (self.skills / "kosmic" / "usage" / "demo-guide.md").unlink()
        generate_library(self.vault, work_record=self.work_record)
        self.assertIsNone(self.catalog_row(self.topic_id))
        note = self.note_path.read_text(encoding="utf-8")
        self.assertIn("kosmic/usage/native-reference", note)
        self.assertNotIn("kosmic/usage/demo-guide", note)

    def test_usage_topic_refuses_development_only_source(self) -> None:
        """An existing usage topic whose persisted source note has become
        development-only must fail closed (audience partition is authority),
        not publish development-only body to usage consumers."""
        before_skills = self.snapshot(self.skills)
        # Separate valid stable usage anchor keeps the Project pair
        # publishable after the TARGET note flips to development-only; the
        # anchor is unmapped and unrelated, so the audience authority check
        # is what must refuse the usage topic's development-only source.
        (self.project / "notes" / "anchor.md").write_text(
            "---\ntype: Project Knowledge\nstatus: stable\naudience: usage\n---\n\n"
            "# Anchor\n\nStable usage anchor guidance.\n",
            encoding="utf-8",
        )
        note_dev_only = self.note_path.read_text(encoding="utf-8").replace(
            "audience: usage", "audience: development"
        ).replace(
            "Original published guidance.", "Internal contributor-only guidance body."
        )
        self.note_path.write_text(note_dev_only, encoding="utf-8")
        before_project = self.snapshot(self.project)
        with self.assertRaises(LibraryError):
            generate_library(self.vault, work_record=self.work_record)
        self.assertEqual(self.snapshot(self.skills), before_skills)
        self.assertEqual(self.snapshot(self.project), before_project)
        packet = self.consumer_packet(self.topic_id)
        self.assertIn("Original published guidance.", packet)
        self.assertNotIn("Internal contributor-only guidance body.", packet)
        self.assertNotIn("updated:", self.note_path.read_text(encoding="utf-8"))

    def test_both_audience_note_serves_usage_and_development_topics(self) -> None:
        """A 'both' note feeds an EXISTING usage topic and an EXISTING
        development topic through the ordinary flow: both consumers load the
        final body, pins match final raw bytes, identity/source persisted,
        and the note audience is never remapped."""
        note_both = self.note_path.read_text(encoding="utf-8").replace(
            "audience: usage", "audience: both"
        )
        self.note_path.write_text(note_both, encoding="utf-8")
        self.write_topic(
            "kosmic/development/demo-guide",
            source_project="demo",
            source_sha256=sha(self.note_path.read_bytes()),
            body="Original published guidance.",
        )
        generate_library(self.vault, work_record=self.work_record)
        corrected = self.note_path.read_text(encoding="utf-8").replace(
            "Original published guidance.", "Dual-audience corrected guidance body."
        )
        self.note_path.write_text(corrected, encoding="utf-8")
        generate_library(self.vault, work_record=self.work_record)
        final_hash = sha(self.note_path.read_bytes())
        for route in ("kosmic/usage/demo-guide", "kosmic/development/demo-guide"):
            packet = self.consumer_packet(route)
            self.assertIn("Dual-audience corrected guidance body.", packet)
            self.assertNotIn("Original published guidance.", packet)
            row = self.catalog_row(route)
            self.assertEqual(row["source_sha256"], final_hash)
        for topic_id in (
            "kosmic/usage/demo-guide",
            "kosmic/development/demo-guide",
        ):
            domain, audience, slug = topic_id.split("/")
            text = (self.skills / domain / audience / f"{slug}.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("source: notes/guide.md", text)
            self.assertIn(f"source_sha256: {final_hash}", text)
        self.assertIn("audience: both", self.note_path.read_text(encoding="utf-8"))
        validate_library(self.vault)

    def test_stage_graph_failure_rolls_back_real_mutations(self) -> None:
        """Post-mutation consumer rollback: note sync and Project pair
        regeneration succeed, then the staged library graph fails
        (relationship to a missing topic). Note, pair, and library must be
        byte-identical to the pre-call state — no false actual-use ID, no
        `updated` bump, caller-provided topic input untouched."""
        bad_topic = self.skills / "kosmic" / "usage" / "extra-topic.md"
        bad_topic.write_text(
            TOPIC.format(
                id="kosmic/usage/extra-topic", domain="kosmic", audience="usage",
                artifact_role="knowledge", summary="Extra topic", triggers="extra",
                requires_procedures="[]", uses_knowledge="[kosmic/usage/missing]",
                source_project="demo", source_sha256=sha(self.note_path.read_bytes()),
                slug="extra-topic", body="Extra body.",
            ),
            encoding="utf-8",
        )
        before_skills = self.snapshot(self.skills)
        before_project = self.snapshot(self.project)
        with self.assertRaises(LibraryError):
            generate_library(self.vault, work_record=self.work_record)
        self.assertEqual(self.snapshot(self.skills), before_skills)
        self.assertEqual(self.snapshot(self.project), before_project)
        note_text = self.note_path.read_text(encoding="utf-8")
        self.assertIn("skill_resources: [kosmic/usage/demo-guide]", note_text)
        self.assertNotIn("kosmic/usage/extra-topic", note_text)
        self.assertNotIn("updated:", note_text)
        self.assertEqual(
            bad_topic.read_text(encoding="utf-8"),
            TOPIC.format(
                id="kosmic/usage/extra-topic", domain="kosmic", audience="usage",
                artifact_role="knowledge", summary="Extra topic", triggers="extra",
                requires_procedures="[]", uses_knowledge="[kosmic/usage/missing]",
                source_project="demo", source_sha256=sha(self.note_path.read_bytes()),
                slug="extra-topic", body="Extra body.",
            ),
        )

    def test_migration_hook_failure_restores_pre_migration_library(self) -> None:
        # Two stable notes with IDENTICAL bytes make the pin ambiguous; the
        # hook must fail closed after migration publish and restore the
        # pre-migration library plus note bytes exactly.
        identical = self.note_path.read_text(encoding="utf-8")
        other = self.project / "notes" / "other.md"
        other.write_text(identical, encoding="utf-8")
        _reference, assignments = self.migration_fixture()
        before_library = self.snapshot(self.skills)
        before_project = self.snapshot(self.project)
        with self.assertRaises(LibraryError):
            migrate_assignments(
                self.vault, self.project, assignments, work_record=self.work_record
            )
        self.assertEqual(self.snapshot(self.skills), before_library)
        self.assertEqual(self.snapshot(self.project), before_project)


if __name__ == "__main__":
    unittest.main()
