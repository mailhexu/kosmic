---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-001-library-schema-catalog.md", "../stories/story-002-deterministic-library-resolver.md"]
project_id: "kosmic"
subproject_id: "shared-domain-skill-library"
record_kind: "epic"
local_id: "001"
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
- [Story 025: Library Schema and Catalog](../stories/story-001-library-schema-catalog.md)
- [Story 026: Deterministic Library Resolver](../stories/story-002-deterministic-library-resolver.md)

## Acceptance Criteria
- [x] A valid multi-domain `Skills/` fixture produces byte-identical catalogs across repeated generation.
- [x] Invalid schemas, paths, hashes, dependencies, cycles, or audience edges fail deterministically.
- [x] Explicit and query requests produce hash-pinned, budget-safe plans and packets.
