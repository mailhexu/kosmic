---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-003-cross-project-domain-governance.md", "../stories/story-004-shared-router-installation.md"]
project_id: "kosmic"
subproject_id: "shared-domain-skill-library"
record_kind: "epic"
local_id: "002"
---

# Epic 15: Shared Library Governance and Installation

## Description

Extend Task P to domain-owned library targets and expose exactly one atomically installed Shared Skill Router through every named adapter.

## Scope

### In Scope
- Cross-project Evidence Pack references
- Target-domain Maintainer authorization and rejection memory
- Canonical root-router package, adapter install/check, rollback, and activation wording

### Out of Scope
- Automated Maintainer authentication or host-private runtime introspection

## Stories
- [Story 027: Cross-Project Domain Governance](../stories/story-003-cross-project-domain-governance.md)
- [Story 028: Shared Router Installation](../stories/story-004-shared-router-installation.md)

## Acceptance Criteria
- [x] A TB2J proposal cannot update ABINIT guidance without an ABINIT Maintainer identifier and Task 7 approval.
- [x] Each adapter exposes one verified Shared Skill Router and no managed Project pair after cutover.
- [x] Failed publication or installation preserves the last complete valid state.
