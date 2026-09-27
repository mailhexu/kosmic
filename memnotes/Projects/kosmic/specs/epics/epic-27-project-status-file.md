---
status: approved
created: 2026-09-27
updated: 2026-09-27
linked_prd: ../prd-project-status-file.md
linked_architecture: ../architecture-project-status-file.md
linked_stories: [../stories/story-064-status-generation-core.md, ../stories/story-065-status-drift-gates.md, ../stories/story-066-status-workflow-dogfood-release.md]
---

# Epic 27: Project Status File

## Description

Give every Kosmic-managed working directory a self-describing, generated
STATUS.md: current spec statuses derived deterministically from vault
frontmatter, created at initialization, regenerated on every spec event, and
protected against drift by validation and the completion gate.

## Scope

### In Scope

- `status_root` binding in ProjectEntry.md via init/migrate.
- Deterministic `generate-status` command and STATUS.md content contract.
- Validate drift detection and `check-completion` staleness gate.
- Task 1/0/5/6/7 workflow steps and AGENTS.md template reference.
- Dogfood: bind this repository and live with the generated STATUS.md.

### Out of Scope

- Dream content in STATUS.md; multi-project directories; filesystem watchers.

## Dependency Order

`064 → 065 → 066`.

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-064](../stories/story-064-status-generation-core.md) | Status Generation Core | approved |
| [story-065](../stories/story-065-status-drift-gates.md) | Status Drift Gates | approved |
| [story-066](../stories/story-066-status-workflow-dogfood-release.md) | Status Workflow Dogfood Release | approved |

## Success Criteria

- [x] All three stories complete in order
- [x] Fresh fixture project initializes with AGENTS.md section and matching STATUS.md
- [x] Status flips regenerate byte-stably; hand edits fail validation; stale STATUS blocks story done
- [x] Full suite, gates, pair validation, and adapter checks green
- [x] This repository's own STATUS.md generated, committed, and drift-free

## Progress

- Stories: 3/3 done
- Last updated: 2026-09-27
