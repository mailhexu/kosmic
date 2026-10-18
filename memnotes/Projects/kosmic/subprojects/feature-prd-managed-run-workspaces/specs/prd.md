---
status: "approved"
created: "2026-09-14"
updated: "2026-09-14"
linked_research: ["research/2026-09-14-managed-run-workspace-mechanisms.md"]
linked_epics: ["epics/epic-001-managed-run-foundation.md", "epics/epic-002-managed-run-initial-release.md", "epics/epic-003-managed-run-destructive-cleanup.md"]
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "prd"
local_id: "prd"
---

# Feature PRD: Managed Run Workspaces

## Problem Statement

Kosmic creates temporary files through Python `tempfile` calls, destination-sibling staging, agent experiments, generated scientific outputs, diagnostic logs, patch scripts, and manually chosen `.tmp` directories. Existing file-hygiene prose asks agents to classify and clean these files, but it supplies neither one path resolver nor enforceable ownership, lifetime, crash recovery, or Git-state records.

Scratch consequently appears in repository roots, arbitrary `.tmp` paths, `/tmp`, and `/dev/shm`. Stale files survive after their purpose ends, while later cleanup cannot safely distinguish Kosmic-owned artifacts from pre-existing or concurrent user work. Broad cleanup risks data loss; manual cleanup is routinely omitted.

Kosmic needs a managed run-workspace lifecycle: one rational worktree-local path, explicit ownership, deterministic bounded retention, mandatory Git-status evidence, and conservative whole-run cleanup. Destination-sibling staging remains a separate exception where same-filesystem atomic replacement requires it, but its lifetime must also be bounded by its owning module.

## Goals

- Place Kosmic-managed scratch under the active worktree's `.tmp/kosmic/` tree, never `/tmp`, `/dev/shm`, the repository root, or ad hoc paths.
- Give each run an owner, purpose, state, deterministic retention class, and deletion deadline.
- Give contributor agents a lease-backed lifecycle interface spanning the tool calls of one run.
- Record Git identity and machine-readable Git status before and after every run, cleanup, and durable promotion.
- Delete successful and disposable runs promptly; retain failed diagnostics only for a bounded period.
- Recover interrupted runs and cleanup operations without deleting active, malformed, unknown, or unattributed material.
- Delete only positively owned Kosmic run directories and preserve unrelated user work.
- Keep skill behavior predictable: one mandatory managed-run step in the orchestrator and one progressively disclosed lifecycle reference as the single source of truth.
- Preserve atomic publication's commit-or-rollback guarantee and same-filesystem staging requirement.

## Non-Goals

- Manage arbitrary user-created files under `.tmp/` or elsewhere in a worktree.
- Infer ownership solely from Git-status deltas, filename patterns, age, process IDs, or directory timestamps.
- Delete unrelated, pre-existing, or concurrently created worktree changes.
- Use `/tmp`, `/dev/shm`, `$TMPDIR`, or platform temporary-directory defaults for Kosmic scratch.
- Replace `pending_tests/`, Evidence Packs, source, specifications, or project logs with temporary storage.
- Provide a general system temporary-file daemon or clean other applications' files.
- Allow run garbage collection to delete destination-sibling publication staging.
- Introduce per-artifact retention state when whole-run retention suffices.
- Persist complete diffs or file contents as Git-status evidence.
- Support managed runs outside a Git worktree in this feature.

## Users and Responsibilities

| Role | Responsibility |
|---|---|
| Contributor agent | Begins a managed run before creating scratch, writes only below its resolved directory, and explicitly finalizes or fails it. |
| Kosmic command | Uses the same lifecycle interface, holds the lease, captures Git state, and applies the declared retention class. |
| Maintainer | Approves lifetime defaults, exceptional staging behavior, and destructive cleanup capability. |
| Reviewer | Confirms every Kosmic-owned artifact is deleted, retained with expiry, or promoted and that Git records explain the resulting worktree delta. |

