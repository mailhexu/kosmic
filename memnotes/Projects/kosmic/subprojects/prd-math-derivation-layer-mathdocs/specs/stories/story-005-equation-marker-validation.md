---
status: "done"
created: "2026-09-05"
updated: "2026-09-05"
linked_epic: "../epics/epic-003-math-linkage-gates.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["cli-projection-commands.md"]
consumer_interface_change: true
evidence_packs: ["2026-09-05-math-derivation-layer-impl"]
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "prd-math-derivation-layer-mathdocs"
record_kind: "story"
local_id: "005"
---

# Story 014: Equation Marker Validation

## User Story

As a knowledge consumer, I want displayed results checked against their named
MathDoc source, so that copied equations cannot silently drift.

## Acceptance Criteria

- [x] Stable notes with display math require resolvable plural `derivations:` and one adjacent valid marker per equation outside fences.
- [x] `MathDoc: project/slug#result` requires exact LaTeX agreement with the active registry result.
- [x] `MathDoc-Exposition: project/slug` verifies declaration/resolution without claiming equality.
- [x] Draft dangling links pass; deprecated/missing/unknown slug or result, duplicate marker, unmarked display math, and undeclared source fail naming the note/equation.
- [x] Inline math is not treated as an authoritative result.

## Tasks

### Phase 1: Research
- [x] Reuse fenced-text scanning and stable-note validation patterns

### Phase 2: Tests (TDD)
- [x] TEST-014A: plural result markers and exact comparison
- [x] TEST-014B: exposition, draft, deprecated, and unknown cases
- [x] TEST-014C: code-fence exclusion, inline boundary, malformed adjacency

### Phase 3: Implementation
- [x] IMPL-014A: equation/marker scanner outside fences
- [x] IMPL-014B: extend stable-note validation with registry
- [x] IMPL-014C: add file/equation-specific diagnostics

### Phase 4: Review
- [x] Focused/full tests pass
- [x] Task 7 review approved

## Definition of Done

- [x] All acceptance criteria met
- [x] Existing no-math notes remain compatible
- [x] Code reviewed; knowledge docs current
