---
project_id: "kosmic"
subproject_id: null
record_kind: "proposal"
local_id: "2026-10-11-migration-routine-decision"
status: "draft"
created: "2026-10-11"
updated: "2026-10-11"
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
proposer_ref: "agent://MigrationRoutineDecision"
proposer_reason: "Fresh-context independent governance decision for shared-routine scope; verified all four manifest SHA pins; Task P procedure found no eligible separately governed procedural target, so the no-action result is recorded without implementation authority."
input_manifest: ["specs/skill-proposals/inputs/2026-10-11-migration-routine-decision.md"]
related_notes: []
behavioral_evidence: []
decision: "pending"
approved_by: ""
fingerprint: ""
reconsiders: ""
---

# Routine decision: retain migration as its supported command

## Problem

Stories 001/002 materially change deterministic planning and recovery mechanics and require an explicit routine decision. That requirement does not automatically authorize shared routine or skill publication.

## Evidence

The curated manifest pins the approved contracts, observed implementation outcomes and inspected shared routine inventory. The existing atomic tree publisher is not a drop-in implementation of checked deletions and interrupted per-path recovery. The implementation reuses the planner, creation lock, catalog and run lifecycle instead of creating a parallel migration convention.

## Applicability

This work exposes one Project-owned command family. Its consumer knowledge describes that API; no separately governed cross-domain procedure or new uses_routines edge has been established. The knowledge/evidence input does not establish eligibility for publishing a shared procedural target.

## No-Action Reason

Keep the tested migration mechanics behind their supported command interface. None of the curated sources is a `procedure` note: they are approved PRD/Architecture contracts and an observed implementation record, so executable-reuse eligibility is not established. The generated inventory contains only `kosmic/atomic-publish-tree`, whose whole-tree recovery contract cannot express checked per-path deletions or per-path interrupted recovery, so neither `reuse` nor `extend` applies and the deterministic mechanics already live inside the supported Project CLI command family, reusing the planner, creation lock, catalog and run lifecycle; its consumer knowledge is informational and no new uses_routines edge is demonstrated. Do not add a speculative shared routine namespace or publish a new skill solely because one feature contains deterministic code. A demonstrated independent reusable procedure can later obtain its own governed routine decision. This no-action record claims neither accepted human approval nor authority to publish canonical/installed artifacts.

## Behavioral Validation

No skill/routine candidate is proposed or published. Actual command behavior, source hashes, test results and independent review are recorded in the linked implementation contracts and curated session record.

## Risks

Premature shared extraction would duplicate the supported command interface and impose unapproved ownership/consumer obligations. Existing code remains tested and discoverable through its CLI and documentation.
