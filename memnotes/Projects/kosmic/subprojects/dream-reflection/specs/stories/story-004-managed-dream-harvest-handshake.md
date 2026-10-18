---
status: "done"
created: "2026-09-23"
updated: "2026-09-23"
linked_epic: "../epics/epic-001-dream-reflection-initial-release.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["../../../../notes/dream-reflection-workflow.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
depends_on: ["story-001-dream-day-delta-harvest.md", "story-002-dream-open-work-knowledge-contract.md", "story-003-dream-vault-schema-validator.md"]
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "dream-reflection"
record_kind: "story"
local_id: "004"
---

# Story 060: Managed Dream Harvest Handshake

## User Story

As a Task D agent,
I want one authenticated managed harvest command with confined inputs,
So that reflection receives immutable evidence without reading the live vault or choosing filesystem paths.

## Acceptance Criteria

- [x] Completion fails unless Stories 057–059 are `done`; the public `dream-harvest` command invokes their internal collector/schema implementations rather than duplicating them.
- [x] `dream-harvest` begins a managed run, binds it to the canonical vault, snapshots the current dream tree into a no-follow run-owned stage, and returns only public run ID, private handle path, and harvest path.
- [x] Every readable path/blob is materialized into a run-owned evidence store with role, canonical source path, observation/origin, immutable hash, and safe locator; dirty/untracked/renamed/deleted evidence has explicit availability semantics.
- [x] Task D may additionally read only the installed Task D procedure and its declared usage reference; all evidence discovery and live-vault reads outside the materialized store are prohibited.
- [x] Candidate-record and idea-input destinations are derived from the authenticated handle and accept only Story 059 schemas; caller-selected stage/evidence/output paths, escapes, symlinks, special files, wrong owner/mode, and vault mismatch fail closed.

## Tasks

### Phase 1: Research

- [x] Verify managed-run begin/holder/handle and descriptor-relative containment APIs.
- [x] Define run-owned evidence/control/input layout and deleted/blob materialization rules.

### Phase 2: Tests (TDD - Write First!)

- [x] TEST-060-1: Public command invokes the internal collector and materializes every read-set entry byte-for-byte.
- [x] TEST-060-2: Dirty/untracked/renamed/deleted/blob evidence and procedure-reference exemptions are enforced.
- [x] TEST-060-3: Handle, path, symlink, special-file, owner/mode, and vault-binding attacks fail closed.

### Phase 3: Implementation

- [x] IMPL-060-1: Add run-owned dream layout and read-set materialization.
- [x] IMPL-060-2: Add the public managed `dream-harvest` command and authenticated candidate-input paths.

### Phase 4: Review

- [x] Focused and full tests pass
- [x] Security, Standards, and Spec reviews converge
- [x] Consumer-interface completion gate passes

## Routine Decision

This story composes existing managed-run primitives without adding or changing
a Shared Routine edge.

## Technical Notes

Story 057/058 own pure harvesting. This story alone owns the supported public
`dream-harvest` command; no unmanaged Task D entry point is supported.

## Definition of Done

- [x] All acceptance criteria met
- [x] All prerequisite stories are done
- [x] Security and code reviews approved
- [x] Stable usage note exists and is projected
- [x] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-23 | Created | Rescoped after story review |

| 2026-09-23 | Done | Implemented and verified; dogfood evidence in evidence/2026-09-23-dream-reflection-release |
