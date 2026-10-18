from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from skills.scripts.kosmic_specs import SpecCatalog, migration_plan
from tests.test_kosmic_specs import document, project


CLI = Path(__file__).resolve().parents[1] / 'skills/scripts/kosmic_project_skills.py'


class MigrationApplyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix='kosmic-migration-apply-')
        self.addCleanup(self.tmp.cleanup)
        self.root = project(Path(self.tmp.name) / 'Project')
        (self.root / '.gitignore').write_text('.tmp/\n.kosmic/\n', encoding='utf-8')
        subprocess.run(['git', 'init', '-q', str(self.root)], check=True, capture_output=True)
        for owner in ('export', 'second'):
            document(self.root / f'specs/prd-{owner}.md', {'status': 'approved'}, owner.title())
            document(self.root / f'specs/architecture-{owner}.md', {
                'status': 'approved', 'linked_prd': f'prd-{owner}.md'}, owner.title() + ' Architecture')
            document(self.root / f'specs/epics/epic-01-{owner}.md', {
                'status': 'approved', 'linked_prd': f'../prd-{owner}.md',
                'linked_architecture': f'../architecture-{owner}.md'}, owner.title() + ' Epic')
            document(self.root / f'specs/stories/story-01-{owner}.md', {
                'status': 'approved', 'linked_prd': f'../prd-{owner}.md',
                'linked_architecture': f'../architecture-{owner}.md',
                'linked_epic': f'../epics/epic-01-{owner}.md',
                'depends_on': ['story-01-export.md'] if owner == 'second' else []}, owner.title() + ' Story')
        self.task = document(self.root / 'specs/quick-tasks/migrate.md', {
            'project_id': 'demo', 'subproject_id': None, 'record_kind': 'quick-task',
            'local_id': 'migration-authority', 'status': 'approved',
            'consumer_interface_change': False}, 'Migration authority')
        (self.root / 'notes').mkdir(exist_ok=True)
        (self.root / 'notes/live.md').write_text('# Live note\n\n[Export](../specs/prd-export.md)\n', encoding='utf-8')
        (self.root / 'evidence').mkdir()
        (self.root / 'evidence/historical.md').write_text('[Old](../specs/prd-export.md)\n', encoding='utf-8')
        (self.root / 'log').mkdir()
        (self.root / 'log/history.md').write_text('[Old](../specs/prd-export.md)\n', encoding='utf-8')
        self.reference = 'demo/quick-task/migration-authority'
        self.plan_path = Path(self.tmp.name) / 'plan.json'

    def plan(self) -> dict:
        from skills.scripts.kosmic_migration import save_migration_plan
        result = migration_plan(self.root)
        save_migration_plan(result, self.plan_path)
        return result

    def snapshot(self) -> dict[str, bytes]:
        return {path.relative_to(self.root).as_posix(): path.read_bytes()
                for path in self.root.rglob('*') if path.is_file()
                and path.relative_to(self.root).parts[0] not in ('.git', '.tmp', '.kosmic')}

    def cli(self, command: str, plan: dict, **env: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, str(CLI), command, '--project', str(self.root),
            '--plan', str(self.plan_path), '--approve-digest', plan['digest'],
            '--work-record', self.reference], capture_output=True, text=True,
            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', **env}, timeout=15)

    def test_approved_plan_migrates_identities_and_live_links_without_minting_authority(self) -> None:
        from skills.scripts.kosmic_migration import apply_migration
        before = self.snapshot()
        plan = self.plan()
        result = apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(result['status'], 'successful')
        catalog = SpecCatalog(self.root)
        catalog.validate()
        self.assertEqual(catalog.resolve('demo/export/story/001').status, 'approved')
        second = catalog.resolve('demo/second/story/001')
        self.assertEqual([ref.qualified_id for ref in catalog.dependencies(second)], ['demo/export/story/001'])
        self.assertEqual(catalog.resolve(self.reference).local_id, 'migration-authority')
        self.assertFalse((self.root / 'specs/prd-export.md').exists())
        self.assertIn('../subprojects/export/specs/prd.md', (self.root / 'notes/live.md').read_text())
        self.assertEqual((self.root / 'evidence/historical.md').read_bytes(), before['evidence/historical.md'])
        self.assertEqual((self.root / 'log/history.md').read_bytes(), before['log/history.md'])
        after = self.snapshot()
        self.assertEqual(apply_migration(self.root, self.plan_path, plan['digest'], self.reference), result)
        self.assertEqual(self.snapshot(), after)

    def test_interrupted_cli_application_recovers_and_can_retry_the_same_plan(self) -> None:
        before = self.snapshot()
        plan = self.plan()
        interrupted = self.cli('migrate-subprojects-apply', plan,
                               KOSMIC_MIGRATION_FAIL_STAGE='crash-after-write:0')
        self.assertEqual(interrupted.returncode, 86, interrupted.stderr)
        refused = self.cli('migrate-subprojects-apply', plan)
        self.assertEqual(refused.returncode, 2)
        self.assertIn('MIGRATION_RECOVERY_REQUIRED', refused.stderr)
        recovered = self.cli('migrate-subprojects-recover', plan)
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(json.loads(recovered.stdout)['status'], 'rolled-back')
        self.assertEqual(self.snapshot(), before)
        from skills.scripts.kosmic_runs import report_runs
        self.assertNotIn('active', {entry.state for entry in report_runs(self.root).entries})
        applied = self.cli('migrate-subprojects-apply', plan)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertEqual(json.loads(applied.stdout)['status'], 'successful')
        SpecCatalog(self.root).validate()

    def test_recovery_preserves_an_external_edit_instead_of_overwriting_it(self) -> None:
        plan = self.plan()
        interrupted = self.cli('migrate-subprojects-apply', plan,
                               KOSMIC_MIGRATION_FAIL_STAGE='crash-after-write:0')
        self.assertEqual(interrupted.returncode, 86, interrupted.stderr)
        transaction = json.loads((self.root / '.kosmic/migrations' / plan['digest']
                                  / 'transaction.json').read_text())
        changed = self.root / transaction['operations'][0]['path']
        changed.write_text('# External work\n', encoding='utf-8')
        recovered = self.cli('migrate-subprojects-recover', plan)
        self.assertEqual(recovered.returncode, 2)
        self.assertIn('MIGRATION_TRANSACTION_CONFLICT', recovered.stderr)
        self.assertEqual(changed.read_text(), '# External work\n')

    def test_occupied_target_is_reported_without_overwriting_it(self) -> None:
        from skills.scripts.kosmic_migration import MigrationError, apply_migration
        plan = self.plan()
        target = self.root / 'subprojects/export/specs/prd.md'
        target.parent.mkdir(parents=True)
        target.write_text('# Another writer\n', encoding='utf-8')
        before = self.snapshot()
        with self.assertRaisesRegex(MigrationError, 'MIGRATION_TARGET_COLLISION'):
            apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(self.snapshot(), before)

    def test_target_only_research_drift_refuses_actual_cli_application(self) -> None:
        target = self.root / 'research/showcase.md'
        target.parent.mkdir()
        target.write_text('# Original research\n')
        source = self.root / 'specs/prd-export.md'
        source.write_text(source.read_text() + '\n[Research](../research/showcase.md)\n')
        plan = self.plan()
        target.write_text('# Owner changed research\n')
        before = self.snapshot()
        rejected = self.cli('migrate-subprojects-apply', plan)
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn('MIGRATION_INPUT_DRIFT', rejected.stderr)
        self.assertEqual(self.snapshot(), before)

    def test_added_input_and_changed_input_both_require_a_new_plan(self) -> None:
        from skills.scripts.kosmic_migration import MigrationError, apply_migration
        plan = self.plan()
        added = self.root / 'notes/new-live.md'
        added.write_text('[Export](../specs/prd-export.md)\n', encoding='utf-8')
        before = self.snapshot()
        with self.assertRaisesRegex(MigrationError, 'MIGRATION_INPUT_DRIFT'):
            apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(self.snapshot(), before)
        added.unlink()
        source = self.root / 'specs/prd-export.md'
        source.write_text(source.read_text() + '\nNew requirement\n')
        changed = self.snapshot()
        with self.assertRaisesRegex(MigrationError, 'MIGRATION_INPUT_DRIFT'):
            apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(self.snapshot(), changed)

    def test_rehashed_arbitrary_candidate_is_not_executable(self) -> None:
        from skills.scripts.kosmic_migration import MigrationError, apply_migration
        plan = self.plan()
        row = next(row for row in plan['outputs'] if row['path'].endswith('/specs/prd.md'))
        row['content'] = '# Invented replacement\n'
        row['after_sha256'] = hashlib.sha256(row['content'].encode()).hexdigest()
        plan.pop('digest')
        plan['digest'] = hashlib.sha256(json.dumps(plan, sort_keys=True,
            separators=(',', ':')).encode()).hexdigest()
        self.plan_path.write_text(json.dumps(plan))
        before = self.snapshot()
        with self.assertRaisesRegex(MigrationError, 'MIGRATION_INPUT_DRIFT'):
            apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(self.snapshot(), before)

    def test_foreign_qualified_reference_cannot_borrow_this_projects_task(self) -> None:
        from skills.scripts.kosmic_migration import MigrationError, apply_migration
        plan = self.plan()
        before = self.snapshot()
        with self.assertRaisesRegex(MigrationError, 'MIGRATION_AUTHORITY_DENIED'):
            apply_migration(self.root, self.plan_path, plan['digest'],
                            'foreign/quick-task/migration-authority')
        self.assertEqual(self.snapshot(), before)

    def test_draft_and_revoked_authority_deny_execution(self) -> None:
        from skills.scripts.kosmic_migration import MigrationError, apply_migration
        plan = self.plan()
        approved = self.task.read_text()
        for status in ('draft', 'done'):
            with self.subTest(status=status):
                self.task.write_text(approved.replace('"approved"', f'"{status}"'))
                before = self.snapshot()
                with self.assertRaisesRegex(MigrationError, 'MIGRATION_AUTHORITY_DENIED'):
                    apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
                self.assertEqual(self.snapshot(), before)

    def test_symlinked_plan_or_destination_never_writes_outside_the_project(self) -> None:
        from skills.scripts.kosmic_migration import MigrationError, apply_migration
        plan = self.plan()
        linked_plan = Path(self.tmp.name) / 'linked-plan.json'
        linked_plan.symlink_to(self.plan_path)
        before = self.snapshot()
        with self.assertRaisesRegex(MigrationError, 'MIGRATION_PATH_UNSAFE'):
            apply_migration(self.root, linked_plan, plan['digest'], self.reference)
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        (self.root / 'subprojects').symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(MigrationError, 'MIGRATION_PATH_UNSAFE'):
            apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual(self.snapshot(), before)

    def test_bound_status_is_final_root_rendering_and_failure_restores_it(self) -> None:
        from unittest import mock
        from skills.scripts.kosmic_migration import MigrationError, apply_migration
        from skills.scripts.kosmic_project_skills import load_project, render_status
        document(self.root / 'ProjectEntry.md',
                 {'project_id': 'demo', 'status_root': str(self.root)}, 'Demo')
        (self.root / 'STATUS.md').write_text('# Previous report\n', encoding='utf-8')
        before = self.snapshot()
        plan = self.plan()
        with mock.patch.dict(os.environ, {'KOSMIC_MIGRATION_FAIL_STAGE': 'after-write:5'}):
            with self.assertRaisesRegex(MigrationError, 'MIGRATION_INJECTED_FAILURE'):
                apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(self.snapshot(), before)
        self.assertFalse((self.root / 'subprojects').exists())
        result = apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(result['status_disposition'], 'bound')
        self.assertEqual((self.root / 'STATUS.md').read_bytes(),
                         render_status(load_project(self.root), plan['status_binding']['head']))
        self.assertNotIn('.tmp/', (self.root / 'STATUS.md').read_text())

    def test_interrupted_complete_cutover_is_verified_and_receipted(self) -> None:
        plan = self.plan()
        crashed = self.cli('migrate-subprojects-apply', plan,
                           KOSMIC_MIGRATION_FAIL_STAGE='crash-before-receipt')
        self.assertEqual(crashed.returncode, 86, crashed.stderr)
        migrated = self.snapshot()
        recovered = self.cli('migrate-subprojects-recover', plan)
        self.assertEqual(recovered.returncode, 0, recovered.stderr)
        self.assertEqual(json.loads(recovered.stdout)['status'], 'successful')
        self.assertEqual(self.snapshot(), migrated)
        repeated = self.cli('migrate-subprojects-apply', plan)
        self.assertEqual(repeated.returncode, 0, repeated.stderr)
        self.assertEqual(json.loads(repeated.stdout), json.loads(recovered.stdout))

    def test_saved_plan_output_is_exclusive_even_through_a_symlink(self) -> None:
        output = Path(self.tmp.name) / 'saved-plan.json'
        command = [sys.executable, str(CLI), 'migrate-subprojects-plan',
                   '--project', str(self.root), '--output', str(output)]
        saved = subprocess.run(command, capture_output=True, text=True, timeout=15,
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertEqual(saved.returncode, 0, saved.stderr)
        data = output.read_bytes()
        refused = subprocess.run(command, capture_output=True, text=True, timeout=15,
                                 env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertEqual(refused.returncode, 2)
        self.assertEqual(output.read_bytes(), data)
        alias = Path(self.tmp.name) / 'plan-alias.json'
        alias.symlink_to(output)
        aliased = subprocess.run(command[:-1] + [str(alias)], capture_output=True, text=True,
                                timeout=15, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
        self.assertEqual(aliased.returncode, 2)
        self.assertEqual(output.read_bytes(), data)

    def test_completed_receipt_allows_valid_authority_progress_without_rewriting_outputs(self) -> None:
        from skills.scripts.kosmic_migration import apply_migration, recover_migration
        document(self.root / 'ProjectEntry.md',
                 {'project_id': 'demo', 'status_root': str(self.root)}, 'Demo')
        self.assertFalse((self.root / 'STATUS.md').exists())
        plan = self.plan()
        receipt = apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        self.assertEqual(receipt['status_disposition'], 'bound')
        self.assertEqual((self.root / 'STATUS.md').read_text(), plan['status_binding']['content'])
        self.task.write_text(self.task.read_text().replace('"approved"', '"in_progress"'))
        before = self.snapshot()
        self.assertEqual(apply_migration(self.root, self.plan_path, plan['digest'], self.reference),
                         receipt)
        self.assertEqual(recover_migration(self.root, self.plan_path, plan['digest'], self.reference),
                         receipt)
        self.assertEqual(self.snapshot(), before)

    def test_existing_owner_dependencies_follow_moved_records_and_preserve_local_edges(self) -> None:
        from skills.scripts.kosmic_migration import apply_migration
        from tests.test_kosmic_specs import feature
        specs = feature(self.root, 'existing')
        story = specs / 'stories/story-001.md'
        old = os.path.relpath(self.root / 'specs/stories/story-01-export.md', story.parent)
        text = story.read_text().replace('depends_on: []',
            f'depends_on: ["story-002.md", "{old}"]\ncross_subproject_dependencies: ["{old}"]')
        story.write_text(text)
        common = {'project_id': 'demo', 'subproject_id': 'existing', 'status': 'approved',
                  'record_kind': 'story', 'linked_prd': '../prd.md',
                  'linked_architecture': '../architecture.md', 'linked_epic': '../epics/epic-001.md'}
        document(specs / 'stories/story-002.md', {**common, 'local_id': '002', 'depends_on': []})
        document(specs / 'stories/story-003.md', {**common, 'local_id': '003', 'depends_on': [old]})
        before = (specs / 'prd.md').read_bytes()
        plan = self.plan()
        apply_migration(self.root, self.plan_path, plan['digest'], self.reference)
        catalog = SpecCatalog(self.root)
        catalog.validate()
        existing = catalog.resolve('demo/existing/story/001')
        self.assertEqual([ref.qualified_id for ref in catalog.dependencies(existing)],
                         ['demo/existing/story/002', 'demo/export/story/001'])
        added = catalog.resolve('demo/existing/story/003')
        self.assertEqual([ref.qualified_id for ref in catalog.dependencies(added)],
                         ['demo/export/story/001'])
        self.assertEqual((specs / 'prd.md').read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
