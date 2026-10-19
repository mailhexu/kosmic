---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: "draft"
record_kind: "story"
local_id: "001"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
related_notes: ["notes/cli-projection-commands.md"]
created: 2026-10-19
updated: 2026-10-19
consumer_interface_change: true
---

# Story 001: Unified Safe Completion and Immutable Retry

## User Story

As an agent or operator finishing authorized work,
I want one ordinary `work finish` invocation to run every currently required completion gate — embedded proof, primary scope (`SCOPE_DENIED` first), reviewed scope/source binding, the complete shared read-only domain precheck, and last-moment freshness rechecks — and terminal retries to verify only the unchanged receipt record and its immutable originals plus the declared formal contracts,
so that completion is safe by default and idempotent without re-blessing drifted bytes, mutable re-verification, or a second choreographed command.

Covers FR-002 as exercised by these invocations, FR-003, FR-004, and this Story's FR-012 cutover slice. ADR-B and ADR-C are binding; ADR-A authority semantics are consumed as given (no redesign). No prefill, workflow-policy/delegation, or measurement ownership; this Story has no depends_on.

## Acceptance Criteria

- [ ] AC1: Given a qualifying feature Story with all gates satisfiable, when one ordinary `python3 skills/scripts/kosmic_project_skills.py work finish --project ... --worktree ... --work-record ... --scope ...` runs, then every applicable completion gate is exercised in the normative order and the existing publication order record done → indexes → completion log → receipt → derived STATUS completes with the current CLI JSON receipt schema returned unchanged.
- [ ] AC2: Given injected invalid dependency, retired-input, missing `consumer_interface_change`, unstable/missing related note, projection, STATUS-drift, or math/proposal/routine state, when `work finish` runs, then it refuses before any publication — record not done, no receipt file — for each gate individually.
- [ ] AC3: Given a domain failure inside the shared precheck, when finish rejects, then the public error is `COMPLETION_PRECHECK_FAILED` retaining the original diagnostic and cause; existing authority/scope/proof/review codes (`RECORD_NOT_AUTHORIZED`, `WORK_PHASE_DENIED`, `ACCEPTANCE_INVALID`, `RETIRED_INPUT`, `SCOPE_DENIED`, `REVIEW_INVALID`, `COMPLETION_PENDING`, `COMPLETION_DRIFT`) are unchanged; a missing or unreadable Project config is reported, not swallowed, on this finish path.
- [ ] AC4: Given mis-scoped finish claims plus independently invalid review evidence, when finish runs, then `SCOPE_DENIED` is raised before review validation is consulted, the domain precheck runs after proof/scope/review so its diagnostics never mask them, and no receipt exists until every gate has passed.
- [ ] AC5: Given changed record bytes, a changed `source_revision` binding, or stale mid-episode identity/ancestry/scope/approval authority introduced after the gates ran, when the immediate-before-write freshness rechecks observe it, then the invocation rejects with no partial publication — no atomicity is promised and the caller reruns.
- [ ] AC6: On the terminal route, ordinary linked-note/data evolution and review-base aging leave a valid receipt valid — no mutable note/data rehash, no current dirty-source review rehash, no pin refresh — while tampered record bytes, missing/changed immutable originals, or failing declared formal math/proposal/routine checks reject the retry.
- [ ] AC7: Given a present but unreadable or inconsistent receipt, when finish runs, then it rejects (`COMPLETION_PENDING`/`COMPLETION_DRIFT`) without re-blessing, repinning, or falling through to a fresh completion attempt.
- [ ] AC8: Given an absent receipt, finish enters the full nonterminal path so an interrupted pre-receipt or unreceipted-done episode recovers only by rerunning every gate (never conflated with terminal success); a valid retry returns the receipt and completion log bytes unchanged and repairs only derived STATUS, and legacy inputs are honored solely through the terminal historical route's byte-verified recorded originals.
- [ ] AC9: At cutover, the current docs, CLI guidance, examples, and consumer contracts describing finish/completion match the landed behavior coherently, and historical receipt/pin bytes are untouched.

## Tasks

### Research (before implementing)

- [ ] Read [PRD](../prd.md) FR-002/003/004/012, [Architecture](../architecture.md) ADR-B/ADR-C (ADR-A as given), and [Epic 001](../epics/epic-001.md) scope; survey the current `finish_work` terminal/full paths, `check_done_record_gates`/`check_completion_gates`, `check_completion`'s plain-done formal block, `_check_existing_completion` gates, `validate_receipt_payload` current-vs-legacy binding, and the `kosmic_work` authority contract (`resolve_work_record`, `_ancestry_approved`, `check_record_changes`) — touch `kosmic_work.py` only if that contract requires.
- [ ] Classify routine mechanics and reuse under the existing Task 9 / Task P triggers; record the classification and any interface decisions in Technical Notes; no forced proposal and no canonical skill edit.
- [ ] Write failing-first regression tests for the changed completion behavior; retain passing guard/legacy tests without forcing them to fail (behavior only: no source-text, import, wiring, or call-count assertions).

