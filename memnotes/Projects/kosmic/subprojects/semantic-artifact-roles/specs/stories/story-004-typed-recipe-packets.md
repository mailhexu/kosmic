---
status: "done"
created: "2026-09-07"
updated: "2026-09-07"
linked_epic: "../epics/epic-002-role-aware-resolution.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["shared-domain-skill-library.md"]
evidence_packs: ["2026-09-07-semantic-artifact-roles"]
consumer_interface_change: true
proposal_required: false
review_base: ""
review_round: 2
project_id: "kosmic"
subproject_id: "semantic-artifact-roles"
record_kind: "story"
local_id: "004"
---

# Story 034: Typed Recipe Packets

## User Story

As an agent executing a resolved task, I want each loaded topic's authority and inclusion reason made explicit, so that I can execute procedures while treating supporting material correctly.

## Acceptance Criteria

- [x] Closure deduplicates topics and records role, relation, and every deterministic `included_by` reason.
- [x] Procedures load prerequisite-first, followed by the primary procedure, guidelines, knowledge, and eligible evidence as defined by AD-SR7.
- [x] Evidence is absent from ordinary `do` packets unless explicitly requested.
- [x] Domain/topic caps and framing-inclusive byte budgets reject complete packets without truncation.
- [x] Loader rechecks plan, manifest, source hash, role, relation, and exact byte totals before emitting labeled chunks.
- [x] Cross-domain typed closure remains dependency-first and loads each Domain Skill once.

## Tasks

- [x] Write red closure, ordering, evidence exclusion, budget, stale-plan, and cross-domain tests.
- [x] Replace flat dependency ordering with typed relationship closure.
- [x] Update plan serialization and verified packet framing.
- [x] Run focused and full regression suites.
- [x] Run mandatory Standards and Spec review.

## Definition of Done

- [x] Plans and packets are deterministic for fixed inputs.
- [x] Every emitted topic exposes its operational role and inclusion reason.
- [x] Code review converges with no blocking findings.
