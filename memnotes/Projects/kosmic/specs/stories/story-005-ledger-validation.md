---
status: done
created: 2026-09-02
updated: 2026-09-02 (done)
linked_epic: ../epics/epic-3-impact-ledger.md
linked_architecture: ../architecture.md
linked_prd: ../prd.md
evidence_packs: [2026-09-02-experience-compilation-impl]
consumer_interface_change: true
related_notes: [cli-projection-commands.md]
---

# Story 5: Validate impact.md Schema

## User Story

As a Kosmic contributor,
I want `validate` to reject malformed Impact Ledger entries,
So that the ledger stays machine-queryable ("was X ever proposed and rejected?").

## Acceptance Criteria

- [ ] Entry = exactly 6 fields: date (ISO), kind (`publication|decision`), targets, refs, outcome (`published|accepted|rejected`), reason (≤1 line)
- [ ] Malformed entry fails `validate` naming entry and field
- [ ] Absent `impact.md` → no behavior change

## Tasks

### Phase 1: Tests (TDD)

- [ ] TEST-001: well-formed publication + decision entries pass
- [ ] TEST-002: unknown kind/outcome, missing field, bad date, prose-length reason each fail with field named

### Phase 2: Implementation

- [ ] IMPL-001: ledger entry format (one entry per Markdown list item or table row — pick, document in architecture) + parser + validator wired into `validate`

### Phase 3: Review

- [ ] All tests pass; code review completed

## Technical Notes

Entry serialization must be append-friendly: an agent appends one block at the file end without rewriting. Prefer a Markdown list-item format with inline fields.

## Definition of Done

- [ ] Acceptance criteria met; tests pass; reviewed; no regressions

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
