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
local_id: "003"
---

# Story 020: Proposal Completion Gate

## User Story

As a Kosmic maintainer,
I want completion to require an explicit proposal decision for qualifying new work,
So that skill evolution cannot silently disappear after Distillation.

## Acceptance Criteria

- [x] New Story and Quick Task templates declare `proposal_required: false`; Task 9 explains exactly when it must become true.
- [x] `check-completion` accepts absent metadata for legacy work, validates a present boolean, rejects a proposal path when false, and requires exactly one valid `skill_proposal` when true.
- [x] A true declaration accepts valid create/update/no_action output; no_action requires its validated reason.
- [x] Proposal gating runs after Evidence linkage and before the Consumer Interface early return.

## Tasks

### Phase 1: Research
- [x] Reuse current Evidence and interface gate ordering.

### Phase 2: Tests (TDD)
- [x] TEST-020A: legacy, false, true, missing, malformed, and no_action branches.
- [x] TEST-020B: non-interface work proves gate ordering.

### Phase 3: Implementation
- [x] IMPL-020A: add template fields, Task 9 rule, and completion validator call.

### Phase 4: Review
- [x] Focused/full tests and Task 7 review pass.

## Definition of Done

- [x] All acceptance criteria met; tests pass; review approved; docs and log updated.
