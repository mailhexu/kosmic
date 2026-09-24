---
status: done
created: 2026-09-02
updated: 2026-09-02 (approved)
linked_prd: ../prd.md
linked_architecture: ../architecture.md
linked_stories:
  - ../stories/story-007-completion-gate.md
---

# Epic 4: Completion Gate

## Description

Mechanical enforcement of distillation (AD-4): work items declare `evidence_packs: [slugs]` in frontmatter; `check_completion` (scripts/kosmic_project_skills.py:1244) fails when any declared slug lacks a draft-or-stable note linking it via `evidence:`. Mirrors the existing `consumer_interface_change` declaration pattern; absent key = no gate.

## Scope

### In Scope

- `evidence_packs` handling in `check_completion`
- Failure message naming the orphaned slug

### Out of Scope

- Auto-discovery of packs by date (rejected in design session)

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [[../stories/story-007-completion-gate\|story-007]] | check-completion enforces evidence linkage | draft |

## Success Criteria

- [x] Declared pack with no linking note fails; with a draft note passes; absent declaration passes
- [x] Nonexistent slug fails with the slug named

## Progress

- Stories: 1/1 done
- Last updated: 2026-09-02
