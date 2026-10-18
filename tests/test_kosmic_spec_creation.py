from __future__ import annotations

import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

from skills.scripts import kosmic_specs
from skills.scripts.kosmic_specs import SpecCatalog, SpecError, create_spec, normalize_subproject_title


def project(root: Path) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    (root / "ProjectEntry.md").write_text(
        "---\nproject_id: \"demo\"\n---\n\n# Demo\n", encoding="utf-8")
    return root


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
        self.assertEqual((owner_dir / owner / "specs" / "INDEX.md").read_text(encoding="utf-8"),
                         "# Recoverable Feature Specs\n\n- [PRD](prd.md)\n")
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

    def test_quick_tasks_are_independent_and_never_create_a_prd(self) -> None:
        shared = create_spec(self.root, "quick-task", "Repair Router")
        self.assertIsNone(shared["subproject_id"])
        self.assertIsNone(shared["operation_id"])
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


if __name__ == "__main__":
    unittest.main()
