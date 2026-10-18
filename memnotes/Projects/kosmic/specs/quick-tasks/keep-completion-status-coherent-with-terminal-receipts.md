---
project_id: "kosmic"
subproject_id: null
status: "approved"
record_kind: "quick-task"
local_id: "keep-completion-status-coherent-with-terminal-receipts"
acceptance_evidence: [evidence/2026-10-15-completion-status-coherence/acceptance.json]
review_record: evidence/2026-10-15-completion-status-coherence/review.json
created: "2026-10-15"
updated: "2026-10-15"
review_base: "906c0ab"
consumer_interface_change: true
related_notes: [cli-projection-commands]
---

# Keep completion STATUS coherent with terminal receipts

## Scope

Continue the approved completion/recovery work. Fix the reproduced mismatch between successful `work finish` receipts and STATUS projections, and correct related workflow command guidance (required --work-record arguments, unsupported --record flag, and inaccurate atomic/receipt-last claims). Preserve unrelated work and historical pending receipts. No installations, source Git commits, blanket scope claims, or retroactive review approvals.

## Reproduction

A disposable existing WorkRecordTest fixture driven through the real `work finish` CLI returned exit 0 and a successful checked receipt, but `status_drift(load_project(project))` immediately returned true. STATUS still described the completed record as `done (receipt pending)`.

## Decision

Publish the validated authoritative receipt before deriving final STATUS bytes. A retry with an already-valid receipt must repair interrupted STATUS publication without changing the receipt or duplicating completion logging. This replaces the inaccurate receipt-last report ordering; it does not claim cross-file atomicity. Keep review and acceptance gates intact.

## Acceptance Criteria

- [ ] Successful finish leaves its receipt valid and every registered or bound STATUS projection current.
- [ ] Retrying after interrupted STATUS publication repairs the projections without rewriting the receipt or duplicating the completion log.
- [ ] Missing or stale proof still blocks completion; unrelated pending historical records remain pending.
- [ ] Workflow and generated guidance use supported work-record flags and accurately describe recoverable, non-atomic publication.
## Verification seams

Use the existing real CLI work-finish fixture and consumer-observable STATUS drift/terminal-receipt validation. Fault injection may interrupt real report publication to exercise retry. Preserve the failing-before/passing-after regression. Fixture reviewer labels are test data only, never approvals of real work.

## Status note (2026-10-15)

Implementation, evidence, round-2 approved two-axis review, regenerated Skill Pair
and STATUS, and green validate are complete. Checked `work finish` is intentionally
not run to completion here: this worktree carries the separately governed uncommitted
kosmic-project migration set, and every unrelated dirty path fails the scope gate;
claiming them would be a blanket scope. The record therefore stays `approved` with
completion receipt-pending until the tree's unrelated work is committed/integrated
by its owning records and finish is rerun in a clean writer.
