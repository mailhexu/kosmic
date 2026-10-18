---
status: "done"
created: "2026-09-14"
updated: "2026-09-15"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: ["../stories/story-003-lease-backed-run-lifecycle.md", "../stories/story-004-retention-and-terminal-receipts.md", "../stories/story-010-owner-cleanup-recovery.md", "../stories/story-005-durable-promotion-complete-reporting.md", "../stories/story-006-temporary-caller-migration.md", "../stories/story-014-atomic-staging-markers-detection.md", "../stories/story-011-managed-run-skill-cutover.md", "../stories/story-007-managed-run-initial-release.md"]
project_id: "kosmic"
subproject_id: "feature-prd-managed-run-workspaces"
record_kind: "epic"
local_id: "002"
---

# Epic 24: Managed Run Initial Release

## Description

Deliver a usable managed-run lifecycle for agents and Kosmic commands, including cross-tool-call ownership, deterministic retention, Git-audited promotion and owner cleanup, exhaustive caller migration, and one predictable skill workflow.

## Scope

### In Scope

- Detached per-run `flock` holder and private control transport.
- Begin, succeed, fail, extend, promote, and status/dry-run CLI behavior.
- Terminal receipts, deterministic retention, journaled owner cleanup, and complete reporting.
- Automatic migration of every ordinary temporary caller plus report-only atomic staging markers.
- Task P-governed one-step skill cutover and initial-release dogfood, evidence, and review.

### Out of Scope

- General `gc --apply`.
- Destructive abandoned publication-stage recovery.
- General cleanup outside `.tmp/kosmic/`.

## Stories

| Story | Title | Status |
|---|---|---|
| [story-045](../stories/story-003-lease-backed-run-lifecycle.md) | Lease-Backed Run Lifecycle | done |
| [story-046](../stories/story-004-retention-and-terminal-receipts.md) | Retention and Terminal Receipts | done |
| [story-052](../stories/story-010-owner-cleanup-recovery.md) | Owner Cleanup Transaction and Recovery | done |
| [story-047](../stories/story-005-durable-promotion-complete-reporting.md) | Durable Promotion and Complete Reporting | done |
| [story-048](../stories/story-006-temporary-caller-migration.md) | Temporary Caller Migration | done |
| [story-056](../stories/story-014-atomic-staging-markers-detection.md) | Atomic Staging Markers and Detection | done |
| [story-053](../stories/story-011-managed-run-skill-cutover.md) | Managed Run Skill Cutover | done |
| [story-049](../stories/story-007-managed-run-initial-release.md) | Managed Run Initial Release | done |

## Success Criteria

- [x] Agents complete a multi-tool-call run through checkable lifecycle operations.
- [x] Successful and disposable runs clean through the journaled owner transaction; failures receive exact bounded expiry.
- [x] Promotion is no-clobber, hash-verified, and Git-audited.
- [x] No non-exempt Kosmic caller uses system temp or ad hoc scratch.
- [x] Fresh-context behavior follows one managed-run step and one lifecycle reference.
- [x] Initial release passes security, Standards, and Spec review.

## Progress

- Stories: 8/8 done
- Last updated: 2026-09-16
