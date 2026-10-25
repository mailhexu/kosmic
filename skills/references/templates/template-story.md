---
project_id: {PROJECT_ID}
subproject_id: {SUBPROJECT_ID}
record_kind: story
local_id: "{ALLOCATED_NNN}"
status: draft
created: {DATE}
updated: {DATE}
linked_epic: ../epics/epic-{PARENT_NNN}.md
linked_architecture: ../architecture.md
linked_prd: ../prd.md
related_notes: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
# When true, add: skill_proposal: ../skill-proposals/YYYY-MM-DD-slug.md
# For math-derived implementation, uncomment and populate both:
# derivations: [{slug}]
# math_implementation_files: [relative/source/path.py]
review_base: ""
# Pin review_base to the fixed review baseline before implementation; never move it during re-review.
# review_round counts completed Standards+Spec review pairs: 0 before the first pair, then 1..3.
# finish requires an active phase (approved/in_progress); the review decision lives in completion_review.
review_round: 0
completion_observations: []
completion_review: {}
---

# Story {N}: {Story Title}

## User Story

As a {role},
I want {action},
So that {benefit}.

## Acceptance Criteria

- [ ] Given {context}, when {action}, then {outcome}
- [ ] Given {context}, when {action}, then {outcome}
- [ ] Given {context}, when {action}, then {outcome}

## Tasks

### Phase 1: Research

- [ ] Search memnotes for relevant knowledge
- [ ] Explore codebase for patterns/conventions
- [ ] Identify and verify all assumptions
- [ ] Ask human for clarification if needed
- [ ] Document findings in Technical Notes

### Phase 2: Tests (TDD - Write First!)

- [ ] SCENARIO-001: Write the execution scenario first — one bounded session
      with expected outcomes and refusals; it becomes the disposable smoke.
- [ ] TEST-001: Write test for {scenario}
- [ ] TEST-002: Write test for {scenario}

### Phase 3: Implementation

- [ ] IMPL-001: {task description}
- [ ] IMPL-002: {task description}

### Phase 4: Review

- [ ] All tests pass
- [ ] Code review completed
- [ ] Knowledge notes updated

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed.

## Technical Notes

{To be filled during Research phase. Include:
- Patterns found in codebase
- Relevant knowledge notes
- Implementation approach
- Edge cases to handle}

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| ... | ⬜ | _to verify_ |

## Definition of Done

- [ ] All acceptance criteria met
- [ ] All tests pass
- [ ] Code reviewed and approved
- [ ] Knowledge notes updated
- [ ] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| {DATE} | Created | Initial draft |
| {DATE} | Approved | Ready for implementation |
| {DATE} | Research | Completed research phase |
| {DATE} | Tests | All tests written |
| {DATE} | Implemented | Code complete |
| {DATE} | Reviewed | Code review passed |
| {DATE} | Done | Story complete |
