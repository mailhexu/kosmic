from __future__ import annotations

import hashlib
import json
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


if __name__ == "__main__":
    unittest.main()
