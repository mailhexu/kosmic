---
status: "done"
created: "2026-09-07"
updated: "2026-09-07"
linked_epic: "../epics/epic-003-classification-migration-release.md"
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
local_id: "006"
---

# Story 036: ABINIT Migration, Dogfood, and Release

## User Story

As an ABINIT Maintainer, I want every existing topic explicitly classified and representative tasks proven end to end, so that the role-aware library can replace the ambiguous catalog without losing knowledge or provenance.

## Acceptance Criteria

- [x] Migration assignments cover every current ABINIT topic with target ID, artifact role, and explicit typed relationships; no role is inferred.
- [x] The approved clear procedures and guidelines are classified accordingly; mixed documents remain knowledge unless separately distilled.
- [x] Reports, statuses, audits, and validation snapshots become dated evidence only where observation metadata is defensible; otherwise they remain knowledge pending curation.
- [x] Source hashes, audience, source Project, evidence paths, ownership, and proposal history remain traceable.
- [x] ABINIT `do`, `check`, `understand`, and `investigate` dogfood requests demonstrate correct authority, closure, exclusions, and smaller-or-equal actionable packets.
- [x] Kosmic and TB2J topics migrate after the ABINIT contract passes; generation and publication remain atomic.
- [x] Shared/project validation, full tests, completion gates, independent two-axis review, docs, evidence, ledger, and release metadata pass.
- [x] The one root router installs and byte-verifies on OpenCode, Claude Code, Codex, and OMP; runtime discovery remains honestly separate.

## Tasks

- [x] Build and review a complete ABINIT classification inventory and migration assignment.
- [x] Write failing migration, provenance, rollback, and real-query behavior tests.
- [x] Stage and validate ABINIT, Kosmic, and TB2J migrations before one publication swap.
- [x] Generate, validate, install, and exercise representative role-aware packets.
- [x] Publish Evidence Pack, stable knowledge update, ledger entries, and release documentation.
- [x] Run mandatory independent Standards and Spec review and fix blocking findings.

## Definition of Done

- [x] No current shared topic remains unassigned or uses the old schema.
- [x] All required behavioral checks and adapter byte checks pass.
- [x] All blocking review findings are resolved and release state is reproducible.
