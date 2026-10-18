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
local_id: "003"
---

# Story 3: Migrate Research Memos into Evidence Packs

## User Story

As a Kosmic contributor,
I want the two existing `specs/research/` memos to become `kind: research` Evidence Packs,
So that the vault has exactly one motivating-material layer (ADR-0002) and the migration path is proven on real content.

## Acceptance Criteria

- [ ] `evidence/2026-09-02-route-graph-skill-projection/` and `evidence/2026-09-02-wikiskill-experience-compilation/` exist with MANIFEST (`kind: research`, `produced_by`, `date`, `summary`) and the memo as payload
- [ ] PRD `linked_research` and specs INDEX research-table links resolve to the new pack paths
- [ ] `validate` passes on the migrated vault; `specs/research/` is empty/removed

## Tasks

- [ ] IMPL-001: create the two packs (memo body verbatim as payload; no content edits)
- [ ] IMPL-002: update PRD frontmatter `linked_research`, INDEX research rows, research-memo internal links
- [ ] VERIFY: `python3 scripts/kosmic_project_skills.py validate` on the kosmic vault

## Definition of Done

- [ ] Acceptance criteria met; `validate` passes; links resolve (Obsidian link check)

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
