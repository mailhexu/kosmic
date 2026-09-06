---
status: done
created: 2026-09-06
updated: 2026-09-06
linked_prd: ../prd-shared-domain-skill-library.md
linked_architecture: ../architecture-shared-domain-skill-library.md
linked_stories: [../stories/story-025-library-schema-catalog.md, ../stories/story-026-deterministic-library-resolver.md]
---

# Epic 14: Shared Library Foundation

## Description

Establish the authoritative vault-level Skill Domain model, deterministic generated catalog, and bounded two-step Resolver interface.

## Scope

### In Scope
- Root Router, Domain Skill, and Skill Topic schemas
- Catalog and manifest generation/validation
- Explicit and query routing, dependency closure, budgets, and plan loading

### Out of Scope
- Proposal governance, migration, and adapter cutover

## Stories
- [Story 025: Library Schema and Catalog](../stories/story-025-library-schema-catalog.md)
- [Story 026: Deterministic Library Resolver](../stories/story-026-deterministic-library-resolver.md)

## Acceptance Criteria
- [x] A valid multi-domain `Skills/` fixture produces byte-identical catalogs across repeated generation.
- [x] Invalid schemas, paths, hashes, dependencies, cycles, or audience edges fail deterministically.
- [x] Explicit and query requests produce hash-pinned, budget-safe plans and packets.
