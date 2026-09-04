---
status: done
created: 2026-09-05
updated: 2026-09-05
linked_epic: ../epics/epic-6-mathdocs-substrate.md
linked_architecture: ../architecture-math-derivation-layer.md
linked_prd: ../prd-math-derivation-layer.md
related_notes: [cli-projection-commands.md]
consumer_interface_change: true
evidence_packs: [2026-09-05-math-derivation-layer-impl]
review_base: ""
review_round: 0
---

# Story 011: Mathdocs Metadata and Source-Hash Currency

## User Story

As a developer, I want each stable derivation note bound to the exact script
and verification environment, so that stale equations fail before use.

## Acceptance Criteria

- [x] Stable Math Derivation notes require every FR-003 metadata field with exact type/shape validation.
- [x] `source_sha256` is compared to script bytes without importing SymPy; byte changes make validation fail.
- [x] Draft notes may carry pending metadata; deprecated pairs remain index-consistent but are excluded from active result lookup.
- [x] Host, absolute source directory, UTC timestamp, Python and SymPy versions are preserved in the registry.

## Tasks

### Phase 1: Research
- [x] Reuse existing frontmatter/hash/path patterns
- [x] Define version, UTC, hostname, and hash validators

### Phase 2: Tests (TDD)
- [x] TEST-011A: every missing/malformed metadata field
- [x] TEST-011B: current vs changed script hash
- [x] TEST-011C: draft/deprecated lifecycle behavior

### Phase 3: Implementation
- [x] IMPL-011A: parse typed derivation metadata
- [x] IMPL-011B: compute and validate source hashes
- [x] IMPL-011C: expose only active verified results from registry

### Phase 4: Review
- [x] Focused and full tests pass
- [x] Task 7 review approved

## Definition of Done

- [x] All acceptance criteria met
- [x] Structural validation stays SymPy-independent
- [x] Code reviewed; log/notes current
