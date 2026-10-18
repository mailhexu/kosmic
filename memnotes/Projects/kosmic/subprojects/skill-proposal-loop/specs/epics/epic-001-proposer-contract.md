---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-001-task-p-procedure.md", "../stories/story-002-proposal-validation.md"]
project_id: "kosmic"
subproject_id: "skill-proposal-loop"
record_kind: "epic"
local_id: "001"
---

# Epic 10: Proposer Contract

## Description

Establish Task P and one deep, deterministic `SkillProposal` validation interface so fresh-context agents produce atomic, reviewable decisions rather than informal suggestions.

## Scope

### In Scope
- Task P procedure and proposal template
- Proposal parser, lifecycle, path, section, scope, and independence validation
- `validate-proposal` and project-wide validation

### Out of Scope
- Completion gating, candidate execution, publication

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-018](../stories/story-001-task-p-procedure.md) | Task P procedure and template | draft |
| [story-019](../stories/story-002-proposal-validation.md) | Proposal model and validation | draft |

## Success Criteria

- [x] All stories complete
- [x] Fresh-context contract is self-sufficient
- [x] Proposal validation tests pass
- [x] Code reviewed and approved
