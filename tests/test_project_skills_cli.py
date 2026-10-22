from __future__ import annotations

import hashlib
import json
import re
import os
import subprocess
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


from skills.scripts.kosmic_project_skills import proposal_fingerprint
REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "scripts" / "kosmic_project_skills.py"


class ProjectionCliFixture:
    """Fixture helpers only; concrete suites supply ``unittest.TestCase``."""

    EMPTY_MATH_INDEX = (
        "# Math Derivations\n\n"
        "| Derivation | Status | Result summary |\n"
        "|------------|--------|----------------|\n"
    )

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cli(
        self,
        *arguments: str,
        expected: int = 0,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        process_env = os.environ.copy()
        if arguments and (arguments[0] in {"generate", "generate-status", "install"}
                          or (arguments[0] == "check-math" and "--update" in arguments)):
            project_argument = next((arguments[i + 1] for i, item in enumerate(arguments[:-1])
                                     if item == "--project"), None)
            if project_argument is not None and "--work-record" not in arguments:
                project_path = Path(project_argument)
                entry = project_path / "ProjectEntry.md"
                match = re.search(r"^project_id:\s*([\w.-]+)", entry.read_text(), re.M)
                if match:
                    arguments = (*arguments, "--work-record",
                                 f"{match.group(1)}/quick-task/fixture-task")
        if env:
            process_env.update(env)
        result = subprocess.run(
            [sys.executable, str(CLI), *arguments],
            cwd=REPO_ROOT,
            env=process_env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            expected,
            result.returncode,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )
        return result

    def make_project(self, project_id: str = "acme-demo") -> Path:
        project = self.root / "vault" / "Projects" / "demo"
        notes = project / "notes"
        notes.mkdir(parents=True, exist_ok=True)
        (notes / "index.md").write_text(
            '---\nokf_version: "0.2"\n---\n\n# Project Knowledge\n',
            encoding="utf-8",
        )
        (project / "ProjectEntry.md").write_text(
            "---\n"
            f"project_id: {project_id}\n"
            "working_state: working-tree\n"
            "---\n\n"
            "# Demo\n",
            encoding="utf-8",
        )
        mathdocs = project / "mathdocs"
        mathdocs.mkdir()
        (mathdocs / "index.md").write_text(
            ProjectionCliFixture.EMPTY_MATH_INDEX, encoding="utf-8"
        )
        specs = project / "specs" / "quick-tasks"
        specs.mkdir(parents=True, exist_ok=True)
        (project / "specs" / "INDEX.md").write_text("# Specs\n", encoding="utf-8")
        (specs / "2026-10-04-fixture-task.md").write_text(
            "---\n"
            f"project_id: {project_id}\n"
            "record_kind: quick-task\nlocal_id: fixture-task\n"
            "subproject_id: null\nstatus: approved\n---\n\n"
            "# Fixture Task\n\n## Acceptance Criteria\n\n- [ ] Fixture behavior verified\n",
            encoding="utf-8")
        # Story 048: validate/review/install/check-completion run their scratch
        # below a managed run, which requires a Git worktree at the vault root.
        (project.parents[1] / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(project.parents[1])], check=True, capture_output=True)
        return project

    def write_note(
        self,
        project: Path,
        name: str,
        audience: str | None,
        body: str,
        status: str = "stable",
        usage_stale: bool = False,
        stale_after: str | None = None,
        concept_type: str = "Project Knowledge",
        artifact_role: str | None = None,
    ) -> Path:
        metadata = [f"type: {concept_type}", f"status: {status}"]
        if audience is not None:
            metadata.append(f"audience: {audience}")
        if artifact_role is not None:
            metadata.append(f"artifact_role: {artifact_role}")
        if usage_stale:
            metadata.append("usage_stale: true")
        if stale_after is not None:
            metadata.append(f"stale_after: '{stale_after}'")
        note = project / "notes" / f"{name}.md"
        note.parent.mkdir(parents=True, exist_ok=True)
        note.write_text(
            "---\n" + "\n".join(metadata) + "\n---\n\n" + body + "\n",
            encoding="utf-8",
        )
        return note

    def generate_ready_project(self, project_id: str = "acme-demo") -> Path:
        project = self.make_project(project_id)
        self.write_note(project, "using", "usage", "# Use Demo\n\nRun `demo`.\n")
        self.write_note(
            project,
            "developing",
            "development",
            "# Develop Demo\n\nRun contributor checks.\n",
        )
        self.run_cli("generate", "--project", str(project))
        return project

    def snapshot(self, root: Path) -> dict[str, str]:
        return {
            path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(item for item in root.rglob("*") if item.is_file())
        }

    def manifest(self, package: Path) -> dict[str, object]:
        return json.loads((package / ".kosmic-projection.json").read_text(encoding="utf-8"))

    def write_proposal(
        self,
        project: Path,
        *,
        result: str = "create",
        decision: str = "pending",
        fingerprint: str = "",
        extra: str = "",
    ) -> Path:
        inputs = project / "specs" / "skill-proposals" / "inputs" / "demo.md"
        inputs.parent.mkdir(parents=True, exist_ok=True)
        source = project / "notes" / "index.md"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        inputs.write_text(f"- notes/index.md: {digest}\n", encoding="utf-8")
        proposal = inputs.parent.parent / "2026-09-06-demo.md"
        target = "demo-skill" if result != "no_action" else ""
        target_ref = "skill://demo-skill" if result != "no_action" else ""
        target_hash = "empty" if result == "create" else digest if result == "update" else ""
        proposed = (
            "## No-Action Reason\n\nProject facts only; no reusable procedure.\n"
            if result == "no_action"
            else "## Proposed Change\n\nCreate one repeatable diagnostic procedure.\n"
        )
        proposal.write_text(
            "---\n"
            "status: draft\ncreated: 2026-09-06\nupdated: 2026-09-06\n"
            f"result: {result}\nscope: project-procedure\nartifact_role: procedure\n"
            f"target: {target}\ntarget_ref: {target_ref}\ntarget_sha256: {target_hash}\n"
            "proposer_mode: same-agent\nproposer_ref: agent://test\n"
            'proposer_reason: "Project-local test fixture"\n'
            "input_manifest: [specs/skill-proposals/inputs/demo.md]\n"
            "related_notes: [notes/index.md]\n"
            "behavioral_evidence: []\n"
            f"decision: {decision}\nfingerprint: {fingerprint}\nreconsiders: \"\"\n"
            f"{extra}---\n\n# Skill Proposal: Demo\n\n"
            "## Problem\n\nRepeated diagnostic work.\n\n"
            "## Evidence\n\nObserved in maintained knowledge.\n\n"
            f"{proposed}\n## Applicability\n\nProject-local procedure.\n\n"
            "## Behavioral Validation\n\nPending approval.\n\nCandidate paths: [.scratch/candidate-skill]\n\n"
            "## Risks\n\nPossible overfitting.\n\n"
            "## New Evidence\n\nNone.\n",
            encoding="utf-8",
        )
        return proposal

    def write_routine_proposal(self, project: Path, action: str) -> Path:
        inputs = project / "specs" / "skill-proposals" / "inputs" / f"{action}.md"
        inputs.parent.mkdir(parents=True, exist_ok=True)
        source = project / "notes" / "index.md"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        library = self.root / "vault" / "Skills"
        (library / ".kosmic").mkdir(parents=True, exist_ok=True)
        (library / "kosmic").mkdir(exist_ok=True)
        routine_pin = f"- routine://kosmic/existing: {digest}\n" if action == "extend" else ""
        inputs.write_text(f"- notes/index.md: {digest}\n{routine_pin}", encoding="utf-8")
        (library / "kosmic" / "SKILL.md").write_text(
            "---\nid: kosmic\nmaintainers: [alice]\n---\n# Kosmic\n", encoding="utf-8"
        )
        (library / ".kosmic" / "routines.json").write_text(json.dumps({
            "routines": [{
                "id": "kosmic/existing", "routine_sha256": digest, "procedures": [],
            }],
        }), encoding="utf-8")
        result = {"create": "create", "extend": "update"}.get(action, "no_action")
        routine_id = "kosmic/new" if action == "create" else "kosmic/existing"
        target = routine_id
        target_ref = f"routine://{routine_id}"
        target_hash = "empty" if action == "create" else digest
        if action == "keep_as_prose":
            routine_id = ""
            target = "kosmic/development/procedure"
            target_ref = f"library-skill://{target}"
            target_hash = ""
        elif action == "none":
            routine_id = target = target_ref = target_hash = ""
        change_heading = "No-Action Reason" if result == "no_action" else "Proposed Change"
        candidate = (
            "\n## Routine Candidate\n\n"
            "Repetition: Used by multiple callers.\n\n"
            "Contract: Inputs and outputs are paths; rollback is invariant; filesystem is the side effect.\n\n"
            "Expected failures: Invalid paths and failed replacements.\n\n"
            "Leverage: One implementation removes duplicated transactions.\n"
            if action in {"create", "extend"} else ""
        )
        proposal = inputs.parent.parent / f"2026-09-07-{action.replace('_', '-')}.md"
        rendered_action = '"none"' if action == "none" else action
        proposal.write_text(
            "---\nstatus: draft\ncreated: 2026-09-07\nupdated: 2026-09-07\n"
            f"result: {result}\nscope: shared-routine\nartifact_role: procedure\n"
            "target_kind: routine\n"
            f"routine_action: {rendered_action}\nroutine_id: {routine_id}\n"
            "linked_proposals: []\nconsumer_approvals: []\n"
            f"target: {target}\ntarget_ref: {target_ref}\ntarget_sha256: {target_hash}\n"
            "proposer_mode: subagent\nproposer_ref: agent://test\n"
            "proposer_reason: \"Routine action fixture\"\n"
            f"input_manifest: [specs/skill-proposals/inputs/{action}.md]\n"
            "related_notes: [notes/index.md]\n"
            "behavioral_evidence: []\ndecision: pending\nfingerprint: \"\"\nreconsiders: \"\"\n"
            "---\n\n# Skill Proposal: Routine\n\n"
            "## Problem\n\nRepeated mechanics.\n\n"
            "## Evidence\n\nA deterministic fixture.\n\n"
            f"## {change_heading}\n\nGovern the selected routine action.\n"
            f"{candidate}\n## Applicability\n\nProcedure mechanics.\n\n"
            "## Behavioral Validation\n\nPending.\n\nCandidate paths: [.scratch/routine]\n\n"
            "## Risks\n\nIncorrect reuse.\n\n## New Evidence\n\nNone.\n",
            encoding="utf-8",
        )
        return proposal


