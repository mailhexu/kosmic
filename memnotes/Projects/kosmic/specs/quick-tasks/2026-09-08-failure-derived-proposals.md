---
status: done
created: 2026-09-08
updated: 2026-09-08
related_notes: [../../notes/abinit-procedure-skill-calibration.md]
related_specs: [../prd-skill-proposer.md, ../architecture-skill-proposer.md]
related_files: [skills/SKILL.md, skills/references/task_distill.md, skills/references/task_propose_skill.md]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: c52ab6a15b2dab0df9cbd450a76fcdc386612cdb
review_round: 0
---

# Quick Task: Failure-Derived Procedure Proposals

## Request

Incorporate the ABINIT calibration lesson into Kosmic: repeatedly failed work that yields a general invariant, recovery, and verification matrix is a signal to consider a procedure proposal; it is not automatic promotion.

## Scope

- Add the failure-derived admission rule to Task 9 and Task P.
- Make the root Kosmic Task P routing state the rule concisely.

## Out of Scope

- Changing proposal schemas, CLI behavior, resolver ranking, or artifact-role vocabulary.
- Promoting any ABINIT candidate or creating a Task P artifact.

## Acceptance Criteria

- [x] Task 9 distinguishes one-off incidents from evidence supporting a procedure candidate.
- [x] Task P requires a generalized invariant, recovery, reproducer/verification matrix for failure-derived candidates.
- [x] Root Task P routing states that repeated failure is a signal rather than automatic publication.
- [x] Kosmic skill bundle validation passes.
- [x] Log and specs index updated.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed.

## Implementation Notes

The user explicitly requested this implementation. The change is workflow prose only and remains within the approved Skill Proposal Loop architecture.

## Verification

- `python3 skills/scripts/kosmic_project_skills.py validate --project memnotes/Projects/kosmic`: PASS.
- `python3 skills/scripts/kosmic_project_skills.py check-completion --project memnotes/Projects/kosmic --work-item memnotes/Projects/kosmic/specs/quick-tasks/2026-09-08-failure-derived-proposals.md --source-root .`: PASS.

## Links

- Related notes: [ABINIT Procedure-Skill Calibration](../../notes/abinit-procedure-skill-calibration.md)
- Related specs: [Skill Proposal Loop PRD](../prd-skill-proposer.md), [Architecture](../architecture-skill-proposer.md)

## Review

- [x] Standards review: no findings.
- [x] Spec review: no findings.
- [x] Acceptance criteria satisfied; status set to `done`.
