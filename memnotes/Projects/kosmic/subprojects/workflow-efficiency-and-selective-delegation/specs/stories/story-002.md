---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: done
record_kind: "story"
local_id: "002"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
consumer_interface_change: true
related_notes: ["notes/cli-projection-commands.md"]
review_base: "f0d281d76342cbf741fc6633fe94418f4e039921"
review_round: 2
completion_review:
  reviewer: "Main"
  axes:
    standards:
      decision: "approved"
      reviewer: "EfficiencyStandardsR1"
    spec:
      decision: "approved"
      reviewer: "EfficiencySpecR1"
  decision: "approved"
  review_base: "f0d281d76342cbf741fc6633fe94418f4e039921"
  reviewed_revision: "206bfcfab92827484f9a41679d529c45ed6999f09bed1c6de7c64468baf51314"
  findings:
    - id: "SPEC-001"
      axis: "spec"
      disposition: "Blocking"
      introduced_round: 1
      status: "resolved"
      evidence: "prepare_completion validates criterion but returns non-text observation/source fields; Story 002 AC4 requires malformed authored mappings to be rejected."
      required_resolution: "Require authored observation/source fields to have text structure; preserve authored text and extra fields, and blank drafts for absent entries."
      resolution: "Required string structure added; red CLI regression failed before fix; seven merged CLI cases and affected real S1 passed after fix; EfficiencySpecR1 verified resolution in Round2."
  scope:
    - "worktree:skills/scripts/kosmic_completion.py"
    - "worktree:skills/scripts/kosmic_project_skills.py"
    - "worktree:skills/references/task_project_skills.md"
    - "worktree:tests/test_prepare_completion_prefill.py"
    - "project:notes/cli-projection-commands.md"
    - "project:skills/"
    - "project:subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-002.md"
    - "worktree:memnotes/Skills/"
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
completion_observations:
  - criterion: "AC1: The real `work prepare-completion --project P --work-record R` CLI prints JSON with the record `identity`, the canonical `record_path`, and `completion_observations` listing every criterion's exact text in canonical record order."
    observation: "The native read-only command ran against all four real approved/in-progress Stories and returned their qualified identities, canonical paths and 9/6/8/8 criteria in source order; each record hash stayed unchanged."
    source: "Native work prepare-completion on actual Stories; pytest tests/test_prepare_completion_prefill.py (7 passed); post-fix actual S1; Round2 SPEC-001 review."
  - criterion: "AC2: Each exact-matched authored entry is preserved field-for-field, including adverse findings; a criterion with no authored entry yields a blank observation/source draft, and `work finish` still rejects that incomplete draft."
    observation: "CLI regressions and actual S1 preserved authored adverse/extra fields and blank drafts. Applying the returned blank draft then finishing failed ACCEPTANCE_INVALID, with no receipt."
    source: "Native work prepare-completion on actual Stories; pytest tests/test_prepare_completion_prefill.py (7 passed); post-fix actual S1; Round2 SPEC-001 review."
  - criterion: "AC3: Wrong kind, status, identity, or ancestry is refused at invocation — non-story/quick-task records, completed or terminal records, and unapproved or non-descendant records fail with the existing authorization error codes."
    observation: "Public CLI tests refused done/draft records and unknown identities using the existing authorization paths. Real Story preparation resolved approved owner-local ancestry; no authority token or cached permission was issued."
    source: "Native work prepare-completion on actual Stories; pytest tests/test_prepare_completion_prefill.py (7 passed); post-fix actual S1; Round2 SPEC-001 review."
  - criterion: "AC4: Missing acceptance criteria, duplicated or ambiguous criterion text, and unknown, duplicate, or structurally malformed authored mappings are each rejected; an absent authored entry is reported as a blank draft, never as a mapping error."
    observation: "SPEC-001 was reproduced as malformed list-valued observation acceptance, then corrected. Seven merged CLI tests passed, covering list/dict/int/null/missing text fields, unknown/duplicate mappings and criteria, while authored blank strings and absent-entry blank generation remained valid."
    source: "Native work prepare-completion on actual Stories; pytest tests/test_prepare_completion_prefill.py (7 passed); post-fix actual S1; Round2 SPEC-001 review."
  - criterion: "AC5: The command is read-only: before/after byte snapshots over the Project prove no record, index, log, receipt, STATUS, or sidecar write; no `--write` mode exists; no outcome, reviewer, or approval field is generated; the machine receipt schema is unchanged."
    observation: "Before/after Project snapshots and real-record hashes proved preparation writes nothing. The command has no write/worktree mode and generates no reviewer, approval or result claims; receipt JSON is unchanged."
    source: "Native work prepare-completion on actual Stories; pytest tests/test_prepare_completion_prefill.py (7 passed); post-fix actual S1; Round2 SPEC-001 review."
  - criterion: "AC6: An actual CLI smoke in an isolated authorized fixture applies the prefilled draft and shows the incomplete finish failing, leaving no durable extra artifacts; the consumer note, guidance, command-reference examples, and contracts match the shipped behavior."
    observation: "Post-fix actual S1 performed one clean start, applied the exact returned draft and observed incomplete-finish refusal with no receipt. Native publication refreshed the existing consumer note/pair/library; the updated hash-pinned CLI guideline loaded successfully."
    source: "Native work prepare-completion on actual Stories; pytest tests/test_prepare_completion_prefill.py (7 passed); post-fix actual S1; Round2 SPEC-001 review."
---

# Read-Only Criterion Prefill

## User Story

As an implementer finishing authorized work, I want a read-only
`work prepare-completion` command that returns each acceptance criterion
verbatim from the governing record together with its authored observations,
so that manual exact copying disappears without generating any outcome,
reviewer, or approval claim.