## Product Decisions

### Canonical path

```text
<git-worktree-root>/.tmp/kosmic/
├── runs/
│   └── <UTC-timestamp>-<sanitized-slug>-<opaque-id>/
│       ├── RUN.json
│       ├── RUN.lock
│       ├── git/
│       │   ├── start-status.porcelain-v2
│       │   ├── finish-status.porcelain-v2
│       │   └── delta.json
│       ├── input/
│       ├── output/
│       ├── logs/
│       └── scratch/
├── quarantine/
├── operations/
└── history.jsonl
```

`.tmp/` is ignored at the worktree root. One resolver derives the root from `git rev-parse --show-toplevel`; commands do not choose scratch paths independently. The absolute worktree path is metadata, never deletion authority. User text is sanitized and combined with an opaque identifier so it cannot introduce separators or collisions.

Managed-run creation outside a Git worktree fails with `NO_GIT_WORKTREE`: neither the canonical root nor the mandatory Git record can be established.

### Agent lifecycle interface

The initial release exposes explicit begin, successful-finalization, failed-finalization, and status operations. They must span multiple agent tool calls while maintaining one real lease; each operation returns a checkable state, run path, and ownership identity. Kosmic commands invoke the same interface automatically rather than duplicating lifecycle mechanics.

The Architecture decides the lease-holder mechanism. A short-lived PID record is not sufficient.

### Retention classes

A run declares one class at creation:

| Class | Success | Failure |
|---|---|---|
| `diagnostic` | Delete during clean finalization | Retain 72 hours |
| `disposable` | Delete during clean finalization | Delete during clean finalization |
| `extended-diagnostic` | Not valid at creation | Explicit post-failure extension, capped at seven days |

If the caller omits the class, Kosmic assigns `diagnostic`; an explicitly supplied unknown class rejects creation. A class may change only from `diagnostic` to `extended-diagnostic` after failure. No class permits indefinite retention.

Supported states are `active -> succeeded|failed|abandoned`. State transitions are serialized and idempotent. An active run holds an operating-system lease for its lifetime. Cleanup acquires the same lease non-blockingly and revalidates state. PID and host fields are diagnostic only. An unlocked active run remains an abandoned candidate for 24 hours before becoming cleanup-eligible.

Malformed, missing-version, future-version, symlinked, unexpectedly owned or permissioned, or otherwise untrusted runs are report-only.

### Git-state record

Every run captures at start and terminal finalization:

```bash
git rev-parse HEAD
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git status --porcelain=v2 --branch --untracked-files=all -z
```

Raw NUL-delimited snapshots live inside the retained run. `RUN.json` records their SHA-256 values, start and finish HEAD and branch identities, and capture completeness. `delta.json` classifies pre-existing, introduced, modified, removed, and renamed paths, but temporal appearance never proves Kosmic ownership.

Every cleanup and durable promotion captures Git state immediately before and after mutation. An interrupted run lacking a finish snapshot is marked incomplete; recovery records a separate status snapshot rather than claiming clean finalization.

Before a finalized run is removed, its bounded run and Git summary is prepared outside that run. After removal and the actual post-removal Git capture, Kosmic commits the result to private rotating history. History stores hashes and classifications, not diffs or contents; it is capped at 10 MiB and thirty days.

### Recoverable cleanup

A run directory is the sole run-GC deletion unit. A manifest can never authorize deletion outside it.

Cleanup uses an operation record outside the run:

```text
planned -> quarantined -> deleted -> recorded
```

It writes the operation record and pre-cleanup Git evidence, acquires and revalidates the lease, atomically renames the immediate run child into `.tmp/kosmic/quarantine/<operation-id>/`, removes that tree without following symlinks, captures actual post-removal Git state, appends history, and marks the operation recorded. Recovery reprocesses operation and quarantine remnants idempotently. Cleanup fails closed when its audit record cannot be persisted.

