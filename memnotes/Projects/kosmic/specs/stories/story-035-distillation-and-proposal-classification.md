---
status: done
created: 2026-09-07
updated: 2026-09-07
linked_epic: ../epics/epic-19-classification-migration-release.md
linked_architecture: ../architecture-semantic-artifact-roles.md
linked_prd: ../prd-semantic-artifact-roles.md
related_notes: [shared-domain-skill-library.md]
evidence_packs: [2026-09-07-semantic-artifact-roles]
consumer_interface_change: true
proposal_required: false
review_base: ""
review_round: 2
---

# Story 035: Distillation and Proposal Classification

## User Story

As a Kosmic Maintainer, I want semantic role chosen when experience becomes durable knowledge, so that later proposals preserve authority instead of promoting every stable note into a procedure.

## Acceptance Criteria

- [x] New or materially updated Project notes require a valid `artifact_role`; legacy untouched notes remain valid but are reported unclassified.
- [x] Project procedure notes satisfy the shared behavioral section contract before projection or proposal use.
- [x] Task 9 explicitly classifies outputs and requires Task P consideration only for new or materially changed procedures.
- [x] Task P procedure eligibility requires trigger, bounded outcome, decisions, verification, failure handling, and successful behavioral evidence.
- [x] Proposal manifests and fingerprints include artifact role; non-procedure outcomes retain knowledge/no-action paths.
- [x] Note, proposal, Task 9, Task P, glossary, and authoring documentation use the same vocabulary.

## Tasks

- [x] Write red note-validation, projection, proposal, fingerprint, and completion-gate tests.
- [x] Implement classification in the Project Projection Module and proposal model.
- [x] Update workflow references, templates, glossary, and user documentation.
- [x] Run focused and full regression suites.
- [x] Run mandatory Standards and Spec review.

## Definition of Done

- [x] Classification survives Evidence Pack to note to proposal to Domain Topic.
- [x] Legacy compatibility is bounded and cannot seed an unclassified shared proposal.
- [x] Code review converges with no blocking findings.
