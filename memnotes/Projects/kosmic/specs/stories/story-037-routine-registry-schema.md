---
status: done
created: 2026-09-07
updated: 2026-09-07
linked_epic: ../epics/epic-20-routine-registry-discovery.md
linked_architecture: ../architecture-procedure-compilation.md
linked_prd: ../prd-procedure-compilation.md
proposal_required: false
review_base: c52ab6a15b2dab0df9cbd450a76fcdc386612cdb
review_round: 1
consumer_interface_change: true
related_notes: [cli-projection-commands.md]
evidence_packs: [2026-09-07-procedure-compilation]
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
---

# Story 037: Routine Registry Schema

## Story

As a Maintainer, I want static routine declarations validated without importing source so that discovery is safe, deterministic, and owned.

## Acceptance Criteria

- [x] Add `kosmic_routines.py` with typed records/errors and `build_routine_inventory`/`validate_routine_inventory` interfaces from AD-PC1.
- [x] Parse only literal module-level `KOSMIC_ROUTINES`; reject dynamic expressions, duplicate IDs, missing or ambiguous symbols, unresolvable tests/callers, and side effects outside AD-PC2's fixed vocabulary.
- [x] Enforce domain/owner authority against the generated domain catalog and reciprocal procedure `uses_routines` edges.
- [x] Produce normalized records with source, declaration, and routine hashes; output is byte-identical across repeated runs.
- [x] Add focused behavioral tests for valid and each fail-closed declaration boundary.

## Routine Decision

This story creates registry governance, not a reusable mechanics candidate; `routine_decision_required` is false.

## Tasks

- [x] Write focused failing registry-contract tests.
- [x] Implement static declaration parsing and validation.
- [x] Run focused and full regression suites.
- [x] Complete Standards and Spec review.

## Definition of Done

- [x] All acceptance criteria pass through public behavior.
- [x] Documentation and fixtures match the schema.
- [x] No Blocking, High, or Medium review finding remains.
