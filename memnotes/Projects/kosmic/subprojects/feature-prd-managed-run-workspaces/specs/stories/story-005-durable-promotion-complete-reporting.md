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
local_id: "005"
---

# Story 047: Durable Promotion and Complete Reporting

## User Story

As a contributor, I want useful run output promoted deliberately and every workspace entry reported completely so that durable artifacts are auditable and unknown material is preserved.

## Acceptance Criteria

- [x] `scratch promote` accepts only a contained regular-file source and worktree-relative destination through a verified handle file.
- [x] Default promotion atomically refuses an existing destination; explicit overwrite records and verifies its exact precondition.
- [x] Source, stage, and destination hashes agree; Git status is captured before and after; a durable receipt records the exact resulting delta.
- [x] Crash recovery finishes only a matching recorded publication and never removes or replaces an unexpected destination.
- [x] Status and dry-run GC report every required category, secondary flags, stable reason codes, per-category counts, total/selected bytes, expiry, and partial-report state.
- [x] Reporting and promotion do not follow links, cross devices, capture ambient secrets, or turn unattributed files into owned material.

## Tasks

### Phase 1: Research
- [x] Verify no-clobber `os.link` and explicit-overwrite behavior for supported filesystems.
- [x] Confirm reporting bounds and byte-accounting rules.

### Phase 2: Tests
- [x] Write failing promotion no-clobber, overwrite-precondition, hash, Git-failure, crash, and ambiguity tests.
- [x] Write mixed-category, byte-total, unstable-tree, symlink, device, and seeded-secret report tests.

### Phase 3: Implementation
- [x] Implement `PromotionTransaction` and CLI adapter.
- [x] Complete `RunReport`, status, and dry-run GC output.

### Phase 4: Review
- [x] Run actual promotion and mixed-workspace smoke scenarios.
- [ ] Update consumer knowledge and complete security/Standards/Spec review.

## Routine Decision

Promotion and reporting are approved feature interfaces rather than procedure-compiled mechanics. No `uses_routines` edge or routine proposal is introduced.

## Technical Notes

### Patterns Found

- Default publication uses `os.link(stage, destination, src_dir_fd=..., dst_dir_fd=...)`: same-descriptor-parent hardlink creation is atomic and fails `EEXIST` on any existing destination; explicit overwrite records the prior destination hash as the precondition before `os.replace`.
- Promotion from an **active** run must not take the run lock (the holder holds it for the whole active lifetime); instead the source is opened no-follow **first**, so the descriptor survives a concurrent finalize/quarantine/rmtree and the copied bytes stay consistent.
- Byte accounting and classification share `_tree_bytes` (no-follow, same-device) and `_static_run_classification`, so reporting and promotion observe the same trust boundaries.

### Implementation Approach

1. `promote_file` validates a run-relative source (no absolute/`..`, regular file, no-follow opens) and a worktree-relative destination (created parents walk the toplevel descriptor-relatively), records the destination precondition, stages a private `0600` sibling, fsyncs and re-hashes it, publishes by link or recorded replace, fsyncs the parent, verifies the destination hash, captures Git after state, journals `planned -> staged -> published -> recorded`, appends history, and returns the `PromotionReceipt`.
2. `report_runs` classifies every immediate child of `runs/`, every operation/quarantine remnant, every handle (active handles with existing runs are covered by their run entry; orphan handles and receipts are listed), and every unattributed child of the kosmic root, producing counts, total/selected bytes, warn thresholds, expiry, stable reason codes, and `PARTIAL` for unreadable subtrees or truncation.
3. Categories follow AD-MRW12: `active` (live, incl. `finalizing` under lease), `retained` (interrupted finalization, pending operations, unexpired failures, receipts, quarantine remnants), `expired` (eligible terminal runs and expired receipts), `abandoned` (TTL-expired or unlocked candidates with in-grace/grace-elapsed flags), `oversized` (with the underlying category preserved as a flag), `malformed`, and `unattributed`. A `selected` flag marks GC-selection; `selected_bytes` sums exactly those entries.

### Edge Cases

- `DESTINATION_EXISTS` leaves user content untouched; overwrite preconditions record the prior hash; escaping/symlinked sources and out-of-worktree destinations reject with stable codes; `oversized` retains `retained`/`expired` identifiability; partial reports never hide entries; `gc --apply` still refuses (`GC_APPLY_DISABLED`).

## Review Record

### Round 1 — 2026-09-15

- Pending: security/Standards/Spec review of the full vertical sequence.

## Definition of Done

- [x] All acceptance criteria and focused tests pass.
- [x] No-overwrite and Git-evidence contracts are proven on the real CLI.
- [ ] Review has no unresolved Blocking finding.
- [x] Baseline and final Git status, consumer knowledge, generated projection, and project log are current.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-15 | Implemented | `promote_file` journaled publication with hash verification and Git evidence; complete `RunReport` classification with byte accounting, flags, thresholds, and `scratch promote/status/gc` CLI verbs. |
| 2026-09-15 | Verified | Containment/no-clobber/overwrite/hash/report-category/partial-report tests plus a real cross-process CLI promotion smoke; focused suite 75 OK, full suite 394 OK. |
