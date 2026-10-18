---
status: "done"
created: "2026-09-27"
updated: "2026-09-27"
linked_epic: "../epics/epic-001-project-status-file.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/dream-reflection-workflow.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
depends_on: ["story-002-status-drift-gates.md"]
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "project-status-file"
record_kind: "story"
local_id: "003"
---

# Story 066: Status Workflow Dogfood Release

## User Story

As an agent starting in a managed directory,
I want the workflow to keep STATUS.md current and referenced,
So that I always begin from the true spec picture.

## Acceptance Criteria

- [x] Task 1 reference and `agents_template.md` create/read the binding, generate the first STATUS.md, and reference it in the AGENTS.md section.
- [x] Tasks 0, 5, 6, and 7 references list `generate-status` as a required step after spec creation or any status transition.
- [x] Stable usage knowledge documents the command, binding, drift semantics, and STE-style reading of the file.
- [x] Dogfood: this repository is bound (`status_root` = repo root), STATUS.md generated and committed, a real status flip regenerates it, and validate/completion gates pass end-to-end.
- [x] Full suite, pair generate/validate, and four-adapter router checks green; Standards and Spec reviews converge.

## Tasks

### Phase 1: Research

- [x] Search task references for every spec-event site needing the step.

### Phase 2: Tests (TDD - Write First!)

- [x] TEST-066-1: Fresh fixture project init produces AGENTS.md section + matching STATUS.md (end-to-end).
- [x] TEST-066-2: Dogfood assertions on this repository (binding, generation, flip, gate pass) recorded in evidence.

### Phase 3: Implementation

- [x] IMPL-066-1: Update task references, agents template, usage note, and Skill Pair projection.
- [x] IMPL-066-2: Bind this repo, generate, commit, flip one spec status, regenerate, verify gates.
- [x] IMPL-066-3: Evidence pack, completion gates, full regression, adapter checks, reviews.

### Phase 4: Review

- [x] Behavioral dogfood and full suite pass
- [x] Standards and Spec reviews converge
- [x] Knowledge notes and session log updated

## Routine Decision

Workflow documentation and dogfood only; no routine edge change.

## Technical Notes

The dogfood status flip may use this story's own lifecycle transitions so no
spec is disturbed artificially.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| This repo's ProjectEntry accepts the binding without migration side effects | ⬜ | CLI |

## Definition of Done

- [x] All acceptance criteria met
- [x] Stories 064-065 done
- [x] Dogfood STATUS.md committed and drift-free
- [x] Stable usage note and generated skills current
- [x] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-27 | Created | Initial draft |
