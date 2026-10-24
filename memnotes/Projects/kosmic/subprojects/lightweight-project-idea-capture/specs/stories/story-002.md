---
project_id: "kosmic"
subproject_id: "lightweight-project-idea-capture"
status: done
record_kind: "story"
local_id: "002"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: ["kosmic/lightweight-project-idea-capture/story/001"]
created: "2026-10-24"
updated: "2026-10-24"
related_notes: ["notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "b6cfd541e5199a137b30eea4c5f641d67d571dc6"
review_round: 1
completion_observations:
  - criterion: "AC-001: The skill recognizes an explicit idea-capture request and resolves the configured or explicitly selected Project, or the configured/selected vault for an explicit general idea. It clarifies an ambiguous destination before writing; it never invents a Project or silently changes scope."
    observation: "The owning task and early orchestrator path distinguish configured/selected Project capture from explicitly general vault capture, require clarification of ambiguous scope and forbid fallback/synthetic Projects. Actual walkthrough selected each explicit root without bootstrap."
    source: "task_idea.md / orchestrator and current documentation; managed walkthrough.py actual CLI output"
  - criterion: "AC-002: The owning procedure gives complete native invocations for both destinations, including optional title handling. A routine capture invokes the command once and uses its returned absolute file path for an individual Markdown link labelled with that full path, with no help lookup, confirmation listing/read-back, STATUS refresh or duplicate write."
    observation: "Owning procedure supplies both complete invocations and optional-title handling. Three real invocations saved notes and returned actual absolute-path Markdown links; no help or administrative read-back command followed success."
    source: "task_idea.md / orchestrator and current documentation; managed walkthrough.py actual CLI output"
  - criterion: "AC-003: Capture routing precedes Contributor/bootstrap prerequisites and requires no Quick Task, Story, worktree registration, clean-worktree check, review, receipt, skill/router repair or automatic implementation/research. Other operations retain their normal authority and approval rules; failures follow the actual diagnostic without blindly retrying an uncertain save."
    observation: "Early capture routing precedes bootstrap/Contributor prerequisites and expressly excludes work/Git/review/repair/bookkeeping. Actual minimal-root walkthrough produced only notes; failure handling reports diagnostics and uncertain saves without automatic retry."
    source: "task_idea.md / orchestrator and current documentation; managed walkthrough.py actual CLI output"
  - criterion: "AC-004: Project/vault layouts and all current capture references consistently describe Project `ideas/` and vault-root `GeneralIdeas/`, lazy creation, title-only filenames, safe numeric collision suffixes and dated History content without duplication. No reference claims automatic merging, promotion, append support or Project identity for general ideas."
    observation: "Current skill, README, docs, integration and init-layout references now describe both lazy stores, title-only names, numeric distinct collisions and complete text once under dated History; no append, merge or automatic promotion is introduced."
    source: "task_idea.md / orchestrator and current documentation; managed walkthrough.py actual CLI output"
  - criterion: "AC-005: Canonical Consumer knowledge and regenerated guidance match the exercised implementation. Generated/installed copies are not edited directly; capturing an idea does not itself project, curate, log, index or otherwise publish knowledge."
    observation: "Updated the existing stable Consumer CLI note, then governed generate published the atomic Skill Pair. No generated/installed file was directly edited, and walkthrough footprints show no per-capture knowledge/projection/index/log publication."
    source: "governed generate --work-record kosmic/lightweight-project-idea-capture/story/002; walkthrough.py footprint"
  - criterion: "AC-006: Actual procedure walkthroughs save Project and general ideas through the supported CLI, including no-Project general capture and a same-title second capture, and return the real file links. Affected checks and both independent review axes pass on held source/context before native completion; no implementation or installation claim is inferred from wording alone."
    observation: "Actual documented Project, no-Project general, omitted-title and same-title-second walkthroughs passed and printed real saved links. All five new owning-reference links resolve. Runtime is unchanged from the completed Story001 integration; no duplicate full suite or wording tests were added. Independent axes are requested before native finish."
    source: "walkthrough.py; five-link package check; receipted Story001 integration observations"
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
  review_base: "b6cfd541e5199a137b30eea4c5f641d67d571dc6"
  reviewed_revision: "84355560bee8313ea213d53f2dd23fc41b38b75769fa560e44e43bcf274983ad"
  findings: []
  scope:
    - "worktree:skills/SKILL.md"
    - "worktree:skills/README.md"
    - "worktree:README.md"
    - "worktree:skills/references/task_init.md"
    - "worktree:skills/references/agents_template.md"
    - "worktree:docs/README.md"
    - "worktree:skills/references/task_idea.md"
    - "project:subprojects/lightweight-project-idea-capture/specs/stories/story-002.md"
    - "project:notes/cli-projection-commands.md"
    - "project:skills/"
    - "project:specs/INDEX.md"
    - "project:specs/quick-tasks/register-idea-guidance-writer.md"
    - "project:.kosmic/working-directories.json"
---

# Conversational idea capture and guidance cutover

## User Story

As a Kosmic user, I want to say `kosmic idea` and receive a link to the saved Project or general idea, so capturing a thought stays a small side action rather than another coding workflow.

## Authority and Scope

Parent: [Epic 001](../epics/epic-001.md). Requirements: PRD FR-005–007 and the conversational consumption of FR-001–004. Follow the approved [Architecture](../architecture.md).

Depends on receipted [Story 001](story-001.md). Own the compact `task_idea.md` procedure, conversational routing, remaining skill/README/layout/example references, and corresponding canonical Consumer knowledge/projections. Reconcile shared `record_first_contract()`/entry guidance with Story001 under one integration owner rather than overwriting it. Consume the implemented CLI contract; do not add a second persistence mechanism or silently extend the engine.

Installation, Git push, router replacement, new CLI arguments, append/overwrite behavior, automatic promotion, historical migration and per-capture administration remain outside scope.

## Acceptance Criteria

- [ ] AC-001: The skill recognizes an explicit idea-capture request and resolves the configured or explicitly selected Project, or the configured/selected vault for an explicit general idea. It clarifies an ambiguous destination before writing; it never invents a Project or silently changes scope.
- [ ] AC-002: The owning procedure gives complete native invocations for both destinations, including optional title handling. A routine capture invokes the command once and uses its returned absolute file path for an individual Markdown link labelled with that full path, with no help lookup, confirmation listing/read-back, STATUS refresh or duplicate write.
- [ ] AC-003: Capture routing precedes Contributor/bootstrap prerequisites and requires no Quick Task, Story, worktree registration, clean-worktree check, review, receipt, skill/router repair or automatic implementation/research. Other operations retain their normal authority and approval rules; failures follow the actual diagnostic without blindly retrying an uncertain save.
- [ ] AC-004: Project/vault layouts and all current capture references consistently describe Project `ideas/` and vault-root `GeneralIdeas/`, lazy creation, title-only filenames, safe numeric collision suffixes and dated History content without duplication. No reference claims automatic merging, promotion, append support or Project identity for general ideas.
- [ ] AC-005: Canonical Consumer knowledge and regenerated guidance match the exercised implementation. Generated/installed copies are not edited directly; capturing an idea does not itself project, curate, log, index or otherwise publish knowledge.
- [ ] AC-006: Actual procedure walkthroughs save Project and general ideas through the supported CLI, including no-Project general capture and a same-title second capture, and return the real file links. Affected checks and both independent review axes pass on held source/context before native completion; no implementation or installation claim is inferred from wording alone.

## Implementation and Verification

1. Resolve the dependency's successful receipt and current supported CLI contract. Pin one fixed review baseline before edits and start one clean governed writer; do not re-audit unchanged Story001 source or historical receipts.
2. Add one compact owning reference, route the explicit capture intent early, and migrate all affected current instruction/layout/example callers. Keep capture-only authority narrow and retain normal gates everywhere else.
3. Update the existing stable CLI note and any needed development convention only for actual durable knowledge; regenerate the canonical Skill Pair through the governing Story. Do not create an evidence sidecar or a second idea store.
4. Walk the actual documented procedure on managed disposable roots: explicit Project/general destinations, absent/existing target directory, optional title and same-title capture, then returned full-path links. Check that no unwanted initialization or per-capture bookkeeping happens.
5. Use behavioral checks for changed contracts; do not add permanent prose/source-text snapshots or repeat unchanged engine checks solely because docs changed. Record actual observations and bounded independent Standards/Spec decisions, then finish natively.

## Routine Decision

`routine_decision_required: false`: this Story consumes Story001's supported deterministic capture command and its completed disposition. It adds conversational routing and owning guidance, not new executable capture mechanics or routine edges. Do not create another Task P proposal merely for instruction cutover.

## Technical Notes

- User intent is explicit capture, not approval to implement the idea. General ideas must not trigger Project bootstrap or a synthetic work record.
- Routine success ends with the returned link. Error recovery is diagnostic-driven; uncertain publication is not an instruction to save another copy.
- The note's History keeps dated contributions without duplicating the idea body; this procedure exposes no append command or automatic title-based merge.
- One writer owns shared instruction, canonical-note and projection integration. Native finish owns completion bookkeeping.

## Completion

The user approved this Story; implementation waits for Story001's successful receipt. All AC observations, consistent current guidance/projections, actual walkthrough evidence and converged independent review are required before native `work finish`. No new runtime package, installation or shared-router action is part of this Story.
