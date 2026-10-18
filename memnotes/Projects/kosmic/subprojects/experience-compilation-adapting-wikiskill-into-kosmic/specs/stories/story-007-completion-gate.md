---
status: "done"
created: "2026-09-02"
updated: "2026-09-02 (done)"
linked_epic: "../epics/epic-004-completion-gate.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
evidence_packs: ["2026-09-02-experience-compilation-impl"]
consumer_interface_change: true
related_notes: ["cli-projection-commands.md"]
project_id: "kosmic"
subproject_id: "experience-compilation-adapting-wikiskill-into-kosmic"
record_kind: "story"
local_id: "007"
---

# Story 7: check-completion Enforces Evidence Linkage

## User Story

As a Kosmic orchestrator,
I want `check-completion` to fail when a declared Evidence Pack has no note linking it,
So that distillation is mechanically enforced, not discretionary.

## Acceptance Criteria

- [ ] Work item frontmatter `evidence_packs: [slugs]`: each slug must resolve to `evidence/{slug}/` and have ≥1 draft-or-stable note linking it via `evidence:`
- [ ] Orphaned or nonexistent slug fails naming the slug
- [ ] Absent key → gate skipped (backward compatible); existing `consumer_interface_change` behavior unchanged

## Tasks

### Phase 1: Tests (TDD)

- [ ] TEST-001: declared + linked (draft) → passes
- [ ] TEST-002: declared + unlinked → fails naming slug
- [ ] TEST-003: declared nonexistent slug → fails
- [ ] TEST-004: no declaration → passes; interface-change gate still enforced

### Phase 2: Implementation

- [ ] IMPL-001: extend `check_completion` (:1244) after the `consumer_interface_change` block; note-linkage query reuses the Story-4 resolution logic

### Phase 3: Review

- [ ] All tests pass; code review completed

## Technical Notes

Linkage = note whose `evidence:` list contains a path inside the pack directory. Draft notes count (review promotion is a separate gate).

## Definition of Done

- [ ] Acceptance criteria met; tests pass; reviewed; no regressions

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
