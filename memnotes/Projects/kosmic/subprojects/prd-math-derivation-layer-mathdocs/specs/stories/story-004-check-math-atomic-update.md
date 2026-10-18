---
status: "done"
created: "2026-09-05"
updated: "2026-09-05"
linked_epic: "../epics/epic-002-math-execution-verification.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["cli-projection-commands.md"]
consumer_interface_change: true
evidence_packs: ["2026-09-05-math-derivation-layer-impl"]
derivations: ["atomic-publication-state"]
math_implementation_files: ["skills/scripts/kosmic_project_skills.py"]
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: "prd-math-derivation-layer-mathdocs"
record_kind: "story"
local_id: "004"
---

# Story 013: Atomic Math-Note Update

## User Story

As a maintainer, I want verified results refreshed atomically, so that one
failed derivation cannot leave a mixed mathdocs state.

## Acceptance Criteria

- [x] `check-math --update` executes and validates every selected script before writing canonical state.
- [x] It updates only FR-003 metadata and the single generated region; human prose and Corrections remain byte-identical.
- [x] Temporary-registry validation precedes `publish_directory`; any execution, rendering, validation, or publication failure preserves all canonical files.
- [x] Successful update records current source hash/environment and produces a default `check-math` pass.

## Tasks

### Phase 1: Research
- [x] Reuse publish_directory rollback and metadata update patterns

### Phase 2: Tests (TDD)
- [x] TEST-013A: generated-region insertion/replacement and prose preservation
- [x] TEST-013B: multi-file success and all injected failure stages
- [x] TEST-013C: post-update read-only verification

### Phase 3: Implementation
- [x] IMPL-013A: deterministic result-block renderer
- [x] IMPL-013B: temporary mathdocs staging and full validation
- [x] IMPL-013C: atomic publication with rollback

### Phase 4: Review
- [x] Focused/full tests and mutation smoke check pass
- [x] Task 7 review approved

## Definition of Done

- [x] All acceptance criteria met
- [x] No partial-update path remains
- [x] Code reviewed; related usage note updated
