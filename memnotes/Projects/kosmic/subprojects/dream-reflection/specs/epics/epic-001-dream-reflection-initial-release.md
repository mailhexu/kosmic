---
status: "done"
created: "2026-09-23"
updated: "2026-09-23"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-001-dream-day-delta-harvest.md", "../stories/story-002-dream-open-work-knowledge-contract.md", "../stories/story-003-dream-vault-schema-validator.md", "../stories/story-004-managed-dream-harvest-handshake.md", "../stories/story-005-deterministic-dream-publication.md", "../stories/story-006-dream-run-recovery-concurrency.md", "../stories/story-007-dream-workflow-dogfood-release.md"]
project_id: "kosmic"
subproject_id: "dream-reflection"
record_kind: "epic"
local_id: "001"
---

# Epic 26: Dream Reflection Initial Release

## Description

Deliver the first complete Task D `dream` workflow: deterministic whole-vault
previous-day harvesting, current open-work and knowledge evidence, validated
vault-level records, authenticated managed publication/recovery, and pinned
behavioral dogfood that summarizes work and proposes advisory skills and ideas.

## Scope

### In Scope

- Observable target-day union across authoritative vault surfaces.
- Historical transitions, open work, deterministic flags, candidate evidence,
  and hash-pinned/materialized reflection inputs.
- Dream record/index/ideas schemas and vault-level validation.
- Managed harvest handshake, deterministic publication, and explicit
  retry/abort/concurrency/recovery semantics.
- Task D procedure, usage knowledge, and real-history dogfood evidence.

### Out of Scope

- Scheduled execution, weekly rollups, configurable idea aging.
- Automatic remediation, status changes, Task P proposals, or skill publication.
- Per-project dream records.

## Dependency Order

`057 → 058`; `059` may proceed independently; `057 + 058 + 059 → 060 → 061 → 062 → 063`.
Dependent story completion must fail until every declared prerequisite is done.

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-057](../stories/story-001-dream-day-delta-harvest.md) | Dream Day-Delta Harvest | done |
| [story-058](../stories/story-002-dream-open-work-knowledge-contract.md) | Dream Open Work and Knowledge Contract | done |
| [story-059](../stories/story-003-dream-vault-schema-validator.md) | Dream Vault Schema and Validator | done |
| [story-060](../stories/story-004-managed-dream-harvest-handshake.md) | Managed Dream Harvest Handshake | done |
| [story-061](../stories/story-005-deterministic-dream-publication.md) | Deterministic Dream Publication | done |
| [story-062](../stories/story-006-dream-run-recovery-concurrency.md) | Dream Run Recovery and Concurrency | done |
| [story-063](../stories/story-007-dream-workflow-dogfood-release.md) | Dream Workflow Dogfood Release | done |

## Success Criteria

- [x] All seven stories complete in dependency order
- [x] Real-history dream matches pinned completed/open-work ground truth
- [x] Harvest, validation, publication, rerun, race, failure, and recovery checks pass
- [x] Runtime persistent vault publication changes only `memnotes/dreams/`
- [x] Full suite, completion gates, Skill Pair validation, and adapter checks pass
- [x] Standards, Spec, and security reviews converge with no blockers

## Progress

- Stories: 7/7 done
- Last updated: 2026-09-23
