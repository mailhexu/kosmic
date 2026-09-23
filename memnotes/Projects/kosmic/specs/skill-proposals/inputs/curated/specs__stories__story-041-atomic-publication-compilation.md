---
status: approved
created: 2026-09-07
updated: 2026-09-07
linked_epic: ../epics/epic-22-routine-publication-dogfood.md
linked_architecture: ../architecture-procedure-compilation.md
linked_prd: ../prd-procedure-compilation.md
proposal_required: true
skill_proposal: ../skill-proposals/2026-09-07-atomic-publish-tree.md
review_base: ""
review_round: 0
consumer_interface_change: true
related_notes: []
evidence_packs: []
routine_decision_required: true
routine_proposals: [../skill-proposals/2026-09-07-atomic-publish-tree.md]
---

# Story 041: Atomic Publication Compilation

## Story

As a Maintainer, I want repeated directory publication compiled into one deep routine so that rollback behavior has one tested owner.

## Acceptance Criteria

- [ ] Create and approve a Task P create proposal for `kosmic/atomic-publish-tree` with baseline-versus-candidate behavioral evidence and all consumer approvals.
- [ ] Implement `publish_tree(staged, destination, managed_paths=None)` with containment checks, staging, backup, rollback, cleanup, and failure injection.
- [ ] Register the routine with literal metadata, explicit callers/tests, deterministic/offline properties, and bounded side effects.
- [ ] Migrate `generate`, `migrate_notes_bundle`, MathDocs synchronization, and `generate_library`; delete `publish_directory` and `_replace_generated`.
- [ ] Behavioral tests cover absent/existing destinations, whole/managed modes, nested paths, every mutation-boundary failure, restoration, and cleanup.

## Routine Decision

Repeated atomic publication is the approved first routine candidate; the linked proposal governs creation and evidence.

## Tasks

- [ ] Create and approve the routine proposal.
- [ ] Write failure-injection tests before implementation.
- [ ] Implement and migrate all four callers cleanly.
- [ ] Run focused and full regression suites.
- [ ] Complete Standards and Spec review.

## Definition of Done

- [ ] All acceptance criteria and the routine proposal pass.
- [ ] Obsolete publication implementations are absent.
- [ ] No Blocking, High, or Medium review finding remains.
