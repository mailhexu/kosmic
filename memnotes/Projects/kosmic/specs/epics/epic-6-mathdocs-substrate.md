---
status: done
created: 2026-09-05
updated: 2026-09-05
linked_prd: ../prd-math-derivation-layer.md
linked_architecture: ../architecture-math-derivation-layer.md
linked_stories: [../stories/story-010-mathdocs-structure-registry.md, ../stories/story-011-mathdocs-metadata-hash.md]
---

# Epic 6: Mathdocs Substrate

## Description

Give every Project a structurally valid mathdocs registry whose scripts, notes,
index entries, hashes, and environment metadata can be loaded without SymPy.

## Scope

### In Scope
- Project structure/init/migration
- Side-by-side pairing and reserved index
- Immutable registry model and structural metadata/hash validation

### Out of Scope
- Script execution, equation propagation, source-code linkage

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-010](../stories/story-010-mathdocs-structure-registry.md) | Mathdocs structure and registry | draft |
| [story-011](../stories/story-011-mathdocs-metadata-hash.md) | Metadata and source-hash currency | draft |

## Success Criteria

- [ ] Initialization and migration create mathdocs idempotently
- [ ] Registry rejects pairing/index defects
- [ ] Stable note metadata and source hash are structurally validated
- [ ] Tests pass; code review approved
