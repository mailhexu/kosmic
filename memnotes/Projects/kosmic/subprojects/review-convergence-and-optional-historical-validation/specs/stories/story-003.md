---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: "approved"
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
review_round: 0
completion_observations: []
completion_review: {}
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
- `tests/test_unified_finish_completion.py` (new red-first tests for annotation coherence; existing guards reused, not duplicated)
- `notes/cli-projection-commands.md` and any affected consumer knowledge/projection outputs, refreshed in this same episode if and only if their content genuinely changes

## Acceptance Criteria

- [ ] AC1: Given a ledger row closed before this change with only legacy fields (`status: resolved` or risk-accepted annotations, no `worker_response`/`resolution`), when `finish` or `check-completion` validates the record, then validation passes unchanged with no retroactive field required and no new hash schema introduced.
- [ ] AC2: Given a supplied `worker_response` with `kind: fixed` or `refuted` but empty `detail` or empty `evidence`, when completion validation runs, then it fails with a structural error naming the finding and the incoherence, at the `finish`/`check-completion` seam.
- [ ] AC3: Given a supplied `worker_response` with `kind: blocked`, when completion validation runs, then it is accepted only when both a prerequisite and an escalation rationale/evidence are present, and rejected otherwise.
- [ ] AC4: Given a finding carrying a complete `worker_response: fixed` whose `status` is still open, when `finish` is invoked, then the row remains Blocking and finish is refused — a worker response alone never closes a finding.
- [ ] AC5: Given reviewer closure using existing `status: resolved` with optional `resolution: fixed|refuted`, when completion validation runs, then it is accepted; `resolution` supplied on a non-resolved row is rejected as incoherent, and a refutation rationale/judgment retained on the row remains inspectable.
- [ ] AC6: Given existing strict proof, scope, review-domain precedence, freshness, receipt and `source_revision` semantics, when any annotation is present, then none of those gates are relaxed or reordered and no new receipt/repin/backfill behavior is triggered.

## Tasks

### Phase 1: Research

- [ ] Read `kosmic_completion.py:_checked_review` (`skills/scripts/kosmic_completion.py:348`) and the completion reference assembly; map exactly where row-level review validation occurs and where incoherence errors are raised today.
- [ ] Confirm the existing accepted closed-row and risk-accepted shapes in current ledgers so compatibility is defined against real data, not assumptions.
- [ ] ACTIVATION (before any edit or review): implementation owner pins the real clean-writer baseline for this story in `review_base` (currently intentionally absent — no placeholder). Review of this story uses that fixed base.
- [ ] Bounded activation check: run the existing completion-focused tests once pre-edit to confirm a green starting point (reuse of existing passing guards; no new tests yet).

### Phase 2: Tests (TDD — red-first only for NEW annotation-coherence behavior, against the real `finish`/`check-completion` seam)

- [ ] TEST-001: `fixed`/`refuted` response with empty detail or evidence is rejected with a naming error.
- [ ] TEST-002: `blocked` response without prerequisite or escalation rationale is rejected; complete form accepted.
- [ ] TEST-003: worker-response-only finding stays Blocking and `finish` refuses.
- [ ] TEST-004: `resolved` + optional `resolution: fixed|refuted` accepted; `resolution` on an open row rejected.
- Legacy closed-row compatibility (AC1) and existing proof/freshness/receipt behavior (AC6) are protected by the existing passing guards in `tests/test_unified_finish_completion.py` and related suites — reused as-is, never duplicated or forced red — plus the actual CLI smoke below.

### Phase 3: Implementation

- [ ] IMPL-001: add shape/coherence validation for optional `worker_response` and `resolution` in `_checked_review`'s row validation, reusing existing `_deny` error style and precedence; no new statuses or fields mandated; supplied response states remain inspectable in the existing ledger surface as-is.
- [ ] IMPL-002: knowledge refresh — update `notes/cli-projection-commands.md` and any affected consumer knowledge/projection outputs only if their documented content genuinely changes; refresh in the same episode.

### Phase 4: Review

- [ ] Actual smoke: run real `finish`/`check-completion` against a scratch Project record containing (a) a legacy closed row and (b) one annotated row, observing accept/refuse behavior.
- [ ] Independent fixed-base Standards review and Spec review against the pinned `review_base`, using the stable ledger, one round per complete pair, max three rounds with a human decision packet at cap; native receipt completion for this story per existing completion gates.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed. This story adds ordinary private Project validation/reporting inside kosmic's own completion seam and caller-facing guidance for it; it does not compile any routine, add `uses_routines` edges, or alter registered reusable mechanics. If implementation turns out to change routine edges or registered reusable mechanics, that scope must be updated and reapproved rather than silently expanded.

## Technical Notes

- Known facts: architecture ADR-003 fixes the encoding (`worker_response.kind: fixed|refuted|blocked`; non-empty detail+evidence for fixed/refuted; blocked carries prerequisite + escalation). Reviewer acceptance uses existing `status: resolved`, optionally `resolution: fixed|refuted`; no `refuted` status; no retroactive resolver/version/identity/hash fields.
- Worker response is a claim; reviewer resolution is the decision. Validation is structural, never authentication of the agent process.
- CLI conventions: [Development conventions](../../../../notes/cli-extension-conventions.md) apply to any error-message shape; the [CLI projection commands](../../../../notes/cli-projection-commands.md) note is the related consumer surface.
- `review_base` is deliberately absent from frontmatter; it is pinned by the implementation owner at activation, before edits and review.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| `_checked_review` is the single row-validation seam for finish/check-completion | ⬜ | Phase 1 research |
| Old ledgers contain closed rows without annotation fields | ⬜ | Phase 1 research |
| Existing completion tests are green pre-edit | ⬜ | Activation check |

## Definition of Done

- [ ] All acceptance criteria met
- [ ] Tests pass (new tests written first; no existing guard forced red)
- [ ] Fixed-base Standards + Spec review completed within round cap
- [ ] Knowledge/projection refreshed only where genuinely changed
- [ ] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-22 | Created | Initial draft (approved Epic 002) |
