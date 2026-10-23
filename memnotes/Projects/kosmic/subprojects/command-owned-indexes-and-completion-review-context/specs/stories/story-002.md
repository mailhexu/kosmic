---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: "approved"
record_kind: "story"
local_id: "002"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: ["kosmic/command-owned-indexes-and-completion-review-context/story/001"]
created: "2026-10-23"
updated: "2026-10-23"
related_notes: ["notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: true
routine_proposals: []
review_round: 0
completion_observations: []
completion_review: {}
---

# Finish index coordination and native workflow cutover

## User Story

As a Kosmic caller, I want native creation and finish to preserve each other's index changes and the instructions to use their outputs directly, so the workflow requires no agent-written rows or redundant confirmation passes.

## Authority and Scope

Parent: [Epic 001](../epics/epic-001.md); requirements: creation/index FR-008 and integration of FR-001–004; design: Architecture ADR-003–004 and Caller Cutover.

Depends on receipted completion of [Story 001](story-001.md). Own finish's supported index-writer coordination, real create-through-finish behavior, and all native-index caller/reference/knowledge cutover. Do not change finish admission, review/receipt semantics, publication order, or historical index policy.

Likely source seams: `kosmic_completion.py::_update_indexes`, Story 001's existing creation-lock helpers, workflow references/templates, `skills/SKILL.md`, README, `record_first_contract()` and the repository instruction caller. Update the existing canonical CLI note and regenerate projections; never edit generated or installed copies directly. Installation, global router changes and Git push are not added by this Story.

## Acceptance Criteria

- [ ] AC-001: Supported interleaved creation and finish updates use the existing creation lock for index read/merge/publication and retain all relevant rows/statuses; unrelated index content is unchanged.
- [ ] AC-002: A native-created implementation record completes through actual `work finish`, its owning canonical row becomes `done`, and existing proof/review/source/authority/receipt gates still decide completion.
- [ ] AC-003: Index coordination adds no recursive lock acquisition, new finish admission rule or publication-order change. Detected external index divergence is refused without overwriting; arbitrary non-cooperating editors are not claimed to be transactionally serialized.
- [ ] AC-004: All current creation callers and generated guidance consume returned native identities/paths and use owning-operation resume. Obsolete manual row-creation and PRD-only resume instructions are removed without leaving a second fallback convention.
- [ ] AC-005: Instructions retain user approval gates, full-absolute-path handoff links and trust in successful commands; research/non-native artifacts and historical missing rows are not falsely described as automatically indexed.
- [ ] AC-006: Canonical CLI knowledge and generated projections describe the exercised behavior consistently. The real documented create/resume/finish sequence works without a manual index edit or administrative validation round-trip.

## Implementation and Verification

1. Reuse Story 001's implemented contract; inspect lock ownership and current finish index updates. Pin one fixed review baseline before this Story's source changes.
2. TDD through existing creation/work-record/finish suites: preserve both writers' changes, observe actual status transitions and retain representative refusal/receipt behavior. Test outcomes, not lock calls or copied prose.
3. Acquire the existing creation lock only around finish index updates, with a clear lock-owned helper convention and unchanged completion order.
4. Migrate every native-index caller/reference and the canonical CLI invariant note only after native behavior is exercised. Retain manual handling solely where the command does not own the artifact.
5. Smoke the actual documented creation, interruption/resume and finish path on governed disposable fixtures. Use outputs directly; do not add confirmation-only checks.
6. Integrate related note edits under one writer and regenerate the canonical Skill Pair through the normal publication path. Capture actual observations and independent revision-bound Standards/Spec review before native completion.

## Routine Decision

This changes deterministic coordination used by repeated creation/finish procedures, so the existing routine-decision gate applies. Inspect the generated inventory and record the applicable governed Task P disposition(s) in `routine_proposals` before completion. Reuse the existing CLI/lock ownership; no automatic routine extraction, publication or new authority follows from classification.

## Technical Notes and Boundaries

- Native finish owns completion logging, existing-row status changes and final receipt-derived STATUS. Do not duplicate those writes or refresh STATUS after successful finish.
- Story 001 owns deterministic creation/recovery. This Story must not silently widen that reservation contract while integrating finish.
- [Story 003](story-003.md) owns fingerprint instructions. Shared CLI/reference/note edits have one integration owner and are reconciled, not concurrently overwritten.
- A matching fingerprint is not enough for excluded record context; existing context/scope review remains required.

## Completion

Require all AC observations, related-note/projection consistency, applicable routine decisions, actual CLI smoke, converged independent review and native completion receipt. Run the affected integrated suite after changes stabilize; rerun only for changed inputs or failures. No evidence sidecar, optional-suggestion scope growth or hand-written `done`.

Approved by the user in this conversation. Implementation may proceed after Story 001's receipted completion; no results are claimed yet.
