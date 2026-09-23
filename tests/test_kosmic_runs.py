from __future__ import annotations

from contextlib import redirect_stderr
from io import StringIO
import os
import shutil
import stat
import subprocess
from concurrent.futures import ThreadPoolExecutor
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from skills.scripts import kosmic_runs
from skills.scripts import kosmic_project_skills
from skills.scripts.kosmic_runs import (
    INVENTORY_FILENAME,
    INVENTORY_SCHEMA,
    MANAGED_DIRECTORIES,
    InventoryError,
    RunRootError,
    audit_temporary_policy,
    load_migration_inventory,
    resolve_run_root,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def component_path(worktree: Path, name: str) -> Path:
    if name == ".tmp":
        return worktree / ".tmp"
    if name == "kosmic":
        return worktree / ".tmp" / "kosmic"
    return worktree / ".tmp" / "kosmic" / name


def init_worktree(base: Path, *, ignore_rule: str | None = ".tmp/\n") -> Path:
    worktree = base / "worktree"
    worktree.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(worktree)], check=True)
    if ignore_rule is not None:
        (worktree / ".gitignore").write_text(ignore_rule, encoding="utf-8")
    return worktree


def materialize_audit_tree(destination: Path) -> Path:
    """Copy the authoritative audit surface into a fresh Git repository."""
    destination.mkdir(parents=True)
    for relative in ("skills", "docs"):
        shutil.copytree(
            REPO_ROOT / relative,
            destination / relative,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
    shutil.copy2(REPO_ROOT / ".gitignore", destination / ".gitignore")
    (destination / ".tmp").mkdir(mode=0o700)
    subprocess.run(["git", "init", "-q", str(destination)], check=True)
    return destination


class MigrationInventoryTest(unittest.TestCase):
    def test_loads_versioned_inventory_with_story_baseline_counts(self) -> None:
        inventory = load_migration_inventory()
        self.assertEqual(inventory["schema"], INVENTORY_SCHEMA)

        callers = inventory["callers"]
        self.assertEqual(len(callers), 12)
        self.assertEqual(
            {classification: [row["classification"] for row in callers].count(classification) for classification in {row["classification"] for row in callers}},
            {"atomic-single-file": 1, "atomic-publication": 11},
        )

        consumers = inventory["policy_consumers"]
        self.assertEqual(len(consumers), 9)
        self.assertTrue(all(row["classification"] == "managed-run" for row in consumers))

        root_ignore = inventory["root_ignore"]
        self.assertEqual(root_ignore["classification"], "defect")

        managed = inventory["managed_callers"]
        self.assertEqual(len(managed), 2)
        self.assertTrue(all(row["mechanism"].startswith("managed_command_run(") for row in managed))

        rows = (*callers, *consumers, root_ignore)
        ids = [row["id"] for row in rows]
        self.assertEqual(len(ids), len(set(ids)))
        for row in rows:
            self.assertTrue(row["rationale"].strip(), row["id"])

    def test_rejects_inventory_that_escapes_the_classification_vocabulary(self) -> None:
        source = (REPO_ROOT / "skills" / "scripts" / INVENTORY_FILENAME).read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / INVENTORY_FILENAME
            tampered.write_text(source.replace('"atomic-publication"', '"convenient"'), encoding="utf-8")
            with self.assertRaises(InventoryError):
                load_migration_inventory(tampered)

    def test_rejects_unknown_inventory_schema(self) -> None:
        source = (REPO_ROOT / "skills" / "scripts" / INVENTORY_FILENAME).read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            tampered = Path(temporary) / INVENTORY_FILENAME
            tampered.write_text(source.replace(INVENTORY_SCHEMA, "kosmic.runs-inventory/v0"), encoding="utf-8")
            with self.assertRaises(InventoryError):
                load_migration_inventory(tampered)


class TemporaryPolicyAuditTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.tree = materialize_audit_tree(Path(temporary.name) / "repo")

    def audit(self):
        return audit_temporary_policy(self.tree)

    def project_module(self) -> Path:
        return self.tree / "skills" / "scripts" / "kosmic_project_skills.py"

    def test_clean_tree_passes_with_zero_unexplained_entries(self) -> None:
        report = self.audit()
        self.assertTrue(report.ok, report.findings)
        self.assertEqual(report.counts["callers"], 12)
        self.assertEqual(report.counts["atomic-publication"], 11)
        self.assertEqual(report.counts["atomic-single-file"], 1)
        self.assertEqual(report.counts["defect"], 0)
        self.assertEqual(report.counts["policy-consumers"], 9)
        self.assertEqual(report.counts["root-ignore"], 1)

    def test_real_repository_passes_the_same_audit(self) -> None:
        report = audit_temporary_policy(REPO_ROOT)
        self.assertTrue(report.ok, report.findings)

    def test_unclassified_default_tempfile_call_is_unexplained(self) -> None:
        module = self.project_module()
        module.write_text(
            module.read_text(encoding="utf-8") + "\n\ndef stray():\n    return tempfile.mkdtemp()\n",
            encoding="utf-8",
        )
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("UNEXPLAINED_TEMPFILE_CALL") for finding in report.findings), report.findings)

    def test_bare_tempfile_import_and_call_is_unexplained(self) -> None:
        module = self.project_module()
        module.write_text(
            module.read_text(encoding="utf-8") + "\nfrom tempfile import mkdtemp\nstray = mkdtemp()\n",
            encoding="utf-8",
        )
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("UNEXPLAINED_TEMPFILE_CALL") for finding in report.findings), report.findings)

    def test_removed_caller_leaves_a_stale_inventory_row(self) -> None:
        module = self.project_module()
        module.write_text(
            module.read_text(encoding="utf-8").replace(
                'descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)',
                'descriptor, temporary_name = 0, str(path) + ".new"',
            ),
            encoding="utf-8",
        )
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("STALE_INVENTORY_CALLER") for finding in report.findings), report.findings)

    def test_tmp_literal_in_production_source_is_forbidden(self) -> None:
        module = self.project_module()
        module.write_text(module.read_text(encoding="utf-8") + '\nLEAK = "/tmp/kosmic-leak"\n', encoding="utf-8")
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("FORBIDDEN_TEMP_PATH") for finding in report.findings), report.findings)

    def test_dev_shm_literal_in_production_source_is_forbidden(self) -> None:
        module = self.project_module()
        module.write_text(module.read_text(encoding="utf-8") + '\nLEAK = "/dev/shm/kosmic-leak"\n', encoding="utf-8")
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("FORBIDDEN_TEMP_PATH") for finding in report.findings), report.findings)

    def test_root_scratch_literal_in_production_source_is_forbidden(self) -> None:
        module = self.project_module()
        module.write_text(module.read_text(encoding="utf-8") + '\nLEAK = Path(repo) / "scratch"\n', encoding="utf-8")
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("ROOT_SCRATCH_PATH") for finding in report.findings), report.findings)

    def test_new_duplicate_policy_document_is_unexplained(self) -> None:
        document = self.tree / "skills" / "references" / "task_other.md"
        document.write_text("# Other\n\nRun prototypes under `.tmp/<task-slug>/` and delete them afterwards.\n", encoding="utf-8")
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("UNEXPLAINED_POLICY_CONSUMER") for finding in report.findings), report.findings)

    def test_removed_policy_anchor_makes_consumer_row_stale(self) -> None:
        document = self.tree / "skills" / "references" / "task_create_spec.md"
        document.write_text(document.read_text(encoding="utf-8").replace("mandatory managed run", "in the workspace"), encoding="utf-8")
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("STALE_INVENTORY_CONSUMER") for finding in report.findings), report.findings)

    def test_missing_root_ignore_rule_fails_closed(self) -> None:
        (self.tree / ".gitignore").write_text("Refs/\n", encoding="utf-8")
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("ROOT_IGNORE_MISSING") for finding in report.findings), report.findings)

    def test_negated_root_ignore_rule_fails_closed(self) -> None:
        (self.tree / ".gitignore").write_text("*\n!.tmp/\n", encoding="utf-8")
        report = self.audit()
        self.assertFalse(report.ok)
        self.assertTrue(any(finding.startswith("ROOT_IGNORE_MISSING") for finding in report.findings), report.findings)


class ResolveRunRootTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)

    def test_creates_private_managed_tree_below_git_worktree(self) -> None:
        worktree = init_worktree(self.base)
        root = resolve_run_root(worktree)
        with root:
            self.assertEqual(root.worktree, worktree)
            self.assertEqual(root.path, worktree / ".tmp" / "kosmic")
            self.assertEqual(root.device, os.stat(worktree / ".tmp" / "kosmic").st_dev)
            kosmic_stat = os.stat(worktree / ".tmp" / "kosmic")
            self.assertTrue(stat.S_ISDIR(kosmic_stat.st_mode))
            self.assertEqual(stat.S_IMODE(kosmic_stat.st_mode), 0o700)
            for name in MANAGED_DIRECTORIES:
                component_stat = os.stat(worktree / ".tmp" / "kosmic" / name)
                self.assertTrue(stat.S_ISDIR(component_stat.st_mode), name)
                self.assertEqual(stat.S_IMODE(component_stat.st_mode), 0o700, name)
                self.assertEqual(component_stat.st_uid, os.geteuid(), name)
        with self.assertRaises(OSError):
            os.fstat(root.handles_fd)

    def test_resolve_is_idempotent_on_an_existing_tree(self) -> None:
        worktree = init_worktree(self.base)
        first = resolve_run_root(worktree)
        first.close()
        second = resolve_run_root(worktree)
        second.close()
        self.assertEqual(first.path, second.path)

    def test_rejects_non_git_directory_with_no_git_worktree(self) -> None:
        plain = self.base / "plain"
        plain.mkdir()
        with self.assertRaises(RunRootError) as context:
            resolve_run_root(plain)
        self.assertEqual(context.exception.code, "NO_GIT_WORKTREE")

    def test_rejects_missing_worktree_with_no_git_worktree(self) -> None:
        with self.assertRaises(RunRootError) as context:
            resolve_run_root(self.base / "absent")
        self.assertEqual(context.exception.code, "NO_GIT_WORKTREE")

    def test_rejects_missing_root_ignore_rule(self) -> None:
        worktree = init_worktree(self.base, ignore_rule="Refs/\n")
        with self.assertRaises(RunRootError) as context:
            resolve_run_root(worktree)
        self.assertEqual(context.exception.code, "ROOT_IGNORE_MISSING")

    def test_rejects_negated_root_ignore_rule(self) -> None:
        worktree = init_worktree(self.base, ignore_rule="*\n!.tmp/\n")
        with self.assertRaises(RunRootError) as context:
            resolve_run_root(worktree)
        self.assertEqual(context.exception.code, "ROOT_IGNORE_MISSING")

    def test_rejects_symlinked_path_components(self) -> None:
        for name in (".tmp", "kosmic", *MANAGED_DIRECTORIES):
            with self.subTest(component=name):
                scratch = self.base / f"case-{name}"
                worktree = init_worktree(scratch)
                resolve_run_root(worktree).close()
                component = component_path(worktree, name)
                if name == ".tmp":
                    shutil.rmtree(component)
                elif name == "kosmic":
                    shutil.rmtree(worktree / ".tmp")
                    (worktree / ".tmp").mkdir()
                else:
                    component.rmdir()
                elsewhere = scratch / "elsewhere"
                elsewhere.mkdir()
                component.symlink_to(elsewhere)
                with self.assertRaises(RunRootError) as context:
                    resolve_run_root(worktree)
                self.assertEqual(context.exception.code, "COMPONENT_SYMLINK", name)

    def test_rejects_non_directory_components(self) -> None:
        for name in (".tmp", "kosmic", "handles"):
            with self.subTest(component=name):
                scratch = self.base / f"file-{name}"
                worktree = init_worktree(scratch)
                if name == ".tmp":
                    (worktree / ".tmp").write_text("not a directory", encoding="utf-8")
                elif name == "kosmic":
                    resolve_run_root(worktree).close()
                    shutil.rmtree(worktree / ".tmp")
                    (worktree / ".tmp").mkdir()
                    (worktree / ".tmp" / "kosmic").write_text("not a directory", encoding="utf-8")
                else:
                    resolve_run_root(worktree).close()
                    component = component_path(worktree, name)
                    component.rmdir()
                    component.write_text("not a directory", encoding="utf-8")
                with self.assertRaises(RunRootError) as context:
                    resolve_run_root(worktree)
                self.assertEqual(context.exception.code, "COMPONENT_NOT_DIRECTORY", name)

    def test_rejects_relaxed_component_modes(self) -> None:
        cases = {"kosmic": 0o755, "runs": 0o755, "handles": 0o750, ".tmp": 0o777}
        for name, mode in cases.items():
            with self.subTest(component=name, mode=oct(mode)):
                scratch = self.base / f"mode-{name}"
                worktree = init_worktree(scratch)
                resolve_run_root(worktree).close()
                component_path(worktree, name).chmod(mode)
                with self.assertRaises(RunRootError) as context:
                    resolve_run_root(worktree)
                self.assertEqual(context.exception.code, "COMPONENT_MODE_MISMATCH", name)

    def test_resolution_never_consults_temporary_environment_defaults(self) -> None:
        worktree = init_worktree(self.base)
        polluted = {"TMPDIR": str(self.base / "nonexistent-tmpdir"), "TEMP": str(self.base / "nonexistent-temp"), "TMP": str(self.base / "nonexistent-tmp")}
        with mock.patch.dict(os.environ, polluted):
            root = resolve_run_root(worktree)
        root.close()
        self.assertEqual(root.path, worktree / ".tmp" / "kosmic")
        self.assertFalse((self.base / "nonexistent-tmpdir").exists())


class ComponentValidationTest(unittest.TestCase):
    @staticmethod
    def fabricated(*, file_type: int = stat.S_IFDIR, uid: int | None = None, device: int = 1, mode: int = 0o700):
        actual_uid = os.geteuid() if uid is None else uid
        return type("FabricatedStat", (), {"st_mode": file_type | mode, "st_uid": actual_uid, "st_dev": device})()

    def test_rejects_non_directory_type_owner_mode_and_device(self) -> None:
        cases = [("COMPONENT_NOT_DIRECTORY", dict(file_type=stat.S_IFREG), True, 1), ("COMPONENT_OWNER_MISMATCH", dict(uid=os.geteuid() + 1), True, 1), ("COMPONENT_MODE_MISMATCH", dict(mode=0o755), True, 1), ("COMPONENT_MODE_MISMATCH", dict(mode=0o750), True, 1), ("COMPONENT_MODE_MISMATCH", dict(mode=0o770), False, 1), ("DEVICE_MISMATCH", dict(device=2), True, 1)]
        for code, attributes, private, expected_device in cases:
            with self.subTest(code=code, **attributes):
                with self.assertRaises(RunRootError) as context:
                    kosmic_runs._validate_component_stat("component", self.fabricated(**attributes), expected_device=expected_device, private=private)
                self.assertEqual(context.exception.code, code)

    def test_accepts_private_and_shared_component_shapes(self) -> None:
        kosmic_runs._validate_component_stat("component", self.fabricated(mode=0o700), expected_device=1, private=True)
        for shared_mode in (0o700, 0o755):
            kosmic_runs._validate_component_stat("component", self.fabricated(mode=shared_mode), expected_device=1, private=False)

    def test_component_on_an_unexpected_device_fails_closed(self) -> None:
        if os.stat("/tmp").st_dev == os.stat(REPO_ROOT).st_dev:
            self.skipTest("workstation has no second local device")
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            (parent / "child").mkdir(mode=0o700)
            parent_fd = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_CLOEXEC)
            try:
                with self.assertRaises(RunRootError) as context:
                    kosmic_runs._open_component(parent_fd, "child", expected_device=os.stat(REPO_ROOT).st_dev, private=True)
                self.assertEqual(context.exception.code, "DEVICE_MISMATCH")
            finally:
                os.close(parent_fd)


if __name__ == "__main__":
    unittest.main()


# ---------------------------------------------------------------------------
# Managed-run lifecycle tests (Stories 044-047, 052)
# ---------------------------------------------------------------------------

import base64
import fcntl
import sys
import time
import hashlib
import json as _json
import signal
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath

from skills.scripts.kosmic_runs import (
    FAILURE_RETENTION,
    EXTENSION_CAP,
    UNLOCK_GRACE,
    RunError,
    RunEntry,
    capture_git_snapshot,
    begin_run,
    extend_run,
    finish_run,
    git_delta,
    promote_file,
    recover_cleanup_operations,
    report_runs,
    report_to_json,
    run_live_status,
    validate_run_manifest,
    _parse_porcelain_v2,
)

CLI = REPO_ROOT / "skills" / "scripts" / "kosmic_project_skills.py"
UTC = timezone.utc


def committed_worktree(base: Path, name: str = "worktree") -> Path:
    worktree = init_worktree(base)
    (worktree / "tracked.txt").write_text("initial\n", encoding="utf-8")
    run = subprocess.run(["git", "-C", str(worktree), "add", "-A"], check=True, capture_output=True)
    subprocess.run(
        ["git", "-C", str(worktree), "-c", "user.email=t@example.com", "-c", "user.name=T",
         "commit", "-q", "-m", "seed"], check=True, capture_output=True,
    )
    return worktree


