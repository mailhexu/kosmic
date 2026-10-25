from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import subprocess
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

from skills.scripts import kosmic_completion, kosmic_project_skills, kosmic_work
from skills.scripts.kosmic_specs import SpecCatalog
from skills.scripts.kosmic_work import WorkdirError
from tests.test_kosmic_navigation import (
    build_two_feature_project,
    commit_all,
    receipt_for,
    write,
)


def set_reviewed_revision(record_path: Path, value: str) -> None:
    """Rewrite the embedded ``completion_review.reviewed_revision`` digest."""
    text = record_path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r'^(completion_review: .*"reviewed_revision": ")[0-9a-f]{64}(")',
        lambda match: f"{match.group(1)}{value}{match.group(2)}",
        text, count=1, flags=re.M)
    assert count == 1, "completion_review.reviewed_revision digest not found"
    record_path.write_text(updated, encoding="utf-8")


class WorkRecordTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-record-")
        self.addCleanup(self.tmp.cleanup)
        self.tree, self.root = build_two_feature_project(Path(self.tmp.name))
        epic = self.root / "subprojects/alpha/specs/epics/epic-001.md"
        epic.write_text(epic.read_text().replace('status: "done"', 'status: "approved"'))
        entry = self.root / "ProjectEntry.md"
        entry.write_text(entry.read_text().replace(
            "working_state: working-tree\n",
            f"working_state: working-tree\nstatus_root: {self.tree}\n"))
        self.identity = "nav/alpha/story/001"
        self.record = SpecCatalog(self.root).resolve(self.identity)
        self.path = self.record.path
        reviewed_revision = kosmic_completion.source_revision(
            self.tree, self.root, SpecCatalog(self.root).resolve(self.identity))
        metadata = dict(self.record.metadata)
        metadata.update(
            consumer_interface_change=False,
            review_base="fixture-base", review_round=1,
            completion_observations=[{
                "criterion": "Result file contains verified output",
                "observation": "The fixture story behavior was exercised and observed.",
                "source": "tests/test_kosmic_work_records.py"}],
            completion_review={
                "reviewer": "fixture-reviewer",
                "axes": {
                    "standards": {"reviewer": "fixture-standards-reviewer",
                                  "decision": "approved"},
                    "spec": {"reviewer": "fixture-spec-reviewer",
                             "decision": "approved"}},
                "decision": "approved", "review_base": "fixture-base",
                "reviewed_revision": reviewed_revision, "findings": [],
                "scope": ["worktree:src/",
                          "project:subprojects/alpha/specs/stories/"]})
        write(self.path, metadata, "Alpha Story One",
              "## Acceptance Criteria\n\n- [ ] Result file contains verified output\n")
        commit_all(self.tree, "2026-10-04", "fixture completion baseline")

    def refresh_review_revision(self):
        record = SpecCatalog(self.root).resolve(self.identity)
        set_reviewed_revision(
            self.path,
            kosmic_completion.source_revision(self.tree, self.root, record))

    def refresh_status(self):
        """Regenerate derived STATUS so the finish precheck sees fresh bytes.

        Every nonterminal finish attempt must observe current projections;
        an attempt that flips the record (or an injected publication failure)
        leaves the derived reports honestly stale until the next refresh.
        """
        kosmic_completion._write_status_reports(self.root, None)

    def test_clean_worktree_is_a_start_precondition(self):
        record = kosmic_work.check_work_start(self.root, self.tree, self.identity)
        self.assertEqual(record.qualified_id, self.identity)
        (self.tree / "preexisting.txt").write_text("user change\n")
        with self.assertRaises(WorkdirError) as caught:
            kosmic_work.check_work_start(self.root, self.tree, self.identity)
        self.assertEqual(caught.exception.code, "ATTRIBUTION_AMBIGUOUS")
        self.assertIn("preexisting.txt", caught.exception.detail)

    def test_record_resolution_rechecks_status(self):
        self.assertEqual(kosmic_work.resolve_work_record(self.root, self.identity).qualified_id,
                         self.identity)
        metadata = dict(self.record.metadata)
        metadata["status"] = "done"
        write(self.path, metadata, "Alpha Story One",
              "## Acceptance Criteria\n\n- [ ] Result file contains verified output\n")
        with self.assertRaises(WorkdirError) as caught:
            kosmic_work.resolve_work_record(self.root, self.identity)
        self.assertEqual(caught.exception.code, "WORK_PHASE_DENIED")

    def test_unreceipted_done_ancestor_is_not_terminal_authority(self):
        epic = self.root / "subprojects/alpha/specs/epics/epic-001.md"
        epic.write_text(epic.read_text().replace('status: "approved"', 'status: "done"'))
        ancestor = SpecCatalog(self.root).resolve("nav/alpha/epic/001")
        self.assertTrue(ancestor.receipt_pending)
        self.assertEqual(ancestor.effective_status, "pending")
        with self.assertRaises(WorkdirError) as caught:
            kosmic_work.resolve_work_record(self.root, self.identity)
        self.assertEqual(caught.exception.code, "ANCESTRY_INVALID")

    def test_finish_checks_scope_and_publishes_receipt_idempotently(self):
        source = self.tree / "src/result.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("verified output\n")
        self.refresh_review_revision()
        self.refresh_status()
        scope = ["worktree:src/", "project:subprojects/alpha/specs/stories/"]
        receipt = kosmic_completion.finish_work(self.root, self.tree, self.identity, scope)
        self.assertEqual(receipt["status"], "successful")
        done_record = SpecCatalog(self.root).resolve(self.identity)
        self.assertEqual(done_record.status, "done")
        self.assertEqual(kosmic_completion.check_terminal_receipt(self.root, done_record)["identity"],
                         self.identity)
        repeated = kosmic_completion.finish_work(self.root, self.tree, self.identity, scope)
        self.assertEqual(repeated["identity"], self.identity)

    def test_finish_owner_record_skips_unrelated_project_root_index(self):
        source = self.tree / "src/result.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("verified output\n")
        owner_specs = self.path.parent.parent
        owner_index = owner_specs / "INDEX.md"
        owner_index.write_text(
            "# Alpha Specs\n\n| Story | Status | Dependency | Scope |\n"
            "| --- | --- | --- | --- |\n"
            "| [Story](stories/story-001.md) | in_progress | done | Alpha |\n")
        project_index = self.root / "specs/INDEX.md"
        project_index.parent.mkdir(parents=True, exist_ok=True)
        project_index.write_text("# Shared specs\n\n- [Keep](quick-tasks/keep.md)\n")
        project_before = project_index.read_bytes()
        self.refresh_review_revision()
        self.refresh_status()
        scope = ["worktree:src/", "project:specs/", "project:subprojects/alpha/specs/"]

        receipt = kosmic_completion.finish_work(
            self.root, self.tree, self.identity, scope)

        self.assertEqual(receipt["status"], "successful")
        self.assertEqual(project_index.read_bytes(), project_before)
        self.assertIn("| [Story](stories/story-001.md) | done | done | Alpha |",
                      owner_index.read_text())
        self.assertEqual(
            kosmic_completion.check_terminal_receipt(
                self.root, SpecCatalog(self.root).resolve(self.identity))["identity"],
            self.identity)

    def test_unreceipted_done_remains_pending_and_finish_converges(self):
        source = self.tree / "src/result.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("verified output\n")
        self.refresh_review_revision()
        self.refresh_status()
        scope = ["worktree:src/", "project:subprojects/alpha/specs/stories/"]
        original_write = kosmic_work._atomic_write

        def fail_receipt(base, relative, payload):
            if relative.startswith(".kosmic/work-receipts/"):
                raise OSError("injected receipt publication failure")
            return original_write(base, relative, payload)

        with patch.object(kosmic_work, "_atomic_write", side_effect=fail_receipt):
            with self.assertRaisesRegex(OSError, "receipt publication"):
                kosmic_completion.finish_work(self.root, self.tree, self.identity, scope)
        pending = SpecCatalog(self.root).resolve(self.identity)
        self.assertEqual(pending.status, "done")
        self.assertTrue(pending.receipt_pending)
        self.assertEqual(pending.effective_status, "pending")
        self.refresh_status()
        completed = kosmic_completion.finish_work(self.root, self.tree, self.identity, scope)
        self.assertEqual(completed["status"], "successful")
        settled = SpecCatalog(self.root).resolve(self.identity)
        self.assertFalse(settled.receipt_pending)
        self.assertEqual(settled.effective_status, "done")

    def test_cli_finish_leaves_receipt_valid_and_status_current(self):
        cli = Path(__file__).resolve().parents[1] / "skills/scripts/kosmic_project_skills.py"
        base = [sys.executable, str(cli)]
        common = ["--project", str(self.root), "--worktree", str(self.tree),
                  "--work-record", self.identity]
        start = subprocess.run(base + ["work", "start", *common], capture_output=True, text=True)
        self.assertEqual(start.returncode, 0, start.stderr)
        source = self.tree / "src/result.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("verified output\n")
        self.refresh_review_revision()
        self.refresh_status()
        finish = subprocess.run(base + ["work", "finish", *common,
                                        "--scope", "worktree:src/",
                                        "--scope", "project:subprojects/alpha/specs/stories/"],
                               capture_output=True, text=True)
        self.assertEqual(finish.returncode, 0, finish.stderr)
        receipt = kosmic_completion.check_terminal_receipt(
            self.root, SpecCatalog(self.root).resolve(self.identity))
        self.assertEqual(receipt["status"], "successful")
        self.assertFalse(kosmic_project_skills.status_drift(
            kosmic_project_skills.load_project(self.root)))
        rows = [line for line in (self.tree / "STATUS.md").read_text().splitlines()
                if "Alpha Story One" in line]
        self.assertTrue(rows)
        for row in rows:
            self.assertIn("| done |", row)
            self.assertNotIn("(receipt pending)", row)

    def test_interrupted_status_publication_recovers_without_receipt_rewrite(self):
        source = self.tree / "src/result.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("verified output\n")
        registered = Path(self.tmp.name) / "registered-reports"
        registered.mkdir()
        (registered / "STATUS.md").write_text("stale registered projection\n")
        directory = str(registered)
        registry = {
            "schema": "kosmic.workdirs/1", "project_id": "nav", "sequence": 1,
            "directories": [{
                "schema": "kosmic.workdir/1", "path": directory,
                "directory_id": "wd-" + hashlib.sha256(directory.encode()).hexdigest()[:16],
                "fixed_subproject_id": None,
                "authority": {"record": "nav/quick-task/2026-10-01-shared-task",
                              "run_id": "fixture-run"},
            }],
        }
        registry_path = self.root / ".kosmic/working-directories.json"
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(json.dumps(registry))
        bound_status = self.tree / "STATUS.md"
        bound_status.write_text("stale bound projection\n")
        commit_all(self.tree, "2026-10-05", "stale status projections")
        self.refresh_review_revision()
        self.refresh_status()
        scope = ["worktree:src/", "project:subprojects/alpha/specs/stories/"]
        original_write = kosmic_work._atomic_write

        def fail_status(base, relative, payload):
            if relative == "STATUS.md":
                raise OSError("injected STATUS publication failure")
            return original_write(base, relative, payload)

        with patch.object(kosmic_work, "_atomic_write", side_effect=fail_status):
            with self.assertRaisesRegex(OSError, "STATUS publication"):
                kosmic_completion.finish_work(self.root, self.tree, self.identity, scope)
        interrupted = SpecCatalog(self.root).resolve(self.identity)
        self.assertEqual(interrupted.status, "done")
        receipt = kosmic_completion.check_terminal_receipt(self.root, interrupted)
        self.assertEqual(receipt["status"], "successful")
        receipt_path = self.root / ".kosmic/work-receipts" / receipt_for(self.identity)
        receipt_bytes = receipt_path.read_bytes()
        logs = sorted(self.root.glob("log/*-work-completion.md"))
        self.assertEqual(len(logs), 1)
        log_bytes = logs[0].read_bytes()
        repaired = kosmic_completion.finish_work(self.root, self.tree, self.identity, scope)
        self.assertEqual(repaired["identity"], self.identity)
        self.assertEqual(receipt_path.read_bytes(), receipt_bytes)
        self.assertEqual(logs[0].read_bytes(), log_bytes)
        self.assertEqual(log_bytes.decode().count(f"- `{self.identity}` — "), 1)
        self.assertFalse(kosmic_project_skills.status_drift(
            kosmic_project_skills.load_project(self.root)))
        rows = [line for line in bound_status.read_text().splitlines()
                if "Alpha Story One" in line]
        self.assertTrue(rows, str(bound_status))
        for row in rows:
            self.assertIn("| done |", row)
            self.assertNotIn("(receipt pending)", row)
        self.assertEqual((registered / "STATUS.md").read_text(),
                         "stale registered projection\n")
    def test_stale_embedded_reviewed_revision_denies_completion(self):
        source = self.tree / "src/result.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("verified output\n")
        self.refresh_review_revision()
        set_reviewed_revision(self.path, "0" * 64)
        with self.assertRaises(WorkdirError) as caught:
            kosmic_completion.finish_work(
                self.root, self.tree, self.identity,
                ["worktree:src/", "project:subprojects/alpha/specs/stories/"])
        self.assertEqual(caught.exception.code, "REVIEW_INVALID")
        self.assertNotIn("status: done", self.path.read_text())

    def test_out_of_scope_diff_is_not_completed(self):
        (self.tree / "outside.txt").write_text("outside\n")
        self.refresh_review_revision()
        with self.assertRaises(WorkdirError) as caught:
            kosmic_completion.finish_work(self.root, self.tree, self.identity, ["worktree:src/"])
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        self.assertNotIn("status: done", self.path.read_text())

    def test_legacy_sidecar_receipts_stay_terminal_without_repin(self):
        # Explicitly synthetic pre-cutover fixture: a sidecar-era record whose
        # receipt predates the embedded-completion contract.
        identity = "nav/quick-task/legacy-task"
        record_path = self.root / "specs/quick-tasks/legacy-task.md"
        metadata = {"project_id": "nav", "subproject_id": None, "status": "done",
                    "record_kind": "quick-task", "local_id": "legacy-task",
                    "acceptance_evidence": ["evidence/legacy-acceptance.json"],
                    "review_record": "evidence/legacy-review.json",
                    "review_base": "fixture-base", "review_round": 1}
        write(record_path, metadata, "Legacy Task",
              "## Acceptance Criteria\n\n- [ ] Legacy output is observed\n")
        canonical = record_path.relative_to(self.root).as_posix()
        artifact = self.root / "evidence/legacy-result.txt"
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text("legacy output\n")
        observed = self.root / "notes/legacy-observed.md"
        observed.parent.mkdir(parents=True, exist_ok=True)
        observed.write_text("Legacy observation recorded at receipt time.\n")
        acceptance = {
            "schema": "kosmic.acceptance-evidence/1", "identity": identity,
            "record_path": canonical,
            "results": [{"criterion": "Legacy output is observed", "outcome": "passed",
                         "observation": "Read the legacy output bytes.",
                         "artifacts": [{"path": "evidence/legacy-result.txt",
                                        "sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()},
                                       {"path": "notes/legacy-observed.md",
                                        "sha256": hashlib.sha256(observed.read_bytes()).hexdigest()}]}],
        }
        (self.root / "evidence/legacy-acceptance.json").write_text(json.dumps(acceptance))
        review = {
            "schema": "kosmic.work-review/1", "identity": identity,
            "record_path": canonical, "review_base": "fixture-base", "round": 1,
            "standards": {"decision": "approved", "reviewer": "fixture-standards-reviewer"},
            "spec": {"decision": "approved", "reviewer": "fixture-spec-reviewer"},
            "findings": [], "decision": "approved", "reviewed_revision": "0" * 64,
        }
        review_bytes = (self.root / "evidence/legacy-review.json")
        review_bytes.write_text(json.dumps(review))
        record_sha256 = hashlib.sha256(record_path.read_bytes()).hexdigest()
        receipt = {
            "schema": "kosmic.work-receipt/1", "identity": identity,
            "status": "successful", "record_path": canonical,
            "record_sha256": record_sha256,
            "proof": {
                "evidence/legacy-acceptance.json":
                    hashlib.sha256((self.root / "evidence/legacy-acceptance.json")
                                   .read_bytes()).hexdigest(),
                "evidence/legacy-review.json":
                    hashlib.sha256(review_bytes.read_bytes()).hexdigest(),
                "evidence/legacy-result.txt":
                    hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "notes/legacy-observed.md":
                    hashlib.sha256(observed.read_bytes()).hexdigest()},
            "completed_at": "2026-10-18T00:00:00Z", "detail": "legacy fixture",
        }
        receipt_path = (self.root / ".kosmic/work-receipts" / receipt_for(identity))
        receipt_path.parent.mkdir(parents=True, exist_ok=True)
        receipt_payload = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
        receipt_path.write_bytes(receipt_payload)

        # (a) intact legacy originals: the receipt still validates terminally.
        record = SpecCatalog(self.root).resolve(identity)
        validated = kosmic_completion.check_terminal_receipt(self.root, record)
        self.assertEqual(validated["identity"], identity)

        # (b) a missing historical original surfaces as explicit pending.
        review_backup = review_bytes.read_bytes()
        review_bytes.unlink()
        with self.assertRaises(WorkdirError) as caught:
            kosmic_completion.check_terminal_receipt(self.root, record)
        self.assertEqual(caught.exception.code, "COMPLETION_PENDING")
        self.assertIn("historical receipt original missing: evidence/legacy-review.json",
                      caught.exception.detail)
        with self.assertRaises(WorkdirError) as caught:
            kosmic_completion.check_completion_gates(self.root, identity, self.tree)
        self.assertEqual(caught.exception.code, "COMPLETION_PENDING")
        review_bytes.write_bytes(review_backup)

        # (c) a changed historical original surfaces as drift.
        acceptance_path = self.root / "evidence/legacy-acceptance.json"
        acceptance_backup = acceptance_path.read_bytes()
        acceptance_path.write_bytes(acceptance_backup.replace(b"passed", b"Passed"))
        with self.assertRaises(WorkdirError) as caught:
            kosmic_completion.check_terminal_receipt(self.root, record)
        self.assertEqual(caught.exception.code, "COMPLETION_DRIFT")
        self.assertIn("historical receipt original changed: evidence/legacy-acceptance.json",
                      caught.exception.detail)
        acceptance_path.write_bytes(acceptance_backup)

        # (f) recorded artifact digests are historical facts: raw notes and
        # data files are never opened or re-hashed after the receipt.
        observed.write_text("The observation was later merged and rewritten.\n")
        artifact.write_text("evolved output bytes\n")
        validated = kosmic_completion.check_terminal_receipt(self.root, record)
        self.assertEqual(validated["identity"], identity)
        observed.unlink()
        artifact.unlink()
        validated = kosmic_completion.check_terminal_receipt(self.root, record)
        self.assertEqual(validated["identity"], identity)

        # (g) an empty proof map cannot complete a legacy record.
        empty_payload = (json.dumps({**receipt, "proof": {}},
                                    sort_keys=True, indent=2) + "\n").encode()
        receipt_path.write_bytes(empty_payload)
        with self.assertRaises(WorkdirError) as caught:
            kosmic_completion.check_terminal_receipt(self.root, record)
        self.assertEqual(caught.exception.code, "COMPLETION_PENDING")
        self.assertIn("legacy receipt proof missing recorded original",
                      caught.exception.detail)
        receipt_path.write_bytes(receipt_payload)

        # (d) rerunning finish on the drifted legacy receipt never repins it.
        acceptance_path.write_bytes(acceptance_backup.replace(b"passed", b"Passed"))
        with self.assertRaises(WorkdirError) as caught:
            kosmic_completion.finish_work(
                self.root, self.tree, identity,
                ["worktree:src/", "project:evidence/", "project:specs/"])
        self.assertEqual(caught.exception.code, "COMPLETION_DRIFT")
        self.assertEqual(receipt_path.read_bytes(), receipt_payload)
        acceptance_path.write_bytes(acceptance_backup)

        # (e) editing the legacy record after its receipt breaks the binding.
        record_path.write_text(record_path.read_text() + "\nPost-receipt refinement.\n")
        with self.assertRaises(WorkdirError) as caught:
            kosmic_completion.check_terminal_receipt(
                self.root, SpecCatalog(self.root).resolve(identity))
        self.assertEqual(caught.exception.code, "COMPLETION_PENDING")
        self.assertIn("no matching successful receipt", caught.exception.detail)

    def test_finish_retry_converges_when_project_is_worktree_root(self):
        root = Path(self.tmp.name) / "equal-root"
        root.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.email", "t@example.com"], check=True)
        subprocess.run(["git", "-C", str(root), "config", "user.name", "t"], check=True)
        (root / ".gitignore").write_text(".tmp/\n")
        write(root / "ProjectEntry.md", {"project_id": "equal", "status_root": str(root)}, "Equal")
        identity = "equal/quick-task/task"
        record_path = root / "specs/quick-tasks/task.md"
        metadata = {"project_id": "equal", "subproject_id": None, "status": "approved",
                    "record_kind": "quick-task", "local_id": "task",
                    "consumer_interface_change": False,
                    "review_base": "base", "review_round": 1,
                    "completion_observations": [{
                        "criterion": "Source output is observed",
                        "observation": "The source output bytes were read and observed.",
                        "source": "tests/test_kosmic_work_records.py"}],
                    "completion_review": {
                        "reviewer": "fixture-reviewer",
                        "axes": {
                            "standards": {"reviewer": "fixture-standards-reviewer",
                                          "decision": "approved"},
                            "spec": {"reviewer": "fixture-spec-reviewer",
                                     "decision": "approved"}},
                        "decision": "approved", "review_base": "base",
                        "reviewed_revision": "0" * 64, "findings": [],
                        "scope": ["worktree:src/", "project:specs/"]}}
        write(record_path, metadata, "Task",
              "## Acceptance Criteria\n\n- [ ] Source output is observed\n")
        write(root / "specs/stories/story-legacy.md", {"status": "approved"}, "Legacy feature")
        commit_all(root, "2026-10-04", "equal-root fixture")
        record = kosmic_work.resolve_work_record(root, identity)
        kosmic_work.check_work_start(root, root, identity)
        (root / "src/result.txt").parent.mkdir(parents=True)
        (root / "src/result.txt").write_text("source output\n")
        set_reviewed_revision(
            record_path, kosmic_completion.source_revision(root, root, record))
        kosmic_completion._write_status_reports(root, None)
        scope = ["worktree:src/", "project:specs/"]
        original_write = kosmic_work._atomic_write

        def fail_receipt(base, relative, payload):
            if relative.startswith(".kosmic/work-receipts/"):
                raise OSError("injected receipt publication failure")
            return original_write(base, relative, payload)

        with patch.object(kosmic_work, "_atomic_write", side_effect=fail_receipt):
            with self.assertRaisesRegex(OSError, "receipt publication"):
                kosmic_completion.finish_work(root, root, identity, scope)
        self.assertEqual(kosmic_work.resolve_work_record(root, identity, allow_terminal=True).status, "done")
        kosmic_completion._write_status_reports(root, None)
        cli = Path(__file__).resolve().parents[1] / "skills/scripts/kosmic_project_skills.py"
        result = subprocess.run(
            [sys.executable, str(cli), "work", "finish", "--project", str(root),
             "--worktree", str(root), "--work-record", identity,
             "--scope", "worktree:src/", "--scope", "project:specs/"],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = kosmic_work.resolve_work_record(root, identity, allow_terminal=True)
        receipt = kosmic_completion.check_terminal_receipt(root, record)
        self.assertEqual(receipt["status"], "successful")

    def test_cli_start_finish_and_show_publish_terminal_receipt(self):
        cli = Path(__file__).resolve().parents[1] / "skills/scripts/kosmic_project_skills.py"
        base = [sys.executable, str(cli)]
        common = ["--project", str(self.root), "--worktree", str(self.tree),
                  "--work-record", self.identity]
        start = subprocess.run(base + ["work", "start", *common], capture_output=True, text=True)
        self.assertEqual(start.returncode, 0, start.stderr)
        source = self.tree / "src/result.txt"
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text("verified output\n")
        self.refresh_review_revision()
        self.refresh_status()
        finish = subprocess.run(base + ["work", "finish", *common,
                                        "--scope", "worktree:src/",
                                        "--scope", "project:subprojects/alpha/specs/stories/"],
                               capture_output=True, text=True)
        self.assertEqual(finish.returncode, 0, finish.stderr)
        shown = subprocess.run(base + ["work", "show", "--project", str(self.root),
                                       "--work-record", self.identity],
                               capture_output=True, text=True)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(json.loads(shown.stdout)["status"], "done")
        self.assertEqual(kosmic_completion.check_terminal_receipt(
            self.root, SpecCatalog(self.root).resolve(self.identity))["status"], "successful")
    def test_cli_work_accepts_relative_project_and_reports_git_errors(self):
        cli = Path(__file__).resolve().parents[1] / "skills/scripts/kosmic_project_skills.py"
        base = [sys.executable, str(cli)]
        common = ["--project", ".", "--worktree", str(self.tree),
                  "--work-record", self.identity]
        start = subprocess.run(base + ["work", "start", *common], cwd=self.root,
                               capture_output=True, text=True)
        self.assertEqual(start.returncode, 0, start.stderr)
        shown = subprocess.run(base + ["work", "show", "--project", ".",
                                       "--work-record", self.identity], cwd=self.root,
                               capture_output=True, text=True)
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(json.loads(shown.stdout)["identity"], self.identity)
        invalid_tree = Path(self.tmp.name) / "not-a-git-worktree"
        invalid_tree.mkdir()
        failed = subprocess.run(base + ["work", "start", "--project", str(self.root),
                                        "--worktree", str(invalid_tree),
                                        "--work-record", self.identity],
                                capture_output=True, text=True,
                                env={**os.environ,
                                     "GIT_CEILING_DIRECTORIES": str(invalid_tree.parent)})
        self.assertEqual(failed.returncode, 2)
        self.assertIn("WORKTREE_INVALID", failed.stderr)
        self.assertNotIn("Traceback", failed.stderr)

    def test_mutating_cli_requires_work_record_before_output(self):
        destination = self.tree / "STATUS.md"
        cli = Path(__file__).resolve().parents[1] / "skills/scripts/kosmic_project_skills.py"
        result = subprocess.run(
            [sys.executable, str(cli), "generate-status", "--project", str(self.root)],
            text=True, capture_output=True, env={**__import__("os").environ,
                                                 "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertEqual(result.returncode, 2)
        self.assertIn("WORK_RECORD_REQUIRED", result.stderr)
        self.assertFalse(destination.exists())
if __name__ == "__main__":
    unittest.main()
