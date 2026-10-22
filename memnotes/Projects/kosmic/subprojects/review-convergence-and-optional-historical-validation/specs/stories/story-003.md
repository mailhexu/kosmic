---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: done
record_kind: "story"
local_id: "003"
created: 2026-10-22
updated: 2026-10-22
linked_epic: ../epics/epic-002.md
linked_architecture: ../architecture.md
linked_prd: ../prd.md
related_notes: [notes/cli-projection-commands.md]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_round: 1
review_base: "f1facf01bd779954443cb9419f72e161709d3c89"
completion_observations:
  - criterion: "AC1: Given a ledger row closed before this change with only legacy fields (`status: resolved` or risk-accepted annotations, no `worker_response`/`resolution`), when `finish` or `check-completion` validates the record, then validation passes unchanged with no retroactive field required and no new hash schema introduced."
    observation: "The actual CLI accepted an unannotated resolved legacy row at check-completion and finish and published a receipt. The existing risk-accepted and completion guards passed in the 30-test focused module; standalone legacy rows without annotation/id requirements also stayed accepted."
    source: "PYTHONPATH=tests python -B -m unittest -v test_unified_finish_completion; disposable annotation-smoke.py and annotation-types-smoke.py under the Story 003 managed run"
  - criterion: "AC2: Given a supplied `worker_response` with `kind: fixed` or `refuted` but empty `detail` or empty `evidence`, when completion validation runs, then it fails with a structural error naming the finding and the incoherence, at the `finish`/`check-completion` seam."
    observation: "Red: malformed annotation reached generic unresolved-Blocking errors and standalone check-completion returned 0. After the fix, both actual commands refused the empty-detail A-1 claim with REVIEW_INVALID naming the finding; twelve malformed type/null/whitespace cases were also refused without a receipt."
    source: "Observed red selection; focused module 30 tests OK; actual CLI annotation-smoke.py and annotation-types-smoke.py"
  - criterion: "AC3: Given a supplied `worker_response` with `kind: blocked`, when completion validation runs, then it is accepted only when both a prerequisite and an escalation rationale/evidence are present, and rejected otherwise."
    observation: "Missing prerequisite/escalation fields were refused by the focused CLI regressions. A complete blocked annotation passed standalone annotation validation, but finish still refused the unresolved Blocking B-1 row and published no receipt."
    source: "test_blocked_response_requires_prerequisite_and_escalation; actual CLI blocked-prerequisite smoke scenario"
  - criterion: "AC4: Given a finding carrying a complete `worker_response: fixed` whose `status` is still open, when `finish` is invoked, then the row remains Blocking and finish is refused — a worker response alone never closes a finding."
    observation: "The actual fixed-claim-still-open scenario returned REVIEW_INVALID for unresolved Blocking F-1, with no receipt. The corresponding permanent consumer regression passed."
    source: "annotation-smoke.py fixed-claim-still-open; test_worker_response_fixed_leaves_finding_blocking"
  - criterion: "AC5: Given reviewer closure using existing `status: resolved` with optional `resolution: fixed|refuted`, when completion validation runs, then it is accepted; `resolution` supplied on a non-resolved row is rejected as incoherent, and a refutation rationale/judgment retained on the row remains inspectable."
    observation: "Fresh fixtures accepted fixed and refuted resolution on resolved rows and retained the refutation rationale. An open-row resolution, which incorrectly finished during red, was refused after the fix; the actual accepted-refutation smoke passed check-completion and finish."
    source: "test_resolved_row_accepts_resolution_fixed; test_resolved_row_accepts_resolution_refuted; test_resolution_on_open_row_refuses; annotation-smoke.py"
  - criterion: "AC6: Given existing strict proof, scope, review-domain precedence, freshness, receipt and `source_revision` semantics, when any annotation is present, then none of those gates are relaxed or reordered and no new receipt/repin/backfill behavior is triggered."
    observation: "All 30 focused completion tests passed, including existing proof/scope/review/domain/freshness guards. Read-only check-completion preserved record bytes; refused finish scenarios created no receipt. Changes add annotation checks without granting closure or rewriting historical proof."
    source: "PYTHONPATH=tests python -B -m unittest -v test_unified_finish_completion; actual CLI smoke; fixed-base review of the declared source delta"
