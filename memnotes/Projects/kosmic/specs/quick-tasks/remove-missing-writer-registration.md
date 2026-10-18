---
project_id: "kosmic"
subproject_id: null
status: done
record_kind: "quick-task"
local_id: "remove-missing-writer-registration"
approval_note: User selected removal of only the confirmed missing old library-repair writer registration.
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "7dab77c8fee74a3edaa3fa48d1128d4668877da1"
review_round: 0
acceptance_evidence: [evidence/2026-10-13-registration-maintenance/acceptance.json]
review_record: evidence/2026-10-13-registration-maintenance/review.json
---

# Remove missing writer registration

## Scope

Remove only `wd-083ca86fb05f081a` from the canonical Project directory registry after confirming its path does not exist. Preserve every other registration and adjust the required `sequence == len(directories)` count from 3 to 2; do not delete files or modify other tasks. Retry the already reviewed skill-repair completion transaction, then complete this bounded maintenance with observed evidence and independent review.

## Acceptance Criteria

- [ ] Only the confirmed missing writer registration is removed; other registry entries remain identical.
- [ ] Checked skill-repair finish returns a successful receipt and terminal receipt validation passes.
- [ ] No directory or unrelated task is deleted or rewritten by the maintenance edit.
