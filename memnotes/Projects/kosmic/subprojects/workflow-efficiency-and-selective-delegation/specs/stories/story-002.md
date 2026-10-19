---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: "draft"
record_kind: "story"
local_id: "002"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
consumer_interface_change: true
related_notes: ["notes/cli-projection-commands.md"]
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

- [ ] AC1: The real `work prepare-completion --project P --work-record R` CLI prints JSON with the record `identity`, the canonical `record_path`, and `completion_observations` listing every criterion's exact text in canonical record order.
- [ ] AC2: Each exact-matched authored entry is preserved field-for-field, including adverse findings; a criterion with no authored entry yields a blank observation/source draft, and `work finish` still rejects that incomplete draft.
- [ ] AC3: Wrong kind, status, identity, or ancestry is refused at invocation — non-story/quick-task records, completed or terminal records, and unapproved or non-descendant records fail with the existing authorization error codes.
- [ ] AC4: Missing acceptance criteria, duplicated or ambiguous criterion text, and unknown, duplicate, or structurally malformed authored mappings are each rejected; an absent authored entry is reported as a blank draft, never as a mapping error.
- [ ] AC5: The command is read-only: before/after byte snapshots over the Project prove no record, index, log, receipt, STATUS, or sidecar write; no `--write` mode exists; no outcome, reviewer, or approval field is generated; the machine receipt schema is unchanged.
- [ ] AC6: An actual CLI smoke in an isolated authorized fixture applies the prefilled draft and shows the incomplete finish failing, leaving no durable extra artifacts; the consumer note, guidance, command-reference examples, and contracts match the shipped behavior.

## Tasks

### Research

- [ ] Confirm the validator's `## Acceptance Criteria` checkbox-scan semantics and `resolve_work_record` authorization (kinds, statuses, approved ancestry) for unchanged reuse.
- [ ] Inventory the FR-012 surfaces for this behavior (consumer note, `record_first_contract` guidance, command reference, examples, contracts) and declare one integration owner per shared file with Stories 001/003.
- [ ] Classify the landed surface under the existing Task 9/P triggers; no proposal is forced and no canonical skill is edited by default.
- [ ] Obtain explicit user approval of this draft Story, then pin a review base in a clean dedicated worktree before any source write.

### Test-first verification

- [ ] Add failing-before behavioral regressions for the new prefill behaviors only — canonical order and exact text, authored-field preservation with adverse findings, blank-draft entries, every mapping and authorization refusal, and byte-identical no-write proof; existing passing safety tests are not modified to fail.
- [ ] After affected changes stabilize, rerun the changed and previously failed inputs/contracts and keep scientific validation in scope; never reuse a pass over changed inputs.

### Implementation

- [ ] Factor the criterion scan into the shared completion helper and build prefill on that one parsing rule — no second convention, new module, error code, or artifact.
- [ ] Add the `work prepare-completion` parser and dispatch reusing live record resolution; no work start, no worktree argument, no permission caching.
- [ ] Cut over this behavior's docs coherently: consumer-note invariant, guidance line, command-reference flags/examples, and contract tests.

### Review and Completion

- [ ] Exercise the real CLI smoke — apply the prefilled blank draft in the isolated authorized fixture, observe the incomplete finish rejection, then remove scoped scratch.
- [ ] Complete fixed-base independent Standards/Spec review under the existing max-3 ledger and integrate shared-file edits with the declared owner.
- [ ] Finish through the checked `work finish` path for the successful receipt and repeat the full absolute Story path link in the final human handoff.

## Routine Decision

Research classifies the actual mechanics under the existing Task 9/P
triggers before implementation; `proposal_required` and
`routine_decision_required` are not asserted here. Any required decision is
recorded in this Story, with no forced proposal or direct canonical skill edit.

## Technical Notes

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

- [ ] Every acceptance criterion passes through real CLI behavior, including the isolated apply-draft smoke with no durable extra artifacts.
- [ ] Consumer note, guidance, command-reference examples, and contracts match the shipped prefill behavior.
- [ ] Independent two-axis review on the pinned base leaves no unresolved Blocking, High, or Medium finding.
- [ ] The Story completes through the checked finish path with a successful receipt.
