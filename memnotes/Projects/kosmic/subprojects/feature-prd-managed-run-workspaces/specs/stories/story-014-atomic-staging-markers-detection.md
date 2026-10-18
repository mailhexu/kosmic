---
status: "done"
created: "2026-09-14"
updated: "2026-09-16"
linked_epic: "../epics/epic-002-managed-run-initial-release.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/managed-run-workspace-lifecycle.md", "../../../../notes/atomic-skill-publication.md"]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: true
routine_proposals: ["../skill-proposals/2026-09-14-atomic-publish-tree-recovery.md"]
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "story"
local_id: "014"
---

# Story 056: Atomic Staging Markers and Detection

## User Story

As a maintainer, I want destination-sibling staging marked and detected without mutation so that crash-left publication artifacts have bounded, attributable status in the initial release.

## Approval Blocker

This story must remain `draft` until the declared Task P routine proposal exists, is non-pending, has required behavioral evidence, and is Maintainer-approved. Story 051 reuses the same decision for destructive recovery.

## Acceptance Criteria

- [ ] Every sibling stage and backup carries a versioned marker with operation, destination identity, phase, source Git hash, creation time, 24-hour abandoned-candidate grace, and seven-day maximum retention.
- [ ] Destination-scoped detection examines only exact reserved siblings and reports active, grace-period, expired, malformed, or ambiguous state without mutation.
- [ ] The initial release explicitly rejects restore, finish, retire, and general-glob cleanup operations.
- [ ] Marker writes and normal `finally` cleanup preserve the existing one-visible-tree publication invariant.
- [ ] The accepted routine proposal covers the material `kosmic/atomic-publish-tree` contract extension and known callers.

## Tasks

### Phase 1: Research
- [ ] Complete the shared Task P routine proposal before implementation.
- [ ] Map every sibling-staging caller and marker phase.

### Phase 2: Tests
- [ ] Write failing marker schema, bounded-state, destination-scope, no-mutation, and one-visible-tree tests.
- [ ] Inject crashes at each existing publication phase and verify report-only classification.

### Phase 3: Implementation
- [ ] Add marker lifecycle and destination-scoped read-only detection to the publication seam.
- [ ] Migrate every sibling-staging caller to the accepted marker contract.

### Phase 4: Review
- [ ] Run publication regressions and routine-proposal behavioral comparison.
- [ ] Complete security and Standards/Spec review.

## Routine Decision

This materially extends `kosmic/atomic-publish-tree`; the declared Task P routine proposal must be accepted before implementation.

## Definition of Done

- [ ] Every sibling staging caller emits bounded markers and report-only detection.
- [ ] No destructive recovery is enabled.
- [ ] Baseline and final Git status, routine inventory, notes, and project log are current.
- [ ] Review has no unresolved Blocking finding.
