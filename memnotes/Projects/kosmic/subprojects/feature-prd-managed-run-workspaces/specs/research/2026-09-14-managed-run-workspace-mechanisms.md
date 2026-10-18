---
status: "done"
created: "2026-09-14"
updated: "2026-09-14"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
open_questions: ["shutil.rmtree symlink hardening details to verify in story Phase 1", "holder spawn under restricted sandboxes"]
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "research"
local_id: "2026-09-14-managed-run-workspace-mechanisms"
---

# Research: Managed Run Workspace Mechanisms (Lease, Quarantine, Deletion)

## Question

Which Python 3.11+ standard-library lock primitive and filesystem arrangements can hold one real operating-system lease for a run that spans multiple independent agent tool calls (PRD Open Questions 1 and 2), and which rename/quarantine/deletion and filesystem semantics keep cleanup crash-safe and contained?

## Context

- PRD `prd-managed-run-workspaces.md` (approved 2026-09-14): FR-MRW06 (real OS lease; cleanup acquires it non-blockingly and revalidates), FR-MRW23 (begin/succeed/fail/status across tool calls), FR-MRW13 (journal → quarantine → delete without following symlinks), FR-MRW08 (24 h unlocked-grace, fail closed), NFR-MRW06 (stdlib-only, deterministic, fails closed), NFR-MRW02/NFR-MRW03 (concurrency, PID reuse, crash consistency).
- Each agent tool call is a separate short-lived process. Any lease state held only in a calling process's memory or fd table dies with that process, so "spanning tool calls" requires the lease to outlive every caller.
- PRD explicitly rules out a short-lived PID record as the lease ("The Architecture decides the lease-holder mechanism. A short-lived PID record is not sufficient."); PID/host are diagnostic fields only.

## Sources

- Linux man-pages 6.19, `flock(2)`: https://man7.org/linux/man-pages/man2/flock.2.html
- Linux man-pages, `rename(2)` (`rename`, `renameat`, `renameat2`): https://man7.org/linux/man-pages/man2/rename.2.html
- Python 3 docs, `fcntl` module (`flock`, `lockf`): https://docs.python.org/3/library/fcntl.html
- Git documentation, `git-status` porcelain v2 and `-z`: https://git-scm.com/docs/git-status
- Git documentation, ignore pattern semantics: https://git-scm.com/docs/gitignore
- Python 3 documentation, `shutil.rmtree`, `dir_fd`, and `avoids_symlink_attacks`: https://docs.python.org/3/library/shutil.html
- PRD: `../prd-managed-run-workspaces.md`

## Findings

### Lease primitive: `flock` semantics

- `flock()` locks are associated with an **open file description**, not with a path or a process: descriptors duplicated via `fork(2)` or `dup(2)` refer to the *same* lock, and the lock is released only when **all** such descriptors are closed or an explicit `LOCK_UN` is issued. Locks survive `execve(2)` [flock(2) DESCRIPTION].
- Corollary (documented close-release semantics): when the holding process crashes or is killed, the kernel closes its descriptors and the lock is released with no userspace participation — there is no stale-lock-file recovery problem. Reboot clears all locks likewise; the PRD's 24 h unlocked-active grace covers that residual case.
- Locks are **advisory** only; `LOCK_NB` acquisition of a held file fails with `EWOULDBLOCK` [flock(2) NOTES, ERRORS]. This gives a cheap, race-free liveness probe for any later tool-call process: open `RUN.lock`, try `LOCK_EX|LOCK_NB`; `EWOULDBLOCK` ⇒ lease alive.
- Lock conversion (shared↔exclusive) is **not atomic** — avoid conversions in the protocol [flock(2) NOTES].
- Filesystem scope: on NFS since 2.6.12 `flock` is emulated as whole-file `fcntl` byte-range locks (exclusive requires write-open); on CIFS since 5.5 it is emulated as SMB byte-range locks with non-advisory `EACCES` side effects [flock(2) VERSIONS]. Lock guarantees therefore hold on local filesystems; on network filesystems the design must fail closed (NFR-MRW06), which the worktree-local `.tmp/kosmic/` root makes the normal case.
- Python: `fcntl.flock(fd, op)` wraps `flock(2)` and raises `OSError` on failure; `fcntl.lockf` wraps the `fcntl(2)` record-lock calls and documents a portability quirk (`LOCK_NB` failure surfaces as `errno` `EACCES` or `EAGAIN` — check both) [Python `fcntl` docs]. The `fcntl` module is Unix-only (not WASI).

