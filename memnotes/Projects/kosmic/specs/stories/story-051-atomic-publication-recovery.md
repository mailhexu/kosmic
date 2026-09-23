---
status: done
created: 2026-09-14
updated: 2026-09-16
linked_epic: ../epics/epic-25-managed-run-destructive-cleanup.md
linked_architecture: ../architecture-managed-run-workspaces.md
linked_prd: ../prd-managed-run-workspaces.md
related_notes: [notes/managed-run-workspace-lifecycle.md, notes/atomic-skill-publication.md]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: true
routine_proposals: [../skill-proposals/2026-09-14-atomic-publish-tree-recovery.md]
review_base: ""
review_round: 0
---

# Story 051: Atomic Publication Recovery

## User Story

As a maintainer, I want expired destination-sibling staging recovered by its owning publication routine so that crashes no longer leave permanent debris and canonical visibility remains atomic.

## Approval Blocker

This story remains `draft` until the shared routine proposal declared here exists, is non-pending, includes required baseline/candidate behavioral evidence, and is Maintainer-approved. Story 056 establishes the marker/detection half of the same contract first.

## Acceptance Criteria

- [ ] Recovery examines only a caller-supplied destination and exact reserved siblings, acquires the destination lock, and validates Story 056 markers.
- [ ] Restore, finish, or retire occurs only after proving the old/new canonical state and preserves exactly one valid canonical tree at every observable point.
- [ ] Ambiguous, malformed, active, unrelated, wrong-owner, and unsupported candidates remain report-only.
- [ ] Injected crashes across every recovery phase converge without losing the prior valid tree or deleting unrelated siblings.
- [ ] Source-worktree Git status is recorded before and after recovery and the accepted routine proposal's behavior matrix passes.

## Tasks

### Phase 1: Research
- [ ] Complete or revalidate the shared routine proposal before implementation.
- [ ] Define destination identity and formal restore/finish/retire proofs.

### Phase 2: Tests
- [ ] Write failing destination-lock, ambiguity, unrelated-sibling, and every-phase recovery tests.
- [ ] Extend one-visible-tree tests through all recovery branches.

### Phase 3: Implementation
- [ ] Implement destructive recovery inside the publication routine only.
- [ ] Activate restore, finish, and retire after the evidence gate.

### Phase 4: Review
- [ ] Run routine behavioral comparison and full publication regressions.
- [ ] Complete dedicated security and Standards/Spec review.

## Routine Decision

This materially extends `kosmic/atomic-publish-tree`; the linked Task P routine proposal must be accepted before implementation.

## Definition of Done

- [ ] Every recovery phase preserves exactly one valid canonical tree.
- [ ] Ambiguous/untrusted candidates preserve all data.
- [ ] Baseline and final Git status, routine inventory, notes, and project log are current.
- [ ] Security and code reviews have no unresolved Blocking finding.
