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
local_id: "008"
---

# Story 050: Destructive Run Garbage Collection

## User Story

As a maintainer, I want explicit expired-run garbage collection activated through the proven cleanup transaction so that bounded lifetime is enforceable without risking active runs or user files.

## Acceptance Criteria

- [ ] `gc --apply` selects only valid expired immediate run children already identified by dry-run and never accepts manifest-derived deletion paths.
- [ ] Competing collectors cannot both quarantine or delete one run; active locks, grace candidates, malformed entries, and unsupported filesystems preserve all data.
- [ ] Descriptor-relative no-follow validation and symlink-resistant removal withstand top-level, nested, and ancestor swap attempts.
- [ ] Fault injection after every journal, Git, lock, rename, `fsync`, removal, history, and rotation boundary recovers idempotently.
- [ ] Explicit GC uses the identical `CleanupTransaction` and receipts as owner cleanup; no second destructive implementation exists.
- [ ] Before/after Git records prove that no path outside `.tmp/kosmic/` changed.

## Tasks

### Phase 1: Research
- [ ] Reverify destructive prerequisites on every supported filesystem/runtime.
- [ ] Define operational rollback and disable procedure.

### Phase 2: Tests
- [ ] Write concurrent collector, active lease, expiry, symlink race, malformed, device, permission, and fault-boundary tests.
- [ ] Add actual CLI dry-run/apply smoke scenarios.

### Phase 3: Implementation
- [ ] Activate explicit `gc --apply` only through `CleanupTransaction`.
- [ ] Add stable destructive receipts and operational diagnostics.

### Phase 4: Review
- [ ] Complete dedicated security review before activation.
- [ ] Complete Standards/Spec review and rerun the destructive matrix.

## Routine Decision

This activates the approved cleanup interface and introduces no new Domain Topic routine edge.

## Definition of Done

- [ ] All destructive race, containment, fault, and Git-evidence scenarios pass.
- [ ] Unsupported or ambiguous cases fail closed.
- [ ] Baseline and final Git status, consumer knowledge, and project log are current.
- [ ] Security and code reviews have no unresolved Blocking finding.
