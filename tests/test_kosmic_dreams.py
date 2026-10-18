from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skills.scripts import kosmic_dreams

REPO_ROOT = Path(__file__).resolve().parents[1]


def run_git(worktree: Path, *args: str, env_extra: dict[str, str] | None = None) -> str:
    env = {**os.environ, **(env_extra or {})}
    completed = subprocess.run(
        ["git", *args], cwd=str(worktree), capture_output=True, text=True, env=env, check=True
    )
    return completed.stdout


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
    run_git(worktree, "add", "-A", env_extra=env)
    run_git(worktree, "commit", "-q", "-m", message, env_extra=env)
    return run_git(worktree, "rev-parse", "HEAD").strip()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def note(created: str, updated: str, body: str = "content") -> str:
    return f"---\ntype: Project Knowledge\nstatus: stable\ncreated: {created}\nupdated: {updated}\n---\n\n# Note\n\n{body}\n"


def init_vault_repo(base: Path) -> tuple[Path, Path]:
    worktree = base / "worktree"
    worktree.mkdir(parents=True)
    run_git(worktree, "init", "-q")
    (worktree / ".gitignore").write_text(".tmp/\n", encoding="utf-8")
    vault = worktree / "memnotes"
    return worktree, vault


def project_files(harvest: dict, project: str | None) -> list[dict]:
    for entry in harvest["projects"]:
        if entry["project"] == project:
            return entry["files"]
    return []


def file_entry(files: list[dict], new_path: str) -> dict | None:
    for entry in files:
        if entry.get("new_path") == new_path:
            return entry
    return None


class HarvestCollectorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-dreams-")
        self.base = Path(self.tmp.name)
        self.worktree, self.vault = init_vault_repo(self.base)
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-10", "2026-09-10"))
        write(self.vault / "Projects/foo/notes/old.md", note("2026-09-01", "2026-09-01"))
        write(self.vault / "Projects/foo/notes/r1.md", note("2026-09-02", "2026-09-02"))
        commit_all(self.worktree, "2026-09-10", "baseline")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_window_commit_union_with_status_and_origins(self) -> None:
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-10", "2026-09-16"))
        write(self.vault / "Projects/foo/notes/b.md", note("2026-09-16", "2026-09-16"))
        (self.vault / "Projects/foo/notes/old.md").unlink()
        run_git(self.worktree, "mv", "memnotes/Projects/foo/notes/r1.md", "memnotes/Projects/foo/notes/r2.md")
        head = commit_all(self.worktree, "2026-09-16", "day work")

        harvest = kosmic_dreams.collect_harvest(
            self.vault, date="2026-09-16", timezone_name="UTC"
        )

        self.assertEqual(harvest["schema"], "kosmic.dream.harvest/1")
        self.assertEqual(harvest["date"], "2026-09-16")
        self.assertEqual(harvest["timezone"], "UTC")
        self.assertEqual(harvest["head"], head)
        self.assertEqual(harvest["source_commits"], [head])
        files = project_files(harvest, "foo")
        created = file_entry(files, "Projects/foo/notes/b.md")
        self.assertIsNotNone(created)
        self.assertEqual(created["status"], "created")
        self.assertIn("git", created["origins"])
        self.assertTrue(created["new_blob"])
        modified = file_entry(files, "Projects/foo/notes/a.md")
        self.assertEqual(modified["status"], "modified")
        self.assertTrue(modified["old_blob"] and modified["new_blob"])
        self.assertNotEqual(modified["old_blob"], modified["new_blob"])
        deleted = file_entry(files, "Projects/foo/notes/old.md")
        self.assertEqual(deleted["status"], "deleted")
        self.assertIsNone(deleted["new_blob"])
        renamed = file_entry(files, "Projects/foo/notes/r2.md")
        self.assertEqual(renamed["status"], "renamed")
        self.assertEqual(renamed["old_path"], "Projects/foo/notes/r1.md")
        self.assertFalse(harvest["coverage"]["shallow"])

    def test_frontmatter_and_dirty_union(self) -> None:
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-10", "2026-09-16"))
        write(self.vault / "Projects/foo/notes/c.md", note("2026-09-16", "2026-09-16"))
        write(self.vault / "Projects/foo/notes/other.md", note("2026-09-10", "2026-09-20"))

        harvest = kosmic_dreams.collect_harvest(
            self.vault, date="2026-09-16", timezone_name="UTC"
        )

        files = project_files(harvest, "foo")
        modified = file_entry(files, "Projects/foo/notes/a.md")
        self.assertIsNotNone(modified)
        self.assertIn("frontmatter", modified["origins"])
        self.assertIn("dirty", modified["origins"])
        untracked = file_entry(files, "Projects/foo/notes/c.md")
        self.assertIsNotNone(untracked)
        self.assertEqual(untracked["status"], "created")
        self.assertIn("frontmatter", untracked["origins"])
        self.assertIn("dirty", untracked["origins"])
        self.assertIsNone(file_entry(files, "Projects/foo/notes/other.md"))
        self.assertTrue(harvest["coverage"]["dirty_classes"])

    def test_deterministic_canonical_json(self) -> None:
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-10", "2026-09-16"))
        first = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        second = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        self.assertEqual(kosmic_dreams.canonical_json(first), kosmic_dreams.canonical_json(second))
        payload = json.loads(kosmic_dreams.canonical_json(first).decode("utf-8"))
        self.assertEqual(payload, first)

    def test_timezone_window_boundaries(self) -> None:
        write(self.vault / "Projects/foo/notes/edge.md", note("2026-09-15", "2026-09-15"))
        stamp = "2026-09-15T23:30:00+00:00"
        env = {
            "GIT_AUTHOR_DATE": stamp,
            "GIT_COMMITTER_DATE": stamp,
            "GIT_AUTHOR_NAME": "fixture",
            "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
            "GIT_COMMITTER_NAME": "fixture",
            "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
        }
        run_git(self.worktree, "add", "-A", env_extra=env)
        run_git(self.worktree, "commit", "-q", "-m", "edge", env_extra=env)

        utc = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        kiritimati = kosmic_dreams.collect_harvest(
            self.vault, date="2026-09-16", timezone_name="Pacific/Kiritimati"
        )
        self.assertIsNone(file_entry(project_files(utc, "foo"), "Projects/foo/notes/edge.md"))
        edge = file_entry(project_files(kiritimati, "foo"), "Projects/foo/notes/edge.md")
        self.assertIsNotNone(edge)

    def test_default_date_is_previous_calendar_day(self) -> None:
        harvest = kosmic_dreams.collect_harvest(self.vault, timezone_name="UTC")
        from datetime import date, datetime, timezone as dt_timezone, timedelta

        now = datetime.now(dt_timezone.utc)
        expected = (now.date() - timedelta(days=1)).isoformat() if now.hour or now.minute or now.second else now.date().isoformat()
        self.assertEqual(harvest["date"], expected)

    def test_project_filter_keeps_shared_evidence(self) -> None:
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-10", "2026-09-16"))
        write(self.vault / "Projects/bar/notes/z.md", note("2026-09-16", "2026-09-16"))
        write(self.vault / "Skills/shared.md", note("2026-09-16", "2026-09-16"))
        write(self.vault / "README.md", f"---\ntype: vault\ncreated: 2026-09-16\nupdated: 2026-09-16\n---\n")
        commit_all(self.worktree, "2026-09-16", "multi project")

        harvest = kosmic_dreams.collect_harvest(
            self.vault, date="2026-09-16", timezone_name="UTC", project="foo"
        )
        self.assertEqual(harvest["project_filter"], "foo")
        names = {entry["project"] for entry in harvest["projects"]}
        self.assertIn("foo", names)
        self.assertIn(None, names)
        self.assertNotIn("bar", names)
        shared_files = project_files(harvest, None)
        self.assertIsNotNone(file_entry(shared_files, "Skills/shared.md"))
        self.assertIsNotNone(file_entry(shared_files, "README.md"))

    def test_shallow_repository_warning(self) -> None:
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-10", "2026-09-16"))
        commit_all(self.worktree, "2026-09-16", "shallow base")
        shallow_dir = self.base / "shallow"
        subprocess.run(
            ["git", "clone", "-q", "--depth", "1", f"file://{self.worktree}", str(shallow_dir)],
            capture_output=True,
            text=True,
            check=True,
        )
        harvest = kosmic_dreams.collect_harvest(
            shallow_dir / "memnotes", date="2026-09-16", timezone_name="UTC"
        )
        self.assertTrue(harvest["coverage"]["shallow"])
        self.assertTrue(
            any("shallow" in warning for warning in harvest["coverage"]["warnings"])
        )

    def test_fail_closed_without_repository(self) -> None:
        empty = self.base / "plain"
        empty.mkdir()
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.collect_harvest(empty, date="2026-09-16", timezone_name="UTC")
        self.assertEqual(ctx.exception.code, "NO_REPOSITORY")

    def test_invalid_date_and_timezone_fail_closed(self) -> None:
        with self.assertRaises(kosmic_dreams.DreamError):
            kosmic_dreams.collect_harvest(self.vault, date="2026-9-16", timezone_name="UTC")
        with self.assertRaises(kosmic_dreams.DreamError):
            kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="Mars/Olympus")


if __name__ == "__main__":
    unittest.main()


def spec_file(status: str, updated: str, extra: str = "") -> str:
    return (
        "---\n"
        f"status: {status}\n"
        f"created: 2026-09-01\nupdated: {updated}\n"
        f"{extra}"
        "---\n\n# Item\n\nbody\n"
    )


class StatusChangeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-dreams-")
        self.base = Path(self.tmp.name)
        self.worktree, self.vault = init_vault_repo(self.base)
        story = self.vault / "Projects/foo/specs/stories/story-001-x.md"
        write(story, spec_file("in_progress", "2026-09-10"))
        write(self.vault / "Projects/foo/specs/stories/story-002-y.md", spec_file("in_progress", "2026-09-10"))
        commit_all(self.worktree, "2026-09-10", "baseline")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_status_transition_from_blobs(self) -> None:
        story = self.vault / "Projects/foo/specs/stories/story-001-x.md"
        write(story, spec_file("done", "2026-09-16"))
        head = commit_all(self.worktree, "2026-09-16", "story done")
        harvest = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        changes = project_entry(harvest, "foo")["status_changes"]
        self.assertEqual(len(changes), 1)
        change = changes[0]
        self.assertEqual(change["path"], "Projects/foo/specs/stories/story-001-x.md")
        self.assertEqual(change["from"], "in_progress")
        self.assertEqual(change["to"], "done")
        self.assertTrue(change["old_blob"])
        self.assertEqual(change["new_blob"], blob_of(self.worktree, head, "memnotes/Projects/foo/specs/stories/story-001-x.md"))

    def test_unchanged_story_has_no_transition(self) -> None:
        harvest = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        self.assertEqual(project_entry(harvest, "foo")["status_changes"], [])


class OpenWorkTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-dreams-")
        self.base = Path(self.tmp.name)
        self.worktree, self.vault = init_vault_repo(self.base)
        write(self.vault / "Projects/foo/specs/stories/story-001-x.md", spec_file("in_progress", "2026-09-10"))
        write(self.vault / "Projects/foo/specs/stories/story-002-y.md", spec_file("blocked", "2026-09-12"))
        write(self.vault / "Projects/foo/specs/stories/story-003-z.md", spec_file("done", "2026-09-12"))
        write(self.vault / "Projects/foo/specs/epics/epic-1-e.md", spec_file("done", "2026-09-12"))
        write(self.vault / "Projects/foo/specs/quick-tasks/2026-09-01-a.md", spec_file("draft", "2026-09-14"))
        write(self.vault / "Projects/foo/specs/prd-dream.md", spec_file("draft", "2026-09-15"))
        write(self.vault / "Projects/foo/specs/architecture-dream.md", spec_file("approved", "2026-09-15"))
        write(self.vault / "Projects/foo/specs/skill-proposals/2026-09-10-p.md", spec_file("approved", "2026-09-15", "decision: pending\n"))
        write(self.vault / "Projects/foo/specs/skill-proposals/2026-09-11-q.md", spec_file("done", "2026-09-15", "decision: accepted\n"))
        commit_all(self.worktree, "2026-09-10", "baseline")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_open_work_excludes_terminal_records(self) -> None:
        harvest = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        open_work = project_entry(harvest, "foo")["open_work"]
        by_path = {entry["path"]: entry for entry in open_work}
        self.assertIn("Projects/foo/specs/stories/story-001-x.md", by_path)
        blocked = by_path["Projects/foo/specs/stories/story-002-y.md"]
        self.assertEqual(blocked["blocker"], "blocked")
        self.assertNotIn("Projects/foo/specs/stories/story-003-z.md", by_path)
        self.assertNotIn("Projects/foo/specs/epics/epic-1-e.md", by_path)
        self.assertIn("Projects/foo/specs/quick-tasks/2026-09-01-a.md", by_path)
        prd = by_path["Projects/foo/specs/prd-dream.md"]
        self.assertEqual(prd["kind"], "prd")
        self.assertNotIn("Projects/foo/specs/architecture-dream.md", by_path)
        proposal = by_path["Projects/foo/specs/skill-proposals/2026-09-10-p.md"]
        self.assertEqual(proposal["kind"], "proposal")
        self.assertNotIn("Projects/foo/specs/skill-proposals/2026-09-11-q.md", by_path)
        kinds = {entry["kind"] for entry in open_work}
        self.assertEqual(kinds, {"story", "quick-task", "prd", "proposal"})

    def test_project_filter_excludes_other_projects(self) -> None:
        write(self.vault / "Projects/bar/specs/stories/story-009-b.md", spec_file("in_progress", "2026-09-12"))
        harvest = kosmic_dreams.collect_harvest(
            self.vault, date="2026-09-16", timezone_name="UTC", project="foo"
        )
        names = {entry["project"] for entry in harvest["projects"]}
        self.assertNotIn("bar", names)


def blob_of(worktree: Path, rev: str, repo_path: str) -> str:
    return run_git(worktree, "rev-parse", f"{rev}:{repo_path}").strip()


def project_entry(harvest: dict, project: str) -> dict:
    for entry in harvest["projects"]:
        if entry["project"] == project:
            return entry
    raise AssertionError(f"project {project} missing")


class KnowledgeContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-dreams-")
        self.base = Path(self.tmp.name)
        self.worktree, self.vault = init_vault_repo(self.base)
        log = self.vault / "Projects/foo/log/foo-2026-09-16.md"
        write(log, "# Log\n\n## Session 1\n\n- [Extracted] [done thing](../notes/a.md) - good\n- raw discovery without extraction\n- another raw item\n")
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-16", "2026-09-16"))
        write(self.vault / "Projects/foo/notes/draft-x.md", note("2026-09-16", "2026-09-16").replace("status: stable", "status: draft"))
        write(self.vault / "Projects/foo/notes/cited-draft.md", note("2026-09-16", "2026-09-16").replace("status: stable", "status: draft"))
        write(self.vault / "Projects/foo/notes/linker.md", note("2026-09-16", "2026-09-16", body="see [cited](cited-draft.md#section) and [log](../log/foo-2026-09-16.md)"))
        write(self.vault / "Projects/foo/notes/stale-note.md", note("2026-09-01", "2026-09-01").replace("created: 2026-09-01", "created: 2026-09-01\nstale_after: 2026-09-10"))
        evidence_manifest = self.vault / "Projects/foo/evidence/2026-09-17-pack/MANIFEST.md"
        write(evidence_manifest, "---\nkind: execution\ndate: 2026-09-17\nsummary: pack\nproduced_by: test\n---\n\n- file: role\n")
        write(self.vault / "Projects/foo/notes/evidenced.md", "---\ntype: Project Knowledge\nstatus: stable\ncreated: 2026-09-16\nupdated: 2026-09-16\nevidence: [evidence/2026-09-17-pack/MANIFEST.md]\n---\n\n# Note\n\nbody\n")
        commit_all(self.worktree, "2026-09-16", "day work")
        write(self.vault / "Projects/foo/specs/stories/story-001-x.md", spec_file("in_progress", "2026-09-10"))
        write(self.vault / "dreams/2026-09-10.md", "---\nschema: kosmic.dream.record/1\ntype: dream\ndate: 2026-09-10\n---\n\n# Dream\n\n## Skill Candidates\n\n- candidate one from prior dream\n\n## Done\n\n- old\n")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def harvest(self, **kwargs):
        return kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC", **kwargs)

    def test_unextracted_log_items(self) -> None:
        harvest = self.harvest()
        items = project_entry(harvest, "foo")["log_items"]
        self.assertEqual(len(items), 2)
        kinds = sorted(check["kind"] for check in harvest["knowledge_checks"])
        unextracted = [check for check in harvest["knowledge_checks"] if check["kind"] == "unextracted-log"]
        self.assertEqual(len(unextracted), 2)
        self.assertTrue(all(check["subject"]["path"] == "Projects/foo/log/foo-2026-09-16.md" for check in unextracted))

    def test_uncited_draft_and_backlink_normalization(self) -> None:
        harvest = self.harvest()
        uncited = [check for check in harvest["knowledge_checks"] if check["kind"] == "uncited-draft"]
        self.assertEqual(
            sorted(check["subject"]["path"] for check in uncited),
            ["Projects/foo/notes/draft-x.md"],
        )
        links = {(row["source"], row["target"]) for row in harvest["link_index"]}
        self.assertIn(
            ("Projects/foo/notes/linker.md", "Projects/foo/notes/cited-draft.md"), links
        )

    def test_declared_stale(self) -> None:
        harvest = self.harvest()
        stale = [check for check in harvest["knowledge_checks"] if check["kind"] == "declared-stale"]
        self.assertEqual([check["subject"]["path"] for check in stale], ["Projects/foo/notes/stale-note.md"])

    def test_evidence_order(self) -> None:
        harvest = self.harvest()
        ordered = [check for check in harvest["knowledge_checks"] if check["kind"] == "evidence-order"]
        self.assertEqual(len(ordered), 1)
        self.assertEqual(ordered[0]["subject"]["path"], "Projects/foo/notes/evidenced.md")
        self.assertEqual(
            ordered[0]["evidence"][0]["path"], "Projects/foo/evidence/2026-09-17-pack/MANIFEST.md"
        )

    def test_candidate_evidence_and_read_set(self) -> None:
        harvest = self.harvest()
        kinds = {entry["kind"] for entry in harvest["candidate_evidence"]}
        self.assertIn("prior-dream", kinds)
        prior = [entry for entry in harvest["candidate_evidence"] if entry["kind"] == "prior-dream"][0]
        self.assertEqual(prior["ref"], "dreams/2026-09-10.md")
        self.assertIn("candidate one", prior["summary"])
        read_refs = {entry["ref"] for entry in harvest["read_set"]}
        self.assertIn("Projects/foo/notes/draft-x.md", read_refs)
        self.assertIn("Projects/foo/log/foo-2026-09-16.md", read_refs)
        self.assertIn("Projects/foo/evidence/2026-09-17-pack/MANIFEST.md", read_refs)
        self.assertIn("dreams/2026-09-10.md", read_refs)
        self.assertIn("Projects/foo/specs/stories/story-001-x.md", read_refs)
        for entry in harvest["read_set"]:
            if entry["kind"] == "path":
                content = (self.vault / entry["ref"]).read_bytes()
                self.assertEqual(entry["sha256"], hashlib_sha256(content))

    def test_read_set_blob_for_deleted_file(self) -> None:
        victim = self.vault / "Projects/foo/notes/a.md"
        victim.unlink()
        run_git(self.worktree, "add", "-A")
        # deletion is staged but not committed; frontmatter origin cannot exist
        # for a deleted file, so the deletion is invisible to the union.  This
        # asserts the documented semantics instead.
        harvest = self.harvest()
        refs = {entry["ref"] for entry in harvest["read_set"]}
        self.assertNotIn("Projects/foo/notes/a.md", refs)


