---
project_id: "kosmic"
subproject_id: "deterministic-flat-spec-migration"
record_kind: "story"
local_id: "003"
status: done
created: "2026-10-11"
updated: "2026-10-11"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
depends_on: ["story-002.md"]
related_notes: ["notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "22a36f09af5fce16c2d097c68ab9988f27c3705f"
review_round: 3
acceptance_evidence: ["evidence/2026-10-11-deterministic-flat-spec-migration/acceptance-003.json"]
review_record: "evidence/2026-10-11-deterministic-flat-spec-migration/review-003.json"
---

# Story 003: Integrate and verify the migration workflow

## User Story

As a Project maintainer, I want documented commands and demonstrated end-to-end migration behavior, so that I can run the new workflow without paying for an agent to perform mechanical edits.

## Scope

Integrate and prove Stories 001/002 across the complete CLI, STATUS and proposal handling. Cover PRD FR-M01 through FR-M09 with criterion-specific observed evidence and complete-change review. Fix integration defects in the existing implementation rather than create alternate migration paths.

## Acceptance Criteria

- [ ] AC1: Actual plan/apply/recover commands migrate a disposable Project with multiple PRDs, existing owners, shared tasks/proposals, local and cross-owner dependencies and active inbound references. Final catalog identities and intended link targets match the approved plan.
- [ ] AC2: Evidence/log payloads and lifecycle/review decisions retain original bytes/meaning. Already canonical shared local IDs survive, owner indexes and Project navigation resolve, and unreceipted terminal work does not become implementation authority.
- [ ] AC3: Bound STATUS uses final Project paths and catalog state and rolls back with publication failure. Unbound STATUS is reported without a fabricated directory binding or external write.
- [ ] AC4: Mechanical and non-mechanical proposal fingerprint changes receive the required distinct dispositions. Existing decisions remain traceable; a non-mechanical change cannot inherit fingerprint-bound approval silently.
- [ ] AC5: The documented offline plan → review/approve → apply → verify/recover commands work without model calls or manual feature-record editing. Error guidance distinguishes plan regeneration, explicit ownership assignment, recovery and output drift. Migration and adapter-install approval boundaries are explicit.
- [ ] AC6: Complete-command regressions cover missing/revoked authority, ambiguity, inventory drift, plan tampering, occupied/escaping/symlinked targets, publication failure, interrupted recovery and completed-plan reruns; existing bounded tests pass without weakening behavior assertions.
- [ ] AC7: Independent Standards and Spec review covers the full planner/executor/CLI change against a pinned baseline, with stable finding IDs and no unresolved blocker unless explicitly accepted by the user. Real acceptance observations and artifact hashes cover every PRD success criterion.

## Tasks

### Research and Tests

- [ ] Verify Story 001/002 contracts and map each PRD requirement to observable CLI behavior.
- [ ] Pin the full-feature review baseline and use a clean dedicated worktree.
- [ ] Add tests only for uncertain integration boundaries; use disposable actual-command smoke for the primary workflow.

### Integration and Documentation

- [ ] Fix observed contract defects in the canonical modules/callers.
- [ ] Update supported command docs, Quick Task/migration guidance and stable consumer knowledge, preserving one convention.
- [ ] Exercise complete migration and recovery scenarios without touching live Projects or installed adapters.

### Verification and Review

- [ ] Run the bounded existing suite after integration and retain actual outputs in declared evidence.
- [ ] Complete convergent independent Standards/Spec review of the entire feature.
- [ ] Verify all callsites/docs and acceptance criteria; finish Stories/epic only through the existing checked completion contracts.

## Routine Decision

This Story integrates, documents and verifies deterministic mechanics governed by Stories 001/002; it does not introduce a new routine or procedure `uses_routines` edge. If an observed integration fix materially changes reusable mechanics or adds such an edge, amend this declaration and obtain its Task P decision before completion.

## Non-Goals

No live migration, model invocation during migration, adapter install, approval fabrication or automatic conversion of historical done status into a new completion receipt. Successful temporary fixtures do not approve migration of another Project.

## Progress

Approved by the user and implemented. The integrated repository CLI migrated two temporary flat features alongside an existing owner, verified cross-owner dependencies and original-source receipt hashes, created bound STATUS matching final rendering and returned the same receipt on repetition. Forty-eight focused migration/audit checks and the complete 15-module suite passed; independent Standards and Spec review converged. Evidence is declared above. No live Project migration or adapter installation ran, and canonical terminal closure remains separately gated.
