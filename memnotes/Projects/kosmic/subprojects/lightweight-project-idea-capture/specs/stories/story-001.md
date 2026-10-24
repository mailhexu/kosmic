---
project_id: "kosmic"
subproject_id: "lightweight-project-idea-capture"
status: done
record_kind: "story"
local_id: "001"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
created: "2026-10-24"
updated: "2026-10-24"
related_notes: ["notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: true
routine_proposals: ["../../../../specs/skill-proposals/2026-10-24-native-idea-capture-routine-decision.md"]
review_base: "f30f5f0e3c21a61bf2d12c7efe58d1e672e76b01"
review_round: 2
completion_observations:
  - criterion: "AC-001: The actual `idea` CLI requires exactly one explicit `--project` or `--vault` plus non-blank `--text`, with optional `--title`. Project capture requires valid existing Project identity and selects only that root's `ideas/`; general capture selects vault-root `GeneralIdeas/` without reading, requiring or creating a Project."
    observation: "Real CLI accepted Project and no-Project general destinations; refused both/neither selector, blank text/title and invalid identity before destination creation."
    source: "python -B -m unittest discover -s tests -q (tests.test_idea_capture); managed idea-smoke.py"
  - criterion: "AC-002: The selected missing child directory is created lazily and reused. Notes use title-only normalized filenames with no date; separate same-title requests, identical-content requests and concurrent captures preserve distinct complete notes with safe numeric suffixes."
    observation: "The first filename is title-only; identical repeat saves received -2; concurrent public CLI requests produced distinct complete notes without changing existing bytes."
    source: "python -B -m unittest discover -s tests -q (tests.test_idea_capture); managed idea-smoke.py"
  - criterion: "AC-003: Each note contains a usable title, actual creation time and the complete supplied text exactly once under a dated History entry. Unicode, equations, multiline content and uncertainty are retained. The History day and creation timestamp agree; only Project notes carry `project_id`, and general notes invent no Project identity."
    observation: "Saved χ(q), ħω, equations, multiline uncertainty exactly once under History; UTC creation instant lies within invocation bounds and its date matches History; general metadata/output omit project_id."
    source: "python -B -m unittest discover -s tests -q (tests.test_idea_capture); managed idea-smoke.py"
  - criterion: "AC-004: Project A, Project B, general ideas, canonical notes, dreams and unrelated files remain isolated. Capture works on minimal existing roots without Git, specs, generated guidance or a current work item; it creates no parent root, lock registry, work record, receipt, log, index, STATUS update or persistent sidecar."
    observation: "Minimal roots without Git/specs/guidance captured successfully. Isolation regression preserved Project B, canonical notes, dreams and unrelated bytes; footprint contains only the selected child and notes."
    source: "python -B -m unittest discover -s tests -q (tests.test_idea_capture); managed idea-smoke.py"
  - criterion: "AC-005: Blank input/title, both/neither target, invalid Project identity, missing roots, unsafe destination/candidate types and symlink targets are refused without overwriting existing data or false success JSON. Controlled write/publication failures preserve prior bytes and report the affected path; ordinary exceptions clean owned staging without claiming rollback after uncertain publication."
    observation: "Behavioral regressions refused unsafe children/candidates including symlink, directory and FIFO; injected write/link failures preserved prior bytes and removed owned staging. Late directory-fsync failure reported the complete published note path without rollback claims."
    source: "python -B -m unittest discover -s tests -q (tests.test_idea_capture); managed idea-smoke.py"
  - criterion: "AC-006: Successful JSON identifies the actual absolute `idea_path`, scope, title and creation time, including `project_id` only for Project capture. Nonzero failures do not recommend spec-operation resume or silently replay an uncertain save."
    observation: "Actual JSON returned absolute saved path, scope, title and UTC creation time, with project_id only on Project output. Refusals emitted no success JSON or spec-resume recommendation."
    source: "python -B -m unittest discover -s tests -q (tests.test_idea_capture); managed idea-smoke.py"
  - criterion: "AC-007: The named capture-only mutation exemption is reflected in the minimum entry/record-first guidance and current Consumer knowledge. Individual captures need no governing record or repair/initialization workflow, while an unrelated gated mutation still refuses missing authority."
    observation: "Native capture succeeded record-free while real generate without authority failed. Minimum entry/record-first guidance and stable Consumer note now declare the bounded exception; governed generation published the atomic Skill Pair."
    source: "idea-smoke.py; governed generate --work-record kosmic/lightweight-project-idea-capture/story/001"
  - criterion: "AC-008: Actual CLI smoke exercises both destinations and the changed failure/collision paths; focused behavioral and affected integrated checks pass. Canonical guidance/projections and the routine disposition match the implementation; actual independent Standards/Spec approvals precede native completion."
    observation: "CLI smoke passed both destinations, concurrent/identical saves and failures. All 818 integrated cases were exercised; 812 passed initially and the six environment-sensitive fixtures passed targeted reruns with corrected Git-discovery/device placement. Fresh proposer no-action was human-approved; independent review is requested on this held implementation before native finish."
    source: "integrated.log; fixtures-ceiling.log; device-fixture.log; migration-fixture.log; agent://IdeaRoutineProposer; user Approve no-action"
completion_review:
  reviewer: "coordinator; independent Standards/Spec pair"
  axes:
    standards:
      decision: "approved"
      reviewer: "agent://CreationStandardsScout"
    spec:
      decision: "approved"
      reviewer: "agent://CreationSpecResume"
  decision: "approved"
  review_base: "f30f5f0e3c21a61bf2d12c7efe58d1e672e76b01"
  reviewed_revision: "ee552b40c8b581e0191cd5604ca40da35fc10b7e373c82cb405e88a75d35133c"
  findings:
    - id: "STD-001"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      detail: "Selected root is canonicalized before no-follow open; caller-owned root symlinks resolve to their target. Destination/candidate safety remains enforced; optional stable root-refusal improvement deferred."
      source: "skills/scripts/kosmic_ideas.py:263"
      introduced_round: 1
    - id: "STD-002"
      axis: "standards"
      disposition: "Non-blocking"
      status: "resolved"
      resolution: "fixed"
      detail: "Registration-only carrier index cell was draft while record approved; corrected approved cell as completion bookkeeping. Catalog authority was unchanged."
      source: "specs/INDEX.md"
      introduced_round: 1
    - id: "STD-003"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      detail: "Close-error publication detection uses path in locals(); correct today but an explicit state variable would be clearer. Optional refactor deferred."
      source: "skills/scripts/kosmic_ideas.py:279-290"
      introduced_round: 1
  scope:
    - "worktree:skills/scripts/kosmic_ideas.py"
    - "worktree:skills/scripts/kosmic_project_skills.py"
    - "worktree:skills/SKILL.md"
    - "worktree:tests/test_idea_capture.py"
    - "project:subprojects/lightweight-project-idea-capture/specs/stories/story-001.md"
    - "project:notes/cli-projection-commands.md"
    - "project:skills/"
    - "project:specs/skill-proposals/2026-10-24-native-idea-capture-routine-decision.md"
    - "project:specs/skill-proposals/inputs/2026-10-24-native-idea-capture-routine-decision.md"
    - "project:subprojects/lightweight-project-idea-capture/specs/INDEX.md"
    - "project:specs/quick-tasks/register-native-idea-capture-writer.md"
    - "project:specs/INDEX.md"
    - "project:.kosmic/working-directories.json"
---

# Native Project and general idea capture

## User Story

As a person coding or researching, I want one native command to save a Project or general idea safely, so I can preserve tentative thoughts without creating implementation work.

## Authority and Scope

Parent: [Epic 001](../epics/epic-001.md). Requirements: PRD FR-001–006, the native-command portion of FR-007, and NFR-001–003. Follow the approved [Architecture](../architecture.md), including title-only filenames, dated History content and explicit Project/general selection.

Own `kosmic_ideas.py`, native parser/dispatch, result/refusal behavior, mutation classification and focused behavioral coverage. Include the minimum existing orchestrator entry/record-first and generated authority guidance needed to make native record-free capture truthful and usable; do not leave the new command contradicting a blanket work-record rule. Update the current Consumer CLI note and its governed projections before completion. The dependent Story owns the complete conversational task reference and remaining layout/example cutover.

No general note editor, append/overwrite command, automatic merge/promotion, new lock/journal/database, installation, Git push, router replacement or unrelated refactor is authorized.

## Acceptance Criteria

- [ ] AC-001: The actual `idea` CLI requires exactly one explicit `--project` or `--vault` plus non-blank `--text`, with optional `--title`. Project capture requires valid existing Project identity and selects only that root's `ideas/`; general capture selects vault-root `GeneralIdeas/` without reading, requiring or creating a Project.
- [ ] AC-002: The selected missing child directory is created lazily and reused. Notes use title-only normalized filenames with no date; separate same-title requests, identical-content requests and concurrent captures preserve distinct complete notes with safe numeric suffixes.
- [ ] AC-003: Each note contains a usable title, actual creation time and the complete supplied text exactly once under a dated History entry. Unicode, equations, multiline content and uncertainty are retained. The History day and creation timestamp agree; only Project notes carry `project_id`, and general notes invent no Project identity.
- [ ] AC-004: Project A, Project B, general ideas, canonical notes, dreams and unrelated files remain isolated. Capture works on minimal existing roots without Git, specs, generated guidance or a current work item; it creates no parent root, lock registry, work record, receipt, log, index, STATUS update or persistent sidecar.
- [ ] AC-005: Blank input/title, both/neither target, invalid Project identity, missing roots, unsafe destination/candidate types and symlink targets are refused without overwriting existing data or false success JSON. Controlled write/publication failures preserve prior bytes and report the affected path; ordinary exceptions clean owned staging without claiming rollback after uncertain publication.
- [ ] AC-006: Successful JSON identifies the actual absolute `idea_path`, scope, title and creation time, including `project_id` only for Project capture. Nonzero failures do not recommend spec-operation resume or silently replay an uncertain save.
- [ ] AC-007: The named capture-only mutation exemption is reflected in the minimum entry/record-first guidance and current Consumer knowledge. Individual captures need no governing record or repair/initialization workflow, while an unrelated gated mutation still refuses missing authority.
- [ ] AC-008: Actual CLI smoke exercises both destinations and the changed failure/collision paths; focused behavioral and affected integrated checks pass. Canonical guidance/projections and the routine disposition match the implementation; actual independent Standards/Spec approvals precede native completion.

## Implementation and Verification

1. Search existing knowledge and inspect the current CLI/document/publication patterns. Pin a fixed review baseline before the first implementation edit; use one clean, governed writer and preserve unrelated destination/index state.
2. Use TDD for consumer-visible uncertainties: scope/identity separation, title-only collisions, dated complete content, unsafe targets, concurrent no-replace publication and controlled failures. Test outcomes through the supported interface, not copied text or helper call counts.
3. Implement the single deep capture operation and thin existing-CLI adapter. Reuse no-follow/stage/link conventions, but not `_stage_bytes` identical-content replay semantics. Add no generic transaction or destination override.
4. Integrate native mutation classification, minimum authority guidance and the stable CLI note together; regenerate the canonical Skill Pair through its governed command. Do not edit generated or installed copies directly.
5. Exercise actual CLI behavior on managed disposable fixtures, record truthful per-criterion observations, complete the routine disposition, and obtain both review axes on held source/context. Run affected integration after changes stabilize; no fresh audit of unchanged inputs.

## Routine Decision

This Story introduces deterministic capture/publication mechanics, so `routine_decision_required: true`. Before completion, use the existing fresh-context Task P classification to decide whether the supported command itself is the appropriate reuse surface or a separate routine change is justified. Populate `routine_proposals` only with actual governed artifact paths and satisfy their approval/review gates. No extraction, publication or per-capture artifact is implied by classification.

## Technical Notes

- `--vault` is a general-capture selector, not a fallback Project or authority to initialize the vault.
- History is the note content, not an additional copy or an automatic append operation. Creation never edits an existing idea.
- Destination-sibling staging is the existing atomic-publication exception to managed scratch; capture itself must not create a managed run.
- No new runtime dependency is needed. Keep existing gated operations and historical records unchanged.

## Completion

The user approved this Story. All AC observations, Consumer knowledge/projection consistency, applicable routine disposition, actual CLI proof and converged independent review are required before `work finish`. Keep the record approved/in_progress during review; only native finish publishes receipted done. The dependent Story starts only after that receipt.
