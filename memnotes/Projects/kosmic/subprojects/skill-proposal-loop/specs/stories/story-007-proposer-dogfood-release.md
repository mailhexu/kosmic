---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_epic: "../epics/epic-004-proposal-activation-release.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["cli-projection-commands.md"]
evidence_packs: ["2026-09-06-skill-proposal-loop-impl"]
consumer_interface_change: true
proposal_required: true
skill_proposal: "../skill-proposals/2026-09-06-kosmic-proposer-dogfood.md"
review_base: "ce222de2"
review_round: 2
project_id: "kosmic"
subproject_id: "skill-proposal-loop"
record_kind: "story"
local_id: "007"
---

# Story 024: Proposer Dogfood and Release

## User Story

As a Kosmic maintainer,
I want one real fresh-context Skill Proposal completed and the release installed,
So that the new loop is proven by its own intended behavior rather than fixtures alone.

## Acceptance Criteria

- [x] A dedicated fresh-context proposer subagent receives only the curated manifest and emits one real Kosmic create/update/no_action artifact.
- [x] Proposal validation, human approval, isolated candidate implementation when applicable, baseline/candidate comparison, and independent Task 7 review complete in order.
- [x] Acceptance or rejection is appended to `impact.md`; equivalent-rejection behavior is demonstrated when applicable.
- [x] Full suite and real CLI smoke checks pass; version is bumped, committed, pushed, generated pair refreshed, and supported adapter installations byte-verify.
- [x] Active-session discovery is either observed through an adapter inventory or explicitly recorded as unverified with the required reload action.

## Tasks

### Phase 1: Research
- [x] Select a genuine existing Kosmic Pattern and build the curated proposer manifest.

### Phase 2: Tests (TDD)
- [x] TEST-024A: end-to-end proposal lifecycle fixture and real behavioral comparison.

### Phase 3: Implementation
- [x] IMPL-024A: run proposer, approval, candidate, behavioral gate, ledger outcome, publication, and adapter installation.

### Phase 4: Review
- [x] Independent Standards and Spec reviews converge.
- [x] All gates pass at recorded code state.

## Definition of Done

- [x] All acceptance criteria met; evidence and notes current; release committed, pushed, installed, and recorded.
