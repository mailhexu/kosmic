---
status: done
created: 2026-09-07
updated: 2026-09-07
linked_epic: ../epics/epic-17-semantic-role-schema.md
linked_architecture: ../architecture-semantic-artifact-roles.md
linked_prd: ../prd-semantic-artifact-roles.md
related_notes: [shared-domain-skill-library.md]
evidence_packs: [2026-09-07-semantic-artifact-roles]
consumer_interface_change: true
proposal_required: false
review_base: ""
review_round: 2
---

# Story 032: Procedure and Typed-Relationship Validation

## User Story

As a Domain Maintainer, I want procedural authority and supporting relationships validated structurally, so that malformed reports or role-incompatible dependencies cannot enter a Recipe Packet.

## Acceptance Criteria

- [x] Stable procedures require triggers, outcome, and all seven non-empty behavioral sections from AD-SR3.
- [x] `requires_procedures`, `governed_by`, `uses_knowledge`, and `supported_by` accept only their exact target roles.
- [x] Unknown targets, self-edges, cycles, audience violations, and obsolete `requires` fail with topic-specific errors.
- [x] Evidence requires `observed_on`; optional `supersedes` targets older evidence and is containment-safe and cycle-free.
- [x] Draft/deprecated topics remain ineligible and cannot satisfy active relationships.

## Tasks

- [x] Write failing procedure-body and relationship matrix tests.
- [x] Write failing evidence date, supersession, and cycle tests.
- [x] Implement validation behind the existing catalog seam.
- [x] Run focused and full regression suites.
- [x] Run mandatory Standards and Spec review.

## Definition of Done

- [x] Every invalid graph emits a typed actionable failure and no generated publication.
- [x] Valid cross-domain and Development-to-Usage relationships remain supported.
- [x] Code review converges with no blocking findings.
