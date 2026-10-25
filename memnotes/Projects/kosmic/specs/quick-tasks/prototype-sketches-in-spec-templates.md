---
project_id: "kosmic"
subproject_id: null
status: done
approved_by: user
approved_on: "2026-10-25"
approval_provenance: "User picked 'next' after comparing variants; recommended option A + explicit B adopted."
record_kind: "quick-task"
local_id: "prototype-sketches-in-spec-templates"
registration_root: "/home/hexu/projects/myagentskills/kosmic"
registration_outputs: [".kosmic/working-directories.json", "worktree:.kosmic/workdir.json"]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
created: "2026-10-25"
updated: "2026-10-25"
review_base: 066ea188bbb57aa1c124d8d785eaf7a986086236
review_round: 1
completion_observations:
  - criterion: "The PRD template carries the Prototype section with filling guidance that excludes exact flags, module names, and schemas."
    observation: "template-prd.md gained '## Prototype (what the user sees)' between Non-Goals and Functional Requirements, with filling guidance that shows the experience at shape level and explicitly defers exact flags, module names, and schemas to the Architecture."
    source: "The episode diff for skills/references/templates/template-prd.md."
  - criterion: "The Architecture template's API Design section states the interface-sketch convention and the one-home-per-fact rule."
    observation: "The API Design placeholder now describes the exact interface sketch — flags/parameters, destinations, output shape, refusal list, module/file map — and states that the PRD shows the experience at shape level only while this section is the contract implementers and reviewers work from."
    source: "The episode diff for skills/references/templates/template-architecture.md."
  - criterion: "The Story template's test phase opens with the execution-scenario convention."
    observation: "Phase 2 now opens with SCENARIO-001: write the execution scenario first — one bounded session with expected outcomes and refusals — which becomes the disposable smoke; the retained TEST items keep test-first practice."
    source: "The episode diff for skills/references/templates/template-story.md."
  - criterion: "The templates remain consistent with task_create_spec.md's workflow description, and the installed OMP release package matches the committed tree after reinstall."
    observation: "task_create_spec.md's Principles gained the matching Sketch-at-every-level bullet, and both review axes approved the four-file diff as coherent; the release package was reinstalled from this episode's tree before finish, with the previous installation backed up and diff -r (excluding __pycache__) clean against the working tree that becomes the commit."
    source: "Both review-axis approvals for the episode diff; backup /home/hexu/.omp/agent/skill-backups/kosmic-before-066ea18-20261025T192948Z; diff -r result."
completion_review:
  reviewer: main-assistant-coordinator
  axes:
    standards:
      decision: approved
      reviewer: TemplateSketchStandards
    spec:
      decision: approved
      reviewer: TemplateSketchSpec
  decision: approved
  review_base: 066ea188bbb57aa1c124d8d785eaf7a986086236
  reviewed_revision: a3822596f75804e609f4500a9c8827d6a2666c6371bafb1797ca931c499f6e6f
  scope:
    - worktree:skills/references/templates/template-prd.md
    - worktree:skills/references/templates/template-architecture.md
    - worktree:skills/references/templates/template-story.md
    - worktree:skills/references/task_create_spec.md
    - project:specs/quick-tasks/prototype-sketches-in-spec-templates.md
    - project:specs/INDEX.md
    - project:log/kosmic-2026-10-25.md
  findings: []
---

# Prototype sketches in spec templates

## Request

The user asked where a "prototype description" (a CLI invocation with parameters, a file/function skeleton, a workflow outline) belongs in the spec hierarchy. After comparing variants they accepted the recommendation: every level carries a sketch at its own fidelity — PRD shows the experience, Architecture owns the exact interface contract, the Story's test phase opens with the execution scenario.

## Scope

- `skills/references/templates/template-prd.md`: add a `## Prototype (what the user sees)` section between Non-Goals and Functional Requirements, with filling guidance: one annotated invocation plus output sample and a short workflow, at shape-level fidelity; exact flags, module names, and schemas are excluded (Architecture owns them).
- `skills/references/templates/template-architecture.md`: make the existing `## API Design` section an explicit interface-sketch convention — exact flags, destinations, output shape, refusal list, and module map; one home per fact, with the PRD showing shape only.
- `skills/references/templates/template-story.md`: add to Phase 2 the convention that the execution scenario (one bounded session with expected outcomes, refusals included) is written first and becomes the disposable smoke.
- `skills/references/task_create_spec.md`: one sentence pointing authors at the three sketch levels and the one-home-per-fact rule.
- Register this repository root as the episode writer and remove the registration during owned-run cleanup; reinstall the release `skills/` package to the OMP adapter after the commit (backup-then-copy) and verify with `check-installation`.

## Out of Scope

- No canonical note or generated-pair changes; no change to spec-create, completion gates, or validation; no retroactive editing of existing approved records.

## Acceptance Criteria

- [x] The PRD template carries the Prototype section with filling guidance that excludes exact flags, module names, and schemas.
- [x] The Architecture template's API Design section states the interface-sketch convention and the one-home-per-fact rule.
- [x] The Story template's test phase opens with the execution-scenario convention.
- [x] The templates remain consistent with task_create_spec.md's workflow description, and the installed OMP release package matches the committed tree after reinstall.

## Routine Decision

No new deterministic procedure mechanics: template text only.

## Verification

- Both review axes approved the four-file diff in round 1 with no findings; the full suite ran 825 tests OK on this tree (template text only; no test exercises templates).
- The release package was reinstalled from the episode tree with the previous installation backed up; the installed copy matches the working tree excluding `__pycache__`, and no bytecode ships in the install.

## Links

- Related notes: none; this Quick Task is the governing record.
- Related specs: none.
- Related files: `skills/references/templates/template-prd.md`,
  `skills/references/templates/template-architecture.md`,
  `skills/references/templates/template-story.md`,
  `skills/references/task_create_spec.md`.

## Review

Round 1 reviewed the episode packet against base `066ea18` on both axes; both
approved with no findings. `review_round` is 1 and `completion_review` records
the actual approvals.

## Code Review

**Review Base**: `066ea188bbb57aa1c124d8d785eaf7a986086236`  
**Current Round**: 1  
**Reviewed Revision**: `a3822596f75804e609f4500a9c8827d6a2666c6371bafb1797ca931c499f6e6f`  
**Decision**: approved  
**Standards Reviewer**: `TemplateSketchStandards` — approved  
**Spec Reviewer**: `TemplateSketchSpec` — approved

### Standards

| ID | Disposition | Evidence | Required Resolution | Introduced | Status | Resolution | Worker Response |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (none) | — | No Standards finding: placement, fidelity boundaries, and TDD consistency all approved; the diff changes only the four declared guidance files. | — | — | — | — | — |

### Spec

| ID | Disposition | Evidence | Required Resolution | Introduced | Status | Resolution | Worker Response |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (none) | — | No Spec finding: the diff stays inside the declared scope and satisfies every acceptance criterion. | — | — | — | — | — |

### Re-review History

| Round | Reviewed Revision | Findings Checked | New REG/LATE Evidence | Decision |
| --- | --- | --- | --- | --- |
| 1 | `a3822596f75804e609f4500a9c8827d6a2666c6371bafb1797ca931c499f6e6f` | Complete first-pass inventory | n/a | Approved |
