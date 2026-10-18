---
status: "done"
created: "2026-09-05"
updated: "2026-09-05"
linked_epic: "../epics/epic-004-math-workflow-release.md"
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
local_id: "008"
---

# Story 017: Mathdocs Dogfood and Release

## User Story

As a Kosmic maintainer, I want the complete math workflow proven on a real
SymPy derivation and installed everywhere, so that release claims are grounded.

## Acceptance Criteria

- [x] Kosmic Project contains a real script/note/index pair producing at least two named results with assumptions and units.
- [x] One stable conceptual note contains exact result and exposition markers, and one source file contains an adjacent `MathDoc:` reference.
- [x] Dogfood work item declares derivations and implementation files; `validate`, `check-math`, and `check-completion --source-root` pass.
- [x] A deliberately changed script fails source-hash/default verification; restored/update path passes and records environment/provenance.
- [x] Full suite and real smoke scenario pass; skill version is bumped, committed, pushed, installed, and diff-verified in codex/opencode/omp.

## Tasks

### Phase 1: Research
- [x] Select a genuine Kosmic-relevant symbolic derivation (not a toy identity)
- [x] Confirm host SymPy/Python and source-root provenance

### Phase 2: Tests (TDD)
- [x] TEST-017A: end-to-end real derivation smoke path
- [x] TEST-017B: dirty-script failure and update recovery

### Phase 3: Implementation
- [x] IMPL-017A: add mathdocs dogfood artifacts and source marker
- [x] IMPL-017B: update conceptual note/index/work-item/log
- [x] IMPL-017C: bump and install release

### Phase 4: Review
- [x] Independent Standards + Spec review converges
- [x] All gates pass at recorded code state

## Definition of Done

- [x] All acceptance criteria met
- [x] Review approved with stable finding ledger
- [x] Release committed, pushed, installed, and recorded