class ProjectionCliTest(ProjectionCliFixture, unittest.TestCase):
    def test_migrate_routines_reports_only_explicit_candidates(self) -> None:
        project = self.make_project()
        inventory_path = self.root / "vault" / "Skills" / ".kosmic" / "routines.json"
        inventory_path.parent.mkdir(parents=True)
        inventory_path.write_text(json.dumps({
            "routines": [{
                "id": "kosmic/publish",
                "module": "skills/scripts/ops.py",
                "symbol": "publish",
                "routine_sha256": "a" * 64,
                "callers": ["python:client:run"],
                "procedures": ["kosmic/development/publish"],
            }],
        }), encoding="utf-8")
        report = project / "specs" / "migration.md"
        self.run_cli(
            "migrate-routines",
            "--project", str(project),
            "--output", str(report),
            "--legacy-candidate", "old:publish",
            "--unregistered-helper", "local:helper",
        )
        body = report.read_text(encoding="utf-8")
        self.assertIn("`kosmic/publish`", body)
        self.assertIn("`kosmic/development/publish`", body)
        self.assertIn("`old:publish`", body)
        self.assertIn("`local:helper`", body)
        self.assertNotIn("publish_directory", body)

    def test_generates_exactly_one_usage_and_development_skill(self) -> None:
        project = self.generate_ready_project()
        skills = project / "skills"
        skill_dirs = sorted(path.name for path in skills.iterdir() if path.is_dir())
        self.assertEqual(["acme-demo-development", "acme-demo-usage"], skill_dirs)
        usage = skills / "acme-demo-usage"
        development = skills / "acme-demo-development"
        self.assertTrue((usage / "SKILL.md").is_file())
        self.assertTrue((usage / "references" / "using.md").is_file())
        self.assertTrue((development / "references" / "developing.md").is_file())
        self.assertIn(
            "`acme-demo-usage`",
            (development / "SKILL.md").read_text(encoding="utf-8"),
        )
        self.run_cli("validate", "--project", str(project))

    def test_audience_scope_eligibility_and_provenance(self) -> None:
        project = self.make_project()
        usage = self.write_note(project, "usage", "usage", "# Usage\n\nConsumer only.\n")
        both = self.write_note(project, "both", "both", "# Shared\n\nShared behavior.\n")
        development = self.write_note(
            project, "development", "development", "# Development\n\nInternal behavior.\n"
        )
        unscoped = self.write_note(project, "legacy", None, "# Legacy\n\nLegacy internal.\n")
        self.write_note(project, "draft", "usage", "# Future\n\nNot implemented.\n", status="draft")
        self.write_note(
            project, "stale", "usage", "# Stale\n\nOld behavior.\n", usage_stale=True
        )
        result = self.run_cli("generate", "--project", str(project))
        self.assertIn("Unscoped Knowledge projected to Development only", result.stderr)

        usage_package = project / "skills" / "acme-demo-usage"
        development_package = project / "skills" / "acme-demo-development"
        self.assertEqual(
            ["notes/both.md", "notes/usage.md"],
            [source["path"] for source in self.manifest(usage_package)["sources"]],
        )
        self.assertEqual(
            ["notes/development.md", "notes/legacy.md"],
            [source["path"] for source in self.manifest(development_package)["sources"]],
        )
        reference = usage_package / "references" / "usage.md"
        projected = reference.read_text(encoding="utf-8")
        self.assertIn(f"source_sha256: {hashlib.sha256(usage.read_bytes()).hexdigest()}", projected)
        self.assertNotIn("status: validated", projected)
        self.assertNotIn("Future", "\n".join(path.read_text() for path in usage_package.rglob("*.md")))
        self.assertTrue(both.exists() and development.exists() and unscoped.exists())

    def test_projected_reference_preserves_artifact_role(self) -> None:
        project = self.make_project()
        self.write_note(
            project,
            "knowledge",
            "usage",
            "# Knowledge\n\nExplain the system.\n",
            artifact_role="knowledge",
        )
        self.run_cli("generate", "--project", str(project))
        projected = (
            project
            / "skills"
            / "acme-demo-usage"
            / "references"
            / "knowledge.md"
        ).read_text(encoding="utf-8")
        self.assertIn("artifact_role: knowledge", projected)

    def test_source_change_is_reported_as_drift(self) -> None:
        project = self.generate_ready_project()
        note = project / "notes" / "using.md"
        note.write_text(note.read_text(encoding="utf-8") + "Changed.\n", encoding="utf-8")
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("projection drift detected for source: notes/using.md", result.stderr)

    def test_generation_is_deterministic(self) -> None:
        project = self.generate_ready_project()
        first = self.snapshot(project / "skills")
        self.run_cli("generate", "--project", str(project))
        second = self.snapshot(project / "skills")
        self.assertEqual(first, second)

    def test_publication_failure_preserves_previous_pair(self) -> None:
        project = self.generate_ready_project()
        before = self.snapshot(project / "skills")
        self.write_note(project, "new", "both", "# New Behavior\n\nNew guidance.\n")
        result = self.run_cli(
            "generate",
            "--project",
            str(project),
            expected=5,
            env={"KOSMIC_FAIL_STAGE": "after-backup"},
        )
        self.assertIn("injected publication failure", result.stderr)
        self.assertEqual(before, self.snapshot(project / "skills"))

    def test_empty_usage_blocks_publication(self) -> None:
        project = self.make_project()
        self.write_note(project, "development", "development", "# Development\n\nInternal.\n")
        result = self.run_cli("generate", "--project", str(project), expected=2)
        self.assertIn("Usage Skill requires", result.stderr)
        self.assertFalse((project / "skills").exists())

    def test_init_assigns_identity_and_publishes_pair(self) -> None:
        project = self.root / "vault" / "Projects" / "new-project"
        (project / "notes").mkdir(parents=True)
        self.write_note(project, "usage", "usage", "# Usage\n\nUse it.\n")
        self.write_note(project, "development", "development", "# Dev\n\nChange it.\n")
        self.run_cli(
            "init", "--project", str(project), "--project-id", "acme-new-project"
        )
        entry = (project / "ProjectEntry.md").read_text(encoding="utf-8")
        self.assertIn("project_id: acme-new-project", entry)
        self.assertTrue((project / "skills" / "acme-new-project-usage").is_dir())

    def test_migration_is_restartable_and_unscoped_is_development_only(self) -> None:
        project = self.root / "vault" / "Projects" / "legacy"
        (project / "notes").mkdir(parents=True)
        (project / "ProjectEntry.md").write_text("# Legacy\n", encoding="utf-8")
        self.write_note(project, "legacy", None, "# Legacy knowledge\n\nInternal.\n")
        result = self.run_cli(
            "migrate",
            "--project",
            str(project),
            "--project-id",
            "acme-legacy",
            expected=3,
        )
        self.assertIn("pair publication is blocked", result.stderr)
        self.assertIn(
            "project_id: acme-legacy",
            (project / "ProjectEntry.md").read_text(encoding="utf-8"),
        )
        self.assertFalse((project / "skills").exists())
        self.write_note(project, "usage", "usage", "# Usage\n\nUse legacy.\n")
        self.run_cli(
            "migrate", "--project", str(project), "--project-id", "acme-legacy"
        )
        development_manifest = self.manifest(
            project / "skills" / "acme-legacy-development"
        )
        self.assertEqual("notes/legacy.md", development_manifest["sources"][0]["path"])
        self.run_cli(
            "migrate", "--project", str(project), "--project-id", "acme-legacy"
        )

    def test_project_identifier_collision_is_rejected(self) -> None:
        first = self.make_project("acme-shared")
        second = first.parent / "other"
        (second / "notes").mkdir(parents=True)
        (second / "ProjectEntry.md").write_text("# Other\n", encoding="utf-8")
        result = self.run_cli(
            "migrate",
            "--project",
            str(second),
            "--project-id",
            "acme-shared",
            expected=4,
        )
        self.assertIn("collision", result.stderr)

    def test_completion_gate_requires_current_consumer_knowledge(self) -> None:
        project = self.generate_ready_project()
        work_item = project / "specs" / "quick-tasks" / "change.md"
        work_item.parent.mkdir(parents=True, exist_ok=True)
        work_item.write_text(
            "---\nproject_id: acme-demo\nrecord_kind: quick-task\n"
            "local_id: change\nsubproject_id: null\nstatus: approved\n"
            "consumer_interface_change: true\nrelated_notes: [using]\n---\n# Change\n",
            encoding="utf-8",
        )
        self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(work_item),
        )
        note = project / "notes" / "using.md"
        note.write_text(note.read_text(encoding="utf-8") + "New interface.\n", encoding="utf-8")
        result = self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(work_item),
            expected=2,
        )
        self.assertIn("projection drift", result.stderr)
        self.run_cli("generate", "--project", str(project))
        self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(work_item),
        )

    def test_non_interface_change_does_not_require_usage_refresh(self) -> None:
        project = self.generate_ready_project()
        work_item = project / "internal.md"
        work_item.write_text(
            "---\nconsumer_interface_change: false\n---\n# Internal\n",
            encoding="utf-8",
        )
        (project / "skills").rename(project / "skills-away")
        self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(work_item),
        )

    def test_named_install_adapters_are_discoverable_and_atomic(self) -> None:
        project = self.generate_ready_project()
        adapter_roots = {
            "opencode": Path(".config/opencode/skill"),
            "claude-code": Path(".claude/skills"),
            "codex": Path(".agents/skills"),
            "omp": Path(".omp/agent/skills"),
        }
        for adapter, relative_root in adapter_roots.items():
            with self.subTest(adapter=adapter):
                home = self.root / f"home-{adapter}"
                self.run_cli(
                    "install",
                    "--project",
                    str(project),
                    "--adapter",
                    adapter,
                    "--home",
                    str(home),
                )
                installed = home / relative_root
                self.assertTrue((installed / "acme-demo-usage" / "SKILL.md").is_file())
                development = installed / "acme-demo-development" / "SKILL.md"
                self.assertIn("acme-demo-usage", development.read_text(encoding="utf-8"))

                before = self.snapshot(installed)
                result = self.run_cli(
                    "install",
                    "--project",
                    str(project),
                    "--adapter",
                    adapter,
                    "--home",
                    str(home),
                    expected=5,
                    env={"KOSMIC_FAIL_STAGE": "install-after-first"},
                )
                self.assertIn("injected adapter failure", result.stderr)
                self.assertEqual(before, self.snapshot(installed))

    def test_check_required_skills_reports_missing_and_complete_adapter_sets(self) -> None:
        adapter_roots = {
            "opencode": Path(".config/opencode/skill"),
            "claude-code": Path(".claude/skills"),
            "codex": Path(".agents/skills"),
            "omp": Path(".omp/agent/skills"),
        }
        required_skills = (
            "tdd",
            "code-review",
            "diagnosing-bugs",
            "research",
            "domain-modeling",
            "codebase-design",
            "grill-with-docs",
            "grilling",
            "prototype",
        )
        for adapter, relative_root in adapter_roots.items():
            with self.subTest(adapter=adapter):
                home = self.root / f"required-{adapter}"
                result = self.run_cli(
                    "check-required-skills",
                    "--adapter",
                    adapter,
                    "--home",
                    str(home),
                    expected=4,
                )
                self.assertIn("missing required skills", result.stderr)
                self.assertIn("prototype", result.stderr)

                skill_root = home / relative_root
                for skill in required_skills:
                    (skill_root / skill).mkdir(parents=True, exist_ok=True)
                    (skill_root / skill / "SKILL.md").write_text(
                        f"---\nname: {skill}\n---\n",
                        encoding="utf-8",
                    )

                result = self.run_cli(
                    "check-required-skills",
                    "--adapter",
                    adapter,
                    "--home",
                    str(home),
                )
                self.assertIn("required skills available", result.stdout)

    def test_check_required_skills_rejects_unsupported_adapter(self) -> None:
        result = self.run_cli(
            "check-required-skills",
            "--adapter",
            "pointer",
            "--home",
            str(self.root / "unsupported"),
            expected=2,
        )
        self.assertIn("invalid choice", result.stderr)

    def test_pointer_adapter_updates_managed_section_without_copying_notes(self) -> None:
        project = self.generate_ready_project()
        instructions = self.root / "agent" / "AGENTS.md"
        instructions.parent.mkdir(parents=True)
        instructions.write_text("# Existing instructions\n", encoding="utf-8")
        self.run_cli(
            "install",
            "--project",
            str(project),
            "--adapter",
            "pointer",
            "--instructions",
            str(instructions),
        )
        first = instructions.read_text(encoding="utf-8")
        self.assertIn(str(project / "skills" / "acme-demo-usage"), first)
        self.assertIn(str(project / "skills" / "acme-demo-development"), first)
        self.assertNotIn("Run `demo`", first)
        self.run_cli(
            "install",
            "--project",
            str(project),
            "--adapter",
            "pointer",
            "--instructions",
            str(instructions),
        )
        self.assertEqual(first, instructions.read_text(encoding="utf-8"))

    def test_invalid_identity_and_audience_fail_without_output(self) -> None:
        invalid_id = self.make_project("Acme Demo")
        self.write_note(invalid_id, "usage", "usage", "# Usage\n\nUse it.\n")
        result = self.run_cli("generate", "--project", str(invalid_id), expected=2)
        self.assertIn("invalid Project Identifier", result.stderr)
        self.assertFalse((invalid_id / "skills").exists())

        invalid_audience = self.root / "vault" / "Projects" / "invalid-audience"
        (invalid_audience / "notes").mkdir(parents=True)
        (invalid_audience / "mathdocs").mkdir()
        (invalid_audience / "mathdocs" / "index.md").write_text(
            MathDocsLayerTest.EMPTY_MATH_INDEX, encoding="utf-8"
        )
        (invalid_audience / "notes" / "index.md").write_text(
            '---\nokf_version: "0.2"\n---\n\n# Project Knowledge\n',
            encoding="utf-8",
        )
        (invalid_audience / "ProjectEntry.md").write_text(
            "---\nproject_id: acme-invalid-audience\n---\n# Invalid\n",
            encoding="utf-8",
        )
        self.write_note(
            invalid_audience,
            "usage",
            "everyone",
            "# Usage\n\nAmbiguous audience.\n",
        )
        result = self.run_cli(
            "generate", "--project", str(invalid_audience), expected=2
        )
        self.assertIn("invalid Audience Scope", result.stderr)
        self.assertFalse((invalid_audience / "skills").exists())

    def test_install_collision_preserves_unmanaged_skill(self) -> None:
        project = self.generate_ready_project()
        home = self.root / "collision-home"
        existing = home / ".config" / "opencode" / "skill" / "acme-demo-usage"
        existing.mkdir(parents=True)
        marker = existing / "owner.txt"
        marker.write_text("another skill\n", encoding="utf-8")

        result = self.run_cli(
            "install",
            "--project",
            str(project),
            "--adapter",
            "opencode",
            "--home",
            str(home),
            expected=4,
        )
        self.assertIn("installation collision", result.stderr)
        self.assertEqual("another skill\n", marker.read_text(encoding="utf-8"))
        self.assertFalse(
            (home / ".config" / "opencode" / "skill" / "acme-demo-development").exists()
        )

    def test_review_reports_unscoped_knowledge_until_classified(self) -> None:
        project = self.make_project()
        self.write_note(project, "usage", "usage", "# Usage\n\nUse it.\n")
        legacy = self.write_note(
            project, "legacy", None, "# Legacy\n\nContributor guidance.\n"
        )
        self.run_cli("generate", "--project", str(project))
        result = self.run_cli("review", "--project", str(project), expected=2)
        self.assertIn("Unscoped Knowledge: notes/legacy.md", result.stderr)

        legacy.write_text(
            legacy.read_text(encoding="utf-8").replace(
                "status: stable\n", "status: stable\naudience: development\n"
            ),
            encoding="utf-8",
        )
        self.run_cli("generate", "--project", str(project))
        self.run_cli("review", "--project", str(project))

    def test_init_normalizes_notes_into_dual_okf_obsidian_bundle(self) -> None:
        project = self.root / "vault" / "Projects" / "legacy-init"
        notes = project / "notes"
        notes.mkdir(parents=True)
        (notes / "TOC.md").write_text(
            "# Table of Contents\n\n## Guides\n- [[using]] - Consumer guidance.\n",
            encoding="utf-8",
        )
        (notes / "using.md").write_text(
            "# Use Legacy\n\n"
            "---\n"
            "status: validated\n"
            "audience: usage\n"
            "---\n\n"
            "See [[developing|developer guide]].\n",
            encoding="utf-8",
        )
        (notes / "developing.md").write_text(
            "---\nstatus: validated\naudience: development\n---\n\n"
            "# Develop Legacy\n\nRun contributor checks.\n",
            encoding="utf-8",
        )

        # Story 048: validate requires a Git worktree at the vault root.
        (project.parents[1] / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(project.parents[1])], check=True, capture_output=True)
        self.run_cli(
            "init",
            "--project",
            str(project),
            "--project-id",
            "acme-legacy-init",
        )

        index = notes / "index.md"
        self.assertTrue(index.is_file())
        self.assertFalse((notes / "TOC.md").exists())
        self.assertTrue(index.read_text(encoding="utf-8").startswith("---\n"))
        self.assertIn('okf_version: "0.2"', index.read_text(encoding="utf-8"))
        using = (notes / "using.md").read_text(encoding="utf-8")
        self.assertTrue(using.startswith("---\n"))
        self.assertIn("type: Project Knowledge", using)
        self.assertIn("status: stable", using)
        self.assertIn("[developer guide](developing.md)", using)
        self.assertNotIn("[[", using)
        self.run_cli("validate", "--project", str(project))

    def test_nonconformant_note_cannot_replace_previous_pair(self) -> None:
        project = self.generate_ready_project()
        before = self.snapshot(project / "skills")
        note = project / "notes" / "using.md"
        note.write_text(
            note.read_text(encoding="utf-8").replace(
                "type: Project Knowledge\n", ""
            ),
            encoding="utf-8",
        )

        result = self.run_cli(
            "generate", "--project", str(project), expected=2
        )
        self.assertIn("non-empty type", result.stderr)
        self.assertEqual(before, self.snapshot(project / "skills"))

    def test_generated_skill_pair_is_an_okf_bundle(self) -> None:
        project = self.generate_ready_project()
        skills = project / "skills"
        root_index = (skills / "index.md").read_text(encoding="utf-8")
        self.assertTrue(root_index.startswith("---\n"))
        self.assertIn('okf_version: "0.2"', root_index)
        for path in skills.rglob("*.md"):
            with self.subTest(path=path.relative_to(skills)):
                if path.name == "index.md":
                    continue
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"))
                frontmatter = text.split("---", 2)[1]
                self.assertIn("type:", frontmatter)

    def test_past_stale_after_excludes_consumer_knowledge(self) -> None:
        project = self.make_project()
        self.write_note(
            project,
            "usage",
            "usage",
            "# Usage\n\nOutdated guidance.\n",
            stale_after="2000-01-01",
        )
        self.write_note(
            project,
            "development",
            "development",
            "# Development\n\nInternal guidance.\n",
        )

        result = self.run_cli(
            "generate", "--project", str(project), expected=2
        )
        self.assertIn("Usage Skill requires", result.stderr)
        self.assertFalse((project / "skills").exists())

    def test_migration_rejects_ambiguous_wikilinks_without_partial_note_edits(self) -> None:
        project = self.root / "vault" / "Projects" / "ambiguous"
        notes = project / "notes"
        (notes / "one").mkdir(parents=True)
        (notes / "two").mkdir()
        source_text = (
            "# Usage\n\n"
            "---\nstatus: validated\naudience: usage\n---\n\n"
            "See [[shared]].\n"
        )
        (notes / "usage.md").write_text(source_text, encoding="utf-8")
        for directory in ("one", "two"):
            (notes / directory / "shared.md").write_text(
                "---\nstatus: validated\naudience: development\n---\n\n"
                f"# {directory.title()} Shared\n",
                encoding="utf-8",
            )

        result = self.run_cli(
            "migrate",
            "--project",
            str(project),
            "--project-id",
            "acme-ambiguous",
            expected=3,
        )
        self.assertIn("ambiguous Wikilink", result.stderr)
        self.assertEqual(source_text, (notes / "usage.md").read_text(encoding="utf-8"))
        self.assertFalse((notes / "index.md").exists())

    def test_invalid_okf_index_is_rejected(self) -> None:
        project = self.generate_ready_project()
        index = project / "notes" / "index.md"
        index.write_text(
            '---\nokf_version: "0.2"\ntitle: Not allowed\n---\n\n# Knowledge\n',
            encoding="utf-8",
        )

        result = self.run_cli(
            "validate", "--project", str(project), expected=2
        )
        self.assertIn("index.md frontmatter", result.stderr)

