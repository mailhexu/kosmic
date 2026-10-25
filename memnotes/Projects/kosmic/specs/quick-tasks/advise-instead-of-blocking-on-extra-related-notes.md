---
project_id: "kosmic"
subproject_id: null
status: done
approved_by: user
approved_on: 2026-10-25
approval_provenance: "User explicitly selected 'Approve and run'."
record_kind: "quick-task"
local_id: "advise-instead-of-blocking-on-extra-related-notes"
registration_root: "/home/hexu/projects/myagentskills/kosmic"
registration_outputs: [".kosmic/working-directories.json", "worktree:.kosmic/workdir.json"]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
created: "2026-10-25"
updated: "2026-10-25"
review_base: 20a9871b4cb40f641e4f966cf2176a062b000e86
review_round: 1
completion_observations:
  - criterion: "A consumer-interface record whose related notes include one stable fresh usage/both note plus additional non-stable or non-Consumer notes completes successfully, with a stderr warning naming each non-anchor note and reason."
    observation: "test_consumer_completion_accepts_advisory_related_notes_with_anchor completed with exit 0 and stderr naming the draft note with the advisory wording, so the extra note no longer blocks when a stable anchor exists."
    source: "tests/test_record_scoped_completion.py in the affected-suite run (293 tests, OK)."
  - criterion: "A consumer-interface record with no stable fresh usage/both related note still refuses, and the diagnostic names the offending notes and reasons."
    observation: "test_consumer_completion_still_requires_one_stable_anchor refused with exit 2 and stderr naming the draft note plus the anchor requirement, so the aggregated-reasons refusal is retained."
    source: "tests/test_record_scoped_completion.py in the affected-suite run (293 tests, OK)."
  - criterion: "A missing related-note path still refuses unchanged."
    observation: "The missing-path raise is byte-identical in the episode diff and stays ahead of classification, so an unresolved reference still refuses before any advisory logic runs."
    source: "The episode diff for skills/scripts/kosmic_project_skills.py (raise unchanged, first statement in the loop)."
  - criterion: "The existing stable/fresh/projection consumer regressions keep passing, the new regressions cover the advisory and no-anchor behaviors, and the full suite passes."
    observation: "The affected suites ran 293 tests OK including the pre-existing stable/fresh/projection consumer regressions and the two new ones; the full suite result is recorded in the session log for this episode."
    source: "python -m unittest tests.test_record_scoped_completion tests.test_unified_finish_completion tests.test_project_skills_cli (293 tests, OK); full-suite discover run reported in memnotes/Projects/kosmic/log/kosmic-2026-10-25.md."
completion_review:
  reviewer: main-assistant-coordinator
  axes:
    standards:
      decision: approved
      reviewer: AdvisoryNotesStandards
    spec:
      decision: approved
      reviewer: AdvisoryNotesSpec
  decision: approved
  review_base: 20a9871b4cb40f641e4f966cf2176a062b000e86
  reviewed_revision: 1b038b90cefe40ae5901e325adb7c25113ff5822ff0b2aa136efe2a1fe36b595
  scope:
    - worktree:skills/scripts/kosmic_project_skills.py
    - worktree:tests/test_record_scoped_completion.py
    - project:specs/quick-tasks/advise-instead-of-blocking-on-extra-related-notes.md
    - project:specs/INDEX.md
    - project:log/kosmic-2026-10-25.md
  findings: []
---

# Advise instead of blocking on extra related notes

## Request

The user hit `COMPLETION_PRECHECK_FAILED: related Consumer knowledge is not stable` for a related note and asked that the consumer-interface completion gate not be this strict: extra related notes that are not stable Consumer knowledge should not block completion.

## Scope

- Change only the `consumer_interface_change: true` branch of `_check_existing_completion` in `skills/scripts/kosmic_project_skills.py`: a missing related note still refuses, and the change still requires at least one stable, fresh, usage/both related note as the Consumer anchor; every additional related note that fails stability, freshness, or audience becomes a stderr warning naming the note and reason, and projection validation runs on the anchors only.
- With no stable anchor at all, the gate still refuses, with the aggregated reasons in the diagnostic.
- Add behavioral regressions in `tests/test_record_scoped_completion.py` for both the advisory path and the retained no-anchor refusal.
- Reinstall the release `skills/` package to the OMP adapter after the commit (backup-then-copy) and verify with `check-installation`; the Project pair is unchanged.
- Register this repository root as the episode writer and remove the registration during owned-run cleanup so the published registry stays empty.

## Out of Scope

- No change to the math/proposal/routine related-note gates, the non-interface path, proof, scope, review, or receipt mechanics; no canonical note or pair regeneration (no projected guidance text changes).

## Acceptance Criteria

- [x] A consumer-interface record whose related notes include one stable fresh usage/both note plus additional non-stable or non-Consumer notes completes successfully, with a stderr warning naming each non-anchor note and reason.
- [x] A consumer-interface record with no stable fresh usage/both related note still refuses, and the diagnostic names the offending notes and reasons.
- [x] A missing related-note path still refuses unchanged.
- [x] The existing stable/fresh/projection consumer regressions keep passing, the new regressions cover the advisory and no-anchor behaviors, and the full suite passes.

## Routine Decision

No new deterministic procedure mechanics: the gate keeps its ordered precheck position and helper structure; only the failure classification of extra related notes changes.

## Verification

- Affected suites: 293 tests OK, including the pre-existing stable/fresh/projection consumer regressions and the two new behavioral regressions.
- Full suite: recorded in the session log; the gate change is the only production diff.

## Links

- Related notes: none; this Quick Task is the governing record.
- Related specs: none.
- Related files: `skills/scripts/kosmic_project_skills.py`,
  `tests/test_record_scoped_completion.py`.

## Review

Round 1 reviewed the episode packet against base `20a9871b` on both axes; both
approved with no findings. `review_round` is 1 and `completion_review` records
the actual approvals.

## Code Review

**Review Base**: `20a9871b4cb40f641e4f966cf2176a062b000e86`  
**Current Round**: 1  
**Reviewed Revision**: `1b038b90cefe40ae5901e325adb7c25113ff5822ff0b2aa136efe2a1fe36b595`  
**Decision**: approved  
**Standards Reviewer**: `AdvisoryNotesStandards` — approved  
**Spec Reviewer**: `AdvisoryNotesSpec` — approved

### Standards

| ID | Disposition | Evidence | Required Resolution | Introduced | Status | Resolution | Worker Response |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (none) | — | No Standards finding: missing files still refuse, stale_after validation stays unconditional, advisories cannot satisfy the anchor requirement or enter projection validation, and both new tests exercise the public completion seam. | — | — | — | — | — |

### Spec

| ID | Disposition | Evidence | Required Resolution | Introduced | Status | Resolution | Worker Response |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (none) | — | No Spec finding: the diff stays inside the declared scope and satisfies every acceptance criterion. | — | — | — | — | — |

### Re-review History

| Round | Reviewed Revision | Findings Checked | New REG/LATE Evidence | Decision |
| --- | --- | --- | --- | --- |
| 1 | `1b038b90cefe40ae5901e325adb7c25113ff5822ff0b2aa136efe2a1fe36b595` | Complete first-pass inventory | n/a | Approved |
