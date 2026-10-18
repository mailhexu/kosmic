---
status: "done"
created: "2026-09-14"
updated: "2026-09-16"
linked_epic: "../epics/epic-001-managed-run-foundation.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/managed-run-workspace-lifecycle.md", "../../../../notes/cli-projection-commands.md"]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "c52ab6a15b2dab0df9cbd450a76fcdc386612cdb (implementation-start; the working copy additionally holds pre-existing unrelated changes recorded in log/kosmic-2026-09-14.md)"
review_round: 1
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "story"
local_id: "002"
---

# Story 044: Git Evidence and Run Store

## User Story

As a reviewer, I want canonical run state and related Git status recorded at every lifecycle boundary so that surviving files and worktree changes are explainable without treating Git deltas as ownership.

## Acceptance Criteria

- [x] Strict porcelain-v2 `-z` capture records HEAD, branch, worktree root, common Git directory, raw snapshot hash, and parsed path classes without storing diffs.
- [x] Unknown records and Git failures prevent destructive mutation and return stable errors.
- [x] Canonical manifest, operation, handle/receipt, history, Git-delta, and report schemas validate and write atomically with required file and directory synchronization.
- [x] The store statically enumerates valid and malformed schemas and computes bounded byte data, but defers authoritative active/abandoned classification and CLI status to Story 047 after the lease exists.
- [x] Concurrent or pre-existing user changes remain unattributed evidence and are never assigned Kosmic ownership.

## Tasks

### Phase 1: Research
- [x] Verify porcelain-v2 record grammar and directory `fsync` behavior.
- [x] Confirm existing CLI JSON/error conventions.

### Phase 2: Tests
- [x] Write failing Git parser and repository-state tests, including NUL paths, renames, detached HEAD, and concurrent changes.
- [x] Write failing schema, atomic-write, synchronization, static-enumeration, byte-accounting, and recovery tests.

### Phase 3: Implementation
- [x] Implement private `GitSnapshot` and `RunStore` seams.
- [x] Implement private static enumeration consumed later by the complete report interface.

### Phase 4: Review
- [x] Run focused tests and validate the canonical pair.
- [ ] Complete Standards and Spec review.

## Routine Decision

The story implements the approved managed-run subsystem without adding a Domain Topic routine edge. No routine proposal is required.

## Technical Notes

### Patterns Found

- Porcelain v2 `-z` records are NUL-terminated with no C-quoting; rename records carry `origPath` as the following NUL field; ordinary records have 9 fields, rename records 10 (path is the last field), unmerged records 11.
- `git rev-parse HEAD` on an unborn branch exits non-zero while echoing `HEAD` on stdout; the capture treats that case as `head=None` instead of a failure.
- `os.fsync` on a directory descriptor synchronizes the directory entry on Linux; `_atomic_replace_bytes` stages a same-parent `O_EXCL|O_NOFOLLOW` temporary, fsyncs the file, `os.replace`s, and fsyncs the parent directory.

### Implementation Approach

1. `GitSnapshot` dataclass plus `capture_git_snapshot` (rev-parse HEAD/show-toplevel/git-common-dir and `status --porcelain=v2 --branch --untracked-files=all -z`), `_parse_porcelain_v2` strict parser rejecting unknown records and missing final NUL, and `git_delta` producing the schema-v1 classification with an always-empty `unattributed` list.
2. `RunStore` seams: `validate_run_manifest` (schema v1, states, retentions, hex hashes, timestamps), `_write_manifest`/`load_manifest`, private handle/receipt files under `handles/` validated with `0600` no-follow reads, `_atomic_replace_bytes`, `_read_bounded`, and `_tree_bytes` no-follow device-bounded byte accounting.
3. `enumerate_run_store` statically classifies immediate `runs/` children (valid manifest, malformed variants, unattributed names) without lease authority, deferring live classification to Story 047.

### Edge Cases

- Unknown porcelain records, missing final NUL, unborn HEAD, detached HEAD, paths with spaces, concurrent user changes (classified, never owned), oversized payloads (`PAYLOAD_TOO_LARGE`), non-regular record files, and malformed manifests all return stable `RunError` codes.

## Review Record

### Round 1 — 2026-09-15

- Pending: convergent Standards/Spec review after the full vertical sequence lands.

## Definition of Done

- [x] All acceptance criteria and focused tests pass.
- [x] Consumer CLI knowledge and generated projection are current.
- [ ] Review has no unresolved Blocking finding.
- [x] Git baseline/final status and log are recorded.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-15 | Implemented | GitSnapshot, strict porcelain-v2 parser, manifest/handle schemas, atomic synchronized writes, and static enumeration in `skills/scripts/kosmic_runs.py`. |
| 2026-09-15 | Verified | Focused runs suite 75 tests OK (includes Story 044 coverage); full suite 394 tests OK; canonical pair regenerated and valid. |
