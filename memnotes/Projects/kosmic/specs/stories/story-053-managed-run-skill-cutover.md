---
status: done
created: 2026-09-14
updated: 2026-09-16
linked_epic: ../epics/epic-24-managed-run-initial-release.md
linked_architecture: ../architecture-managed-run-workspaces.md
linked_prd: ../prd-managed-run-workspaces.md
related_notes: [notes/managed-run-workspace-lifecycle.md, notes/cli-projection-commands.md]
consumer_interface_change: true
proposal_required: true
skill_proposal: ../skill-proposals/2026-09-14-managed-run-workflow.md
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
---

# Story 053: Managed Run Skill Cutover

## User Story

As an agent using Kosmic, I want one predictable managed-run instruction and one contextual lifecycle reference so that scratch policy is followed without duplicated prose.

## Approval Blocker

This story must remain `draft` until the declared Task P skill proposal exists, is non-pending, has required behavioral evidence, and is Maintainer-approved. Creating that proposal is the next governance action after Stories 043–048 establish the executable behavior.

## Acceptance Criteria

- [ ] The accepted Task P proposal defines the trigger, one `managed run` leading concept, checkable completion criterion, and progressively disclosed lifecycle reference.
- [ ] `skills/SKILL.md` contains one mandatory universal step and no branch-specific scratch mechanics.
- [ ] `skills/README.md`, task references, ADR/spec references, and all inventory consumers remove copied scratch policy while retaining distinct durable source, evidence, spec, log, and pending-test rules.
- [ ] Fresh-context behavior obtains a managed run before scratch, loads lifecycle detail only when needed, and finalizes with recorded Git status.
- [ ] Canonical project/library projections and supported adapter bytes match the reviewed source.

## Tasks

### Phase 1: Research
- [ ] Run Task P in fresh context and obtain Maintainer approval before implementation.
- [ ] Refresh the policy-consumer inventory.

### Phase 2: Tests
- [ ] Write failing fresh-context trigger, disclosure, and completion tests.
- [ ] Keep the duplicate-policy source check red until clean cutover.

### Phase 3: Implementation
- [ ] Apply the approved one-step and one-reference skill change.
- [ ] Migrate every policy consumer and regenerate canonical artifacts.

### Phase 4: Review
- [ ] Compare baseline and candidate behavior from the Task P proposal.
- [ ] Complete Standards and Spec review.

## Routine Decision

This changes procedural skill content but adds no `uses_routines` edge. Task P governs the skill change; no routine proposal is required.

## Definition of Done

- [ ] Task P proposal is accepted and behaviorally verified.
- [ ] No duplicate scratch policy remains.
- [ ] Baseline and final Git status, knowledge, generated outputs, and project log are current.
- [ ] Review has no unresolved Blocking finding.
