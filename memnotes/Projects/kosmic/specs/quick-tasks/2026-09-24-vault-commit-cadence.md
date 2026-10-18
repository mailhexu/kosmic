---
status: "done"
created: "2026-09-24"
updated: "2026-09-24"
related_notes: ["notes/dream-reflection-workflow.md"]
related_specs: []
related_files: ["skills/SKILL.md", "skills/references/task_implement_story.md", "skills/references/task_review.md"]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: null
record_kind: "quick-task"
local_id: "2026-09-24-vault-commit-cadence"
---

# Quick Task: Vault commit cadence

## Request

Adopt the `2026-09-23-idea-commit-cadence` dream idea: commit the vault after
every epic/story closure instead of accumulating weeks of uncommitted history.

## Scope

- Encode a vault-commit rule in the Kosmic skill procedure docs (SKILL.md
  hygiene section, Task 6 story completion, Task 4 session review).

## Non-Goals

- No CLI changes, hooks, or automation — this is a workflow convention.

## Implementation

- SKILL.md File Hygiene pre-finish gate: every story/epic closure and session
  end commits the whole vault tree (`git add -A && git commit`), not only
  source files.
- task_implement_story.md: story `done` requires a vault commit; epic closure
  commits the vault before recording `done` status.
- task_review.md: session-end checklist gains a commit step after the
  `git status` classification.

## Verification

- Docs-only change; `validate --project` and the projection remain green.
- The quick task itself is committed as part of the vault (dogfooding the rule).

## Outcome

Implemented 2026-09-24; suite untouched; validated.
