---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-003-proposal-completion-gate.md", "../stories/story-004-rejection-memory.md"]
project_id: "kosmic"
subproject_id: "skill-proposal-loop"
record_kind: "epic"
local_id: "002"
---

# Epic 11: Proposal Governance

## Description

Make the proposal decision mechanically unavoidable for new qualifying work and preserve rejected intervention history without changing the Impact Ledger schema.

## Scope

### In Scope
- Additive work-item declaration and completion gate
- New template fields and workflow hooks
- Proposal fingerprints, reconsideration, lifecycle, ledger decision format

### Out of Scope
- LLM inference or automatic approval

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-020](../stories/story-003-proposal-completion-gate.md) | Proposal completion gate | draft |
| [story-021](../stories/story-004-rejection-memory.md) | Rejection fingerprint and ledger memory | draft |

## Success Criteria

- [x] New work cannot silently skip the proposal decision
- [x] Legacy work remains valid
- [x] Equivalent rejected interventions are detected
- [x] Code reviewed and approved