General garbage collection defaults to dry-run. Destructive garbage collection ships only after its containment, locking, quarantine, crash-recovery, and concurrency behavior passes the specified gates. Owner-driven finalization may remove its own successful or disposable run in the initial release through the same journaled transaction.

### Atomic-publication exception

Transactional staging that must be a sibling of its destination remains owned by the atomic-publication module. It uses reserved names, lifecycle metadata, `finally` cleanup, and module-specific abandoned-stage recovery. Neither run manifests nor run garbage collection can delete it.

The atomic-publication module must identify, report, and safely recover or retire abandoned staging and backup paths after a bounded grace period while preserving exactly one visible old-or-new canonical tree.

### Skill information hierarchy

The Kosmic orchestrator contains one mandatory step: obtain a managed run before creating scratch, with a checkable completion criterion. One external lifecycle reference owns path, retention, Git recording, recovery, cleanup, and exception details. The clean cutover removes duplicated scratch mechanics while preserving distinct durable-file rules for source, Evidence Packs, specifications, project logs, and `pending_tests/`.

## Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| FR-MRW01 | Resolve the sole run root at `<git-worktree-root>/.tmp/kosmic/`; prohibit `/tmp`, `/dev/shm`, `$TMPDIR`, platform defaults, root-level scratch, and arbitrary `.tmp` locations for Kosmic-managed scratch. | must |
| FR-MRW02 | Require a worktree-root ignore rule for `.tmp/`; report a missing or contradictory rule before enabling managed runs. | must |
| FR-MRW03 | Create each run as one immediate child of `runs/` with a sanitized slug, opaque ID, private permissions, and atomically written versioned manifest. | must |
| FR-MRW04 | Record project identity, purpose, timestamps, state, retention class, expiry, owner diagnostics, lease identity, Git hashes, and finalization completeness. | must |
| FR-MRW05 | Provide serialized idempotent transitions from `active` to `succeeded`, `failed`, or `abandoned`; reject regressions and invalid transitions. | must |
| FR-MRW06 | Hold a real operating-system lease for every active run; cleanup must acquire and revalidate it. PID or hostname alone never authorizes cleanup. | must |
| FR-MRW07 | Apply deterministic `diagnostic`, `disposable`, and post-failure `extended-diagnostic` retention exactly as specified; omission selects `diagnostic`, while an explicitly supplied unknown class rejects creation. | must |
| FR-MRW08 | Keep an unlocked active run untouched for a 24-hour grace period; fail closed for destructive cleanup where locking guarantees are unavailable. | must |
| FR-MRW09 | Reject managed-run creation outside a Git worktree with `NO_GIT_WORKTREE`. | must |
| FR-MRW10 | Capture mandatory start and final Git identity/status snapshots and their hashes for every run; record interrupted capture explicitly. | must |
| FR-MRW11 | Capture Git state before and after every cleanup and durable promotion and record exact path classifications without inferring ownership from them. | must |
| FR-MRW12 | Keep general worktree audits advisory for unattributed changes; completion may gate only positively owned Kosmic artifacts. | must |
| FR-MRW13 | Limit run garbage collection to a valid immediate run child; default to dry-run; journal, quarantine, delete without following symlinks, and recover incomplete operations idempotently. | must |
| FR-MRW14 | Treat malformed, unknown-version, symlinked, wrong-owner, wrong-permission, and actively leased entries as report-only. | must |
| FR-MRW15 | Commit cleanup history only after observing removal and capturing post-removal Git status; retain recoverable operation state until that commit succeeds. | must |
| FR-MRW16 | Expose read-only status and dry-run collection reporting active, retained, expired, abandoned, oversized, malformed, and unattributed entries plus disk usage. | must |
| FR-MRW17 | Require explicit durable promotion, default no-overwrite, source/destination hash verification, and recorded before/after Git delta. | must |
| FR-MRW18 | Keep `pending_tests/`, Evidence Packs, source, specs, and project logs under their existing durable governance; workspace retention cannot substitute for them. | must |
| FR-MRW19 | Keep destination-sibling staging separate, with reserved markers, `finally` cleanup, bounded abandoned-state detection, and atomic-publication-owned recovery. | must |
| FR-MRW20 | Produce a versioned inventory classifying every current temporary-path caller and policy occurrence as managed run, atomic staging, durable governed output, or defect; allow zero unexplained entries. | must |
| FR-MRW21 | Migrate every non-exempt caller to the canonical resolver and verify the complete caller/command matrix rather than representative samples. | must |
| FR-MRW22 | Update `skills/SKILL.md`, `skills/README.md`, `task_implement_story.md`, `task_quick_task.md`, and every inventory-discovered consumer in one clean cutover; leave one orchestrator step and one lifecycle reference, not competing policies. | must |
| FR-MRW23 | Expose an agent-facing lease-backed begin/succeed/fail/status interface spanning multiple tool calls; every operation returns a checkable completion result. | must |
| FR-MRW24 | Let Kosmic commands invoke the same lifecycle interface automatically rather than reimplementing it. | should |
| FR-MRW25 | Support bounded startup maintenance by both entry count and bytes only after the destructive-GC invariants pass. | should |
| FR-MRW26 | Report quota pressure and support future configurable per-run and aggregate limits without weakening mandatory time bounds. | should |

