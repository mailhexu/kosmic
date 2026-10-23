from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from skills.scripts import kosmic_specs
from skills.scripts.kosmic_specs import SpecCatalog, SpecError, create_spec, normalize_subproject_title

REPO_ROOT = Path(__file__).resolve().parents[1]
CLI = REPO_ROOT / "skills" / "scripts" / "kosmic_project_skills.py"


def project(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "ProjectEntry.md").write_text(
        "---\nproject_id: \"demo\"\n---\n\n# Demo\n", encoding="utf-8")
    return root


def status_table_rows(text: str) -> list[dict[str, str]]:
    """Semantic view of status-table rows: declared column name -> cell text."""
    rows: list[dict[str, str]] = []
    columns: list[str] | None = None
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            columns = None
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        lowered = [cell.casefold() for cell in cells]
        if "status" in lowered:
            columns = lowered
            continue
        if columns is not None:
            rows.append({name: cell for name, cell in zip(columns, cells) if name})
    return rows


class CreationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="kosmic-create-")
        self.addCleanup(self.tmp.cleanup)
        self.root = project(Path(self.tmp.name) / "Project")

    def test_normalization_keeps_ascii_and_falls_back(self) -> None:
        self.assertEqual(normalize_subproject_title("Wavefunction Export!"), "wavefunction-export")
        self.assertEqual(normalize_subproject_title("  Élan -- *Vital*  "), "elan-vital")
        self.assertEqual(normalize_subproject_title(" Frozen Desserts "), "frozen-desserts")
        self.assertEqual(normalize_subproject_title("   "), "subproject")
        self.assertEqual(normalize_subproject_title("!!!"), "subproject")

    def test_long_titles_stay_within_64_characters_with_suffix(self) -> None:
        result = create_spec(self.root, "prd", "a" * 80)
        self.assertLessEqual(len(result["subproject_id"]), 64)
        self.assertTrue(SpecCatalog(self.root).subprojects[result["subproject_id"]])
        second = create_spec(self.root, "prd", "a" * 80)
        self.assertLessEqual(len(second["subproject_id"]), 64)
        suffix = "-2"
        self.assertTrue(second["subproject_id"].endswith(suffix))
        self.assertEqual(second["subproject_id"][:-len(suffix)], result["subproject_id"][:62])

    def test_reserved_identities_are_deterministic_and_collisions_suffix(self) -> None:
        first = create_spec(self.root, "prd", "Wavefunction Export")
        self.assertEqual(first["subproject_id"], "wavefunction-export")
        second = create_spec(self.root, "prd", "wavefunction   EXPORT")
        self.assertEqual(second["subproject_id"], "wavefunction-export-2")
        third = create_spec(self.root, "prd", "wavefunction-export")
        self.assertEqual(third["subproject_id"], "wavefunction-export-3")

    def test_concurrent_same_title_creations_get_distinct_owners(self) -> None:
        results: list[dict] = []
        errors: list[Exception] = []

        def worker() -> None:
            try:
                results.append(create_spec(self.root, "prd", "Parallel Dreams"))
            except Exception as error:  # pragma: no cover - recorded deliberately
                errors.append(error)

        threads = [threading.Thread(target=worker) for _ in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        owners = sorted(item["subproject_id"] for item in results)
        self.assertEqual(len(set(owners)), 4)
        catalog = SpecCatalog(self.root)
        self.assertEqual(set(catalog.subprojects), set(owners))
        for owner in owners:
            catalog.resolve("prd", owner=owner, kind="prd")

    def test_interrupted_reservation_resumes_with_operation_id_only(self) -> None:
        real_stage = kosmic_specs._stage_bytes

        def interrupted(root, parts, data, *, exclusive=True):
            if parts[-1] == "prd.md":
                raise SpecError("SIMULATED", "interrupted during publication")
            return real_stage(root, parts, data, exclusive=exclusive)

        with mock.patch.object(kosmic_specs, "_stage_bytes", interrupted):
            with self.assertRaisesRegex(SpecError, "SIMULATED"):
                create_spec(self.root, "prd", "Recoverable Feature")
        owner_dir = self.root / "subprojects"
        owners = [item.name for item in owner_dir.iterdir()]
        self.assertEqual(len(owners), 1)
        owner = owners[0]
        self.assertFalse((owner_dir / owner / "specs" / "prd.md").exists())
        # The same title does NOT reuse the interrupted reservation.
        fresh = create_spec(self.root, "prd", "Recoverable Feature")
        self.assertEqual(fresh["subproject_id"], f"{owner}-2")
        op_files = list((self.root / ".kosmic" / "create-ops").glob("*.json"))
        original = [json.loads(path.read_text()) for path in op_files
                    if json.loads(path.read_text())["subproject_id"] == owner]
        self.assertEqual(len(original), 1)
        # Resume without the explicit operation id is refused.
        with self.assertRaisesRegex(SpecError, "RESUME_REQUIRED"):
            create_spec(self.root, "prd", "Recoverable Feature", resume=True)
        resumed = create_spec(self.root, "prd", "Recoverable Feature", resume=True,
                              operation_id=original[0]["operation_id"])
        self.assertEqual(resumed["subproject_id"], owner)
        self.assertTrue(resumed["resumed"])
        catalog = SpecCatalog(self.root)
        catalog.validate()
        prd = catalog.resolve("prd", owner=owner, kind="prd")
        self.assertEqual(prd.title, "Recoverable Feature")
        rows = [row for row in status_table_rows(
                    (owner_dir / owner / "specs" / "INDEX.md").read_text(encoding="utf-8"))
                if row.get("record") == "[Recoverable Feature](prd.md)"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "prd")
        self.assertEqual(rows[0]["status"], "draft")
        # Re-resuming a published reservation is refused; nothing is overwritten.
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "prd", "Recoverable Feature", resume=True,
                        operation_id=original[0]["operation_id"])
        self.assertEqual(json.loads((self.root / ".kosmic" / "create-ops" /
                                     f"{original[0]['operation_id']}.json").read_text())["status"],
                         "published")

    def test_resume_uses_recorded_inputs_without_session_handles(self) -> None:
        real_stage = kosmic_specs._stage_bytes

        def interrupted(root, parts, data, *, exclusive=True):
            if parts[-1] == "prd.md":
                raise SpecError("SIMULATED", "interrupted during publication")
            return real_stage(root, parts, data, exclusive=exclusive)

        with mock.patch.object(kosmic_specs, "_stage_bytes", interrupted):
            with self.assertRaisesRegex(SpecError, "SIMULATED"):
                create_spec(self.root, "prd", "Recorded Inputs")
        operation = next(json.loads(path.read_text()) for path
                         in (self.root / ".kosmic" / "create-ops").glob("*.json"))
        owner = operation["subproject_id"]
        operation_id = operation["operation_id"]
        self.assertEqual(operation["title"], "Recorded Inputs")
        self.assertNotIn("work_handle", operation)
        resumed = create_spec(self.root, "prd", "Different Title", resume=True,
                              operation_id=operation_id)
        self.assertEqual(resumed["title"], "Recorded Inputs")
        self.assertEqual(resumed["resumed"], True)
        self.assertNotIn("work_handle", resumed)
        prd = SpecCatalog(self.root).resolve("prd", owner=owner, kind="prd")
        self.assertEqual(prd.title, "Recorded Inputs")
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "prd", "Recorded Inputs", resume=True,
                        operation_id=operation_id)

    def test_empty_title_uses_public_fallback_identity(self) -> None:
        created = create_spec(self.root, "prd", "")
        self.assertEqual(created["subproject_id"], "subproject")
        self.assertEqual(created["title"], "Subproject")
        catalog = SpecCatalog(self.root)
        catalog.validate()
        prd = catalog.resolve("demo/subproject/prd/prd")
        self.assertEqual(prd.title, "Subproject")

    def test_special_file_at_operation_path_is_denied(self) -> None:
        import os as _os
        created = create_spec(self.root, "prd", "Pipe Guard")
        operation_id = created["operation_id"]
        owner = created["subproject_id"]
        import shutil
        shutil.rmtree(self.root / "subprojects" / owner)
        operations = self.root / ".kosmic" / "create-ops"
        (operations / f"{operation_id}.json").unlink()
        _os.mkfifo(operations / f"{operation_id}.json")
        # Existence is not leaked through the operation loader, but nothing blocks.
        with self.assertRaisesRegex(SpecError, "OPERATION_NOT_FOUND"):
            create_spec(self.root, "prd", "Pipe Guard", resume=True,
                        operation_id=operation_id)
        self.assertFalse((self.root / "subprojects" / owner).exists())

    def test_title_edit_keeps_owner_and_never_reuses_identity(self) -> None:
        created = create_spec(self.root, "prd", "Original Name")
        owner = created["subproject_id"]
        prd = SpecCatalog(self.root).resolve("prd", owner=owner, kind="prd")
        prd.path.write_text(
            "---\n" + "".join(
                f"{key}: {json.dumps(value)}\n" for key, value in prd.metadata.items()
                if key != "title") + "---\n\n# Renamed Display Title\n", encoding="utf-8")
        catalog = SpecCatalog(self.root)
        self.assertEqual(catalog.resolve("prd", owner=owner, kind="prd").title,
                         "Renamed Display Title")
        renamed = create_spec(self.root, "prd", "Renamed Display Title")
        self.assertNotEqual(renamed["subproject_id"], owner)
        self.assertTrue(renamed["subproject_id"].startswith("renamed-display-title"))

    def test_hierarchy_creation_is_owner_local_without_sessions(self) -> None:
        created = create_spec(self.root, "prd", "Feature Scope")
        owner = created["subproject_id"]
        architecture = create_spec(self.root, "architecture", "Feature Architecture",
                                   subproject=owner)
        self.assertEqual(architecture["local_id"], "architecture")
        self.assertNotIn("work_handle", architecture)
        epic = create_spec(self.root, "epic", "First Epic", subproject=owner,
                           parent="architecture")
        self.assertEqual(epic["local_id"], "001")
        story = create_spec(self.root, "story", "First Story", subproject=owner,
                            parent="001")
        self.assertEqual(story["local_id"], "001")
        second_epic = create_spec(self.root, "epic", "Second Epic", subproject=owner,
                                  parent="architecture")
        self.assertEqual(second_epic["local_id"], "002")
        catalog = SpecCatalog(self.root)
        catalog.validate()
        story_ref = catalog.resolve("001", owner=owner, kind="story")
        chain = [record.kind for record in catalog.ancestry(story_ref)]
        self.assertEqual(chain, ["epic", "architecture", "prd"])
        # Foreign parent is refused and creates nothing.
        other = create_spec(self.root, "prd", "Other Scope")
        with self.assertRaisesRegex(SpecError, "OWNER_MISMATCH|ANCESTRY_INVALID"):
            create_spec(self.root, "epic", "Foreign Epic", subproject=other["subproject_id"],
                        parent=f"demo/{owner}/architecture/architecture")
        with self.assertRaisesRegex(SpecError, "OWNER_REQUIRED"):
            create_spec(self.root, "architecture", "No Owner")

    def test_cli_architecture_creation_returns_native_paths_and_index_row(self) -> None:
        """Public CLI tracer: a non-PRD creation owns its operation, returns
        canonical Project-relative record/index paths and merges exactly one
        finish-compatible row while preserving all prior index content."""
        owner = create_spec(self.root, "prd", "Tracer Feature")["subproject_id"]
        index_path = self.root / "subprojects" / owner / "specs" / "INDEX.md"
        before = set(index_path.read_text(encoding="utf-8").splitlines())
        result = subprocess.run(
            [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
             "--kind", "architecture", "--subproject", owner,
             "--title", "Tracer Architecture"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        created = json.loads(result.stdout)
        self.assertTrue(created["operation_id"])
        self.assertEqual(created["record_path"], f"subprojects/{owner}/specs/architecture.md")
        self.assertEqual(created["index_path"], f"subprojects/{owner}/specs/INDEX.md")
        self.assertIn(f"subprojects/{owner}/specs/architecture.md", created["paths"])
        matching = [row for row in status_table_rows(index_path.read_text(encoding="utf-8"))
                    if row.get("record") == "[Tracer Architecture](architecture.md)"]
        self.assertEqual(len(matching), 1)
        self.assertEqual(matching[0]["kind"], "architecture")
        self.assertEqual(matching[0]["status"], "draft")
        after = set(index_path.read_text(encoding="utf-8").splitlines())
        self.assertEqual(before & after, before)

    def test_cli_resume_publishes_interrupted_architecture_once(self) -> None:
        """Recovery tracer: an interrupted non-PRD reservation replays through
        the public CLI to the same recorded identity and exactly one row; a
        published operation keeps refusing further resume."""
        real_stage = kosmic_specs._stage_bytes

        def interrupted(root, parts, data, *, exclusive=True):
            if parts[-1] == "architecture.md":
                raise SpecError("SIMULATED", "interrupted during publication")
            return real_stage(root, parts, data, exclusive=exclusive)

        owner = create_spec(self.root, "prd", "Recovery Feature")["subproject_id"]
        with mock.patch.object(kosmic_specs, "_stage_bytes", interrupted):
            with self.assertRaisesRegex(SpecError, "SIMULATED"):
                create_spec(self.root, "architecture", "Recovery Architecture",
                            subproject=owner)
        reservations = [json.loads(path.read_text()) for path
                        in (self.root / ".kosmic" / "create-ops").glob("*.json")
                        if json.loads(path.read_text())["kind"] == "architecture"]
        self.assertEqual(len(reservations), 1)
        operation_id = reservations[0]["operation_id"]
        record_path = self.root / "subprojects" / owner / "specs" / "architecture.md"
        self.assertFalse(record_path.exists())
        result = subprocess.run(
            [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
             "--kind", "architecture", "--subproject", owner,
             "--title", "Retyped Title", "--resume", "--operation-id", operation_id],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        resumed = json.loads(result.stdout)
        self.assertEqual(resumed["operation_id"], operation_id)
        self.assertTrue(resumed["resumed"])
        self.assertEqual(resumed["title"], "Recovery Architecture")
        self.assertEqual(resumed["record_path"], f"subprojects/{owner}/specs/architecture.md")
        self.assertEqual(resumed["index_path"], f"subprojects/{owner}/specs/INDEX.md")
        self.assertTrue(record_path.is_file())
        index_path = self.root / "subprojects" / owner / "specs" / "INDEX.md"
        rows = [row for row in status_table_rows(index_path.read_text(encoding="utf-8"))
                if row.get("record") == "[Recovery Architecture](architecture.md)"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "architecture")
        self.assertEqual(rows[0]["status"], "draft")
        self.assertEqual(
            json.loads((self.root / ".kosmic" / "create-ops" / f"{operation_id}.json")
                       .read_text(encoding="utf-8"))["status"], "published")
        # Published operations keep their refusal; nothing is republished.
        second = subprocess.run(
            [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
             "--kind", "architecture", "--subproject", owner,
             "--title", "Recovery Architecture", "--resume", "--operation-id", operation_id],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("RESERVATION_CONFLICT", second.stderr)

    def test_cli_resume_merges_unrelated_index_edits(self) -> None:
        """Recovery: an interrupted PRD whose index was already published and
        then edited resumes through the public CLI, merging only its row into
        the current index instead of replaying whole-index bytes."""
        real_store = kosmic_specs._store_operation

        def interrupted_store(root, operation, *, replace):
            if replace:
                raise SpecError("SIMULATED", "interrupted before publication marker")
            return real_store(root, operation, replace=replace)

        with mock.patch.object(kosmic_specs, "_store_operation", interrupted_store):
            with self.assertRaisesRegex(SpecError, "SIMULATED"):
                create_spec(self.root, "prd", "Editable Recovery")
        operation = json.loads(
            next((self.root / ".kosmic" / "create-ops").glob("*.json")).read_text())
        self.assertEqual(operation["status"], "reserved")
        owner = operation["subproject_id"]
        index_path = self.root / "subprojects" / owner / "specs" / "INDEX.md"
        index_path.write_text(
            index_path.read_text(encoding="utf-8") + "\nUnrelated editorial note.\n",
            encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
             "--kind", "prd", "--title", "Retyped Bootstrap",
             "--resume", "--operation-id", operation["operation_id"]],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        resumed = json.loads(result.stdout)
        self.assertEqual(resumed["title"], "Editable Recovery")
        self.assertTrue(resumed["resumed"])
        text = index_path.read_text(encoding="utf-8")
        self.assertIn("Unrelated editorial note.", text)
        rows = [row for row in status_table_rows(text)
                if row.get("record") == "[Editable Recovery](prd.md)"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "prd")
        self.assertEqual(rows[0]["status"], "draft")
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "prd", "Editable Recovery", resume=True,
                        operation_id=operation["operation_id"])

    def test_cli_resume_replays_literal_historical_prd_operation(self) -> None:
        """AC-006: a literal pre-change reserved PRD operation (no documents,
        local_id or path fields) resumes through the public CLI: recorded
        identity and owner are retained, the existing immutable record bytes
        and the historical bullet index with unrelated prose are preserved
        without duplicate row or bulk conversion, and the historical
        operation file gains only the published marker."""
        owner = "historic-owner"
        title = "Historical Feature"
        specs_dir = self.root / "subprojects" / owner / "specs"
        specs_dir.mkdir(parents=True)
        # Literal pre-change record bytes captured from pinned baseline
        # 216b709: an independent oracle that does not track the current
        # template, so future historical-template regressions surface here.
        entry_path = self.root / "subprojects" / owner / "SubprojectEntry.md"
        entry_path.write_text(
            '---\n'
            'schema: "kosmic.subproject/1"\n'
            'project_id: "demo"\n'
            'subproject_id: "historic-owner"\n'
            'title: "Historical Feature"\n'
            'linked_prd: "specs/prd.md"\n'
            'status: "draft"\n'
            '---\n'
            '\n'
            '# Historical Feature\n', encoding="utf-8")
        prd_path = specs_dir / "prd.md"
        prd_path.write_text(
            '---\n'
            'project_id: "demo"\n'
            'subproject_id: "historic-owner"\n'
            'status: "draft"\n'
            'record_kind: "prd"\n'
            'local_id: "prd"\n'
            '---\n'
            '\n'
            '# Historical Feature\n'
            '\n'
            '## Purpose\n'
            '\n'
            '(draft)\n', encoding="utf-8")
        index_path = specs_dir / "INDEX.md"
        index_text = ("# Historical Feature Specs\n\n- [PRD](prd.md)\n\n"
                      "Unrelated historical prose.\n")
        index_path.write_text(index_text, encoding="utf-8")
        operation_id = "0123456789abcdef0123456789abcdef"
        legacy_operation = {
            "operation_id": operation_id,
            "project_id": "demo",
            "kind": "prd",
            "title": title,
            "subproject_id": owner,
            "status": "reserved",
        }
        operations = self.root / ".kosmic" / "create-ops"
        operations.mkdir(parents=True)
        operation_path = operations / f"{operation_id}.json"
        operation_path.write_text(
            json.dumps(legacy_operation, sort_keys=True, indent=2) + "\n",
            encoding="utf-8")
        entry_before = (self.root / "subprojects" / owner / "SubprojectEntry.md").read_bytes()
        prd_before = (specs_dir / "prd.md").read_bytes()
        result = subprocess.run(
            [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
             "--kind", "prd", "--title", "Retyped Bootstrap",
             "--resume", "--operation-id", operation_id],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        resumed = json.loads(result.stdout)
        self.assertEqual(resumed["operation_id"], operation_id)
        self.assertTrue(resumed["resumed"])
        self.assertEqual(resumed["subproject_id"], owner)
        self.assertEqual(resumed["title"], title)
        self.assertEqual(resumed["record_path"], f"subprojects/{owner}/specs/prd.md")
        self.assertEqual(resumed["index_path"], f"subprojects/{owner}/specs/INDEX.md")
        self.assertEqual(resumed["paths"]["subprojects/historic-owner/specs/INDEX.md"],
                         ["subprojects", owner, "specs", "INDEX.md"])
        # Existing immutable bytes and the historical index are preserved
        # verbatim: no duplicate row, no bulk conversion, no prose loss.
        self.assertEqual(
            (self.root / "subprojects" / owner / "SubprojectEntry.md").read_bytes(),
            entry_before)
        self.assertEqual((specs_dir / "prd.md").read_bytes(), prd_before)
        self.assertEqual(index_path.read_text(encoding="utf-8"), index_text)
        after = json.loads(operation_path.read_text(encoding="utf-8"))
        self.assertEqual(set(after), set(legacy_operation))
        self.assertEqual(after["status"], "published")
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "prd", title, resume=True,
                        operation_id=operation_id)

    def test_legacy_index_content_is_preserved_and_conflicts_refused(self) -> None:
        owner = create_spec(self.root, "prd", "Legacy Owner")["subproject_id"]
        index_path = self.root / "subprojects" / owner / "specs" / "INDEX.md"
        index_path.write_text(
            "# Legacy Specs\n\n- [PRD](prd.md)\n\n## Notes\n\nKeep this section.\n",
            encoding="utf-8")
        create_spec(self.root, "architecture", "Legacy Neighbor", subproject=owner)
        text = index_path.read_text(encoding="utf-8")
        self.assertIn("# Legacy Specs\n", text)
        self.assertIn("- [PRD](prd.md)\n", text)
        self.assertIn("Keep this section.\n", text)
        rows = [row for row in status_table_rows(text)
                if row.get("record") == "[Legacy Neighbor](architecture.md)"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "architecture")
        self.assertEqual(rows[0]["status"], "draft")
        # A conflicting non-table entry for the same canonical link is
        # refused instead of gaining a duplicate row or overwriting it.
        index_path.write_text(text + "- [Someone Else](epics/epic-001.md)\n",
                              encoding="utf-8")
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "epic", "Clashing Epic", subproject=owner,
                        parent="architecture")
        conflicted = index_path.read_text(encoding="utf-8")
        self.assertIn("- [Someone Else](epics/epic-001.md)", conflicted)
        self.assertEqual([row for row in status_table_rows(conflicted)
                          if row.get("record") == "[Clashing Epic](epics/epic-001.md)"],
                         [])

    def test_resume_refuses_changed_record_bytes(self) -> None:
        real_stage = kosmic_specs._stage_bytes

        def interrupted(root, parts, data, *, exclusive=True):
            if parts[-1] == "architecture.md":
                raise SpecError("SIMULATED", "interrupted during publication")
            return real_stage(root, parts, data, exclusive=exclusive)

        owner = create_spec(self.root, "prd", "Drift Owner")["subproject_id"]
        with mock.patch.object(kosmic_specs, "_stage_bytes", interrupted):
            with self.assertRaisesRegex(SpecError, "SIMULATED"):
                create_spec(self.root, "architecture", "Drifted Draft",
                            subproject=owner)
        operation = next(json.loads(path.read_text()) for path
                         in (self.root / ".kosmic" / "create-ops").glob("*.json")
                         if json.loads(path.read_text())["kind"] == "architecture")
        record_path = self.root / "subprojects" / owner / "specs" / "architecture.md"
        reserved_text = operation["documents"][
            f"subprojects/{owner}/specs/architecture.md"]
        record_path.write_text(reserved_text + "\nForeign editorial drift.\n",
                               encoding="utf-8")
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "architecture", "Drifted Draft", resume=True,
                        subproject=owner, operation_id=operation["operation_id"])
        self.assertEqual(record_path.read_text(encoding="utf-8"),
                         reserved_text + "\nForeign editorial drift.\n")
        self.assertEqual(
            json.loads((self.root / ".kosmic" / "create-ops" /
                        f"{operation['operation_id']}.json").read_text())["status"],
            "reserved")

    def test_symlinked_record_or_index_targets_are_refused(self) -> None:
        owner = create_spec(self.root, "prd", "Link Guard")["subproject_id"]
        outside = Path(self.tmp.name) / "outside-index.md"
        outside.write_text("do not touch\n", encoding="utf-8")
        record_path = self.root / "subprojects" / owner / "specs" / "architecture.md"
        record_path.symlink_to(outside)
        # Catalog admission owns record-path reads and keeps its established
        # no-follow SCOPE_DENIED precedence over creation staging.
        with self.assertRaisesRegex(SpecError, "SCOPE_DENIED"):
            create_spec(self.root, "architecture", "Linked Draft", subproject=owner)
        self.assertTrue(record_path.is_symlink())
        record_path.unlink()
        index_path = self.root / "subprojects" / owner / "specs" / "INDEX.md"
        index_path.unlink()
        index_path.symlink_to(outside)
        with self.assertRaisesRegex(SpecError, "SCOPE_DENIED"):
            create_spec(self.root, "architecture", "Linked Draft", subproject=owner)
        self.assertTrue(index_path.is_symlink())
        self.assertEqual(outside.read_text(encoding="utf-8"), "do not touch\n")

    def test_concurrent_creations_preserve_each_others_rows(self) -> None:
        owner = create_spec(self.root, "prd", "Parallel Rows")["subproject_id"]
        results: list[dict] = []
        errors: list[Exception] = []

        def worker(kind: str, title: str) -> None:
            try:
                results.append(create_spec(self.root, kind, title, subproject=owner))
            except Exception as error:  # pragma: no cover - recorded deliberately
                errors.append(error)

        threads = [
            threading.Thread(target=worker,
                             args=("architecture", "Parallel Architecture")),
            threading.Thread(target=worker,
                             args=("quick-task", "Parallel Task")),
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        text = (self.root / "subprojects" / owner / "specs" / "INDEX.md").read_text(
            encoding="utf-8")
        records = {row.get("record") for row in status_table_rows(text)}
        self.assertTrue({"[Parallel Architecture](architecture.md)",
                         "[Parallel Task](quick-tasks/parallel-task.md)",
                         "[Parallel Rows](prd.md)"} <= records)
        SpecCatalog(self.root).validate()

    def test_new_creation_refuses_matching_bullet_entry(self) -> None:
        """The historical bullet exemption belongs to legacy operations only:
        a new creation whose only index entry is a non-table match conflicts
        instead of succeeding without a canonical row."""
        owner = create_spec(self.root, "prd", "Bullet Guard")["subproject_id"]
        index_path = self.root / "subprojects" / owner / "specs" / "INDEX.md"
        index_path.write_text(
            "# Bullet Guard Specs\n\n- [Same Title](architecture.md)\n",
            encoding="utf-8")
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "architecture", "Same Title", subproject=owner)
        text = index_path.read_text(encoding="utf-8")
        self.assertEqual(text, "# Bullet Guard Specs\n\n- [Same Title](architecture.md)\n")
        self.assertEqual(status_table_rows(text), [])

    def test_pending_reservation_holds_sequential_identity(self) -> None:
        real_stage = kosmic_specs._stage_bytes

        def interrupted(root, parts, data, *, exclusive=True):
            if parts[-1] == "epic-001.md":
                raise SpecError("SIMULATED", "interrupted during publication")
            return real_stage(root, parts, data, exclusive=exclusive)

        owner = create_spec(self.root, "prd", "Pending Owner")["subproject_id"]
        create_spec(self.root, "architecture", "Pending Architecture",
                    subproject=owner)
        with mock.patch.object(kosmic_specs, "_stage_bytes", interrupted):
            with self.assertRaisesRegex(SpecError, "SIMULATED"):
                create_spec(self.root, "epic", "Pending Epic", subproject=owner,
                            parent="architecture")
        # The pending reservation holds epic 001 under the creation lock; the
        # next sequential epic allocates the next free identity instead of
        # reusing the reserved slot.
        second = create_spec(self.root, "epic", "Second Epic", subproject=owner,
                             parent="architecture")
        self.assertEqual(second["local_id"], "002")
        operation = next(json.loads(path.read_text()) for path
                         in (self.root / ".kosmic" / "create-ops").glob("*.json")
                         if json.loads(path.read_text()).get("kind") == "epic"
                         and json.loads(path.read_text()).get("status") == "reserved")
        resumed = create_spec(self.root, "epic", "Retyped", resume=True,
                              subproject=owner, operation_id=operation["operation_id"])
        self.assertEqual(resumed["local_id"], "001")
        self.assertEqual(resumed["title"], "Pending Epic")
        catalog = SpecCatalog(self.root)
        catalog.validate()
        self.assertEqual(catalog.resolve("001", owner=owner, kind="epic").title,
                         "Pending Epic")
        self.assertEqual(catalog.resolve("002", owner=owner, kind="epic").title,
                         "Second Epic")

    def test_fresh_creation_refuses_pending_fixed_identity(self) -> None:
        real_stage = kosmic_specs._stage_bytes

        def interrupted(root, parts, data, *, exclusive=True):
            if parts[-1] == "architecture.md":
                raise SpecError("SIMULATED", "interrupted during publication")
            return real_stage(root, parts, data, exclusive=exclusive)

        owner = create_spec(self.root, "prd", "Fixed Owner")["subproject_id"]
        with mock.patch.object(kosmic_specs, "_stage_bytes", interrupted):
            with self.assertRaisesRegex(SpecError, "SIMULATED"):
                create_spec(self.root, "architecture", "Reserved Architecture",
                            subproject=owner)
        # A reserved fixed identity refuses a fresh same-kind duplicate until
        # the owning operation resumes or is explicitly reconciled.
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "architecture", "Different Title",
                        subproject=owner)
        self.assertFalse(
            (self.root / "subprojects" / owner / "specs" / "architecture.md").exists())

    def test_index_replace_refuses_external_divergence(self) -> None:
        owner = create_spec(self.root, "prd", "Divergence Owner")["subproject_id"]
        index_path = self.root / "subprojects" / owner / "specs" / "INDEX.md"
        real_replace = kosmic_specs._replace_regular_bytes

        def racing_replace(root, parts, data, **kwargs):
            # Narrow race injection at ensure-row's publication point: an
            # external edit lands after the index read, before the replace.
            target = root.joinpath(*parts)
            target.write_text(target.read_text(encoding="utf-8")
                              + "External editor line.\n", encoding="utf-8")
            return real_replace(root, parts, data, **kwargs)

        with mock.patch.object(kosmic_specs, "_replace_regular_bytes", racing_replace):
            with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
                create_spec(self.root, "architecture", "Diverged Draft",
                            subproject=owner)
        text = index_path.read_text(encoding="utf-8")
        self.assertIn("External editor line.\n", text)
        self.assertNotIn("[Diverged Draft](architecture.md)", text)

    def test_resume_refuses_altered_index_path_escape(self) -> None:
        """Stored output paths are not publication targets: a reserved op
        whose index_parts leave the Project is refused before any staging
        and outside bytes are preserved."""
        created = create_spec(self.root, "quick-task", "Containment Task")
        operation_id = created["operation_id"]
        outside = Path(self.tmp.name) / "outside-project-index.md"
        outside.write_text("outside\n", encoding="utf-8")
        op_path = self.root / ".kosmic" / "create-ops" / f"{operation_id}.json"
        operation = json.loads(op_path.read_text(encoding="utf-8"))
        operation["status"] = "reserved"
        operation["index_parts"] = ["..", "outside-project-index.md"]
        op_path.write_text(json.dumps(operation, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
             "--kind", "quick-task", "--title", "Containment Task",
             "--resume", "--operation-id", operation_id],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RESERVATION_CONFLICT", result.stderr)
        self.assertEqual(outside.read_text(encoding="utf-8"), "outside\n")

    def test_resume_refuses_noncanonical_document_targets(self) -> None:
        """Stored documents keys are publication targets: traversal escapes
        and document sets that do not match the recorded identity's canonical
        outputs are refused before any staging."""
        owner = create_spec(self.root, "prd", "Doc Guard")["subproject_id"]
        created = create_spec(self.root, "architecture", "Doc Guard Draft",
                              subproject=owner)
        operation_id = created["operation_id"]
        op_path = self.root / ".kosmic" / "create-ops" / f"{operation_id}.json"
        operation = json.loads(op_path.read_text(encoding="utf-8"))
        record_text = operation["documents"][
            f"subprojects/{owner}/specs/architecture.md"]
        outside = Path(self.tmp.name) / "escaped-record.md"
        operation["status"] = "reserved"
        operation["documents"] = {
            f"subprojects/{owner}/specs/../../escaped-record.md": record_text,
        }
        op_path.write_text(json.dumps(operation, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
             "--kind", "architecture", "--subproject", owner,
             "--title", "Doc Guard Draft", "--resume", "--operation-id", operation_id],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RESERVATION_CONFLICT", result.stderr)
        self.assertFalse(outside.exists())
        # An inside-but-noncanonical document set is likewise refused.
        operation["documents"] = {
            f"subprojects/{owner}/specs/architecture.md": record_text,
            f"subprojects/{owner}/specs/extra.md": record_text,
        }
        op_path.write_text(json.dumps(operation, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
             "--kind", "architecture", "--subproject", owner,
             "--title", "Doc Guard Draft", "--resume", "--operation-id", operation_id],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(
            (self.root / "subprojects" / owner / "specs" / "extra.md").exists())

    def test_resume_refuses_identity_mismatch(self) -> None:
        """A reserved op must match the live Project identity and the exact
        requested operation id; refused resumes never rewrite the stored
        operation state."""
        created = create_spec(self.root, "quick-task", "Identity Guard")
        operation_id = created["operation_id"]
        op_path = self.root / ".kosmic" / "create-ops" / f"{operation_id}.json"

        def resume() -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, str(CLI), "spec-create", "--project", str(self.root),
                 "--kind", "quick-task", "--title", "Identity Guard",
                 "--resume", "--operation-id", operation_id],
                cwd=REPO_ROOT, capture_output=True, text=True)

        operation = json.loads(op_path.read_text(encoding="utf-8"))
        operation["status"] = "reserved"
        operation["project_id"] = "other"
        op_path.write_text(json.dumps(operation, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
        result = resume()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RESERVATION_CONFLICT", result.stderr)
        self.assertEqual(
            json.loads(op_path.read_text(encoding="utf-8"))["project_id"], "other")
        # A payload whose operation id disagrees with the requested file is
        # refused the same way.
        operation["project_id"] = "demo"
        operation["operation_id"] = "f" * 32
        op_path.write_text(json.dumps(operation, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
        result = resume()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("RESERVATION_CONFLICT", result.stderr)
        self.assertEqual(
            json.loads(op_path.read_text(encoding="utf-8"))["status"], "reserved")

    def test_quick_tasks_are_independent_and_never_create_a_prd(self) -> None:
        shared = create_spec(self.root, "quick-task", "Repair Router")
        self.assertIsNone(shared["subproject_id"])
        self.assertTrue(shared["operation_id"])
        self.assertEqual(shared["record_path"], "specs/quick-tasks/repair-router.md")
        self.assertEqual(shared["index_path"], "specs/INDEX.md")
        self.assertTrue((self.root / "specs" / "quick-tasks" / "repair-router.md").exists())
        self.assertFalse((self.root / "specs" / "prd.md").exists())
        created = create_spec(self.root, "prd", "Local Owner")
        owner = created["subproject_id"]
        local = create_spec(self.root, "quick-task", "Repair Router", subproject=owner)
        self.assertEqual(local["subproject_id"], owner)
        self.assertEqual(local["local_id"], "repair-router")
        catalog = SpecCatalog(self.root)
        catalog.validate()
        shared_ref = catalog.resolve("repair-router", kind="quick-task")
        self.assertIsNone(shared_ref.subproject_id)
        local_ref = catalog.resolve("repair-router", owner=owner, kind="quick-task")
        self.assertEqual(local_ref.subproject_id, owner)
        # Existing quick task is never overwritten.
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "quick-task", "Repair Router", subproject=owner)

    def test_flat_legacy_specs_allow_only_draft_shared_quick_task_bootstrap(self) -> None:
        from skills.scripts.kosmic_work import WorkdirError, resolve_work_record

        legacy = self.root / "specs" / "stories"
        legacy.mkdir(parents=True)
        (legacy / "story-001.md").write_text("# Legacy feature\n", encoding="utf-8")
        created = create_spec(self.root, "quick-task", "Bootstrap Migration")
        path = self.root / "specs" / "quick-tasks" / "bootstrap-migration.md"
        self.assertEqual(created["status"], "draft")
        self.assertEqual(created["paths"], {
            "specs/quick-tasks/bootstrap-migration.md": "demo/quick-task/bootstrap-migration"
        })
        self.assertTrue(path.is_file())
        with self.assertRaisesRegex(WorkdirError, "WORK_PHASE_DENIED"):
            resolve_work_record(self.root, "demo/quick-task/bootstrap-migration")
        draft = path.read_text(encoding="utf-8")
        self.assertIn('status: "draft"', draft)
        path.write_text(draft.replace('status: "draft"', 'status: "approved"'),
                        encoding="utf-8")
        self.assertEqual(resolve_work_record(
            self.root, "demo/quick-task/bootstrap-migration").path, path)
        with self.assertRaisesRegex(SpecError, "MIGRATION_REQUIRED"):
            SpecCatalog(self.root)
        with self.assertRaisesRegex(SpecError, "MIGRATION_REQUIRED"):
            create_spec(self.root, "architecture", "Feature Without Migration",
                        subproject="feature")
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "quick-task", "Bootstrap Migration")

    def test_flat_bootstrap_refuses_an_existing_quick_task_identity_alias(self) -> None:
        legacy = self.root / "specs" / "stories"
        legacy.mkdir(parents=True)
        (legacy / "story-001.md").write_text("# Legacy feature\n", encoding="utf-8")
        quick_tasks = self.root / "specs" / "quick-tasks"
        quick_tasks.mkdir()
        (quick_tasks / "dated-name.md").write_text(
            '---\nproject_id: "demo"\nsubproject_id: null\n'
            'record_kind: "quick-task"\nlocal_id: "bootstrap-migration"\n'
            'status: "approved"\n---\n\n# Existing task\n', encoding="utf-8")
        with self.assertRaisesRegex(SpecError, "RESERVATION_CONFLICT"):
            create_spec(self.root, "quick-task", "Bootstrap Migration")
        self.assertFalse((quick_tasks / "bootstrap-migration.md").exists())

    def test_bootstrap_writes_only_the_governing_records(self) -> None:
        create_spec(self.root, "prd", "Bounded Bootstrap")
        owner = SpecCatalog(self.root).records[0].subproject_id
        written = sorted(
            path.relative_to(self.root).as_posix()
            for path in self.root.rglob("*")
            if path.is_file())
        self.assertFalse([name for name in written if ".stage-" in name],
                         "staging temporaries must not survive publication")
        self.assertEqual(written, sorted([
            "ProjectEntry.md",
            ".kosmic/create.lock",
            f".kosmic/create-ops/{json.loads(next((self.root / '.kosmic' / 'create-ops').glob('*.json')).read_text())['operation_id']}.json",
            f"subprojects/{owner}/SubprojectEntry.md",
            f"subprojects/{owner}/specs/INDEX.md",
            f"subprojects/{owner}/specs/prd.md",
        ]))

    def test_symlinked_subprojects_root_is_refused(self) -> None:
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.root / "subprojects").symlink_to(outside)
        with self.assertRaisesRegex(SpecError, "SCOPE_DENIED"):
            create_spec(self.root, "prd", "Escape Artist")

    def test_escaped_titles_resume_after_index_publication(self) -> None:
        for title in ("Measurement [A]", "Measurement | context", "Backslash \\ case"):
            with self.subTest(title=title):
                args = [sys.executable, str(CLI), "spec-create", "--project",
                        str(self.root), "--kind", "quick-task", "--title", title]
                created = subprocess.run(args, capture_output=True, text=True)
                self.assertEqual(created.returncode, 0, created.stderr)
                result = json.loads(created.stdout)
                operation = (self.root / ".kosmic/create-ops" /
                             (result["operation_id"] + ".json"))
                payload = json.loads(operation.read_text())
                payload["status"] = "reserved"
                operation.write_text(json.dumps(payload))
                index = self.root / result["index_path"]
                before = index.read_bytes()
                resumed = subprocess.run(
                    args + ["--resume", "--operation-id", result["operation_id"]],
                    capture_output=True, text=True)
                self.assertEqual(resumed.returncode, 0, resumed.stderr)
                self.assertEqual(json.loads(resumed.stdout)["record_path"],
                                 result["record_path"])
                self.assertEqual(index.read_bytes(), before)

    def test_finish_preserves_escaped_title_cells_and_neighbor_rows(self) -> None:
        from skills.scripts.kosmic_completion import _update_indexes

        create_spec(self.root, "quick-task", "Neighbor observation")
        for title in ("Measurement [A]", "Measurement | context", "Backslash \\ case"):
            with self.subTest(title=title):
                result = create_spec(self.root, "quick-task", title)
                record = SpecCatalog(self.root).resolve(result["local_id"], kind="quick-task")
                index = self.root / result["index_path"]
                before = index.read_text()
                relative = record.path.relative_to(index.parent).as_posix()
                row = next(line for line in before.splitlines(keepends=True)
                           if f"]({relative})" in line)
                self.assertIn("| draft |", row)
                expected = before.replace(row, row.replace("| draft |", "| done |"))
                _update_indexes(self.root, record)
                self.assertEqual(index.read_text(), expected)

    def test_existing_index_layouts_preserve_rows_through_resume_and_finish(self) -> None:
        from skills.scripts.kosmic_completion import _update_indexes

        layouts = {
            "task-header": "| Task | Status |\n| --- | --- |\n| Existing context | planned |\n",
            "reordered": "| Status | Kind | Record |\n| --- | --- | --- |\n",
            "extra-column": "| Kind | Record | Owner | Status |\n| --- | --- | --- | --- |\n",
            "no-final-newline": "| Kind | Record | Status |\n| --- | --- | --- |",
        }
        for name, layout in layouts.items():
            with self.subTest(layout=name):
                root = project(Path(self.tmp.name) / name)
                (root / "specs").mkdir()
                index = root / "specs/INDEX.md"
                original = "# Specs\n\n" + layout
                index.write_text(original)
                result = create_spec(root, "quick-task", "Native observation")
                record = SpecCatalog(root).resolve(result["local_id"], kind="quick-task")
                relative = record.path.relative_to(index.parent).as_posix()
                before = index.read_text()
                self.assertTrue(before.startswith(original))
                matching = [row for row in status_table_rows(before)
                            if f"]({relative})" in row.get("record", "")]
                self.assertEqual(matching, [{"kind": "quick-task", "record":
                    f"[Native observation]({relative})", "status": "draft"}])
                operation = root / ".kosmic/create-ops" / (result["operation_id"] + ".json")
                payload = json.loads(operation.read_text())
                payload["status"] = "reserved"
                operation.write_text(json.dumps(payload))
                create_spec(root, "quick-task", "Native observation", resume=True,
                            operation_id=result["operation_id"])
                self.assertEqual(index.read_text(), before)
                _update_indexes(root, record)
                self.assertEqual(index.read_text(), before.replace("| draft |", "| done |"))




if __name__ == "__main__":
    unittest.main()
