---
status: "done"
created: "2026-09-06"
updated: "2026-09-06"
linked_epic: "../epics/epic-001-proposer-contract.md"
linked_architecture: "../architecture.md"
linked_prd: "../prd.md"
related_notes: ["cli-projection-commands.md"]
evidence_packs: ["2026-09-06-skill-proposal-loop-impl"]
consumer_interface_change: true
proposal_required: false
review_base: "ce222de2"
review_round: 2
project_id: "kosmic"
subproject_id: "skill-proposal-loop"
record_kind: "story"
local_id: "001"
---

# Story 018: Task P Procedure and Template

## User Story

As a Kosmic maintainer,
I want a self-sufficient fresh-context proposal procedure,
So that reusable Patterns are explicitly classified into one atomic skill decision.

## Acceptance Criteria

- [x] `references/task_propose_skill.md` defines inputs, curated-context rules, novelty search, scope classification, independence policy, and exactly one `create|update|no_action` output.
- [x] Shared/global changes require a fresh-context proposer subagent; permitted same-agent fallback records mode and reason.
- [x] A shipped proposal template matches AD-P3, and SKILL.md/README/task routing place Task P after qualifying Distillation.
- [x] Task P forbids direct edits to canonical or installed skills and requires exact proposed files/instructions rather than generic advice.

## Tasks

### Phase 1: Research
- [x] Re-read WikiSkill proposer contract and existing Task 9/Task 7 patterns.

### Phase 2: Tests (TDD)
- [x] TEST-018A: shipped procedure and template contain all normative contract points.

### Phase 3: Implementation
- [x] IMPL-018A: add Task P procedure, template, routing, and user docs.

### Phase 4: Review
- [x] Documentation contract test passes.
- [x] Task 7 review approves.

## Definition of Done

- [x] All acceptance criteria met; tests pass; review approved; knowledge and log updated.
