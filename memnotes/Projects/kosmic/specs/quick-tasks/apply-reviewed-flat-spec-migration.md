---
project_id: "kosmic"
subproject_id: null
status: done
record_kind: "quick-task"
local_id: "apply-reviewed-flat-spec-migration"
created: "2026-10-11"
updated: "2026-10-11"
related_notes: ["notes/cli-projection-commands.md"]
related_specs: []
related_files: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "cc697aed137aee374e0a5eabf6fcb8cac6679c15"
review_round: 1
acceptance_evidence: ["evidence/2026-10-11-live-flat-spec-migration/acceptance.json"]
review_record: "evidence/2026-10-11-live-flat-spec-migration/review.json"
---

# Apply reviewed flat-spec migration

## Request

Apply the Kosmic Project's separately reviewed deterministic flat-spec migration plan through the supported CLI, without changing installed skills or manufacturing lifecycle approvals.

## Allowed Scope

- Project: `memnotes/Projects/kosmic`, immutable Project ID `kosmic`.
- Apply only the recomputed, explicitly approved plan's exact `outputs` and `deletions`, plus the executor's managed scratch, transaction journal, before images and migration receipt.
- Preserve protected evidence, logs, generated skills and proposal input manifests/snapshots byte-for-byte; retain existing record statuses and completion decisions.
- Verify the final owner-aware catalog, mapped live links and checked receipt. Reapplying the identical completed plan must return its existing receipt.
- Recover interruption only through the supported recover command using the same approved plan and exact digest; conflicting external changes are not overwrite authority.

## Out of Scope

- Source implementation, adapter installation, generated-skill publication, unrelated file cleanup, Git history rewriting, manual status promotion and completion of other work items.
- Applying a stale plan after approval or documentation changes. This draft is not execution authority.

## Approval Sequence

1. User approves this bounded shared Quick Task.
2. Regenerate and save the final plan after recording that approval: the task itself is a hash-pinned input, so changing its status invalidates an earlier review snapshot.
3. User approves the regenerated plan's exact digest and live migration.
4. Invoke the supported apply command with this explicit work record; reject input drift instead of substituting a different plan.

## Acceptance Criteria

- [ ] The final saved plan has no ownership/path ambiguity and no authoritative unresolved-link diagnostic; protected diagnostics remain report-only.
- [ ] Actual application succeeds with the exact reviewed digest and currently approved or in-progress shared task.
- [ ] Every moved source maps to its planned final identity; the final catalog and recorded live targets validate.
- [ ] Protected inputs remain byte-identical, and no installed skill or unrelated path changes.
- [ ] The migration receipt records original source hashes; repeating the completed plan verifies outputs and returns the same receipt.
- [ ] No unrelated lifecycle approval or completion receipt is fabricated. Complete this task only through the checked workflow after actual acceptance evidence and review.

## Routine Decision

No reusable procedure mechanics or routine edges were introduced or changed by this task: it invokes the existing approved-plan CLI. Planner source corrections are governed separately by Story 001; this execution task neither publishes a shared routine nor authorizes implementation changes.

## Completion Review Scope

Review the executed migration data and evidence, not the separately governed planner source implementation. The fixed review baseline was reconstructed after execution from all 258 transaction before-images, authenticating every original byte against its recorded SHA-256; unrelated current files were held constant. This is a retrospective data baseline, not a claim of a Git checkpoint made before execution. The existing capped source-code review ledger remains unchanged and is not re-approved through this task.

## Current State

The user-approved corrected digest `b1a87b1dd0c4626b2946b99cc2f757161ba001c7f2794ff4a2ad63991140575f` was applied successfully. All 146 outputs, 112 source deletions, final identities/statuses, mapped targets and original-source receipt hashes were verified; all 99 protected Markdown inputs were byte-identical during publication. Repeating the exact command before documentation updates returned an identical receipt. Six criterion-specific acceptance results and both actual independent execution-data review approvals are recorded; the formal checked-completion gate passed. The task's terminal state and receipt are published solely by supported `work finish`, not raw status editing. This execution-data approval does not approve the separately capped planner source-code ledger or complete its Stories.