completion_review:
  reviewer: Main
  axes:
    standards: {decision: approved, reviewer: Review003Standards-2}
    spec: {decision: approved, reviewer: Review003Spec-2}
  decision: approved
  review_base: "f1facf01bd779954443cb9419f72e161709d3c89"
  reviewed_revision: "d586d7b83966b817f32069029d57c918243ffe030848c730b9c65331b239d912"
  findings: []
  scope:
    - worktree:skills/scripts/kosmic_completion.py
    - worktree:skills/scripts/kosmic_project_skills.py
    - worktree:tests/test_unified_finish_completion.py
---

# Story 003: Compatible finding-response and refutation annotations

## User Story

As a kosmic worker finishing work under an approved Epic,
I want optional per-finding `worker_response` annotations validated for shape and coherence at the native completion seam,
So that complete fixed/refuted/blocked claims are inspectable while worker claims never close findings and old closed rows stay valid unchanged.

## Scope

### In Scope

- Optional `finding.worker_response` (`kind: fixed|refuted|blocked` with detail/evidence; `blocked` carries prerequisite + escalation rationale) validated for shape/coherence in `kosmic_completion.py` (`_checked_review` and the completion reference path) at the native `finish` / `check-completion` consumer seam.
- Reviewer-only closure via existing `status: resolved`, optionally `resolution: fixed|refuted`; rejected refutation remains open/Blocking with finding and rationale retained.
- Backward compatibility: old closed rows and existing `risk-accepted` fields remain valid with no retroactive fields.
- Genuine consumer-contract knowledge refresh (including a coherent native projection refresh of a published note in the same episode if its content changes).

### Out of Scope

- New finding statuses, resolver/version/hash fields, authority over worker claims, or any new hash schema.
- The coordinator barrier/handoff protocol and reference-doc refresh (Story 004).
- New CLI commands; changes to existing strict proof/scope/review/domain precedence and freshness gates; changes to routine edges or registered reusable mechanics.

### Owned Files

- `skills/scripts/kosmic_completion.py` (annotation/resolution validation in `_checked_review` and completion reference assembly)
- `skills/scripts/kosmic_project_skills.py` (the standalone `_check_existing_completion` annotation-only hook; actual CLI smoke exposed this distinct consumer seam)
- `tests/test_unified_finish_completion.py` (new red-first tests for annotation coherence; existing guards reused, not duplicated)
- `notes/cli-projection-commands.md` and any affected consumer knowledge/projection outputs, refreshed in this same episode if and only if their content genuinely changes

## Acceptance Criteria

- [x] AC1: Given a ledger row closed before this change with only legacy fields (`status: resolved` or risk-accepted annotations, no `worker_response`/`resolution`), when `finish` or `check-completion` validates the record, then validation passes unchanged with no retroactive field required and no new hash schema introduced.
- [x] AC2: Given a supplied `worker_response` with `kind: fixed` or `refuted` but empty `detail` or empty `evidence`, when completion validation runs, then it fails with a structural error naming the finding and the incoherence, at the `finish`/`check-completion` seam.
- [x] AC3: Given a supplied `worker_response` with `kind: blocked`, when completion validation runs, then it is accepted only when both a prerequisite and an escalation rationale/evidence are present, and rejected otherwise.
- [x] AC4: Given a finding carrying a complete `worker_response: fixed` whose `status` is still open, when `finish` is invoked, then the row remains Blocking and finish is refused — a worker response alone never closes a finding.
- [x] AC5: Given reviewer closure using existing `status: resolved` with optional `resolution: fixed|refuted`, when completion validation runs, then it is accepted; `resolution` supplied on a non-resolved row is rejected as incoherent, and a refutation rationale/judgment retained on the row remains inspectable.
- [x] AC6: Given existing strict proof, scope, review-domain precedence, freshness, receipt and `source_revision` semantics, when any annotation is present, then none of those gates are relaxed or reordered and no new receipt/repin/backfill behavior is triggered.

## Tasks

### Phase 1: Research

- [x] Read the findings loop and completion assembly; finish/bound completion use `_checked_review`, while standalone completion needed its own annotation-only hook.
- [x] Confirm legacy closed-row/risk-accepted compatibility through existing fixtures and actual CLI smoke.
- [x] Pin the clean-writer baseline before source edits: `f1facf01bd779954443cb9419f72e161709d3c89`.
- [x] Baseline guards: the unchanged 21-test module passed on the clean baseline snapshot; executed during verification rather than before edits. New-behavior red was observed before implementation, then the final 30-test module passed.

