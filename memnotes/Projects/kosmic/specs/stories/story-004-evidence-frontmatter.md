---
status: done
created: 2026-09-02
updated: 2026-09-02 (done)
linked_epic: ../epics/epic-2-note-linkage.md
linked_architecture: ../architecture.md
linked_prd: ../prd.md
evidence_packs: [2026-09-02-experience-compilation-impl]
consumer_interface_change: true
related_notes: [cli-projection-commands.md]
---

# Story 4: Validate `evidence:` Note Frontmatter

## User Story

As a Maintainer,
I want stable notes' `evidence:` links verified against the pack layer,
So that every distilled Pattern stays traceable to its motivating evidence.

## Acceptance Criteria

- [ ] Stable note with `evidence: [paths]` — every path resolving relative to Project root passes; any unresolvable path fails naming the path
- [ ] Draft note with dangling `evidence:` passes (pending packs allowed)
- [ ] Notes without the key unaffected

## Tasks

### Phase 1: Tests (TDD)

- [ ] TEST-001: stable + resolvable passes
- [ ] TEST-002: stable + dangling fails with path named
- [ ] TEST-003: draft + dangling passes
- [ ] TEST-004: no key → no behavior change

### Phase 2: Implementation

- [ ] IMPL-001: extend the per-note loop in `validate_notes_bundle` (:340-343); resolution root = Project root (parent of `notes/`)

### Phase 3: Review

- [ ] All tests pass; code review completed

## Technical Notes

Paths are relative to the **Project root**, not the note (PRD FR-004) — packs live outside `notes/`, so note-relative paths would need `../` everywhere.

## Definition of Done

- [ ] Acceptance criteria met; tests pass; reviewed; no regressions

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
