---
status: approved
created: 2026-09-02
updated: 2026-09-02 (approved)
linked_prd: ../prd.md
linked_architecture: ../architecture.md
linked_stories:
  - ../stories/story-008-task9-distill-doc.md
  - ../stories/story-009-docs-retention.md
---

# Epic 5: Distillation Procedure and Docs

## Description

The human/agent-facing half (AD-5/AD-6): Task 9 (Distill) reference doc adopting the Appendix E.2 analysis rules wholesale (minus JSON output contract and wholesale index rewrite), with attribution to arXiv 2608.27454 and the pinned MIT repo revision; Task 4 retention flag (unreferenced packs >3 months, flag-only); task-catalogue and docs updates.

## Scope

### In Scope

- `skills/references/task_distill.md` + SKILL.md catalogue entry
- Task 4 review flag; updates to task_add_note / task_implement_story / task_quick_task / task_review references
- README + docs updates; attribution records

### Out of Scope

- Stage 2 transcript-capture wrappers (ADR-0003, separate approval); any CLI code

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [[../stories/story-008-task9-distill-doc\|story-008]] | Write Task 9: Distill procedure doc | draft |
| [[../stories/story-009-docs-retention\|story-009]] | Retention flag and docs updates | draft |

## Success Criteria

- [ ] Task 9 doc is self-sufficient (any agent can execute it from the doc alone, NFR-004)
- [ ] Attribution + pinned revision recorded wherever E.2-derived text appears
- [ ] SKILL.md catalogue, README, and affected references updated consistently

## Progress

- Stories: 2/2 done
- Last updated: 2026-09-02
