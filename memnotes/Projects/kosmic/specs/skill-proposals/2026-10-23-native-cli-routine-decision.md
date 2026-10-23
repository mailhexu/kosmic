---
project_id: "kosmic"
subproject_id: null
record_kind: "proposal"
local_id: "2026-10-23-native-cli-routine-decision"
status: "done"
created: "2026-10-23"
updated: "2026-10-23"
result: "no_action"
scope: "shared-routine"
artifact_role: "knowledge"
target_kind: "routine"
routine_action: "none"
routine_id: ""
linked_proposals: []
consumer_approvals: []
target: ""
target_ref: ""
target_sha256: ""
proposer_mode: "subagent"
proposer_ref: "agent://NativeCliRoutineProposer"
proposer_reason: "Fresh-context independent proposer for shared-routine scope: received only the hash-pinned knowledge inputs, the pinned routine coordinate, and the Task P procedure; verified all three manifest SHA pins against the generated inventory before deciding."
input_manifest: ["specs/skill-proposals/inputs/2026-10-23-native-cli-routine-decision.md"]
related_notes: []
behavioral_evidence: []
decision: "accepted"
approved_by: "user (Approve no-action)"
fingerprint: "c570299cd891170483b9fab3049576b17b10c0a37c77b078ee6a04759d9f06b4"
reconsiders: ""
---

# Routine decision: retain native CLI draft-creation and completion mechanics as Project knowledge

## Problem

The approved native CLI work — operation-backed indexed draft creation for all five record kinds, operation resume with context preservation, and read-only completion preparation bound to reviewed source — materially changes how Project records are created and completed and therefore requires an explicit shared-routine decision. That requirement does not authorize publication of a shared routine or a skill.

## Evidence

The curated manifest (`specs/skill-proposals/inputs/2026-10-23-native-cli-routine-decision.md`) pins exactly three decision sources, all verified by SHA-256: `notes/index.md` (`2fe40171…`), the stable source note `notes/cli-projection-commands.md` (`e92429b7…`), and the generated routine coordinate `routine://kosmic/atomic-publish-tree` (`725d4a99…`, matching the generated inventory's `routine_sha256`).

The source note `notes/cli-projection-commands.md` carries `artifact_role: knowledge`: it states the durable invariants of the native CLI (operation-backed stepwise creation publication, resume semantics that preserve unrelated index content and refuse conflicting draft bytes, read-only `prepare-completion`, and finish behavior that rejects stale source) but is not a `procedure` note with typed triggers, inputs, and outputs. The parent's actual CLI exercises — five kinds creating native indexed drafts with explicit paths and operation IDs, resume preserving unrelated context and refusing conflicting bytes, and preparation being read-only with stale-source finish refused and matching reviewed bytes succeeding — are observations recorded in the governing record, not behavioral evidence establishing a reusable procedure, and they are not claims that the feature Stories are completed (all three retain `routine_decision_required: true`).

## Applicability

The mechanics are a single Project-owned native CLI command family; the pinned knowledge note is its consumer documentation. Native draft creation, operation resume/recovery, and prepare hashing are owned by the existing Project CLI modules, not by any separately governed cross-domain procedure. The governing scope contains no `uses_routines` edge and no proposed shared-routine extraction, and the generated inventory exposes only one routine.

## No-Action Reason

None of the curated sources establishes executable-reuse eligibility: the only source note is `artifact_role: knowledge`, and Task P admits only `procedure` notes for reusable mechanics, so no routine candidate (`create`/`extend`/`reuse`) can be formed. The inventory's sole routine, `kosmic/atomic-publish-tree` (pinned `725d4a99…`), publishes a staged tree atomically with whole-tree rollback; its contract cannot express per-record indexed draft creation, operation-backed resume that merges a single row, or prepare/finish hashing, so treating it as the reused routine would be false reuse, and extracting a new shared routine would duplicate the supported CLI interface without demonstrated cross-domain leverage. The mechanics remain owned by the existing Project CLI modules, documented through the stable knowledge note and its CLI command reference; no speculative shared routine, duplicate framework, or imported internal recipe is proposed. `no_action` with `routine_action: none` is the only honest disposition from the pinned evidence.

## Behavioral Validation

No skill or routine candidate is proposed or published, so no candidate path exists. The cited command behaviors are parent observations from the actual CLI exercises; acceptance of the feature Stories remains pending in the governing record, and the completion gate is unchanged.

## Risks

Premature shared extraction would duplicate the supported CLI command interface and impose unapproved ownership and consumer obligations on a deterministic area that is already tested and discoverable through the CLI reference. Recording `no_action` keeps the disposition referenceable from all three Stories without altering the completion gate or the existing routine inventory.