class LifecycleTestCase(unittest.TestCase):
    """Shared fixture: a committed worktree plus holder teardown."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.worktree = committed_worktree(self.base)
        self._holder_pids: list[int] = []

    def track(self, handle) -> None:
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        self._holder_pids.append(int(manifest["holder_pid"]))

    def tearDown(self) -> None:
        for pid in self._holder_pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        kosmic_runs._clock = None


class GitSnapshotTest(LifecycleTestCase):
    def test_parses_all_porcelain_v2_record_kinds_with_nul_paths(self) -> None:
        raw = (
            b"# branch.oid 4b825dc642cb6eb9a060e54bf8d69288fbee4904\0"
            b"# branch.head main\0"
            b"# branch.upstream origin/main\0"
            b"# branch.ab +0 -0\0"
            b"1 .M N... 100644 100644 100644 abcdef0001 abcdef0002 path with spaces.txt\0"
            b"2 R. N... 100644 100644 100644 abcdef0001 abcdef0002 R100 new name.txt\0old name.txt\0"
            b"u AA N... 100644 100644 100644 100644 abcdef1 abcdef2 abcdef3 merged.txt\0"
            b"? untracked file.txt\0"
            b"! ignored.log\0"
        )
        parsed = _parse_porcelain_v2(raw, source="probe")
        self.assertEqual(parsed["branch"]["branch.head"], "main")
        kinds = [entry["kind"] for entry in parsed["entries"]]
        self.assertEqual(kinds, ["ordinary", "renamed", "unmerged", "untracked", "ignored"])
        self.assertEqual(parsed["entries"][0]["path"], "path with spaces.txt")
        self.assertEqual(parsed["entries"][1]["path"], "new name.txt")
        self.assertEqual(parsed["entries"][1]["orig_path"], "old name.txt")

    def test_rejects_unknown_records_and_missing_final_nul(self) -> None:
        with self.assertRaises(RunError) as context:
            _parse_porcelain_v2(b"9 XY broken\0", source="probe")
        self.assertEqual(context.exception.code, "GIT_SNAPSHOT_UNKNOWN_RECORD")
        with self.assertRaises(RunError) as context:
            _parse_porcelain_v2(b"? no terminator", source="probe")
        self.assertEqual(context.exception.code, "GIT_SNAPSHOT_UNKNOWN_RECORD")

    def test_capture_records_identity_branch_and_paths(self) -> None:
        (self.worktree / "nested").mkdir()
        (self.worktree / "nested" / "un tracked.txt").write_text("x", encoding="utf-8")
        snapshot = capture_git_snapshot(self.worktree, name="probe")
        self.assertIsInstance(snapshot.branch, str)
        self.assertEqual(len(snapshot.head), 40)
        self.assertIn("nested/un tracked.txt", snapshot.paths)
        self.assertEqual(snapshot.sha256, hashlib.sha256(snapshot.raw).hexdigest())

    def test_capture_supports_detached_head_and_unborn_repository(self) -> None:
        subprocess.run(["git", "-C", str(self.worktree), "checkout", "-q", "--detach"], check=True, capture_output=True)
        detached = capture_git_snapshot(self.worktree, name="detached")
        self.assertIsNone(detached.branch)
        self.assertIsNotNone(detached.head)
        fresh = init_worktree(self.base / "fresh")
        unborn = capture_git_snapshot(fresh, name="unborn")
        self.assertIsNone(unborn.head)
        self.assertIsNone(unborn.branch_oid)

    def test_capture_failure_returns_stable_error(self) -> None:
        broken = self.base / "broken"
        broken.mkdir()
        with self.assertRaises(RunError) as context:
            capture_git_snapshot(broken, name="broken")
        self.assertEqual(context.exception.code, "GIT_CAPTURE_FAILED")

    def test_delta_classifies_paths_without_inferring_ownership(self) -> None:
        (self.worktree / "user.txt").write_text("concurrent user work\n", encoding="utf-8")
        (self.worktree / "gone.txt").write_text("transient\n", encoding="utf-8")
        first = capture_git_snapshot(self.worktree, name="first")
        (self.worktree / "user.txt").write_text("changed\n", encoding="utf-8")
        (self.worktree / "new.txt").write_text("new\n", encoding="utf-8")
        os.remove(self.worktree / "gone.txt")
        second = capture_git_snapshot(self.worktree, name="second")
        delta = git_delta(first, second)
        self.assertIn("new.txt", delta["introduced"])
        self.assertIn("user.txt", delta["modified"])
        self.assertIn("gone.txt", delta["pre_existing"])
        self.assertEqual(delta["unattributed"], [])
        self.assertFalse(delta["head_changed"])


class RunStoreTest(LifecycleTestCase):
    def test_manifest_schema_rejects_missing_unknown_and_invalid_values(self) -> None:
        def manifest(**overrides):
            base = {
                "schema": 1, "sequence": 1, "run_id": "20260915T000000Z-probe-" + "a" * 32,
                "project_id": "kosmic", "purpose": "probe", "state": "active",
                "retention": "diagnostic", "created_at": "2026-09-15T00:00:00Z",
                "finished_at": None, "expires_at": "2026-09-16T00:00:00Z",
                "lease_expires_at": "2026-09-16T00:00:00Z", "holder_pid": 42,
                "token_sha256": "b" * 64, "worktree_root": "/tmp-x", "git_common_dir": "/tmp-x",
                "git_start_sha256": "c" * 64, "git_finish_sha256": None, "snapshot_complete": False,
            }
            base.update(overrides)
            return base

        validate_run_manifest(manifest())
        cases = [
            dict(schema=2),
            dict(state="weird"),
            dict(retention="weekly"),
            dict(retention="extended-diagnostic"),
            dict(token_sha256="nothex"),
            dict(created_at="not-a-time"),
            dict(sequence=0),
            dict(run_id="20260915T000000Z-probe"),
            dict(git_finish_sha256="zz"),
            dict(snapshot_complete="yes"),
        ]
        for overrides in cases:
            with self.subTest(**overrides):
                with self.assertRaises(RunError):
                    validate_run_manifest(manifest(**overrides))
        with self.assertRaises(RunError) as context:
            validate_run_manifest({"schema": 1})
        self.assertEqual(context.exception.code, "MANIFEST_INVALID")


class BeginFinishTest(LifecycleTestCase):
    def test_begin_creates_private_leased_run_with_git_evidence(self) -> None:
        handle = begin_run(self.worktree, purpose="Evidence Run")
        self.track(handle)
        self.assertEqual(handle.state, "active")
        self.assertNotIn(" ", handle.run_id)
        run_dir = self.worktree / ".tmp" / "kosmic" / "runs" / handle.run_id
        self.assertTrue((run_dir / "RUN.json").is_file())
        raw = (run_dir / "git" / "start-status.porcelain-v2").read_bytes()
        manifest = _json.loads((run_dir / "RUN.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["state"], "active")
        self.assertEqual(manifest["git_start_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(stat.S_IMODE(os.stat(run_dir / "RUN.lock").st_mode), 0o600)
        for child in ("input", "output", "logs", "scratch", "git"):
            self.assertTrue(stat.S_ISDIR(os.stat(run_dir / child).st_mode), child)
        handle_stat = os.stat(handle.handle_file)
        self.assertEqual(stat.S_IMODE(handle_stat.st_mode), 0o600)

    def test_unknown_retention_and_active_bounds_reject(self) -> None:
        with self.assertRaises(RunError) as context:
            begin_run(self.worktree, purpose="p", retention="weekly")
        self.assertEqual(context.exception.code, "RETENTION_UNKNOWN")
        with self.assertRaises(RunError) as context:
            begin_run(self.worktree, purpose="p", active_for=timedelta(days=8))
        self.assertEqual(context.exception.code, "ACTIVE_FOR_INVALID")
        with self.assertRaises(RunError) as context:
            begin_run(self.worktree, purpose="p", active_for=timedelta(0))
        self.assertEqual(context.exception.code, "ACTIVE_FOR_INVALID")

    def test_holder_keeps_lock_across_processes_and_finish_commits_terminal_state(self) -> None:
        handle = begin_run(self.worktree, purpose="cross call")
        # Independent probe: the detached holder keeps flock after begin returns.
        probe = subprocess.run(
            ["python3", "-c",
             "import fcntl, sys\n"
             f"fd = open({str(handle.path / 'RUN.lock')!r}, 'r')\n"
             "try:\n"
             "    fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)\n"
             "    print('FREE')\n"
             "except BlockingIOError:\n"
             "    print('HELD')\n"],
            capture_output=True, text=True, check=True,
        )
        self.assertEqual(probe.stdout.strip(), "HELD")
        receipt = finish_run(handle.handle_file, "succeeded")
        self.assertEqual(receipt.state, "succeeded")
        manifest_dir = handle.path
        self.assertFalse(manifest_dir.exists(), "diagnostic success must delete the run")

    def test_finish_failure_retains_run_with_72h_expiry_and_git_evidence(self) -> None:
        handle = begin_run(self.worktree, purpose="failing")
        self.track(handle)
        receipt = finish_run(handle.handle_file, "failed", detail="reproducer")
        self.assertTrue(handle.path.exists())
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["state"], "failed")
        self.assertTrue(manifest["snapshot_complete"])
        created = datetime.strptime(manifest["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        expiry = datetime.strptime(manifest["expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        finished = datetime.strptime(manifest["finished_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        self.assertEqual(expiry - finished, FAILURE_RETENTION)
        self.assertLessEqual(abs(finished - created), timedelta(seconds=30))
        self.assertTrue((handle.path / "git" / "finish-status.porcelain-v2").is_file())
        delta = _json.loads((handle.path / "git" / "delta.json").read_text(encoding="utf-8"))
        self.assertEqual(delta["schema"], 1)

    def test_disposable_failure_is_deleted_during_finalization(self) -> None:
        handle = begin_run(self.worktree, purpose="disposable fail", retention="disposable")
        finish_run(handle.handle_file, "failed")
        self.assertFalse(handle.path.exists())

    def test_finish_is_idempotent_and_conflicting_outcome_rejected(self) -> None:
        handle = begin_run(self.worktree, purpose="retry")
        self.track(handle)
        first = finish_run(handle.handle_file, "failed")
        second = finish_run(handle.handle_file, "failed")
        self.assertEqual(first.run_id, second.run_id)
        self.assertEqual(second.code, "OK")
        with self.assertRaises(RunError) as context:
            finish_run(handle.handle_file, "succeeded")
        self.assertEqual(context.exception.code, "RUN_ALREADY_FINALIZED")

    def test_token_never_appears_in_owned_output(self) -> None:
        secret_handle = begin_run(self.worktree, purpose="secret-keepout x7K9TOKENVALUE")
        self.track(secret_handle)
        raw_handle = (secret_handle.handle_file).read_text(encoding="utf-8")
        token = base64.b64decode(_json.loads(raw_handle)["token"])
        receipt = finish_run(secret_handle.handle_file, "failed", detail="detail")
        outputs = [
            _json.dumps(report_to_json(report_runs(self.worktree))),
            _json.dumps(kosmic_runs.receipt_to_json(receipt)),
            (secret_handle.handle_file).read_text(encoding="utf-8"),
        ]
        history = self.worktree / ".tmp" / "kosmic" / "history.jsonl"
        if history.exists():
            outputs.append(history.read_text(encoding="utf-8"))
        for text in outputs:
            self.assertNotIn(token.hex(), text)
            self.assertNotIn(base64.b64encode(token).decode(), text)

    def test_live_unreachable_when_lock_held_without_holder(self) -> None:
        handle = begin_run(self.worktree, purpose="held")
        self.track(handle)
        lock_fd = os.open(handle.path / "RUN.lock", os.O_RDWR)
        try:
            fcntl.flock(lock_fd, fcntl.LOCK_SH | fcntl.LOCK_NB)  # holder holds EX; SH also conflicts
            held = False
        except BlockingIOError:
            held = True
        self.assertTrue(held)
        # Kill the holder but keep our own exclusive hold on the lock.
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        os.kill(manifest["holder_pid"], signal.SIGKILL)
        time.sleep(0.2)  # kernel releases flock at process death
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        with self.assertRaises(RunError) as context:
            finish_run(handle.handle_file, "succeeded")
        self.assertEqual(context.exception.code, "LIVE_UNREACHABLE")
        # no mutation happened
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["state"], "active")
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)

    def test_holder_crash_leaves_unlocked_candidate_then_owner_finishes(self) -> None:
        handle = begin_run(self.worktree, purpose="crash")
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        os.kill(manifest["holder_pid"], signal.SIGKILL)
        time.sleep(0.2)  # kernel releases flock at process death
        status = run_live_status(self.worktree, handle.run_id)
        self.assertTrue(status["abandoned_candidate"])
        self.assertIn("grace_until", status)
        report = report_runs(self.worktree)
        entry = [e for e in report.entries if e.run_id == handle.run_id][0]
        self.assertEqual(entry.category, "abandoned")
        self.assertIn("in-grace", entry.flags)
        receipt = finish_run(handle.handle_file, "succeeded")
        self.assertEqual(receipt.state, "succeeded")

    def test_active_ttl_expiry_transitions_to_abandoned_under_lock(self) -> None:
        handle = begin_run(self.worktree, purpose="ttl", active_for=timedelta(seconds=1))
        deadline = datetime.now(UTC) + timedelta(seconds=8)
        while datetime.now(UTC) < deadline:
            status = run_live_status(self.worktree, handle.run_id)
            if status["code"] == "OK" and status.get("state") == "abandoned":
                break
            time.sleep(0.5)
        status = run_live_status(self.worktree, handle.run_id)
        self.assertEqual(status["state"], "abandoned")
        report = report_runs(self.worktree)
        entry = [e for e in report.entries if e.run_id == handle.run_id][0]
        self.assertEqual(entry.category, "abandoned")
        with self.assertRaises(RunError) as context:
            finish_run(handle.handle_file, "succeeded")
        self.assertEqual(context.exception.code, "RUN_ALREADY_FINALIZED")

    def test_interrupted_finalization_recovers_requested_outcome(self) -> None:
        handle = begin_run(self.worktree, purpose="recovery")
        environment = {**os.environ, "KOSMIC_RUNS_FAULT": "after-outcome-persist"}
        with mock.patch.dict(os.environ, environment):
            with self.assertRaises(kosmic_runs._FaultInjected):
                finish_run(handle.handle_file, "failed", detail="interrupted")
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["state"], "finalizing")
        self.assertEqual(manifest["requested_outcome"], "failed")
        receipt = finish_run(handle.handle_file, "failed")
        self.assertEqual(receipt.state, "failed")
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["state"], "failed")
        self.assertTrue(manifest["snapshot_complete"])

    def test_fault_after_manifest_commit_publishes_receipt_on_replay(self) -> None:
        handle = begin_run(self.worktree, purpose="receipt-crash")
        environment = {**os.environ, "KOSMIC_RUNS_FAULT": "after-manifest-commit"}
        with mock.patch.dict(os.environ, environment):
            with self.assertRaises(kosmic_runs._FaultInjected):
                finish_run(handle.handle_file, "failed")
        handle_data = _json.loads(handle.handle_file.read_text(encoding="utf-8"))
        self.assertEqual(handle_data["kind"], "handle")  # receipt not yet published
        receipt = finish_run(handle.handle_file, "failed")
        self.assertEqual(receipt.state, "failed")


class RetentionAndReceiptTest(LifecycleTestCase):
    def finished_failure(self, purpose: str = "retention probe"):
        handle = begin_run(self.worktree, purpose=purpose)
        receipt = finish_run(handle.handle_file, "failed")
        return handle, receipt

    def test_failed_diagnostic_expires_exactly_after_72_hours(self) -> None:
        handle, _ = self.finished_failure()
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        finished = datetime.strptime(manifest["finished_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        kosmic_runs._clock = lambda: finished + FAILURE_RETENTION - timedelta(seconds=1)
        report = report_runs(self.worktree)
        entry = [e for e in report.entries if e.run_id == handle.run_id][0]
        self.assertEqual(entry.category, "retained")
        kosmic_runs._clock = lambda: finished + FAILURE_RETENTION
        report = report_runs(self.worktree)
        entry = [e for e in report.entries if e.run_id == handle.run_id][0]
        self.assertEqual(entry.category, "expired")

    def test_extend_only_after_diagnostic_failure_capped_at_seven_days(self) -> None:
        handle, _ = self.finished_failure()
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        finished = datetime.strptime(manifest["finished_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        target = finished + timedelta(days=4)
        kosmic_runs._clock = lambda: finished + timedelta(hours=1)
        extended = extend_run(handle.handle_file, target)
        self.assertEqual(extended.expires_at, target)
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["retention"], "extended-diagnostic")
        # idempotent repeat returns the receipt unchanged
        repeat = extend_run(handle.handle_file, target - timedelta(hours=1))
        self.assertEqual(repeat.expires_at, target)
        with self.assertRaises(RunError) as context:
            extend_run(handle.handle_file, finished + EXTENSION_CAP + timedelta(hours=1))
        self.assertEqual(context.exception.code, "EXTENSION_CAP_EXCEEDED")

    def test_extend_rejects_non_failed_states(self) -> None:
        handle = begin_run(self.worktree, purpose="active-extend")
        self.track(handle)
        with self.assertRaises(RunError) as context:
            extend_run(handle.handle_file, datetime.now(UTC) + timedelta(days=1))
        self.assertEqual(context.exception.code, "EXTENSION_INVALID_STATE")
        finish_run(handle.handle_file, "succeeded")
        # a disposable failure is deleted during finalization, so extension of
        # anything but a retained failed diagnostic run is structurally impossible

    def test_receipt_expires_after_thirty_days(self) -> None:
        handle, receipt = self.finished_failure()
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        finished = datetime.strptime(manifest["finished_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        receipt_data = _json.loads(handle.handle_file.read_text(encoding="utf-8"))
        self.assertEqual(receipt_data["kind"], "receipt")
        self.assertNotIn("token", receipt_data)  # only the hash survives
        kosmic_runs._clock = lambda: finished + timedelta(days=29)
        report = report_runs(self.worktree)
        categories = {e.report_only_reason for e in report.entries if e.run_id == handle.run_id}
        self.assertIn("terminal-receipt", categories)
        kosmic_runs._clock = lambda: finished + timedelta(days=31)
        report = report_runs(self.worktree)
        categories = {e.report_only_reason for e in report.entries if e.run_id == handle.run_id}
        self.assertIn("receipt-expired", categories)

    def test_secrets_never_enter_lifecycle_output(self) -> None:
        secret = "hunter2-SUPERSECRET"
        with mock.patch.dict(os.environ, {"AWS_SECRET_ACCESS_KEY": secret}):
            handle, receipt = self.finished_failure("ambient secret probe")
        artifacts = handle.handle_file.read_text(encoding="utf-8")
        artifacts += (handle.path / "RUN.json").read_text(encoding="utf-8")
        history = self.worktree / ".tmp" / "kosmic" / "history.jsonl"
        if history.exists():
            artifacts += history.read_text(encoding="utf-8")
        self.assertNotIn(secret, artifacts)


class CleanupTransactionTest(LifecycleTestCase):
    def test_owner_cleanup_journals_quarantine_delete_and_history(self) -> None:
        handle = begin_run(self.worktree, purpose="clean me")
        (handle.path / "scratch" / "data.bin").parent.mkdir(parents=True, exist_ok=True)
        (handle.path / "scratch" / "data.bin").write_bytes(b"0" * 4096)
        receipt = finish_run(handle.handle_file, "succeeded")
        self.assertEqual(receipt.code, "OK")
        self.assertFalse(handle.path.exists())
        operations = self.worktree / ".tmp" / "kosmic" / "operations"
        self.assertEqual(os.listdir(operations), [])
        quarantine = self.worktree / ".tmp" / "kosmic" / "quarantine"
        self.assertEqual(os.listdir(quarantine), [])
        history = [_json.loads(line) for line in (self.worktree / ".tmp" / "kosmic" / "history.jsonl").read_text(encoding="utf-8").splitlines()]
        cleanups = [record for record in history if record["kind"] == "cleanup"]
        self.assertEqual(len(cleanups), 1)
        self.assertEqual(cleanups[0]["result"], "removed")
        self.assertEqual(cleanups[0]["git_delta"], {
            "schema": 1,
            "head_changed": False,
            "pre_existing": [],
            "introduced": [],
            "modified": [],
            "removed": [],
            "renamed": [],
            "unattributed": [],
        })
        self.assertNotIn("b\"0\" * 4096", _json.dumps(history))
        self.assertNotIn(b"0" * 4096, (self.worktree / ".tmp" / "kosmic" / "history.jsonl").read_bytes())

    def _interrupted_cleanup(self, fault: str, outcome: str = "succeeded", purpose: str = "faulted"):
        handle = begin_run(self.worktree, purpose=purpose)
        environment = {**os.environ, "KOSMIC_RUNS_FAULT": fault}
        with mock.patch.dict(os.environ, environment):
            with self.assertRaises(kosmic_runs._FaultInjected):
                finish_run(handle.handle_file, outcome)
        return handle

    def test_fault_after_planned_resumes_through_recovery(self) -> None:
        handle = self._interrupted_cleanup("cleanup-after-planned")
        operations = self.worktree / ".tmp" / "kosmic" / "operations"
        self.assertEqual(len(os.listdir(operations)), 1)
        reports = recover_cleanup_operations(self.worktree)
        self.assertTrue(any(r.get("recovered") for r in reports), reports)
        self.assertFalse(handle.path.exists())
        self.assertEqual(os.listdir(operations), [])

    def test_fault_after_quarantine_resumes_deletion(self) -> None:
        handle = self._interrupted_cleanup("cleanup-after-quarantine")
        quarantine = self.worktree / ".tmp" / "kosmic" / "quarantine"
        self.assertEqual(len(os.listdir(quarantine)), 1)
        recover_cleanup_operations(self.worktree)
        self.assertFalse(handle.path.exists())
        self.assertEqual(os.listdir(quarantine), [])
        receipt = _json.loads(handle.handle_file.read_text(encoding="utf-8"))
        self.assertEqual((receipt["kind"], receipt["cleanup"]), ("receipt", "removed"))

    def test_fault_after_removed_resumes_history_and_recording(self) -> None:
        handle = self._interrupted_cleanup("cleanup-after-removed")
        self.assertFalse(handle.path.exists())
        operations = self.worktree / ".tmp" / "kosmic" / "operations"
        self.assertEqual(len(os.listdir(operations)), 1)
        recover_cleanup_operations(self.worktree)
        self.assertEqual(os.listdir(operations), [])

    def test_fault_after_history_recovers_receipt_idempotently(self) -> None:
        handle = self._interrupted_cleanup("cleanup-after-history")
        self.assertFalse(handle.path.exists())

        recover_cleanup_operations(self.worktree)
        recover_cleanup_operations(self.worktree)

        receipt = _json.loads(handle.handle_file.read_text(encoding="utf-8"))
        self.assertEqual((receipt["kind"], receipt["cleanup"]), ("receipt", "removed"))
        history = [
            _json.loads(line)
            for line in (self.worktree / ".tmp" / "kosmic" / "history.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(sum(entry.get("run_id") == handle.run_id for entry in history), 1)
    def test_fault_after_receipt_replays_owner_cleanup(self) -> None:
        handle = self._interrupted_cleanup("after-receipt")
        # manifest committed, receipt published, cleanup interrupted
        receipt = finish_run(handle.handle_file, "succeeded")
        self.assertEqual(receipt.code, "OK")
        self.assertFalse(handle.path.exists())

    def test_recovery_conflict_and_orphan_quarantine_are_report_only(self) -> None:
        handle = self._interrupted_cleanup("cleanup-after-quarantine")
        quarantine = self.worktree / ".tmp" / "kosmic" / "quarantine"
        op_name = os.listdir(operations := self.worktree / ".tmp" / "kosmic" / "operations")[0]
        op_id = op_name[: -len(".json")]
        # fabricate the conflict quadrant: source present AND quarantine present
        handle.path.mkdir(parents=True)
        (handle.path / "RUN.json").write_text("{}", encoding="utf-8")
        reports = recover_cleanup_operations(self.worktree)
        self.assertTrue(any(r.get("reason") == "RECOVERY_CONFLICT" for r in reports), reports)
        # orphan quarantine child without an operation record
        os.remove(operations / op_name)
        shutil.rmtree(quarantine / op_id)
        (quarantine / "orphan-child").mkdir()
        reports = recover_cleanup_operations(self.worktree)
        self.assertTrue(any(r.get("reason") == "ORPHAN_QUARANTINE_CHILD" for r in reports), reports)
        self.assertTrue((quarantine / "orphan-child").exists())

    def test_cleanup_refuses_active_and_untrusted_runs(self) -> None:
        handle = begin_run(self.worktree, purpose="active run")
        self.track(handle)
        root = kosmic_runs.resolve_run_root(self.worktree)
        run_fd = kosmic_runs._open_run(root.runs_fd, handle.run_id)
        manifest = kosmic_runs.load_manifest(run_fd, run_id=handle.run_id)
        try:
            with self.assertRaises(RunError) as context:
                kosmic_runs._execute_cleanup_transaction(root, handle.run_id, manifest)
            self.assertEqual(context.exception.code, "RUN_ACTIVE")
        finally:
            os.close(run_fd)
            root.close()
        finish_run(handle.handle_file, "failed")
        # relaxed permissions make the run untrusted
        os.chmod(handle.path, 0o755)
        report = report_runs(self.worktree)
        entry = [e for e in report.entries if e.run_id == handle.run_id][0]
        self.assertEqual(entry.category, "malformed")
        self.assertEqual(entry.report_only_reason, "UNTRUSTED_OWNER_MODE")
        reports = recover_cleanup_operations(self.worktree)
        self.assertTrue(all(r.get("result") != "removed" for r in reports))

    def test_history_rotation_bounds_size_and_age(self) -> None:
        handle = begin_run(self.worktree, purpose="rotation")
        finish_run(handle.handle_file, "succeeded")
        root = kosmic_runs.resolve_run_root(self.worktree)
        history = self.worktree / ".tmp" / "kosmic" / "history.jsonl"
        try:
            stale_record = {
                "schema": 1, "kind": "cleanup", "ts": "2020-01-01T00:00:00Z",
                "run_id": "x", "operation_id": "cleanup-20200101T000000Z-000000000000",
                "git_before_sha256": "0" * 64, "git_after_sha256": "0" * 64, "result": "removed",
            }
            # rotation triggers at the appended size and drops the stale record
            with mock.patch.object(kosmic_runs, "HISTORY_MAX_BYTES", history.stat().st_size):
                kosmic_runs._history_append(root, stale_record)
            content = history.read_text(encoding="utf-8")
            self.assertIn(handle.run_id, content)
            self.assertNotIn("2020-01-01T00:00:00Z", content)
        finally:
            root.close()

    def test_unrelated_worktree_files_survive_owner_cleanup(self) -> None:
        user_file = self.worktree / "precious-user-file.txt"
        user_file.write_text("do not touch\n", encoding="utf-8")
        handle = begin_run(self.worktree, purpose="neighbor")
        finish_run(handle.handle_file, "succeeded")
        self.assertEqual(user_file.read_text(encoding="utf-8"), "do not touch\n")
        # unattributed children under .tmp/kosmic are report-only
        foreign = self.worktree / ".tmp" / "kosmic" / "foreign.txt"
        foreign.write_text("user data", encoding="utf-8")
        handle2 = begin_run(self.worktree, purpose="second")
        self.track(handle2)
        finish_run(handle2.handle_file, "succeeded")
        report = report_runs(self.worktree)
        unattributed = [e for e in report.entries if e.category == "unattributed"]
        self.assertTrue(any(e.path.as_posix() == "foreign.txt" for e in unattributed))
        self.assertEqual(foreign.read_text(encoding="utf-8"), "user data")


class PromotionTest(LifecycleTestCase):
    def test_promote_publishes_contained_file_with_hashes_and_git_evidence(self) -> None:
        handle = begin_run(self.worktree, purpose="promote me")
        self.track(handle)
        source = handle.path / "output" / "report.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("promoted payload\n", encoding="utf-8")
        receipt = promote_file(handle.handle_file, PurePosixPath("output/report.txt"), Path("results/report.txt"))
        destination = self.worktree / "results" / "report.txt"
        self.assertEqual(destination.read_text(encoding="utf-8"), "promoted payload\n")
        self.assertEqual(receipt.destination, destination)
        self.assertEqual(
            receipt.destination_sha256,
            hashlib.sha256(b"promoted payload\n").hexdigest(),
        )
        self.assertEqual(receipt.source_sha256, receipt.destination_sha256)
        self.assertNotEqual(receipt.git_before_sha256, receipt.git_after_sha256)
        operations = self.worktree / ".tmp" / "kosmic" / "operations"
        op_files = os.listdir(operations)
        self.assertEqual(len(op_files), 1)
        record = _json.loads((operations / op_files[0]).read_text(encoding="utf-8"))
        self.assertEqual(record["kind"], "promotion")
        self.assertEqual(record["state"], "recorded")
        self.assertFalse(record["overwrite"])

    def test_promote_refuses_existing_destination_and_records_overwrite_precondition(self) -> None:
        handle = begin_run(self.worktree, purpose="clobber")
        source = handle.path / "scratch" / "new.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("new content\n", encoding="utf-8")
        destination_dir = self.worktree / "results"
        destination_dir.mkdir()
        (destination_dir / "out.txt").write_text("existing user content\n", encoding="utf-8")
        with self.assertRaises(RunError) as context:
            promote_file(handle.handle_file, PurePosixPath("scratch/new.txt"), Path("results/out.txt"))
        self.assertEqual(context.exception.code, "DESTINATION_EXISTS")
        self.assertEqual((destination_dir / "out.txt").read_text(encoding="utf-8"), "existing user content\n")
        receipt = promote_file(
            handle.handle_file, PurePosixPath("scratch/new.txt"), Path("results/out.txt"), overwrite=True
        )
        self.assertEqual((destination_dir / "out.txt").read_text(encoding="utf-8"), "new content\n")
        operations = self.worktree / ".tmp" / "kosmic" / "operations"
        record = _json.loads((operations / os.listdir(operations)[0]).read_text(encoding="utf-8"))
        self.assertTrue(record["overwrite"])
        self.assertTrue(record["destination_precondition"]["exists"])
        self.assertEqual(record["destination_precondition"]["sha256"], hashlib.sha256(b"existing user content\n").hexdigest())
        self.track(handle)

    def test_explicit_overwrite_never_loses_a_competing_destination_update(self) -> None:
        handle = begin_run(self.worktree, purpose="overwrite race")
        source = handle.path / "scratch" / "new.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("promoted content\n", encoding="utf-8")
        destination_dir = self.worktree / "results"
        destination_dir.mkdir()
        destination = destination_dir / "out.txt"
        destination.write_text("recorded precondition\n", encoding="utf-8")
        real_exchange = kosmic_runs._exchange_names
        exchange_count = 0

        def exchange_after_competing_update(dir_fd: int, left: str, right: str) -> None:
            nonlocal exchange_count
            if exchange_count == 0:
                competing = destination_dir / "competing.tmp"
                competing.write_text("competing user update\n", encoding="utf-8")
                os.replace(competing, destination)
            exchange_count += 1
            real_exchange(dir_fd, left, right)

        with mock.patch.object(kosmic_runs, "_exchange_names", side_effect=exchange_after_competing_update):
            with self.assertRaises(RunError) as context:
                promote_file(
                    handle.handle_file,
                    PurePosixPath("scratch/new.txt"),
                    Path("results/out.txt"),
                    overwrite=True,
                )

        self.assertEqual(context.exception.code, "PRECONDITION_MISMATCH")
        self.assertEqual(destination.read_text(encoding="utf-8"), "competing user update\n")
        operation = _json.loads(next((self.worktree / ".tmp" / "kosmic" / "operations").iterdir()).read_text(encoding="utf-8"))
        self.assertFalse((destination_dir / operation["staging_name"]).exists())
        self.assertEqual(source.read_text(encoding="utf-8"), "promoted content\n")
        self.track(handle)
    def test_promotion_crash_recovery_finishes_only_matching_publication(self) -> None:
        handle = begin_run(self.worktree, purpose="promotion crash")
        source = handle.path / "scratch" / "recoverable.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("recoverable payload\n", encoding="utf-8")
        environment = {**os.environ, "KOSMIC_RUNS_FAULT": "promote-after-staged"}
        with mock.patch.dict(os.environ, environment):
            with self.assertRaises(kosmic_runs._FaultInjected):
                promote_file(handle.handle_file, PurePosixPath("scratch/recoverable.txt"), Path("results/recoverable.txt"))
        operations = self.worktree / ".tmp" / "kosmic" / "operations"
        op_name = os.listdir(operations)[0]
        record = _json.loads((operations / op_name).read_text(encoding="utf-8"))
        self.assertEqual(record["state"], "staged")
        # recovery completes the matching staged publication
        reports = recover_cleanup_operations(self.worktree)
        recovered = [r for r in reports if r.get("result") == "published"]
        self.assertTrue(recovered, reports)
        self.assertEqual((self.worktree / "results" / "recoverable.txt").read_text(encoding="utf-8"), "recoverable payload\n")
        record = _json.loads((operations / op_name).read_text(encoding="utf-8"))
        self.assertEqual(record["state"], "recorded")
        self.assertIn("git_delta", record)
        history_records = [
            _json.loads(line)
            for line in (self.worktree / ".tmp" / "kosmic" / "history.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        recovered_history = [entry for entry in history_records if entry.get("operation_id") == record["operation_id"]]
        self.assertEqual(len(recovered_history), 1)
        self.assertEqual(recovered_history[0]["git_delta"], record["git_delta"])
        # an unexpected destination appearing after the staged record stays untouched
        handle2 = begin_run(self.worktree, purpose="ambiguity")
        source2 = handle2.path / "scratch" / "amb.txt"
        source2.parent.mkdir(parents=True, exist_ok=True)
        source2.write_text("amb\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {**os.environ, "KOSMIC_RUNS_FAULT": "promote-after-planned"}):
            with self.assertRaises(kosmic_runs._FaultInjected):
                promote_file(handle2.handle_file, PurePosixPath("scratch/amb.txt"), Path("results/amb.txt"))
        # stage the file manually to fabricate a staged op with an appeared destination
        amb_ops = [n for n in os.listdir(operations) if n != op_name]
        self.assertEqual(len(amb_ops), 1)
        amb_record = _json.loads((operations / amb_ops[0]).read_text(encoding="utf-8"))
        amb_record["state"] = "staged"
        (operations / amb_ops[0]).write_text(_json.dumps(amb_record), encoding="utf-8")
        (self.worktree / "results" / "amb.txt").write_text("user wrote this\n", encoding="utf-8")
        reports = recover_cleanup_operations(self.worktree)
        self.assertTrue(any(r.get("reason") == "DESTINATION_APPEARED" for r in reports), reports)
        self.assertEqual((self.worktree / "results" / "amb.txt").read_text(encoding="utf-8"), "user wrote this\n")
        self.track(handle)
        self.track(handle2)

    def test_promotion_recovery_records_git_delta_after_publication_crash(self) -> None:
        handle = begin_run(self.worktree, purpose="published crash")
        source = handle.path / "scratch" / "published.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("published before crash\n", encoding="utf-8")
        with mock.patch.dict(os.environ, {**os.environ, "KOSMIC_RUNS_FAULT": "promote-after-published"}):
            with self.assertRaises(kosmic_runs._FaultInjected):
                promote_file(
                    handle.handle_file,
                    PurePosixPath("scratch/published.txt"),
                    Path("results/published.txt"),
                )
        operations = self.worktree / ".tmp" / "kosmic" / "operations"
        op_path = operations / os.listdir(operations)[0]
        before_recovery = _json.loads(op_path.read_text(encoding="utf-8"))
        self.assertEqual(before_recovery["state"], "published")

        reports = recover_cleanup_operations(self.worktree)

        self.assertTrue(any(item.get("result") == "published" for item in reports), reports)
        recovered = _json.loads(op_path.read_text(encoding="utf-8"))
        self.assertEqual(recovered["state"], "recorded")
        self.assertIn("git_delta", recovered)
        history_records = [
            _json.loads(line)
            for line in (self.worktree / ".tmp" / "kosmic" / "history.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        recovered_history = [entry for entry in history_records if entry.get("operation_id") == recovered["operation_id"]]
        self.assertEqual(len(recovered_history), 1)
        self.assertEqual(recovered_history[0]["git_delta"], recovered["git_delta"])
        self.track(handle)
    def test_promote_rejects_escaping_sources_and_foreign_destinations(self) -> None:
        handle = begin_run(self.worktree, purpose="containment")
        self.track(handle)
        (handle.path / "scratch" / "file.txt").write_text("x", encoding="utf-8")
        outside = self.base / "outside"
        outside.mkdir()
        (outside / "target.txt").write_text("y", encoding="utf-8")
        os.symlink(outside / "target.txt", handle.path / "scratch" / "link.txt")
        cases = [
            (PurePosixPath("../escape.txt"), Path("ok.txt"), "SOURCE_PATH_INVALID"),
            (PurePosixPath("/etc/passwd"), Path("ok.txt"), "SOURCE_PATH_INVALID"),
            (PurePosixPath("scratch/link.txt"), Path("ok.txt"), "SOURCE_OPEN_FAILED"),
            (PurePosixPath("scratch"), Path("ok.txt"), "SOURCE_NOT_A_FILE"),
            (PurePosixPath("scratch/file.txt"), Path("../escape.txt"), "DESTINATION_PATH_INVALID"),
            (PurePosixPath("scratch/file.txt"), outside / "target.txt", "DESTINATION_OUTSIDE_WORKTREE"),
        ]
        for source, destination, code in cases:
            with self.subTest(source=str(source), destination=str(destination)):
                with self.assertRaises(RunError) as context:
                    promote_file(handle.handle_file, source, destination)
                self.assertEqual(context.exception.code, code)
        self.assertEqual(outside.joinpath("target.txt").read_text(encoding="utf-8"), "y")


class ReportRunsTest(LifecycleTestCase):
    def test_report_classifies_every_required_category(self) -> None:
        # live active run
        active = begin_run(self.worktree, purpose="active probe")
        self.track(active)
        # retained failed diagnostic
        failed = begin_run(self.worktree, purpose="retained failure")
        finish_run(failed.handle_file, "failed")
        # expired failed diagnostic via frozen clock
        manifest = _json.loads((failed.path / "RUN.json").read_text(encoding="utf-8"))
        finished = datetime.strptime(manifest["finished_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        # leftover succeeded run (crash between finish and cleanup)
        leftover = begin_run(self.worktree, purpose="leftover")
        environment = {**os.environ, "KOSMIC_RUNS_FAULT": "after-receipt"}
        with mock.patch.dict(os.environ, environment):
            with self.assertRaises(kosmic_runs._FaultInjected):
                finish_run(leftover.handle_file, "succeeded")
        # malformed run: bad manifest; symlinked child; unattributed names
        runs = self.worktree / ".tmp" / "kosmic" / "runs"
        malformed = runs / ("20260915T000000Z-malformed-" + "a" * 32)
        malformed.mkdir()
        (malformed / "RUN.json").write_text("{ not json", encoding="utf-8")
        foreign = runs / "not-a-run-id"
        foreign.mkdir()
        (self.worktree / ".tmp" / "kosmic" / "stranger-dir").mkdir()
        kosmic_runs._clock = lambda: finished + FAILURE_RETENTION
        report = report_runs(self.worktree, action="gc-dry-run")
        by_path = {entry.path.as_posix(): entry for entry in report.entries}
        self.assertEqual(by_path[f"runs/{active.run_id}"].category, "active")
        self.assertEqual(by_path[f"runs/{failed.run_id}"].category, "expired")
        self.assertEqual(by_path[f"runs/{leftover.run_id}"].category, "expired")
        self.assertEqual(by_path[by_path and f"runs/{malformed.name}"].category, "malformed")
        self.assertEqual(by_path["runs/not-a-run-id"].category, "unattributed")
        self.assertEqual(by_path["stranger-dir"].category, "unattributed")
        self.assertEqual(report.counts["active"], 1)
        self.assertGreater(report.selected_bytes, 0)
        payload = report_to_json(report)
        self.assertEqual(set(payload["counts"]), {"active", "retained", "expired", "abandoned", "oversized", "malformed", "unattributed"})
        self.assertIn("warn_thresholds", payload)

    def test_oversized_flag_preserves_underlying_category(self) -> None:
        handle = begin_run(self.worktree, purpose="big data")
        finish_run(handle.handle_file, "failed")
        with mock.patch.object(kosmic_runs, "PER_RUN_WARN_BYTES", 1):
            report = report_runs(self.worktree)
        entry = [e for e in report.entries if e.run_id == handle.run_id][0]
        self.assertEqual(entry.category, "oversized")
        self.assertIn("retained", entry.flags)
        self.assertIn("oversized", entry.flags)

    def test_partial_report_when_subtree_unreadable(self) -> None:
        handle = begin_run(self.worktree, purpose="locked subtree")
        finish_run(handle.handle_file, "failed")
        os.chmod(handle.path / "scratch", 0o000)
        try:
            report = report_runs(self.worktree)
            self.assertEqual(report.code, "PARTIAL")
        finally:
            os.chmod(handle.path / "scratch", 0o700)

    def test_status_single_run_and_unknown_run(self) -> None:
        handle = begin_run(self.worktree, purpose="single")
        self.track(handle)
        status = run_live_status(self.worktree, handle.run_id)
        self.assertEqual((status["code"], status["live"], status["state"]), ("OK", True, "active"))
        with self.assertRaises(RunError) as context:
            run_live_status(self.worktree, "20260915T000000Z-missing-" + "0" * 32)
        self.assertEqual(context.exception.code, "RUN_OPEN_FAILED")


    def test_report_classifies_dot_prefixed_operation_and_quarantine_entries(self) -> None:
        handle = begin_run(self.worktree, purpose="dot entries")
        self.track(handle)
        root = self.worktree / ".tmp" / "kosmic"
        (root / "operations" / ".unattributed").write_text("operator data", encoding="utf-8")
        (root / "quarantine" / ".remnant").mkdir()
        (root / "quarantine" / ".remnant" / "payload").write_text("retained", encoding="utf-8")
        (root / ".unknown-root-entry").write_text("unattributed", encoding="utf-8")

        report = report_runs(self.worktree)

        by_path = {entry.path.as_posix(): entry for entry in report.entries}
        self.assertEqual(by_path["operations/.unattributed"].category, "unattributed")
        self.assertEqual(by_path["quarantine/.remnant"].category, "retained")
        self.assertEqual(by_path[".unknown-root-entry"].category, "unattributed")
        recovery = recover_cleanup_operations(self.worktree)
        self.assertTrue(
            any(item.get("operation_id") == ".unattributed" and item.get("reason") == "UNATTRIBUTED_OPERATION_NAME" for item in recovery),
            recovery,
        )
        self.assertTrue(
            any(item.get("operation_id") == ".remnant" and item.get("reason") == "ORPHAN_QUARANTINE_CHILD" for item in recovery),
            recovery,
        )
    def test_gc_apply_removes_only_expired_valid_runs_with_durable_receipt(self) -> None:
        expired = begin_run(self.worktree, purpose="expired diagnostic")
        self.track(expired)
        receipt = finish_run(expired.handle_file, "failed")
        active = begin_run(self.worktree, purpose="active survivor")
        self.track(active)
        user_file = self.worktree / "user-work.txt"
        user_file.write_text("preserve me\n", encoding="utf-8")
        self.assertIsNotNone(receipt.expires_at)
        kosmic_runs._clock = lambda: receipt.expires_at

        dry_run = report_runs(self.worktree, action="gc-dry-run")
        self.assertTrue(any(entry.run_id == expired.run_id and "selected" in entry.flags for entry in dry_run.entries))
        applied = report_runs(self.worktree, action="gc-apply")

        self.assertFalse(expired.path.exists())
        self.assertTrue(active.path.exists())
        self.assertEqual(user_file.read_text(encoding="utf-8"), "preserve me\n")
        self.assertEqual(len(applied.operations), 1)
        self.assertEqual(applied.operations[0]["result"], "removed")
        payload = report_to_json(applied)
        self.assertEqual(payload["operations"], list(applied.operations))
        self.assertEqual(payload["remaining_eligible"], 0)
        self.assertEqual(payload["remaining_bytes"], 0)
        terminal = _json.loads(expired.handle_file.read_text(encoding="utf-8"))
        self.assertEqual((terminal["kind"], terminal["cleanup"]), ("receipt", "removed"))

    def test_competing_gc_collectors_record_one_removal(self) -> None:
        expired = begin_run(self.worktree, purpose="collector race")
        self.track(expired)
        receipt = finish_run(expired.handle_file, "failed")
        self.assertIsNotNone(receipt.expires_at)
        kosmic_runs._clock = lambda: receipt.expires_at

        with ThreadPoolExecutor(max_workers=2) as executor:
            reports = list(executor.map(lambda _: report_runs(self.worktree, action="gc-apply"), range(2)))

        self.assertFalse(expired.path.exists())
        history = [
            _json.loads(line)
            for line in (self.worktree / ".tmp" / "kosmic" / "history.jsonl").read_text(encoding="utf-8").splitlines()
        ]
        removals = [entry for entry in history if entry.get("kind") == "cleanup" and entry.get("run_id") == expired.run_id]
        self.assertEqual(len(removals), 1)
        self.assertEqual(sum(len(report.operations) for report in reports), 1)

    def test_startup_collection_is_bounded_and_converges(self) -> None:
        handles = []
        expiries = []
        for index in range(3):
            handle = begin_run(self.worktree, purpose=f"startup expired {index}")
            self.track(handle)
            receipt = finish_run(handle.handle_file, "failed")
            handles.append(handle)
            self.assertIsNotNone(receipt.expires_at)
            expiries.append(receipt.expires_at)
        kosmic_runs._clock = lambda: max(expiries)

        first = kosmic_runs.startup_collect(self.worktree, max_entries=1, max_bytes=1 << 20)

        self.assertEqual(len(first.operations), 1)
        self.assertEqual(first.remaining_eligible, 2)
        second = kosmic_runs.startup_collect(self.worktree, max_entries=1, max_bytes=1 << 20)
        third = kosmic_runs.startup_collect(self.worktree, max_entries=1, max_bytes=1 << 20)
        self.assertEqual((second.remaining_eligible, third.remaining_eligible), (1, 0))
        self.assertTrue(all(not handle.path.exists() for handle in handles))
    def test_startup_attempt_bound_applies_when_cleanup_fails(self) -> None:
        expiries = []
        for index in range(3):
            handle = begin_run(self.worktree, purpose=f"bounded failure {index}")
            self.track(handle)
            receipt = finish_run(handle.handle_file, "failed")
            self.assertIsNotNone(receipt.expires_at)
            expiries.append(receipt.expires_at)
        kosmic_runs._clock = lambda: max(expiries)

        with mock.patch.object(
            kosmic_runs,
            "_execute_cleanup_transaction",
            side_effect=kosmic_runs.RunError("REMOVAL_FAILED", "injected"),
        ) as execute:
            report = kosmic_runs.startup_collect(self.worktree, max_entries=1, max_bytes=1 << 20)

        self.assertEqual(execute.call_count, 1)
        self.assertEqual(report.remaining_eligible, 3)
        self.assertEqual(report.code, "PARTIAL")

    def test_gc_transitions_unlocked_past_grace_run_to_abandoned(self) -> None:
        handle = begin_run(self.worktree, purpose="expired lease", active_for=timedelta(hours=1))
        manifest = _json.loads((handle.path / "RUN.json").read_text(encoding="utf-8"))
        os.kill(manifest["holder_pid"], signal.SIGKILL)
        time.sleep(0.2)
        lease_expiry = datetime.strptime(manifest["lease_expires_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        kosmic_runs._clock = lambda: lease_expiry + kosmic_runs.UNLOCK_GRACE

        report = report_runs(self.worktree, action="gc-apply")

        self.assertEqual(len(report.operations), 1)
        self.assertFalse(handle.path.exists())
        receipt = _json.loads(handle.handle_file.read_text(encoding="utf-8"))
        self.assertEqual((receipt["outcome"], receipt["cleanup"]), ("abandoned", "removed"))
class StartupMaintenanceIntegrationTest(LifecycleTestCase):
    def test_maintenance_failure_does_not_hide_primary_command_result(self) -> None:
        stderr = StringIO()
        with mock.patch.object(
            kosmic_runs,
            "startup_collect",
            side_effect=kosmic_runs.RunError("MAINTENANCE_PROBE", "injected"),
        ) as collect:
            with redirect_stderr(stderr):
                with kosmic_project_skills.managed_command_run(self.worktree, purpose="primary command") as scratch:
                    artifact = scratch / "primary.txt"
                    artifact.write_text("primary succeeded\n", encoding="utf-8")
                    self.assertEqual(artifact.read_text(encoding="utf-8"), "primary succeeded\n")
        collect.assert_called_once_with(self.worktree)
        self.assertIn("MANAGED_RUN_MAINTENANCE_FAILED:MAINTENANCE_PROBE", stderr.getvalue())

    def test_startup_maintenance_reports_removed_and_remaining_work(self) -> None:
        maintenance = mock.Mock(code="OK", operations=({"result": "removed"},), diagnostics=(), remaining_eligible=2)
        stderr = StringIO()
        with mock.patch.object(kosmic_runs, "startup_collect", return_value=maintenance):
            with redirect_stderr(stderr):
                with kosmic_project_skills.managed_command_run(self.worktree, purpose="bounded command"):
                    pass
        self.assertIn("MANAGED_RUN_MAINTENANCE:OK:removed=1:remaining=2", stderr.getvalue())
class ScratchCliTest(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.worktree = committed_worktree(self.base)
        self._pids: list[int] = []

    def run_cli(self, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [sys.executable, str(CLI), *arguments],
            capture_output=True, text=True, check=False, cwd=REPO_ROOT,
        )
        self.assertEqual(expected, result.returncode, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        return result

    def track(self, payload: dict) -> None:
        run_dir = self.worktree / ".tmp" / "kosmic" / "runs" / payload["run_id"]
        manifest = _json.loads((run_dir / "RUN.json").read_text(encoding="utf-8"))
        self._pids.append(int(manifest["holder_pid"]))

    def tearDown(self) -> None:
        for pid in self._pids:
            try:
                os.kill(pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass

    def test_cli_lifecycle_spans_processes_with_json_results(self) -> None:
        begin = _json.loads(self.run_cli(
            "scratch", "begin", "--project", str(self.worktree), "--purpose", "cli run",
        ).stdout)
        self.track(begin)
        self.assertEqual(begin["code"], "OK")
        self.assertTrue(begin["handle_file"].startswith(str(self.worktree / ".tmp" / "kosmic" / "handles")))
        run_dir = self.worktree / ".tmp" / "kosmic" / "runs" / begin["run_id"]
        (run_dir / "scratch" / "artifact.txt").parent.mkdir(parents=True, exist_ok=True)
        (run_dir / "scratch" / "artifact.txt").write_text("cli artifact", encoding="utf-8")
        promote = _json.loads(self.run_cli(
            "scratch", "promote", "--project", str(self.worktree),
            "--handle-file", begin["handle_file"],
            "--source", "scratch/artifact.txt", "--destination", "from-cli.txt",
        ).stdout)
        self.assertEqual(promote["code"], "OK")
        self.assertEqual((self.worktree / "from-cli.txt").read_text(encoding="utf-8"), "cli artifact")
        status = _json.loads(self.run_cli(
            "scratch", "status", "--project", str(self.worktree), "--run", begin["run_id"],
        ).stdout)
        self.assertEqual((status["code"], status["live"], status["state"]), ("OK", True, "active"))
        succeed = _json.loads(self.run_cli(
            "scratch", "succeed", "--project", str(self.worktree), "--handle-file", begin["handle_file"],
        ).stdout)
        self.assertEqual((succeed["code"], succeed["state"]), ("OK", "succeeded"))
        self.assertFalse(run_dir.exists())
        report = _json.loads(self.run_cli("scratch", "gc", "--project", str(self.worktree), "--dry-run").stdout)
        self.assertEqual(report["code"], "OK")

    def test_cli_accepts_gc_apply_and_rejects_bad_inputs(self) -> None:
        result = self.run_cli("scratch", "gc", "--project", str(self.worktree), "--apply")
        self.assertEqual(_json.loads(result.stdout)["action"], "gc-apply")
        self.run_cli("scratch", "begin", "--project", str(self.worktree), "--purpose", "x",
                     "--retention", "weekly", expected=2)
        begin = _json.loads(self.run_cli(
            "scratch", "begin", "--project", str(self.worktree), "--purpose", "bad outcome",
        ).stdout)
        self.track(begin)
        self.run_cli("scratch", "succeed", "--project", str(self.worktree),
                     "--handle-file", begin["handle_file"] + "0", expected=2)

    def test_cli_token_absent_from_output(self) -> None:
        begin = _json.loads(self.run_cli(
            "scratch", "begin", "--project", str(self.worktree), "--purpose", "token probe",
        ).stdout)
        self.track(begin)
        handle_data = _json.loads(Path(begin["handle_file"]).read_text(encoding="utf-8"))
        token = base64.b64decode(handle_data["token"])
        outputs = self.run_cli("scratch", "status", "--project", str(self.worktree)).stdout
        outputs += self.run_cli("scratch", "gc", "--project", str(self.worktree), "--dry-run").stdout
        self.assertNotIn(token.hex(), outputs)
        self.assertNotIn(base64.b64encode(token).decode(), outputs)
        fail = self.run_cli("scratch", "fail", "--project", str(self.worktree),
                            "--handle-file", begin["handle_file"], "--detail", "boom").stdout
        self.assertNotIn(token.hex(), fail)


class AutomaticCommandIntegrationTest(unittest.TestCase):
    """Story 048: non-exempt commands run automatically through managed runs."""

    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def make_vault_project(self) -> Path:
        vault = self.root / "vault"
        project = vault / "Projects" / "demo"
        notes = project / "notes"
        notes.mkdir(parents=True)
        (notes / "index.md").write_text('---\nokf_version: "0.2"\n---\n\n# Knowledge\n', encoding="utf-8")
        (project / "ProjectEntry.md").write_text(
            "---\nproject_id: demo-proj\nworking_state: working-tree\n---\n\n# Demo\n", encoding="utf-8",
        )
        mathdocs = project / "mathdocs"
        mathdocs.mkdir()
        (mathdocs / "index.md").write_text(
            "# Math Derivations\n\n| Derivation | Status | Result summary |\n|------------|--------|----------------|\n",
            encoding="utf-8",
        )
        usage = project / "notes" / "usage-guide.md"
        usage.write_text(
            "---\ntype: Project Knowledge\ntitle: Usage Guide\nstatus: stable\naudience: usage\n"
            "artifact_role: knowledge\n---\n\n# Usage Guide\nUse the tool.\n",
            encoding="utf-8",
        )
        (vault / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q", str(vault)], check=True, capture_output=True)
        return project

    def run_cli(self, *arguments: str, expected: int = 0) -> subprocess.CompletedProcess:
        result = subprocess.run(
            [sys.executable, str(CLI), *arguments],
            capture_output=True, text=True, check=False, cwd=REPO_ROOT,
        )
        self.assertEqual(expected, result.returncode, msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}")
        return result

    def test_validate_uses_managed_run_and_leaves_no_system_temp(self) -> None:
        project = self.make_vault_project()
        self.run_cli("generate", "--project", str(project))
        result = self.run_cli("validate", "--project", str(project))
        self.assertIn("valid Skill Pair", result.stdout)
        runs = project.parents[1] / ".tmp" / "kosmic" / "runs"
        history = project.parents[1] / ".tmp" / "kosmic" / "history.jsonl"
        self.assertEqual(os.listdir(runs), [])  # disposable run finalized and cleaned
        self.assertTrue(history.exists())
        record = _json.loads(history.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(record["run_summary"]["purpose"], "validate-projection")

    def test_validate_fails_closed_outside_git_worktree(self) -> None:
        project = self.make_vault_project()
        self.run_cli("generate", "--project", str(project))
        shutil.rmtree(project.parents[1] / ".git")
        result = self.run_cli("validate", "--project", str(project), expected=2)
        self.assertIn("NO_GIT_WORKTREE", result.stderr)

    def test_provenance_uses_managed_run_index(self) -> None:
        project = self.make_vault_project()
        vault = project.parents[1]
        subprocess.run(["git", "-C", str(vault), "add", "-A"], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(vault), "-c", "user.email=t@e.com", "-c", "user.name=T", "commit", "-q", "-m", "seed"],
            check=True, capture_output=True,
        )
        result = self.run_cli("provenance", "--repo", str(vault))
        self.assertIn("git_head: ", result.stdout)
        self.assertIn("worktree_tree: clean", result.stdout)
        self.assertEqual(subprocess.run(["git", "-C", str(vault), "status", "--porcelain"],
                                        capture_output=True, text=True).stdout, "")
