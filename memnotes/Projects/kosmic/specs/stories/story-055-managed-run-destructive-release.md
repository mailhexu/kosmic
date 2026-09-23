---
status: done
created: 2026-09-14
updated: 2026-09-16
linked_epic: ../epics/epic-25-managed-run-destructive-cleanup.md
linked_architecture: ../architecture-managed-run-workspaces.md
linked_prd: ../prd-managed-run-workspaces.md
related_notes: [notes/managed-run-workspace-lifecycle.md, notes/atomic-skill-publication.md, notes/cli-projection-commands.md]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
---

# Story 055: Managed Run Destructive Release

## User Story

As a Kosmic maintainer, I want the independently proven destructive paths released together so that cleanup is operationally complete and migration-only diagnostics can be removed safely.

## Acceptance Criteria

- [ ] Stories 050, 054, and 051 are done with convergent security and code reviews before release work begins.
- [ ] General run GC, bounded startup collection, and destination-specific publication recovery pass one combined real-worktree acceptance matrix.
- [ ] No destructive operation changes an unrelated path; Git before/after records prove expected deltas.
- [ ] Migration-only diagnostics are removed only after equivalent permanent status/recovery behavior is active.
- [ ] Full suites, project/library generation and validation, completion gates, Evidence Pack, Impact Ledger, notes, release notes, and supported adapter byte checks pass.

## Tasks

### Phase 1: Research
- [ ] Confirm all prerequisite evidence and operational rollback instructions.
- [ ] Define combined release and upgrade scenarios.

### Phase 2: Tests
- [ ] Run the combined destructive acceptance and regression matrices before release edits.
- [ ] Add upgrade coverage for worktrees containing old report-only staging markers.

### Phase 3: Implementation
- [ ] Remove migration-only paths and finalize release artifacts.
- [ ] Install and byte-verify supported adapters.

### Phase 4: Review
- [ ] Complete final Standards, Spec, and security review.
- [ ] Repeat all release and Git-status checks after corrections.

## Routine Decision

This releases previously accepted mechanics and changes no additional routine contract or edge.

## Definition of Done

- [ ] Every prerequisite story and combined release scenario passes.
- [ ] Evidence, impact, notes, generated outputs, adapters, and Git records are current.
- [ ] No migration-only duplicate behavior remains.
- [ ] Review has no unresolved Blocking finding.
