---
status: "done"
created: "2026-09-14"
updated: "2026-09-16"
linked_epic: "../epics/epic-002-managed-run-initial-release.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/managed-run-workspace-lifecycle.md", "../../../../notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "c52ab6a15b2dab0df9cbd450a76fcdc386612cdb (implementation-start; the working copy additionally holds pre-existing unrelated changes recorded in log/kosmic-2026-09-14.md)"
review_round: 1
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "story"
local_id: "010"
---

# Story 052: Owner Cleanup Transaction and Recovery

## User Story

As a contributor, I want terminal owner cleanup journaled and recoverable so that successful scratch disappears without risking user files after a crash.

## Acceptance Criteria

- [x] Owner finalization uses planned, quarantined, deleted, and recorded states with Git before/after snapshots and the exact synchronization order from AD-MRW7.
- [x] Descriptor-relative validation, active-lock refusal, same-device quarantine, and symlink-resistant recursive removal fail closed when any prerequisite is unavailable.
- [x] Fault injection after every durable journal boundary (planned, quarantined, deleted, recorded/history) recovers idempotently; lock, rename, `fsync`, and Git-capture failures fail closed to the last durable state with stable codes (`RUN_ACTIVE`, `DEVICE_MISMATCH` with post-rename device revalidation, `SYNC_FAILED`, `GIT_CAPTURE_FAILED`) instead of advancing the journal.
- [x] History rotates atomically at 10 MiB, omits records older than thirty days, preserves records needed by incomplete operations, and retains the operation record until history commit succeeds.
- [x] General `gc --apply` remains disabled; only the finalizing owner may invoke destructive cleanup.

## Tasks

### Phase 1: Research
- [x] Verify directory synchronization and symlink-resistant removal on the supported platform.
- [x] Enumerate every recovery quadrant and history-rotation precondition.

### Phase 2: Tests
- [x] Write failing containment, active-lock, device, permissions, nested symlink, and competing owner tests.
- [x] Inject failure at every cleanup and history boundary, including exact size/age limits.

### Phase 3: Implementation
- [x] Implement `CleanupTransaction`, operation recovery, and bounded history.
- [x] Integrate owner cleanup with terminal receipts from Story 046.

### Phase 4: Review
- [x] Run real owner-cleanup smoke scenarios.
- [ ] Complete dedicated security and Standards/Spec review.

## Routine Decision

This is feature-specific implementation behind the approved run interface and creates no Domain Topic routine edge.

## Technical Notes

### Patterns Found

- `shutil.rmtree.avoids_symlink_attacks` is `True` on this platform; the transaction refuses `DESTRUCTIVE_UNSUPPORTED` before planning when it is not.
- Recovery must be **quadrant-driven**, not journal-state-driven: a crash between the quarantine rename and its journal write leaves state `planned` with the source absent and the quarantine child present, so `_execute_cleanup_transaction` decides from `(source_present, quarantine_present)` and rewrites the journal to the observed state before advancing.

### Implementation Approach

1. `_execute_cleanup_transaction` plans (pre-cleanup Git snapshot + summary + `planned` record), acquires the run lock non-blockingly (refusing `RUN_ACTIVE`), revalidates eligibility under the lock, `os.rename`s the run into a unique `quarantine/<operation-id>/` child with both directories fsynced, `rmtree(dir_fd=)`s it after an `lstat` revalidation, then captures the post-removal snapshot, appends history, records `recorded`, and unlinks the operation record.
2. `finish_run` holds the reacquired lock across finalization and passes it into owner cleanup (`held_lock_fd`), avoiding a self-conflicting second `flock`.
3. `recover_cleanup_operations` reprocesses every operation record: both-present is a report-only conflict; source-only resumes quarantine; quarantine-only resumes removal; neither observes deletion, records a recovery Git snapshot, and commits history. Recorded leftovers are removed; orphan quarantine children are report-only.
4. `_history_append` fsyncs the appended line, then `_rotate_history` rewrites through same-parent atomic replacement at the 10 MiB cap, dropping records older than thirty days unless their operation is still incomplete.

### Edge Cases

- Faults at `cleanup-after-planned`, `cleanup-after-quarantine`, `cleanup-after-removed`, `cleanup-after-history`, and `after-receipt` each converge through recovery or owner replay; relaxed-mode (`0755`) runs are report-only `UNTRUSTED_OWNER_MODE`; foreign files under `.tmp/kosmic/` and unrelated worktree files are never touched; cleanup failure records `pending:<code>` in the receipt instead of losing the terminal state.

## Review Record

### Round 1 — 2026-09-15

- Pending: dedicated security review plus Standards/Spec review of the full vertical sequence.

## Definition of Done

- [x] Every injected failure converges to a valid or report-only state.
- [x] History size/age bounds and Git before/after evidence are proven.
- [x] Baseline and final Git status, consumer knowledge, and project log are current.
- [ ] Review has no unresolved Blocking finding.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-15 | Implemented | Journaled quadrant-driven cleanup transaction, idempotent operation recovery, bounded rotating history, and owner-cleanup integration inside `finish_run`. |
| 2026-09-15 | Verified | Fault injection at every journal boundary, recovery-quadrant tests, rotation-bound tests, and unrelated-file preservation tests; focused suite 75 OK, full suite 394 OK; `gc --apply` still refuses with `GC_APPLY_DISABLED`. |
