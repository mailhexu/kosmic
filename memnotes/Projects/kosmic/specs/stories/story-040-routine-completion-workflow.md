---
status: done
created: 2026-09-07
updated: 2026-09-07
linked_epic: ../epics/epic-21-routine-governance.md
linked_architecture: ../architecture-procedure-compilation.md
linked_prd: ../prd-procedure-compilation.md
proposal_required: false
review_base: c52ab6a15b2dab0df9cbd450a76fcdc386612cdb
review_round: 1
consumer_interface_change: true
related_notes: [cli-projection-commands.md]
evidence_packs: [2026-09-07-procedure-compilation]
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
---

# Story 040: Routine Completion Workflow

## Story

As a Maintainer, I want work-item and Distillation gates for routine decisions so that mechanics cannot bypass review or silently duplicate code.

## Acceptance Criteria

- [x] Add `routine_decision_required` and `routine_proposals` to Story and Quick Task templates with legacy absence as no-op.
- [x] Gate true declarations on valid decisions, evidence, exact consumer approvals, reciprocal edges, caller migration, and convergent review; add a mandatory `routine_edge_change` declaration whose true value requires `routine_decision_required: true`.
- [x] Gate false declarations on an explicit Routine Decision reason.
- [x] Extend Task 9 classification and Task P instructions with inventory-first search, judgment/routine/mixed outcomes, procedure-role-only eligibility, uncertain-material `no_action`, and recorded repetition-or-waiver plus query result.
- [x] Add completion tests covering absent, false, false-with-edge-change, reuse, create/extend, missing approval/evidence/link, and Consumer Interface early-return ordering.

## Routine Decision

This story implements governance workflow rather than repeated mechanics; `routine_decision_required` is false.

## Tasks

- [x] Write focused failing workflow-gate tests.
- [x] Implement work-item, Task 9, and Task P changes.
- [x] Run focused and full regression suites.
- [x] Complete Standards and Spec review.

## Definition of Done

- [x] All acceptance criteria pass through public CLI behavior.
- [x] Templates and task references match the gates.
- [x] No Blocking, High, or Medium review finding remains.
