---
status: done
created: 2026-09-23
updated: 2026-09-23
linked_epic: ../epics/epic-26-dream-reflection-initial-release.md
linked_architecture: ../architecture-dream-reflection.md
linked_prd: ../prd-dream-reflection.md
related_notes: [notes/dream-reflection-workflow.md]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
depends_on: [story-061-deterministic-dream-publication.md]
review_base: ""
review_round: 0
---

# Story 062: Dream Run Recovery and Concurrency

## User Story

As a Task D operator,
I want explicit retry, abort, race, and crash semantics,
So that every managed dream run has one safe terminal result.

## Acceptance Criteria

- [x] Completion fails unless Story 061 is `done`; the run state table defines active, publishing, retryable-input-error, retryable-validation-error, reharvest-required, succeeded, failed/aborted, and expired outcomes.
- [x] The publication commit point serializes publish/publish, publish/abort, abort/expiry, and retry races so exactly one terminal receipt wins and repeated terminal calls return that receipt idempotently.
- [x] Input/validation errors retain an active retryable run; evidence/base/concurrency drift requires a fresh harvest; partial publication failures follow `publish_tree` recovery and cannot be retried until reconciled.
- [x] `dream-abort` authenticates the handle, stops the holder, records failed finalization, and owns cleanup; holder expiry/reaping yields the same bounded terminal semantics after agent crash.
- [x] Tests pin exit/result codes, receipts, cleanup ownership, and same-date outcomes for identical output, divergent generated output, manual divergence, and `--replace`.

## Tasks

### Phase 1: Research

- [x] Map existing managed-run control/receipt/recovery states to dream transitions.
- [x] Specify the serialized commit boundary and race outcome table.

### Phase 2: Tests (TDD - Write First!)

- [x] TEST-062-1: Every state transition, retry, repeated call, and terminal receipt.
- [x] TEST-062-2: Publish/publish, publish/abort, abort/expiry, crash, and partial-publication races.
- [x] TEST-062-3: Cleanup ownership and fresh-harvest requirements after every failure class.

### Phase 3: Implementation

- [x] IMPL-062-1: Implement dream-specific run state/receipt transitions around existing holder controls.
- [x] IMPL-062-2: Add authenticated `dream-abort`, retry classification, race serialization, and bounded recovery/reaping.

### Phase 4: Review

- [x] Focused and full tests pass
- [x] Security, Standards, and Spec reviews converge
- [x] Consumer-interface completion gate passes

## Routine Decision

This story composes existing run and publication recovery mechanisms without
changing a Shared Routine edge.

## Technical Notes

No failure path may silently leave an active holder without either a retryable
contract or bounded expiry/reaping.

## Definition of Done

- [x] All acceptance criteria met
- [x] Story 061 is done
- [x] Race tests are deterministic and full-suite safe
- [x] Stable usage note exists and is projected
- [x] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-23 | Created | Split concurrency/recovery slice |

| 2026-09-23 | Done | Implemented and verified; dogfood evidence in evidence/2026-09-23-dream-reflection-release |
