---
project_id: kosmic
subproject_id: null
record_kind: quick-task
local_id: restore-cli-executable-release-and-observable-verification-guida
status: done
created: '2026-10-20'
updated: '2026-10-20'
consumer_interface_change: true
related_notes: [notes/cli-projection-commands.md]
related_specs: [subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-003.md]
related_files: [skills/scripts/kosmic_project_skills.py, skills/references/task_implement_story.md, README.md]
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: cd24ce98f812c27d5b7f6cebe9e58aa555534664
review_round: 2
completion_observations:
  - criterion: "The committed CLI artifact has executable Git mode 100755; direct execution and Python-prefixed invocation both render the actual CLI help, with script bytes otherwise unchanged."
    observation: "The isolated script has executable mode0755 and unchanged bytes; actual direct and Python-prefixed --help both exit0 and render byte-identical help when run with the same Python3.12.10 interpreter. The committed final artifact mode is checked separately at publication."
    source: "Actual matched-interpreter direct/Python CLI help; bounded guidance review; canonical creation handoff in parent conversation"
  - criterion: "Story implementation guidance requires one observable check per criterion without requiring a permanent prose or incidental-wording test, while preserving tests for consumer-visible runtime behavior and real policy/handoff exercises."
    observation: "The retained per-criterion permanent-test mandate was replaced by an observable check per criterion, permanent tests for changed consumer-visible runtime boundaries, and real workflow/producer exercises for policy/handoff; TDD and review safeguards remain unchanged."
    source: "Actual matched-interpreter direct/Python CLI help; bounded guidance review; canonical creation handoff in parent conversation"
  - criterion: "The bounded guidance change is exercised against an actual policy-only handoff example, independent Standards/Spec review approves, and pre-existing completed Story and receipt bytes remain unchanged."
    observation: "This episode exercised a policy-only creation handoff using actual full-absolute-path Markdown links to both existing canonical correction records in the user conversation, without a permanent prose or wording test. The initial combined help comparison failed only because interpreter versions differed; targeted matched-interpreter help passed. Independent review and historical-byte verification are recorded separately. Native finish initially refused projection drift in the relocated writer; native generate refreshed only that writer's derived Skill Pair, leaving the reviewed source_revision unchanged. Those private generated paths will not be integrated into Original."
    source: "Actual matched-interpreter direct/Python CLI help; bounded guidance review; canonical creation handoff in parent conversation"
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
  reviewed_revision: "19190da81fa724bdf09719c78d68298cfc8a6ed573a13e67b58fb64b4d6dd0cd"
  findings:
    - id: "STD-002"
      axis: "standards"
      disposition: "Blocking"
      status: "resolved"
      introduced_round: 1
      evidence: "CorrectionStandardsReview approved pure 100644 to 100755 mode restoration with no source-byte change; actual help passed."
    - id: "SPEC-002"
      axis: "spec"
      disposition: "Blocking"
      status: "resolved"
      introduced_round: 1
      evidence: "CorrectionSpecReview approved observable verification rule retaining runtime tests and real policy/handoff exercises."
  scope:
    - "worktree:skills/scripts/kosmic_project_skills.py"
    - "worktree:skills/references/task_implement_story.md"
    - "worktree:README.md"
    - "project:specs/quick-tasks/restore-cli-executable-release-and-observable-verification-guida.md"
    - "project:specs/INDEX.md"
    - "project:skills/"
registration_root: /home/hexu/projects/myagentskills/kosmic/.tmp/kosmic/runs/20261020T060344Z-workflow-review-correcti-b539ce7f427497e56cb78e591f4d6bee/scratch/guidance
registration_outputs: [.kosmic/working-directories.json, 'worktree:.kosmic/workdir.json']
---

# Restore CLI executable release and observable verification guidance

## Request

User said “next” after the independent full implementation review. Repair STD-002 and SPEC-002 as bounded corrections to existing behavior and guidance.

## Scope

- Restore Git mode 100755 for skills/scripts/kosmic_project_skills.py without changing its source bytes.
- Replace the retained permanent-test-per-criterion mandate with one observable check per criterion, keeping permanent tests for new or changed consumer-visible runtime boundaries and real producer/handoff exercises for policy criteria.
- Clarify the existing README invocation/verification guidance only as needed for these corrections.
- This record also authorizes registering its exact isolated writer once registration_root and registration_outputs are declared, local derived STATUS, this record, shared specs index, and one completion/session log entry.

## Out of Scope

- Source logic changes, permanent wording/wiring tests, new artifact classes, changed review/approval/receipt contracts, completed Story edits, installed skills, global vaults, or unrelated work.

## Acceptance Criteria

- [ ] The committed CLI artifact has executable Git mode 100755; direct execution and Python-prefixed invocation both render the actual CLI help, with script bytes otherwise unchanged.
- [ ] Story implementation guidance requires one observable check per criterion without requiring a permanent prose or incidental-wording test, while preserving tests for consumer-visible runtime behavior and real policy/handoff exercises.
- [ ] The bounded guidance change is exercised against an actual policy-only handoff example, independent Standards/Spec review approves, and pre-existing completed Story and receipt bytes remain unchanged.

## Routine Decision

No deterministic routine mechanics or uses_routines edges change. This restores an existing executable artifact mode and resolves contradictory prose.

## Implementation Notes

The prior audit verified the released 0644 bytes failed direct execution with Permission denied while the same bytes at 0755 rendered help. The working-tree script is already executable; the release object, not just local stat, must retain the corrected mode. Use an observable policy/handoff exercise rather than a permanent text assertion.

## Approval

Approved by the user's continuation of the reported fixes on 2026-10-20; no product or architecture change.
