---
status: "done"
created: "2026-09-23"
updated: "2026-09-23"
linked_epic: "../epics/epic-001-dream-reflection-initial-release.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
depends_on: ["story-001-dream-day-delta-harvest.md"]
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "dream-reflection"
record_kind: "story"
local_id: "002"
---

# Story 058: Dream Open Work and Knowledge Contract

## User Story

As a dream reflector,
I want current work and bounded knowledge evidence in the harvest,
So that Done, In Flight, Knowledge Flags, and Skill Candidates are complete and auditable.

## Acceptance Criteria

- [x] Open work includes nonterminal stories/epics/quick tasks, draft PRD/Architecture gates, and pending Skill Proposals, including records begun before the target day.
- [x] Status changes are derived from immutable ordered Git before/after blobs rather than current-file inference.
- [x] The complete link-only scan and typed Knowledge Flag oracles match AD-DR3 for unextracted logs, uncited changed drafts, declared staleness, and evidence ordering.
- [x] Candidate evidence contains hash-pinned prior dream candidate sections and routine-query rows; no proposal is created.
- [x] Logical `read_set` entries identify every and only evidence path/blob Task D may consume, with role, canonical path, observation/origin, immutable content hash, and materialization source; Story 060 owns the run-local byte store and safe locator.

## Tasks

### Phase 1: Research

- [x] Inventory work-item status conventions and terminal/nonterminal values.
- [x] Verify link parser, evidence MANIFEST, stale metadata, proposal, and routine-query contracts.

### Phase 2: Tests (TDD - Write First!)

- [x] TEST-058-1: Open-work fixtures cover every authoritative record type, blocker, terminal exclusion, and project filter.
- [x] TEST-058-2: Each Knowledge Flag has positive, negative, malformed, multi-citation, and link-normalization cases.
- [x] TEST-058-3: Historical transitions, candidate evidence, and read-set hashes remain stable across checkout state.

### Phase 3: Implementation

- [x] IMPL-058-1: Extend harvest with status transitions and authoritative open-work discovery.
- [x] IMPL-058-2: Build complete link index and deterministic flag records.
- [x] IMPL-058-3: Add candidate evidence and role-typed path/blob read set.

### Phase 4: Review

- [x] All tests pass
- [x] Standards and Spec review completed
- [x] Knowledge contract documented if reusable

## Routine Decision

The work extends the Kosmic-specific DreamHarvest schema and existing project
parsers; it does not create a reusable Shared Routine edge.

## Technical Notes

This story extends Story 057's internal collector and exposes no supported CLI. Task D is forbidden from broadening discovery beyond its hash-pinned contract. Possible contradiction remains judgmental and must link both inputs.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Spec statuses are machine-readable across existing work-item types | ⬜ | Current specs and validators |
| Existing Markdown-link parsing can produce canonical backlinks | ⬜ | Projection CLI link utilities |

## Definition of Done

- [x] All acceptance criteria met
- [x] Focused and full tests pass
- [x] Code reviewed and approved
- [x] Knowledge notes updated when warranted
- [x] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-23 | Created | Initial draft |

| 2026-09-23 | Done | Implemented and verified; dogfood evidence in evidence/2026-09-23-dream-reflection-release |