def hashlib_sha256(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def candidate_record(date: str = "2026-09-16", body: str | None = None) -> str:
    body = body or (
        "## Done\n\n- shipped the release\n\n"
        "## In Flight\n\n- story 001 awaiting approval\n\n"
        "## Notes Digest\n\n- [note](../Projects/foo/notes/a.md) updated\n\n"
        "## Knowledge Flags\n\n- unextracted log items exist\n\n"
        "## Skill Candidates\n\n- candidate with [two](../Projects/foo/notes/a.md) [refs](../Projects/foo/log/foo-2026-09-16.md)\n\n"
        "## Ideas\n\n- 2026-09-16-idea-x — try nightly dream — trigger: [log](../Projects/foo/log/foo-2026-09-16.md) — next: discuss (added 2026-09-16)\n\n"
        "## Today\n\n- review the record\n"
    )
    return f"---\nschema: kosmic.dream.candidate/1\ntype: dream-candidate\ndate: {date}\n---\n\n# Dream\n\n{body}"


class RecordSchemaTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-dreams-")
        self.base = Path(self.tmp.name)
        self.worktree, self.vault = init_vault_repo(self.base)
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-16", "2026-09-16"))
        write(self.vault / "Projects/foo/log/foo-2026-09-16.md", "# Log\n\n- item\n")
        commit_all(self.worktree, "2026-09-16", "day")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def build(self, **overrides):
        harvest = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        candidate = kosmic_dreams.parse_candidate(candidate_record())
        return kosmic_dreams.build_record_bytes(
            candidate, harvest=harvest, run_id="20260923T000000Z-dream-abc123"
        )

    def test_build_record_bytes_and_hash_roundtrip(self) -> None:
        record_bytes = self.build()
        text = record_bytes.decode("utf-8")
        self.assertTrue(text.startswith("---\nschema: kosmic.dream.record/1\n"))
        fields, sections = kosmic_dreams.parse_record(text)
        self.assertEqual(fields["type"], "dream")
        self.assertEqual(fields["date"], "2026-09-16")
        self.assertEqual(fields["status"], "draft")
        self.assertEqual(fields["produced_by"], "dream/20260923T000000Z-dream-abc123")
        self.assertEqual(list(sections), kosmic_dreams.SECTION_ORDER)
        self.assertEqual(
            fields["generated_content_sha256"], kosmic_dreams.compute_generated_hash(record_bytes)
        )
        kosmic_dreams.validate_record_text(text, expected_date="2026-09-16")

    def test_candidate_with_forged_fields_fails(self) -> None:
        forged = candidate_record().replace(
            "date: 2026-09-16\n---", "date: 2026-09-16\nproduced_by: dream/fake\n---"
        )
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.parse_candidate(forged)
        self.assertEqual(ctx.exception.code, "CANDIDATE_FIELD_FORBIDDEN")

    def test_candidate_date_mismatch_fails_at_build(self) -> None:
        harvest = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        candidate = kosmic_dreams.parse_candidate(candidate_record(date="2026-09-15"))
        with self.assertRaises(kosmic_dreams.DreamError):
            kosmic_dreams.build_record_bytes(candidate, harvest=harvest, run_id="r-1")

    def test_missing_section_fails_validation(self) -> None:
        harvest = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        broken = candidate_record().replace("## Today\n\n- review the record\n", "")
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.parse_candidate(broken)
        self.assertEqual(ctx.exception.code, "SECTION_MISSING")
        candidate = kosmic_dreams.parse_candidate(candidate_record())
        record = kosmic_dreams.build_record_bytes(candidate, harvest=harvest, run_id="r-1")
        stripped = record.decode("utf-8").replace("## Today", "## Notes Digest", 1)
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.validate_record_text(stripped, expected_date="2026-09-16")
        self.assertIn(ctx.exception.code, {"SECTION_ORDER", "RECORD_HASH_MISMATCH"})

    def test_redaction_strips_control_patterns(self) -> None:
        dirty = "handle_file: /x/.tmp/kosmic/handles/abc and token: ghp_supersecret stay out"
        cleaned = kosmic_dreams.redact_text(dirty)
        self.assertNotIn("ghp_supersecret", cleaned)
        self.assertNotIn(".tmp/kosmic", cleaned)


class IdeasTest(unittest.TestCase):
    def test_parse_and_merge_dedupe(self) -> None:
        base = "- 2026-09-10-idea-a — first — trigger: [x](../Projects/foo/notes/a.md) — next: chat (added 2026-09-10)\n"
        same = "- 2026-09-10-idea-a — first — trigger: [x](../Projects/foo/notes/a.md) — next: chat (added 2026-09-10)\n"
        fresh = "- 2026-09-16-idea-b — second — trigger: [y](../Projects/foo/notes/a.md) — next: try (added 2026-09-16)\n"
        merged = kosmic_dreams.merge_ideas(base, same + fresh)
        self.assertEqual(merged.count("- 2026-09-10-idea-a"), 1)
        self.assertIn("2026-09-16-idea-b", merged)

    def test_conflicting_same_id_fails(self) -> None:
        base = "- 2026-09-10-idea-a — first — trigger: t — next: chat (added 2026-09-10)\n"
        clash = "- 2026-09-10-idea-a — different text — trigger: t — next: chat (added 2026-09-10)\n"
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.merge_ideas(base, clash)
        self.assertEqual(ctx.exception.code, "IDEA_ID_CONFLICT")

    def test_bad_id_format_fails(self) -> None:
        with self.assertRaises(kosmic_dreams.DreamError):
            kosmic_dreams.merge_ideas("", "- not-an-id — text\n")


class ValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-dreams-")
        self.base = Path(self.tmp.name)
        self.worktree, self.vault = init_vault_repo(self.base)
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-16", "2026-09-16"))
        write(self.vault / "Projects/foo/log/foo-2026-09-16.md", "# Log\n\n- item\n")
        commit_all(self.worktree, "2026-09-16", "day")
        harvest = kosmic_dreams.collect_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        candidate = kosmic_dreams.parse_candidate(candidate_record())
        self.record = kosmic_dreams.build_record_bytes(
            candidate, harvest=harvest, run_id="20260923T000000Z-dream-abc123"
        )
        self.root = self.base / "staged" / "dreams"
        self.root.mkdir(parents=True)
        (self.root / "2026-09-16.md").write_bytes(self.record)
        (self.root / "ideas.md").write_text(
            "- 2026-09-16-idea-x — try nightly dream — trigger: [log](../Projects/foo/log/foo-2026-09-16.md) — next: discuss (added 2026-09-16)\n"
        )
        (self.root / "index.md").write_text(
            "# Dreams\n\n| Date | Summary |\n|------|---------|\n| [2026-09-16](2026-09-16.md) | shipped the release |\n"
        )

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_valid_tree_passes(self) -> None:
        kosmic_dreams.validate_dream_tree(self.vault, root=self.root)

    def test_unknown_child_fails_closed(self) -> None:
        (self.root / "notes.md").write_text("stray\n")
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.validate_dream_tree(self.vault, root=self.root)
        self.assertEqual(ctx.exception.code, "DREAM_CHILD_UNKNOWN")

    def test_index_drift_fails(self) -> None:
        (self.root / "index.md").write_text(
            "# Dreams\n\n| Date | Summary |\n|------|---------|\n| [2026-09-15](2026-09-15.md) | wrong |\n"
        )
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.validate_dream_tree(self.vault, root=self.root)
        self.assertEqual(ctx.exception.code, "INDEX_MISMATCH")

    def test_missing_external_link_target_fails(self) -> None:
        (self.vault / "Projects/foo/notes/a.md").unlink()
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.validate_dream_tree(self.vault, root=self.root)
        self.assertEqual(ctx.exception.code, "LINK_TARGET_MISSING")

    def test_secret_labels_fail_closed(self) -> None:
        tampered = self.record.decode("utf-8").replace(
            "## Today", "## Today\n\n- token: ghp_leakedvalue\n"
        )
        (self.root / "2026-09-16.md").write_text(tampered)
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.validate_dream_tree(self.vault, root=self.root)
        self.assertEqual(ctx.exception.code, "SECRET_CONTENT")

    def test_index_rebuild_reverse_chronological(self) -> None:
        index = kosmic_dreams.rebuild_index({"2026-09-16": "newer", "2026-09-10": "older"})
        lines = index.decode("utf-8").splitlines()
        dates = [line.split("]")[0].strip("| [") for line in lines if line.startswith("| [")]
        self.assertEqual(dates, ["2026-09-16", "2026-09-10"])


class PipelineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-dreams-")
        self.base = Path(self.tmp.name)
        self.worktree, self.vault = init_vault_repo(self.base)
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-16", "2026-09-16"))
        write(self.vault / "Projects/foo/log/foo-2026-09-16.md", "# Log\n\n- item\n")
        write(self.vault / "Projects/foo/specs/stories/story-001-x.md", spec_file("in_progress", "2026-09-10"))
        commit_all(self.worktree, "2026-09-16", "day")
        self.handles: list[Path] = []

    def tearDown(self) -> None:
        from skills.scripts import kosmic_runs

        for handle in self.handles:
            try:
                state = kosmic_dreams.read_dream_state(handle)
                if state["handle_state"] == "active":
                    kosmic_runs.finish_run(handle, "failed", detail="test cleanup")
            except Exception:
                pass
        self.tmp.cleanup()

    def harvest_run(self, **kwargs):
        kwargs.setdefault("date", "2026-09-16")
        payload = kosmic_dreams.dream_harvest(self.vault, timezone_name="UTC", **kwargs)
        handle = Path(payload["handle_file"])
        self.handles.append(handle)
        return payload, handle

    def write_candidate(self, payload) -> None:
        Path(payload["candidate_record"]).write_text(candidate_record(), encoding="utf-8")
        Path(payload["candidate_ideas"]).write_text(
            "- 2026-09-16-idea-x — try nightly dream — trigger: [log](../Projects/foo/log/foo-2026-09-16.md) — next: discuss (added 2026-09-16)\n",
            encoding="utf-8",
        )

    def test_dream_publish_cli_resolves_record_under_projects_owner(self) -> None:
        payload, handle = self.harvest_run()
        self.write_candidate(payload)
        project_root = self.vault / "Projects/foo"
        write(project_root / "ProjectEntry.md", "---\nproject_id: foo\n---\n\n# foo\n")
        write(project_root / "specs/quick-tasks/2026-10-04-dream-publish.md",
              "---\nproject_id: foo\nsubproject_id: null\nrecord_kind: quick-task\n"
              "local_id: dream-publish\nstatus: approved\n---\n\n# Dream publication\n")
        cli = REPO_ROOT / "skills/scripts/kosmic_project_skills.py"
        result = subprocess.run(
            [sys.executable, str(cli), "dream-publish", "--vault", str(self.vault),
             "--handle", str(handle), "--work-record", "foo/quick-task/dream-publish"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.vault / "dreams/2026-09-16.md").is_file())

    def test_full_pipeline_publishes_canonical_tree(self) -> None:
        payload, handle = self.harvest_run()
        self.assertTrue(Path(payload["harvest"]).is_file())
        self.assertEqual(payload["evidence_count"] > 0, True)
        self.write_candidate(payload)
        result = kosmic_dreams.dream_publish(self.vault, handle)
        self.assertEqual(result["code"], "OK")
        canonical = self.vault / "dreams" / "2026-09-16.md"
        self.assertTrue(canonical.is_file())
        kosmic_dreams.validate_dream_tree(self.vault)
        index = (self.vault / "dreams" / "index.md").read_text(encoding="utf-8")
        self.assertIn("2026-09-16", index)
        ideas = (self.vault / "dreams" / "ideas.md").read_text(encoding="utf-8")
        self.assertIn("2026-09-16-idea-x", ideas)
        state = kosmic_dreams.read_dream_state(handle)
        self.assertEqual(state["handle_state"], "succeeded")

    def test_publish_without_candidate_fails_retryable(self) -> None:
        payload, handle = self.harvest_run()
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.dream_publish(self.vault, handle)
        self.assertEqual(ctx.exception.code, "DREAM_INPUT_MISSING")
        state = kosmic_dreams.read_dream_state(handle)
        self.assertEqual(state["dream_state"]["state"], "retryable-input")
        self.write_candidate(payload)
        result = kosmic_dreams.dream_publish(self.vault, handle)
        self.assertEqual(result["code"], "OK")

    def test_base_drift_requires_new_harvest(self) -> None:
        payload, handle = self.harvest_run()
        self.write_candidate(payload)
        (self.vault / "dreams").mkdir(exist_ok=True)
        (self.vault / "dreams" / "2026-09-01.md").write_text("tamper\n")
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.dream_publish(self.vault, handle)
        self.assertEqual(ctx.exception.code, "DREAM_BASE_DRIFT")
        state = kosmic_dreams.read_dream_state(handle)
        self.assertEqual(state["dream_state"]["state"], "reharvest-required")

    def test_manual_divergence_requires_replace(self) -> None:
        payload, handle = self.harvest_run()
        self.write_candidate(payload)
        self.assertEqual(kosmic_dreams.dream_publish(self.vault, handle)["code"], "OK")
        record = self.vault / "dreams" / "2026-09-16.md"
        record.write_text(record.read_text().replace("## Today", "## Today\n\n- human note"), encoding="utf-8")
        payload2, handle2 = self.harvest_run()
        self.write_candidate(payload2)
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.dream_publish(self.vault, handle2)
        self.assertEqual(ctx.exception.code, "DREAM_MANUAL_DIVERGENCE")
        result = kosmic_dreams.dream_publish(self.vault, handle2, replace=True)
        self.assertEqual(result["code"], "OK")

    def test_idempotent_generated_rerun_and_terminal_repeat(self) -> None:
        payload, handle = self.harvest_run()
        self.write_candidate(payload)
        self.assertEqual(kosmic_dreams.dream_publish(self.vault, handle)["code"], "OK")
        payload2, handle2 = self.harvest_run()
        self.write_candidate(payload2)
        self.assertEqual(kosmic_dreams.dream_publish(self.vault, handle2)["code"], "OK")
        again = kosmic_dreams.dream_publish(self.vault, handle2)
        self.assertEqual(again["code"], "OK_ALREADY_PUBLISHED")
        index = (self.vault / "dreams" / "index.md").read_text(encoding="utf-8")
        self.assertEqual(index.count("[2026-09-16](2026-09-16.md)"), 1)

    def test_abort_then_publish_is_terminal(self) -> None:
        payload, handle = self.harvest_run()
        result = kosmic_dreams.dream_abort(self.vault, handle, reason="operator cancelled")
        self.assertEqual(result["code"], "OK")
        self.assertEqual(kosmic_dreams.dream_abort(self.vault, handle, reason="again")["code"], "OK_ALREADY_FAILED")
        self.write_candidate(payload)
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.dream_publish(self.vault, handle)
        self.assertEqual(ctx.exception.code, "DREAM_TERMINAL")

    def test_two_dates_keep_reverse_index_unique(self) -> None:
        payload, handle = self.harvest_run()
        self.write_candidate(payload)
        self.assertEqual(kosmic_dreams.dream_publish(self.vault, handle)["code"], "OK")
        write(self.vault / "Projects/foo/notes/b.md", note("2026-09-17", "2026-09-17"))
        commit_all(self.worktree, "2026-09-17", "next day")
        payload2, handle2 = self.harvest_run(date="2026-09-17")
        Path(payload2["candidate_record"]).write_text(
            candidate_record(date="2026-09-17", body="## Done\n\n- second day\n\n## In Flight\n\n- x\n\n## Notes Digest\n\n- [n](../Projects/foo/notes/b.md)\n\n## Knowledge Flags\n\n- none new\n\n## Skill Candidates\n\n- none\n\n## Ideas\n\n- none\n\n## Today\n\n- continue\n"),
            encoding="utf-8",
        )
        Path(payload2["candidate_ideas"]).write_text("", encoding="utf-8")
        self.assertEqual(kosmic_dreams.dream_publish(self.vault, handle2)["code"], "OK")
        kosmic_dreams.validate_dream_tree(self.vault)
        rows = [
            line.split("]")[0].strip("| [")
            for line in (self.vault / "dreams" / "index.md").read_text(encoding="utf-8").splitlines()
            if line.startswith("| [")
        ]
        self.assertEqual(rows, ["2026-09-17", "2026-09-16"])


class BindingDriftTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-dreams-")
        self.base = Path(self.tmp.name)
        self.worktree, self.vault = init_vault_repo(self.base)
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-16", "2026-09-16"))
        commit_all(self.worktree, "2026-09-16", "day")

    def tearDown(self) -> None:
        from skills.scripts import kosmic_runs

        for handle_dir in sorted((self.worktree / ".tmp/kosmic/handles").glob("*")):
            try:
                kosmic_runs.finish_run(handle_dir, "failed", detail="cleanup")
            except Exception:
                pass
        self.tmp.cleanup()

    def test_cross_vault_publish_fails_closed(self) -> None:
        payload = kosmic_dreams.dream_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        Path(payload["candidate_record"]).write_text(candidate_record())
        Path(payload["candidate_ideas"]).write_text("")
        other_worktree, other_vault = init_vault_repo(self.base / "other")
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.dream_publish(other_vault, Path(payload["handle_file"]))
        self.assertEqual(ctx.exception.code, "VAULT_MISMATCH")

    def test_live_read_set_drift_fails_closed(self) -> None:
        payload = kosmic_dreams.dream_harvest(self.vault, date="2026-09-16", timezone_name="UTC")
        Path(payload["candidate_record"]).write_text(candidate_record())
        Path(payload["candidate_ideas"]).write_text("")
        write(self.vault / "Projects/foo/notes/a.md", note("2026-09-16", "2026-09-23"))
        with self.assertRaises(kosmic_dreams.DreamError) as ctx:
            kosmic_dreams.dream_publish(self.vault, Path(payload["handle_file"]))
        self.assertEqual(ctx.exception.code, "DREAM_EVIDENCE_DRIFT")
