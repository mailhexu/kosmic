---
status: done
created: 2026-09-07
updated: 2026-09-07
linked_epic: ../epics/epic-22-routine-publication-dogfood.md
linked_architecture: ../architecture-procedure-compilation.md
linked_prd: ../prd-procedure-compilation.md
proposal_required: false
review_base: c52ab6a15b2dab0df9cbd450a76fcdc386612cdb
review_round: 1
consumer_interface_change: true
related_notes: [cli-projection-commands.md]
evidence_packs: [2026-09-07-procedure-compilation]
routine_edge_change: true
routine_decision_required: true
routine_proposals: [../skill-proposals/2026-09-07-atomic-publish-tree-reuse.md]
---

# Story 042: Procedure Compilation Dogfood and Release

## Story

As a Kosmic user, I want procedure packets to carry verified routine coordinates and the feature released atomically so that reusable mechanics remain discoverable and trustworthy.

## Acceptance Criteria

- [x] Add procedure-only `uses_routines` validation, reciprocal inventory edges, and sorted, deduplicated catalog topic routine rows.
- [x] Extend plans and Recipe Packets with inventory hash, routine records, exact byte framing, load-time hash checks, and budget-overflow rejection of the complete packet without truncation.
- [x] Dogfood a reviewed mixed procedure against `kosmic/atomic-publish-tree` while retaining judgment and approval branches; prove query, proposal, baseline-versus-candidate success, injected-failure rollback, generation, validation, loading, and completion end to end.
- [x] Emit the AD-PC11 migration report listing declared routines, procedure edges, Task 9 legacy candidates, and only explicitly supplied unregistered helpers; update SKILL/task references, templates, README/glossary, specs/log, evidence pack, Impact Ledger, and release notes.
- [x] Run full focused suites, generated-library/project validation, four-adapter byte-verification install checks, completion gates, and independent Standards/Spec review with no Blocking/High/Medium findings.

## Routine Decision

This story adds the first reciprocal `uses_routines` edge and therefore links the accepted `kosmic/atomic-publish-tree` reuse decision; no second routine candidate is introduced.

## Tasks

- [x] Write focused failing edge, packet, and stale-hash tests.
- [x] Implement procedure/inventory integration.
- [x] Dogfood and regenerate canonical artifacts.
- [x] Run focused and full verification.
- [x] Complete Standards and Spec review.

## Definition of Done

- [x] All acceptance criteria pass end to end.
- [x] Evidence, ledger, docs, generated artifacts, and installs are current.
- [x] No Blocking, High, or Medium review finding remains.
