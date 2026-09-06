---
status: done
created: 2026-09-06
updated: 2026-09-06
linked_epic: ../epics/epic-12-proposal-behavior.md
linked_architecture: ../architecture-skill-proposer.md
linked_prd: ../prd-skill-proposer.md
related_notes: [cli-projection-commands.md]
evidence_packs: [2026-09-06-skill-proposal-loop-impl]
consumer_interface_change: true
proposal_required: false
review_base: ce222de2
review_round: 2
---

# Story 022: Behavioral Comparison and Review Gate

## User Story

As a Kosmic reviewer,
I want baseline and candidate skill behavior compared at a predeclared real seam,
So that acceptance demonstrates useful agent behavior rather than a plausible document edit.

## Acceptance Criteria

- [x] Task P and Task 7 define invariant inputs, observable verdict, creation no-skill baseline, update current-skill baseline, and candidate isolation.
- [x] Baseline and candidate records live in an execution Evidence Pack; accepted create/update proposals require resolvable `behavioral_evidence`.
- [x] Candidate files cannot be canonical or installed paths before acceptance; rejected candidate files are removed while evidence/proposal persist.
- [x] No-action proposals require reviewable rationale but no fabricated behavioral run.

## Tasks

### Phase 1: Research
- [x] Map Evidence Pack, review, publication, and scratch-file rules.

### Phase 2: Tests (TDD)
- [x] TEST-022A: accepted procedural proposal without behavioral evidence fails.
- [x] TEST-022B: valid evidence passes; canonical/installed candidate paths fail.
- [x] TEST-022C: no_action lifecycle passes without candidate evidence.

### Phase 3: Implementation
- [x] IMPL-022A: add behavioral procedure, review checks, and deterministic path/evidence validation.

### Phase 4: Review
- [x] Behavioral smoke fixture, full tests, and Task 7 review pass.

## Definition of Done

- [x] All acceptance criteria met; tests pass; review approved; docs and log updated.
