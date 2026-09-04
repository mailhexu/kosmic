---
status: done
created: 2026-09-05
updated: 2026-09-05
linked_epic: ../epics/epic-8-math-linkage-gates.md
linked_architecture: ../architecture-math-derivation-layer.md
linked_prd: ../prd-math-derivation-layer.md
related_notes: [cli-projection-commands.md]
consumer_interface_change: true
evidence_packs: [2026-09-05-math-derivation-layer-impl]
review_base: ""
review_round: 0
---

# Story 015: Math Implementation Completion Gate

## User Story

As a reviewer, I want equation-derived source linked to stable MathDocs, so
that every implemented formula is traceable to its checked derivation.

## Acceptance Criteria

- [x] `check-completion` accepts `--source-root` and requires `derivations` and `math_implementation_files` together.
- [x] Paths must be relative files resolving beneath source root; absolute, traversal, missing, directory, and symlink-escape paths fail.
- [x] Every declared slug is stable/current and occurs as `MathDoc: project/slug[#result]` in at least one declared file.
- [x] Every declared implementation file references at least one declared slug; unknown result identifiers fail.
- [x] Math gating runs before the consumer-interface early return; absent math fields preserve existing behavior.

## Tasks

### Phase 1: Research
- [x] Map completion-gate ordering and containment patterns

### Phase 2: Tests (TDD)
- [x] TEST-015A: two-field declarations and coverage in both directions
- [x] TEST-015B: every containment/path failure
- [x] TEST-015C: non-interface and absent-key compatibility

### Phase 3: Implementation
- [x] IMPL-015A: add source-root parser/dispatch
- [x] IMPL-015B: implement finite-file identifier validation
- [x] IMPL-015C: place math gate before interface early return

### Phase 4: Review
- [x] Focused/full tests and completion smoke check pass
- [x] Task 7 verifies marker adjacency; review approved

## Definition of Done

- [x] All acceptance criteria met
- [x] Source traceability is language-independent and finite
- [x] Consumer documentation updated before completion
