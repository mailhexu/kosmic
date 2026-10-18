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
local_id: "002"
---

# Story 2: Validate MANIFEST.md Schema

## User Story

As a Maintainer,
I want `validate` to check every Evidence Pack's MANIFEST.md against the fixed schema,
So that packs stay machine-usable and provenance never rots.

## Acceptance Criteria

- [ ] MANIFEST frontmatter requires `kind` (`execution|research`), `produced_by`, `date` (ISO), `summary` (≤2 lines); body lists each payload file with a one-line role
- [ ] Missing/invalid field fails `validate` naming the pack and field
- [ ] Payload file listed in body but absent from disk (or vice versa) fails
- [ ] Valid packs pass; vaults with no `evidence/` unaffected

## Tasks

### Phase 1: Tests (TDD)

- [ ] TEST-001: valid execution pack passes; valid research pack passes
- [ ] TEST-002: bad `kind`, missing `produced_by`, non-ISO `date` each fail with field named
- [ ] TEST-003: body/disk file mismatch fails

### Phase 2: Implementation

- [ ] IMPL-001: `validate_evidence_packs(project_root)` called from `validate`; stdlib-only markdown frontmatter parsing reused from existing `parse_markdown`

### Phase 3: Review

- [ ] All tests pass; code review completed

## Technical Notes

No hashes in manifests (ADR-0002 session decision: git is the hash layer). Reuse the CLI's existing markdown parser rather than adding YAML deps.

## Definition of Done

- [ ] Acceptance criteria met; tests pass; reviewed; no regressions

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
