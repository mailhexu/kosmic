"""Story 005 runtime retirement regressions (consumer-visible behavior only).

Post-cutover contract:
- retired pack/ledger inputs are rejected as unsupported for new
  declarations; historical ``done`` readers keep validating;
- ``validate``/``generate`` carry no pack-inventory, MANIFEST, stable-note
  evidence-path, or ``impact.md`` duties; ``generate`` publishes no ledger;
- dreams reflection payload carries no pack/ledger surfaces.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from tests.scoped_completion_support import (
        ScopedProjectCase,
        commit_baseline,
    )
except ImportError:  # direct test-directory execution
    from scoped_completion_support import (
        ScopedProjectCase,
        commit_baseline,
    )

from skills.scripts import kosmic_completion, kosmic_dreams, kosmic_work
from skills.scripts.kosmic_project_skills import proposal_fingerprint

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "scripts" / "kosmic_project_skills.py"

USAGE_BODY = "# Use Demo\n\nRun `demo`.\n"
DEVELOPMENT_BODY = "# Develop Demo\n\nRun contributor checks.\n"


def run_git(worktree: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=str(worktree), capture_output=True, text=True, check=True
    )
    return completed.stdout


def commit_all(worktree: Path, date: str, message: str) -> str:
    stamp = f"{date}T12:00:00"
    env = {
        **os.environ,
        "GIT_AUTHOR_DATE": stamp,
        "GIT_COMMITTER_DATE": stamp,
        "GIT_AUTHOR_NAME": "fixture",
        "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
        "GIT_COMMITTER_NAME": "fixture",
        "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
    }
    subprocess.run(["git", "add", "-A"], cwd=str(worktree), check=True,
                   capture_output=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=str(worktree),
                   check=True, capture_output=True, env=env)
    return run_git(worktree, "rev-parse", "HEAD").strip()


class PackRetirementTest(ScopedProjectCase):
    """Retired pack/ledger inputs fail typed-unsupported; done readers survive."""

    def make_pack(self, slug: str = "2026-09-02-demo") -> Path:
        pack = self.project / "evidence" / slug
        pack.mkdir(parents=True, exist_ok=True)
        (pack / "findings.md").write_text("# findings\n\npack payload\n",
                                          encoding="utf-8")
        (pack / "MANIFEST.md").write_text(
            "---\nkind: execution\nproduced_by: story-001\ndate: 2026-09-02\n"
            'summary: "Demo pack"\n---\n\n# Manifest\n\n- findings.md: role\n',
            encoding="utf-8",
        )
        return pack

    def make_proposal(
        self,
        *,
        done: bool = False,
        declare_packs: bool = False,
    ) -> Path:
        inputs = self.project / "specs" / "skill-proposals" / "inputs" / "demo.md"
        inputs.parent.mkdir(parents=True, exist_ok=True)
        source = self.project / "notes" / "index.md"
        digest = hashlib.sha256(source.read_bytes()).hexdigest()
        inputs.write_text(f"- notes/index.md: {digest}\n", encoding="utf-8")
        self.make_pack()
        body = (
            "# Skill Proposal: Demo\n\n"
            "## Problem\n\nRepeated diagnostic work.\n\n"
            "## Evidence\n\nObserved in maintained knowledge.\n\n"
            "## Proposed Change\n\nCreate one repeatable diagnostic procedure.\n\n"
            "## Applicability\n\nProject-local procedure.\n\n"
            "## Behavioral Validation\n\nPending approval.\n\n"
            "Candidate paths: [.scratch/candidate-skill]\n\n"
            "## Risks\n\nPossible overfitting.\n\n"
            "## New Evidence\n\nNone.\n"
        )
        fingerprint = proposal_fingerprint(
            "create", "project-procedure", "demo-skill", "procedure",
            ["notes/index.md"], ("2026-09-02-demo",) if declare_packs else (),
            body,
        )
        proposal = inputs.parent.parent / "2026-09-06-demo.md"
        proposal.write_text(
            "---\n"
            f"status: {'done' if done else 'draft'}\n"
            "created: 2026-09-06\nupdated: 2026-09-06\n"
            "result: create\nscope: project-procedure\nartifact_role: procedure\n"
            "target: demo-skill\ntarget_ref: skill://demo-skill\ntarget_sha256: empty\n"
            "proposer_mode: same-agent\nproposer_ref: agent://test\n"
            'proposer_reason: "Project-local test fixture"\n'
            "input_manifest: [specs/skill-proposals/inputs/demo.md]\n"
            "related_notes: [notes/index.md]\n"
            + ("evidence_packs: [2026-09-02-demo]\n" if declare_packs else "")
            + "behavioral_evidence: [evidence/2026-09-02-demo/findings.md]\n"
            f"decision: {'accepted' if done else 'pending'}\n"
            f"fingerprint: {fingerprint}\n"
            'reconsiders: ""\n'
            "---\n\n" + body + "\n",
            encoding="utf-8",
        )
        return proposal

    def publish_pair(self) -> None:
        self.note("using.md", USAGE_BODY)
        self.note("developing.md", DEVELOPMENT_BODY)
        result = self.run_cli(
            "generate", "--project", self.project,
            "--work-record", "scope-demo/quick-task/fixture-task",
        )
        assert result.returncode == 0, result.stderr

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CLI), *map(str, arguments)],
            cwd=self.root, text=True, capture_output=True,
        )

    def test_draft_proposal_omitting_evidence_packs_field_validates(self) -> None:
        self.publish_pair()
        self.make_proposal()
        result = self.run_cli("validate", "--project", self.project)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_done_proposal_input_pins_survive_source_evolution(self) -> None:
        """Story 005 defect regression: a completed proposal's recorded input
        pins are historical facts. When a canonical source note legitimately
        evolves after pinning, live re-hashing must not revoke the done
        proposal; nothing is repinned and the draft duty still binds live."""
        self.publish_pair()
        self.make_proposal(done=True)
        audited = self.run_cli("validate", "--project", self.project)
        self.assertEqual(0, audited.returncode, audited.stderr)
        # The declared source legitimately evolves after pinning (Story 005:
        # knowledge refinement by the canonical source owner).
        note = self.project / "notes" / "index.md"
        note.write_text(
            "---\nokf_version: \"0.2\"\n---\n\n# Project Knowledge\n\nEvolved.\n",
            encoding="utf-8",
        )
        evolved = self.run_cli("validate", "--project", self.project)
        self.assertEqual(0, evolved.returncode, evolved.stderr)

    def test_done_proposal_snapshot_pins_stay_verifiable(self) -> None:
        """Immutable capture validity: a done proposal's non-note pins
        (snapshot/evidence/subproject artifacts) must STILL match — evolution
        amnesty applies only to evolving canonical surfaces, not to captures."""
        self.publish_pair()
        self.make_proposal(done=True)
        note_path = self.project / "notes" / "index.md"
        stable = self.project / "specs" / "INDEX.md"
        index_bytes = note_path.read_bytes()
        digest = hashlib.sha256(stable.read_bytes()).hexdigest()
        inputs = self.project / "specs" / "skill-proposals" / "inputs" / "demo.md"
        inputs.write_text(
            f"- notes/index.md: {hashlib.sha256(index_bytes).hexdigest()}\n"
            f"- specs/INDEX.md: {digest}\n",
            encoding="utf-8",
        )
        audited = self.run_cli("validate", "--project", self.project)
        self.assertEqual(0, audited.returncode, audited.stderr)
        inputs.write_text(
            f"- notes/index.md: {hashlib.sha256(index_bytes).hexdigest()}\n"
            f"- specs/INDEX.md: {'0' * 64}\n",
            encoding="utf-8",
        )
        tampered = self.run_cli("validate", "--project", self.project)
        self.assertEqual(2, tampered.returncode, tampered.stdout)
        self.assertIn("specs/INDEX.md", tampered.stderr)

    def test_draft_proposal_input_pin_binds_live_source(self) -> None:
        """Current-proposal freshness: an unfinished draft's input pin still
        binds the live declared source; evolution without re-authoring stays
        a typed stale rejection (no blanket amnesty on mutable records)."""
        self.publish_pair()
        self.make_proposal()
        note = self.project / "notes" / "index.md"
        stale_hash = "e" * 64
        inputs = self.project / "specs" / "skill-proposals" / "inputs" / "demo.md"
        inputs.write_text(f"- notes/index.md: {stale_hash}\n", encoding="utf-8")
        stale = self.run_cli("validate", "--project", self.project)
        self.assertEqual(2, stale.returncode, stale.stdout)
        self.assertIn("notes/index.md", stale.stderr)
        self.assertIn("stale", stale.stderr)

    def test_draft_proposal_evidence_packs_declaration_is_unsupported(self) -> None:
        self.publish_pair()
        self.make_proposal(declare_packs=True)
        result = self.run_cli("validate", "--project", self.project)
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("evidence_packs", result.stderr)
        self.assertIn("unsupported", result.stderr)

    def test_done_proposal_legacy_evidence_packs_reader_survives(self) -> None:
        self.publish_pair()
        self.make_proposal(done=True)
        result = self.run_cli("validate", "--project", self.project)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_validate_tolerates_legacy_ledger_and_pack_dirs(self) -> None:
        self.publish_pair()
        (self.project / "impact.md").write_text(
            "# Impact Ledger\n\n"
            "- date: 2026-09-02 | kind: publication | targets: [notes/index.md]"
            ' | refs: "null->abc" | outcome: published | reason: ""\n'
            "- this line was never a valid ledger entry\n",
            encoding="utf-8",
        )
        bad = self.project / "evidence" / "not-a-dated-slug"
        bad.mkdir(parents=True)
        (bad / "loose.md").write_text("# loose file in an invalid pack\n",
                                      encoding="utf-8")
        result = self.run_cli("validate", "--project", self.project)
        self.assertEqual(0, result.returncode, result.stderr)

    def test_generate_publishes_no_impact_ledger(self) -> None:
        self.note("using.md", USAGE_BODY)
        self.note("developing.md", DEVELOPMENT_BODY)
        result = self.run_cli(
            "generate", "--project", self.project,
            "--work-record", "scope-demo/quick-task/fixture-task",
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertFalse((self.project / "impact.md").exists())

    def test_stable_note_evidence_metadata_is_ungated(self) -> None:
        self.note(
            "ghost.md",
            "# Ghost\n\nBody.\n",
            "evidence: [evidence/2026-09-02-demo/MANIFEST.md]\n",
        )
        generated = self.run_cli(
            "generate", "--project", self.project,
            "--work-record", "scope-demo/quick-task/fixture-task",
        )
        self.assertEqual(0, generated.returncode, generated.stderr)
        audited = self.run_cli("validate", "--project", self.project)
        self.assertEqual(0, audited.returncode, audited.stderr)

    def test_check_completion_rejects_new_evidence_packs_declaration(self) -> None:
        item = self.item(
            "consumer_interface_change: false\nevidence_packs: [2026-09-02-demo]\n"
        )
        result = self.run_cli(
            "check-completion", "--project", self.project, "--work-item", item
        )
        self.assertEqual(2, result.returncode, result.stdout)
        self.assertIn("evidence_packs", result.stderr)
        self.assertIn("unsupported", result.stderr)

    def test_legacy_done_record_with_sidecars_stays_complete(self) -> None:
        """Synthetic pre-cutover fixture: a sidecar-era record finished before
        the retirement gate existed. Its receipt, recorded originals, and the
        retired ``evidence_packs`` frontmatter stay valid as produced; the
        terminal reader and the receipt-first finish bypass the new gate."""
        identity = "scope-demo/quick-task/change"
        canonical = "specs/quick-tasks/change.md"
        record_path = self.project / canonical
        record_text = (
            "---\n"
            "project_id: scope-demo\n"
            "subproject_id: null\n"
            "record_kind: quick-task\n"
            "local_id: change\n"
            "status: done\n"
            "acceptance_evidence: [evidence/change-acceptance.json]\n"
            "review_record: evidence/change-review.json\n"
            "evidence_packs: [2026-09-02-demo]\n"
            "---\n\n"
            "# Change\n\n## Acceptance Criteria\n\n- [x] Fixture behavior observed\n"
        )
        record_path.write_text(record_text, encoding="utf-8")
        self.make_pack()
        result_bytes = b"observed fixture output\n"
        (self.project / "evidence/result.txt").write_bytes(result_bytes)
        acceptance = {
            "schema": "kosmic.acceptance-evidence/1",
            "identity": identity,
            "record_path": canonical,
            "results": [{
                "criterion": "Fixture behavior observed",
                "outcome": "passed",
                "observation": "Read the observed output bytes.",
                "artifacts": [{"path": "evidence/result.txt",
                               "sha256": hashlib.sha256(result_bytes).hexdigest()}],
            }],
        }
        review = {
            "schema": "kosmic.work-review/1",
            "identity": identity,
            "record_path": canonical,
        }
        acceptance_path = self.project / "evidence/change-acceptance.json"
        review_path = self.project / "evidence/change-review.json"
        acceptance_bytes = (json.dumps(acceptance, sort_keys=True, indent=2) + "\n").encode()
        review_bytes = (json.dumps(review, sort_keys=True, indent=2) + "\n").encode()
        acceptance_path.write_bytes(acceptance_bytes)
        review_path.write_bytes(review_bytes)
        receipt = {
            "schema": "kosmic.work-receipt/1",
            "identity": identity,
            "status": "successful",
            "record_path": canonical,
            "record_sha256": hashlib.sha256(record_text.encode()).hexdigest(),
            "proof": {
                "evidence/change-acceptance.json": hashlib.sha256(acceptance_bytes).hexdigest(),
                "evidence/change-review.json": hashlib.sha256(review_bytes).hexdigest(),
                "evidence/result.txt": hashlib.sha256(result_bytes).hexdigest(),
            },
            "completed_at": "2026-09-02T00:00:00Z",
            "detail": "pre-cutover sidecar completion",
        }
        receipts = self.project / ".kosmic/work-receipts"
        receipts.mkdir(parents=True)
        receipt_path = receipts / kosmic_dreams.receipt_name(identity)
        receipt_bytes = (json.dumps(receipt, sort_keys=True, indent=2) + "\n").encode()
        receipt_path.write_bytes(receipt_bytes)

        # Setup control only: real HEAD + official registration under a
        # separate synthetic approved bootstrap Quick Task (never the terminal
        # legacy record as registration authority). Completed-record and
        # receipt bytes stay frozen from the commit onward.
        (self.root / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        bootstrap = self.project / "specs" / "quick-tasks" / "bootstrap-register.md"
        bootstrap.write_text(
            "---\n"
            "project_id: scope-demo\n"
            "subproject_id: null\n"
            "record_kind: quick-task\n"
            "local_id: bootstrap-register\n"
            "status: approved\n"
            f"registration_root: {self.root}\n"
            'registration_outputs: [".kosmic/working-directories.json",'
            ' "worktree:.kosmic/workdir.json"]\n'
            "---\n\n"
            "# Bootstrap Register\n\n## Acceptance Criteria\n\n- [ ] Worktree registered\n",
            encoding="utf-8",
        )
        commit_baseline(self.root, "baseline")
        registered = self.run_cli(
            "workdir-register", "--project", self.project, "--worktree", self.root,
            "--quick-task", "scope-demo/quick-task/bootstrap-register",
        )
        self.assertEqual(0, registered.returncode, registered.stderr)

        audited = self.run_cli(
            "check-completion", "--project", self.project, "--work-item", record_path,
        )
        self.assertEqual(0, audited.returncode, audited.stderr)
        finished = self.run_cli(
            "work", "finish", "--project", self.project, "--worktree", self.root,
            "--work-record", identity, "--scope", "worktree:Projects/demo/specs/",
        )
        self.assertEqual(0, finished.returncode, finished.stderr)
        self.assertEqual(receipt_path.read_bytes(), receipt_bytes)

    def _embedded_completion_record(self, name: str, extra: str) -> Path:
        record_path = self.project / "specs" / "quick-tasks" / name
        record_path.write_text(
            "---\n"
            "project_id: scope-demo\n"
            "subproject_id: null\n"
            "record_kind: quick-task\n"
            "local_id: " + name.replace(".md", "") + "\n"
            "status: approved\n"
            "review_base: fixture-base\n"
            "completion_observations: "
            '[{"criterion": "Fixture behavior observed", '
            '"observation": "Observed the fixture output bytes.", '
            '"source": "fixture"}]\n'
            "completion_review: "
            '{"reviewer": "fixture-reviewer", '
            '"axes": {"standards": {"decision": "approved", "reviewer": "std"}, '
            '"spec": {"decision": "approved", "reviewer": "spec"}}, '
            '"decision": "approved", "review_base": "fixture-base", '
            '"reviewed_revision": "' + "0" * 64 + '", "findings": [], '
            '"scope": ["worktree:Projects/demo/specs/"]}\n'
            + extra +
            "---\n\n"
            "# Change\n\n## Acceptance Criteria\n\n- [ ] Fixture behavior observed\n",
            encoding="utf-8",
        )
        return record_path

    def test_finish_rejects_new_evidence_packs_declaration(self) -> None:
        record_path = self._embedded_completion_record(
            "pack-decl.md", "evidence_packs: [2026-09-02-demo]\n")
        refused = self.run_cli(
            "work", "finish", "--project", self.project, "--worktree", self.root,
            "--work-record", "scope-demo/quick-task/pack-decl",
            "--scope", "worktree:Projects/demo/specs/",
        )
        self.assertEqual(2, refused.returncode, refused.stdout)
        self.assertIn("evidence_packs", refused.stderr)
        self.assertIn("unsupported", refused.stderr)
        self.assertNotIn("status: done", record_path.read_text(encoding="utf-8"))

    def test_finish_rejects_sidecar_input_declarations(self) -> None:
        record_path = self._embedded_completion_record(
            "sidecar-decl.md",
            "acceptance_evidence: [evidence/story-acceptance.json]\n"
            "review_record: evidence/story-review.json\n")
        refused = self.run_cli(
            "work", "finish", "--project", self.project, "--worktree", self.root,
            "--work-record", "scope-demo/quick-task/sidecar-decl",
            "--scope", "worktree:Projects/demo/specs/",
        )
        self.assertEqual(2, refused.returncode, refused.stdout)
        self.assertIn("acceptance_evidence", refused.stderr)
        self.assertIn("unsupported", refused.stderr)
        self.assertNotIn("status: done", record_path.read_text(encoding="utf-8"))


class DreamsRetirementTest(unittest.TestCase):
    """Dream reflection payload carries no pack/ledger surfaces post-cutover."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="kosmic-dreams-retire-")
        self.addCleanup(self.temporary.cleanup)
        self.worktree = Path(self.temporary.name) / "worktree"
        self.worktree.mkdir()
        run_git(self.worktree, "init", "-q")
        (self.worktree / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
        self.vault = self.worktree / "memnotes"
        (self.vault / "Projects/foo/notes").mkdir(parents=True)
        (self.vault / "Projects/foo/notes/a.md").write_text(
            "---\ntype: Project Knowledge\nstatus: stable\n"
            "created: 2026-09-16\nupdated: 2026-09-16\n---\n\n# Note\n\ncontent\n",
            encoding="utf-8",
        )
        commit_all(self.worktree, "2026-09-16", "baseline")

    def harvest(self) -> dict:
        return kosmic_dreams.collect_harvest(
            self.vault, date="2026-09-16", timezone_name="UTC"
        )

    def test_project_payload_has_no_pack_or_ledger_surfaces(self) -> None:
        (self.vault / "Projects/foo/impact.md").write_text(
            "# Impact Ledger\n\n"
            "- date: 2026-09-16 | kind: publication | targets: [notes/a.md]"
            ' | refs: "null->abc" | outcome: published | reason: ""\n',
            encoding="utf-8",
        )
        (self.vault / "Projects/foo/evidence/2026-09-16-pack").mkdir(parents=True)
        harvest = self.harvest()
        entry = next(e for e in harvest["projects"] if e["project"] == "foo")
        self.assertNotIn("evidence_packs", entry)
        self.assertNotIn("impact_entries", entry)
        self.assertFalse(
            any(check["kind"] == "evidence-order"
                for check in harvest["knowledge_checks"])
        )

    def test_evidence_order_check_is_retired(self) -> None:
        pack = self.vault / "Projects/foo/evidence/2026-09-16-pack"
        pack.mkdir(parents=True)
        (pack / "MANIFEST.md").write_text(
            "---\nkind: execution\ndate: 2026-09-17\nsummary: pack\n"
            "produced_by: test\n---\n\n- file: role\n",
            encoding="utf-8",
        )
        (self.vault / "Projects/foo/notes/evidenced.md").write_text(
            "---\ntype: Project Knowledge\nstatus: stable\ncreated: 2026-09-16\n"
            "updated: 2026-09-16\n"
            "evidence: [evidence/2026-09-16-pack/MANIFEST.md]\n---\n\n# Note\n\nbody\n",
            encoding="utf-8",
        )
        harvest = self.harvest()
        self.assertFalse(
            any(check["kind"] == "evidence-order"
                for check in harvest["knowledge_checks"])
        )


if __name__ == "__main__":
    unittest.main()
