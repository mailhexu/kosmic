# Procedure Compilation and Routine Reuse Implementation

## Scope

Implemented Stories 037-042 from the approved Procedure Compilation and Routine Reuse PRD and Architecture.

## Delivered behavior

- Added `skills/scripts/kosmic_routines.py` with AST-literal routine declarations, static inventory validation, deterministic query, and atomic tree publication.
- Replaced project and Shared Library publication mechanics with the shared atomic publication routine.
- Generated `.kosmic/routines.json` beside the Shared Library catalog and manifest.
- Added role-filtered `uses_routines` relationships and hash-pinned routine packet chunks.
- Extended Task 9, Task P, Story, Quick Task, templates, completion gates, and CLI documentation with routine classification and decisions.
- Added `generate-library --source-root`, `validate-library --source-root`, and `query-routines` CLI behavior.

## Verification

- Initial implementation checkpoint: the same regression command passed 302 tests before review-driven coverage was added; the final count is recorded in `final-validation.md`.
- `python3 skills/scripts/kosmic_project_skills.py generate-library --vault memnotes`: generated catalog, manifest, routine inventory, and domain indexes.
- `python3 skills/scripts/kosmic_project_skills.py query-routines --vault memnotes --id kosmic/atomic-publish-tree`: returned the canonical routine with four callers and matching inventory/manifest hashes.

## Failure lessons

- Text-anchor edits against a large moving CLI file can land inside the wrong parser/function block. Immediate targeted reads exposed and repaired each misplaced edit.
- Source-root inference must remain in CLI dispatch; shared functions receive resolved roots rather than rediscovering repository layout.