class ExperienceCompilationTest(ProjectionCliTest):
    """Post-cutover projection hygiene: packs never surface inside the pair."""

    def make_pack(
        self,
        project: Path,
        slug: str = "2026-09-02-demo",
        kind: str = "execution",
        payload: tuple[str, ...] = ("findings.md",),
        manifest_frontmatter: str | None = None,
        manifest_body: str | None = None,
    ) -> Path:
        pack = project / "evidence" / slug
        pack.mkdir(parents=True, exist_ok=True)
        for name in payload:
            (pack / name).write_text(f"# {name}\n\npack payload\n", encoding="utf-8")
        if manifest_frontmatter is None:
            manifest_frontmatter = (
                f"kind: {kind}\nproduced_by: story-001\ndate: 2026-09-02\n"
                'summary: "Demo pack for tests"'
            )
        if manifest_body is None:
            manifest_body = "\n".join(f"- {name}: role of {name}" for name in payload)
        (pack / "MANIFEST.md").write_text(
            f"---\n{manifest_frontmatter}\n---\n\n# Manifest\n\n{manifest_body}\n",
            encoding="utf-8",
        )
        return pack

    def test_generate_output_contains_no_evidence(self) -> None:
        project = self.generate_ready_project()
        self.run_cli("generate", "--project", str(project))
        published = project / "skills"
        for path in published.rglob("*"):
            self.assertNotIn("evidence", path.relative_to(published).parts)

class LinkRewriteTest(ProjectionCliTest):
    """Quick task: package-consistent link rewriting in projected references."""

    def test_same_package_links_survive(self) -> None:
        project = self.make_project()
        self.write_note(
            project, "alpha", "usage", "# Alpha\n\nSee [Beta](./beta.md).\n"
        )
        self.write_note(
            project, "beta", "usage", "# Beta\n\nSee [Alpha](./alpha.md).\n"
        )
        self.run_cli("generate", "--project", str(project))
        references = project / "skills" / "acme-demo-usage" / "references"
        alpha = (references / "alpha.md").read_text(encoding="utf-8")
        beta = (references / "beta.md").read_text(encoding="utf-8")
        self.assertIn("[Beta](./beta.md)", alpha)
        self.assertIn("[Alpha](./alpha.md)", beta)

    def test_unprojected_target_is_demoted(self) -> None:
        project = self.make_project()
        self.write_note(
            project,
            "published",
            "usage",
            "# Published\n\nSee [Draft](./draft.md) and [Dev](./dev.md).\n",
        )
        self.write_note(
            project, "draft", "draft", "# Draft\n\nPending.\n", status="draft"
        )
        self.write_note(
            project, "dev", "development", "# Dev\n\nContributor only.\n"
        )
        result = self.run_cli("generate", "--project", str(project))
        reference = (
            project / "skills" / "acme-demo-usage" / "references" / "published.md"
        ).read_text(encoding="utf-8")
        self.assertIn("**Draft**", reference)
        self.assertIn("**Dev**", reference)
        self.assertNotIn("(./draft.md)", reference)
        self.assertNotIn("(./dev.md)", reference)
        self.assertIn("draft.md", result.stderr)
        self.assertIn("dev.md", result.stderr)

    def test_no_demotion_warning_when_all_targets_projected(self) -> None:
        project = self.make_project()
        self.write_note(project, "solo", "usage", "# Solo\n\nNo links.\n")
        result = self.run_cli("generate", "--project", str(project))
        self.assertNotIn("demoted", result.stderr)

    def test_links_inside_code_fences_are_untouched(self) -> None:
        project = self.make_project()
        self.write_note(
            project,
            "fenced",
            "usage",
            "# Fenced\n\nSee [Draft](./draft.md).\n\n"
            "```markdown\n[Draft](./draft.md)\n```\n",
        )
        self.write_note(project, "draft", "draft", "# Draft\n\nPending.\n", status="draft")
        self.run_cli("generate", "--project", str(project))
        reference = (
            project / "skills" / "acme-demo-usage" / "references" / "fenced.md"
        ).read_text(encoding="utf-8")
        self.assertIn("**Draft**", reference)
        self.assertIn("[Draft](./draft.md)\n```", reference)




