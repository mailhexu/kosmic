---
status: done
created: 2026-09-07
updated: 2026-09-07
linked_prd: ../prd-semantic-artifact-roles.md
linked_architecture: ../architecture-semantic-artifact-roles.md
linked_stories: [../stories/story-031-domain-topic-role-schema.md, ../stories/story-032-procedure-and-relationship-validation.md]
---

# Epic 17: Semantic Role Schema

## Description

Replace universal Skill Topic semantics with role-neutral Domain Topics and explicit operational authority. Validate procedure structure, typed relationships, and optional evidence supersession while preserving audience as an independent dimension.

## Scope

### In Scope
- `Domain Topic` and `artifact_role` schema cutover
- Strict procedure body contract
- Typed relationship and evidence freshness graph validation
- Catalog, manifest, generated index, error, and terminology updates

### Out of Scope
- Intent-aware selection and packet ordering (Epic 18)
- Vault migration and ABINIT classification (Epic 19)

## Stories

| Story | Description | Status |
|---|---|---|
| [Story 031](../stories/story-031-domain-topic-role-schema.md) | Domain Topic and artifact-role schema | draft |
| [Story 032](../stories/story-032-procedure-and-relationship-validation.md) | Procedure, relationship, and evidence validation | draft |

## Success Criteria

- [x] Every active shared topic has one validated artifact role independent of audience.
- [x] Canonical and generated terminology contains no `Skill Topic` compatibility alias.
- [x] Invalid procedure structure, role edges, or supersession graphs fail closed.
