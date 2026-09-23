from __future__ import annotations
from datetime import datetime, timedelta, timezone

import hashlib
import json
import tempfile
import os
import unittest
import subprocess
import sys
from pathlib import Path

from skills.scripts.kosmic_routines import (
    RoutineError,
    RoutineQuery,
    build_routine_inventory,
    detect_publication_siblings,
    publish_tree,
    query_routines,
    recover_publication_siblings,
)


class RoutineRegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.source = self.repo / "skills" / "scripts"
        self.library = self.repo / "vault" / "Skills"
        self.tests = self.repo / "tests"
        self.source.mkdir(parents=True)
        self.library.mkdir(parents=True)
        (self.library / "kosmic").mkdir()
        (self.library / "kosmic" / "SKILL.md").write_text(
            "---\nid: kosmic\nmaintainers: [kosmic-maintainers]\n---\n# Kosmic\n",
            encoding="utf-8",
        )
        self.tests.mkdir()
        (self.tests / "test_ops.py").write_text("def test_publish(): pass\n", encoding="utf-8")
        self.ops = self.source / "ops.py"
        self.declaration = (
            "def publish(staged, destination, managed_paths=None):\n    return destination\n\n"
            "KOSMIC_ROUTINES = [{\n"
            "  'id': 'kosmic/publish', 'symbol': 'publish', 'summary': 'Publish staged files atomically',\n"
            "  'owner': 'kosmic-maintainers', 'deterministic': True, 'offline': True,\n"
            "  'side_effects': ['filesystem'], 'tests': ['tests/test_ops.py::test_publish'],\n"
            "  'callers': ['python:client:run'], 'procedures': []\n"
            "}]\n"
        )
        self.ops.write_text(self.declaration, encoding="utf-8")
        (self.source / "client.py").write_text("def run(): pass\n", encoding="utf-8")

    def test_builds_normalized_inventory_without_importing_source(self) -> None:
        inventory = build_routine_inventory(self.repo, self.source, self.library)
        self.assertEqual(inventory["schema"], "kosmic.routines/v1")
        self.assertEqual([row["id"] for row in inventory["routines"]], ["kosmic/publish"])
        row = inventory["routines"][0]
        self.assertEqual(row["module"], "skills/scripts/ops.py")
        self.assertEqual(row["domain"], "kosmic")
        self.assertEqual(len(row["routine_sha256"]), 64)

    def test_query_filters_domain_and_ties_deterministically(self) -> None:
        inventory = build_routine_inventory(self.repo, self.source, self.library)
        rows = query_routines(inventory, RoutineQuery(domain="kosmic"))
        self.assertEqual([row["id"] for row in rows], ["kosmic/publish"])
        self.assertEqual(query_routines(inventory, RoutineQuery(query="absent")), ())

    def test_dynamic_declaration_fails_closed(self) -> None:
        (self.source / "ops.py").write_text(
            "def publish(): pass\nKOSMIC_ROUTINES = make_declarations()\n",
            encoding="utf-8",
        )
        with self.assertRaisesRegex(RoutineError, "must be literal"):
            build_routine_inventory(self.repo, self.source, self.library)

    def test_declaration_boundaries_fail_closed(self) -> None:
        mutations = {
            "invalid routine id": self.declaration.replace("kosmic/publish", "Kosmic/Bad Id"),
            "missing routine symbol": self.declaration.replace("'symbol': 'publish'", "'symbol': 'missing'"),
            "ambiguous routine symbol": "def publish(): pass\n" + self.declaration,
            "missing routine test": self.declaration.replace("tests/test_ops.py::test_publish", "tests/test_ops.py::missing"),
            "unresolvable callers": self.declaration.replace("python:client:run", "python:client:missing"),
            "invalid side effect": self.declaration.replace("['filesystem']", "['network']"),
            "invalid owner": self.declaration.replace("kosmic-maintainers", "intruder"),
            "non-reciprocal procedure": self.declaration.replace("'procedures': []", "'procedures': ['topic:kosmic/development/missing']"),
        }
        for message, source in mutations.items():
            with self.subTest(message=message):
                self.ops.write_text(source, encoding="utf-8")
                with self.assertRaises(RoutineError):
                    build_routine_inventory(self.repo, self.source, self.library)
        self.ops.write_text(self.declaration, encoding="utf-8")
        (self.source / "duplicate.py").write_text(self.declaration, encoding="utf-8")
        with self.assertRaisesRegex(RoutineError, "duplicate routine id"):
            build_routine_inventory(self.repo, self.source, self.library)

    def test_query_supports_exact_selectors_and_stable_ties(self) -> None:
        inventory = build_routine_inventory(self.repo, self.source, self.library)
        row = inventory["routines"][0]
        selectors = {
            "id": row["id"], "domain": row["domain"], "module": row["module"],
            "symbol": row["symbol"], "owner": row["owner"],
            "caller": row["callers"][0],
        }
        for field, value in selectors.items():
            with self.subTest(field=field):
                self.assertEqual(
                    query_routines(inventory, RoutineQuery(**{field: value}))[0]["id"],
                    "kosmic/publish",
                )
        tied = {"routines": [
            {"id": "z/two", "summary": "atomic publish"},
            {"id": "a/one", "summary": "atomic publish"},
        ]}
        self.assertEqual(
            [row["id"] for row in query_routines(tied, RoutineQuery(query="atomic"))],
            ["a/one", "z/two"],
        )
        with self.assertRaisesRegex(RoutineError, "at least one selector"):
            query_routines(inventory, RoutineQuery())

    def test_query_cli_emits_pinned_json_no_match_and_rejects_stale_bytes(self) -> None:
        inventory = build_routine_inventory(self.repo, self.source, self.library)
        meta = self.library / ".kosmic"
        meta.mkdir()
        inventory_path = meta / "routines.json"
        inventory_path.write_text(
            json.dumps(inventory, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        manifest = {"routine_inventory_sha256": hashlib.sha256(inventory_path.read_bytes()).hexdigest()}
        (meta / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        cli = Path(__file__).resolve().parents[1] / "skills" / "scripts" / "kosmic_project_skills.py"
        command = [
            sys.executable, str(cli), "query-routines", "--vault", str(self.repo / "vault"),
            "--source-root", str(self.source), "--format", "json",
        ]
        found = subprocess.run(
            [*command, "--id", "kosmic/publish"], capture_output=True, text=True
        )
        self.assertEqual(found.returncode, 0, found.stderr)
        payload = json.loads(found.stdout)
        self.assertEqual(payload["inventory_sha256"], manifest["routine_inventory_sha256"])
        self.assertRegex(payload["manifest_sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(payload["routines"][0]["id"], "kosmic/publish")
        missing = subprocess.run(
            [*command, "--id", "kosmic/missing"], capture_output=True, text=True
        )
        self.assertEqual(missing.returncode, 2)
        self.assertIn("NO_ROUTINE_MATCH", missing.stderr)
        inventory_path.write_text(inventory_path.read_text(encoding="utf-8") + " ", encoding="utf-8")
        stale = subprocess.run(
            [*command, "--id", "kosmic/publish"], capture_output=True, text=True
        )
        self.assertEqual(stale.returncode, 2)
        self.assertIn("stale routine inventory hash", stale.stderr)

    def test_publish_tree_restores_destination_after_failure(self) -> None:
        staged = self.repo / "staged"
        destination = self.repo / "published"
        staged.mkdir()
        destination.mkdir()
        (staged / "value").write_text("new", encoding="utf-8")
        (destination / "value").write_text("old", encoding="utf-8")
        prior = os.environ.get("KOSMIC_FAIL_STAGE")
        os.environ["KOSMIC_FAIL_STAGE"] = "after-backup"
        try:
            with self.assertRaisesRegex(OSError, "injected publication failure"):
                publish_tree(staged, destination)
        finally:
            if prior is None:
                os.environ.pop("KOSMIC_FAIL_STAGE", None)
            else:
                os.environ["KOSMIC_FAIL_STAGE"] = prior
        self.assertEqual((destination / "value").read_text(encoding="utf-8"), "old")

    def test_publish_tree_managed_paths_support_nested_success_and_rollback(self) -> None:
        destination = self.repo / "managed"
        destination.mkdir()
        (destination / "nested").mkdir()
        (destination / "nested" / "value").write_text("old", encoding="utf-8")
        staged = self.repo / "managed-staged"
        (staged / "nested").mkdir(parents=True)
        (staged / "nested" / "value").write_text("new", encoding="utf-8")
        publish_tree(staged, destination, ["nested/value"])
        self.assertEqual((destination / "nested" / "value").read_text(encoding="utf-8"), "new")

        retry = self.repo / "managed-retry"
        (retry / "nested").mkdir(parents=True)
        (retry / "nested" / "value").write_text("candidate", encoding="utf-8")
        prior = os.environ.get("KOSMIC_FAIL_STAGE")
        os.environ["KOSMIC_FAIL_STAGE"] = "after-backup"
        try:
            with self.assertRaisesRegex(OSError, "injected publication failure"):
                publish_tree(retry, destination, ["nested/value"])
        finally:
            if prior is None:
                os.environ.pop("KOSMIC_FAIL_STAGE", None)
            else:
                os.environ["KOSMIC_FAIL_STAGE"] = prior
        self.assertEqual((destination / "nested" / "value").read_text(encoding="utf-8"), "new")
        self.assertFalse(any(destination.parent.glob(".kosmic-publish-backup-*")))

    def test_detects_and_recovers_expired_crashed_publication(self) -> None:
        staged = self.repo / "crash-staged"
        destination = self.repo / "crash-published"
        staged.mkdir()
        destination.mkdir()
        (staged / "value").write_text("new", encoding="utf-8")
        (destination / "value").write_text("old", encoding="utf-8")
        environment = {**os.environ, "KOSMIC_FAIL_STAGE": "crash-after-backup"}
        crashed = subprocess.run(
            [
                sys.executable,
                "-c",
                "from pathlib import Path; from skills.scripts.kosmic_routines import publish_tree; "
                "publish_tree(Path(__import__('sys').argv[1]), Path(__import__('sys').argv[2]))",
                str(staged),
                str(destination),
            ],
            cwd=Path(__file__).resolve().parents[1],
            env=environment,
            check=False,
        )
        self.assertEqual(crashed.returncode, 86)
        self.assertFalse(destination.exists())
        now = datetime.now(timezone.utc)
        states = detect_publication_siblings(destination, now=now)
        self.assertEqual((len(states), states[0].state), (1, "grace"))
        marker_path = states[0].path / ".kosmic-publish-marker.json"
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        marker["grace_expires_at"] = (now - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        marker_path.write_text(json.dumps(marker), encoding="utf-8")
        foreign = destination.parent / ".kosmic-publish-backup-unrelated"
        foreign.mkdir()
        (foreign / "user.txt").write_text("keep", encoding="utf-8")

        recovered = recover_publication_siblings(destination, now=now)
        restored = [result for result in recovered if result.action == "restored"]
        self.assertEqual(len(restored), 1, recovered)
        self.assertEqual((destination / "value").read_text(encoding="utf-8"), "old")
        self.assertTrue(foreign.exists())
        foreign_state = [state for state in detect_publication_siblings(destination, now=now) if state.path == foreign]
        self.assertEqual(foreign_state[0].state, "ambiguous")

    def test_recovery_finishes_installed_tree_and_preserves_ambiguous_managed_backup(self) -> None:
        destination = self.repo / "installed"
        destination.mkdir()
        (destination / "old").write_text("old", encoding="utf-8")
        staged = self.repo / "installed-stage"
        staged.mkdir()
        (staged / "new").write_text("new", encoding="utf-8")
        command = [sys.executable, "-c", "from pathlib import Path; from skills.scripts.kosmic_routines import publish_tree; publish_tree(Path(__import__('sys').argv[1]), Path(__import__('sys').argv[2]))", str(staged), str(destination)]
        crashed = subprocess.run(command, cwd=Path(__file__).resolve().parents[1], env={**os.environ, "KOSMIC_FAIL_STAGE": "crash-after-installed"}, check=False)
        self.assertEqual(crashed.returncode, 87)
        state = detect_publication_siblings(destination)[0]
        marker_path = state.path / ".kosmic-publish-marker.json"
        marker = json.loads(marker_path.read_text(encoding="utf-8"))
        now = datetime.now(timezone.utc)
        marker["grace_expires_at"] = (now - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        marker_path.write_text(json.dumps(marker), encoding="utf-8")
        self.assertEqual(recover_publication_siblings(destination, now=now)[0].action, "finished")
        self.assertEqual((destination / "new").read_text(encoding="utf-8"), "new")

        managed = self.repo / "managed-crash"
        (managed / "nested").mkdir(parents=True)
        (managed / "nested" / "value").write_text("old", encoding="utf-8")
        managed_stage = self.repo / "managed-crash-stage"
        (managed_stage / "nested").mkdir(parents=True)
        (managed_stage / "nested" / "value").write_text("new", encoding="utf-8")
        command[-2:] = [str(managed_stage), str(managed)]
        command[2] = "from pathlib import Path; from skills.scripts.kosmic_routines import publish_tree; publish_tree(Path(__import__('sys').argv[1]), Path(__import__('sys').argv[2]), ['nested/value'])"
        crashed = subprocess.run(command, cwd=Path(__file__).resolve().parents[1], env={**os.environ, "KOSMIC_FAIL_STAGE": "crash-after-backup"}, check=False)
        self.assertEqual(crashed.returncode, 86)
        state = detect_publication_siblings(managed)[0]
        marker = json.loads((state.path / ".kosmic-publish-marker.json").read_text(encoding="utf-8"))
        marker["grace_expires_at"] = (now - timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        (state.path / ".kosmic-publish-marker.json").write_text(json.dumps(marker), encoding="utf-8")
        recovery = recover_publication_siblings(managed, now=now)[0]
        self.assertEqual((recovery.action, recovery.reason), ("report-only", "MANAGED_PATH_RECOVERY_AMBIGUOUS"))
        self.assertTrue((state.path / "nested" / "value").exists())
if __name__ == "__main__":
    unittest.main()
