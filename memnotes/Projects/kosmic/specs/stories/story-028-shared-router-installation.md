---
status: done
created: 2026-09-06
updated: 2026-09-06
linked_epic: ../epics/epic-15-shared-library-governance.md
linked_architecture: ../architecture-shared-domain-skill-library.md
linked_prd: ../prd-shared-domain-skill-library.md
related_notes: [shared-domain-skill-library.md]
evidence_packs: [2026-09-06-shared-domain-skill-library]
consumer_interface_change: true
proposal_required: false
review_base: 0daf64e5711c14407b551f199832d8b16a2a1db1
review_round: 2
---

# Story 028: Shared Router Installation

## User Story

As an agent host operator,
I want one small Shared Skill Router installed through each adapter,
So that native discovery stays constant while domain content loads dynamically.

## Acceptance Criteria
- [x] The generated router package contains bounded identity, trigger, resolver usage, vault location, budgets, and failure instructions but no domain catalog or Recipe body.
- [x] OpenCode, Claude Code, and Codex named adapters atomically install and byte/identity-verify exactly one router package.
- [x] Only after verification, installation removes all managed Project Usage/Development pairs; unmanaged collisions fail without deletion.
- [x] Rollback restores the prior complete inventory on copy, replace, removal, or verification failure.
- [x] Install/check output distinguishes on-disk verification from runtime activation and names the required reload/inventory observation.

## Tasks
- [x] Write failing package-boundary, adapter, collision, rollback, cleanup, and diagnostic tests.
- [x] Implement canonical router generation and named-adapter install/check cutover.
- [x] Update installation documentation.
- [x] Run focused tests, full regression, and Task 7 review.
