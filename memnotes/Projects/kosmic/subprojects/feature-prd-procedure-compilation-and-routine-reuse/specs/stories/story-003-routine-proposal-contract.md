---
status: "done"
created: "2026-09-07"
updated: "2026-09-07"
linked_epic: "../epics/epic-002-routine-governance.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
proposal_required: false
review_base: "c52ab6a15b2dab0df9cbd450a76fcdc386612cdb"
review_round: 1
consumer_interface_change: true
related_notes: ["cli-projection-commands.md"]
evidence_packs: ["2026-09-07-procedure-compilation"]
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
project_id: "kosmic"
subproject_id: "feature-prd-procedure-compilation-and-routine-reuse"
record_kind: "story"
local_id: "003"
---

# Story 039: Routine Proposal Contract

## Story

As a Reviewer, I want routine decisions represented in Task P without changing its result vocabulary so that compatibility and rejection memory remain intact.

## Acceptance Criteria

- [x] Add routine target/action/link/consumer-approval fields and the `shared-routine` scope with the exact mapping in AD-PC7.
- [x] Validate `routine://domain/slug` references, create/update hashes, owner authority, consumer approvals, and bidirectional linked proposals.
- [x] Require the four-part Routine Candidate section for create/extend and valid inventory matches for reuse.
- [x] Include explicit routine fields in fingerprints while preserving byte-identical legacy done/rejected fingerprints when absent.
- [x] Extend Task P templates and docs; tests cover all five routine actions and invalid combinations.

## Routine Decision

This story extends proposal policy rather than compiling mechanics; `routine_decision_required` is false.

## Tasks

- [x] Write focused failing proposal compatibility tests.
- [x] Implement routine proposal validation and templates.
- [x] Run focused and full regression suites.
- [x] Complete Standards and Spec review.

## Definition of Done

- [x] All acceptance criteria pass through public CLI behavior.
- [x] Legacy proposal fingerprints remain byte-identical.
- [x] No Blocking, High, or Medium review finding remains.