## Non-Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| NFR-MRW01 | Safety: no manifest, slug, symlink, Git path, or pattern may expand destructive authority beyond one validated immediate run directory. | must |
| NFR-MRW02 | Concurrency: lifecycle and cleanup remain correct under concurrent commands, competing collectors, PID reuse, crashes, and linked Git worktrees. | must |
| NFR-MRW03 | Crash consistency: manifest, operation, and history updates are atomic; every interrupted mutation leaves a previous valid or report-only recoverable state. | must |
| NFR-MRW04 | Privacy: roots and metadata are private by default; retained logs do not silently capture credentials or secret environment values. | must |
| NFR-MRW05 | Boundedness: retention caps, grace periods, bounded startup work, and history rotation prevent indefinite lifetime. Byte quotas are later hardening under FR-MRW26. | must |
| NFR-MRW06 | Portability: core behavior uses Python 3.11+ standard-library facilities, remains deterministic/offline, and fails closed without required filesystem or locking guarantees. | must |
| NFR-MRW07 | Performance: Git capture and inspection do not scan outside the active worktree and canonical scratch root. | must |
| NFR-MRW08 | Predictability: the skill uses the leading concept `managed run`; every step has a checkable completion criterion, and branch-specific detail is progressively disclosed rather than duplicated. | must |
| NFR-MRW09 | Compatibility: atomic Skill Pair and Shared Library publication retain current commit-or-rollback behavior and never expose partially staged output. | must |
| NFR-MRW10 | Auditability: every surviving Kosmic-owned path maps to a run, expiry, promotion, or governed durable destination with related initial and final Git state. | must |

## Release Boundaries

### Initial release

- Canonical resolver and `.tmp/` ignore validation.
- Agent-facing lease-backed begin/succeed/fail/status lifecycle and automatic command integration.
- Private run creation, atomic state transitions, deterministic retention classes, and exclusive lease.
- Mandatory start/final Git snapshots and bounded history.
- Journaled owner-finalization cleanup for succeeded and disposable runs.
- Failed-run retention, abandoned-run grace period, status, and dry-run garbage collection.
- Advisory worktree audit.
- Versioned exhaustive migration inventory and migration of every non-exempt caller.
- Atomic-publication abandoned-stage detection and bounded module-owned recovery contract.
- Clean skill/reference cutover using the `managed run` leading concept.

### Destructive cleanup release

`gc --apply`, bounded startup cleanup, and destructive abandoned-stage recovery require focused concurrency, containment, symlink, quarantine, operation-recovery, malformed-state, crash-boundary, and linked-worktree verification. They do not ship merely because dry-run discovery exists.

