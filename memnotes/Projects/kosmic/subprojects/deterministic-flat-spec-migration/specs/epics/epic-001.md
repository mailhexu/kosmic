---
project_id: "kosmic"
subproject_id: "deterministic-flat-spec-migration"
record_kind: "epic"
local_id: "001"
status: "approved"
created: "2026-10-11"
updated: "2026-10-11"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-001.md", "../stories/story-002.md", "../stories/story-003.md"]
---

# Epic 001: Script-driven flat-spec migration

## Description

Provide an offline plan → review/approve → apply → verify workflow that migrates one explicitly selected Project without agent-driven file edits. Reuse the existing planner and catalog, preserve work authority and immutable history, and provide safe recovery of interrupted publication.

## Scope

### In Scope

- Complete, reproducible saved plans with source, target and live-link inventories.
- Project-scoped apply and recover commands with explicit authority and approved digest.
- Staged catalog and link validation, checked per-path publication, durable before images and receipt-based idempotence.
- Bound STATUS generation, proposal fingerprint disposition, actual CLI proof, deterministic regression tests and consumer documentation.

### Out of Scope

- Migrating a live Project without its separately approved plan and current shared Quick Task.
- Approving tasks or creating acceptance, review or completion authority from historical status.
- Shared Skill Library migration, adapter installation or automatic vault-wide migration.

## Approved Story Breakdown

The user approved this epic breakdown on 2026-10-11. The linked Story records remain draft until their separate implementation approval.

| Order | Proposed slice | Dependencies | Observable acceptance |
|---|---|---|---|
| 1 | [Complete and save deterministic migration plans](../stories/story-001.md) | None | Saved plans cover complete inputs, outputs, ownership, live links and deterministic rewrites without mutating source records. |
| 2 | [Apply approved plans and recover interruption](../stories/story-002.md) | Story 001 | Pinned-plan application, authority checks, staged validation, checked publication, safe recovery and idempotent receipts work through actual CLI commands. |
| 3 | [Integrate and verify the migration workflow](../stories/story-003.md) | Story 002 | Multi-feature CLI migration, STATUS and proposal handling, historical authority preservation, documentation and complete regression/review coverage satisfy FR-M01 through FR-M09. |

## Success Criteria

- [ ] All approved PRD requirements FR-M01 through FR-M09 are satisfied by the complete CLI workflow.
- [ ] A representative temporary Project migrates and validates through actual commands, without agent calls or manual record rewrites.
- [ ] Ambiguity, missing approval, lost work authority, source drift, plan tampering, destination collisions and unsafe paths fail before authoritative mutation.
- [ ] Failure and interruption checks demonstrate recoverable state and protect unrelated edits.
- [ ] Repeated completed application is verified and does not change content.
- [ ] Historical evidence, logs and existing decisions are preserved; migration receipts do not masquerade as completion receipts.
- [ ] Consumer documentation, regression tests and independent Standards/Spec review cover the complete change.

## Requirement Coverage

- Slice 1: FR-M01, FR-M03, the planning portions of FR-M04 through FR-M06 and FR-M09.
- Slice 2: FR-M02, FR-M04, FR-M05, FR-M07, FR-M08 and authority preservation from FR-M06/FR-M09.
- Slice 3: End-to-end FR-M01 through FR-M09, STATUS/proposal integration and documented execution.

## Implementation Discipline

Use TDD for consumer-visible failure boundaries and deterministic state transitions. Start each approved Story in a clean dedicated worktree; preserve the current pre-existing work. Pin its review baseline and record actual acceptance evidence. The final review must cover the whole executor and its planner/CLI callsites, not only the last integration slice.

## Progress

- Implementation: all three Stories implemented and independently reviewed; 15 test modules passed with zero failures.
- Last updated: 2026-10-11.
- Gate: canonical checked terminal closure and any live migration remain separate. Story approval does not approve a live Project's migration plan.
