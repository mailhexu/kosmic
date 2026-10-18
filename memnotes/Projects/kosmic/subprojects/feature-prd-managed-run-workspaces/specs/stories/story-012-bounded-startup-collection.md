---
status: "done"
created: "2026-09-14"
updated: "2026-09-16"
linked_epic: "../epics/epic-003-managed-run-destructive-cleanup.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/managed-run-workspace-lifecycle.md", "../../../../notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "story"
local_id: "012"
---

# Story 054: Bounded Startup Collection

## User Story

As a Kosmic user, I want proven cleanup applied incrementally at command startup so that expired runs do not accumulate when manual garbage collection is forgotten.

## Acceptance Criteria

- [ ] Startup collection invokes only the already activated `CleanupTransaction`; it contains no second selector, mutation, or recovery implementation.
- [ ] One startup pass is bounded by configured entry count and selected bytes and reports remaining eligible work.
- [ ] Active, grace-period, malformed, unsupported, and unattributed entries are preserved exactly as in explicit GC.
- [ ] Cleanup failure does not hide or corrupt the primary command result; the command reports a stable maintenance diagnostic.
- [ ] Startup and explicit collection produce equivalent receipts and Git before/after evidence for the same selected run.

## Tasks

### Phase 1: Research
- [ ] Select conservative entry/byte bounds from observed retained-run data.
- [ ] Define primary-command precedence when maintenance fails.

### Phase 2: Tests
- [ ] Write failing bounded-selection, remaining-work, equivalence, and command-precedence tests.
- [ ] Exercise repeated startup convergence without starvation.

### Phase 3: Implementation
- [ ] Add the bounded startup adapter over activated GC.
- [ ] Expose status diagnostics without changing cleanup authority.

### Phase 4: Review
- [ ] Run actual repeated-startup smoke scenarios.
- [ ] Complete security and Standards/Spec review.

## Routine Decision

This reuses the approved cleanup transaction and introduces no new routine edge.

## Definition of Done

- [ ] Startup work is bounded and converges through the same transaction as explicit GC.
- [ ] Primary commands remain correct when maintenance fails.
- [ ] Baseline and final Git status, consumer knowledge, and project log are current.
- [ ] Review has no unresolved Blocking finding.
