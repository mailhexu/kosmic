---
status: "done"
created: "2026-09-14"
updated: "2026-09-14"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-008-destructive-run-garbage-collection.md", "../stories/story-012-bounded-startup-collection.md", "../stories/story-009-atomic-publication-recovery.md", "../stories/story-013-managed-run-destructive-release.md"]
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "epic"
local_id: "003"
---

# Epic 25: Managed Run Destructive Cleanup

## Description

Activate destructive cleanup only after real concurrency, crash, containment, and recovery evidence proves that expired run and publication staging can be removed without touching user work or violating atomic publication.

## Scope

### In Scope

- Explicit `gc --apply` for verified run directories, followed by bounded startup reuse.
- Fault-injected cleanup recovery and dedicated security review.
- Destination-specific atomic-publication recovery using Story 056 markers.
- Combined destructive release verification and migration-report removal.

### Out of Scope

- Cleanup of arbitrary `.tmp` or root-level files.
- Network-filesystem destructive mode.
- Cross-worktree shared scratch and permanent background daemon.

## Stories

| Story | Title | Status |
|---|---|---|
| [story-050](../stories/story-008-destructive-run-garbage-collection.md) | Destructive Run Garbage Collection | done |
| [story-054](../stories/story-012-bounded-startup-collection.md) | Bounded Startup Collection | done |
| [story-051](../stories/story-009-atomic-publication-recovery.md) | Atomic Publication Recovery | done |
| [story-055](../stories/story-013-managed-run-destructive-release.md) | Managed Run Destructive Release | approved |

## Success Criteria

- [x] Competing collectors and every interrupted operation converge without double deletion.
- [x] Symlink, malformed, active, wrong-owner, and unsupported-filesystem cases preserve all data.
- [x] Publication recovery proves exactly one valid canonical tree before removing staging or backup.
- [x] Git before/after records show no unrelated worktree mutation.
- [x] Both destructive paths pass dedicated security and code review.

## Progress

- Stories: 3/4 done (055 destructive release and combined matrix remain)
- Last updated: 2026-09-16
