---
status: done
created: 2026-09-06
updated: 2026-09-06
linked_epic: ../epics/epic-16-shared-library-migration-release.md
linked_architecture: ../architecture-shared-domain-skill-library.md
linked_prd: ../prd-shared-domain-skill-library.md
related_notes: [shared-domain-skill-library.md]
evidence_packs: [2026-09-06-shared-domain-skill-library]
consumer_interface_change: true
proposal_required: false
review_base: 0daf64e5711c14407b551f199832d8b16a2a1db1
review_round: 2
---

# Story 029: Shared Library Migration

## User Story

As a Kosmic Maintainer,
I want an explicit staged migration from Project Skill Pairs to domain-owned topics,
So that clean cutover loses neither behavior nor provenance.

## Acceptance Criteria
- [x] Migration inventories every stable projected topic and requires an explicit target domain/topic ID for each; slug inference alone never publishes.
- [x] Candidate topics preserve audience, source hash, Evidence Pack references, and source Project identity.
- [x] Collisions, unassigned topics, stale sources, invalid domain ownership, or behavioral differences abort before canonical publication.
- [x] Valid candidates and generated indexes replace the Shared Library atomically; source Project knowledge remains intact.
- [x] The migration report maps every old package/reference to its new topic ID and records comparison evidence.

## Tasks
- [x] Write failing inventory, assignment, preservation, collision, stale-source, and rollback tests.
- [x] Implement migration plan, validation, staging, report, and publication commands.
- [x] Create explicit Kosmic migration assignments.
- [x] Run focused tests, full regression, and Task 7 review.
