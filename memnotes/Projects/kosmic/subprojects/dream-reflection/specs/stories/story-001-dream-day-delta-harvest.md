---
status: "done"
created: "2026-09-23"
updated: "2026-09-23"
linked_epic: "../epics/epic-001-dream-reflection-initial-release.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
depends_on: []
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "dream-reflection"
record_kind: "story"
local_id: "001"
---

# Story 057: Dream Day-Delta Harvest

## User Story

As a Kosmic maintainer,
I want a deterministic target-day vault inventory,
So that reflection starts from auditable history rather than agent discovery.

## Acceptance Criteria

- [x] Given an explicit or default date, timezone resolution follows AD-DR1 and DST boundary cases are deterministic.
- [x] Given committed, late-committed, staged, unstaged, untracked, renamed, and deleted Markdown changes, harvest emits the complete observable union with origins, old/new paths, blob IDs/hashes, and coverage warnings.
- [x] Given identical captured vault state and arguments, canonical JSON bytes are identical.
- [x] Given a project filter, project-local content is filtered while labeled shared root/Skills evidence remains.
- [x] Given shallow or unresolvable history/timezone, harvest fails or warns exactly as AD-DR1 specifies without claiming exact edit history.

## Tasks

### Phase 1: Research

- [x] Verify Git snapshot, porcelain-v2, path-containment, frontmatter, and canonical JSON patterns.
- [x] Pin authoritative vault surfaces and merge/rename/date-window behavior in Technical Notes.

### Phase 2: Tests (TDD - Write First!)

- [x] TEST-057-1: Fixture Git history covers additions, modifications, deletions, renames, merges, late commits, and DST boundaries.
- [x] TEST-057-2: Dirty/untracked and frontmatter-union fixtures prove origins and coverage.
- [x] TEST-057-3: Shuffled discovery order produces byte-identical JSON.

### Phase 3: Implementation

- [x] IMPL-057-1: Implement typed harvest models, timezone/date resolution, Git before/after observations, and dirty-state union.
- [x] IMPL-057-2: Implement canonical ordering/path normalization/serialization and project filtering.

### Phase 4: Review

- [x] All tests pass
- [x] Standards and Spec review completed
- [x] Harvest conventions captured as Project Knowledge if durable

## Routine Decision

The mechanic remains Kosmic-project CLI infrastructure because its vault
surfaces and schemas are Kosmic-specific; no Shared Routine edge is introduced.

## Technical Notes

Implementation must follow AD-DR1 and the `DreamHarvest` canonicalization contract. This story owns only a side-effect-free internal collector and versioned artifact model: it exposes no supported CLI, starts no managed run, performs no agent reflection, and publishes no dream file. Story 060 exclusively owns the public managed `dream-harvest` command.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Existing Git snapshot helpers can be reused safely | ⬜ | `skills/scripts/kosmic_runs.py` |
| Existing Markdown parser exposes required dates | ⬜ | `skills/scripts/kosmic_project_skills.py` |

## Definition of Done

- [x] All acceptance criteria met
- [x] Focused and full tests pass
- [x] Code reviewed and approved
- [x] Knowledge notes updated when warranted
- [x] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-23 | Created | Initial draft |

| 2026-09-23 | Done | Implemented and verified; dogfood evidence in evidence/2026-09-23-dream-reflection-release |
