---
status: "done"
created: "2026-09-05"
updated: "2026-09-05"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-005-equation-marker-validation.md", "../stories/story-006-math-implementation-gate.md"]
project_id: "kosmic"
subproject_id: "prd-math-derivation-layer-mathdocs"
record_kind: "epic"
local_id: "003"
---

# Epic 8: Math Linkage Gates

## Description

Carry verified results from Math Notes into regular knowledge and
implementation with deterministic, finite validation.

## Scope

### In Scope
- Plural derivation frontmatter and result/exposition markers
- Stable-note equation validation outside code fences
- Source-root containment and implementation MathDoc references

### Out of Scope
- Language-specific AST parsing, whole-repository scans

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-014](../stories/story-005-equation-marker-validation.md) | Equation marker validation | draft |
| [story-015](../stories/story-006-math-implementation-gate.md) | Math implementation completion gate | draft |

## Success Criteria

- [ ] Stable note equations resolve and exact results agree
- [ ] Exposition remains explicitly non-authoritative
- [ ] Implementations reference stable/current derivations
- [ ] Tests pass; code review approved
