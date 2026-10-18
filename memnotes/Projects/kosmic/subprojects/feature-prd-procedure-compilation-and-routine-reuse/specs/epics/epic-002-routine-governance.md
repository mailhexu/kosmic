---
status: "done"
created: "2026-09-07"
updated: "2026-09-07"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-003-routine-proposal-contract.md", "../stories/story-004-routine-completion-workflow.md"]
project_id: "kosmic"
subproject_id: "feature-prd-procedure-compilation-and-routine-reuse"
record_kind: "epic"
local_id: "002"
---

# Epic 21: Routine Governance

## Description

Make reuse, extension, creation, and prose-retention explicit Task P decisions with deterministic approval and completion gates.

## Scope

### In Scope
- Compatible routine proposal fields, fingerprints, and rejection memory
- Candidate evidence and owner/consumer approvals
- Story, Quick Task, Task 9, Task P, and completion-gate integration

### Out of Scope
- Static inventory implementation (Epic 20)
- First compiled routine and release dogfood (Epic 22)

## Stories

| Story | Description | Status |
|---|---|---|
| [Story 039](../stories/story-003-routine-proposal-contract.md) | Routine-aware Task P contract | done |
| [Story 040](../stories/story-004-routine-completion-workflow.md) | Work-item and Distillation gates | done |

## Success Criteria

- [x] Existing Task P result vocabulary and legacy artifact bytes remain valid.
- [x] Every material mechanics change records a deterministic routine decision.
- [x] Required evidence, links, migration, and Maintainer approvals fail closed.