### Cross-call holder

- Because the lock lives on an open file description, it can be held across tool calls only if **some process keeps the descriptor open for the whole run**. None of the per-call processes qualifies; the lease therefore needs a small detached holder process spawned at `begin` and terminated at finalization.
- The lock is on the *inode*, not the path: renaming or unlinking the lock file would not release a live holder's lock, but any later probe opening the (new/absent) path would test a different inode. Cleanup must consequently **acquire the lock on the existing path before any rename**, exactly the order FR-MRW13 already mandates.
- `PR_SET_PDEATHSIG`-style parent-death wiring must **not** be used for the holder: the spawning *begin* tool call legitimately exits at the end of the call, which would kill the lease immediately [design inference].

### Quarantine and deletion

- `rename()` atomically replaces an existing `newpath` ("no point at which another process ... will find it missing"), and if the operation fails with `newpath` existing, an instance of `newpath` is left in place [rename(2) DESCRIPTION]. For directory sources, `newpath` must not exist or must be an empty directory (`ENOTEMPTY`/`EEXIST` otherwise) [rename(2) ERRORS]. A quarantine target under a fresh unique operation-id therefore gets pure create-no-clobber semantics from plain `os.rename`.
- `EXDEV` is raised across mount points, *even when the same filesystem is mounted twice* [rename(2) ERRORS]: `runs/` and `quarantine/` must be verified to share `st_dev` before cleanup, else fail closed.
- Open file descriptors for the renamed path are unaffected by the rename [rename(2) DESCRIPTION]: concurrent writers holding open fds keep writing into the quarantined (then unlinked) inode, while path-based writers fail — neither corrupts the operation; anything a stray writer recreates under `runs/` is unattributed and report-only per FR-MRW12/FR-MRW14.
- `EBUSY` may be returned for a directory in use (e.g., as some process's cwd) but is not guaranteed [rename(2) ERRORS]: treat it as retryable and verify post-state rather than assuming.
- `renameat2` offers `RENAME_NOREPLACE`/`RENAME_EXCHANGE` but requires per-filesystem support and is not exposed by `os.rename` in the standard library [rename(2) DESCRIPTION]: the stdlib design sticks to plain `os.rename` with a unique never-existing destination; no exchange semantics are needed for quarantine.
- Atomicity of `rename` is with respect to concurrent observers, not power loss: journal commit order and any directory-`fsync` durability policy belong to Architecture (open question below).

## Options Considered

### Option A: Detached holder process + `fcntl.flock` on `RUN.lock` (recommended)

`begin` creates the run, then spawns a minimal detached holder that opens `RUN.lock`, takes `LOCK_EX|LOCK_NB`, and blocks in a bounded poll loop until a release sentinel appears or a maximum lease TTL elapses. `status`/cleanup probe by attempting `LOCK_EX|LOCK_NB` themselves. `finalize` writes the sentinel, then acquires the now-free lock, revalidates state, and applies retention.

**Pros**:
- One real OS lease satisfying FR-MRW06; authority is the kernel lock, never a PID.
- Crash-safe by construction: holder death or reboot releases the lock instantly; leftover directories degrade to the 24 h abandoned path with no stale-lock cleanup.
- Standard-library only; the probe/acquire path is one `os.open` + one `fcntl.flock` per operation.

**Cons**:
- One stray background process per active run; needs a self-TTL so orphans cannot outlive bounded retention.
- Release latency is bounded by the holder's poll interval; restricted sandboxes may forbid detached processes (must fail closed).

### Option B: `fcntl.lockf` (POSIX record locks) in the same holder design

**Pros**:
- Also kernel-managed and auto-released on process death; works over NFS where `flock` is emulated anyway.

**Cons**:
- Record locks have different semantics from `flock` with respect to `fork`/`dup` [flock(2) NOTES] and add nothing for a single dedicated holder; `lockf`'s `LOCK_NB` failure portability (`EACCES` vs `EAGAIN`) is worse to reason about [Python `fcntl` docs]. No advantage; rejected.


### Option C: Timestamp/PID heartbeat lease (pure userspace)

**Pros**:
- No background process.

**Cons**:
- No OS lease at all; violates FR-MRW06; PID reuse and clock skew corrupt authority. Rejected outright by the PRD.

### Option D: `flock(1)` utility holding a sleeping command

**Pros**:
- Same kernel semantics with a battle-tested wrapper.

**Cons**:
- External util-linux dependency; NFR-MRW06 asks for a stdlib core. `fcntl.flock` gives the identical primitive natively. Rejected.

## Interface Designs

Three independent designs were compared under the `design-an-interface` method:

1. **Minimal lifecycle module** — three operations (`begin`, `finish`, `report`) hide all path, lease, Git, and cleanup mechanics. Deep, but incomplete without explicit post-failure extension and promotion.
2. **Supervised per-run holder** — a detached process holds `flock` and serves authenticated lifecycle requests over a private Unix socket. It is the only design that supplies liveness across independent tool calls without a global daemon.
3. **Capability-only token** — persistent token rotation serializes callers but cannot represent liveness; holder death is indistinguishable from inactivity. Rejected as the lease, retained only as accidental cross-run protection.

Recommendation: use the supervised holder internally and expose five cohesive module operations—begin, finish, extend, promote, and report. The holder is per-run and bounded, not a system daemon. Token data remains internal to a private handle file and never substitutes for the kernel lease.

## Recommendation

Adopt **Option A**. Model it as one deep module — a `RunLease` interface with three operations (`hold(run, ttl) -> LeaseHandle`, `probe(run) -> held|free`, `acquire(run) -> lock|busy`) — so state transitions, cleanup, and Kosmic commands consume only "is the lease held" and "release", never holder processes, sentinels, or lock-file protocol. Cleanup keeps the PRD's order (journal → pre-Git capture → non-blocking acquire + revalidate → same-filesystem rename into `quarantine/<op-id>/` → symlink-safe tree removal → post-Git capture → history), and fails closed on `EXDEV`-class `st_dev` mismatch, non-local filesystems, or holder-spawn failure.

## Open Questions

- [ ] Verify current Python 3.11+ `shutil.rmtree` symlink semantics and error-retry hooks (`onexc`) in story Phase 1 before hardening deletion.
- [ ] Verify `subprocess.Popen(..., start_new_session=True)` detach and zombie-reaping behavior (including containers with non-reaping PID 1) for the holder.
- [ ] Complete the Git citation pass (`git-status` porcelain v2 `-z` record grammar incl. rename records, `gitignore`/`info/exclude` precedence for the `.tmp/` rule, `git-worktree` lock/prune and `--git-common-dir` in linked worktrees) — not covered in this truncated pass.
- [ ] Decide the crash-durability policy: where to `fsync` directories after journal/rename commits, and how to fail closed where directory `fsync` is unsupported.
- [ ] Choose the lease ceiling TTL so legitimate long runs never expire silently, aligned with the 24 h abandoned grace.

## Architecture Impact

- Introduce a single `RunLease` module (holder spawn, sentinel release, probe/acquire) as the only owner of lock mechanics; FR-MRW05/FR-MRW13/FR-MRW23 consumers depend on it, not on `fcntl` directly.
- Fix operation-order invariants: lease acquisition always precedes quarantine rename; `RUN.lock` is protocol-internal and never a deletion authority or GC target by itself.
- Encode fail-closed checks as architecture constraints: `st_dev` equality between `runs/` and `quarantine/`, local-filesystem requirement for lock guarantees, `NO_LEASE`-style error on holder-spawn failure instead of a degraded heartbeat fallback.
- Convert the recommendation into an ADR (lease mechanism) and carry the open questions into story Phase 1 research.

## Notes to Capture

- `flock` locks live on the open file description and vanish when the kernel closes a dead process's descriptors — the property that makes a detached-holder `flock` lease crash-safe without stale-lock recovery.
