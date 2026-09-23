---
status: done
created: 2026-09-07
updated: 2026-09-07
result: no_action
scope: shared-routine
artifact_role: procedure
target_kind: routine
routine_action: reuse
routine_id: kosmic/atomic-publish-tree
linked_proposals: []
consumer_approvals: []
target: kosmic/atomic-publish-tree
target_ref: routine://kosmic/atomic-publish-tree
target_sha256: aeaad9c360fe1a0a046196208d3bb5d17919cf6d418d4da0ce79e9d3016057fc
proposer_mode: subagent
proposer_ref: agent://ProcedureRoutineProposer
proposer_reason: "Fresh-context Task P assessment restricted to the hash-pinned curated manifest"
input_manifest: [specs/skill-proposals/inputs/procedure-compilation-routine.md]
related_notes: [notes/procedure-compilation-and-routine-reuse.md]
evidence_packs: [2026-09-07-procedure-compilation]
behavioral_evidence: [evidence/2026-09-07-procedure-compilation/behavioral-validation.md]
decision: accepted
fingerprint: cb708be1202c46ea0408eb35ec36853c46b16fd0028227ea76d004b970008c76
reconsiders: ""
---

# Skill Proposal: Reuse Atomic Publish Tree Routine

## Problem

Project and Shared Library procedure publication previously repeated transaction mechanics. The approved implementation now exposes one canonical routine, so governance must decide whether consuming procedures reuse it or retain duplicated mechanics.

## Evidence

The execution pack records four migrated callers and six passing observable scenarios: rollback restoration, static fail-closed discovery, unknown-edge rejection, reciprocal-edge rejection, exact-ID query, and routine-bearing procedure packets.

## Applicability

Use `kosmic/atomic-publish-tree` whenever Kosmic publishes a complete staged directory or a declared managed-path subset into a canonical destination. Interpretation, content approval, and semantic validation remain outside the routine.

## Behavioral Validation

Baseline consumers owned separate publication implementations. Candidate consumers call `publish_tree(staged, destination, managed_paths=None)` and the full regression suite passes. Injected failures after backup restore the prior complete destination.

## Risks

Cross-filesystem rename behavior is not separately exercised. The current callers stage under the destination parent, preserving same-filesystem atomic replacement; future callers must preserve that invariant.

## No-Action Reason

No new routine code is required. The exact canonical routine already exists, all four consumers use it, and the former duplicate helpers were removed. Task P's reuse-before-extension-before-creation order therefore resolves to governed `reuse`.
