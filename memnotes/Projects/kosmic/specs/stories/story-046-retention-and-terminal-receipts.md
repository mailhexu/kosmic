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

# Story 046: Retention and Terminal Receipts

## User Story

As a contributor, I want each terminal run assigned deterministic retention and a durable receipt so that identical outcomes have identical lifetimes and retries remain safe after restart.

## Acceptance Criteria

- [x] Omitted retention selects diagnostic; disposable and explicitly unknown values behave exactly as approved.
- [x] Diagnostic success is cleanup-eligible, diagnostic failure expires after exactly 72 hours, and disposable terminal outcomes are cleanup-eligible.
- [x] `scratch extend` works only after diagnostic failure, is serialized and idempotent, and cannot exceed seven days from failure.
- [x] Before any run deletion, the private handle file is atomically rewritten as a 30-day terminal receipt containing outcome, expiry, Git hashes, and cleanup eligibility.
- [x] Repeated matching finish/extend returns the existing receipt; conflicting outcome or invalid extension returns a stable error without mutation.
- [x] Consumer outputs never reveal token contents or ambient secrets.

## Tasks

### Phase 1: Research
- [x] Verify receipt lookup and expiry behavior after process restart.
- [x] Confirm consumer output and redaction conventions.

### Phase 2: Tests
- [x] Write failing retention, exact-boundary, extension, repeat/conflict, restart, and receipt-expiry tests.
- [x] Seed token and credential values and require their absence from every owned output.

### Phase 3: Implementation
- [x] Implement retention transitions, `extend_run`, and terminal receipt publication.
- [x] Wire extend and terminal receipt behavior through the CLI adapter without deleting runs yet (deletion arrives with Story 052's owner cleanup).

### Phase 4: Review
- [x] Run focused lifecycle and restart smoke scenarios.
- [ ] Update consumer knowledge and complete security/Standards/Spec review.

## Routine Decision

This implements approved product state transitions and creates no Domain Topic routine edge.

## Technical Notes

### Patterns Found

- `_cleanup_eligible(manifest, now)` centralizes the whole-run retention decision: disposable terminal outcomes and diagnostic successes are immediately eligible; diagnostic/extended-diagnostic failures become eligible exactly at `expires_at = finished_at + 72h`; `abandoned` is eligible.
- Extension rewrites both the manifest (`retention -> extended-diagnostic`, new `expires_at`) and, when the handle is already a receipt, the receipt itself, so restart-safe idempotence needs no extra state.

### Implementation Approach

1. `finish_run` computes expiry from the terminal state and retention class, then `_publish_receipt` atomically rewrites the private handle as a receipt holding only the token hash, outcome, expiry, Git hashes, cleanup state, promotions, and a 30-day `receipt_expires_at`.
2. `extend_run` validates state before touching the lock, revalidates under it, rejects `until > finished_at + 7d` with `EXTENSION_CAP_EXCEEDED`, returns the existing receipt unchanged for `until <= expires_at`, and otherwise extends.
3. Receipt replay: `finish_run` on a receipt returns it for matching outcomes and raises `RUN_ALREADY_FINALIZED` for conflicts; expired receipts surface as `receipt-expired` report entries (Story 047).

### Edge Cases

- Exact 72-hour boundary (`retained` one second before, `expired` at the instant), cap boundary at seven days, extension of an already-extended run, extension requests after cleanup eligibility, ambient `AWS_SECRET_ACCESS_KEY`-style values never captured, and raw token bytes absent from every consumer-visible artifact.

## Review Record

### Round 1 — 2026-09-15

- Pending: security/Standards/Spec review of the full vertical sequence.

## Definition of Done

- [x] Retention and receipt behavior passes every exact boundary and retry case.
- [x] No secret appears in consumer-observable output.
- [x] Baseline and final Git status, consumer knowledge, generated projection, and project log are current.
- [ ] Review has no unresolved Blocking finding.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-15 | Implemented | Retention classes with exact expiry computation, capped idempotent `extend_run`, 30-day terminal receipts, and the `scratch extend` CLI verb. |
| 2026-09-15 | Verified | Exact-boundary tests with a frozen private clock, restart/replay receipt tests, and seeded-secret absence tests; focused suite 75 OK, full suite 394 OK. |
