---
status: approved
created: 2026-09-07
updated: 2026-09-07
linked_prd: ../prd-procedure-compilation.md
linked_architecture: ../architecture-procedure-compilation.md
linked_stories: [../stories/story-037-routine-registry-schema.md, ../stories/story-038-routine-inventory-query.md]
---

# Epic 20: Routine Registry and Discovery

## Description

Expose reusable deterministic Python mechanics through one static, validated, hash-pinned inventory and bounded query interface.

## Scope

### In Scope
- Literal routine declarations and fail-closed static validation
- Deterministic inventory generation and manifest pinning
- Exact and bounded text query selectors

### Out of Scope
- Task P routine decisions and work-item gates (Epic 21)
- Compiling or migrating publication mechanics (Epic 22)

## Stories

| Story | Description | Status |
|---|---|---|
| [Story 037](../stories/story-037-routine-registry-schema.md) | Static routine schema and validation | done |
| [Story 038](../stories/story-038-routine-inventory-query.md) | Inventory generation and bounded query | done |

## Success Criteria

- [x] Unsafe or stale declarations fail without importing source modules.
- [x] Generation publishes one deterministic, manifest-pinned inventory.
- [x] Agents can search every FR-PC17 dimension with deterministic output.
