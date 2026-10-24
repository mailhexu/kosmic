"""Project/general idea capture through the supported CLI and its saved files."""
from __future__ import annotations

import concurrent.futures
import datetime
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from skills.scripts import kosmic_ideas
from skills.scripts.kosmic_yaml import parse_mapping

CLI = Path(__file__).resolve().parents[1] / "skills/scripts/kosmic_project_skills.py"



class IdeaCaptureTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.vault = Path(self.temporary.name)
        self.project = self.vault / "Projects/alpha"
        self.project.mkdir(parents=True)
        (self.project / "ProjectEntry.md").write_text(
            "---\nproject_id: alpha\n---\n\n# Alpha\n", encoding="utf-8")

    def invoke(self, *arguments):
        return subprocess.run(
            [sys.executable, "-B", str(CLI), "idea", *map(str, arguments)],
            cwd=self.vault, text=True, capture_output=True,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}, timeout=30)

    def capture(self, *arguments):
        result = self.invoke(*arguments)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        path = Path(payload["idea_path"])
        self.assertTrue(path.is_absolute())
        raw = path.read_text(encoding="utf-8")
        frontmatter, body = raw.split("---", 2)[1:]
        return payload, path, parse_mapping(frontmatter), body

    def test_project_capture_creates_title_named_dated_history(self):
        text = "Try symmetry reduction.\n\nCheck χ(q) before assuming equivalence."
        before = datetime.datetime.now(datetime.timezone.utc)
        payload, path, metadata, body = self.capture(
            "--project", self.project, "--title", "Symmetry-reduced sampling", "--text", text)
        after = datetime.datetime.now(datetime.timezone.utc)
        self.assertEqual(self.project / "ideas/symmetry-reduced-sampling.md", path)
        self.assertEqual("project", payload["scope"])
        self.assertEqual("alpha", metadata["project_id"])
        self.assertEqual("idea", metadata["type"])
        self.assertEqual("draft", metadata["status"])
        created = datetime.datetime.fromisoformat(metadata["created"].replace("Z", "+00:00"))
        self.assertLessEqual(before, created)
        self.assertLessEqual(created, after)
        self.assertIn("## History\n", body)
        self.assertIn("### " + created.date().isoformat() + "\n", body)
        self.assertEqual(1, body.count(text))
        self.assertEqual({"ProjectEntry.md", "ideas"}, {p.name for p in self.project.iterdir()})

    def test_general_capture_needs_no_project_and_omits_project_identity(self):
        vault = self.vault / "minimal-vault"
        vault.mkdir()
        result = self.invoke("--vault", vault, "--title", "General thought", "--text", "Maybe this works.")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        path = Path(payload["idea_path"])
        self.assertEqual(vault / "GeneralIdeas/general-thought.md", path)
        self.assertEqual("general", payload["scope"])
        self.assertNotIn("project_id", payload)
        _, body = path.read_text(encoding="utf-8").split("---", 2)[1:]
        metadata = parse_mapping(path.read_text(encoding="utf-8").split("---", 2)[1])
        self.assertNotIn("project_id", metadata)
        self.assertEqual(1, body.count("Maybe this works."))
        self.assertFalse((vault / "Projects").exists())

    def test_omitted_title_uses_decorated_first_nonempty_line(self):
        result = self.invoke(
            "--vault", self.vault, "--text", "  ## Preserve   this title\n\nComplete body.")
        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("Preserve this title", payload["title"])
        self.assertEqual(self.vault / "GeneralIdeas/preserve-this-title.md",
                         Path(payload["idea_path"]))
        self.assertIn("  ## Preserve   this title\n\nComplete body.",
                      Path(payload["idea_path"]).read_text(encoding="utf-8"))

    def test_project_and_general_capture_stay_isolated(self):
        other = self.vault / "Projects/beta"
        other.mkdir()
        (other / "ProjectEntry.md").write_text(
            "---\nproject_id: beta\n---\n\n# Beta\n", encoding="utf-8")
        canonical = self.project / "notes/canonical.md"
        canonical.parent.mkdir()
        canonical.write_bytes(b"canonical note")
        dream = self.vault / "dreams/keep.md"
        dream.parent.mkdir()
        dream.write_bytes(b"dream bytes")
        unrelated = self.vault / "unrelated.bin"
        unrelated.write_bytes(b"unrelated bytes")
        project_result = self.invoke(
            "--project", self.project, "--title", "Project thought", "--text", "Alpha only.")
        general_result = self.invoke(
            "--vault", self.vault, "--title", "General thought", "--text", "Not a Project.")
        self.assertEqual(0, project_result.returncode, project_result.stderr)
        self.assertEqual(0, general_result.returncode, general_result.stderr)
        self.assertTrue((self.project / "ideas/project-thought.md").is_file())
        self.assertTrue((self.vault / "GeneralIdeas/general-thought.md").is_file())
        self.assertFalse((other / "ideas").exists())
        self.assertEqual(b"canonical note", canonical.read_bytes())
        self.assertEqual(b"dream bytes", dream.read_bytes())
        self.assertEqual(b"unrelated bytes", unrelated.read_bytes())
        self.assertEqual({"ProjectEntry.md", "ideas", "notes"},
                         {item.name for item in self.project.iterdir()})
        self.assertEqual({"ProjectEntry.md"}, {item.name for item in other.iterdir()})

    def test_identical_captures_create_distinct_complete_notes(self):
        first = self.capture("--project", self.project, "--title", "Same idea", "--text", "Repeat exactly.")
        original = first[1].read_bytes()
        second = self.capture("--project", self.project, "--title", "Same idea", "--text", "Repeat exactly.")
        self.assertEqual(self.project / "ideas/same-idea-2.md", second[1])
        self.assertEqual(original, first[1].read_bytes())
        self.assertEqual(1, first[3].count("Repeat exactly."))
        self.assertEqual(1, second[3].count("Repeat exactly."))
        self.assertEqual({"same-idea.md", "same-idea-2.md"},
                         {item.name for item in (self.project / "ideas").iterdir()})

    def test_concurrent_same_title_captures_publish_distinct_notes(self):
        def run(index):
            return self.invoke(
                "--project", self.project, "--title", "Concurrent idea",
                "--text", f"Complete body {index}.")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(run, range(4)))
        self.assertTrue(all(result.returncode == 0 for result in results),
                        [result.stderr for result in results])
        paths = [Path(json.loads(result.stdout)["idea_path"]) for result in results]
        self.assertEqual(4, len(set(paths)))
        contents = [path.read_text(encoding="utf-8") for path in paths]
        self.assertTrue(all(content.startswith("---\n") for content in contents))
        expected_bodies = {f"Complete body {index}." for index in range(4)}
        self.assertTrue(all(sum(body in content for content in contents) == 1
                            for body in expected_bodies))

    def test_unsafe_destination_types_are_refused(self):
        for kind in ("symlink", "file"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as outside:
                destination = self.project / "ideas"
                if kind == "symlink":
                    destination.symlink_to(outside, target_is_directory=True)
                else:
                    destination.write_text("preserve", encoding="utf-8")
                result = self.invoke(
                    "--project", self.project, "--title", "Blocked", "--text", "No write.")
                self.assertNotEqual(0, result.returncode)
                self.assertFalse((Path(outside) / "blocked.md").exists())
                self.assertTrue(destination.is_symlink() if kind == "symlink"
                                else destination.read_text(encoding="utf-8") == "preserve")
                if kind == "symlink":
                    destination.unlink()
                else:
                    destination.unlink()

    def test_unsafe_candidate_types_are_refused_without_bypassing(self):
        ideas = self.project / "ideas"
        ideas.mkdir()
        for kind in ("symlink", "directory", "fifo"):
            name = ideas / f"unsafe-{kind}.md"
            if kind == "symlink":
                name.symlink_to(self.vault / "missing-target")
            elif kind == "directory":
                name.mkdir()
            else:
                os.mkfifo(name)
            result = self.invoke(
                "--project", self.project, "--title", f"Unsafe {kind}", "--text", "No overwrite.")
            self.assertNotEqual(0, result.returncode)
            self.assertTrue(name.is_symlink() if kind == "symlink" else name.exists())
            self.assertFalse((ideas / f"unsafe-{kind}-2.md").exists())

    def test_invalid_requests_do_not_create_destinations_or_roots(self):
        before = {path.name for path in self.project.iterdir()}
        cases = [
            ("--project", self.project, "--text", "   "),
            ("--project", self.project, "--title", "   ", "--text", "body"),
            ("--project", self.project, "--vault", self.vault, "--text", "body"),
            ("--text", "body"),
            ("--project", self.vault / "missing", "--text", "body"),
        ]
        for args in cases:
            with self.subTest(args=args):
                result = self.invoke(*args)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual("", result.stdout)
        self.assertEqual(before, {path.name for path in self.project.iterdir()})
        self.assertFalse((self.vault / "missing").exists())

    def test_invalid_project_identity_does_not_create_ideas_directory(self):
        entry = self.project / "ProjectEntry.md"
        entry.write_text("---\nproject_id: Invalid_ID\n---\n", encoding="utf-8")
        result = self.invoke("--project", self.project, "--text", "body")
        self.assertNotEqual(0, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertFalse((self.project / "ideas").exists())

    def test_injected_write_and_publication_failures_clean_staging(self):
        ideas = self.project / "ideas"
        ideas.mkdir()
        existing = ideas / "preserve.md"
        existing.write_bytes(b"prior bytes")
        for syscall in ("write", "link"):
            with self.subTest(syscall=syscall):
                if syscall == "link":
                    real_link = os.link

                    def fail_after_existing_collision(source, destination, **kwargs):
                        if destination == "preserve.md":
                            return real_link(source, destination, **kwargs)
                        raise OSError(errno.EIO, "injected publication failure")

                    patcher = mock.patch(
                        "skills.scripts.kosmic_ideas.os.link",
                        side_effect=fail_after_existing_collision,
                    )
                    affected = "preserve-2.md"
                else:
                    patcher = mock.patch(
                        "skills.scripts.kosmic_ideas.os.write",
                        side_effect=OSError(errno.EIO, "injected write failure"),
                    )
                    affected = "preserve.md"
                with patcher, self.assertRaises(OSError) as caught:
                    kosmic_ideas.capture_idea(
                        "new body", project_root=self.project, title="Preserve")
                self.assertIn(affected, str(caught.exception))
                self.assertEqual(b"prior bytes", existing.read_bytes())
                self.assertEqual({"preserve.md"}, {item.name for item in ideas.iterdir()})

    def test_late_directory_sync_failure_reports_published_path(self):
        ideas = self.project / "ideas"
        ideas.mkdir()
        real_fsync = os.fsync
        calls = 0

        def fail_directory_sync(descriptor):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError(errno.EIO, "injected directory sync failure")
            return real_fsync(descriptor)

        with mock.patch("skills.scripts.kosmic_ideas.os.fsync", side_effect=fail_directory_sync):
            with self.assertRaises(OSError) as caught:
                kosmic_ideas.capture_idea(
                    "saved body", project_root=self.project, title="Late failure")
        path = ideas / "late-failure.md"
        self.assertIn(str(path), str(caught.exception))
        self.assertTrue(path.is_file())
        self.assertEqual({"late-failure.md"}, {item.name for item in ideas.iterdir()})

    def test_invalid_utf8_text_refuses_without_creating_destination(self):
        with self.assertRaises(kosmic_ideas.IdeaError):
            kosmic_ideas.capture_idea(chr(0xD800), project_root=self.project)
        self.assertFalse((self.project / "ideas").exists())


if __name__ == "__main__":
    unittest.main()
