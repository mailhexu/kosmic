---
status: done
created: 2026-09-14
updated: 2026-09-15
linked_prd: ../prd-managed-run-workspaces.md
linked_architecture: ../architecture-managed-run-workspaces.md
linked_stories: [../stories/story-045-lease-backed-run-lifecycle.md, ../stories/story-046-retention-and-terminal-receipts.md, ../stories/story-052-owner-cleanup-recovery.md, ../stories/story-047-durable-promotion-complete-reporting.md, ../stories/story-048-temporary-caller-migration.md, ../stories/story-056-atomic-staging-markers-detection.md, ../stories/story-053-managed-run-skill-cutover.md, ../stories/story-049-managed-run-initial-release.md]
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
| [story-045](../stories/story-045-lease-backed-run-lifecycle.md) | Lease-Backed Run Lifecycle | done |
| [story-046](../stories/story-046-retention-and-terminal-receipts.md) | Retention and Terminal Receipts | done |
| [story-052](../stories/story-052-owner-cleanup-recovery.md) | Owner Cleanup Transaction and Recovery | done |
| [story-047](../stories/story-047-durable-promotion-complete-reporting.md) | Durable Promotion and Complete Reporting | done |
| [story-048](../stories/story-048-temporary-caller-migration.md) | Temporary Caller Migration | done |
| [story-056](../stories/story-056-atomic-staging-markers-detection.md) | Atomic Staging Markers and Detection | done |
| [story-053](../stories/story-053-managed-run-skill-cutover.md) | Managed Run Skill Cutover | done |
| [story-049](../stories/story-049-managed-run-initial-release.md) | Managed Run Initial Release | done |

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
