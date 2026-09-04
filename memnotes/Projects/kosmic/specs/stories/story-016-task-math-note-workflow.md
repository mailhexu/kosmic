---
status: done
created: 2026-09-05
updated: 2026-09-05
linked_epic: ../epics/epic-9-math-workflow-release.md
linked_architecture: ../architecture-math-derivation-layer.md
linked_prd: ../prd-math-derivation-layer.md
related_notes: [cli-projection-commands.md]
consumer_interface_change: true
evidence_packs: [2026-09-05-math-derivation-layer-impl]
review_base: ""
review_round: 0
---

# Story 016: Task M and Math Workflow Integration

## User Story

As a Kosmic agent, I want one derivation-first procedure and valid templates,
so that I never substitute LLM algebra for executable SymPy authority.

## Acceptance Criteria

- [x] Task M independently covers create, verify, update, correction, index, provenance, and failure/blocking behavior.
- [x] SKILL.md routes math creation/maintenance/debugging to Task M and states the derivation-first checkpoint.
- [x] Task 1/8, Task 2, Task 3, Task 4, Task 6, and Task 7 contain the approved integration rules without duplicated authority.
- [x] Index, script, derivation-note, regular-note, and work-item templates generate validator-conforming structures.
- [x] README documents setup, trust boundary, commands, and the authority chain.

## Tasks

### Phase 1: Research
- [x] Map each workflow rule to one authoritative task file
- [x] Review writing-great-skills rubric for disclosure/duplication

### Phase 2: Tests (TDD)
- [x] TEST-016A: CLI-created/indexed structures from templates validate
- [x] TEST-016B: installed skill contains every referenced task/template

### Phase 3: Implementation
- [x] IMPL-016A: add Task M and task-matrix/checkpoint routing
- [x] IMPL-016B: update affected task references with context pointers
- [x] IMPL-016C: add templates and README guidance

### Phase 4: Review
- [x] Skill-optimizer review and full suite pass
- [x] Task 7 review approved

## Definition of Done

- [x] All acceptance criteria met
- [x] No duplicated or contradictory math authority
- [x] Skill docs self-contained and reviewed
