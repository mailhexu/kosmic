---
status: "done"
created: "2026-09-05"
updated: "2026-09-05"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-003-check-math-protocol.md", "../stories/story-004-check-math-atomic-update.md"]
project_id: "kosmic"
subproject_id: "prd-math-derivation-layer-mathdocs"
record_kind: "epic"
local_id: "002"
---

# Epic 7: Math Execution and Verification

## Description

Execute trusted SymPy derivations through a deterministic protocol and prove
that paired Math Notes contain their current named results.

## Scope

### In Scope
- Versioned JSON protocol and bounded subprocess execution
- Read-only verification and exact result comparison
- Atomic generated-block/metadata updates

### Out of Scope
- OS sandboxing, parallel execution, numeric tolerances

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-012](../stories/story-003-check-math-protocol.md) | check-math protocol and verification | draft |
| [story-013](../stories/story-004-check-math-atomic-update.md) | Atomic math-note update | draft |

## Success Criteria

- [ ] Malformed, stale, failed, and timed-out derivations fail loudly
- [ ] Verified results compare exactly
- [ ] Multi-note updates are all-or-none
- [ ] Tests pass; code review approved
