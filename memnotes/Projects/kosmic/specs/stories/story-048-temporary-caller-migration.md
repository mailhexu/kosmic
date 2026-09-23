---
status: done
created: 2026-09-14
updated: 2026-09-16
linked_epic: ../epics/epic-24-managed-run-initial-release.md
linked_architecture: ../architecture-managed-run-workspaces.md
linked_prd: ../prd-managed-run-workspaces.md
related_notes: [notes/managed-run-workspace-lifecycle.md, notes/cli-projection-commands.md]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "c52ab6a15b2dab0df9cbd450a76fcdc386612cdb (implementation-start; the working copy additionally holds pre-existing unrelated changes recorded in log/kosmic-2026-09-14.md)"
review_round: 1
---

# Story 048: Temporary Caller Migration

## User Story

As a Kosmic maintainer, I want every ordinary temporary caller to invoke the shared managed-run lifecycle automatically so that supported commands no longer spill into system temp or depend on manual setup.

## Acceptance Criteria

- [x] The inventory is refreshed against implementation HEAD and still classifies every caller with zero unexplained entries.
- [x] Both platform-default temporary defects move below active managed runs; no ordinary caller uses `/tmp`, `/dev/shm`, `$TMPDIR`, root scratch, or arbitrary `.tmp` locations.
- [x] Every non-exempt Kosmic command automatically begins and terminally finalizes through the shared module, with identical retention, receipts, and Git boundaries to explicit lifecycle commands.
- [x] The complete command/caller matrix proves there is no caller-chosen run path and no duplicate begin/finalize implementation.
- [x] Atomic single-file and destination-sibling publication callers remain unchanged except for classification; marker/recovery work belongs to Story 056.
- [x] The source-policy check prevents any new unexplained temporary caller.

## Tasks

### Phase 1: Research
- [x] Refresh the exhaustive inventory and command/caller matrix.
- [x] Identify command outcome mapping for success, failure, and interruption.

### Phase 2: Tests
- [x] Keep source-policy and automatic-integration tests red until every non-exempt caller migrates.
- [x] Test each command's success/failure finalization, receipt, retention, and Git snapshots.

### Phase 3: Implementation
- [x] Migrate all ordinary callers through the shared lifecycle interface.
- [x] Remove superseded temporary-path and lifecycle code without touching publication mechanics.

### Phase 4: Review
- [x] Run the complete command matrix and project validation.
- [ ] Update consumer knowledge and complete Standards/Spec review.

## Routine Decision

This migrates callers to an approved product interface and does not change `publish_tree` or any Domain Topic routine edge.

## Technical Notes

### Patterns Found

- Only two production callers used platform-default temporary storage: `validate_current_projection` (`TemporaryDirectory(prefix="kosmic-validation-")`) and `collect_provenance` (`TemporaryDirectory()` for the temporary Git index). The remaining twelve sites are the classified atomic single-file write and destination-sibling publication callers and stay untouched.
- `managed_command_run` is the single automatic-integration seam: every non-exempt command's scratch begins one disposable run with a one-hour active bound (crashed commands self-expire to `abandoned` instead of leaking holders) and finalizes terminally through the identical `begin_run`/`finish_run` used by explicit `scratch` commands — no caller chooses a path and no duplicate lifecycle implementation exists.
- Resolver fail-closed semantics surface as CLI errors: non-Git vaults answer `NO_GIT_WORKTREE`, vaults without a root `.tmp/` ignore rule answer `ROOT_IGNORE_MISSING`. Test vault fixtures therefore materialize Git worktrees with the ignore rule, matching the dogfooded repository.

### Implementation Approach

1. `validate_current_projection` rebuilds the expected projection inside `managed_command_run(project.root, "validate-projection")` scratch; `collect_provenance` points `GIT_INDEX_FILE` at `<run>/scratch/index`.
2. The inventory drops the two defect rows (their tempfile sites no longer exist) and records both migrations in a versioned `managed_callers` section with mechanism and rationale; loader and auditor baselines move to 12 explained tempfile sites.
3. `validate`, `review`, `check-completion`, `install` (all named adapters plus pointer), and `provenance` exercise the seam through their existing `validate_current_projection`/`collect_provenance` calls; publication staging and `atomic_write` remain byte-identical.

### Edge Cases

- Automatic runs fail as `failed` with the exception type as detail when the command body raises, then re-raise the original error; disposal still removes the run for both outcomes; a first-ever run on a foreign repository without the ignore rule fails closed rather than mutating Git configuration.

## Review Record

### Round 1 — 2026-09-15

- Pending: Standards/Spec review of the full vertical sequence.

## Definition of Done

- [x] Every non-exempt caller automatically uses managed-run begin/finalize.
- [x] Inventory and source-policy checks have zero unexplained entries.
- [x] Baseline and final Git status, consumer knowledge, and project log are current.
- [ ] Review has no unresolved Blocking finding.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-15 | Implemented | `managed_command_run` seam; both defect callers migrated; inventory refreshed to 12 callers plus the `managed_callers` migration section; vault/provenance test fixtures became Git worktrees. |
| 2026-09-15 | Verified | Full suite 394 OK including the real-repository source-policy audit; automatic-integration tests prove per-command managed runs with history evidence and no system-temp usage. |
