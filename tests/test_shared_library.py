from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skills.scripts.kosmic_shared_library import (
    LibraryError,
    _validate_routine_edges,
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
type: Domain Topic
id: {id}
domain: {domain}
audience: {audience}
artifact_role: {artifact_role}
status: stable
summary: {summary}
triggers: [{triggers}]
outcome: {outcome}
aliases: []
requires_procedures: {requires_procedures}
governed_by: {governed_by}
uses_knowledge: {uses_knowledge}
supported_by: {supported_by}
uses_routines: {uses_routines}
supersedes: {supersedes}
observed_on: {observed_on}
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
        governing_project = self.vault / "Projects" / "demo-proj"
        governing_project.mkdir(parents=True)
        (governing_project / "ProjectEntry.md").write_text("---\nproject_id: demo-proj\nworking_state: working-tree\n---\n# Demo\n", encoding="utf-8")
        quick_task = governing_project / "specs" / "quick-tasks" / "library.md"
        quick_task.parent.mkdir(parents=True)
        quick_task.write_text("---\nproject_id: demo-proj\nrecord_kind: quick-task\nlocal_id: shared-library\nsubproject_id: null\nstatus: approved\n---\n# Shared Library Tests\n", encoding="utf-8")
        self.work_record = "demo-proj/quick-task/shared-library"
        (self.skills / "SKILL.md").write_text(ROOT, encoding="utf-8")
        self.write_domain("abinit", "alice")
        self.write_domain("tb2j", "bob")
        self.write_domain("kosmic", "hexu")
        self.write_topic(
            "kosmic/development/atomic-skill-publication",
            audience="development",
            artifact_role="knowledge",
            body="Atomic publication preserves one complete visible tree.",
        )
        self.write_topic(
            "abinit/usage/export-wavefunctions",
            summary="Export ABINIT wavefunctions",
            triggers="export wavefunctions",
            artifact_role="knowledge",
            body="ABINIT wavefunction export reference.",
        )
        self.write_topic(
            "abinit/usage/spin-orbit-conventions",
            summary="ABINIT spin orbit conventions",
            triggers="spin orbit conventions",
            artifact_role="knowledge",
            body="ABINIT SOC conventions.",
        )
        self.write_topic(
            "tb2j/development/debug-exchange",
            audience="development",
            summary="Debug TB2J exchange from ABINIT",
            triggers="debug exchange parameters",
            artifact_role="procedure",
            uses_knowledge="[abinit/usage/export-wavefunctions, abinit/usage/spin-orbit-conventions]",
            body=self.procedure_body("Debug TB2J exchange."),
        )

    def write_domain(self, domain: str, maintainer: str) -> None:
        path = self.skills / domain
        path.mkdir(parents=True)
        (path / "SKILL.md").write_text(
            DOMAIN.format(domain=domain, maintainer=maintainer, title=domain.upper()),
            encoding="utf-8",
        )

    @staticmethod
    def procedure_body(step: str = "Perform the task.") -> str:
        return (
            "## When to use\n\nUse for this task.\n\n"
            "## Preconditions\n\nRequired inputs exist.\n\n"
            f"## Procedure\n\n1. {step}\n\n"
            "## Decisions and branches\n\nStop when prerequisites are missing.\n\n"
            "## Verification\n\nVerify the observable result.\n\n"
            "## Failure handling\n\nReport the failing step.\n\n"
            "## References\n\nUse the declared relationships.\n"
        )

    @staticmethod
    def migration_assignment(target_id: str, artifact_role: str = "knowledge") -> dict[str, object]:
        return {
            "target_id": target_id,
            "artifact_role": artifact_role,
            "requires_procedures": [],
            "governed_by": [],
            "uses_knowledge": [],
            "supported_by": [],
            "supersedes": [],
        }

    def write_topic(
        self,
        topic_id: str,
        *,
        audience: str = "usage",
        status: str = "stable",
        summary: str = "summary",
        triggers: str = "trigger",
        artifact_role: str = "knowledge",
        outcome: str = "",
        requires_procedures: str = "[]",
        governed_by: str = "[]",
        uses_knowledge: str = "[]",
        supported_by: str = "[]",
        uses_routines: str = "[]",
        supersedes: str = "[]",
        observed_on: str = "",
        body: str = "Body.",
        source_project: str = "fixture",
        source_sha256: str = "a" * 64,
    ) -> Path:
        domain, _, slug = topic_id.split("/")
        path = self.skills / domain / audience / f"{slug}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            TOPIC.format(
                id=topic_id, domain=domain, audience=audience,
                artifact_role=artifact_role, summary=summary, triggers=triggers,
                outcome=outcome or ("Complete the task." if artifact_role == "procedure" else ""),
                requires_procedures=requires_procedures, governed_by=governed_by,
                uses_knowledge=uses_knowledge, supported_by=supported_by,
                supersedes=supersedes, observed_on=observed_on,
                uses_routines=uses_routines,
                source_project=source_project, source_sha256=source_sha256,
                title=slug, body=body,
            ).replace("status: stable", f"status: {status}", 1),
            encoding="utf-8",
        )
        return path

    def test_procedure_packet_carries_hash_pinned_routine(self) -> None:
        source_root = self.vault.parent / "fixture-source/skills/scripts"
        source_root.mkdir(parents=True)
        repo_root = source_root.parent.parent
        (repo_root / "tests").mkdir()
        (repo_root / "tests/test_ops.py").write_text(
            "def test_publish():\n"
            "    from pathlib import Path\n"
            "    from tempfile import TemporaryDirectory\n"
            "    from ops import publish\n"
            "    with TemporaryDirectory() as directory:\n"
            "        source = Path(directory) / 'source'\n"
            "        destination = Path(directory) / 'destination'\n"
            "        source.write_bytes(b'payload')\n"
            "        publish(source, destination)\n"
            "        assert destination.read_bytes() == b'payload'\n",
            encoding="utf-8",
        )
        (source_root / "ops.py").write_text(
            "def publish(source, destination):\n"
            "    destination.write_bytes(source.read_bytes())\n"
            "KOSMIC_ROUTINES = [{\n"
            " 'id': 'kosmic/fixture-publish', 'symbol': 'publish',\n"
            " 'summary': 'Publish the fixture payload', 'owner': 'hexu',\n"
            " 'deterministic': True, 'offline': True, 'side_effects': ['filesystem'],\n"
            " 'tests': ['tests/test_ops.py::test_publish'],\n"
            " 'callers': ['python:client:run'],\n"
            " 'procedures': ['topic:kosmic/development/publish-fixture']\n"
            "}]\n",
            encoding="utf-8",
        )
        (source_root / "client.py").write_text(
            "from ops import publish\n"
            "def run(source, destination):\n"
            "    publish(source, destination)\n",
            encoding="utf-8",
        )
        self.write_topic(
            "kosmic/development/publish-fixture",
            audience="development",
            artifact_role="procedure",
            uses_routines="[kosmic/fixture-publish]",
            body=self.procedure_body("Call the fixture publication routine."),
        )
        generate_library(self.vault, source_root=source_root, work_record=self.work_record)
        with mock.patch(
            "skills.scripts.kosmic_shared_library.__file__",
            str(source_root / "kosmic_shared_library.py"),
        ):
            plan = resolve_library(
                self.vault,
                route="kosmic/development/publish-fixture",
                role="development",
                intent="do",
            )
            self.assertEqual(
                [row["id"] for row in plan["routines"]],
                ["kosmic/fixture-publish"],
            )
            packet = load_recipe_packet(self.vault, plan)
            self.assertIn("routine:kosmic/fixture-publish", packet)

    def test_procedure_with_unknown_routine_fails_closed(self) -> None:
        self.write_topic(
            "kosmic/development/unknown-routine",
            audience="development",
            artifact_role="procedure",
            uses_routines="[kosmic/missing]",
            body=self.procedure_body("Call a missing routine."),
        )
        with self.assertRaisesRegex(LibraryError, "unknown routine"):
            generate_library(self.vault, work_record=self.work_record)

    def test_routine_procedure_outside_active_domain_fails_closed(self) -> None:
        routines = {
            "routines": [{
                "id": "kosmic/atomic-publish-tree",
                "procedures": ["orphan/development/procedure"],
            }]
        }
        catalog = {"domains": [{"id": "kosmic"}], "topics": []}
        with self.assertRaisesRegex(LibraryError, "outside active catalog domain"):
            _validate_routine_edges(routines, catalog)

    def test_catalog_generation_is_deterministic_and_valid(self) -> None:
        first = generate_library(self.vault, work_record=self.work_record)
        snapshot = {p.relative_to(self.skills).as_posix(): p.read_bytes() for p in first}
        second = generate_library(self.vault, work_record=self.work_record)
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
        self.write_topic(
            "abinit/usage/bad",
            artifact_role="procedure",
            requires_procedures="[tb2j/development/debug-exchange]",
            body=self.procedure_body(),
        )
        with self.assertRaisesRegex(LibraryError, "Usage topic.*Development"):
            build_catalog(self.vault)

    def test_stable_topic_may_not_require_nonstable_topic(self) -> None:
        self.write_topic(
            "abinit/usage/draft-helper", status="draft",
            artifact_role="procedure", body=self.procedure_body(),
        )
        self.write_topic(
            "abinit/usage/stable-caller",
            artifact_role="procedure",
            requires_procedures="[abinit/usage/draft-helper]",
            body=self.procedure_body(),
        )
        with self.assertRaisesRegex(LibraryError, "BROKEN_DEPENDENCY.*ineligible"):
            build_catalog(self.vault)

    def test_query_resolves_cross_domain_dependency_first(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        plan = resolve_library(
            self.vault,
            query="debug exchange parameters from ABINIT",
            role="development",
            project="tb2j",
            intent="do",
        )
        ids = [row["id"] for row in plan["topics"]]
        self.assertEqual(ids[0], "tb2j/development/debug-exchange")
        self.assertEqual(set(ids[1:]), {"abinit/usage/export-wavefunctions", "abinit/usage/spin-orbit-conventions"})
        self.assertEqual(plan, resolve_library(self.vault, query="debug exchange parameters from ABINIT", role="development", project="tb2j", intent="do"))
        packet = load_recipe_packet(self.vault, plan)
        self.assertIn("Debug TB2J exchange", packet)
        self.assertIn("ABINIT wavefunction export reference", packet)

    def test_explicit_route_and_stale_plan(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        plan = resolve_library(self.vault, route="abinit/usage/export-wavefunctions", role="usage")
        self.assertEqual([row["id"] for row in plan["topics"]], ["abinit/usage/export-wavefunctions"])
        path = self.skills / "abinit/usage/export-wavefunctions.md"
        path.write_text(path.read_text() + "changed\n", encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "stale|hash"):
            load_recipe_packet(self.vault, plan)

    def test_domain_route_loads_only_domain_router(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        plan = resolve_library(self.vault, route="abinit", role="usage")
        self.assertEqual([row["id"] for row in plan["domains"]], ["abinit"])
        self.assertEqual(plan["topics"], [])
        packet = load_recipe_packet(self.vault, plan)
        self.assertIn("# ABINIT", packet)
        self.assertNotIn("Run ABINIT export", packet)

    def test_total_bytes_counts_exact_emitted_packet(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
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
        generate_library(self.vault, work_record=self.work_record)
        with self.assertRaisesRegex(LibraryError, "BUDGET_EXCEEDED"):
            resolve_library(self.vault, route="tb2j/development/debug-exchange", role="development", max_bytes=10)

    def test_ambiguity_fails_closed(self) -> None:
        self.write_topic("abinit/usage/export-density", summary="Export density", triggers="export", artifact_role="procedure", body=self.procedure_body())
        self.write_topic("tb2j/usage/export-density", summary="Export density", triggers="export", artifact_role="procedure", body=self.procedure_body())
        generate_library(self.vault, work_record=self.work_record)
        with self.assertRaisesRegex(LibraryError, "AMBIGUOUS"):
            resolve_library(self.vault, query="export", role="usage", intent="do")

    def test_intent_inference_origin_fallback_and_ambiguity(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        default = resolve_library(
            self.vault, query="wavefunction export reference", role="usage"
        )
        self.assertEqual(default["intent"], "understand")
        self.assertEqual(default["intent_origin"], "inferred")
        self.assertEqual(default["request"]["intent_origin"], "inferred")
        action = resolve_library(
            self.vault,
            query="debug exchange parameters from ABINIT",
            role="development",
            project="tb2j",
        )
        self.assertEqual(action["intent"], "do")
        self.assertEqual(action["primary_topic"], "tb2j/development/debug-exchange")
        fallback = resolve_library(
            self.vault,
            query="review debug exchange",
            role="development",
            intent="check",
        )
        self.assertEqual(fallback["topics"][0]["artifact_role"], "procedure")
        self.assertEqual(fallback["intent_origin"], "explicit")
        with self.assertRaisesRegex(LibraryError, "AMBIGUOUS_INTENT"):
            resolve_library(
                self.vault, query="check why export fails", role="usage"
            )

    def test_chained_procedures_are_dependency_first(self) -> None:
        self.write_topic(
            "abinit/usage/z-base",
            artifact_role="procedure",
            summary="Base setup",
            triggers="base setup",
            body=self.procedure_body("Prepare the base."),
        )
        self.write_topic(
            "abinit/usage/a-middle",
            artifact_role="procedure",
            summary="Middle setup",
            triggers="middle setup",
            requires_procedures="[abinit/usage/z-base]",
            body=self.procedure_body("Prepare the middle."),
        )
        self.write_topic(
            "abinit/usage/run-chain",
            artifact_role="procedure",
            summary="Run chain",
            triggers="run chain",
            requires_procedures="[abinit/usage/a-middle]",
            body=self.procedure_body("Run the chain."),
        )
        generate_library(self.vault, work_record=self.work_record)
        plan = resolve_library(
            self.vault, query="run chain", role="usage", intent="do"
        )
        self.assertEqual(
            [row["id"] for row in plan["topics"]],
            [
                "abinit/usage/z-base",
                "abinit/usage/a-middle",
                "abinit/usage/run-chain",
            ],
        )

    def test_include_evidence_loads_declared_support(self) -> None:
        self.write_topic(
            "abinit/usage/export-observation",
            artifact_role="evidence",
            observed_on="2026-09-07",
            summary="Observed export",
            triggers="observed export",
        )
        self.write_topic(
            "abinit/usage/export-procedure",
            artifact_role="procedure",
            summary="Export procedure",
            triggers="run export",
            supported_by="[abinit/usage/export-observation]",
            body=self.procedure_body(),
        )
        generate_library(self.vault, work_record=self.work_record)
        without = resolve_library(
            self.vault, query="run export", role="usage", intent="do"
        )
        with_evidence = resolve_library(
            self.vault,
            query="run export",
            role="usage",
            intent="do",
            include_evidence=True,
        )
        self.assertNotIn(
            "abinit/usage/export-observation",
            [row["id"] for row in without["topics"]],
        )
        self.assertIn(
            "abinit/usage/export-observation",
            [row["id"] for row in with_evidence["topics"]],
        )

    def test_procedure_sections_must_be_non_empty_and_requires_is_obsolete(self) -> None:
        empty = self.procedure_body().replace(
            "## Verification\n\nVerify the observable result.",
            "## Verification\n\n",
        )
        self.write_topic(
            "abinit/usage/empty-verification",
            artifact_role="procedure",
            body=empty,
        )
        with self.assertRaisesRegex(LibraryError, "non-empty section.*verification"):
            build_catalog(self.vault)
        (self.skills / "abinit/usage/empty-verification.md").unlink()
        path = self.write_topic("abinit/usage/legacy-requires")
        text = path.read_text(encoding="utf-8").replace(
            "requires_procedures: []", "requires: [abinit/usage/anything]"
        )
        path.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "obsolete requires"):
            build_catalog(self.vault)

    def test_generated_drift_fails(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
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
            migrate_assignments(self.vault, project, {}, work_record=self.work_record)
        report = migrate_assignments(
            self.vault,
            project,
            {"demo-usage/references/one.md": self.migration_assignment("abinit/usage/one")},
            work_record=self.work_record,
        )
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
                {"demo-development/references/one.md": self.migration_assignment("abinit/usage/one")},
                work_record=self.work_record,
            )

    def test_migration_failure_preserves_prior_library(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
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
                    {"demo-usage/references/one.md": self.migration_assignment("abinit/usage/one")},
                    work_record=self.work_record,
                )
        self.assertEqual((self.skills / ".kosmic/catalog.json").read_bytes(), before)
        self.assertFalse((self.skills / "abinit/usage/one.md").exists())

    def test_shared_router_install_is_atomic_and_removes_managed_pairs(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        destination = Path(self.temp.name) / "agent-skills"
        old = destination / "demo-usage"
        old.mkdir(parents=True)
        (old / ".kosmic-projection.json").write_text('{"project_id":"demo"}\n', encoding="utf-8")
        unmanaged = destination / "personal"
        unmanaged.mkdir()
        install_shared_router(self.vault, destination, work_record=self.work_record)
        self.assertFalse(old.exists())
        self.assertTrue(unmanaged.exists())
        self.assertEqual(check_shared_router_installation(self.vault, destination), destination / "memnotes-skills")

    def test_shared_router_collision_preserves_inventory(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        destination = Path(self.temp.name) / "agent-skills"
        collision = destination / "memnotes-skills"
        collision.mkdir(parents=True)
        (collision / "personal.txt").write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "collision"):
            install_shared_router(self.vault, destination, work_record=self.work_record)
        self.assertEqual((collision / "personal.txt").read_text(), "keep")


    def test_router_contains_executable_invocation_and_budget_policy(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        destination = Path(self.temp.name) / "agent-skills"
        installed = install_shared_router(self.vault, destination, work_record=self.work_record)
        body = (installed / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("python3 ", body)
        self.assertIn("kosmic_project_skills.py", body)
        self.assertIn("32768 packet bytes, 4 domains, 8 topics", body)

    def test_router_replace_failure_preserves_previous_router(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        destination_root = Path(self.temp.name) / "agent-skills"
        destination = install_shared_router(self.vault, destination_root, work_record=self.work_record)
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
                install_shared_router(self.vault, destination_root, work_record=self.work_record)
        self.assertEqual(marker.read_text(encoding="utf-8"), "prior")
    def test_generation_rollback_preserves_previous_artifacts(self) -> None:
        generate_library(self.vault, work_record=self.work_record)
        before = (self.skills / ".kosmic/catalog.json").read_bytes()
        with mock.patch.dict(os.environ, {"KOSMIC_FAIL_STAGE": "after-backup"}):
            with self.assertRaises(OSError):
                generate_library(self.vault, work_record=self.work_record)
        self.assertEqual((self.skills / ".kosmic/catalog.json").read_bytes(), before)

    def test_role_and_procedure_contract_fail_closed(self) -> None:
        topic = self.skills / "abinit/usage/export-wavefunctions.md"
        topic.write_text(topic.read_text().replace("artifact_role: knowledge", "artifact_role: report"), encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "artifact_role"):
            build_catalog(self.vault)
        topic.write_text(topic.read_text().replace("artifact_role: report", "artifact_role: procedure"), encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "missing required fields: outcome|procedure.*section"):
            build_catalog(self.vault)

    def test_typed_relationship_requires_matching_role(self) -> None:
        self.write_topic("abinit/usage/rules", artifact_role="guideline")
        self.write_topic(
            "abinit/usage/bad-role-edge",
            artifact_role="procedure",
            uses_knowledge="[abinit/usage/rules]",
            body=self.procedure_body(),
        )
        with self.assertRaisesRegex(LibraryError, "uses_knowledge.*knowledge"):
            build_catalog(self.vault)

    def test_evidence_date_and_supersession_are_validated(self) -> None:
        self.write_topic("abinit/usage/old-result", artifact_role="evidence", observed_on="2026-01-01")
        self.write_topic(
            "abinit/usage/new-result", artifact_role="evidence",
            observed_on="2026-02-01", supersedes="[abinit/usage/old-result]",
        )
        build_catalog(self.vault)
        old = self.skills / "abinit/usage/old-result.md"
        old.write_text(old.read_text().replace("observed_on: 2026-01-01", "observed_on: "), encoding="utf-8")
        with self.assertRaisesRegex(LibraryError, "observed_on"):
            build_catalog(self.vault)

    def test_do_understand_and_investigate_select_by_role(self) -> None:
        self.write_topic("abinit/usage/export-guide", artifact_role="guideline", summary="Export guidance", triggers="export guidance")
        self.write_topic("abinit/usage/export-facts", artifact_role="knowledge", summary="Export facts", triggers="understand export storage")
        self.write_topic("abinit/usage/export-result", artifact_role="evidence", summary="Export failure evidence", triggers="investigate export failure", observed_on="2026-03-01")
        generate_library(self.vault, work_record=self.work_record)
        task = resolve_library(self.vault, query="debug exchange parameters", role="development", intent="do")
        self.assertEqual(task["mode"], "task")
        self.assertEqual(task["primary_topic"], "tb2j/development/debug-exchange")
        knowledge = resolve_library(self.vault, query="understand export storage", role="usage")
        self.assertEqual((knowledge["intent"], knowledge["mode"]), ("understand", "reference"))
        self.assertEqual(knowledge["primary_topic"], "abinit/usage/export-facts")
        evidence = resolve_library(self.vault, query="investigate export failure", role="usage")
        self.assertEqual(evidence["primary_topic"], "abinit/usage/export-result")
        with self.assertRaisesRegex(LibraryError, "NO_EXECUTABLE_MATCH"):
            resolve_library(self.vault, query="understand export storage", role="usage", intent="do")

    def test_typed_packet_labels_relations_and_excludes_evidence(self) -> None:
        self.write_topic("abinit/usage/export-rules", artifact_role="guideline")
        self.write_topic("abinit/usage/export-proof", artifact_role="evidence", observed_on="2026-03-01")
        topic = self.skills / "tb2j/development/debug-exchange.md"
        text = topic.read_text().replace(
            "governed_by: []", "governed_by: [abinit/usage/export-rules]"
        ).replace("supported_by: []", "supported_by: [abinit/usage/export-proof]")
        topic.write_text(text, encoding="utf-8")
        generate_library(self.vault, work_record=self.work_record)
        plan = resolve_library(self.vault, query="debug exchange parameters", role="development", intent="do")
        rows = {row["id"]: row for row in plan["topics"]}
        self.assertEqual(rows["tb2j/development/debug-exchange"]["relation"], "primary")
        self.assertEqual(rows["abinit/usage/export-rules"]["relation"], "governing")
        self.assertNotIn("abinit/usage/export-proof", rows)
        packet = load_recipe_packet(self.vault, plan)
        self.assertIn("role:procedure relation:primary", packet)


if __name__ == "__main__":
    unittest.main()
