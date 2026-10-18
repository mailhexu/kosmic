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
depends_on: ["story-006-dream-run-recovery-concurrency.md"]
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "dream-reflection"
record_kind: "story"
local_id: "007"
---

# Story 063: Dream Workflow Dogfood Release

## User Story

As a Kosmic user,
I want a documented Task D workflow proven against pinned real history,
So that a new session starts from trustworthy reflection and useful next ideas.

## Acceptance Criteria

- [x] Completion fails unless Stories 057–062 are `done`; `references/task_dream.md`, task routing, README, and stable usage knowledge expose Task D without claiming the CLI performs judgment.
- [x] Before tests, a checked-in dogfood manifest pins target date 2026-09-16, captured HEAD/commits/blobs, expected completed/open work sets, seeded link/contradiction inputs, expected candidate evidence, second date, allowed runtime persistent write set, and evidence-pack destination.
- [x] A machine-readable Task D result/transcript schema makes routing, evidence reads, record sections, candidates/ideas, and publish/abort outcomes checkable rather than subjective.
- [x] Dogfood matches the pinned oracle, includes frontmatter fallback, links both contradiction inputs, and proposes a repeated mechanic without creating a proposal file.
- [x] Two dates plus same-date rerun prove index uniqueness, idea dedupe, and manual-divergence protection.
- [x] During the dogfood runtime, persistent vault publication changes only `memnotes/dreams/`; managed private scratch/control artifacts are allowed by lifecycle and cleaned/retained normally. Usage-note, generated-skill, evidence, and session-log updates occur separately as implementation/release changes.
- [x] Evidence pack, completion gates, full suite, Skill Pair generation/validation, and all adapter byte checks pass; Standards and Spec reviews converge.

## Tasks

### Phase 1: Research

- [x] Verify Task Review/9/P and managed-run routing conventions.
- [x] Write and independently check the pinned dogfood oracle manifest before any behavioral test.

### Phase 2: Tests (TDD - Write First!)

- [x] TEST-063-1: Checker validates the machine-readable Task D transcript/result against the pinned oracle.
- [x] TEST-063-2: Before/after snapshots enforce the persistent runtime write boundary and governance negatives.

### Phase 3: Implementation

- [x] IMPL-063-1: Add Task D procedure, task selection, README, stable usage note, and generated Skill Pair updates.
- [x] IMPL-063-2: Run pinned two-date/rerun dogfood and publish immutable evidence.
- [x] IMPL-063-3: Run completion/full/adapters/review release gates.

### Phase 4: Review

- [x] Behavioral dogfood and full suite pass
- [x] Standards and Spec reviews converge
- [x] Knowledge notes and session log updated

## Routine Decision

Task D orchestrates existing project-local commands and approved publication
mechanics; it introduces no new Shared Routine edge.

## Technical Notes

Skill Candidates remain in-record prose. Any later proposal begins a separate
Task 9 → Task P approval flow.

## Definition of Done

- [x] All acceptance criteria met
- [x] Stories 057–062 are done
- [x] Pinned oracle and evidence are immutable
- [x] Stable usage note and generated skills are current
- [x] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-09-23 | Created | Pinned dogfood/release draft |

| 2026-09-23 | Done | Implemented and verified; dogfood evidence in evidence/2026-09-23-dream-reflection-release |
