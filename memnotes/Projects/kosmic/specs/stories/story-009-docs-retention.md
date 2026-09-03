---
status: done
created: 2026-09-02
updated: 2026-09-02 (done)
linked_epic: ../epics/epic-5-distillation-docs.md
linked_architecture: ../architecture.md
linked_prd: ../prd.md
evidence_packs: [2026-09-02-experience-compilation-impl]
consumer_interface_change: true
related_notes: [cli-projection-commands.md]
---

# Story 9: Retention Flag and Docs Updates

## User Story

As a Kosmic orchestrator,
I want Task 4 to flag stale unreferenced packs and all task docs to reflect the evidence workflow,
So that the pack layer stays navigable and the workflow is documented end-to-end.

## Acceptance Criteria

- [ ] Task 4 review reference gains: list packs referenced by no note's `evidence:` and older than 3 months (date from directory name); flag-only, never delete/archive
- [ ] `references/task_add_note.md` documents `evidence:` frontmatter; `task_implement_story.md` + `task_quick_task.md` document `evidence_packs:` declaration and the completion gate; `task_review.md` documents decision-entry appends + retention flag
- [ ] README and `docs/` updated (evidence layer, ledger, Task 9)
- [ ] No CLI code changes in this story

## Tasks

- [ ] IMPL-001: update the five references + SKILL.md cross-links
- [ ] IMPL-002: README + docs pages
- [ ] VERIFY: read-through consistency check (every gate/field named in docs exists in shipped CLI behavior from Stories 1-7)

## Definition of Done

- [ ] Acceptance criteria met; docs consistent with shipped code; reviewed

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
