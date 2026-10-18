---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_epic: "../epics/epic-002-proposal-governance.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["cli-projection-commands.md"]
evidence_packs: ["2026-09-06-skill-proposal-loop-impl"]
consumer_interface_change: true
proposal_required: false
review_base: "ce222de2"
review_round: 2
project_id: "kosmic"
subproject_id: "skill-proposal-loop"
record_kind: "story"
local_id: "004"
---

# Story 021: Rejection Fingerprint and Ledger Memory

## User Story

As a skill proposer,
I want rejected interventions remembered deterministically,
So that I do not repeat the same failed proposal without materially new evidence.

## Acceptance Criteria

- [x] Proposal fingerprint is canonical SHA-256 of result, scope, target, related notes, and exact Proposed Change content; evidence paths do not alter it.
- [x] A duplicate done/rejected fingerprint fails unless `reconsiders` resolves to that proposal and `New Evidence` is non-empty.
- [x] Lifecycle validation requires pending before implementation and accepted/rejected before done, with behavioral evidence required for accepted create/update.
- [x] Task 7 documents the fixed six-field ledger entry using `proposal:<path>#<fingerprint>`; no ledger schema change occurs.

## Tasks

### Phase 1: Research
- [x] Inspect ledger validator and proposal lifecycle conventions.

### Phase 2: Tests (TDD)
- [x] TEST-021A: stable fingerprint and tamper detection.
- [x] TEST-021B: rejected duplicate, valid reconsideration, and lifecycle matrix.
- [x] TEST-021C: proposal ledger entry remains valid.

### Phase 3: Implementation
- [x] IMPL-021A: implement fingerprint, rejection scan, reconsideration, and review docs.

### Phase 4: Review
- [x] Focused/full tests and Task 7 review pass.

## Definition of Done

- [x] All acceptance criteria met; tests pass; review approved; knowledge and log updated.
