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
routine_proposals: [../skill-proposals/2026-09-07-atomic-publish-tree-reuse.md, ../skill-proposals/2026-09-14-atomic-publish-tree-recovery.md]
depends_on: [story-059-dream-vault-schema-validator.md, story-060-managed-dream-harvest-handshake.md]
review_base: ""
review_round: 0
---

# Story 061: Deterministic Dream Publication

## User Story

As a Task D agent,
I want publisher-owned merge, validation, and atomic promotion,
So that untrusted reflection inputs become one consistent dream tree without losing manual work.

## Acceptance Criteria

- [x] Completion fails unless Stories 059–060 are `done`; `dream-publish` derives all paths and publisher-owned fields from the authenticated handle/control state.
- [x] Candidate inputs with forged date/project/run provenance, generated digest, canonical IDs, or index data fail; permitted sections/ideas merge deterministically.
- [x] Publish rechecks evidence/external-link hashes, redacts, canonically serializes, inserts `generated_content_sha256`, validates, and promotes the complete tree through the approved `publish_tree` routine.
- [x] Exactly matching idea IDs deduplicate; differing same-ID entries fail. Index rows are rebuilt uniquely newest-first.
- [x] Tree/read/link drift always fails; manual record divergence requires `--replace`, which never bypasses those checks. Byte-identical same-date output is idempotent.
- [x] Approved atomic-publication routine contracts are pinned and conformance-tested unchanged; any required semantic extension reopens Task P instead of landing here.

## Tasks

### Phase 1: Research

- [x] Verify accepted routine proposals, current routine hash, caller contract, rollback, and recovery semantics.
- [x] Pin candidate-to-canonical merge and digest comparison tables.

### Phase 2: Tests (TDD - Write First!)

- [x] TEST-061-1: Forbidden/allowed candidate fields and deterministic merge/order/dedupe matrix.
- [x] TEST-061-2: Redaction, canonical digest, composite links, and validator equivalence.
- [x] TEST-061-3: Base/read/link drift, manual divergence, replace, identical rerun, idea collision, rollback, and routine-conformance controls.

### Phase 3: Implementation

- [x] IMPL-061-1: Implement deterministic candidate merge, index/ideas rebuild, redaction, serialization, digest, and validation pipeline.
- [x] IMPL-061-2: Add authenticated `dream-publish` using the approved whole-tree routine unchanged.

### Phase 4: Review

- [x] Focused and full tests pass
- [x] Security, Standards, and Spec reviews converge
- [x] Routine conformance and consumer-interface completion gates pass

## Routine Decision

Reuse accepted `kosmic/atomic-publish-tree` decisions in the linked 2026-09-07
and 2026-09-14 proposals. This story changes no routine edge or routine
semantics; any mismatch is a blocker requiring a new Task P decision.

## Technical Notes

This story owns the commit point but not retry/abort/race policy, which belongs
to Story 062.

## Definition of Done

- [x] All acceptance criteria met
- [x] All prerequisite stories are done
- [x] Routine conformance, security, and code reviews approved
- [x] Stable usage note exists and is projected
- [x] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-23 | Created | Split from original publication/release story |

| 2026-09-23 | Done | Implemented and verified; dogfood evidence in evidence/2026-09-23-dream-reflection-release |
