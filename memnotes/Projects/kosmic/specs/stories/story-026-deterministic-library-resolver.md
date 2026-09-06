---
status: done
created: 2026-09-06
updated: 2026-09-06
linked_epic: ../epics/epic-14-shared-library-foundation.md
linked_architecture: ../architecture-shared-domain-skill-library.md
linked_prd: ../prd-shared-domain-skill-library.md
related_notes: [shared-domain-skill-library.md]
evidence_packs: [2026-09-06-shared-domain-skill-library]
consumer_interface_change: true
proposal_required: false
review_base: 0daf64e5711c14407b551f199832d8b16a2a1db1
review_round: 2
---

# Story 026: Deterministic Library Resolver

## User Story

As an agent performing a technical task,
I want a bounded, hash-pinned Recipe Packet selected by route or query,
So that I load only relevant and complete cross-domain procedures.

## Acceptance Criteria
- [x] `resolve-library` accepts exactly one query/route, role, Project hint, and hard byte/domain/topic caps and emits canonical JSON.
- [x] Explicit routes are exact; query routing applies documented normalization, integer scores, eligibility filters, Project boost, stable trace, and fail-closed ambiguity.
- [x] Required topics load once in dependency-first order with owning Domain Skills; Usage cannot acquire Development dependencies.
- [x] Exact-fit budgets pass; one-byte/body/domain/topic overflow fails without Recipe bodies; no topic is truncated.
- [x] `load-library` verifies plan self-hash, manifest hash, every source hash, and byte cost before emitting only the ordered packet.
- [x] Equivalent progressive/query fixtures produce equivalent topic closure and repeated runs are byte-identical.

## Tasks
- [x] Write failing route, search, ambiguity, dependency, budget, stale-plan, and determinism tests.
- [x] Implement the resolver, plan serializer, and loader behind one module seam.
- [x] Add CLI contracts and root/domain router instructions.
- [x] Run focused tests, full regression, and Task 7 review.
