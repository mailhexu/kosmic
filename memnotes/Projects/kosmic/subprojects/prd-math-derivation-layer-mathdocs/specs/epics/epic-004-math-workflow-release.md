---
status: "done"
created: "2026-09-05"
updated: "2026-09-05"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-007-task-math-note-workflow.md", "../stories/story-008-mathdocs-dogfood-release.md"]
project_id: "kosmic"
subproject_id: "prd-math-derivation-layer-mathdocs"
record_kind: "epic"
local_id: "004"
---

# Epic 9: Math Workflow and Release

## Description

Make derivation-first behavior executable by any Kosmic agent, prove it on a
real SymPy derivation, and distribute the updated skill.

## Scope

### In Scope
- Task M, task routing, templates, search/implementation/review integration
- Real-project dogfood and all CLI gates
- Version bump, installation, and publication records

### Out of Scope
- Math-note projection, untrusted-code sandbox, numerical datasets

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-016](../stories/story-007-task-math-note-workflow.md) | Task M and workflow integration | draft |
| [story-017](../stories/story-008-mathdocs-dogfood-release.md) | Dogfood and release | draft |

## Success Criteria

- [x] Agent instructions make derivation-first behavior unavoidable
- [x] Templates produce valid structures by construction
- [x] Real SymPy smoke path and every gate pass
- [x] Skill installed and diff-verified in all acceptance-criterion homes
