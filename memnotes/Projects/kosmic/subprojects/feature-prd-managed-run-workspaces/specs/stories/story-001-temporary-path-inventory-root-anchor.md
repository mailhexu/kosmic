---
status: "done"
created: "2026-09-14"
updated: "2026-09-14"
linked_epic: "../epics/epic-001-managed-run-foundation.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/managed-run-workspace-lifecycle.md"]
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
local_id: "001"
---

# Story 043: Temporary-Path Inventory and Root Anchor

## User Story

As a Kosmic maintainer, I want every temporary-path caller classified and every managed path anchored below the active worktree so that migration is exhaustive and later cleanup cannot escape its authority.

## Acceptance Criteria

- [x] A checked-in versioned inventory classifies all fourteen current production temporary callers and every scratch-policy consumer as managed run, atomic single-file write, atomic publication, durable output, or defect, with zero unexplained entries.
- [x] The inventory identifies the two current platform-default `/tmp` defects, eleven sibling-staging callers, one atomic single-file write, eight policy consumers, and the missing root ignore rule.
- [x] Root resolution accepts only a Git worktree and produces `.tmp/kosmic/{runs,quarantine,operations,handles}` with root `.tmp/` ignored.
- [x] Every path component is opened descriptor-relatively with no-follow, owner, mode, type, and device checks; symlinked or malformed ancestors fail closed.
- [x] A source-policy check fails for new unexplained `tempfile` defaults, `/tmp`, `/dev/shm`, root scratch, or duplicate lifecycle policy.

## Tasks

### Phase 1: Research

- [x] Verify the inventory against current source and policy files.
- [x] Confirm Python 3.11 descriptor-relative and no-follow behavior on the supported workstation.

### Phase 2: Tests

- [x] Write failing inventory-completeness and source-policy tests.
- [x] Write failing path traversal, symlink ancestor, owner/mode, device, ignore-rule, and non-Git tests.

### Phase 3: Implementation

- [x] Add the versioned inventory and root-anchor implementation.
- [x] Add root ignore validation and stable failure codes.

### Phase 4: Review

- [x] Run focused tests and project validation.
- [x] Complete Standards, Spec, and security review.

## Routine Decision

This is a new product module and migration contract, not mechanics compiled from a Domain Topic procedure. It introduces no `uses_routines` edge, so no routine proposal is required.

## Technical Notes

### Patterns Found

- Existing production modules keep every temporary path explicit: `kosmic_project_skills.py` (8 sites), `kosmic_routines.py` (1), `kosmic_shared_library.py` (5); only `atomic_write` stages a same-parent single file (`mkstemp` + `os.replace`).
- Publication convention: destination-sibling `mkdtemp` staging/backup directories feeding `publish_tree`/`os.replace` rollback (10 sites) plus the mathdocs destination-sibling staging copy (1 site).
- Tests are `unittest`-style under `tests/`, importing `skills.scripts.*` from the repository root; the suite runs with `python -m unittest discover -s tests` (baseline: 320 tests pass).

### Phase 1 Verification (2026-09-14)

| Item | Verified | Evidence |
|---|---|---|
| Fourteen production `tempfile` call sites: 2 platform defaults, 1 same-parent single-file write, 11 destination-sibling staging | ✅ | `grep -n "tempfile\." skills/scripts/*.py` (kosmic_project_skills.py:1079,1516,1545,1766,1948,1949,2027,2346; kosmic_routines.py:284; kosmic_shared_library.py:433,824,960,1000,1002) |
| Eight scratch-policy consumers (marker regex `File Hygiene|\.tmp/|\.scratch[/}]` over `skills`+`docs` markdown) | ✅ | skills/SKILL.md, skills/README.md, task_implement_story.md, task_quick_task.md, task_create_spec.md, templates/template-skill-proposal.md, docs/adr/0001-*, docs/specs/required-procedure-skills.md; no other file matches |
| No `/tmp`, `/dev/shm`, `gettempdir`, or `TMPDIR` literals in production modules | ✅ | grep over the three existing production modules returns no match |
| Root `.gitignore` lacks a `.tmp/` rule before implementation | ✅ | `.gitignore` contained only `Refs/` at baseline |
| Python 3.13 (>= required 3.11): `O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC` open, `mkdir(dir_fd=)`, `stat(dir_fd=, follow_symlinks=False)` | ✅ | probe under `.tmp/story-043/research/`; symlinked directory fails the no-follow open and `S_ISLNK` classification via dir_fd-relative lstat works |
| `git check-ignore` negation semantics | ✅ | probe matrix over plain / negated / absent-rule repositories |
| Cross-device test fixture available unprivileged | ✅ | `/tmp` device 53 differs from repository device 66308 |

### Implementation Approach

1. New `skills/scripts/kosmic_runs.py`: versioned inventory loader (`kosmic.runs-inventory/v1` from `skills/scripts/kosmic_runs_inventory.json`), read-only source-policy auditor, and descriptor-anchored `resolve_run_root` with stable `RunRootError` codes.
2. Focused behavioral tests in `tests/test_kosmic_runs.py` at the two public seams (auditor over a materialized copy of the real tree; resolver over temporary Git worktrees), plus narrowly focused internal checks for owner/device mismatches (unobservable without root or cross-device components).
3. Root `.gitignore` gains `.tmp/` (the inventory's root-ignore defect row is resolved by this story).

### Edge Cases

- Symlinked or non-directory `.tmp`/`kosmic`/managed component, relaxed mode (`0755` kosmic subtree; group/world-writable `.tmp`), negated ignore rule, non-Git input, double resolve (idempotence), `TMPDIR` pollution, bare tempfile imports, explicit root scratch, and stale/absent inventory anchors.

## Review Record

### Round 1 — 2026-09-14

- **Standards axis:** no unresolved blocking documented-standard violation. The review identified and the implementation fixed a missing `function` field on one inventory row, added loader validation for that field, and removed the auditor's `.tmp/` creation side effect. Remaining observations (private invariant tests and mixed report-count keys) were non-blocking design judgements; tests import the shared `MANAGED_DIRECTORIES` constant.
- **Spec axis:** caller/policy inventory verified against current source (14/14 and 8/8); no scope creep. The review identified and the implementation fixed source-policy gaps for bare tempfile imports and explicit root-scratch literals. All Story/PRD/Architecture requirements in scope are covered; caller migration, lease, retention, promotion, cleanup, and skill cutover remain correctly out of scope.
- **Security review:** descriptor-relative no-follow opens, owner/mode/type/device checks, symlink and malformed-ancestor fail-closed behavior, Git-root and ignore-rule authority, environment-default independence, and cross-device rejection are covered by focused tests. No unresolved blocking security finding.

## Definition of Done

- [x] All acceptance criteria and focused tests pass.
- [x] Inventory has zero unexplained entries.
- [x] Review has no unresolved Blocking finding.
- [x] Git baseline/final status and knowledge/log updates are recorded.

## Progress Log

| Date | Action | Notes |
|---|---|---|
| 2026-09-14 | Implemented | Added descriptor-anchored resolver, exhaustive inventory, source-policy auditor, root ignore, and 28 focused tests. |
| 2026-09-14 | Verified | Focused suite: 28 passed; full suite: 348 passed. |
| 2026-09-14 | Reviewed | Standards, Spec, and security review completed; findings fixed and no blocking findings remain. |
| 2026-09-14 | Done | Story complete; later lifecycle and migration stories remain separately scoped. |
