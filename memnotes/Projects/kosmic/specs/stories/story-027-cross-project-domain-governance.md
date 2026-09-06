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

# Story 027: Cross-Project Domain Governance

## User Story

As an ABINIT Maintainer,
I want TB2J evidence to propose ABINIT recipe changes without transferring ownership,
So that cross-project learning is reusable and reviewable.

## Acceptance Criteria
- [x] Task P supports `library-skill://{domain}/{audience}/{slug}` create/update targets with exact candidate isolation and update hashes.
- [x] Evidence remains in its source Project; declared cross-project pack paths resolve only inside the same vault and are included in proposal fingerprints.
- [x] Approval/acceptance requires `approved_by` to match the target Domain Skill's `maintainers`; the CLI records but does not claim to authenticate that human.
- [x] Accepted changes require behavioral Evidence and independent Task 7 review; rejected equivalent fingerprints require materially new Evidence before reconsideration.
- [x] A proposal cannot mutate Project knowledge and Shared Library content as one artifact.

## Tasks
- [x] Write failing target, containment, ownership, evidence, fingerprint, and rejection-memory tests.
- [x] Extend proposal schemas, validator, templates, completion gate, and Task P guidance.
- [x] Add a TB2J-to-ABINIT governance fixture.
- [x] Run focused tests, full regression, and Task 7 review.
