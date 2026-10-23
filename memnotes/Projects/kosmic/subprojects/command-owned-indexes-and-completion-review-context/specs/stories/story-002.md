---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: done
record_kind: "story"
local_id: "002"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: ["kosmic/command-owned-indexes-and-completion-review-context/story/001"]
created: "2026-10-23"
updated: "2026-10-23"
related_notes: ["notes/cli-projection-commands.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: true
routine_proposals: ["../../../../specs/skill-proposals/2026-10-23-native-cli-routine-decision.md"]
review_base: "d375e013e54171efd95fff573b42dbb1e99434b1"
review_round: 1
completion_observations:
  - criterion: "AC-001: Supported interleaved creation and finish updates use the existing creation lock for index read/merge/publication and retain all relevant rows/statuses; unrelated index content is unchanged."
    observation: "Native CLI finish waited for the active index writer while concurrent native creation completed; own done row, escaped-title neighbor draft row and unrelated context all survived."
    source: "Serialization regression failed against pre-lock runtime (0.368s), passed after coordination (1.184s);80 affected tests passed."
  - criterion: "AC-002: A native-created implementation record completes through actual `work finish`, its owning canonical row becomes `done`, and existing proof/review/source/authority/receipt gates still decide completion."
    observation: "A native-created Quick Task completed through actual CLI finish with a real successful fixture receipt and its owning row done; escaped link/title and legacy context were preserved. Existing proof/review/source/authority refusal cases also passed."
    source: "Actual smoke_title_finish.py EXIT0;80 affected tests passed including native-created finish and existing gate/receipt regressions."
  - criterion: "AC-003: Index coordination adds no recursive lock acquisition, new finish admission rule or publication-order change. Detected external index divergence is refused without overwriting; arbitrary non-cooperating editors are not claimed to be transactionally serialized."
    observation: "Shared locking and expected-current no-follow publication preserve native-created workflows and refuse detected external edits without a new admission gate or publication-order change. The user approved the exact canonical creation-lock metadata amendment after integrated retry failures; only this output is scope-exempt and only its same-root digest entry is excluded. Other metadata remains bound."
    source: "All three previously failing legacy retry cases and both same-root/external-writer fingerprint cases pass (5 tests,2.302s). Actual CLI finish refuses unrelated .kosmic/source-context.txt with SCOPE_DENIED, unchanged record and no receipt (0.335s). Full integrated suite:805 tests passed in185.962s."
  - criterion: "AC-004: All current creation callers and generated guidance consume returned native identities/paths and use owning-operation resume. Obsolete manual row-creation and PRD-only resume instructions are removed without leaving a second fallback convention."
    observation: "All native creation steps consume returned identities/record/index paths and owning-operation recovery. Manual native-row steps and obsolete slug filename aliases were removed; the caller scan retained only the intentional Research memo index instruction."
    source: "Source caller scan over README.md and skills/ found only task_create_spec.md Research indexing; revised Epic/Story/index templates and record_first_contract are in scope."
  - criterion: "AC-005: Instructions retain user approval gates, full-absolute-path handoff links and trust in successful commands; research/non-native artifacts and historical missing rows are not falsely described as automatically indexed."
    observation: "User approval gates and individual full-absolute-path handoff instructions remain intact. Research/non-native navigation remains manually maintained; historical missing rows are explicitly not automatically migrated. Native finish alone owns completion bookkeeping."
    source: "Reviewed owning workflow reference sections and templates; actual five-kind creation/resume/finish smoke used native results without a manual record-row edit or confirmation command."
  - criterion: "AC-006: Canonical CLI knowledge and generated projections describe the exercised behavior consistently. The real documented create/resume/finish sequence works without a manual index edit or administrative validation round-trip."
    observation: "Canonical usage/development knowledge and the generated Skill Pair now describe shared index serialization and truly read-only Git discovery. Documented CLI creation/resume/finish and explicit-writer preparation succeeded without administrative read-back."
    source: "Native generate EXIT0 atomic publication; actual five-kind/recovery and finish smokes EXIT0. Read-only Git smoke kept all Project/writer bytes unchanged with caller optional locks enabled, while its ordinary-git-status positive control changed the index."
completion_review:
  reviewer: "Main"
  decision: "approved"
  axes:
    standards:
      reviewer: "CreationStandardsScout"
      decision: "approved"
    spec:
      reviewer: "CreationSpecResume"
      decision: "approved"
  review_base: "d375e013e54171efd95fff573b42dbb1e99434b1"
  reviewed_revision: "79779e39581772774447299c0d0273394e2108a0a6595b402c15f3bb6a5512f6"
  scope:
    - "worktree:skills/scripts/kosmic_completion.py"
    - "worktree:skills/scripts/kosmic_work.py"
    - "worktree:skills/scripts/kosmic_project_skills.py"
    - "worktree:tests/test_record_scoped_completion.py"
    - "worktree:tests/test_prepare_completion_prefill.py"
    - "worktree:skills/references/task_create_spec.md"
    - "worktree:skills/references/task_quick_task.md"
    - "worktree:skills/references/templates/template-specs-index.md"
    - "worktree:skills/README.md"
    - "worktree:skills/references/templates/template-epic.md"
    - "worktree:skills/references/templates/template-story.md"
    - "project:subprojects/command-owned-indexes-and-completion-review-context/specs/stories/story-002.md"
    - "project:subprojects/command-owned-indexes-and-completion-review-context/specs/INDEX.md"
    - "project:specs/INDEX.md"
    - "project:notes/cli-projection-commands.md"
    - "project:notes/cli-extension-conventions.md"
    - "project:skills/"
    - "project:subprojects/command-owned-indexes-and-completion-review-context/specs/prd.md"
    - "project:subprojects/command-owned-indexes-and-completion-review-context/specs/architecture.md"
    - "project:subprojects/command-owned-indexes-and-completion-review-context/specs/epics/epic-001.md"
    - "project:subprojects/command-owned-indexes-and-completion-review-context/specs/epics/epic-002.md"
    - "worktree:skills/references/work_completion.md"
  findings:
    - id: "INT-001"
      axis: "standards"
      disposition: "Blocking"
      status: "resolved"
      introduced_round: 1
      summary: "New creation-lock metadata breaks legacy interrupted-finish retries and same-root source binding."
      evidence: "Integrated804 tests produced3 retry failures: SCOPE_DENIED on the newly created canonical .kosmic/create.lock. Actual native same-root preparation changed digest44136fa3... to a90f655e... when only that empty lock file was added."
      worker_response:
        kind: "fixed"
        detail: "User approved exact canonical Project .kosmic/create.lock as command-owned output and same-root-only digest exclusion; implemented only this classification."
        evidence: "Three observed retry failures and two fingerprint boundary cases pass (5 tests,2.302s); actual unrelated metadata scope refusal passes;805 integrated tests passed in185.962s."
      resolution: "fixed"
      resolution_note: "CreationStandardsScout and CreationSpecResume independently accepted the exact implementation and confirmed approval on final source pin79779e39... in the first complete two-axis pair."
    - id: "STD2-A"
      axis: "standards"
      disposition: "Non-blocking"
      status: "resolved"
      introduced_round: 1
      summary: "Packet omitted an abandoned worker duplicate test scaffold."
      resolution: "fixed"
      resolution_note: "Removed only the failed worker-owned duplicate block, restoring exact fixed-base file; both reviewers confirmed approval on corrected binding. The805-test checkout never included this abandoned scaffold."
    - id: "STD2-B"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "index.relative_to(root) is unguarded for an out-of-root index; unreachable under canonical record layouts."
    - id: "STD2-C"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Finish reuses creation-layer RESERVATION_CONFLICT for detected index divergence; a dedicated error vocabulary could distinguish it."
    - id: "STD2-D"
      axis: "standards"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Persistent canonical creation lock is not ignored or exempt from work start clean-worktree admission; pre-existing creation-path trade-off, not expanded in this Story."
    - id: "SP2-B"
      axis: "spec"
      disposition: "Non-blocking"
      status: "open"
      introduced_round: 1
      summary: "Finish now refuses symlinked INDEX.md consistently with creation no-follow publication, stricter than the old follow-symlink behavior."
---

# Finish index coordination and native workflow cutover

## User Story

As a Kosmic caller, I want native creation and finish to preserve each other's index changes and the instructions to use their outputs directly, so the workflow requires no agent-written rows or redundant confirmation passes.

## Authority and Scope

Parent: [Epic 001](../epics/epic-001.md); requirements: creation/index FR-008 and integration of FR-001–004; design: Architecture ADR-003–004 and Caller Cutover.

Depends on receipted completion of [Story 001](story-001.md). Own finish's supported index-writer coordination, real create-through-finish behavior, and all native-index caller/reference/knowledge cutover. Do not change finish admission, review/receipt semantics, publication order, or historical index policy.

Likely source seams: `kosmic_completion.py::_update_indexes`, Story 001's existing creation-lock helpers, workflow references/templates, `skills/SKILL.md`, README, `record_first_contract()` and the repository instruction caller. Update the existing canonical CLI note and regenerate projections; never edit generated or installed copies directly. Installation, global router changes and Git push are not added by this Story.

## Acceptance Criteria

- [ ] AC-001: Supported interleaved creation and finish updates use the existing creation lock for index read/merge/publication and retain all relevant rows/statuses; unrelated index content is unchanged.
- [ ] AC-002: A native-created implementation record completes through actual `work finish`, its owning canonical row becomes `done`, and existing proof/review/source/authority/receipt gates still decide completion.
- [ ] AC-003: Index coordination adds no recursive lock acquisition, new finish admission rule or publication-order change. Detected external index divergence is refused without overwriting; arbitrary non-cooperating editors are not claimed to be transactionally serialized.
- [ ] AC-004: All current creation callers and generated guidance consume returned native identities/paths and use owning-operation resume. Obsolete manual row-creation and PRD-only resume instructions are removed without leaving a second fallback convention.
- [ ] AC-005: Instructions retain user approval gates, full-absolute-path handoff links and trust in successful commands; research/non-native artifacts and historical missing rows are not falsely described as automatically indexed.
- [ ] AC-006: Canonical CLI knowledge and generated projections describe the exercised behavior consistently. The real documented create/resume/finish sequence works without a manual index edit or administrative validation round-trip.

## Implementation and Verification

1. Reuse Story 001's implemented contract; inspect lock ownership and current finish index updates. Pin one fixed review baseline before this Story's source changes.
2. TDD through existing creation/work-record/finish suites: preserve both writers' changes, observe actual status transitions and retain representative refusal/receipt behavior. Test outcomes, not lock calls or copied prose.
3. Acquire the existing creation lock only around finish index updates, with a clear lock-owned helper convention and unchanged completion order.
4. Migrate every native-index caller/reference and the canonical CLI invariant note only after native behavior is exercised. Retain manual handling solely where the command does not own the artifact.
5. Smoke the actual documented creation, interruption/resume and finish path on governed disposable fixtures. Use outputs directly; do not add confirmation-only checks.
6. Integrate related note edits under one writer and regenerate the canonical Skill Pair through the normal publication path. Capture actual observations and independent revision-bound Standards/Spec review before native completion.

## Routine Decision

The existing independent [no-action routine disposition](../../../../specs/skill-proposals/2026-10-23-native-cli-routine-decision.md) was approved by the user and reviewed with this implementation family. Reuse the existing CLI/lock ownership; no routine extraction, publication, router change or new authority follows from classification. The routine gate remains enabled.

## Technical Notes and Boundaries

- Native finish owns completion logging, existing-row status changes and final receipt-derived STATUS. Do not duplicate those writes or refresh STATUS after successful finish.
- Story 001 owns deterministic creation/recovery. This Story must not silently widen that reservation contract while integrating finish.
- [Story 003](story-003.md) owns fingerprint instructions. Shared CLI/reference/note edits have one integration owner and are reconciled, not concurrently overwritten.
- A matching fingerprint is not enough for excluded record context; existing context/scope review remains required.
- Integration exposed a pre-existing read-only violation in the explicit-writer fingerprint path: ordinary Git status refreshed .git/index. The shared changed-path reader now disables optional refresh, without changing its payload, exclusions, or fingerprint algorithm. The completed Story003 record remains immutable; its existing byte-preservation test was strengthened with stale Git stat metadata and caller-enabled optional locks.
- User-approved integration amendment: exactly the canonical Project's `.kosmic/create.lock` is command-owned finish output and excluded from the digest only for same-root Projects. Other `.kosmic/` data and an external Project's writer-local lock remain bound. The approved Architecture/PRD/Epic and current usage guidance record this narrow change; completed Story003 and historical pins remain untouched.

## Completion

Require all AC observations, related-note/projection consistency, applicable routine decisions, actual CLI smoke, converged independent review and native completion receipt. Run the affected integrated suite after changes stabilize; rerun only for changed inputs or failures. No evidence sidecar, optional-suggestion scope growth or hand-written `done`.

Story001's receipt satisfied the dependency and the writer started clean at d375e013e54171efd95fff573b42dbb1e99434b1. Native locking, divergence, creation/recovery/finish and read-only preparation smokes passed. After the user-approved exact creation-lock metadata amendment, all805 integrated tests passed in185.962s. CreationStandardsScout and CreationSpecResume approved the first complete two-axis pair and independently accepted INT-001 as fixed on source pin79779e39581772774447299c0d0273394e2108a0a6595b402c15f3bb6a5512f6. An abandoned duplicate worker test scaffold was removed, not shipped; both reviewers confirmed the final binding. Non-blocking advisories remain recorded without scope growth. Native completion publication is the remaining lifecycle transition.