class CodeProvenanceTest(ExperienceCompilationTest):
    """Quick task: code provenance lines remain a read-only diagnostic."""

    def test_provenance_command_reports_clean_then_dirty(self) -> None:
        import subprocess

        repo = self.make_project()
        def git(*args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(repo), *args],
                capture_output=True, text=True, check=True,
            ).stdout.strip()

        git("init", "-q")
        git("config", "user.email", "test@example.com")
        git("config", "user.name", "Test")
        (repo / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        (repo / "notes").mkdir(exist_ok=True)
        (repo / "notes" / "seed.md").write_text("seed\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "seed")

        clean = self.run_cli("provenance", "--repo", str(repo)).stdout
        self.assertIn("git_head: ", clean)
        self.assertIn("worktree_tree: clean", clean)
        # no side effects on the real index or working tree
        self.assertEqual(git("status", "--porcelain"), "")

        (repo / "dirty.txt").write_text("dirty\n", encoding="utf-8")
        dirty = self.run_cli("provenance", "--repo", str(repo)).stdout
        head = git("rev-parse", "HEAD")
        self.assertIn(f"git_head: {head}", dirty)
        match = re.search(r"worktree_tree: ([0-9a-f]{40})", dirty)
        self.assertIsNotNone(match)
        self.assertNotEqual(match.group(1), git("rev-parse", f"{head}^{{tree}}"))
        # untracked file did not enter the real index
        self.assertEqual(git("status", "--porcelain"), "?? dirty.txt")




class MathDocsLayerTest(ExperienceCompilationTest):
    def write_math_pair(
        self,
        project: Path,
        slug: str = "force",
        status: str = "stable",
        include_metadata: bool = True,
    ) -> tuple[Path, Path]:
        mathdocs = project / "mathdocs"
        script = mathdocs / f"{slug}.py"
        script.write_text("print('{}')\n", encoding="utf-8")
        metadata = [
            "type: Math Derivation",
            f"status: {status}",
            f"derivation: {slug}.py",
        ]
        if include_metadata:
            metadata.extend(
                [
                    f"source_sha256: {hashlib.sha256(script.read_bytes()).hexdigest()}",
                    "python_version: 3.13.7",
                    "sympy_version: 1.14.0",
                    "verified_at: 2026-09-05T12:00:00Z",
                    "verified_host: test-host",
                    f"verified_directory: {project.parent.resolve()}",
                ]
            )
        note = mathdocs / f"{slug}.md"
        body = f"# {slug.title()}\n\n## Corrections\n"
        if status == "stable":
            body += (
                "\n<!-- KOSMIC-MATH-RESULTS:START -->\n"
                "## Verified Results\n\n"
                f"<!-- MathDoc: acme-demo/{slug}#value -->\n"
                "$$\n1\n$$\n"
                "<!-- KOSMIC-SREPR: Integer(1) -->\n"
                "<!-- KOSMIC-MATH-RESULTS:END -->\n"
            )
        note.write_text(
            "---\n" + "\n".join(metadata) + "\n---\n\n" + body,
            encoding="utf-8",
        )
        if status != "deprecated":
            with (mathdocs / "index.md").open("a", encoding="utf-8") as handle:
                handle.write(f"| [{slug}]({slug}.md) | {status} | {slug} result |\n")
        return script, note

    def test_stable_math_note_requires_metadata_and_current_hash(self) -> None:
        project = self.generate_ready_project()
        self.write_math_pair(project, include_metadata=False)
        missing = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("source_sha256", missing.stderr)

        shutil.rmtree(project / "mathdocs")
        self.make_mathdocs(project)
        script, _ = self.write_math_pair(project)
        self.run_cli("validate", "--project", str(project))
        script.write_text("print('{\"changed\": true}')\n", encoding="utf-8")
        stale = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("source_sha256", stale.stderr)
        self.assertIn("force.py", stale.stderr)

    def test_draft_metadata_may_be_pending_and_deprecated_is_not_indexed(self) -> None:
        project = self.generate_ready_project()
        self.write_math_pair(
            project, slug="draft-force", status="draft", include_metadata=False
        )
        self.write_math_pair(project, slug="old-force", status="deprecated")
        self.run_cli("validate", "--project", str(project))

    def write_protocol_pair(
        self,
        project: Path,
        slug: str,
        *,
        results: list[dict[str, str]] | None = None,
        python_version: str = "3.13.7",
        sympy_version: str = "1.14.0",
        script_suffix: str = "",
    ) -> tuple[Path, Path]:
        results = results or [
            {"name": "value", "srepr": "Integer(1)", "latex": "1"}
        ]
        payload = {
            "schema_version": 1,
            "python_version": python_version,
            "sympy_version": sympy_version,
            "results": results,
        }
        script_text = (
            "import json\n"
            f"print(json.dumps({payload!r}, sort_keys=True))\n"
            + script_suffix
        )
        mathdocs = project / "mathdocs"
        script = mathdocs / f"{slug}.py"
        project_id_match = re.search(
            r"^project_id:\s*(\S+)",
            (project / "ProjectEntry.md").read_text(encoding="utf-8"),
            re.MULTILINE,
        )
        assert project_id_match is not None
        project_id = project_id_match.group(1)
        script.write_text(script_text, encoding="utf-8")
        digest = hashlib.sha256(script.read_bytes()).hexdigest()
        result_blocks = "".join(
            f"<!-- MathDoc: {project_id}/{slug}#{result['name']} -->\n"
            f"$$\n{result['latex']}\n$$\n"
            f"<!-- KOSMIC-SREPR: {result['srepr']} -->\n"
            for result in results
        )
        note = mathdocs / f"{slug}.md"
        note.write_text(
            "---\n"
            "type: Math Derivation\n"
            "status: stable\n"
            f"derivation: {slug}.py\n"
            f"source_sha256: {digest}\n"
            f"python_version: {python_version}\n"
            f"sympy_version: {sympy_version}\n"
            "verified_at: 2026-09-05T12:00:00Z\n"
            "verified_host: test-host\n"
            f"verified_directory: {project.parent.resolve()}\n"
            "---\n\n"
            f"# {slug.title()}\n\n"
            "<!-- KOSMIC-MATH-RESULTS:START -->\n"
            "## Verified Results\n\n"
            f"{result_blocks}"
            "<!-- KOSMIC-MATH-RESULTS:END -->\n",
            encoding="utf-8",
        )
        with (mathdocs / "index.md").open("a", encoding="utf-8") as handle:
            handle.write(f"| [{slug}]({slug}.md) | stable | checked |\n")
        return script, note

    def test_check_math_valid_protocol_selection_and_read_only(self) -> None:
        project = self.generate_ready_project()
        self.write_protocol_pair(project, "beta")
        self.write_protocol_pair(project, "alpha")
        before = self.snapshot(project / "mathdocs")
        result = self.run_cli("check-math", "--project", str(project))
        self.assertIn("alpha, beta", result.stdout)
        self.assertIn("without an OS sandbox", result.stderr)
        self.assertEqual(before, self.snapshot(project / "mathdocs"))
        self.assertIn("alpha: PASS", result.stdout)
        self.assertIn("beta: PASS", result.stdout)

        selected = self.run_cli(
            "check-math", "--project", str(project), "--slug", "beta"
        )
        self.assertIn("beta", selected.stdout)
        self.assertNotIn("alpha", selected.stdout)

    def test_check_math_reports_each_file_before_failure_summary(self) -> None:
        project = self.generate_ready_project()
        alpha, _ = self.write_protocol_pair(project, "alpha")
        self.write_protocol_pair(project, "beta")
        alpha.write_text("print('not json')\n", encoding="utf-8")
        alpha_note = project / "mathdocs" / "alpha.md"
        alpha_note.write_text(
            re.sub(
                r"source_sha256: [0-9a-f]{64}",
                f"source_sha256: {hashlib.sha256(alpha.read_bytes()).hexdigest()}",
                alpha_note.read_text(encoding="utf-8"),
            ),
            encoding="utf-8",
        )

        result = self.run_cli("check-math", "--project", str(project), expected=2)
        self.assertIn("alpha: FAIL", result.stderr)
        self.assertIn("beta: PASS", result.stdout)
        self.assertIn("1 passed, 1 failed", result.stderr)

    def test_check_math_rejects_protocol_process_and_environment_failures(self) -> None:
        cases = {
            "malformed": "print('not json')\n",
            "nonzero": "raise SystemExit(7)\n",
            "extra": "print('noise')\n",
        }
        for index, (kind, suffix) in enumerate(cases.items()):
            with self.subTest(kind=kind):
                project = self.generate_ready_project(f"case-{index}")
                self.write_protocol_pair(project, kind, script_suffix=suffix)
                result = self.run_cli(
                    "check-math", "--project", str(project), expected=2
                )
                self.assertIn(kind, result.stderr)
                self.assertIn("remedy", result.stderr)
                shutil.rmtree(project)

        project = self.generate_ready_project("stale")
        self.write_protocol_pair(project, "stale", python_version="0.0.0")
        _, note = self.write_protocol_pair(
            project, "current", python_version="3.13.7"
        )
        note.write_text(
            note.read_text(encoding="utf-8").replace(
                "python_version: 3.13.7", "python_version: 9.9.9"
            ),
            encoding="utf-8",
        )
        result = self.run_cli(
            "check-math", "--project", str(project), "--slug", "current", expected=2
        )
        self.assertIn("python_version", result.stderr)

    def test_check_math_update_rewrites_only_metadata_and_generated_region(self) -> None:
        project = self.generate_ready_project()
        script, note = self.write_protocol_pair(project, "force")
        original = note.read_text(encoding="utf-8")
        prose = "\n## Assumptions\n\nKeep this exactly.\n\n## Corrections\n\nHuman history.\n"
        note.write_text(original + prose, encoding="utf-8")
        updated_results = [
            {"name": "value", "srepr": "Integer(2)", "latex": "2"}
        ]
        updated_payload = {
            "schema_version": 1,
            "python_version": "3.13.7",
            "sympy_version": "1.14.0",
            "results": updated_results,
        }
        script.write_text(
            "import json\n"
            f"print(json.dumps({updated_payload!r}, sort_keys=True))\n",
            encoding="utf-8",
        )

        self.run_cli(
            "check-math",
            "--project",
            str(project),
            "--update",
            "--source-root",
            str(project.parent),
        )
        updated = note.read_text(encoding="utf-8")
        self.assertIn("<!-- KOSMIC-SREPR: Integer(2) -->", updated)
        self.assertIn("$$\n2\n$$", updated)
        self.assertTrue(updated.endswith(prose))
        self.assertIn(
            f"source_sha256: {hashlib.sha256(script.read_bytes()).hexdigest()}",
            updated,
        )
        self.run_cli("check-math", "--project", str(project))

    def test_check_math_update_precedes_dependent_note_corrections(self) -> None:
        project = self.generate_ready_project()
        script, paired_note = self.write_protocol_pair(project, "force")
        note = self.write_note(
            project,
            "physics",
            "development",
            "# Physics\n\n"
            "<!-- MathDoc: acme-demo/force#value -->\n"
            "$$\n1\n$$\n",
        )
        note.write_text(
            note.read_text(encoding="utf-8").replace(
                "audience: development\n",
                "audience: development\nderivations: [mathdocs/force.py]\n",
            ),
            encoding="utf-8",
        )
        script.write_text(
            script.read_text(encoding="utf-8")
            .replace("'srepr': 'Integer(1)'", "'srepr': 'Integer(2)'")
            .replace("'latex': '1'", "'latex': '2'"),
            encoding="utf-8",
        )

        self.run_cli(
            "check-math",
            "--project",
            str(project),
            "--update",
            "--source-root",
            str(self.root),
        )
        self.assertIn("$$\n2\n$$", paired_note.read_text(encoding="utf-8"))
        stale = self.run_cli("generate", "--project", str(project), expected=2)
        self.assertIn("physics.md", stale.stderr)
        note.write_text(
            note.read_text(encoding="utf-8").replace("$$\n1\n$$", "$$\n2\n$$"),
            encoding="utf-8",
        )
        self.run_cli("generate", "--project", str(project))


    def test_check_math_update_is_all_or_none(self) -> None:
        project = self.generate_ready_project()
        alpha_script, _ = self.write_protocol_pair(project, "alpha")
        beta_script, _ = self.write_protocol_pair(project, "beta")
        alpha_script.write_text(
            alpha_script.read_text(encoding="utf-8").replace("Integer(1)", "Integer(2)"),
            encoding="utf-8",
        )
        beta_script.write_text("raise SystemExit(9)\n", encoding="utf-8")
        before = self.snapshot(project / "mathdocs")
        result = self.run_cli(
            "check-math", "--project", str(project), "--update", expected=2
        )
        self.assertIn("beta", result.stderr)
        self.assertEqual(before, self.snapshot(project / "mathdocs"))

    def test_stable_note_math_markers_resolve_and_match_results(self) -> None:
        project = self.generate_ready_project()
        self.write_protocol_pair(project, "force")
        note = self.write_note(
            project,
            "physics",
            "development",
            "# Physics\n\n"
            "<!-- MathDoc: acme-demo/force#value -->\n"
            "$$\n1\n$$\n\n"
            "<!-- MathDoc-Exposition: acme-demo/force -->\n"
            "$$\nx + 1\n$$\n",
        )
        note.write_text(
            note.read_text(encoding="utf-8").replace(
                "audience: development\n",
                "audience: development\nderivations: [mathdocs/force.py]\n",
            ),
            encoding="utf-8",
        )
        self.run_cli("generate", "--project", str(project))
        self.run_cli("validate", "--project", str(project))

        note.write_text(
            note.read_text(encoding="utf-8").replace("$$\n1\n$$", "$$\n2\n$$", 1),
            encoding="utf-8",
        )
        mismatch = self.run_cli("generate", "--project", str(project), expected=2)
        self.assertIn("physics.md", mismatch.stderr)
        self.assertIn("force#value", mismatch.stderr)

    def test_stable_note_marker_requires_declared_derivation(self) -> None:
        project = self.generate_ready_project()
        self.write_protocol_pair(project, "force")
        self.write_note(
            project,
            "physics",
            "development",
            "# Physics\n\n"
            "<!-- MathDoc: acme-demo/force#value -->\n"
            "$$\n1\n$$\n",
        )
        result = self.run_cli("generate", "--project", str(project), expected=2)
        self.assertIn("derivations", result.stderr)

    def test_stable_note_unmarked_display_math_fails(self) -> None:
        project = self.generate_ready_project()
        self.write_note(
            project,
            "physics",
            "development",
            "# Physics\n\n$$\n1\n$$\n",
        )
        result = self.run_cli("generate", "--project", str(project), expected=2)
        self.assertIn("MathDoc marker", result.stderr)

    def test_draft_dangling_and_fenced_markers_do_not_block(self) -> None:
        project = self.generate_ready_project()
        self.write_note(
            project,
            "draft-math",
            "development",
            "# Draft\n\n<!-- MathDoc: acme-demo/missing#value -->\n$$\n9\n$$\n",
            status="draft",
        )
        self.write_note(
            project,
            "literal",
            "development",
            "# Literal\n\n```markdown\n"
            "<!-- MathDoc: acme-demo/missing#value -->\n$$\n9\n$$\n```\n",
        )
        self.run_cli("generate", "--project", str(project))
        self.run_cli("validate", "--project", str(project))
    def write_math_work_item(
        self,
        project: Path,
        derivations: str | None,
        files: str | None,
    ) -> Path:
        item = project / "specs" / "quick-tasks" / "math-work.md"
        item.parent.mkdir(parents=True, exist_ok=True)
        fields = ["consumer_interface_change: false"]
        if derivations is not None:
            fields.append(f"derivations: {derivations}")
        if files is not None:
            fields.append(f"math_implementation_files: {files}")
        item.write_text(
            "---\n" + "\n".join(fields) + "\n---\n\n# Math work\n",
            encoding="utf-8",
        )
        return item

    def test_completion_math_gate_accepts_finite_source_references(self) -> None:
        project = self.generate_ready_project()
        self.write_protocol_pair(project, "force")
        source_root = self.root / "source"
        source = source_root / "src" / "model.py"
        source.parent.mkdir(parents=True)
        source.write_text(
            "# MathDoc: acme-demo/force#value\nforce = 1\n", encoding="utf-8"
        )
        item = self.write_math_work_item(
            project, "[force]", "[src/model.py]"
        )
        self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(item),
            "--source-root",
            str(source_root),
        )

    def test_completion_math_gate_requires_both_fields_and_known_results(self) -> None:
        project = self.generate_ready_project()
        self.write_protocol_pair(project, "force")
        source_root = self.root / "source"
        source_root.mkdir()
        source = source_root / "model.py"
        source.write_text(
            "# MathDoc: acme-demo/force#missing\nforce = 1\n", encoding="utf-8"
        )
        partial = self.write_math_work_item(project, "[force]", None)
        missing_field = self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(partial),
            "--source-root",
            str(source_root),
            expected=2,
        )
        self.assertIn("math_implementation_files", missing_field.stderr)

        item = self.write_math_work_item(project, "[force]", "[model.py]")
        unknown = self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(item),
            "--source-root",
            str(source_root),
            expected=2,
        )
        self.assertIn("missing", unknown.stderr)

    def test_completion_math_gate_rejects_escaping_and_uncovered_files(self) -> None:
        project = self.generate_ready_project()
        self.write_protocol_pair(project, "force")
        source_root = self.root / "source"
        source_root.mkdir()
        (source_root / "plain.py").write_text("force = 1\n", encoding="utf-8")

        for path in ("../escape.py", "/tmp/absolute.py", "plain.py"):
            with self.subTest(path=path):
                item = self.write_math_work_item(project, "[force]", f"[{path}]")
                result = self.run_cli(
                    "check-completion",
                    "--project",
                    str(project),
                    "--work-item",
                    str(item),
                    "--source-root",
                    str(source_root),
                    expected=2,
                )
                self.assertRegex(result.stderr, "path|reference")



    def make_mathdocs(self, project: Path) -> Path:
        root = project / "mathdocs"
        root.mkdir(exist_ok=True)
        (root / "index.md").write_text(self.EMPTY_MATH_INDEX, encoding="utf-8")
        return root

    def test_migrate_creates_mathdocs_index_without_overwrite(self) -> None:
        project = self.make_project()
        shutil.rmtree(project / "mathdocs")
        self.write_note(project, "using", "usage", "# Use\n\nRun it.\n")
        self.assertFalse((project / "mathdocs").exists())
        self.run_cli(
            "migrate", "--project", str(project), "--project-id", "acme-demo"
        )
        index = project / "mathdocs" / "index.md"
        self.assertEqual(self.EMPTY_MATH_INDEX, index.read_text(encoding="utf-8"))

        custom = self.EMPTY_MATH_INDEX + "\n<!-- retained -->\n"
        index.write_text(custom, encoding="utf-8")
        self.run_cli(
            "migrate", "--project", str(project), "--project-id", "acme-demo"
        )
        self.assertEqual(custom, index.read_text(encoding="utf-8"))
    def test_migrate_rejects_invalid_math_notes_before_publication(self) -> None:
        project = self.make_project()
        self.write_note(
            project,
            "physics",
            "development",
            "# Physics\n\n$$\n1\n$$\n",
        )
        before = self.snapshot(project / "notes")
        result = self.run_cli(
            "migrate",
            "--project",
            str(project),
            "--project-id",
            "acme-demo",
            expected=2,
        )
        self.assertIn("MathDoc marker", result.stderr)
        self.assertEqual(before, self.snapshot(project / "notes"))


    def test_validate_rejects_unpaired_mathdocs_files(self) -> None:
        project = self.generate_ready_project()
        mathdocs = self.make_mathdocs(project)
        (mathdocs / "force.py").write_text("print('x')\n", encoding="utf-8")
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("unpaired", result.stderr)
        self.assertIn("force.py", result.stderr)

    def test_validate_rejects_missing_unknown_and_status_mismatch_rows(self) -> None:
        project = self.generate_ready_project()
        mathdocs = self.make_mathdocs(project)
        (mathdocs / "force.py").write_text("print('{}')\n", encoding="utf-8")
        (mathdocs / "force.md").write_text(
            "---\ntype: Math Derivation\nstatus: draft\nderivation: force.py\n"
            "---\n\n# Force\n",
            encoding="utf-8",
        )

        missing = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("index", missing.stderr)
        self.assertIn("force", missing.stderr)

        (mathdocs / "index.md").write_text(
            self.EMPTY_MATH_INDEX
            + "| [force](force.md) | stable | force result |\n"
            + "| [ghost](ghost.md) | draft | absent |\n",
            encoding="utf-8",
        )
        invalid = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertRegex(invalid.stderr, "status|unknown")
    def test_task_m_workflow_and_templates_are_shipped(self) -> None:
        skill_root = REPO_ROOT / "skills"
        task = (skill_root / "references" / "task_math_note.md").read_text(
            encoding="utf-8"
        )
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("executable file is the authority", task)
        self.assertIn("check-math --update", task)
        self.assertIn("Task M: Math Note", task)
        self.assertIn("[task_math_note.md](references/task_math_note.md)", skill)
        self.assertTrue(
            (skill_root / "references" / "templates" / "template-math-index.md").is_file()
        )
        self.assertTrue(
            (skill_root / "references" / "templates" / "template-math-derivation.md").is_file()
        )
        script = (
            skill_root / "references" / "templates" / "template-math-derivation.py"
        )
        self.assertTrue(script.is_file())
        self.assertTrue(os.access(script, os.X_OK))


