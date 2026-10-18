"""Story070 navigation: owner-aware STATUS and dream discovery over one catalog.

Behavioral seams only: generated STATUS grouping/links/Open Work state,
catalog-driven dream open-work ownership, the pending-transaction degradation,
and unchanged bootstrap-flat output.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from skills.scripts import kosmic_dreams
from skills.scripts.kosmic_project_skills import (
    generate_status,
    load_project,
    render_status,
    status_drift,
)
from skills.scripts.kosmic_specs import SpecError, validate_project_specs
from skills.scripts.kosmic_work import directory_id


def frontmatter(fields: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {json.dumps(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def raw_frontmatter(fields: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {value}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def write(path: Path, fields: dict[str, object], title: str, body: str = "",
          *, raw: bool = False) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (raw_frontmatter(fields) if raw else frontmatter(fields)) + f"\n# {title}\n"
    if body:
        text += f"\n{body}\n"
    path.write_text(text, encoding="utf-8")
    return path


def commit_all(worktree: Path, date: str, message: str) -> str:
    stamp = f"{date}T12:00:00"
    env = {
        "GIT_AUTHOR_DATE": stamp,
        "GIT_COMMITTER_DATE": stamp,
        "GIT_AUTHOR_NAME": "fixture",
        "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_NAME": "fixture",
        "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    }
    subprocess.run(["git", "add", "-A"], cwd=str(worktree), env=env, check=True)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=str(worktree), env=env, check=True)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(worktree), capture_output=True, text=True, check=True
    ).stdout.strip()


def spec(project_id: str, owner: str | None, kind: str, local_id: str, status: str,
         updated: str, **extra: object) -> dict[str, object]:
    fields: dict[str, object] = {
        "project_id": project_id,
        "subproject_id": owner if owner is not None else "null",
        "record_kind": kind,
        "local_id": local_id,
        "status": status,
        "created": "2026-10-01",
        "updated": updated,
    }
    fields.update(extra)
    return fields


def build_two_feature_project(base: Path, *, project_id: str = "nav") -> tuple[Path, Path]:
    """Disposable worktree with two subprojects, shared Quick Task, and proposal."""
    worktree = base / "worktree"
    worktree.mkdir(parents=True)
    subprocess.run(["git", "init", "-q"], cwd=str(worktree), check=True)
    (worktree / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
    vault = worktree / "vault"
    root = vault / "Projects" / project_id
    (root / "notes").mkdir(parents=True)
    (root / "ProjectEntry.md").write_text(
        f"---\nproject_id: {project_id}\nworking_state: working-tree\n---\n\n# {project_id}\n",
        encoding="utf-8",
    )
    (root / "notes" / "index.md").write_text("# Index\n", encoding="utf-8")

    for owner, title in (("alpha", "Alpha Feature"), ("beta", "Beta Feature")):
        write(
            root / "subprojects" / owner / "SubprojectEntry.md",
            {
                "schema": "kosmic.subproject/1",
                "project_id": project_id,
                "subproject_id": owner,
                "title": title,
                "linked_prd": "specs/prd.md",
                "status": "draft",
                "created": "2026-10-01",
            },
            title,
        )
        write(
            root / "subprojects" / owner / "specs" / "prd.md",
            spec(project_id, owner, "prd", "prd", "approved", "2026-10-01"),
            title,
        )
        write(
            root / "subprojects" / owner / "specs" / "architecture.md",
            spec(project_id, owner, "architecture", "architecture", "approved",
                 "2026-10-01", linked_prd="prd.md"),
            f"{title} Architecture",
        )
        (root / "subprojects" / owner / "specs" / "INDEX.md").write_text(
            f"# {title} Specs\n\n- [PRD](prd.md)\n", encoding="utf-8"
        )

    write(
        root / "subprojects" / "alpha" / "specs" / "epics" / "epic-001.md",
        spec(project_id, "alpha", "epic", "001", "done", "2026-10-01",
             linked_architecture="../architecture.md", linked_prd="../prd.md"),
        "Alpha Epic One",
    )
    write(
        root / "subprojects" / "alpha" / "specs" / "stories" / "story-001.md",
        spec(project_id, "alpha", "story", "001", "in_progress", "2026-10-01",
             linked_epic="../epics/epic-001.md", linked_architecture="../architecture.md",
             linked_prd="../prd.md", depends_on=[]),
        "Alpha Story One",
    )
    write(
        root / "subprojects" / "alpha" / "specs" / "quick-tasks" / "2026-10-01-alpha-task.md",
        spec(project_id, "alpha", "quick-task", "2026-10-01-alpha-task", "draft", "2026-10-01"),
        "Alpha Task",
    )
    write(
        root / "subprojects" / "beta" / "specs" / "epics" / "epic-001.md",
        spec(project_id, "beta", "epic", "001", "done", "2026-10-01",
             linked_architecture="../architecture.md", linked_prd="../prd.md"),
        "Beta Epic One",
    )
    write(
        root / "subprojects" / "beta" / "specs" / "stories" / "story-001.md",
        spec(project_id, "beta", "story", "001", "done", "2026-10-01",
             linked_epic="../epics/epic-001.md", linked_architecture="../architecture.md",
             linked_prd="../prd.md", depends_on=[]),
        "Beta Story One",
    )
    write(
        root / "specs" / "quick-tasks" / "2026-10-01-shared-task.md",
        spec(project_id, None, "quick-task", "2026-10-01-shared-task", "approved", "2026-10-01"),
        "Shared Task",
    )
    write(
        root / "specs" / "skill-proposals" / "001-shared-proposal.md",
        spec(project_id, None, "proposal", "001-shared-proposal", "approved", "2026-10-01",
             decision="pending"),
        "Shared Proposal",
    )
    commit_all(worktree, "2026-10-01", "fixture baseline")
    return worktree, root


def receipt_for(identity: str) -> str:
    return kosmic_dreams.receipt_name(identity)


def open_receipt_store(root: Path, satisfied: tuple[str, ...] = ()) -> Path:
    """Publish fixture receipts bound to the current embedded record contract.

    Flat bootstrap identities retain their explicitly supported minimal format.
    """
    store = root / ".kosmic" / "work-receipts"
    store.mkdir(parents=True, exist_ok=True)
    for identity in satisfied:
        receipt = {"schema": "kosmic.work-receipt/1", "identity": identity, "status": "successful"}
        if not identity.startswith("specs/"):
            import hashlib
            from skills.scripts.kosmic_specs import SpecCatalog
            from skills.scripts.kosmic_completion import (
                source_revision,
                validate_completion_proof,
            )
            ref = SpecCatalog(root).resolve(identity)
            canonical = ref.path.relative_to(root).as_posix()
            metadata = dict(ref.metadata)
            metadata.update(
                review_base="fixture-base", review_round=1,
                completion_observations=[{
                    "criterion": "Result equals 42",
                    "observation": "Observed 42",
                    "source": "tests/test_kosmic_navigation.py",
                }],
                completion_review={
                    "reviewer": "fixture-reviewer",
                    "axes": {
                        "standards": {"decision": "approved",
                                      "reviewer": "fixture-standards"},
                        "spec": {"decision": "approved", "reviewer": "fixture-spec"}},
                    "decision": "approved",
                    "review_base": "fixture-base",
                    "reviewed_revision": source_revision(
                        root.parents[2], root, SpecCatalog(root).resolve(identity)),
                    "findings": [],
                    "scope": ["project:specs/"],
                },
            )
            title = next(line[2:] for line in ref.path.read_text().splitlines() if line.startswith("# "))
            write(ref.path, metadata, title, "## Acceptance Criteria\n\n- [x] Result equals 42\n")
            ref = SpecCatalog(root).resolve(identity)
            receipt.update(
                record_path=canonical,
                record_sha256=hashlib.sha256(ref.path.read_bytes()).hexdigest(),
                proof=validate_completion_proof(root, ref),
            )
        (store / receipt_for(identity)).write_text(json.dumps(receipt) + "\n", encoding="utf-8")
    return store


class NavigationStatusTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-navigation-")
        self.worktree, self.root = build_two_feature_project(Path(self.tmp.name))
        entry = self.root / "ProjectEntry.md"
        entry.write_text(
            entry.read_text(encoding="utf-8").replace(
                "working-tree\n", f"working-tree\nstatus_root: {self.worktree.resolve()}\n"
            ),
            encoding="utf-8",
        )
        self.project = load_project(self.root)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_status_groups_every_owner_and_class_with_canonical_links(self) -> None:
        validate_project_specs(self.root)
        first = render_status(self.project, "head0")
        self.assertEqual(first, render_status(self.project, "head0"))
        text = first.decode("utf-8")
        self.assertIn("### Project", text)
        self.assertIn("### Subproject: alpha", text)
        self.assertIn("### Subproject: beta", text)
        self.assertIn(
            "| [Alpha Story One](vault/Projects/nav/subprojects/alpha/specs/stories/story-001.md)"
            " | in_progress | 2026-10-01 |",
            text,
        )
        self.assertIn(
            "| [Shared Task](vault/Projects/nav/specs/quick-tasks/2026-10-01-shared-task.md)"
            " | approved | 2026-10-01 |",
            text,
        )
        self.assertIn(
            "| [Shared Proposal](vault/Projects/nav/specs/skill-proposals/001-shared-proposal.md)"
            " | approved | 2026-10-01 |",
            text,
        )
        project_section = text.split("### Project", 1)[1].split("### Subproject: alpha", 1)[0]
        self.assertIn("#### Quick Tasks", project_section)
        self.assertIn("#### Skill Proposals", project_section)
        self.assertNotIn("#### Stories", project_section)
        alpha_section = text.split("### Subproject: alpha", 1)[1].split("### Subproject: beta", 1)[0]
        self.assertIn("#### Epics", alpha_section)
        self.assertIn("#### Stories", alpha_section)
        self.assertIn("#### Quick Tasks", alpha_section)
        self.assertNotIn("[Shared Task]", alpha_section)
        beta_section = text.split("### Subproject: beta", 1)[1].split("## Open Work", 1)[0]
        self.assertIn("#### Epics", beta_section)
        self.assertIn("| [Beta Epic One]", beta_section)

    def test_open_work_is_project_wide_and_unreceipted_done_is_pending(self) -> None:
        text = render_status(self.project, "head0").decode("utf-8")
        open_section = text.split("## Open Work", 1)[1]
        self.assertIn(
            "[alpha/Alpha Story One]"
            "(vault/Projects/nav/subprojects/alpha/specs/stories/story-001.md) - in_progress",
            open_section,
        )
        self.assertIn(
            "[alpha/Alpha Task]"
            "(vault/Projects/nav/subprojects/alpha/specs/quick-tasks/2026-10-01-alpha-task.md)"
            " - draft",
            open_section,
        )
        self.assertIn(
            "[Shared Task](vault/Projects/nav/specs/quick-tasks/2026-10-01-shared-task.md)"
            " - approved",
            open_section,
        )
        self.assertIn("[Shared Proposal]", open_section)
        self.assertIn("[beta/Beta Story One]", open_section)
        self.assertIn("[alpha/Alpha Epic One]", open_section)
        self.assertIn("done (receipt pending)", open_section)

    def test_unreceipted_done_is_pending_not_completed(self) -> None:
        open_receipt_store(
            self.root, satisfied=("nav/alpha/epic/001", "nav/beta/epic/001")
        )
        first = render_status(self.project, "head0")
        self.assertEqual(first, render_status(self.project, "head0"))
        text = first.decode("utf-8")
        self.assertIn(
            "| [Beta Story One](vault/Projects/nav/subprojects/beta/specs/stories/story-001.md)"
            " | done (receipt pending) | 2026-10-01 |",
            text,
        )
        open_section = text.split("## Open Work", 1)[1]
        self.assertIn(
            "[beta/Beta Story One]"
            "(vault/Projects/nav/subprojects/beta/specs/stories/story-001.md)"
            " - done (receipt pending)",
            open_section,
        )
        self.assertIn("- 5 open item(s)", open_section)
        receipts = self.root / ".kosmic" / "work-receipts"
        beta_story = receipts / receipt_for("nav/beta/story/001")
        beta_story.write_text("{}\n", encoding="utf-8")
        empty = render_status(self.project, "head0").decode("utf-8")
        self.assertIn(
            "| [Beta Story One](vault/Projects/nav/subprojects/beta/specs/stories/story-001.md)"
            " | done (receipt pending) | 2026-10-01 |",
            empty,
        )
        beta_story.write_text(
            json.dumps({
                "schema": "kosmic.work-receipt/1",
                "identity": "nav/alpha/story/001",
                "status": "successful",
            }) + "\n",
            encoding="utf-8",
        )
        wrong_record = render_status(self.project, "head0").decode("utf-8")
        self.assertIn(
            "| [Beta Story One](vault/Projects/nav/subprojects/beta/specs/stories/story-001.md)"
            " | done (receipt pending) | 2026-10-01 |",
            wrong_record,
        )
        open_receipt_store(
            self.root,
            satisfied=("nav/alpha/epic/001", "nav/beta/epic/001", "nav/beta/story/001"),
        )
        settled = render_status(self.project, "head0").decode("utf-8")
        self.assertIn("| [Beta Story One](vault/Projects/nav/subprojects/beta/specs/stories/story-001.md) | done | 2026-10-01 |", settled)
        self.assertNotIn("Beta Story One", settled.split("## Open Work", 1)[1])

    def test_failed_and_symlinked_receipts_keep_records_pending(self) -> None:
        open_receipt_store(
            self.root, satisfied=("nav/alpha/epic/001", "nav/beta/epic/001")
        )
        store = self.root / ".kosmic" / "work-receipts"
        receipt = store / receipt_for("nav/beta/story/001")
        receipt.write_text(
            json.dumps({
                "schema": "kosmic.work-receipt/1",
                "identity": "nav/beta/story/001",
                "status": "failed",
            }) + "\n",
            encoding="utf-8",
        )
        failed = render_status(self.project, "head0").decode("utf-8")
        open_section = failed.split("## Open Work", 1)[1]
        self.assertIn("[beta/Beta Story One]", open_section)
        self.assertIn("- 5 open item(s)", open_section)
        real = store / "successful-elsewhere.json"
        real.write_text(
            json.dumps({
                "schema": "kosmic.work-receipt/1",
                "identity": "nav/beta/story/001",
                "status": "successful",
            }) + "\n",
            encoding="utf-8",
        )
        receipt.unlink()
        receipt.symlink_to(real)
        linked = render_status(self.project, "head0").decode("utf-8")
        self.assertIn("[beta/Beta Story One]", linked.split("## Open Work", 1)[1])

    def test_generate_status_matches_drift_gate(self) -> None:
        self.assertTrue(status_drift(self.project))
        path = generate_status(self.project, work_record="nav/quick-task/2026-10-01-shared-task")
        self.assertEqual(path, self.worktree / "STATUS.md")
        self.assertFalse(status_drift(self.project))
        open_receipt_store(self.root, satisfied=("nav/beta/story/001",))
        self.assertTrue(status_drift(self.project))
        generate_status(self.project, work_record="nav/quick-task/2026-10-01-shared-task")
        self.assertFalse(status_drift(self.project))


    def test_broken_owner_metadata_fails_closed(self) -> None:
        story = self.root / "subprojects" / "beta" / "specs" / "stories" / "story-001.md"
        story.write_text(story.read_text(encoding="utf-8").replace(
            'subproject_id: "beta"', 'subproject_id: "alpha"'), encoding="utf-8")
        with self.assertRaises(SpecError) as ctx:
            render_status(self.project, "head0")
        self.assertEqual(ctx.exception.code, "OWNER_MISMATCH")

    def test_broken_dependency_fails_navigation_closed(self) -> None:
        story = self.root / "subprojects" / "alpha" / "specs" / "stories" / "story-001.md"
        story.write_text(story.read_text(encoding="utf-8").replace(
            "depends_on: []", 'depends_on: ["nav/alpha/story/999"]'), encoding="utf-8")
        with self.assertRaises(SpecError) as ctx:
            render_status(self.project, "head0")
        self.assertEqual(ctx.exception.code, "DEPENDENCY_INVALID")

    def test_shared_root_violation_fails_navigation_closed(self) -> None:
        notes = self.root / "subprojects" / "alpha" / "notes"
        notes.mkdir()
        (notes / "duplicate.md").write_text("# duplicate knowledge\n", encoding="utf-8")
        with self.assertRaises(SpecError) as ctx:
            render_status(self.project, "head0")
        self.assertEqual(ctx.exception.code, "SHARED_ROOT_INVALID")


class NavigationDreamTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-navigation-dream-")
        self.worktree, self.root = build_two_feature_project(Path(self.tmp.name))

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def harvest(self) -> dict:
        return kosmic_dreams.collect_harvest(
            self.worktree / "vault", date="2026-10-02", timezone_name="UTC"
        )

    def test_open_work_includes_every_subproject_with_qualified_ownership(self) -> None:
        harvest = self.harvest()
        entry = next(item for item in harvest["projects"] if item["project"] == "nav")
        by_path = {row["path"]: row for row in entry["open_work"]}
        alpha_story = by_path["Projects/nav/subprojects/alpha/specs/stories/story-001.md"]
        self.assertEqual(alpha_story["subproject"], "alpha")
        self.assertEqual(alpha_story["record"], "nav/alpha/story/001")
        self.assertEqual(alpha_story["blocker"], "in_progress")
        beta_story = by_path.get("Projects/nav/subprojects/beta/specs/stories/story-001.md")
        self.assertEqual(beta_story["blocker"], kosmic_dreams.RECEIPT_PENDING_BLOCKER)
        self.assertEqual(beta_story["record"], "nav/beta/story/001")
        shared = by_path["Projects/nav/specs/quick-tasks/2026-10-01-shared-task.md"]
        self.assertIsNone(shared["subproject"])
        self.assertEqual(shared["record"], "nav/quick-task/2026-10-01-shared-task")
        proposal = by_path["Projects/nav/specs/skill-proposals/001-shared-proposal.md"]
        self.assertIsNone(proposal["subproject"])
        self.assertEqual(proposal["blocker"], "decision-pending")
        alpha_task = by_path["Projects/nav/subprojects/alpha/specs/quick-tasks/2026-10-01-alpha-task.md"]
        self.assertEqual(alpha_task["subproject"], "alpha")

    def test_dream_surfaces_pending_transaction_without_receipt(self) -> None:
        open_receipt_store(
            self.root, satisfied=("nav/alpha/epic/001", "nav/beta/epic/001")
        )
        harvest = self.harvest()
        entry = next(item for item in harvest["projects"] if item["project"] == "nav")
        by_path = {row["path"]: row for row in entry["open_work"]}
        beta_story = by_path["Projects/nav/subprojects/beta/specs/stories/story-001.md"]
        self.assertEqual(beta_story["blocker"], kosmic_dreams.RECEIPT_PENDING_BLOCKER)
        self.assertEqual(beta_story["status"], "done")
        self.assertEqual(beta_story["subproject"], "beta")
        alpha_epic = by_path.get("Projects/nav/subprojects/alpha/specs/epics/epic-001.md")
        self.assertIsNone(alpha_epic)
        first = json.dumps(harvest["projects"], sort_keys=True)
        second = json.dumps(self.harvest()["projects"], sort_keys=True)
        self.assertEqual(first, second)

    def test_catalog_discovery_enumerates_all_kinds_directly(self) -> None:
        write(
            self.root / "specs" / "skill-proposals" / "notes-capture.md",
            spec("nav", None, "proposal", "notes-capture", "approved", "2026-10-01",
                 decision="pending"),
            "Notes Capture",
        )
        write(
            self.root / "subprojects" / "alpha" / "specs" / "research" / "2026-10-01-alpha-research.md",
            spec("nav", "alpha", "research", "2026-10-01-alpha-research", "draft", "2026-10-01",
                 linked_prd="../prd.md"),
            "Alpha Research",
        )
        harvest = self.harvest()
        entry = next(item for item in harvest["projects"] if item["project"] == "nav")
        by_path = {row["path"]: row for row in entry["open_work"]}
        proposal = by_path["Projects/nav/specs/skill-proposals/notes-capture.md"]
        self.assertEqual(proposal["kind"], "proposal")
        self.assertEqual(proposal["record"], "nav/proposal/notes-capture")
        self.assertIsNone(proposal["subproject"])
        self.assertEqual(proposal["blocker"], "decision-pending")
        research = by_path[
            "Projects/nav/subprojects/alpha/specs/research/2026-10-01-alpha-research.md"
        ]
        self.assertEqual(research["kind"], "research")
        self.assertEqual(research["record"], "nav/alpha/research/2026-10-01-alpha-research")
        self.assertEqual(research["subproject"], "alpha")
        self.assertEqual(research["blocker"], "draft")

    def test_broken_dependency_blocks_harvest(self) -> None:
        story = self.root / "subprojects" / "alpha" / "specs" / "stories" / "story-001.md"
        story.write_text(story.read_text(encoding="utf-8").replace(
            "depends_on: []", 'depends_on: ["nav/alpha/story/999"]'), encoding="utf-8")
        with self.assertRaises(SpecError) as ctx:
            self.harvest()
        self.assertEqual(ctx.exception.code, "DEPENDENCY_INVALID")

    def test_broken_catalog_blocks_harvest_instead_of_flat_scan(self) -> None:
        story = self.root / "subprojects" / "beta" / "specs" / "stories" / "story-001.md"
        story.write_text(story.read_text(encoding="utf-8").replace(
            'subproject_id: "beta"', 'subproject_id: "alpha"'), encoding="utf-8")
        with self.assertRaises(SpecError) as ctx:
            self.harvest()
        self.assertEqual(ctx.exception.code, "OWNER_MISMATCH")


class FlatBehaviorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-navigation-flat-")
        self.worktree = Path(self.tmp.name) / "worktree"
        self.worktree.mkdir(parents=True)
        subprocess.run(["git", "init", "-q"], cwd=str(self.worktree), check=True)
        root = self.worktree / "vault" / "Projects" / "flat"
        (root / "specs" / "stories").mkdir(parents=True)
        (root / "ProjectEntry.md").write_text(
            "---\nproject_id: flat\nworking_state: working-tree\n"
            f"status_root: {self.worktree.resolve()}\n---\n\n# flat\n",
            encoding="utf-8",
        )
        write(
            root / "specs" / "stories" / "story-001-a.md",
            {"status": "in_progress", "updated": "2026-09-23"},
            "Flat Story",
            raw=True,
        )
        (root / "specs" / "quick-tasks").mkdir()
        write(
            root / "specs" / "quick-tasks" / "2026-09-01-q.md",
            {"status": "done", "updated": "2026-09-23"},
            "Flat Quick",
            raw=True,
        )
        self.root = root
        self.project = load_project(root)
        commit_all(self.worktree, "2026-09-23", "flat baseline")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_flat_status_keeps_existing_shape(self) -> None:
        text = render_status(self.project, "head0").decode("utf-8")
        self.assertEqual(text, render_status(self.project, "head0").decode("utf-8"))
        self.assertIn("### Stories", text)
        self.assertIn("| [Flat Story](vault/Projects/flat/specs/stories/story-001-a.md) | in_progress | 2026-09-23 |", text)
        self.assertIn("| — | — | — |", text)
        self.assertNotIn("#### ", text)
        self.assertNotIn("### Subproject:", text)
        self.assertNotIn("### Project", text)
        self.assertNotIn("## Work Context", text)
        self.assertIn("- 1 open item(s)", text)

    def test_flat_status_bytes_are_exact(self) -> None:
        expected = (
            "<!-- Generated by the Kosmic Projection CLI. Do not edit. -->\n"
            "# Status: flat\n"
            "\n"
            "Vault HEAD: head0\n"
            "\n"
            "## Spec Status\n"
            "\n"
            "### PRD\n"
            "\n"
            "| Spec | Status | Updated |\n"
            "|------|--------|---------|\n"
            "| — | — | — |\n"
            "\n"
            "### Architecture\n"
            "\n"
            "| Spec | Status | Updated |\n"
            "|------|--------|---------|\n"
            "| — | — | — |\n"
            "\n"
            "### Epics\n"
            "\n"
            "| Spec | Status | Updated |\n"
            "|------|--------|---------|\n"
            "| — | — | — |\n"
            "\n"
            "### Stories\n"
            "\n"
            "| Spec | Status | Updated |\n"
            "|------|--------|---------|\n"
            "| [Flat Story](vault/Projects/flat/specs/stories/story-001-a.md) | in_progress | 2026-09-23 |\n"
            "\n"
            "### Quick Tasks\n"
            "\n"
            "| Spec | Status | Updated |\n"
            "|------|--------|---------|\n"
            "| [Flat Quick](vault/Projects/flat/specs/quick-tasks/2026-09-01-q.md) | done | 2026-09-23 |\n"
            "\n"
            "### Skill Proposals\n"
            "\n"
            "| Spec | Status | Updated |\n"
            "|------|--------|---------|\n"
            "| — | — | — |\n"
            "\n"
            "## Open Work\n"
            "\n"
            "- 1 open item(s)\n"
            "- [Flat Story](vault/Projects/flat/specs/stories/story-001-a.md) - in_progress\n"
        )
        self.assertEqual(render_status(self.project, "head0"), expected.encode("utf-8"))

    def test_flat_dream_entries_keep_legacy_shape(self) -> None:
        harvest = kosmic_dreams.collect_harvest(
            self.worktree / "vault", date="2026-10-02", timezone_name="UTC"
        )
        entry = next(item for item in harvest["projects"] if item["project"] == "flat")
        self.assertEqual(len(entry["open_work"]), 1)
        row = entry["open_work"][0]
        self.assertNotIn("subproject", row)
        self.assertNotIn("record", row)
        self.assertEqual(row["blocker"], "in_progress")

    def test_seam_degrades_without_receipt_store(self) -> None:
        identity = "specs/stories/story-001-a.md"
        self.assertEqual(
            kosmic_dreams.pending_terminal_receipts(self.root, [(identity, "done")]), {}
        )
        open_receipt_store(self.root)
        pending = kosmic_dreams.pending_terminal_receipts(
            self.root,
            [(identity, "done"), (identity, "draft")],
        )
        self.assertEqual(
            pending,
            {identity: ".kosmic/work-receipts/" + receipt_for(identity)},
        )

    def test_receipt_seam_accepts_only_successful_matching_receipts(self) -> None:
        identity = "specs/stories/story-001-a.md"
        records = [(identity, "done")]
        expected_path = ".kosmic/work-receipts/" + receipt_for(identity)
        store = open_receipt_store(self.root)
        receipt = store / receipt_for(identity)

        def still_pending() -> None:
            self.assertEqual(
                kosmic_dreams.pending_terminal_receipts(self.root, records),
                {identity: expected_path},
            )

        still_pending()
        for payload in (
            b"",
            b"null",
            b"{",
            b"\xff\xfe not utf-8",
            json.dumps({"schema": "kosmic.work-receipt/2", "identity": identity,
                        "status": "successful"}).encode("utf-8"),
            json.dumps({"schema": "kosmic.work-receipt/1", "identity": "other/record",
                        "status": "successful"}).encode("utf-8"),
            json.dumps({"schema": "kosmic.work-receipt/1", "identity": identity,
                        "status": "failed"}).encode("utf-8"),
            json.dumps({"schema": "kosmic.work-receipt/1",
                        "identity": identity}).encode("utf-8"),
            b'{"schema": "kosmic.work-receipt/1", "identity": "' + identity.encode("utf-8")
            + b'", "status": "successful"}' + b" " * 65536,
        ):
            receipt.write_bytes(payload)
            still_pending()
        receipt.write_text(
            json.dumps({
                "schema": "kosmic.work-receipt/1",
                "identity": identity,
                "status": "successful",
            }) + "\n",
            encoding="utf-8",
        )
        self.assertEqual(kosmic_dreams.pending_terminal_receipts(self.root, records), {})

    def test_receipt_seam_denies_symlinked_and_non_regular_receipts(self) -> None:
        identity = "specs/stories/story-001-a.md"
        records = [(identity, "done")]
        expected_path = ".kosmic/work-receipts/" + receipt_for(identity)
        store = open_receipt_store(self.root)
        receipt = store / receipt_for(identity)
        successful = json.dumps({
            "schema": "kosmic.work-receipt/1",
            "identity": identity,
            "status": "successful",
        })
        receipt.write_text(successful, encoding="utf-8")
        real = store / "real-receipt.json"
        real.write_text(successful, encoding="utf-8")
        receipt.unlink()
        receipt.symlink_to(real)
        self.assertEqual(
            kosmic_dreams.pending_terminal_receipts(self.root, records),
            {identity: expected_path},
        )
        receipt.unlink()
        receipt.mkdir()
        self.assertEqual(
            kosmic_dreams.pending_terminal_receipts(self.root, records),
            {identity: expected_path},
        )
        receipt.rmdir()
        receipt.write_text(successful, encoding="utf-8")
        self.assertEqual(kosmic_dreams.pending_terminal_receipts(self.root, records), {})

    def test_symlinked_receipt_store_keeps_done_pending(self) -> None:
        identity = "specs/stories/story-001-a.md"
        open_receipt_store(self.root, satisfied=(identity,))
        store = self.root / ".kosmic" / "work-receipts"
        moved = self.root / ".kosmic" / "work-receipts-actual"
        store.rename(moved)
        store.symlink_to(moved)
        self.assertEqual(
            kosmic_dreams.pending_terminal_receipts(self.root, [(identity, "done")]),
            {identity: ".kosmic/work-receipts/" + receipt_for(identity)},
        )

    def test_flat_spec_reads_fail_closed_on_symlinked_spec(self) -> None:
        secret = self.worktree / "secret.md"
        secret.write_text(
            "---\nstatus: done\nupdated: 2026-09-23\n---\n\n# Outside\n", encoding="utf-8"
        )
        story = self.root / "specs" / "stories" / "story-001-a.md"
        story.unlink()
        story.symlink_to(secret)
        with self.assertRaises(SpecError) as ctx:
            render_status(self.project, "head0")
        self.assertEqual(ctx.exception.code, "SCOPE_DENIED")
        with self.assertRaises(SpecError):
            kosmic_dreams.collect_harvest(
                self.worktree / "vault", date="2026-10-02", timezone_name="UTC"
            )

    def test_flat_spec_reads_fail_closed_on_invalid_utf8(self) -> None:
        (self.root / "specs" / "stories" / "story-001-a.md").write_bytes(
            b"---\nstatus: in_progress\xff\nupdated: 2026-09-23\n---\n\n# Flat Story\n"
        )
        with self.assertRaises(UnicodeDecodeError):
            render_status(self.project, "head0")
        with self.assertRaises(UnicodeDecodeError):
            kosmic_dreams.collect_harvest(
                self.worktree / "vault", date="2026-10-02", timezone_name="UTC"
            )


if __name__ == "__main__":
    unittest.main()
