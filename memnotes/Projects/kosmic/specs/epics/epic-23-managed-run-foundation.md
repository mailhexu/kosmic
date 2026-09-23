---
status: done
created: 2026-09-14
updated: 2026-09-15
linked_prd: ../prd-managed-run-workspaces.md
linked_architecture: ../architecture-managed-run-workspaces.md
linked_stories: [../stories/story-043-temporary-path-inventory-root-anchor.md, ../stories/story-044-git-evidence-run-store.md]
---

# Epic 23: Managed Run Foundation

## Description

Establish the trusted path, exhaustive migration inventory, Git evidence, and recoverable state substrate needed before any process can own or delete temporary artifacts.

## Scope

### In Scope

- Versioned inventory of every temporary-path caller and policy consumer.
- Worktree-local `.tmp/kosmic/` resolution and root ignore validation.
- Descriptor-relative root anchoring, private permissions, and fail-closed path checks.
- Strict porcelain-v2 Git snapshots, manifests, operation records, reports, and read-only diagnostics.

### Out of Scope

- Detached holder and terminal retention.
- Promotion or destructive cleanup.
- Existing caller migration and skill cutover.

## Stories

| Story | Title | Status |
|---|---|---|
| [story-043](../stories/story-043-temporary-path-inventory-root-anchor.md) | Temporary-Path Inventory and Root Anchor | done |
| [story-044](../stories/story-044-git-evidence-run-store.md) | Git Evidence and Run Store | done |

## Success Criteria

- [x] Every current caller and policy occurrence is classified with zero unexplained entries.
- [x] Path resolution never uses `/tmp`, `/dev/shm`, or an unverified ancestor.
- [x] Read-only status classifies every managed or unattributed entry and records Git evidence.
- [x] Both stories pass focused tests and mandatory code review.

## Progress

- Stories: 2/2 done
- Last updated: 2026-09-16
