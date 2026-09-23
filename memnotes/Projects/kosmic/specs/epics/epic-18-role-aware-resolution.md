---
status: approved
created: 2026-09-07
updated: 2026-09-07
linked_prd: ../prd-semantic-artifact-roles.md
linked_architecture: ../architecture-semantic-artifact-roles.md
linked_stories: [../stories/story-033-intent-and-primary-selection.md, ../stories/story-034-typed-recipe-packets.md]
---

# Epic 18: Role-Aware Resolution

## Description

Make the existing Resolver Module distinguish action from reference requests, select a role-compatible primary topic, and emit a bounded packet whose contents and authority are explicit.

## Scope

### In Scope
- Deterministic intent inference with explicit override
- Role-filtered scoring and reference-only results
- Typed relationship closure, ordering, trace, hashes, and byte accounting
- Resolver and loader CLI contracts

### Out of Scope
- Model-based classification
- Paragraph truncation or unbounded evidence loading

## Stories

| Story | Description | Status |
|---|---|---|
| [Story 033](../stories/story-033-intent-and-primary-selection.md) | Intent inference and role-aware primary selection | draft |
| [Story 034](../stories/story-034-typed-recipe-packets.md) | Typed closure and verified Recipe Packets | draft |

## Success Criteria

- [x] `do` never falls back to knowledge or evidence.
- [x] Reference intents label non-executable results explicitly.
- [x] Packet relations, ordering, byte totals, and hashes are deterministic and verified.
