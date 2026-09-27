---
status: approved
created: 2026-09-27
updated: 2026-09-27
linked_epic: ../epics/epic-27-project-status-file.md
linked_architecture: ../architecture-project-status-file.md
linked_prd: ../prd-project-status-file.md
related_notes: []
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
depends_on: []
review_base: ""
review_round: 0
---

# Story 064: Status Generation Core

## User Story

As a project maintainer,
I want a deterministic STATUS.md generator bound to my working directory,
So that the directory states its own spec status without hand maintenance.

## Acceptance Criteria

- [ ] `status_root` is an optional ProjectEntry.md field: init/migrate accept `--status-root`, validate its worktree containment, and reject cross-project collisions with `STATUS_ROOT_COLLISION`.
- [ ] `generate-status --project {P}` reads spec frontmatter (PRD/Architecture roots, epics/, stories/, quick-tasks/, skill-proposals direct children) and writes the AD-S5 document atomically at the bound root.
- [ ] Identical vault state produces byte-identical output; the header carries project id, vault HEAD (or `no-head`), and the generated marker — never wall clock.
- [ ] Rows are sorted by class then path; links are POSIX-relative from STATUS.md to the vault files; Open Work counts nonterminal records and lists one bullet per open item.
- [ ] Unbound project fails `generate-status` with `STATUS_ROOT_UNBOUND`; missing root path fails with `STATUS_ROOT_MISSING`.

## Tasks

### Phase 1: Research

- [ ] Reuse frontmatter parsing, atomic write, and provenance (HEAD) helpers.
- [ ] Pin the exact document grammar in Technical Notes.

### Phase 2: Tests (TDD - Write First!)

- [ ] TEST-064-1: Fixture project specs → exact expected bytes (golden, incl. sorting/links/HEAD marker).
- [ ] TEST-064-2: Determinism double-run; unbound/missing/collision failure fixtures.
- [ ] TEST-064-3: init/migrate `--status-root` binding round-trip.

### Phase 3: Implementation

- [ ] IMPL-064-1: Binding field, init/migrate flags, collision check.
- [ ] IMPL-064-2: Renderer, atomic writer, `generate-status` CLI.

### Phase 4: Review

- [ ] Focused and full tests pass
- [ ] Standards and Spec review completed
- [ ] Consumer-interface completion gate passes

## Routine Decision

No reusable deterministic procedure mechanics beyond existing CLI helpers
are introduced; the renderer is Kosmic-specific projection logic.

## Technical Notes

Follows AD-S1..S3 and the Data Models grammar. Excluded: validation drift
(story 065) and workflow docs (story 066).

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| ProjectEntry optional fields parse via existing reader | ⬜ | Projection CLI |
| Relative link computation is stable across vault depth | ⬜ | os.path.relpath fixtures |

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Focused and full tests pass
- [ ] Code reviewed and approved
- [ ] Stable usage knowledge updated when story 066 lands
- [ ] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-27 | Created | Initial draft |
