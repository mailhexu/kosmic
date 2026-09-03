from __future__ import annotations

import hashlib
import json
import re
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "scripts" / "kosmic_project_skills.py"


class ProjectionCliTest(unittest.TestCase):
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
        notes.mkdir(parents=True)
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
    ) -> Path:
        metadata = [f"type: {concept_type}", f"status: {status}"]
        if audience is not None:
            metadata.append(f"audience: {audience}")
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
        work_item.parent.mkdir(parents=True)
        work_item.write_text(
            "---\nconsumer_interface_change: true\nrelated_notes: [using]\n---\n# Change\n",
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
    """Stories 1-7: evidence layer, note linkage, impact ledger, completion gate."""

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

    def write_note_with_evidence(
        self, project: Path, name: str, status: str, evidence: str
    ) -> Path:
        note = project / "notes" / f"{name}.md"
        note.write_text(
            "---\n"
            "type: Project Knowledge\n"
            f"status: {status}\n"
            "audience: development\n"
            f"evidence: {evidence}\n"
            "---\n\n"
            f"# {name}\n\nBody.\n",
            encoding="utf-8",
        )
        return note

    def write_work_item(
        self, project: Path, extra_frontmatter: str = ""
    ) -> Path:
        item = project / "specs" / "stories" / "story-001-demo.md"
        item.parent.mkdir(parents=True, exist_ok=True)
        item.write_text(
            "---\n"
            "status: approved\n"
            "consumer_interface_change: false\n"
            f"{extra_frontmatter}"
            "---\n\n# Story\n",
            encoding="utf-8",
        )
        return item

    def append_ledger(self, project: Path, text: str) -> Path:
        ledger = project / "impact.md"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        if not ledger.is_file():
            ledger.write_text("# Impact Ledger\n\n", encoding="utf-8")
        with ledger.open("a", encoding="utf-8") as handle:
            handle.write(text)
        return ledger

    # Story 1: root-walk tolerance

    def test_validate_and_generate_tolerate_evidence_layer(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, payload=("findings.md", "transcript.jsonl"))
        self.append_ledger(
            project,
            "- date: 2026-09-02 | kind: publication | targets: [notes/using.md] | "
            'refs: "null->abc" | outcome: published | reason: ""\n',
        )
        self.run_cli("generate", "--project", str(project))
        self.run_cli("validate", "--project", str(project))

    def test_generate_output_contains_no_evidence(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project)
        self.run_cli("generate", "--project", str(project))
        published = project / "skills"
        for path in published.rglob("*"):
            self.assertNotIn("evidence", path.relative_to(published).parts)

    # Story 2: MANIFEST validation

    def test_valid_packs_of_both_kinds_pass(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, "2026-09-02-run", kind="execution")
        self.make_pack(project, "2026-09-02-paper", kind="research")
        self.run_cli("validate", "--project", str(project))

    def test_manifest_invalid_kind_fails(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, manifest_frontmatter=(
            "kind: experiment\nproduced_by: story-001\ndate: 2026-09-02\n"
            'summary: "bad kind"'
        ))
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("kind", result.stderr)

    def test_manifest_missing_field_fails(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, manifest_frontmatter=(
            "kind: execution\ndate: 2026-09-02\nsummary: \"no producer\""
        ))
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("produced_by", result.stderr)

    def test_manifest_body_disk_mismatch_fails(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(
            project,
            payload=("findings.md", "unlisted.md"),
            manifest_body="- findings.md: the only listed file",
        )
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("unlisted.md", result.stderr)

    # Story 4: evidence frontmatter

    def test_stable_note_resolvable_evidence_passes(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project)
        self.write_note_with_evidence(
            project, "linked", "stable", "[evidence/2026-09-02-demo/findings.md]"
        )
        self.run_cli("generate", "--project", str(project))
        self.run_cli("validate", "--project", str(project))

    def test_stable_note_dangling_evidence_fails(self) -> None:
        project = self.generate_ready_project()
        self.write_note_with_evidence(
            project, "dangling", "stable", "[evidence/2026-09-02-missing/findings.md]"
        )
        result = self.run_cli("generate", "--project", str(project), expected=2)
        self.assertIn("evidence/2026-09-02-missing/findings.md", result.stderr)

    def test_deprecated_note_does_not_satisfy_linkage(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, "2026-09-02-demo")
        self.write_note_with_evidence(
            project, "retired", "deprecated", "[evidence/2026-09-02-demo/findings.md]"
        )
        item = self.write_work_item(project, "evidence_packs: [2026-09-02-demo]\n")
        result = self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(item),
            expected=2,
        )
        self.assertIn("2026-09-02-demo", result.stderr)

    def test_draft_note_dangling_evidence_passes(self) -> None:
        project = self.generate_ready_project()
        self.write_note_with_evidence(
            project, "pending", "draft", "[evidence/2026-09-02-missing/findings.md]"
        )
        self.run_cli("generate", "--project", str(project))

    # Story 5: ledger validation

    def test_valid_ledger_entries_pass(self) -> None:
        project = self.generate_ready_project()
        self.append_ledger(
            project,
            "- date: 2026-09-02 | kind: publication | targets: [notes/using.md] | "
            'refs: "null->abc" | outcome: published | reason: ""\n'
            "- date: 2026-09-02 | kind: decision | targets: [notes/old.md] | "
            'refs: story-002 | outcome: rejected | reason: "contradicts finding"\n',
        )
        self.run_cli("validate", "--project", str(project))

    def test_malformed_ledger_fails(self) -> None:
        project = self.generate_ready_project()
        self.append_ledger(
            project,
            "- date: 2026-09-02 | kind: mutation | targets: [notes/using.md] | "
            'refs: "null" | outcome: published | reason: ""\n',
        )
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("kind", result.stderr)

    def test_ledger_missing_field_fails(self) -> None:
        project = self.generate_ready_project()
        self.append_ledger(
            project,
            "- date: 2026-09-02 | kind: decision | targets: [notes/old.md]\n",
        )
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("impact.md", result.stderr)

    # Story 6: generate appends publication entries

    def test_generate_appends_publication_entry_with_hashes(self) -> None:
        project = self.generate_ready_project()
        ledger = project / "impact.md"
        entries = lambda: [
            line
            for line in ledger.read_text(encoding="utf-8").splitlines()
            if line.startswith("- ")
        ]
        first = entries()
        self.assertEqual(2, len(first))  # notes/using.md + notes/developing.md
        for line in first:
            self.assertIn("kind: publication", line)
            self.assertIn("outcome: published", line)
            self.assertIn("null->", line)
        note = project / "notes" / "using.md"
        note.write_text(
            "---\ntype: Project Knowledge\nstatus: stable\naudience: usage\n---\n\n"
            "# Use Demo\n\nRun `demo` differently.\n",
            encoding="utf-8",
        )
        self.run_cli("generate", "--project", str(project))
        changed = [line for line in entries() if "notes/using.md" in line]
        self.assertEqual(2, len(changed))
        self.assertIn("->", changed[-1])
        self.assertNotIn("null->", changed[-1])
        self.assertEqual(
            1, len([line for line in entries() if "notes/developing.md" in line])
        )
        self.run_cli("validate", "--project", str(project))

    def test_generate_without_changes_appends_nothing(self) -> None:
        project = self.generate_ready_project()
        self.run_cli("generate", "--project", str(project))
        ledger = project / "impact.md"
        before = ledger.read_text(encoding="utf-8")
        self.run_cli("generate", "--project", str(project))
        self.assertEqual(before, ledger.read_text(encoding="utf-8"))

    # Story 7: completion gate

    def test_completion_gate_linked_draft_passes(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, "2026-09-02-demo")
        self.write_note_with_evidence(
            project, "distilled", "draft", "[evidence/2026-09-02-demo/findings.md]"
        )
        item = self.write_work_item(project, "evidence_packs: [2026-09-02-demo]\n")
        self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item)
        )

    def test_completion_gate_unlinked_pack_fails(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, "2026-09-02-demo")
        item = self.write_work_item(project, "evidence_packs: [2026-09-02-demo]\n")
        result = self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(item),
            expected=2,
        )
        self.assertIn("2026-09-02-demo", result.stderr)

    def test_completion_gate_nonexistent_slug_fails(self) -> None:
        project = self.generate_ready_project()
        item = self.write_work_item(project, "evidence_packs: [2026-09-02-ghost]\n")
        result = self.run_cli(
            "check-completion",
            "--project",
            str(project),
            "--work-item",
            str(item),
            expected=2,
        )
        self.assertIn("2026-09-02-ghost", result.stderr)

    def test_completion_gate_absent_declaration_passes(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, "2026-09-02-orphan")
        item = self.write_work_item(project)
        self.run_cli(
            "check-completion", "--project", str(project), "--work-item", str(item)
        )


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
    """Quick task: optional code provenance keys in evidence pack manifests."""

    PROVENANCE_FM = (
        "kind: execution\nproduced_by: story-001\ndate: 2026-09-02\n"
        'summary: "provenance pack"\n'
        "git_head: {hex_40}\n"
        "worktree_tree: {tree}"
    )

    def test_manifest_valid_provenance_passes(self) -> None:
        project = self.generate_ready_project()
        hex_40 = "0123456789abcdef0123456789abcdef01234567"
        self.make_pack(project, manifest_frontmatter=self.PROVENANCE_FM.format(
            hex_40=hex_40, tree=hex_40
        ))
        self.make_pack(
            project,
            slug="2026-09-02-clean",
            manifest_frontmatter=self.PROVENANCE_FM.format(
                hex_40=hex_40, tree="clean"
            ),
        )
        self.run_cli("validate", "--project", str(project))

    def test_manifest_bad_provenance_hash_fails(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, manifest_frontmatter=self.PROVENANCE_FM.format(
            hex_40="0123456789abcdef0123456789abcdef01234567", tree="not-a-hash"
        ))
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("worktree_tree", result.stderr)

    def test_manifest_tree_without_head_fails(self) -> None:
        project = self.generate_ready_project()
        self.make_pack(project, manifest_frontmatter=(
            "kind: execution\nproduced_by: story-001\ndate: 2026-09-02\n"
            'summary: "partial provenance"\n'
            "worktree_tree: 0123456789abcdef0123456789abcdef01234567"
        ))
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("git_head", result.stderr)

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


if __name__ == "__main__":
    unittest.main()
