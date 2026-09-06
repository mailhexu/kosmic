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

# Story 030: Shared Library Dogfood and Release

## User Story

As a Kosmic Maintainer,
I want the new library proven on Kosmic and a realistic TB2J-to-ABINIT workflow before release,
So that routing, composition, migration, and installation are observed end to end.

## Acceptance Criteria
- [x] `Skills/kosmic/`, `Skills/abinit/`, and `Skills/tb2j/` provide valid domain fixtures with bounded routers and atomic topics.
- [x] A Kosmic query resolves only relevant Kosmic procedures; a TB2J development query loads declared ABINIT Usage dependencies in dependency-first order and no unrelated topic.
- [x] Old and new representative tasks have recorded equivalent outcomes, while an ambiguous and an over-budget task fail closed without bodies.
- [x] Canonical generation, validation, proposal governance, migration report, adapter install/check, and all Story completion gates pass at one fixed review base.
- [x] User documentation, Context glossary, Project index/log, Evidence Pack, Impact Ledger, and generated router package describe the released interface.

## Tasks
- [x] Build realistic domain/topic fixtures and behavioral scenarios.
- [x] Run migration, generate the catalog/router, resolve/load packets, and install every named adapter.
- [x] Complete independent Standards and Spec reviews and fix all blocking findings.
- [x] Publish evidence, ledger decisions, docs, and release metadata.
