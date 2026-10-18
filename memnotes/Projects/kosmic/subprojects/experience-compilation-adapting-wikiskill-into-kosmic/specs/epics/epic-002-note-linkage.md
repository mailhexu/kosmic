---
status: "approved"
created: "2026-09-02"
updated: "2026-09-02 (approved)"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-004-evidence-frontmatter.md"]
project_id: "kosmic"
subproject_id: "experience-compilation-adapting-wikiskill-into-kosmic"
record_kind: "epic"
local_id: "002"
---

# Epic 2: Note Evidence Linkage

## Description

Additive optional note frontmatter `evidence: [paths]` linking a note to its motivating packs (AD-2). For stable notes every entry must resolve relative to the Project root; drafts may dangle. Hooks into the existing per-note loop of `validate_notes_bundle` (scripts/kosmic_project_skills.py:340-343).

## Scope

### In Scope

- `evidence:` key parsing and resolution for stable notes in `validate_notes_bundle`
- Tests: stable dangling → fail; draft dangling → pass; absent key → unaffected

### Out of Scope

- Completion-gate enforcement of linkage (Epic 4)

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [[subprojects/experience-compilation-adapting-wikiskill-into-kosmic/specs/stories/story-004-evidence-frontmatter.md\|story-004]] | Validate `evidence:` note frontmatter | draft |

## Success Criteria

- [ ] Stable note with resolvable `evidence:` passes; unresolvable fails with the path named
- [ ] Existing notes without the key are unaffected (backward compatible)

## Progress

- Stories: 1/1 done
- Last updated: 2026-09-02
