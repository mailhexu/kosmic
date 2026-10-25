---
project_id: "kosmic"
subproject_id: null
status: "approved"
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

- [ ] The PRD template carries the Prototype section with filling guidance that excludes exact flags, module names, and schemas.
- [ ] The Architecture template's API Design section states the interface-sketch convention and the one-home-per-fact rule.
- [ ] The Story template's test phase opens with the execution-scenario convention.
- [ ] The templates remain consistent with task_create_spec.md's workflow description, and the installed OMP release package matches the committed tree after reinstall.

## Routine Decision

No new deterministic procedure mechanics: template text only.
