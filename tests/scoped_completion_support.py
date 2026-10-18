"""Small real-CLI fixture shared by the record-scope regression scenarios."""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "skills/scripts/kosmic_project_skills.py"
MATH_INDEX = "# Math Derivations\n\n| Derivation | Status | Result summary |\n|------------|--------|----------------|\n"

FIXTURE_COMMIT_ENV = {
    "GIT_AUTHOR_DATE": "2026-10-18T12:00:00",
    "GIT_COMMITTER_DATE": "2026-10-18T12:00:00",
    "GIT_AUTHOR_NAME": "fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


def commit_baseline(worktree: Path, message: str = "fixture baseline") -> str:
    """Commit every current path so later diffs isolate the declared scope."""
    environment = {**os.environ, **FIXTURE_COMMIT_ENV}
    subprocess.run(["git", "add", "-A"], cwd=str(worktree), check=True,
                   capture_output=True, env=environment)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=str(worktree), check=True,
                   capture_output=True, env=environment)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(worktree), check=True,
                          capture_output=True, text=True, env=environment).stdout.strip()


def frontmatter(fields: dict[str, object]) -> str:
    """Render record frontmatter as single-line JSON-compatible flow YAML."""
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {json.dumps(value)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def write_document(path: Path, fields: dict[str, object], title: str,
                   body: str = "") -> Path:
    """Rewrite a spec record document with the given frontmatter fields."""
    text = frontmatter(fields) + f"\n# {title}\n"
    if body:
        text += f"\n{body}\n"
    path.write_text(text, encoding="utf-8")
    return path


class ScopedProjectCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.project = self.root / "vault/Projects/demo"
        self.project.mkdir(parents=True)
        (self.project / "ProjectEntry.md").write_text(
            "---\nproject_id: scope-demo\nworking_state: working-tree\n---\n# Demo\n"
        )
        (self.project / "notes").mkdir()
        (self.project / "notes/index.md").write_text(
            '---\nokf_version: "0.2"\n---\n# Knowledge\n'
        )
        (self.project / "mathdocs").mkdir()
        (self.project / "mathdocs/index.md").write_text(MATH_INDEX)
        (self.project / "specs/quick-tasks").mkdir(parents=True)
        (self.project / "specs/INDEX.md").write_text("# Specs\n")
        (self.project / "specs/quick-tasks/fixture-task.md").write_text(
            "---\nproject_id: scope-demo\nsubproject_id: null\nrecord_kind: quick-task\n"
            "local_id: fixture-task\nstatus: approved\n---\n# Fixture\n"
            "## Acceptance Criteria\n- [ ] Fixture behavior verified\n"
        )
        (self.root / ".gitignore").write_text(".tmp/\n")
        subprocess.run(["git", "init", "-q", str(self.root)], check=True,
                       capture_output=True)

    def tearDown(self):
        self.temporary.cleanup()

    def run_cli(self, *arguments):
        return subprocess.run([sys.executable, str(CLI), *map(str, arguments)],
                              cwd=self.root, text=True, capture_output=True)

    def note(self, name, body="# Knowledge\n\nA documented convention.\n", metadata=""):
        path = self.project / "notes" / name
        path.write_text("---\ntype: reference\nstatus: stable\naudience: both\n"
                        "artifact_role: knowledge\n" + metadata + "---\n" + body)
        return path

    def item(self, metadata="consumer_interface_change: false\n"):
        path = self.project / "specs/quick-tasks/change.md"
        path.write_text(
            "---\nproject_id: scope-demo\nsubproject_id: null\n"
            "record_kind: quick-task\nlocal_id: change\nstatus: approved\n"
            + metadata + "---\n# Change\n"
        )
        return path