class SkillProposalTest(ExperienceCompilationTest):
    def test_all_routine_proposal_actions_validate_and_bad_mapping_fails(self) -> None:
        project = self.make_project("demo-routines")
        for action in ("create", "extend", "reuse", "keep_as_prose", "none"):
            with self.subTest(action=action):
                proposal = self.write_routine_proposal(project, action)
                self.run_cli("validate-proposal", "--project", str(project), "--proposal", str(proposal))
        proposal = self.write_routine_proposal(project, "create")
        proposal.write_text(
            proposal.read_text(encoding="utf-8").replace("result: create", "result: no_action"),
            encoding="utf-8",
        )
        self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(proposal),
            expected=2,
        )

    def test_validate_proposal_accepts_valid_create(self) -> None:
        project = self.make_project()
        proposal = self.write_proposal(project)
        result = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
        )
        self.assertIn("valid Skill Proposal", result.stdout)

    def test_validate_pending_proposal_prints_canonical_fingerprint(self) -> None:
        project = self.make_project()
        proposal = self.write_proposal(project)
        result = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(proposal)
        )
        self.assertRegex(result.stdout, r"fingerprint: [0-9a-f]{64}")

    def write_proposal_work_item(
        self, project: Path, required: str, reference: str | None
    ) -> Path:
        item = project / "specs" / "stories" / "proposal-work.md"
        item.parent.mkdir(parents=True, exist_ok=True)
        lines = [
            "consumer_interface_change: false",
            f"proposal_required: {required}",
        ]
        if reference is not None:
            lines.append(f"skill_proposal: {reference}")
        item.write_text(
            "---\n" + "\n".join(lines) + "\n---\n\n# Proposal work\n",
            encoding="utf-8",
        )
        return item

    def test_completion_requires_one_finished_proposal_when_declared(self) -> None:
        project = self.make_project()
        proposal = self.write_proposal(project, result="no_action")
        item = self.write_proposal_work_item(
            project, "true", "../skill-proposals/2026-09-06-demo.md"
        )
        pending = self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(item),
            expected=2,
        )
        self.assertIn("pending", pending.stderr)

        validated = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(proposal)
        )
        fingerprint = re.search(r"fingerprint: ([0-9a-f]{64})", validated.stdout).group(1)
        proposal.write_text(
            proposal.read_text(encoding="utf-8")
            .replace("status: draft", "status: done")
            .replace("decision: pending", "decision: accepted")
            .replace("fingerprint: \n", f"fingerprint: {fingerprint}\n"),
            encoding="utf-8",
        )
        self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(item),
        )

    def test_routine_completion_requires_unique_finished_proposals(self) -> None:
        project = self.make_project("routine-gate")
        (project / "specs" / "stories").mkdir(parents=True, exist_ok=True)
        item = project / "specs" / "stories" / "routine-work.md"
        item.write_text(
            "---\nconsumer_interface_change: false\nroutine_edge_change: true\nroutine_decision_required: false\n"
            "routine_proposals: []\n---\n\n# Routine work\n"
            "\n## Routine Decision\n\nA governed routine decision is required.\n",
            encoding="utf-8",
        )
        content = item.read_text(encoding="utf-8")
        item.write_text(
            content.replace("routine_edge_change: true\n", ""), encoding="utf-8"
        )
        absent = self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item),
            expected=2,
        )
        self.assertIn("must declare routine_edge_change", absent.stderr)
        item.write_text(content, encoding="utf-8")
        undeclared = self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item),
            expected=2,
        )
        self.assertIn("routine_edge_change", undeclared.stderr)
        item.write_text(
            item.read_text(encoding="utf-8").replace(
                "routine_decision_required: false", "routine_decision_required: true"
            ),
            encoding="utf-8",
        )
        missing = self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item),
            expected=2,
        )
        self.assertIn("routine_proposals", missing.stderr)

        proposal = self.write_routine_proposal(project, "none")
        checked = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(proposal)
        )
        fingerprint = re.search(r"fingerprint: ([0-9a-f]{64})", checked.stdout).group(1)
        proposal.write_text(
            proposal.read_text(encoding="utf-8")
            .replace("status: draft", "status: done")
            .replace("decision: pending", "decision: accepted")
            .replace('fingerprint: ""', f"fingerprint: {fingerprint}"),
            encoding="utf-8",
        )
        reference = "../skill-proposals/2026-09-07-none.md"
        item.write_text(
            item.read_text(encoding="utf-8").replace(
                "routine_proposals: []", f"routine_proposals: [{reference}, {reference}]"
            ),
            encoding="utf-8",
        )
        duplicate = self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item),
            expected=2,
        )
        self.assertIn("duplicate", duplicate.stderr)
        item.write_text(
            item.read_text(encoding="utf-8").replace(
                f"routine_proposals: [{reference}, {reference}]",
                f"routine_proposals: [{reference}]",
            ),
            encoding="utf-8",
        )
        self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item)
        )
    def test_routine_false_gate_rejects_proposals_and_missing_reason(self) -> None:
        project = self.make_project("routine-false")
        item = project / "routine-false.md"
        item.write_text(
            "---\nconsumer_interface_change: false\nroutine_edge_change: false\n"
            "routine_decision_required: false\nroutine_proposals: [proposal.md]\n"
            "---\n\n# Work\n\n## Routine Decision\n\nNo candidate.\n",
            encoding="utf-8",
        )
        populated = self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item),
            expected=2,
        )
        self.assertIn("requires empty routine_proposals", populated.stderr)
        item.write_text(
            item.read_text(encoding="utf-8")
            .replace("routine_proposals: [proposal.md]", "routine_proposals: []")
            .replace("## Routine Decision\n\nNo candidate.\n", ""),
            encoding="utf-8",
        )
        reasonless = self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item),
            expected=2,
        )
        self.assertIn("requires a Routine Decision reason", reasonless.stderr)

    def test_completion_accepts_finished_create_and_extend_with_evidence(self) -> None:
        project = self.make_project("routine-create-extend")
        self.make_pack(
            project, "2026-09-07-demo",
            payload=("result.md",),
        )
        references = []
        for action in ("create", "extend"):
            proposal = self.write_routine_proposal(project, action)
            proposal.write_text(
                proposal.read_text(encoding="utf-8").replace(
                    "behavioral_evidence: []",
                    "behavioral_evidence: [evidence/2026-09-07-demo/result.md]",
                ),
                encoding="utf-8",
            )
            checked = self.run_cli(
                "validate-proposal", "--project", str(project), "--proposal", str(proposal)
            )
            fingerprint = re.search(r"fingerprint: ([0-9a-f]{64})", checked.stdout).group(1)
            proposal.write_text(
                proposal.read_text(encoding="utf-8")
                .replace("status: draft", "status: done")
                .replace("decision: pending", "decision: accepted")
                .replace('fingerprint: ""', f"fingerprint: {fingerprint}"),
                encoding="utf-8",
            )
            references.append(f"../skill-proposals/{proposal.name}")
        item = project / "specs" / "stories" / "routine-create-extend.md"
        item.parent.mkdir(parents=True, exist_ok=True)
        item.write_text(
            "---\nconsumer_interface_change: false\nroutine_edge_change: true\n"
            "routine_decision_required: true\n"
            f"routine_proposals: [{', '.join(references)}]\n"
            "---\n\n# Routine changes\n\n## Routine Decision\n\nApproved candidates.\n",
            encoding="utf-8",
        )
        self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item)
        )

    def test_legacy_done_and_rejected_fingerprints_remain_byte_identical(self) -> None:
        project = self.make_project("legacy-fingerprints")
        accepted = self.write_proposal(project, result="no_action")
        accepted.write_text(
            accepted.read_text(encoding="utf-8").replace("artifact_role: procedure\n", ""),
            encoding="utf-8",
        )
        checked = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(accepted)
        )
        accepted_fingerprint = re.search(
            r"fingerprint: ([0-9a-f]{64})", checked.stdout
        ).group(1)
        accepted.write_text(
            accepted.read_text(encoding="utf-8")
            .replace("status: draft", "status: done")
            .replace("decision: pending", "decision: accepted")
            .replace("fingerprint: \n", f"fingerprint: {accepted_fingerprint}\n"),
            encoding="utf-8",
        )
        accepted_check = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(accepted)
        )
        self.assertIn(accepted_fingerprint, accepted_check.stdout)

        rejected = accepted.with_name("2026-09-07-legacy-rejected.md")
        rejected.write_text(
            accepted.read_text(encoding="utf-8")
            .replace("status: done", "status: draft")
            .replace("decision: accepted", "decision: pending")
            .replace(f"fingerprint: {accepted_fingerprint}", "fingerprint: ")
            .replace("Project facts only", "Uncertain evidence only"),
            encoding="utf-8",
        )
        checked = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(rejected)
        )
        rejected_fingerprint = re.search(
            r"fingerprint: ([0-9a-f]{64})", checked.stdout
        ).group(1)
        rejected.write_text(
            rejected.read_text(encoding="utf-8")
            .replace("status: draft", "status: done")
            .replace("decision: pending", "decision: rejected")
            .replace("fingerprint: \n", f"fingerprint: {rejected_fingerprint}\n"),
            encoding="utf-8",
        )
        rejected_check = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(rejected)
        )
        self.assertIn(rejected_fingerprint, rejected_check.stdout)


    def test_completion_rejects_proposal_path_when_not_required(self) -> None:
        project = self.make_project()
        item = self.write_proposal_work_item(
            project, "false", "../skill-proposals/2026-09-06-demo.md"
        )
        result = self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(item),
            expected=2,
        )
        self.assertIn("proposal_required: false", result.stderr)

    def test_rejected_fingerprint_blocks_equivalent_proposal(self) -> None:
        project = self.make_project()
        rejected = self.write_proposal(project)
        checked = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(rejected)
        )
        fingerprint = re.search(r"fingerprint: ([0-9a-f]{64})", checked.stdout).group(1)
        rejected.write_text(
            rejected.read_text(encoding="utf-8")
            .replace("status: draft", "status: done")
            .replace("decision: pending", "decision: rejected")
            .replace("fingerprint: \n", f"fingerprint: {fingerprint}\n"),
            encoding="utf-8",
        )
        duplicate = rejected.with_name("2026-09-07-demo-again.md")
        duplicate.write_text(
            rejected.read_text(encoding="utf-8")
            .replace("status: done", "status: draft")
            .replace("decision: rejected", "decision: pending")
            .replace(f"fingerprint: {fingerprint}", "fingerprint: "),
            encoding="utf-8",
        )
        result = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(duplicate),
            expected=2,
        )
        self.assertIn("equivalent rejected", result.stderr)

    def test_generated_descriptions_use_concrete_activation_triggers(self) -> None:
        project = self.generate_ready_project()
        self.run_cli("generate", "--project", str(project))
        usage = (project / "skills" / "acme-demo-usage" / "SKILL.md").read_text(
            encoding="utf-8"
        )
        development = (
            project / "skills" / "acme-demo-development" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "Use when invoking, configuring, integrating, validating, installing, or troubleshooting acme-demo consumer interfaces.",
            usage,
        )
        self.assertIn(
            "Use when changing, testing, reviewing, or releasing acme-demo implementation or development infrastructure.",
            development,
        )

    def test_check_installation_detects_current_and_stale_pair(self) -> None:
        project = self.generate_ready_project()
        self.run_cli("generate", "--project", str(project))
        home = self.root / "home"
        installed = self.run_cli(
            "install",
            "--project",
            str(project),
            "--adapter",
            "codex",
            "--home",
            str(home),
        )
        self.assertIn("installed on disk", installed.stdout)
        self.assertIn("active-session discovery unverified", installed.stdout)
        self.run_cli(
            "check-installation",
            "--project",
            str(project),
            "--adapter",
            "codex",
            "--home",
            str(home),
        )
        skill = home / ".agents" / "skills" / "acme-demo-usage" / "SKILL.md"
        skill.write_text(skill.read_text(encoding="utf-8") + "\nstale\n", encoding="utf-8")
        stale = self.run_cli(
            "check-installation",
            "--project",
            str(project),
            "--adapter",
            "codex",
            "--home",
            str(home),
            expected=2,
        )
        self.assertIn("installed Skill Pair", stale.stderr)

    def test_proposal_validation_rejects_stale_inputs_and_missing_independence(self) -> None:
        project = self.make_project()
        proposal = self.write_proposal(
            project, extra="scope_override: ignored\n"
        )
        proposal.write_text(
            proposal.read_text(encoding="utf-8")
            .replace("scope: project-procedure", "scope: global-procedure"),
            encoding="utf-8",
        )
        independence = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
            expected=2,
        )
        self.assertIn("requires proposer_mode: subagent", independence.stderr)

        proposal.write_text(
            proposal.read_text(encoding="utf-8")
            .replace("scope: global-procedure", "scope: project-procedure"),
            encoding="utf-8",
        )
        (project / "notes" / "index.md").write_text("# changed\n", encoding="utf-8")
        stale = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
            expected=2,
        )
        self.assertIn("missing or stale", stale.stderr)

    def test_approved_pending_proposal_is_valid(self) -> None:
        project = self.make_project()
        proposal = self.write_proposal(project)
        proposal.write_text(
            proposal.read_text(encoding="utf-8").replace(
                "status: draft", "status: approved"
            ),
            encoding="utf-8",
        )
        result = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(proposal)
        )
        self.assertIn("valid Skill Proposal", result.stdout)

    def test_fenced_heading_does_not_satisfy_required_section(self) -> None:
        project = self.make_project()
        proposal = self.write_proposal(project)
        text = proposal.read_text(encoding="utf-8").replace(
            "## Proposed Change\n\nCreate one repeatable diagnostic procedure.",
            "## Missing Change\n\n```markdown\n## Proposed Change\nfake\n```",
        )
        proposal.write_text(text, encoding="utf-8")
        result = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
            expected=2,
        )
        self.assertIn("Proposed Change", result.stderr)

    def test_candidate_path_cannot_be_canonical(self) -> None:
        project = self.make_project()
        proposal = self.write_proposal(project)
        proposal.write_text(
            proposal.read_text(encoding="utf-8").replace(
                ".scratch/candidate-skill", "skills/demo-usage"
            ),
            encoding="utf-8",
        )
        result = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
            expected=2,
        )
        self.assertIn("candidate path is canonical", result.stderr)

    def test_project_local_update_allows_same_agent_with_reason(self) -> None:
        project = self.make_project()
        proposal = self.write_proposal(project, result="update")
        result = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(proposal)
        )
        self.assertIn("valid Skill Proposal", result.stdout)

    def test_shared_procedure_targets_domain_and_requires_independent_proposer(self) -> None:
        project = self.make_project()
        domain = project.parent.parent / "Skills" / "abinit"
        domain.mkdir(parents=True)
        (domain / "SKILL.md").write_text(
            "---\ntype: Domain Skill\nid: abinit\nstatus: stable\n"
            "description: ABINIT procedures\nmaintainers: [alice]\n"
            "triggers: [abinit]\naliases: []\n---\n# ABINIT\n",
            encoding="utf-8",
        )
        proposal = self.write_proposal(project)
        text = proposal.read_text(encoding="utf-8")
        text = text.replace("scope: project-procedure", "scope: shared-procedure")
        text = text.replace("demo-skill", "abinit/usage/export-wavefunctions")
        text = text.replace(
            "target_ref: skill://", "target_ref: library-skill://"
        ).replace("proposer_mode: same-agent", "proposer_mode: subagent")
        proposal.write_text(text, encoding="utf-8")
        valid = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(proposal)
        )
        self.assertIn("valid Skill Proposal", valid.stdout)
        proposal.write_text(
            text.replace("proposer_mode: subagent", "proposer_mode: same-agent"),
            encoding="utf-8",
        )
        invalid = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
            expected=2,
        )
        self.assertIn("shared-procedure Skill Proposal requires proposer_mode: subagent", invalid.stderr)

    def test_shared_procedure_acceptance_requires_domain_maintainer(self) -> None:
        project = self.make_project()
        self.make_pack(project, "2026-09-06-governance")
        domain = project.parent.parent / "Skills" / "abinit"
        domain.mkdir(parents=True)
        (domain / "SKILL.md").write_text(
            "---\ntype: Domain Skill\nid: abinit\nstatus: stable\n"
            "description: ABINIT procedures\nmaintainers: [alice]\n"
            "triggers: [abinit]\naliases: []\n---\n# ABINIT\n",
            encoding="utf-8",
        )
        proposal = self.write_proposal(project)
        text = proposal.read_text(encoding="utf-8")
        text = text.replace("scope: project-procedure", "scope: shared-procedure")
        text = text.replace("demo-skill", "abinit/usage/export-wavefunctions")
        text = text.replace("target_ref: skill://", "target_ref: library-skill://")
        text = text.replace("proposer_mode: same-agent", "proposer_mode: subagent")
        text = text.replace("decision: pending", "decision: accepted")
        text = text.replace(
            "behavioral_evidence: []",
            "behavioral_evidence: [evidence/2026-09-06-governance/findings.md]",
        )
        text = text.replace('fingerprint: ""', "fingerprint: placeholder")
        text = text.replace("status: draft", "status: done")
        text = text.replace("proposer_reason:", "approved_by: mallory\nproposer_reason:")
        proposal.write_text(text, encoding="utf-8")
        result = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
            expected=2,
        )
        self.assertIn("OWNERSHIP_REQUIRED", result.stderr)


