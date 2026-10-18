---
status: "done"
created: "2026-09-07"
updated: "2026-09-07"
linked_epic: "../epics/epic-003-routine-publication-dogfood.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
proposal_required: false
review_base: "c52ab6a15b2dab0df9cbd450a76fcdc386612cdb"
review_round: 1
consumer_interface_change: true
related_notes: ["cli-projection-commands.md"]
evidence_packs: ["2026-09-07-procedure-compilation"]
routine_edge_change: false
routine_decision_required: true
routine_proposals: ["../skill-proposals/2026-09-07-atomic-publish-tree-reuse.md"]
project_id: "kosmic"
subproject_id: "feature-prd-procedure-compilation-and-routine-reuse"
record_kind: "story"
local_id: "005"
---

# Story 041: Atomic Publication Compilation

## Story

As a Maintainer, I want repeated directory publication compiled into one deep routine so that rollback behavior has one tested owner.

## Acceptance Criteria

- [x] Implement AD-PC10's architecture-selected first compiled routine, then approve the Task P `reuse` decision required when the changed procedure declares its invocation, with baseline-versus-candidate behavioral evidence.
- [x] Implement `publish_tree(staged, destination, managed_paths=None)` with containment checks, staging, backup, rollback, cleanup, and failure injection.
- [x] Register the routine with literal metadata, explicit callers/tests, deterministic/offline properties, and bounded side effects.
- [x] Migrate `generate`, `migrate_notes_bundle`, MathDocs synchronization, and `generate_library`; delete `publish_directory` and `_replace_generated`.
- [x] Behavioral tests cover absent/existing destinations, whole/managed modes, nested paths, every mutation-boundary failure, restoration, and cleanup.

## Routine Decision

Repeated atomic publication is the architecture-selected first compiled routine. The accepted Task P proposal governs the changed procedure's subsequent reuse decision, as required by the PRD's new-invocation rule.

## Tasks

- [x] Implement the AD-PC10 first routine and approve the changed procedure's reuse proposal.
- [x] Write failure-injection tests before implementation.
- [x] Implement and migrate all four callers cleanly.
- [x] Run focused and full regression suites.
- [x] Complete Standards and Spec review.

## Definition of Done

- [x] All acceptance criteria and the governed reuse proposal pass.
- [x] Obsolete publication implementations are absent.
- [x] No Blocking, High, or Medium review finding remains.
