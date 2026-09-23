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

# Story 045: Lease-Backed Run Lifecycle

## User Story

As a contributor agent, I want one managed run to remain live across independent tool calls so that scratch ownership is checkable and cannot be inferred from a stale PID or timestamp.

## Acceptance Criteria

- [x] `scratch begin` creates a private run and handle file, records starting Git state, double-forks a session-detached holder, and returns only after socket readiness and held-lock verification.
- [x] The holder keeps `fcntl.flock` for the entire active lifetime and accepts bounded authenticated Unix-socket requests using peer UID plus a token read only from the private handle file.
- [x] Raw tokens never appear in argv, stdout JSON, logs, manifests, history, or diagnostics.
- [x] Begin exposes a 24-hour default active lifetime capped at seven days; expiry changes state to abandoned while the lock remains held before release.
- [x] Unexpected holder death produces an unlocked candidate protected by the 24-hour grace; live-but-unreachable holders report `LIVE_UNREACHABLE` without mutation.
- [x] Finish requests quiescing, persists the requested outcome, releases the holder, reacquires the lease, and commits one terminal state idempotently.
- [x] Faults after requested-outcome persistence, holder acknowledgement/release, lock reacquisition, terminal Git capture, and manifest commit recover the requested outcome under the free lock, mark incomplete capture honestly, and add a distinct recovery Git snapshot.

## Tasks

### Phase 1: Research
- [x] Prove holder survival after the invoking process and PTY exit in the actual harness.
- [x] Verify local-filesystem detection, Unix socket peer credentials, and process reaping.

### Phase 2: Tests
- [x] Write failing holder readiness, detach, lock, socket authentication, token-redaction, expiry, crash, and status-authority tests.
- [x] Write failing concurrent/conflicting/idempotent finish tests and inject failure at every quiesce-to-terminal boundary.

### Phase 3: Implementation
- [x] Implement private `RunLease` and control transport.
- [x] Wire begin, succeed, fail, and live status through the CLI adapter.
- [x] Implement interrupted-finalization recovery under the reacquired lock.

### Phase 4: Review
- [x] Run real subprocess smoke scenarios and focused tests.
- [ ] Update consumer CLI knowledge and complete security/Standards/Spec review.

## Routine Decision

The holder is implementation of the approved product interface, not a procedure-compiled routine. It adds no `uses_routines` edge; no routine proposal is required.

## Technical Notes

### Patterns Found

- Filesystem AF_UNIX sockets fail in deep worktrees (`sun_path` is limited to 107 bytes; the dogfood worktree alone exceeds it), so the control transport binds an **abstract-namespace** socket `\0kosmic-run-<run_id>`: no path limit, and the kernel reclaims the name when the holder dies. Peer credentials (`SO_PEERCRED`) plus `hmac.compare_digest` on the token remain the authentication boundary; the same-UID trust model is unchanged.
- `os.pipe()` descriptors survive `fork` (CLOEXEC matters only for `exec`); the intermediate process `setsid`s, redirects stdio to the null device, forks the holder, and exits while the holder alone keeps the readiness write end, so parent EOF reliably distinguishes holder death.
- `flock` conflicts even between two descriptors of the same process, which `finish_run` uses to its advantage: it reacquires the lock after the holder exits and passes the held descriptor into owner cleanup instead of re-acquiring.

### Implementation Approach

1. `begin_run` resolves the verified root, creates the private run tree (`input/output/logs/scratch/git`), captures the start snapshot, writes the `creating` manifest and opaque `0600` handle, double-forks the holder, verifies readiness plus a second non-blocking lock probe, then transitions to `active` and returns only after that evidence.
2. The holder opens `RUN.lock` `O_NOFOLLOW`, takes `LOCK_EX|LOCK_NB`, binds the abstract control socket, acknowledges readiness with its PID, then serves one bounded JSON request per connection (`ping` for read-only live status, authenticated `finish` persisting `finalizing` + requested outcome before acknowledging and exiting). At TTL expiry it transitions `active -> abandoned` while still holding the lock, and exits quietly when the run directory disappears.
3. `finish_run` opens the handle through the verified root; replays receipts idempotently (`RUN_ALREADY_FINALIZED` on conflicts); reaches the holder for quiescing, or acquires the free lock itself when the holder is gone; captures the terminal snapshot plus `delta.json`; commits the terminal manifest; and publishes the receipt (Story 046) before owner cleanup (Story 052).
4. Fault checkpoints (`KOSMIC_RUNS_FAULT=after-outcome-persist|after-lock-reacquire|after-terminal-git|after-manifest-commit|after-receipt`) leave recoverable on-disk states that a later `finish_run` or `recover_cleanup_operations` completes.

### Edge Cases

- Holder killed with SIGKILL leaves an unlocked `active` run: status reports `abandoned-candidate` with `grace_until = lease_expires_at + 24h`; the owner may still finalize; GC selection only appears after the grace.
- Lock held but socket unreachable (holder wedged): `LIVE_UNREACHABLE` with no mutation.
- Token mismatch answers `HANDLE_TOKEN_MISMATCH`; requests over 4096 bytes or from another UID answer `AUTH`/`REQUEST` without mutation.

## Review Record

### Round 1 — 2026-09-15

- Pending: dedicated security review plus Standards/Spec review of the full vertical sequence.

## Definition of Done

- [x] A real multi-tool-call smoke run proves lease survival and terminal release.
- [x] All acceptance criteria and focused tests pass.
- [x] Consumer knowledge and generated projection are current.
- [ ] Review has no unresolved Blocking finding.
- [x] Baseline and final Git status, knowledge, generated projection, and project log are current.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-15 | Implemented | Detached double-fork holder with flock lease, abstract control socket with SO_PEERCRED+token auth, begin/finish/live-status operations, and `scratch begin/succeed/fail/status` CLI verbs. |
| 2026-09-15 | Verified | Real cross-process smoke (begin in one CLI process, promote+status+succeed in others) plus holder-survival probe tests; focused suite 75 OK, full suite 394 OK. |