### Phase 2: Tests (TDD — red-first only for NEW annotation-coherence behavior, against the real `finish`/`check-completion` seam)

- [x] TEST-001: `fixed`/`refuted` response with empty detail or evidence is rejected with a naming error.
- [x] TEST-002: `blocked` response without prerequisite or escalation rationale is rejected; complete form passes annotation validation but never closes an open Blocking finding.
- [x] TEST-003: worker-response-only finding stays Blocking and `finish` refuses.
- [x] TEST-004: `resolved` + optional `resolution: fixed|refuted` accepted; `resolution` on an open row rejected.
- Legacy closed-row compatibility (AC1) and existing proof/freshness/receipt behavior (AC6) are protected by the existing passing guards in `tests/test_unified_finish_completion.py` and related suites — reused as-is, never duplicated or forced red — plus the actual CLI smoke below.

### Phase 3: Implementation

- [x] IMPL-001: implement shared optional-annotation validation at finish and standalone completion, preserving final gate precedence and existing closure semantics.
- [x] IMPL-002: update the durable Usage invariant and regenerate the canonical Skill Pair in the same episode.

### Phase 4: Review

- [x] Actual smoke: run real `finish`/`check-completion` for legacy closure, accepted refutation, incomplete claim, still-open fixed claim and blocked prerequisite; additionally refuse twelve malformed annotation type cases.
- [x] Independent fixed-base Standards and Spec axes approved Round 1 over the identical held record/source/acceptance payload, with an empty findings ledger. Native `work finish` is the sole completion publisher.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed. This story adds ordinary private Project validation/reporting inside kosmic's own completion seam and caller-facing guidance for it; it does not compile any routine, add `uses_routines` edges, or alter registered reusable mechanics. If implementation turns out to change routine edges or registered reusable mechanics, that scope must be updated and reapproved rather than silently expanded.

## Technical Notes

- Known facts: architecture ADR-003 fixes the encoding (`worker_response.kind: fixed|refuted|blocked`; non-empty detail+evidence for fixed/refuted; blocked carries prerequisite + escalation). Reviewer acceptance uses existing `status: resolved`, optionally `resolution: fixed|refuted`; no `refuted` status; no retroactive resolver/version/identity/hash fields.
- Worker response is a claim; reviewer resolution is the decision. Validation is structural, never authentication of the agent process.
- CLI conventions: [Development conventions](../../../../notes/cli-extension-conventions.md) apply to any error-message shape; the [CLI projection commands](../../../../notes/cli-projection-commands.md) note is the related consumer surface.
- `review_base` was pinned before implementation. Explicit null is supplied-but-invalid for the new annotation keys; absent keys remain a no-op. Standalone completion validates annotations without demanding modern proof, a stable finding ID or reviewer closure from legacy rows.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Finish and standalone completion share one entry seam | Corrected | Actual CLI initially exposed standalone acceptance of malformed annotation; both paths now reuse the annotation validator |
| Legacy closed/risk-accepted rows need no new fields | Verified | Existing guards plus actual legacy CLI smoke |
| Existing completion guards remain green | Verified | Original module 21 tests OK; final module 30 tests OK |

## Definition of Done

- [x] All acceptance criteria met
- [x] Tests pass (new tests written first; no existing guard forced red)
- [x] Fixed-base Standards + Spec review completed within round cap
- [x] Knowledge/projection refreshed only where genuinely changed
- [x] No regressions observed in the focused completion guards and actual consumer smoke; integrated suite follows after all four slices stabilize.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-22 | Created | Initial draft (approved Epic 002) |
| 2026-10-22 | Approved → implemented | User approved all four Stories; observed red, repaired incomplete worker handoffs before review, then 30 focused tests and public CLI/type smokes passed. Independent review pending. |
| 2026-10-22 | Round 1 approved | Review003Standards-2 and Review003Spec-2 approved independently; empty ledger; source and full record/consumer-note context unchanged across the pair. |
| 2026-10-22 | Completion phase corrected | Native finish refused `review` as unsupported. Retained `in_progress` with the approved review decision unchanged; no source, acceptance, proof or authority gate changed. Story 004 aligns coordinator guidance to this existing runtime contract. |
