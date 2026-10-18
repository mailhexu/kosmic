---
status: "approved"
created: "2026-09-02"
updated: "2026-09-02 (approved)"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-005-ledger-validation.md", "../stories/story-006-generate-publication-entries.md"]
project_id: "kosmic"
subproject_id: "experience-compilation-adapting-wikiskill-into-kosmic"
record_kind: "epic"
local_id: "003"
---

# Epic 3: Impact Ledger

## Description

Flat, append-only `impact.md` at Project root recording knowledge-state transitions (AD-3): `validate` enforces the fixed 6-field schema (date, kind `publication|decision`, targets, refs, outcome, reason ≤1 line); `generate` appends publication entries (old→new source hashes reused from Projection Provenance) after atomic publication; Task 7 review appends decision entries per its task doc — the CLI validates but never authors decisions.

## Scope

### In Scope

- Ledger parsing and schema validation in `validate`
- Programmatic publication entries at the end of `generate`
- Task 7 decision-entry format documented (authoring is procedural, not code)

### Out of Scope

- Per-year splitting; deletion/editing of entries (append-only forever)

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [[subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-005-ledger-validation.md\|story-005]] | Validate impact.md schema | draft |
| [[subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-006-generate-publication-entries.md\|story-006]] | generate appends publication entries | draft |

## Success Criteria

- [ ] Malformed entries fail `validate` with the field named
- [ ] `generate` appends one entry per changed note with correct old→new hashes; re-running with no changes appends nothing

## Progress

- Stories: 2/2 done
- Last updated: 2026-09-02
