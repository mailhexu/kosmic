---
project_id: {PROJECT_ID}
subproject_id: null
record_kind: quick-task
local_id: {ALLOCATED_LOCAL_ID}
status: draft
created: {DATE}
updated: {DATE}
related_notes: []
related_specs: []
related_files: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
# When true, add: skill_proposal: ../skill-proposals/YYYY-MM-DD-slug.md
# For math-derived implementation, uncomment and populate both:
# derivations: [{slug}]
# math_implementation_files: [relative/source/path.py]
review_base: ""
review_round: 0
completion_observations: []
completion_review: {}
---

# Quick Task: {Title}

## Request

{Original user request or concise summary.}

## Scope

- {What will change}

## Out of Scope

- {What will not change}

## Acceptance Criteria

- [ ] {Concrete expected result}
- [ ] Tests or verification pass
- [ ] Log updated
- [ ] Notes updated if durable knowledge was learned
- [ ] Specs index updated

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed.

## Implementation Notes

{Short technical plan.}

## Verification

- {Command/check}: {result}

## Links

- Related notes: {links}
- Related specs: {links}
- Related files: {paths}

## Review

- [ ] Diff reviewed against scope
- [ ] Acceptance criteria satisfied
- [ ] Status set to `done` only after verification passes
