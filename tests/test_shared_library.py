from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skills.scripts.kosmic_shared_library import (
    LibraryError,
    build_catalog,
    generate_library,
    load_recipe_packet,
    migrate_assignments,
    resolve_library,
    install_shared_router,
    check_shared_router_installation,
    validate_library,
)


ROOT = """---
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
id: {domain}
status: stable
description: {domain} procedures
maintainers: [{maintainer}]
triggers: [{domain}]
aliases: []
---
# {title}
"""

TOPIC = """---
type: Skill Topic
id: {id}
domain: {domain}
audience: {audience}
status: stable
summary: {summary}
triggers: [{triggers}]
aliases: []
requires: {requires}
evidence: []
source_project: {source_project}
source_sha256: {source_sha256}
---
# {title}

{body}
"""


class SharedLibraryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.vault = Path(self.temp.name) / "memnotes"
        self.skills = self.vault / "Skills"
        self.skills.mkdir(parents=True)
        (self.skills / "SKILL.md").write_text(ROOT, encoding="utf-8")
        self.write_domain("abinit", "alice")
        self.write_domain("tb2j", "bob")
        self.write_topic(
            "abinit/usage/export-wavefunctions",
            summary="Export ABINIT wavefunctions",
            triggers="export wavefunctions",
            body="Run ABINIT export.",
        )
        self.write_topic(
            "abinit/usage/spin-orbit-conventions",
            summary="ABINIT spin orbit conventions",
            triggers="spin orbit conventions",
            body="Use ABINIT SOC conventions.",
        )
        self.write_topic(
            "tb2j/development/debug-exchange",
            audience="development",
            summary="Debug TB2J exchange from ABINIT",
            triggers="debug exchange parameters",
            requires="[abinit/usage/export-wavefunctions, abinit/usage/spin-orbit-conventions]",
            body="Debug TB2J exchange.",
        )

    def write_domain(self, domain: str, maintainer: str) -> None:
        path = self.skills / domain
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(
            DOMAIN.format(domain=domain, maintainer=maintainer, title=domain.upper()),
            encoding="utf-8",
        )

    def write_topic(
        self,
        topic_id: str,
        *,
        audience: str = "usage",
        status: str = "stable",
        summary: str = "summary",
        triggers: str = "trigger",
        requires: str = "[]",
        body: str = "Body.",
        source_project: str = "fixture",
        source_sha256: str = "a" * 64,
    ) -> Path:
        domain, _, slug = topic_id.split("/")
        path = self.skills / domain / audience / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            TOPIC.format(
                id=topic_id,
                domain=domain,
                audience=audience,
                summary=summary,
                triggers=triggers,
                requires=requires,
                source_project=source_project,
                source_sha256=source_sha256,
                title=slug,
                body=body,
            ).replace("status: stable", f"status: {status}", 1),
            encoding="utf-8",
        )
        return path

    def test_catalog_generation_is_deterministic_and_valid(self) -> None:
        first = generate_library(self.vault)
        snapshot = {p.relative_to(self.skills).as_posix(): p.read_bytes() for p in first}
        second = generate_library(self.vault)
        self.assertEqual(snapshot, {p.relative_to(self.skills).as_posix(): p.read_bytes() for p in second})
        validate_library(self.vault)
        catalog = json.loads((self.skills / ".kosmic/catalog.json").read_text())
        self.assertEqual([row["id"] for row in catalog["topics"]], sorted(row["id"] for row in catalog["topics"]))

    def test_unknown_dependency_and_cycle_fail(self) -> None:
        topic = self.skills / "tb2j/development/debug-exchange.md"
        topic.write_text(topic.read_text().replace("abinit/usage/export-wavefunctions", "missing/usage/topic"), encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "unknown dependency"):
            build_catalog(self.vault)
        topic.write_text(topic.read_text().replace("missing/usage/topic", "tb2j/development/debug-exchange"), encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "self-dependency|cycle"):
            build_catalog(self.vault)

    def test_usage_may_not_require_development(self) -> None:
        self.write_topic("abinit/usage/bad", requires="[tb2j/development/debug-exchange]")
        with self.assertRaisesRegex(LibraryError, "Usage topic.*Development"):
            build_catalog(self.vault)

    def test_stable_topic_may_not_require_nonstable_topic(self) -> None:
        self.write_topic("abinit/usage/draft-helper", status="draft")
        self.write_topic(
            "abinit/usage/stable-caller",
            requires="[abinit/usage/draft-helper]",
        )
        with self.assertRaisesRegex(LibraryError, "BROKEN_DEPENDENCY.*ineligible"):
            build_catalog(self.vault)

    def test_query_resolves_cross_domain_dependency_first(self) -> None:
        generate_library(self.vault)
        plan = resolve_library(
            self.vault,
            query="debug exchange parameters from ABINIT",
            role="development",
            project="tb2j",
        )
        ids = [row["id"] for row in plan["topics"]]
        self.assertEqual(ids[-1], "tb2j/development/debug-exchange")
        self.assertEqual(set(ids[:-1]), {"abinit/usage/export-wavefunctions", "abinit/usage/spin-orbit-conventions"})
        self.assertEqual(plan, resolve_library(self.vault, query="debug exchange parameters from ABINIT", role="development", project="tb2j"))
        packet = load_recipe_packet(self.vault, plan)
        self.assertIn("Debug TB2J exchange", packet)
        self.assertIn("Run ABINIT export", packet)

    def test_explicit_route_and_stale_plan(self) -> None:
        generate_library(self.vault)
        plan = resolve_library(self.vault, route="abinit/usage/export-wavefunctions", role="usage")
        self.assertEqual([row["id"] for row in plan["topics"]], ["abinit/usage/export-wavefunctions"])
        path = self.skills / "abinit/usage/export-wavefunctions.md"
        path.write_text(path.read_text() + "changed\n", encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "stale|hash"):
            load_recipe_packet(self.vault, plan)

    def test_domain_route_loads_only_domain_router(self) -> None:
        generate_library(self.vault)
        plan = resolve_library(self.vault, route="abinit", role="usage")
        self.assertEqual([row["id"] for row in plan["domains"]], ["abinit"])
        self.assertEqual(plan["topics"], [])
        packet = load_recipe_packet(self.vault, plan)
        self.assertIn("# ABINIT", packet)
        self.assertNotIn("Run ABINIT export", packet)

    def test_total_bytes_counts_exact_emitted_packet(self) -> None:
        generate_library(self.vault)
        plan = resolve_library(
            self.vault,
            route="abinit/usage/export-wavefunctions",
            role="usage",
        )
        packet = load_recipe_packet(self.vault, plan)
        self.assertEqual(plan["total_bytes"], len(packet.encode("utf-8")))
        with self.assertRaisesRegex(LibraryError, "BUDGET_EXCEEDED"):
            resolve_library(
                self.vault,
                route="abinit/usage/export-wavefunctions",
                role="usage",
                max_bytes=plan["total_bytes"] - 1,
            )

    def test_budget_overflow_returns_no_packet(self) -> None:
        generate_library(self.vault)
        with self.assertRaisesRegex(LibraryError, "BUDGET_EXCEEDED"):
            resolve_library(self.vault, route="tb2j/development/debug-exchange", role="development", max_bytes=10)

    def test_ambiguity_fails_closed(self) -> None:
        self.write_topic("abinit/usage/export-density", summary="Export density", triggers="export")
        self.write_topic("tb2j/usage/export-density", summary="Export density", triggers="export")
        generate_library(self.vault)
        with self.assertRaisesRegex(LibraryError, "AMBIGUOUS"):
            resolve_library(self.vault, query="export", role="usage")

    def test_generated_drift_fails(self) -> None:
        generate_library(self.vault)
        catalog = self.skills / ".kosmic/catalog.json"
        catalog.write_text("{}\n", encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "drift|catalog"):
            validate_library(self.vault)

    def test_migration_requires_complete_explicit_assignments(self) -> None:
        project = self.vault / "Projects/demo"
        source = project / "notes/one.md"
        source.parent.mkdir(parents=True)
        source.write_text("---\nevidence: []\n---\n# One\n\nDo one.\n", encoding="utf-8")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        refs = project / "skills/demo-usage/references"
        refs.mkdir(parents=True)
        (refs / "one.md").write_text(
            "---\naudience: usage\nsource: notes/one.md\nsource_sha256: "
            + digest
            + "\n---\n# One\n\nDo one.\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(LibraryError, "unassigned"):
            migrate_assignments(self.vault, project, {})
        report = migrate_assignments(self.vault, project, {"demo-usage/references/one.md": "abinit/usage/one"})
        self.assertEqual(report["migrations"][0]["target"], "abinit/usage/one")
        self.assertTrue((self.skills / "abinit/usage/one.md").is_file())

    def test_migration_rejects_audience_reclassification(self) -> None:
        project = self.vault / "Projects/demo"
        source = project / "notes/one.md"
        source.parent.mkdir(parents=True)
        source.write_text("---\nevidence: []\n---\n# One\n", encoding="utf-8")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        reference = project / "skills/demo-development/references/one.md"
        reference.parent.mkdir(parents=True)
        reference.write_text(
            "---\naudience: development\nsource: notes/one.md\nsource_sha256: "
            + digest
            + "\n---\n# One\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(LibraryError, "audience.*does not permit"):
            migrate_assignments(
                self.vault,
                project,
                {"demo-development/references/one.md": "abinit/usage/one"},
            )

    def test_migration_failure_preserves_prior_library(self) -> None:
        generate_library(self.vault)
        before = (self.skills / ".kosmic/catalog.json").read_bytes()
        project = self.vault / "Projects/demo"
        source = project / "notes/one.md"
        source.parent.mkdir(parents=True)
        source.write_text("---\nevidence: []\n---\n# One\n", encoding="utf-8")
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        reference = project / "skills/demo-usage/references/one.md"
        reference.parent.mkdir(parents=True)
        reference.write_text(
            "---\naudience: usage\nsource: notes/one.md\nsource_sha256: "
            + digest
            + "\n---\n# One\n",
            encoding="utf-8",
        )
        with mock.patch(
            "skills.scripts.kosmic_shared_library._generated_payloads",
            side_effect=OSError("generation failed"),
        ):
            with self.assertRaises(OSError):
                migrate_assignments(
                    self.vault,
                    project,
                    {"demo-usage/references/one.md": "abinit/usage/one"},
                )
        self.assertEqual((self.skills / ".kosmic/catalog.json").read_bytes(), before)
        self.assertFalse((self.skills / "abinit/usage/one.md").exists())

    def test_shared_router_install_is_atomic_and_removes_managed_pairs(self) -> None:
        generate_library(self.vault)
        destination = Path(self.temp.name) / "agent-skills"
        old = destination / "demo-usage"
        old.mkdir(parents=True)
        (old / ".kosmic-projection.json").write_text('{"project_id":"demo"}\n', encoding="utf-8")
        unmanaged = destination / "personal"
        unmanaged.mkdir()
        install_shared_router(self.vault, destination)
        self.assertFalse(old.exists())
        self.assertTrue(unmanaged.exists())
        self.assertEqual(check_shared_router_installation(self.vault, destination), destination / "memnotes-skills")

    def test_shared_router_collision_preserves_inventory(self) -> None:
        generate_library(self.vault)
        destination = Path(self.temp.name) / "agent-skills"
        collision = destination / "memnotes-skills"
        collision.mkdir(parents=True)
        (collision / "personal.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "collision"):
            install_shared_router(self.vault, destination)
        self.assertEqual((collision / "personal.txt").read_text(), "keep")


    def test_router_contains_executable_invocation_and_budget_policy(self) -> None:
        generate_library(self.vault)
        destination = Path(self.temp.name) / "agent-skills"
        installed = install_shared_router(self.vault, destination)
        body = (installed / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("python3 ", body)
        self.assertIn("kosmic_project_skills.py", body)
        self.assertIn("32768 packet bytes, 4 domains, 8 topics", body)

    def test_router_replace_failure_preserves_previous_router(self) -> None:
        generate_library(self.vault)
        destination_root = Path(self.temp.name) / "agent-skills"
        destination = install_shared_router(self.vault, destination_root)
        marker = destination / "keep.txt"
        marker.write_text("prior", encoding="utf-8")
        real_replace = __import__("os").replace

        def fail_first_router_move(source: Path, target: Path) -> None:
            if Path(source) == destination:
                raise OSError("replace failed")
            real_replace(source, target)

        with mock.patch(
            "skills.scripts.kosmic_shared_library.os.replace",
            side_effect=fail_first_router_move,
        ):
            with self.assertRaisesRegex(OSError, "replace failed"):
                install_shared_router(self.vault, destination_root)
        self.assertEqual(marker.read_text(encoding="utf-8"), "prior")
    def test_generation_rollback_preserves_previous_artifacts(self) -> None:
        generate_library(self.vault)
        before = (self.skills / ".kosmic/catalog.json").read_bytes()
        with mock.patch("skills.scripts.kosmic_shared_library._replace_generated", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                generate_library(self.vault)
        self.assertEqual((self.skills / ".kosmic/catalog.json").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
