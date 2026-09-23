# Routine Migration Report

## Canonical routines

- `kosmic/atomic-publish-tree` — `skills/scripts/kosmic_routines.py::publish_tree`; hash `44e467e88e889271253ad251417f93d5da29a5ab1a1d02d68813bf261c5b166b`; callers: `python:kosmic_project_skills:generate`, `python:kosmic_project_skills:migrate_notes_bundle`, `python:kosmic_project_skills:update_mathdocs`, `python:kosmic_shared_library:generate_library`; procedures: `kosmic/development/atomic-skill-publication`

## Legacy candidates supplied by Task 9

- None supplied.

## Explicit unregistered helpers

- None supplied.

## Behavioral equivalence

- Canonical publication behavior: whole-tree and managed-path success, failure before backup, failure after backup, restoration, and cleanup.
- Evidence must compare baseline and candidate outcomes before another routine cutover.

## Blockers

- None.
