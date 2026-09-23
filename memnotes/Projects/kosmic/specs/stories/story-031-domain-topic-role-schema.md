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

# Story 031: Domain Topic and Artifact-Role Schema

## User Story

As a Domain Maintainer, I want each maintained topic to declare what authority it has, so that agents and reviewers do not mistake reference material for executable guidance.

## Acceptance Criteria

- [x] `Domain Topic` replaces `Skill Topic` in authoritative metadata, generated artifacts, schemas, templates, and errors with no permanent alias.
- [x] Every active Domain Topic declares exactly one `artifact_role`: procedure, guideline, knowledge, or evidence.
- [x] Audience remains independent and retains Usage-to-Development restrictions.
- [x] Catalog and plan rows preserve artifact role deterministically.
- [x] Schema and generator versions reject stale pre-cutover catalogs and plans with actionable regeneration errors.

## Tasks

- [x] Inspect current parser, catalog, fixture, template, and documentation call sites.
- [x] Write focused failing schema, terminology, and version-cutover tests.
- [x] Implement the clean schema cutover and regenerate fixtures.
- [x] Run focused and full regression suites.
- [x] Run mandatory Standards and Spec review.

## Definition of Done

- [x] Acceptance criteria pass through public CLI behavior.
- [x] No obsolete canonical `Skill Topic` path remains.
- [x] Documentation and generated examples match the new schema.
- [x] Code review converges with no blocking findings.
