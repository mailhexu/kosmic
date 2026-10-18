---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_epic: "../epics/epic-004-proposal-activation-release.md"
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
local_id: "006"
---

# Story 023: Installation and Activation Diagnostics

## User Story

As a Kosmic consumer,
I want installation and active-session discovery reported separately,
So that files on disk are not mistaken for a skill actually offered to the model.

## Acceptance Criteria

- [x] Generated Usage and Development descriptions use the concrete fixed trigger sentences from AD-P8.
- [x] `check-installation --project --adapter --home` verifies both installed package bytes and project identity, and fails on missing, stale, partial, or colliding pairs.
- [x] `install` reports disk installation success followed by adapter-specific reload/new-session guidance and `active-session discovery unverified`.
- [x] Documentation gives an inventory probe where supported and never claims unobserved activation.

## Tasks

### Phase 1: Research
- [x] Map projection description rendering and install adapter roots.

### Phase 2: Tests (TDD)
- [x] TEST-023A: exact generated descriptions.
- [x] TEST-023B: current, missing, stale, partial, and collision installation fixtures.
- [x] TEST-023C: install output accurately separates disk and session state.

### Phase 3: Implementation
- [x] IMPL-023A: update descriptions, installation validator, CLI, and docs.

### Phase 4: Review
- [x] Adapter smoke checks, full tests, and Task 7 review pass.

## Definition of Done

- [x] All acceptance criteria met; tests pass; review approved; usage note and log updated.
