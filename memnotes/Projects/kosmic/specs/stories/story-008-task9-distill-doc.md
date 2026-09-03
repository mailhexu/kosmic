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

# Story 8: Write Task 9 — Distill Procedure Doc

## User Story

As any coding agent,
I want a self-sufficient Task 9 (Distill) reference doc,
So that I can execute evidence distillation correctly without hidden prompt state (NFR-004).

## Acceptance Criteria

- [ ] `skills/references/task_distill.md` exists; SKILL.md task catalogue lists Task 9
- [ ] Procedure adopts Appendix E.2 analysis rules: root cause (WHY not WHAT), success-vs-failure comparison, action patterns not error messages, exact command sequences, both success and failure patterns, 10–30-line notes, never-duplicate (update with new evidence), index entry states problem + root cause + fix
- [ ] Outputs: draft notes / updates / deprecations via Task 2 conflict policy; promotion only via human review
- [ ] Attribution header: arXiv 2608.27454 + MIT repo with pinned revision (record commit SHA at implementation time)
- [ ] JSON output contract and wholesale-index-rewrite rules explicitly excluded (adaptation notes)

## Tasks

- [ ] IMPL-001: write the reference doc from the verbatim E.2 text (in `docs/research/` session artifact) + third-party SKILL.md
- [ ] IMPL-002: add Task 9 to SKILL.md catalogue with trigger (post-work-item, when `evidence_packs` declared)
- [ ] VERIFY: dry-run the doc against a toy pack — an agent reading only the doc produces a conforming draft note

## Definition of Done

- [ ] Acceptance criteria met; dry-run succeeds; doc reviewed

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-02 | Created | Initial draft |
