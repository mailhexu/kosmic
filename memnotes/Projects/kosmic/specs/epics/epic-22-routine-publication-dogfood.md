---
status: approved
created: 2026-09-07
updated: 2026-09-07
linked_prd: ../prd-procedure-compilation.md
linked_architecture: ../architecture-procedure-compilation.md
linked_stories: [../stories/story-041-atomic-publication-compilation.md, ../stories/story-042-procedure-compilation-dogfood-release.md]
---

# Epic 22: Atomic Publication Dogfood and Release

## Description

Compile the first shared routine from repeated publication mechanics, migrate every caller, and release the complete feature atomically.

## Scope

### In Scope
- Deep atomic publication routine and four-caller clean cutover
- Procedure `uses_routines`, plans, Recipe Packets, and hash checks
- Migration report, mixed-procedure dogfood, adapters, evidence, and release

### Out of Scope
- Automatic source-to-routine generation
- Mandatory registration of every existing helper

## Stories

| Story | Description | Status |
|---|---|---|
| [Story 041](../stories/story-041-atomic-publication-compilation.md) | Compile and migrate atomic publication | done |
| [Story 042](../stories/story-042-procedure-compilation-dogfood-release.md) | Integrate, dogfood, and release | done |

## Success Criteria

- [x] Four callers use one tested routine and obsolete implementations are absent.
- [x] Procedure packets carry validated, budget-bounded routine coordinates.
- [x] Mixed-procedure dogfood proves baseline-equivalent success and failure behavior through all adapters.