### Tests (verification-first)

- [ ] TEST-001: unified single-invocation success (AC1) and each AC2 gate refusal leaving record not-done and no receipt; standalone `check-completion` stays diagnostic/fail-fast.
- [ ] TEST-002: precedence and translation — `SCOPE_DENIED` over review validation, precheck-after-review ordering, `COMPLETION_PRECHECK_FAILED` cause retention, retained codes, config-not-swallowed (AC3/AC4).
- [ ] TEST-003: freshness drift (record bytes, `source_revision`, authority) detected at the pre-write recheck (AC5).
- [ ] TEST-004: terminal invariance — evolution-tolerant retry vs record/original tampering and formal math/proposal/routine failure, invalid-receipt rejection, absent-receipt full recovery, retry receipt/log byte-invariance with STATUS-only repair, legacy terminal-historical route (AC6–AC8); the same formal checks hold through both `check-completion` entry modes.

### Implementation

- [ ] IMPL-001: extend `finish_work` in `skills/scripts/kosmic_completion.py` — terminal route first (fresh identity/approved ancestry, receipt validation, shared terminal formal helper, STATUS-only repair); absent-receipt fall-through: `validate_completion_proof` → primary `check_record_changes` scope (`SCOPE_DENIED` precedence) → `_checked_review` reviewed scope/`source_revision`/fixed-base review → complete shared readonly precheck via the established deferred import calling `kosmic_project_skills._check_existing_completion(project, record.path, source_root=worktree, record_scoped=True, record_owner=record.subproject_id)` — not a recursive CLI call — with `KosmicError` translated to `WorkdirError("COMPLETION_PRECHECK_FAILED", …)` keeping the original cause; then record/source/authority freshness rechecks immediately before the unchanged publication sequence.
- [ ] IMPL-002: in `skills/scripts/kosmic_project_skills.py`, extract the shared terminal formal helper (`load_math_registry` restricted to the record's `derivations` + `_check_math_proposal_routine_gates`) used identically by the plain done path and the finish terminal route; public `finish_work` signature and CLI JSON unchanged.
- [ ] IMPL-003: FR-012 slice — update current docs, CLI guidance, examples, and consumer contracts coherently with landed behavior; shared runtime/docs files get one integration owner, not concurrent blind edits; scoped managed scratch is removed after the smoke; no live/global vault or install changes.

### Review / Completion

- [ ] Real throwaway CLI smoke of `work finish` on managed scratch (success plus refusal cases), removed afterward; integrated verification runs once affected changes are stable, rerunning changed/failed inputs; scientific validation never skipped.
- [ ] User approval before implementation; fixed-base two-axis independent review with the existing max-3 findings ledger; successful receipted `work finish`; final human handoff repeats the full absolute Story path link.

## Routine Decision

Not asserted at draft: `proposal_required`/`routine_decision_required` are set only from observed Research, never assumed unchanged. Research classifies the unified gate order, precheck reuse, and shared formal helper against the existing Task 9 / Task P triggers during implementation; any routine/proposal outcome follows those triggers. This plan forces no proposal and no canonical skill edit.

## Technical Notes

- Frozen surface: `finish_work(project_root, worktree, record_ref, scope, *, detail="") -> dict` and the `work finish` CLI receipt JSON; receipts keep the `{record_path: record_sha256}` binding; historical receipts byte-verify only their recorded immutable originals and are never repinned or re-blessed.
- The precheck is the same helper standalone `check-completion` uses, so finish and the diagnostic stay one implementation; unlike the tolerant STATUS-candidate enumeration, the finish precheck path does not swallow a missing/unreadable Project config.
- The terminal route never re-hashes evolving notes/data, never recomputes the current dirty-source review binding, never refreshes historical pins, and applies the declared formal checks exactly as the plain done path so both check-completion entry modes agree.
- The only new public error code is `COMPLETION_PRECHECK_FAILED`; the nonterminal precheck never auto-repairs stale STATUS/projections or refreshes pins. Valid terminal retry still repairs derived STATUS only. No path automatically rebinds a changed record/source.
- Empty `completion_observations` and review metadata is correct at draft; they are filled only by real exercised outcomes, never fabricated.

## Definition of Done

- Every AC exercised through the applicable real CLI/API path; no source-text, import, wiring, or incidental-wording tests.
- New regression tests demonstrate changed behavior failing before and passing after; existing safety guards remain green, with changed or previously failed inputs rerun once stable.
- Actual throwaway CLI smoke performed and its scratch removed; runtime-change claims grounded in observed behavior, not test passes alone.
- User approval before implementation; fixed-base two-axis review approved under the max-3 ledger; successful `work finish` receipt; final handoff links the full absolute Story path again; docs/contracts coherent at cutover with historical bytes untouched.
