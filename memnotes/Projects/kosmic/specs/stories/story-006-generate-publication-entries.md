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

# Story 6: generate Appends Publication Entries

## User Story

As a Kosmic contributor,
I want `generate` to append a ledger entry for every note whose projected content changed,
So that the publication history of Project Knowledge is complete without manual bookkeeping.

## Acceptance Criteria

- [ ] After a successful atomic publication, `impact.md` gains one `kind: publication` entry per changed note: date, targets `[note path]`, refs `{old hash → new hash}` (from Projection Provenance), outcome `published`, reason `""`
- [ ] `generate` with no changed notes appends nothing
- [ ] Append-only: existing entries never rewritten; failure mid-generate leaves ledger untouched (append after publication only)

## Tasks

### Phase 1: Tests (TDD)

- [ ] TEST-001: modify a note → generate → exactly one new entry with correct old→new hashes
- [ ] TEST-002: generate twice with no change → no new entries
- [ ] TEST-003: entry format passes the Story-5 validator

### Phase 2: Implementation

- [ ] IMPL-001: hook at end of `generate` after atomic publication; diff source hashes from existing provenance data — no new hashing

### Phase 3: Review

- [ ] All tests pass; code review completed

## Technical Notes

First-ever generate (no prior hashes) uses `old: null`. Deterministic ordering: entries sorted by note path.

## Definition of Done

- [ ] Acceptance criteria met; tests pass; reviewed; no regressions

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
