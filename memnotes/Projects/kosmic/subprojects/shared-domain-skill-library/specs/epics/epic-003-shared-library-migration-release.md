---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-005-shared-library-migration.md", "../stories/story-006-shared-library-dogfood-release.md"]
project_id: "kosmic"
subproject_id: "shared-domain-skill-library"
record_kind: "epic"
local_id: "003"
---

# Epic 16: Shared Library Migration and Release

## Description

Migrate existing stable procedural knowledge without lost provenance, prove cross-domain loading on realistic fixtures, and release the clean single-router cutover.

## Scope

### In Scope
- Staged migration planning, collision detection, and atomic publication
- Kosmic, ABINIT, and TB2J domain fixtures
- Behavioral comparison, documentation, generated outputs, and release verification

### Out of Scope
- Semantic auto-classification without Maintainer review
- Compatibility aliases for old per-Project Skill Pairs

## Stories
- [Story 029: Shared Library Migration](../stories/story-005-shared-library-migration.md)
- [Story 030: Shared Library Dogfood and Release](../stories/story-006-shared-library-dogfood-release.md)

## Acceptance Criteria
- [x] Migration refuses unassigned, colliding, or stale sources and otherwise preserves hashes, evidence, and audience.
- [x] A TB2J development query loads declared ABINIT Usage procedures and excludes unrelated topics.
- [x] The released tree, catalog, router package, adapters, docs, and completion gates validate together.
