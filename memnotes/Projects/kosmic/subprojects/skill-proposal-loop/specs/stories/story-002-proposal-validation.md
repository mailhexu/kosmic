---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_epic: "../epics/epic-001-proposer-contract.md"
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
local_id: "002"
---

# Story 019: Proposal Model and Validation

## User Story

As a Kosmic maintainer,
I want one deterministic SkillProposal loader and validator,
So that every proposer result has a safe, machine-checkable contract.

## Acceptance Criteria

- [x] `SkillProposal` and `load_skill_proposal` validate flat metadata, lifecycle, required sections, path containment, evidence/note resolution, exact action/scope rules, and target pins.
- [x] Global/shared proposals fail unless `proposer_mode: subagent`, `proposer_ref` is non-empty, and the curated input manifest is valid; allowed same-agent cases require a reason.
- [x] `validate-proposal` validates one artifact; normal `validate` validates every proposal under `specs/skill-proposals/`.
- [x] Invalid artifacts fail with the proposal path and actionable field/section error; projects without the directory are unchanged.

## Tasks

### Phase 1: Research
- [x] Map parser, path-containment, and validation orchestration seams.

### Phase 2: Tests (TDD)
- [x] TEST-019A: valid create, update, and no_action fixtures pass.
- [x] TEST-019B: malformed metadata, sections, paths, lifecycle, pins, and independence cases fail.
- [x] TEST-019C: project-wide validation and absent-directory compatibility pass.

### Phase 3: Implementation
- [x] IMPL-019A: implement deep proposal loader/validator and CLI dispatch.

### Phase 4: Review
- [x] Focused and full tests pass; Task 7 review approves.

## Definition of Done

- [x] All acceptance criteria met; tests pass; review approved; usage knowledge and log updated.
