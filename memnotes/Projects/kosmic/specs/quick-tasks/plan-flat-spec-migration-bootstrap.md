---
project_id: "kosmic"
subproject_id: null
status: "draft"
record_kind: "quick-task"
local_id: "plan-flat-spec-migration-bootstrap"
created: "2026-10-11"
updated: "2026-10-11"
related_notes: []
related_specs: []
related_files: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "54b9030de20ed7deab0247f8c224c0b62dff7a63"
review_round: 0
acceptance_evidence: []
review_record: ""
---

# Plan Flat Spec Migration Bootstrap

## Request

Break the flat-spec prerequisite loop by establishing an explicit, reviewable migration plan before attempting any feature-spec migration.

## Scope

- Inventory the Kosmic Project's flat feature records and their links; propose a lossless, owner-aware migration map for separate approval.
- Record source identities, target owners and paths, reference rewrites, collision checks, rollback and verification steps.
- Prepare a plan for review; keep the migration execution under its own approval gate.

## Out of Scope

- Moving feature specs or rewriting their identities, approving this record, changing installed skills, or starting unrelated implementation.

## Acceptance Criteria

- [ ] Every existing flat feature record has an explicit target identity or a documented, reviewable exception.
- [ ] The plan checks links, identity collisions and rollback without changing feature records.
- [ ] The proposed migration is presented for separate approval; no migration runs from draft authority.

## Routine Decision

No reusable procedure mechanics are introduced or materially changed.

## Implementation Notes

The shared Quick Task exists as a draft even while `SpecCatalog` refuses flat feature specs. Approval of this planning task must be explicit before `work start`; plan approval must precede migration execution.

## Verification

- CLI `spec-create` returned a draft shared Quick Task at the canonical path; feature catalog remains migration-blocked.

## Review

- [ ] Scope and approval boundary reviewed.
- [ ] Acceptance criteria satisfied.
