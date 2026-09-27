---
status: in_progress
created: 2026-09-27
updated: 2026-09-27
linked_epic: ../epics/epic-27-project-status-file.md
linked_architecture: ../architecture-project-status-file.md
linked_prd: ../prd-project-status-file.md
related_notes: [notes/dream-reflection-workflow.md]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
depends_on: [story-065-status-drift-gates.md]
review_base: ""
review_round: 0
---

# Story 066: Status Workflow Dogfood Release

## User Story

As an agent starting in a managed directory,
I want the workflow to keep STATUS.md current and referenced,
So that I always begin from the true spec picture.

## Acceptance Criteria

- [ ] Task 1 reference and `agents_template.md` create/read the binding, generate the first STATUS.md, and reference it in the AGENTS.md section.
- [ ] Tasks 0, 5, 6, and 7 references list `generate-status` as a required step after spec creation or any status transition.
- [ ] Stable usage knowledge documents the command, binding, drift semantics, and STE-style reading of the file.
- [ ] Dogfood: this repository is bound (`status_root` = repo root), STATUS.md generated and committed, a real status flip regenerates it, and validate/completion gates pass end-to-end.
- [ ] Full suite, pair generate/validate, and four-adapter router checks green; Standards and Spec reviews converge.

## Tasks

### Phase 1: Research

- [ ] Search task references for every spec-event site needing the step.

### Phase 2: Tests (TDD - Write First!)

- [ ] TEST-066-1: Fresh fixture project init produces AGENTS.md section + matching STATUS.md (end-to-end).
- [ ] TEST-066-2: Dogfood assertions on this repository (binding, generation, flip, gate pass) recorded in evidence.

### Phase 3: Implementation

- [ ] IMPL-066-1: Update task references, agents template, usage note, and Skill Pair projection.
- [ ] IMPL-066-2: Bind this repo, generate, commit, flip one spec status, regenerate, verify gates.
- [ ] IMPL-066-3: Evidence pack, completion gates, full regression, adapter checks, reviews.

### Phase 4: Review

- [ ] Behavioral dogfood and full suite pass
- [ ] Standards and Spec reviews converge
- [ ] Knowledge notes and session log updated

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

- [ ] All acceptance criteria met
- [ ] Stories 064-065 done
- [ ] Dogfood STATUS.md committed and drift-free
- [ ] Stable usage note and generated skills current
- [ ] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-27 | Created | Initial draft |