def _fixture_project_id(project: Path) -> str:
    match = re.search(
        r"^project_id:\s*([\w.-]+)",
        (project / "ProjectEntry.md").read_text(encoding="utf-8"),
        re.M,
    )
    return match.group(1) if match else ""


class HistoryIntegrityTest(ProjectionCliFixture, unittest.TestCase):
    """Story 001: configured historical inspection and canonical reporting."""

    def configure_history_policy(
        self, project: Path, policy_yaml: str, status_root: Path | None = None
    ) -> None:
        binding = f"status_root: {status_root}\n" if status_root is not None else ""
        entry = project / "ProjectEntry.md"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace(
                "working_state: working-tree\n",
                "working_state: working-tree\n" + binding + policy_yaml,
            ),
            encoding="utf-8",
        )

    def write_governor(self, project: Path, project_id: str) -> Path:
        governor = project / "specs" / "quick-tasks" / "2026-10-05-history-governor.md"
        governor.write_text(
            "---\n"
            f"project_id: {project_id}\n"
            "record_kind: quick-task\nlocal_id: history-governor\n"
            "subproject_id: null\nstatus: approved\n---\n\n"
            "# History Governor\n\n## Acceptance Criteria\n\n- [ ] Governs STATUS output\n",
            encoding="utf-8",
        )
        return governor

    def mark_fixture_done(self, project: Path) -> Path:
        quick_task = project / "specs" / "quick-tasks" / "2026-10-04-fixture-task.md"
        quick_task.write_text(
            quick_task.read_text(encoding="utf-8").replace(
                "status: approved", 'status: "done"'
            ),
            encoding="utf-8",
        )
        return quick_task

    def test_warn_mode_reports_selected_receiptless_done_as_unverified(self) -> None:
        project = self.generate_ready_project("demo-history")
        quick_task = self.mark_fixture_done(project)
        self.write_governor(project, "demo-history")
        status_root = self.root / "vault" / "status-demo"
        status_root.mkdir(parents=True, exist_ok=True)
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n",
            status_root,
        )
        before = quick_task.read_bytes()
        arguments = (
            "generate-status", "--project", str(project),
            "--work-record", "demo-history/quick-task/history-governor",
        )
        self.run_cli(*arguments)
        result = self.run_cli("validate", "--project", str(project))
        self.assertIn("specs/quick-tasks/2026-10-04-fixture-task.md", result.stderr)
        self.assertIn("unverified", result.stderr)
        self.assertIn("not audited", result.stderr)
        self.assertEqual(quick_task.read_bytes(), before)
        self.run_cli(*arguments)
        status = (status_root / "STATUS.md").read_text(encoding="utf-8")
        self.assertIn("done (unverified — not audited)", status)
        self.assertNotIn("done (receipt pending)", status)
        open_work = status.split("## Open Work", 1)[1].split("## Work Context", 1)[0]
        self.assertNotIn("Fixture Task", open_work)
        self.assertIn("## Historical Integrity", status)
        self.run_cli("validate", "--project", str(project))
        self.assertEqual(quick_task.read_bytes(), before)

    def test_absent_or_empty_policy_keeps_exact_baseline_behavior(self) -> None:
        project = self.generate_ready_project("demo-parity")
        status_root = self.root / "vault" / "status-parity"
        status_root.mkdir(parents=True, exist_ok=True)
        self.configure_history_policy(project, "", status_root)
        arguments = (
            "generate-status", "--project", str(project),
            "--work-record", "demo-parity/quick-task/fixture-task",
        )
        self.run_cli(*arguments)
        baseline_status = (status_root / "STATUS.md").read_bytes()
        validate_before = self.run_cli("validate", "--project", str(project))

        self.configure_history_policy(
            project,
            "history_integrity:\n  mode: warn\n  records: []\n",
        )
        validate_after = self.run_cli("validate", "--project", str(project))
        self.assertEqual(validate_before.stdout, validate_after.stdout)
        self.assertEqual(validate_before.stderr, validate_after.stderr)
        self.run_cli(*arguments)
        self.assertEqual(baseline_status, (status_root / "STATUS.md").read_bytes())

    def test_strict_mode_fails_on_missing_selected_done_receipt(self) -> None:
        project = self.generate_ready_project("demo-strict")
        quick_task = self.mark_fixture_done(project)
        self.write_governor(project, "demo-strict")
        status_root = self.root / "vault" / "status-strict"
        status_root.mkdir(parents=True, exist_ok=True)
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: strict\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n",
            status_root,
        )
        before = quick_task.read_bytes()
        self.run_cli(
            "generate-status",
            "--project",
            str(project),
            "--work-record",
            "demo-strict/quick-task/history-governor",
        )
        status_before = (status_root / "STATUS.md").read_bytes()
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("HISTORY_INTEGRITY", result.stderr)
        self.assertIn("specs/quick-tasks/2026-10-04-fixture-task.md", result.stderr)
        self.assertIn("receipt", result.stderr)
        self.assertEqual(quick_task.read_bytes(), before)
        self.assertEqual(status_before, (status_root / "STATUS.md").read_bytes())

    def test_configured_view_is_one_view_across_status_writers(self) -> None:
        project = self.generate_ready_project("demo-view")
        quick_tasks = project / "specs" / "quick-tasks"
        self.mark_fixture_done(project)
        (quick_tasks / "2026-10-06-other-done.md").write_text(
            "---\n"
            "project_id: demo-view\n"
            "record_kind: quick-task\nlocal_id: other-done\n"
            "subproject_id: null\nstatus: \"done\"\n---\n\n"
            "# Other Done\n\n## Acceptance Criteria\n\n- [ ] Unselected history\n",
            encoding="utf-8",
        )
        self.write_governor(project, "demo-view")
        status_root = self.root / "vault" / "status-view"
        status_root.mkdir(parents=True, exist_ok=True)
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n",
            status_root,
        )
        arguments = (
            "generate-status", "--project", str(project),
            "--work-record", "demo-view/quick-task/history-governor",
        )
        self.run_cli(*arguments)
        first = (status_root / "STATUS.md").read_bytes()
        self.run_cli(*arguments)
        self.assertEqual(first, (status_root / "STATUS.md").read_bytes())
        status = first.decode("utf-8")
        self.assertIn("done (unverified — not audited)", status)
        self.assertIn("done (receipt pending)", status)
        self.assertIn("## Historical Integrity", status)
        self.assertIn(
            "- Policy: warn mode; 1 configured record(s) reported without retrospective audit.",
            status,
        )
        open_work = status.split("## Open Work", 1)[1].split("## Historical Integrity", 1)[0]
        self.assertIn("History Governor", open_work)
        self.assertIn("Other Done", open_work)
        self.assertNotIn("Fixture Task", open_work)
        self.run_cli("validate", "--project", str(project))

    def test_selected_stale_proposal_skips_scan_but_direct_loader_stays_strict(self) -> None:
        project = self.generate_ready_project("demo-skip")
        governor = self.write_governor(project, "demo-skip")
        proposal = self.write_proposal(project)
        self._patch_proposal_catalog_metadata(project, proposal, "demo")
        stale_digest = hashlib.sha256(governor.read_bytes()).hexdigest()
        (project / "specs" / "skill-proposals" / "inputs" / "demo.md").write_text(
            f"- specs/quick-tasks/2026-10-05-history-governor.md: {stale_digest}\n",
            encoding="utf-8",
        )
        governor.write_text(
            governor.read_text(encoding="utf-8") + "\nLater edit drifts the pin.\n",
            encoding="utf-8",
        )
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/skill-proposals/2026-09-06-demo.md\n",
        )
        result = self.run_cli("validate", "--project", str(project))
        self.assertIn("specs/skill-proposals/2026-09-06-demo.md", result.stderr)
        self.assertIn("unverified", result.stderr)
        self.assertIn("not audited", result.stderr)
        self.assertNotIn("input_manifest", result.stderr)
        direct = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
            expected=2,
        )
        self.assertIn("input_manifest source missing or stale", direct.stderr)

    def test_unselected_proposals_remain_strict_under_configured_warn(self) -> None:
        project = self.generate_ready_project("demo-unselected")
        selected = self.write_proposal(project)
        base_text = selected.read_text(encoding="utf-8")
        self._patch_proposal_catalog_metadata(project, selected, "demo")
        broken = project / "specs" / "skill-proposals" / "2026-09-07-beta.md"
        broken.write_text(
            base_text
            .replace("decision: pending", "decision: accepted")
            .replace("status: draft", "status: done"),
            encoding="utf-8",
        )
        self._patch_proposal_catalog_metadata(project, broken, "beta")
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/skill-proposals/2026-09-06-demo.md\n",
        )
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("fingerprint mismatch", result.stderr)

    def test_operational_surfaces_gain_no_history_flags(self) -> None:
        project = self.generate_ready_project("demo-surface")
        status_root = self.root / "vault" / "status-surface"
        status_root.mkdir(parents=True, exist_ok=True)
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n",
            status_root,
        )
        check_help = self.run_cli("check-completion", "--help")
        self.assertNotIn("history", check_help.stdout)
        finish_help = self.run_cli("work", "finish", "--help")
        self.assertNotIn("history", finish_help.stdout)
        # Operational parsers gain no history flags: with otherwise valid
        # finish syntax the unsupported flag is refused and nothing mutates.
        refused = self.run_cli(
            "work", "finish",
            "--project", str(project),
            "--worktree", str(self.root / "vault"),
            "--work-record", "demo-surface/quick-task/fixture-task",
            "--scope", "project:specs/",
            "--history-audit",
            expected=2,
        )
        self.assertIn("unrecognized arguments", refused.stderr)
        self.assertFalse((project / ".kosmic" / "work-receipts").exists())

    def _patch_proposal_catalog_metadata(self, project: Path, proposal: Path, local_id: str) -> None:
        """Give a fixture proposal the catalog identity the scanner requires."""
        marker = 'reconsiders: ""\n'
        proposal.write_text(
            proposal.read_text(encoding="utf-8").replace(
                marker,
                marker
                + f"project_id: {_fixture_project_id(project)}\n"
                + "subproject_id: null\n"
                + "record_kind: proposal\n"
                + f"local_id: {local_id}\n",
                1,
            ),
            encoding="utf-8",
        )

    def test_configured_warn_on_bootstrap_flat_project_reports_unverified(self) -> None:
        project = self.generate_ready_project("demo-flat")
        # Force the sanctioned bootstrap-flat state: a flat feature
        # specification keeps the Project out of the owner-aware catalog.
        (project / "specs" / "prd.md").write_text(
            "---\nproject_id: demo-flat\nsubproject_id: null\nstatus: draft\n---\n\n"
            "# Flat Feature\n",
            encoding="utf-8",
        )
        quick_task = self.mark_fixture_done(project)
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n",
        )
        before = quick_task.read_bytes()
        result = self.run_cli("validate", "--project", str(project))
        self.assertIn("specs/quick-tasks/2026-10-04-fixture-task.md", result.stderr)
        self.assertIn("unverified", result.stderr)
        self.assertIn("not audited", result.stderr)
        self.assertNotIn("MIGRATION_REQUIRED", result.stderr)
        self.assertEqual(quick_task.read_bytes(), before)

    def test_strict_mode_fails_flat_legacy_done_without_or_with_corrupt_receipt(self) -> None:
        project = self.generate_ready_project("demo-flat-strict")
        (project / "specs" / "prd.md").write_text(
            "---\nproject_id: demo-flat-strict\nsubproject_id: null\nstatus: draft\n---\n\n"
            "# Flat Feature\n",
            encoding="utf-8",
        )
        quick_task = self.mark_fixture_done(project)
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: strict\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n",
        )
        before = quick_task.read_bytes()
        from skills.scripts.kosmic_dreams import receipt_name
        identity = "specs/quick-tasks/2026-10-04-fixture-task.md"
        receipt_path = (
            project / ".kosmic" / "work-receipts" / receipt_name(identity)
        )
        absent = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("HISTORY_INTEGRITY", absent.stderr)
        self.assertIn("specs/quick-tasks/2026-10-04-fixture-task.md", absent.stderr)
        self.assertIn("receipt", absent.stderr)
        self.assertFalse(receipt_path.parent.exists())

        # A present but corrupt receipt (matching envelope, wrong recorded
        # hash and proof) is still missing claimed completion proof under the
        # selected strict inspection; the read-only audit never rewrites it.
        receipt_path.parent.mkdir(parents=True)
        receipt_path.write_text(json.dumps({
            "schema": "kosmic.work-receipt/1",
            "identity": identity,
            "status": "successful",
            "record_path": identity,
            "record_sha256": "0" * 64,
            "proof": {identity: "0" * 64},
        }), encoding="utf-8")
        corrupt_bytes = receipt_path.read_bytes()
        corrupt = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("HISTORY_INTEGRITY", corrupt.stderr)
        self.assertIn("specs/quick-tasks/2026-10-04-fixture-task.md", corrupt.stderr)
        self.assertEqual(receipt_path.read_bytes(), corrupt_bytes)
        self.assertEqual(quick_task.read_bytes(), before)

    def test_valid_receipt_keeps_current_done_row_in_degraded_report(self) -> None:
        from skills.scripts import kosmic_completion
        from skills.scripts import kosmic_dreams
        from skills.scripts import kosmic_project_skills as cli

        project = self.generate_ready_project("demo-closed")
        self.mark_fixture_done(project)
        self.write_governor(project, "demo-closed")
        identity = "demo-closed/quick-task/fixture-task"
        record = project / "specs" / "quick-tasks" / "2026-10-04-fixture-task.md"
        record_sha256 = hashlib.sha256(record.read_bytes()).hexdigest()
        receipt = {
            "schema": "kosmic.work-receipt/1",
            "identity": identity,
            "status": "successful",
            "record_path": "specs/quick-tasks/2026-10-04-fixture-task.md",
            "record_sha256": record_sha256,
            "proof": {"specs/quick-tasks/2026-10-04-fixture-task.md": record_sha256},
        }
        store = project / ".kosmic" / "work-receipts"
        store.mkdir(parents=True)
        (store / kosmic_dreams.receipt_name(identity)).write_text(
            json.dumps(receipt), encoding="utf-8")
        # Break whole-catalog enumeration with a malformed sibling
        # SubprojectEntry, forcing the degraded bounded structural report.
        broken = project / "subprojects" / "broken"
        broken.mkdir(parents=True)
        (broken / "SubprojectEntry.md").write_text("plain prose, no frontmatter\n")
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-05-history-governor.md\n",
        )
        configured = cli.load_project(project)
        with self.assertRaises(cli.SpecError):
            cli.render_status(configured, "no-head")
        rendered = cli.render_status(configured, "no-head", structural_bounded=True).decode("utf-8")
        self.assertIn("| [Fixture Task]", rendered)
        self.assertIn(" | done | ", rendered)
        self.assertNotIn("done (receipt pending)", rendered)
        self.assertEqual(
            kosmic_completion.check_terminal_receipt(
                project, cli.SpecCatalog.bounded(project, None).resolve(identity),
            )["identity"],
            identity,
        )

    def test_history_audit_reports_missing_receipt_before_stale_status(self) -> None:
        from skills.scripts import kosmic_dreams

        project_id = "demo-audit-stale-status"
        project = self.generate_ready_project(project_id)
        self.mark_fixture_done(project)
        self.write_governor(project, project_id)
        identity = f"{project_id}/quick-task/fixture-task"
        record = project / "specs" / "quick-tasks" / "2026-10-04-fixture-task.md"
        record_sha256 = hashlib.sha256(record.read_bytes()).hexdigest()
        receipt = {
            "schema": "kosmic.work-receipt/1",
            "identity": identity,
            "status": "successful",
            "record_path": "specs/quick-tasks/2026-10-04-fixture-task.md",
            "record_sha256": record_sha256,
            "proof": {"specs/quick-tasks/2026-10-04-fixture-task.md": record_sha256},
        }
        store = project / ".kosmic" / "work-receipts"
        store.mkdir(parents=True)
        receipt_path = store / kosmic_dreams.receipt_name(identity)
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        status_root = self.root / "vault" / "audit-stale-status"
        status_root.mkdir()
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: strict\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n",
            status_root,
        )
        work_record = f"{project_id}/quick-task/history-governor"
        self.run_cli(
            "generate-status", "--project", str(project),
            "--work-record", work_record,
        )
        self.run_cli("validate", "--project", str(project))
        status_before = (status_root / "STATUS.md").read_bytes()

        # The only intentional mutation is this receipt removal. STATUS now
        # reflects the prior valid receipt and is stale after the removal.
        receipt_path.unlink()
        before_audit = self.snapshot(self.root)
        audited = self.run_cli(
            "validate", "--project", str(project), "--history-audit", expected=2)
        self.assertIn("HISTORY_INTEGRITY", audited.stderr)
        self.assertNotIn("STATUS_STALE", audited.stderr)
        self.assertEqual(before_audit, self.snapshot(self.root))
        self.assertEqual(status_before, (status_root / "STATUS.md").read_bytes())

        ordinary = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("STATUS_STALE", ordinary.stderr)


    def test_strict_mode_fails_stale_selected_proposal_pin(self) -> None:
        project = self.generate_ready_project("demo-strict-pin")
        governor = self.write_governor(project, "demo-strict-pin")
        proposal = self.write_proposal(project)
        self._patch_proposal_catalog_metadata(project, proposal, "demo")
        pinned_governor = governor.read_bytes()
        stale_digest = hashlib.sha256(pinned_governor).hexdigest()
        (project / "specs" / "skill-proposals" / "inputs" / "demo.md").write_text(
            f"- specs/quick-tasks/2026-10-05-history-governor.md: {stale_digest}\n",
            encoding="utf-8",
        )
        governor.write_text(
            governor.read_text(encoding="utf-8") + "\nLater edit drifts the pin.\n",
            encoding="utf-8",
        )
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/skill-proposals/2026-09-06-demo.md\n",
        )
        before_proposal = proposal.read_bytes()
        before_governor = governor.read_bytes()

        warn = self.run_cli("validate", "--project", str(project))
        self.assertIn("specs/skill-proposals/2026-09-06-demo.md", warn.stderr)
        self.assertIn("unverified", warn.stderr)
        self.assertIn("not audited", warn.stderr)

        entry = project / "ProjectEntry.md"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace("mode: warn", "mode: strict"),
            encoding="utf-8",
        )
        strict = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("HISTORY_INTEGRITY", strict.stderr)
        self.assertIn("specs/skill-proposals/2026-09-06-demo.md", strict.stderr)
        self.assertIn("input_manifest source missing or stale", strict.stderr)
        self.assertEqual(proposal.read_bytes(), before_proposal)
        self.assertEqual(governor.read_bytes(), before_governor)

        direct = self.run_cli(
            "validate-proposal",
            "--project",
            str(project),
            "--proposal",
            str(proposal),
            expected=2,
        )
        self.assertIn("input_manifest source missing or stale", direct.stderr)

        # Restoring the pinned bytes makes the selected proposal audited
        # clean: strict validate passes and claims no un-audited state for it.
        governor.write_bytes(pinned_governor)
        clean = self.run_cli("validate", "--project", str(project))
        self.assertNotIn("specs/skill-proposals/2026-09-06-demo.md", clean.stderr)
        self.assertNotIn("unverified", clean.stderr)
        self.assertEqual(proposal.read_bytes(), before_proposal)

    def test_history_audit_requires_configured_nonempty_scope(self) -> None:
        project = self.generate_ready_project("demo-history-audit-scope")
        absent = self.run_cli(
            "validate", "--project", str(project), "--history-audit", expected=2)
        self.assertIn("HISTORY_AUDIT_SCOPE_REQUIRED", absent.stderr)
        self.assertNotIn("valid Skill Pair", absent.stdout)

        self.configure_history_policy(
            project, "history_integrity:\n  mode: warn\n  records: []\n")
        empty = self.run_cli(
            "validate", "--project", str(project), "--history-audit", expected=2)
        self.assertIn("HISTORY_AUDIT_SCOPE_REQUIRED", empty.stderr)
        self.assertNotIn("valid Skill Pair", empty.stdout)

    def test_history_audit_missing_receipt_fails_in_warn_and_strict_modes(self) -> None:
        project = self.generate_ready_project("demo-history-audit-receipt")
        quick_task = self.mark_fixture_done(project)
        self.write_governor(project, "demo-history-audit-receipt")
        status_root = self.root / "vault" / "history-audit-status"
        status_root.mkdir(parents=True)
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n",
            status_root,
        )
        status = status_root / "STATUS.md"
        self.run_cli(
            "generate-status", "--project", str(project),
            "--work-record", "demo-history-audit-receipt/quick-task/history-governor",
        )
        status_before = status.read_bytes()
        before = self.snapshot(self.root)
        result = self.run_cli(
            "validate", "--project", str(project), "--history-audit", expected=2)
        self.assertIn("HISTORY_INTEGRITY", result.stderr)
        self.assertIn("receipt", result.stderr.lower())
        self.assertEqual(before, self.snapshot(self.root))
        self.assertEqual(status_before, status.read_bytes())
        self.assertTrue(quick_task.exists())
        # Regeneration uses the unchanged warn policy and must reproduce the
        # canonical bytes from before the read-only audit.
        self.run_cli(
            "generate-status", "--project", str(project),
            "--work-record", "demo-history-audit-receipt/quick-task/history-governor",
        )
        self.assertEqual(status_before, status.read_bytes())
        entry = project / "ProjectEntry.md"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace("mode: warn", "mode: strict"),
            encoding="utf-8",
        )
        self.run_cli(
            "generate-status", "--project", str(project),
            "--work-record", "demo-history-audit-receipt/quick-task/history-governor",
        )
        strict_before = self.snapshot(self.root)
        strict_status_before = status.read_bytes()
        strict = self.run_cli(
            "validate", "--project", str(project), "--history-audit", expected=2)
        self.assertIn("HISTORY_INTEGRITY", strict.stderr)
        self.assertIn("receipt", strict.stderr.lower())
        self.assertEqual(strict_before, self.snapshot(self.root))
        self.assertEqual(strict_status_before, status.read_bytes())

    def test_history_audit_passes_valid_proposal_pins_without_claiming_authority(self) -> None:
        project = self.generate_ready_project("demo-history-audit-pin")
        governor = self.write_governor(project, "demo-history-audit-pin")
        proposal = self.write_proposal(project)
        self._patch_proposal_catalog_metadata(project, proposal, "demo")
        digest = hashlib.sha256(governor.read_bytes()).hexdigest()
        manifest = project / "specs" / "skill-proposals" / "inputs" / "demo.md"
        manifest.write_text(
            f"- specs/quick-tasks/2026-10-05-history-governor.md: {digest}\n",
            encoding="utf-8",
        )
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/skill-proposals/2026-09-06-demo.md\n",
        )
        before = self.snapshot(self.root)
        result = self.run_cli(
            "validate", "--project", str(project), "--history-audit")
        self.assertIn("history audit passed", result.stdout.lower())
        self.assertIn("configured record", result.stdout.lower())
        self.assertIn("invocation-time", result.stdout.lower())
        self.assertIn("not completion proof or authority", result.stdout.lower())
        self.assertNotIn("not audited", result.stderr)
        self.assertEqual(before, self.snapshot(self.root))

    def test_history_audit_fails_stale_proposal_pin(self) -> None:
        project = self.generate_ready_project("demo-history-audit-stale-pin")
        governor = self.write_governor(project, "demo-history-audit-stale-pin")
        proposal = self.write_proposal(project)
        self._patch_proposal_catalog_metadata(project, proposal, "demo")
        digest = hashlib.sha256(governor.read_bytes()).hexdigest()
        manifest = project / "specs" / "skill-proposals" / "inputs" / "demo.md"
        manifest.write_text(
            f"- specs/quick-tasks/2026-10-05-history-governor.md: {digest}\n",
            encoding="utf-8",
        )
        governor.write_text(
            governor.read_text(encoding="utf-8") + "\nDrifted after pin.\n",
            encoding="utf-8",
        )
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/skill-proposals/2026-09-06-demo.md\n",
        )
        before = self.snapshot(self.root)
        result = self.run_cli(
            "validate", "--project", str(project), "--history-audit", expected=2)
        self.assertIn("HISTORY_INTEGRITY", result.stderr)
        self.assertIn("input_manifest source missing or stale", result.stderr)
        self.assertEqual(before, self.snapshot(self.root))

    def test_history_audit_rejects_invalid_scope_before_validation(self) -> None:
        project = self.generate_ready_project("demo-history-audit-invalid")
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/quick-tasks/missing.md\n",
        )
        result = self.run_cli(
            "validate", "--project", str(project), "--history-audit", expected=2)
        self.assertIn("unknown or stale", result.stderr)
        self.assertNotIn("valid Skill Pair", result.stdout)


    def test_empty_curated_manifest_stays_strict_operationally_and_in_history_audit(self) -> None:
        project = self.generate_ready_project("demo-empty-manifest")
        proposal = self.write_proposal(project)
        self._patch_proposal_catalog_metadata(project, proposal, "demo")
        manifest = project / "specs" / "skill-proposals" / "inputs" / "demo.md"
        manifest.write_text("# intentionally empty\n", encoding="utf-8")
        proposal_before = proposal.read_bytes()
        manifest_before = manifest.read_bytes()

        direct = self.run_cli(
            "validate-proposal", "--project", str(project), "--proposal", str(proposal),
            expected=2,
        )
        self.assertIn("input_manifest must list at least one input", direct.stderr)

        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: strict\n"
            "  records:\n"
            "    - specs/skill-proposals/2026-09-06-demo.md\n",
        )
        strict = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("HISTORY_INTEGRITY", strict.stderr)
        self.assertIn("input_manifest must list at least one input", strict.stderr)

        entry = project / "ProjectEntry.md"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace("mode: strict", "mode: warn"),
            encoding="utf-8",
        )
        warning = self.run_cli("validate", "--project", str(project))
        self.assertIn("unverified", warning.stderr)
        self.assertIn("not audited", warning.stderr)
        self.assertEqual(proposal.read_bytes(), proposal_before)
        self.assertEqual(manifest.read_bytes(), manifest_before)

    def test_bounded_report_intersects_foreign_history_scope_before_lookup(self) -> None:
        from skills.scripts import kosmic_project_skills as cli

        project = self.generate_ready_project("demo-bounded-history")
        foreign_specs = project / "subprojects" / "foreign" / "specs" / "quick-tasks"
        foreign_specs.mkdir(parents=True)
        (project / "subprojects" / "foreign" / "SubprojectEntry.md").write_text(
            "---\nschema: kosmic.subproject/1\n"
            "project_id: demo-bounded-history\nsubproject_id: foreign\n"
            "linked_prd: prd.md\n---\n\n# Foreign\n",
            encoding="utf-8",
        )
        (foreign_specs / "2026-10-06-foreign.md").write_text(
            "---\nproject_id: demo-bounded-history\nsubproject_id: foreign\n"
            "record_kind: quick-task\nlocal_id: foreign\nstatus: approved\n"
            "---\n\n# Foreign Task\n",
            encoding="utf-8",
        )
        broken = project / "subprojects" / "broken"
        broken.mkdir(parents=True)
        (broken / "SubprojectEntry.md").write_text(
            "plain prose, no frontmatter\n", encoding="utf-8")
        status_root = self.root / "vault" / "status-bounded-history"
        status_root.mkdir(parents=True)
        self.configure_history_policy(
            project,
            "history_integrity:\n"
            "  mode: warn\n"
            "  records:\n"
            "    - specs/quick-tasks/2026-10-04-fixture-task.md\n"
            "    - subprojects/foreign/specs/quick-tasks/2026-10-06-foreign.md\n",
            status_root,
        )
        configured = cli.load_project(project)
        rendered = cli.render_status(
            configured, "no-head", structural_bounded=True).decode("utf-8")
        self.assertIn("Scope: bounded active-record view (shared records only)", rendered)
        self.assertIn("Fixture Task", rendered)
        self.assertNotIn("Foreign Task", rendered)
        self.assertIn(
            "- Policy: warn mode; 1 configured record(s) reported without retrospective audit.",
            rendered,
        )
        (status_root / "STATUS.md").write_text(rendered, encoding="utf-8")
        self.assertFalse(cli.status_drift(
            configured, record_scoped=True, record_owner=None))

        # The same bounded scope still refuses a missing configured subject
        # that is actually inside its shared-record intersection.
        entry = project / "ProjectEntry.md"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace(
                "    - subprojects/foreign/specs/quick-tasks/2026-10-06-foreign.md\n",
                "    - subprojects/foreign/specs/quick-tasks/2026-10-06-foreign.md\n"
                "    - specs/quick-tasks/missing-in-scope.md\n",
            ),
            encoding="utf-8",
        )
        invalid = cli.load_project(project)
        with self.assertRaises(cli.KosmicError) as caught:
            cli.render_status(invalid, "no-head", structural_bounded=True)
        self.assertIn("unknown or stale", str(caught.exception))

    def test_invalid_policy_scopes_fail_validate_hard(self) -> None:
        def minimal_project(name: str) -> Path:
            project = self.root / "vault" / "Projects" / name
            project.mkdir(parents=True, exist_ok=True)
            (project / "ProjectEntry.md").write_text(
                f"---\nproject_id: {name}\nworking_state: working-tree\n---\n\n# {name}\n",
                encoding="utf-8",
            )
            return project

        def policy(records: str, mode: str = "warn") -> str:
            return (
                "history_integrity:\n"
                f"  mode: {mode}\n"
                "  records:\n"
                f"{records}"
            )

        selected = "    - specs/quick-tasks/2026-10-04-fixture-task.md\n"
        wrong_owner_project = minimal_project("demo-wrong-owner")
        owner_base = wrong_owner_project / "subprojects" / "left" / "specs" / "stories"
        owner_base.mkdir(parents=True)
        (wrong_owner_project / "subprojects" / "left" / "SubprojectEntry.md").write_text(
            "---\nschema: kosmic.subproject/1\n"
            "project_id: demo-wrong-owner\n"
            "subproject_id: left\n---\n\n# Left\n",
            encoding="utf-8",
        )
        (owner_base / "story-001.md").write_text(
            "---\nproject_id: demo-wrong-owner\nsubproject_id: right\n"
            "record_kind: story\nlocal_id: \"001\"\n---\n\n# Spoofed\n",
            encoding="utf-8",
        )
        cases = {
            "non-mapping": ("demo-non-mapping", "history_integrity: warn\n", "must be a mapping"),
            "unknown-key": (
                "demo-unknown-key",
                "history_integrity:\n  record:\n" + selected,
                "unknown keys",
            ),
            "bad-mode": ("demo-bad-mode", policy(selected, mode="audit"), "mode must be one of"),
            "duplicate": (
                "demo-duplicate",
                policy(selected + selected),
                "duplicates a path",
            ),
            "absolute": ("demo-absolute", policy("    - /etc/passwd\n"), "Project-relative"),
            "traversal": (
                "demo-traversal",
                policy("    - specs/../notes/index.md\n"),
                "not canonical",
            ),
            "uncontained": (
                "demo-uncontained",
                policy("    - notes/index.md\n"),
                "must name a spec record",
            ),
            "unknown-path": (
                "demo-unknown-path",
                policy("    - specs/quick-tasks/missing-record.md\n"),
                "unknown or stale",
            ),
            "wrong-owner": (
                "demo-wrong-owner",
                policy("    - subprojects/left/specs/stories/story-001.md\n"),
                "OWNER_MISMATCH",
            ),
        }
        for name, (dirname, policy_yaml, expected) in cases.items():
            with self.subTest(case=name):
                project = minimal_project(dirname)
                entry = project / "ProjectEntry.md"
                entry.write_text(
                    entry.read_text(encoding="utf-8").replace(
                        "working_state: working-tree\n",
                        "working_state: working-tree\n" + policy_yaml,
                    ),
                    encoding="utf-8",
                )
                result = self.run_cli("validate", "--project", str(project), expected=2)
                self.assertIn(expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
