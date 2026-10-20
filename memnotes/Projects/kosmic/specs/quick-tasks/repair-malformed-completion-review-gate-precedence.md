---
project_id: kosmic
subproject_id: null
record_kind: quick-task
local_id: repair-malformed-completion-review-gate-precedence
status: done
created: '2026-10-20'
updated: '2026-10-20'
consumer_interface_change: true
related_notes: [notes/cli-projection-commands.md]
related_specs: [subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-001.md]
related_files: [skills/scripts/kosmic_completion.py, tests/test_unified_finish_completion.py, skills/references/work_completion.md]
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: cd24ce98f812c27d5b7f6cebe9e58aa555534664
review_round: 2
completion_observations:
  - criterion: "Truthy non-mapping completion_review values are refused with REVIEW_INVALID rather than an uncaught exception when preceding gates pass."
    observation: "A new public-CLI regression failed before the source fix (exit1/AttributeError) and passed afterward for nonempty list, string and integer completion_review values, each refusing as REVIEW_INVALID with exit2, no traceback and no publication."
    source: "New red/green CLI regression; 28 focused unittest cases; disposable actual CLI smoke; parent execution output"
  - criterion: "Invalid proof and unclaimed changes retain ACCEPTANCE_INVALID and SCOPE_DENIED precedence respectively even when review metadata is malformed; no record or receipt is published on refusal."
    observation: "The new CLI regression verifies ACCEPTANCE_INVALID for missing proof and SCOPE_DENIED for unclaimed changes despite malformed review; record bytes remain identical and no receipt appears. The disposable actual-CLI harness also reached these refusal guards without failure."
    source: "New red/green CLI regression; 28 focused unittest cases; disposable actual CLI smoke; parent execution output"
  - criterion: "Existing reviewed-source and record freshness guards remain effective, and focused completion/prefill regression checks pass."
    observation: "The focused completion/prefill run passed all 28 tests in 13.064s, including unchanged record/source freshness guards. The fix retains entry capture and compares the final source hash to the original reviewed_revision; no gates were moved."
    source: "New red/green CLI regression; 28 focused unittest cases; disposable actual CLI smoke; parent execution output"
  - criterion: "The actual CLI correction is exercised, independent Standards/Spec review approves the scoped change, and all pre-existing completed Story and receipt bytes remain unchanged."
    observation: "The throwaway CLI harness passed the refusal, valid receipt and immutable retry guards before a cross-interpreter help-byte-comparison failed. Matching the help interpreter fixed that harness-only comparison without product changes. Independent review and canonical historical-byte verification are recorded separately; no pre-existing Story or receipt is edited. Native finish initially refused projection drift in the relocated writer; native generate refreshed only that writer's derived Skill Pair, leaving the reviewed source_revision unchanged. Those private generated paths will not be integrated into Original."
    source: "New red/green CLI regression; 28 focused unittest cases; disposable actual CLI smoke; parent execution output"
completion_review:
  reviewer: "Main (integration coordinator)"
  axes:
    standards:
      reviewer: "CorrectionStandardsReview"
      decision: "approved"
    spec:
      reviewer: "CorrectionSpecReview"
      decision: "approved"
  decision: "approved"
  review_base: "cd24ce98f812c27d5b7f6cebe9e58aa555534664"
  reviewed_revision: "c00ee0e1d5bbee16760a962f8f05a3c061b113e32c2498b4a43161bfa780513e"
  findings:
    - id: "STD-001"
      axis: "standards"
      disposition: "Blocking"
      status: "resolved"
      introduced_round: 1
      evidence: "CorrectionStandardsReview approved: dict-safe entry capture; original gate order and freshness retained; public CLI regression green."
    - id: "SPEC-001"
      axis: "spec"
      disposition: "Blocking"
      status: "resolved"
      introduced_round: 1
      evidence: "CorrectionSpecReview approved: REVIEW_INVALID and preceding ACCEPTANCE_INVALID/SCOPE_DENIED contracts preserved without publication."
  scope:
    - "worktree:skills/scripts/kosmic_completion.py"
    - "worktree:tests/test_unified_finish_completion.py"
    - "worktree:skills/references/work_completion.md"
    - "project:specs/quick-tasks/repair-malformed-completion-review-gate-precedence.md"
    - "project:specs/INDEX.md"
    - "project:skills/"
registration_root: /home/hexu/projects/myagentskills/kosmic/.tmp/kosmic/runs/20261020T060344Z-workflow-review-correcti-b539ce7f427497e56cb78e591f4d6bee/scratch/runtime
registration_outputs: [.kosmic/working-directories.json, 'worktree:.kosmic/workdir.json']
---

# Repair malformed completion review gate precedence

## Request

User said “next” after the independent full implementation review. Repair STD-001 / SPEC-001 without broadening the approved completion contract. This is a bounded correction, not new authority to modify completed Stories.

## Scope

- Make the existing entry-snapshot capture safe for non-mapping completion_review metadata; preserve proof → primary scope → review → domain ordering and final freshness checks.
- Add a consumer-visible regression at the existing completion boundary and clarify the existing completion reference.
- This record also authorizes registering its exact isolated writer once registration_root and registration_outputs are declared, local derived STATUS, this record, shared specs index, and one completion/session log entry.

## Out of Scope

- Changes to receipt schemas, completed Stories or receipt bytes, public API shapes, installed skills, unrelated proposals, global vaults, or unrelated user work.
- New routine mechanics, fallback approval, or weakened completion gates.

## Acceptance Criteria

- [ ] Truthy non-mapping completion_review values are refused with REVIEW_INVALID rather than an uncaught exception when preceding gates pass.
- [ ] Invalid proof and unclaimed changes retain ACCEPTANCE_INVALID and SCOPE_DENIED precedence respectively even when review metadata is malformed; no record or receipt is published on refusal.
- [ ] Existing reviewed-source and record freshness guards remain effective, and focused completion/prefill regression checks pass.
- [ ] The actual CLI correction is exercised, independent Standards/Spec review approves the scoped change, and all pre-existing completed Story and receipt bytes remain unchanged.

## Routine Decision

No reusable deterministic mechanics or uses_routines edges are introduced or materially changed; this restores existing input-validation and refusal-order contracts.

## Implementation Notes

The prior audit already reproduced the failure before modification: baseline emitted ACCEPTANCE_INVALID / SCOPE_DENIED / REVIEW_INVALID; release emitted AttributeError for a truthy list in all three cases. Preserve the exact record snapshot before gates, safely capture the original review revision, and leave structural review validation at its existing ordered gate. Regression seam: the existing work finish consumer boundary, asserting specific error codes and absence of publication.

Writer note 2026-10-20: in the isolated writer, `finish_work` now extracts `reviewed_revision` only when the original `completion_review` is a dict — the record-byte snapshot stays at entry before every gate, non-mapping values are never coerced, and structural refusal stays at the existing `_checked_review` position after proof and primary scope. Added consumer regression `tests/test_unified_finish_completion.py::UnifiedFinishCompletionTest.test_malformed_completion_review_refused_after_proof_and_scope` (nonempty list/string/int subcases; ACCEPTANCE_INVALID and SCOPE_DENIED precedence; unchanged record bytes/status; no receipt) and one ordering sentence in `skills/references/work_completion.md`. Red run (AttributeError before the fix) was observed by the parent; green and all integrated checks remain parent-owned.

## Approval

Approved by the user's continuation of the reported fixes on 2026-10-20; no product or architecture change.