## Scope

Implements ADR-D (FR-005) and this Story's FR-012 slice: the shared criterion
parser/helper in `kosmic_completion.py`, the `work prepare-completion` parser
and dispatch in `kosmic_project_skills.py`, and the consumer note, guidance,
examples, and contracts for this behavior. No finish-engine or workflow-policy
change, no new artifact class, and no semantic dependency on Story 001; shared
runtime/docs files declare one integration owner before edits.

## Acceptance Criteria

- [x] AC1: The real `work prepare-completion --project P --work-record R` CLI prints JSON with the record `identity`, the canonical `record_path`, and `completion_observations` listing every criterion's exact text in canonical record order.
- [x] AC2: Each exact-matched authored entry is preserved field-for-field, including adverse findings; a criterion with no authored entry yields a blank observation/source draft, and `work finish` still rejects that incomplete draft.
- [x] AC3: Wrong kind, status, identity, or ancestry is refused at invocation — non-story/quick-task records, completed or terminal records, and unapproved or non-descendant records fail with the existing authorization error codes.
- [x] AC4: Missing acceptance criteria, duplicated or ambiguous criterion text, and unknown, duplicate, or structurally malformed authored mappings are each rejected; an absent authored entry is reported as a blank draft, never as a mapping error.
- [x] AC5: The command is read-only: before/after byte snapshots over the Project prove no record, index, log, receipt, STATUS, or sidecar write; no `--write` mode exists; no outcome, reviewer, or approval field is generated; the machine receipt schema is unchanged.
- [x] AC6: An actual CLI smoke in an isolated authorized fixture applies the prefilled draft and shows the incomplete finish failing, leaving no durable extra artifacts; the consumer note, guidance, command-reference examples, and contracts match the shipped behavior.

## Tasks

### Research

- [x] Confirm the validator's `## Acceptance Criteria` checkbox-scan semantics and `resolve_work_record` authorization (kinds, statuses, approved ancestry) for unchanged reuse.
- [x] Inventory the FR-012 surfaces for this behavior (consumer note, `record_first_contract` guidance, command reference, examples, contracts) and declare one integration owner per shared file with Stories 001/003.
- [x] Classify the landed surface under the existing Task 9/P triggers; no proposal is forced and no canonical skill is edited by default.
- [x] Obtain explicit user approval of this draft Story, then pin a review base in a clean dedicated worktree before any source write.

### Test-first verification

- [x] Add failing-before behavioral regressions for the new prefill behaviors only — canonical order and exact text, authored-field preservation with adverse findings, blank-draft entries, every mapping and authorization refusal, and byte-identical no-write proof; existing passing safety tests are not modified to fail.
- [x] After affected changes stabilize, rerun the changed and previously failed inputs/contracts and keep scientific validation in scope; never reuse a pass over changed inputs.

### Implementation

- [x] Factor the criterion scan into the shared completion helper and build prefill on that one parsing rule — no second convention, new module, error code, or artifact.
- [x] Add the `work prepare-completion` parser and dispatch reusing live record resolution; no work start, no worktree argument, no permission caching.
- [x] Cut over this behavior's docs coherently: consumer-note invariant, guidance line, command-reference flags/examples, and contract tests.

### Review and Completion

- [ ] Exercise the real CLI smoke — apply the prefilled blank draft in the isolated authorized fixture, observe the incomplete finish rejection, then remove scoped scratch.
- [x] Complete fixed-base independent Standards/Spec review under the existing max-3 ledger and integrate shared-file edits with the declared owner.
- [ ] Finish through the checked `work finish` path for the successful receipt and repeat the full absolute Story path link in the final human handoff.

## Routine Decision


Research outcome: no Shared Skill Library routine or `uses_routines` edge is created or changed. This approved slice extends the ordinary Project CLI backend or its existing guidance; no Task P proposal trigger was found. The false routine/proposal declarations record that classification, not an exemption from the existing gates. Canonical topics refresh only through the native authorized producer; installed skills stay unchanged.

## Technical Notes

Pre-publication verification: actual CLI exercises and independent Round 2 review are complete. Receipt creation, its final human handoff and managed-scratch finalization are downstream transactions; their checklist rows are deliberately not claimed before publication and the bound record is not edited afterward merely to tick them.

- Output is JSON only — `identity`, canonical `record_path`,
  `completion_observations` — a draft editing aid, never completion proof or
  authorization; applying it is ordinary scoped record editing, and any later
  record/source change invalidates the review binding exactly as today.
- Refusals reuse existing codes (`ACCEPTANCE_INVALID` for criteria/mapping
  defects; `WORK_PHASE_DENIED`/`RECORD_NOT_AUTHORIZED` for authorization), so
  publication order, finish behavior, and the receipt schema stay untouched by
  this Story; STATUS repair on the valid terminal retry route is Story 001's
  surface and is not addressed here.
- Blank observation/source entries are expected draft state, not errors, and
  never count as completion evidence; review/approval/completion metadata
  stays empty until actually exercised.
- Story 001 owns the unified finish route and its docs; Story 003 owns
  workflow-policy guidance — no concurrent blind edits to shared files, and
  integrated verification happens only once affected changes are stable.

## Definition of Done

- [x] Every acceptance criterion passes through real CLI behavior, including the isolated apply-draft smoke with no durable extra artifacts.
- [x] Consumer note, guidance, command-reference examples, and contracts match the shipped prefill behavior.
- [x] Independent two-axis review on the pinned base leaves no unresolved Blocking, High, or Medium finding.
- [ ] The Story completes through the checked finish path with a successful receipt.
