---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_epic: "../epics/epic-001-shared-library-foundation.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["shared-domain-skill-library.md"]
evidence_packs: ["2026-09-06-shared-domain-skill-library"]
consumer_interface_change: true
proposal_required: false
review_base: "0daf64e5711c14407b551f199832d8b16a2a1db1"
review_round: 2
project_id: "kosmic"
subproject_id: "shared-domain-skill-library"
record_kind: "story"
local_id: "001"
---

# Story 025: Library Schema and Catalog

## User Story

As a library Maintainer,
I want authoritative root/domain/topic documents validated and indexed deterministically,
So that every later resolver and governance decision uses one trustworthy snapshot.

## Acceptance Criteria
- [x] Root Router, Domain Skill, and Skill Topic flat metadata validate with stable unique IDs and vault-contained paths.
- [x] Domain ownership comes only from the domain `SKILL.md`; topics cannot override Maintainers.
- [x] Generation emits canonical `catalog.json`, `manifest.json`, and domain `index.md` files with stable ordering, exact UTF-8 sizes, hashes, and provenance.
- [x] Unknown dependencies, duplicate IDs, self-edges, cycles, Usage-to-Development edges, stale sources, and generated drift fail with actionable errors.
- [x] Generation is staged and atomic and never rewrites authoritative Markdown bodies.

## Tasks
- [x] Write failing schema, graph, determinism, drift, and rollback tests.
- [x] Implement library models, parser, validator, graph checks, and atomic catalog generation.
- [x] Document the authoring and validation contract.
- [x] Run focused tests, full regression, and Task 7 review.
