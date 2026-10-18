---
status: "done"
created: "2026-09-02"
updated: "2026-09-02 (done)"
linked_epic: "../epics/epic-001-evidence-substrate.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
evidence_packs: ["2026-09-02-experience-compilation-impl"]
consumer_interface_change: true
related_notes: ["cli-projection-commands.md"]
project_id: "kosmic"
subproject_id: "experience-compilation-adapting-wikiskill-into-kosmic"
record_kind: "story"
local_id: "001"
---

# Story 1: Project-Root Walks Tolerate the Evidence Layer

## User Story

As a Kosmic contributor,
I want `evidence/` directories and `impact.md` at Project roots to be accepted by every Projection CLI command,
So that capturing experience never breaks validation, migration, or projection.

## Acceptance Criteria

- [ ] `validate`, `init`, `migrate`, `generate`, `check-completion` all succeed on a vault containing `evidence/{slug}/MANIFEST.md` + payloads and a non-empty `impact.md`
- [ ] No projection output (`generate`) ever contains evidence or ledger content
- [ ] `validate` on a vault without the layer is unchanged (backward compatible)

## Tasks

### Phase 1: Tests (TDD — write first)

- [ ] TEST-001: fixture vault with evidence pack + impact.md passes `validate`
- [ ] TEST-002: `generate` output tree contains no `evidence` path
- [ ] TEST-003: vault without layer behaves exactly as before

### Phase 2: Implementation

- [ ] IMPL-001: locate every Project-root walk in `scripts/kosmic_project_skills.py` that could trip on unknown entries; add tolerance for `evidence/` and `impact.md`
- [ ] IMPL-002: no changes to `validate_notes_bundle`/`collect_projection_plan` (structural exclusion — verify by test, not edit)

### Phase 3: Review

- [ ] All tests pass; code review completed

## Technical Notes

Exclusion is structural (AD-1): the layer lives outside `notes/`, so `validate_notes_bundle` (:338) and `collect_projection_plan` (:450) already never see it. The risk surface is any code enumerating the Project root itself.

## Definition of Done

- [ ] Acceptance criteria met; tests pass; reviewed; no regressions

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
