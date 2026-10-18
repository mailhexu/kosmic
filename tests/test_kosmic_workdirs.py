from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from skills.scripts.kosmic_specs import SpecCatalog
from skills.scripts.kosmic_work import (
    REGISTRY_RELATIVE,
    WORKDIRS_SCHEMA,
    RegistrationContext,
    WorkdirError,
    begin_registration,
    check_work_start,
    load_registry,
    register_workdir,
    resolve_directory,
)


def git(cwd: Path, *arguments: str) -> None:
    subprocess.run(
        ["git", "-C", str(cwd), *arguments],
        check=True, capture_output=True, text=True,
    )


def commit_all(path: Path) -> None:
    git(path, "add", "-A")
    git(path, "-c", "user.email=t@example.com", "-c", "user.name=t", "commit", "-qm", "init")


def repository(path: Path) -> Path:
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.email", "t@example.com")
    git(path, "config", "user.name", "t")
    (path / ".gitignore").write_text(".tmp/\n.kosmic/\n", encoding="utf-8")
    (path / "README.md").write_text("demo\n", encoding="utf-8")
    (path / ".tmp").mkdir()
    commit_all(path)
    return path


def worktree(repository_root: Path, path: Path, branch: str) -> Path:
    git(repository_root, "worktree", "add", "-q", "-b", branch, str(path))
    (path / ".tmp").mkdir()
    return path


def document(path: Path, metadata: dict, title: str = "Specification") -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "---\n" + "".join(f"{key}: {json.dumps(value)}\n" for key, value in metadata.items())
        + f"---\n\n# {title}\n", encoding="utf-8",
    )
    return path


def project(root: Path, project_id: str = "demo") -> Path:
    document(root / "ProjectEntry.md", {"project_id": project_id}, "Demo")
    return root


def quick_task(project_root: Path, root_path: Path, *, status: str = "approved",
               outputs: list[str] | None = None, project_id: str = "demo",
               owner: dict | None = None) -> Path:
    metadata = {
        "project_id": project_id,
        "status": status,
        "record_kind": "quick-task",
        "local_id": "register-root",
        "subproject_id": None,
        "registration_root": str(root_path),
        "registration_outputs": outputs
        if outputs is not None
        else [REGISTRY_RELATIVE, "worktree:.kosmic/workdir.json"],
    }
    metadata.update(owner or {})
    return document(project_root / "specs" / "quick-tasks" / "2026-10-01-register-root.md", metadata)


def subproject(project_root: Path, owner: str) -> None:
    base = project_root / "subprojects" / owner
    document(base / "SubprojectEntry.md", {
        "schema": "kosmic.subproject/1", "project_id": "demo", "subproject_id": owner,
        "title": owner, "linked_prd": "specs/prd.md",
    })


def finish(context: RegistrationContext) -> None:
    from skills.scripts.kosmic_runs import finish_run

    finish_run(context.run.handle_file, "succeeded")


class WorkdirRegistrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-workdirs-")
        self.addCleanup(self.tmp.cleanup)
        self.base = Path(self.tmp.name)
        self.project_root = project(self.base / "Project")
        self.repo = repository(self.base / "wt-main")
        self.other = worktree(self.repo, self.base / "wt-other", "other")

    def register(self, worktree_path: Path, *, subproject_id: str | None = None,
                 status: str = "approved", outputs: list[str] | None = None,
                 task_root: Path | None = None):
        quick_task(
            self.project_root, task_root or worktree_path,
            status=status, outputs=outputs,
        )
        context = begin_registration(self.project_root, worktree_path, "register-root")
        self.addCleanup(finish, context)
        return register_workdir(context, subproject_id=subproject_id)

    def test_same_project_worktrees_register_without_touching_existing_entries(self) -> None:
        first = self.register(self.repo)
        second = self.register(self.other, subproject_id=None)
        registry = load_registry(self.project_root)
        self.assertEqual(registry["schema"], WORKDIRS_SCHEMA)
        self.assertEqual(registry["project_id"], "demo")
        self.assertEqual([entry["path"] for entry in registry["directories"]],
                         [str(self.repo), str(self.other)])
        self.assertEqual([entry["directory_id"] for entry in registry["directories"]],
                         [first["directory_id"], second["directory_id"]])
        expected_first = "wd-" + hashlib.sha256(str(self.repo).encode()).hexdigest()[:16]
        self.assertEqual(first["directory_id"], expected_first)
        self.assertIsNone(first["fixed_subproject_id"])
        for path in (self.repo, self.other):
            binding = json.loads((path / ".kosmic" / "workdir.json").read_text())
            self.assertEqual(binding["project_id"], "demo")

    def test_duplicate_registration_is_denied_without_changes(self) -> None:
        self.register(self.repo)
        before = (self.project_root / REGISTRY_RELATIVE).read_bytes()
        with self.assertRaisesRegex(WorkdirError, "DIRECTORY_REGISTERED"):
            self.register(self.repo)
        self.assertEqual((self.project_root / REGISTRY_RELATIVE).read_bytes(), before)

    def test_cross_project_collision_is_denied_before_any_write(self) -> None:
        self.register(self.repo)
        foreign = project(self.base / "Foreign", "foreign")
        foreign_task = quick_task(foreign, self.repo, project_id="foreign")
        with self.assertRaisesRegex(WorkdirError, "CROSS_PROJECT_DENIED"):
            begin_registration(foreign, self.repo, "register-root")
        self.assertFalse((foreign / REGISTRY_RELATIVE).exists())
        binding = json.loads((self.repo / ".kosmic" / "workdir.json").read_text())
        self.assertEqual(binding["project_id"], "demo")

    def test_unsafe_roots_are_rejected_before_writes(self) -> None:
        cases = [
            self.base / "missing",
            self.base / "wt-main" / "README.md",
            self.base / "escape" / ".." / "wt-main",
        ]
        symlink = self.base / "linked"
        symlink.symlink_to(self.repo)
        cases.append(symlink)
        for candidate in cases:
            with self.subTest(path=str(candidate)):
                quick_task(self.project_root, candidate)
                with self.assertRaises(WorkdirError):
                    begin_registration(self.project_root, candidate, "register-root")
        self.assertFalse((self.project_root / REGISTRY_RELATIVE).exists())

    def test_fixed_subproject_must_be_a_real_owner(self) -> None:
        subproject(self.project_root, "feature")
        entry = self.register(self.repo, subproject_id="feature")
        self.assertEqual(entry["fixed_subproject_id"], "feature")
        with self.assertRaisesRegex(WorkdirError, "SUBPROJECT_UNKNOWN"):
            self.register(self.other, subproject_id="ghost")

    def test_bootstrap_requires_approved_quick_task_declaring_root_and_outputs(self) -> None:
        quick_task(self.project_root, self.repo, status="draft")
        with self.assertRaisesRegex(WorkdirError, "RECORD_NOT_AUTHORIZED"):
            begin_registration(self.project_root, self.repo, "register-root")
        quick_task(self.project_root, self.other)
        with self.assertRaisesRegex(WorkdirError, "ROOT_MISMATCH"):
            begin_registration(self.project_root, self.repo, "register-root")
        quick_task(self.project_root, self.repo, outputs=[REGISTRY_RELATIVE])
        with self.assertRaisesRegex(WorkdirError, "OUTPUTS_UNDECLARED"):
            begin_registration(self.project_root, self.repo, "register-root")

    def test_registration_context_authorizes_only_registration(self) -> None:
        task = quick_task(self.project_root, self.repo)
        context = begin_registration(self.project_root, self.repo, "register-root")
        self.addCleanup(finish, context)
        self.assertIsInstance(context, RegistrationContext)
        self.assertTrue(context.permits("workdir-register"))
        self.assertTrue(context.permits("registration-evidence"))
        self.assertFalse(context.permits("source-write"))
        self.assertFalse(context.permits("work-begin"))
        self.assertEqual(context.record, "demo/quick-task/register-root")
        self.assertTrue(context.run.run_id)
        register_workdir(context)
        with self.assertRaisesRegex(WorkdirError, "DIRECTORY_REGISTERED"):
            begin_registration(self.project_root, self.repo, "register-root")

    def test_registration_rechecks_live_authority_before_writing(self) -> None:
        from skills.scripts.kosmic_work import REGISTRATION_OPERATIONS

        quick_task(self.project_root, self.repo)
        context = begin_registration(self.project_root, self.repo, "register-root")
        self.addCleanup(finish, context)
        quick_task(self.project_root, self.repo, status="draft")
        with self.assertRaisesRegex(WorkdirError, "RECORD_NOT_AUTHORIZED"):
            register_workdir(context)
        self.assertFalse((self.project_root / REGISTRY_RELATIVE).exists())

        quick_task(self.project_root, self.repo, outputs=[REGISTRY_RELATIVE])
        with self.assertRaisesRegex(WorkdirError, "CONTEXT_INVALID"):
            register_workdir(context)
        self.assertFalse((self.project_root / REGISTRY_RELATIVE).exists())

        quick_task(self.project_root, self.repo)
        finish(context)
        with self.assertRaisesRegex(WorkdirError, "CONTEXT_INVALID"):
            register_workdir(context)
        self.assertFalse((self.project_root / REGISTRY_RELATIVE).exists())
        self.assertIn("workdir-register", REGISTRATION_OPERATIONS)

    def test_resolve_directory_is_exact_and_fails_closed_on_binding_mismatch(self) -> None:
        self.register(self.repo)
        entry = resolve_directory(self.project_root, self.repo / "README.md")
        self.assertEqual(entry["path"], str(self.repo))
        self.assertEqual(check_work_start(
            self.project_root, self.repo, "demo/quick-task/register-root").qualified_id,
            "demo/quick-task/register-root")
        with self.assertRaisesRegex(WorkdirError, "NOT_REGISTERED"):
            check_work_start(self.project_root, self.other, "demo/quick-task/register-root")
        with self.assertRaisesRegex(WorkdirError, "NOT_REGISTERED"):
            resolve_directory(self.project_root, self.other)
        binding_path = self.repo / ".kosmic" / "workdir.json"
        tampered = json.loads(binding_path.read_text())
        tampered["project_id"] = "foreign"
        binding_path.write_text(json.dumps(tampered))
        with self.assertRaisesRegex(WorkdirError, "BINDING_MISMATCH"):
            resolve_directory(self.project_root, self.repo)

    def test_unsafe_registry_state_is_not_treated_as_absent(self) -> None:
        self.register(self.repo)
        registry_path = self.project_root / REGISTRY_RELATIVE
        registry_path.unlink()
        registry_path.symlink_to(self.repo / "README.md")
        with self.assertRaises(WorkdirError):
            load_registry(self.project_root)
        with self.assertRaises(WorkdirError):
            begin_registration(self.project_root, self.other, "register-root")
        binding = self.other / ".kosmic" / "workdir.json"
        self.assertFalse(binding.exists())

    def test_registry_rejects_malformed_state(self) -> None:
        self.register(self.repo)
        registry_path = self.project_root / REGISTRY_RELATIVE
        good = json.loads(registry_path.read_text())
        for mutation in (
            {**good, "schema": "kosmic.workdirs/2"},
            {**good, "project_id": "other"},
            {**good, "directories": [*good["directories"], *good["directories"]]},
            {**good, "directories": [{**good["directories"][0], "directory_id": "wd-forged"}]},
            {**good, "sequence": 7},
        ):
            registry_path.write_text(json.dumps(mutation))
            with self.assertRaises(WorkdirError):
                load_registry(self.project_root)

    def test_catalog_still_validates_registered_project(self) -> None:
        self.register(self.repo)
        catalog = SpecCatalog(self.project_root)
        self.assertEqual(catalog.project_id, "demo")


if __name__ == "__main__":
    unittest.main()
