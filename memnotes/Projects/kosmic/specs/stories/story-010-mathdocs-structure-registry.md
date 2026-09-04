---
status: done
created: 2026-09-05
updated: 2026-09-05
linked_epic: ../epics/epic-6-mathdocs-substrate.md
linked_architecture: ../architecture-math-derivation-layer.md
linked_prd: ../prd-math-derivation-layer.md
related_notes: [cli-projection-commands.md]
consumer_interface_change: true
evidence_packs: [2026-09-05-math-derivation-layer-impl]
review_base: ""
review_round: 0
---

# Story 010: Mathdocs Structure and Registry

## User Story

As a Kosmic maintainer, I want every Project to expose one validated mathdocs
registry, so that every later math workflow consumes one authoritative model.

## Acceptance Criteria

- [x] `init` and `migrate` create the exact empty `mathdocs/index.md` idempotently and never overwrite existing content.
- [x] Every `.py`/`.md` pair is discovered by slug; unpaired, duplicate, and invalid-slug files fail naming the path.
- [x] Index validation rejects missing, duplicate, unknown, and status-mismatched rows; empty index passes.
- [x] `MathRegistry` is the sole registry interface used by subsequent math checks.

## Tasks

### Phase 1: Research
- [x] Locate all project-structure, migration, validation, and publication seams
- [x] Record exact index parser and path-containment assumptions

### Phase 2: Tests (TDD)
- [x] TEST-010A: init/migrate empty, existing, and rollback cases
- [x] TEST-010B: pairing and slug failures
- [x] TEST-010C: index completeness/uniqueness/status cases

### Phase 3: Implementation
- [x] IMPL-010A: add `Project.mathdocs_dir` and reserved index creation
- [x] IMPL-010B: implement immutable registry load and index validation
- [x] IMPL-010C: route project validation through the registry seam

### Phase 4: Review
- [x] Focused and full tests pass
- [x] Task 7 review approved

## Definition of Done

- [x] All acceptance criteria met
- [x] No existing Project content overwritten
- [x] Code reviewed; log/notes current
