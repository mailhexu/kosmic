---
status: "done"
created: "2026-09-08"
updated: "2026-09-08"
related_notes: ["../../notes/abinit-procedure-skill-calibration.md"]
related_specs: ["../../subprojects/shared-domain-skill-library/specs/architecture.md", "../../subprojects/semantic-artifact-roles/specs/architecture.md"]
related_files: ["../../../Skills/abinit/SKILL.md", "../../../../../skills/references/task_project_skills.md"]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
review_base: "c52ab6a15b2dab0df9cbd450a76fcdc386612cdb"
review_round: 0
project_id: "kosmic"
subproject_id: null
record_kind: "quick-task"
local_id: "2026-09-08-scoped-abinit-mpi-source-project"
---

# Quick Task: Scoped ABINIT MPI Source Project

## Request

Adopt a scoped ABINIT source Project for the MPI CG-reduction material so it can later supply same-vault provenance to Task 9 and Task P.

## Scope

- Create `Projects/abinit/` as a deliberately scoped, authoritative source Project for ABINIT MPI CG-reduction guidance.
- Preserve the historical template as dated migration evidence rather than copying it into the Shared Domain Library.
- Distill the supported MPI material into role-classified Project notes and record the bounded adoption boundary.
- Validate the resulting Project bundle.

## Out of Scope

- Adopt the external ABINIT Project in full.
- Propose, publish, or install `abinit/development/implement-cg-mpi-reduction`.
- Change the Shared Domain Library or its router.
- Claim that the historical validation is current execution evidence.

## Acceptance Criteria

- [x] `Projects/abinit/` has immutable identity, an explicit scoped-authority boundary, and valid note bundle structure.
- [x] The MPI source material is represented as Project knowledge, a governing guideline, and historical evidence without operational promotion.
- [x] A dated Evidence Pack records external provenance and its limits.
- [x] The Project validation command passes.
- [x] Log updated.
- [x] Notes and specs index updated.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed.

## Implementation Notes

The user selected a scoped MPI source Project instead of full Project adoption. The new source Project owns only provenance and future evidence for the MPI CG-reduction packet. Its notes retain `draft` status until current ABINIT execution refreshes the historical topology matrix. Task 9 and a fresh Task P proposal remain separate future work.

## Verification

- `python3 skills/scripts/kosmic_project_skills.py generate --project memnotes/Projects/abinit`: published the scoped Project Skill Pair atomically.
- `python3 skills/scripts/kosmic_project_skills.py validate --project memnotes/Projects/abinit`: PASS.

## Links

- Related notes: [ABINIT Procedure-Skill Calibration](../../notes/abinit-procedure-skill-calibration.md)
- Related specs: [Shared Domain Skill Library Architecture](../../subprojects/shared-domain-skill-library/specs/architecture.md), [Semantic Artifact Roles Architecture](../../subprojects/semantic-artifact-roles/specs/architecture.md)
- Related files: `memnotes/Skills/abinit/SKILL.md`, `skills/references/task_project_skills.md`

## Review

- [x] Diff reviewed against scope
- [x] Acceptance criteria satisfied
- [x] Status set to `done` after verification passed.
- Standards review: no findings.
- Spec review: no findings.