### Deferred

- Cleanup of arbitrary temporary files outside `.tmp/kosmic/`.
- General-run authority over destination-sibling staging.
- Per-artifact lifecycle state machines.
- Cross-worktree shared scratch roots.
- Mandatory byte quotas; time bounds remain mandatory.

## Success Criteria

### Initial release

- [ ] The versioned inventory accounts for every temporary-path caller and policy occurrence with zero unexplained entries.
- [ ] Every non-exempt caller creates scratch only under `.tmp/kosmic/`; no current Kosmic path uses `/tmp`, `/dev/shm`, the worktree root, or arbitrary `.tmp` locations.
- [ ] The agent-facing lifecycle spans multiple tool calls, holds one real lease, and returns checkable begin, success, failure, and status outcomes.
- [ ] Every managed run has valid ownership, state, retention class, lease, expiry, and start/final Git-status records.
- [ ] Successful diagnostic and disposable runs leave no run directory and leave history containing both run Git-status hashes and cleanup before/after hashes.
- [ ] Diagnostic failures expire after exactly 72 hours; authorized extensions cannot exceed seven days.
- [ ] Interrupted runs are reported, receive recovery Git snapshots, and remain protected through the grace period.
- [ ] Non-Git creation fails with `NO_GIT_WORKTREE`.
- [ ] Unattributed user changes remain untouched and advisory.
- [ ] The orchestrator contains one concise managed-run step with a checkable completion criterion; one lifecycle reference owns all branch detail; the inventory finds no competing scratch policy.

### Destructive cleanup release

- [ ] Competing collectors cannot both quarantine or delete one run.
- [ ] Symlink, traversal, malformed, unknown-version, wrong-owner, wrong-permission, and active-lease cases preserve all data and remain report-only.
- [ ] Interruption at every cleanup operation state recovers idempotently and records actual post-mutation Git status before final history publication.
- [ ] Cleanup changes no tracked or untracked path outside `.tmp/kosmic/`; before/after Git records prove the result.
- [ ] Atomic-publication recovery retires expired sibling staging without exposing a mixed or missing canonical tree.

### Cross-release regression gates

- [ ] Promotion refuses unexpected overwrite, verifies hashes, and records the exact resulting Git delta.
- [ ] Retention deadlines and history rotation keep runs and metadata within specified lifetime bounds.
- [ ] Existing atomic-publication rollback and cleanup scenarios continue to pass.
- [ ] Every skill step introduced or modified by the feature has an observable completion criterion.

## Open Questions

- [ ] Which standard-library lock primitive and filesystem set can support a lease across multiple agent tool calls?
- [ ] What concrete mechanism should hold that lease between begin and finalization without relying on PID identity?
- [ ] Which current temporary-path callers require destination-sibling atomic staging rather than ordinary managed scratch?
- [ ] What quota defaults can later protect disk space without unexpectedly killing large scientific diagnostics?

## Review Record

Subagent PRD review applied the `writing-great-skills` principles and initially requested changes. All nine findings were resolved; focused re-review returned **Approve**. The user approved the PRD on 2026-09-14.

| Finding | Resolution |
|---|---|
| PRD-001 | Added a required agent-facing lease-backed lifecycle spanning multiple tool calls. |
| PRD-002 | Added bounded atomic-publication-owned staging recovery. |
| PRD-003 | Added a recoverable cleanup operation journal and post-removal Git recording order. |
| PRD-004 | Moved byte quotas to explicit later hardening while retaining mandatory time bounds. |
| PRD-005 | Chose fail-closed non-Git behavior with `NO_GIT_WORKTREE`. |
| PRD-006 | Required an exhaustive versioned caller/policy inventory and complete migration matrix. |
| PRD-007 | Defined deterministic retention classes and transitions. |
| PRD-008 | Named the known skill/reference consumers for clean cutover. |
| PRD-009 | Grouped objective success criteria by release and added skill-step completion checks. |
