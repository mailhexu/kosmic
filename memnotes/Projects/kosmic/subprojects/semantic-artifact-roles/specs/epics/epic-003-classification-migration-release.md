---
status: "done"
created: "2026-09-07"
updated: "2026-09-07"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-005-distillation-and-proposal-classification.md", "../stories/story-006-abinit-migration-dogfood-release.md"]
project_id: "kosmic"
subproject_id: "semantic-artifact-roles"
record_kind: "epic"
local_id: "003"
---

# Epic 19: Classification Migration and Release

## Description

Move semantic classification upstream into Project knowledge workflows, migrate the authoritative shared library explicitly, and prove the model against ABINIT without losing provenance or changing the one-router installation architecture.

## Scope

### In Scope
- Project-note role validation and migration reporting
- Task 9, Task P, templates, glossary, and documentation
- Explicit role-aware assignment schema and atomic migration
- Complete ABINIT classification, representative behavior, review, and release

### Out of Scope
- Reclassifying every historical note in every external vault
- Automatically converting mixed knowledge into procedures

## Stories

| Story | Description | Status |
|---|---|---|
| [Story 035](../stories/story-005-distillation-and-proposal-classification.md) | Upstream classification in notes, Task 9, and Task P | draft |
| [Story 036](../stories/story-006-abinit-migration-dogfood-release.md) | ABINIT-first migration, dogfood, review, and release | draft |

## Success Criteria

- [x] New or materially updated Project notes carry a validated role.
- [x] Only procedure results trigger procedural proposal eligibility.
- [x] Every ABINIT topic has an explicit reviewed assignment and representative queries demonstrate the intended authority.
- [x] Atomic publication, provenance, tests, and four-adapter one-router checks pass.
