---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: "draft"
record_kind: "story"
local_id: "004"
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
depends_on: ["kosmic/review-convergence-and-optional-historical-validation/story/003"]
---

# Story 004: Coordinator readiness and bounded re-review handoff

## User Story

As a kosmic coordinator submitting routine re-review,
I want the workflow references to define a pre-submit readiness barrier, a complete frozen same-payload handoff to both axes, and bounded pair-based round semantics,
So that incomplete or changed Blocking rows are held, blocked prerequisites escalate instead of reviewing, and review always terminates within three rounds with a concrete human decision packet.

## Scope

### In Scope

- Refresh of the source workflow guidance surfaces — `skills/SKILL.md`, `skills/references/task_review_spec.md`, `skills/references/task_implement_story.md`, `skills/references/task_quick_task.md`, `skills/references/work_completion.md`, `skills/references/templates/template-story.md`, and `skills/README.md` as needed — to encode the actual coordinator protocol: readiness barrier, blocked escalation, complete frozen handoff payload, one-round-per-pair counting, Round-2→3 continuation, max-3 cap, and later-round regression/`LATE` scope.
- Accepted and refused refutation outcomes expressed consistently with Story 003's native closure semantics (`status: resolved` + optional `resolution: fixed|refuted`; rejected refutation stays open/Blocking).
- Policy observables evidenced by actual producer/coordinator traces, not permanent prose, source-text, import, wiring, or mock-echo tests.
- Bounded same-episode integration of genuinely changed shared consumer surfaces — the Usage note (`notes/cli-projection-commands.md`) and published-note projections affected by the coordinator protocol — executed under the parent integration coordinator's single-writer ownership with baseline checks, not deferred to a separate follow-up.

### Out of Scope

- New CLI commands, engine, journal, persistent round artifact, context hash, or sidecar; no edit to the upstream generic code-review skill or installed copies.
- Any runtime change to `kosmic_completion.py` (Story 003's seam) beyond consuming its semantics.
- Concurrent whole-file edits to shared surfaces: shared paths above are written only within the parent's single-writer integration pass, with this story declaring the exact bounded changes.

### Owned Files

- `skills/SKILL.md`, `skills/README.md` (workflow/phase guidance only as needed)
- `skills/references/task_review_spec.md`, `skills/references/task_implement_story.md`, `skills/references/task_quick_task.md`, `skills/references/work_completion.md`
- `skills/references/templates/template-story.md` (review-handoff fields guidance only)
- Bounded shared integration targets under parent single-writer pass: `notes/cli-projection-commands.md` and affected published-note projections, if and only if their content genuinely changes

## Acceptance Criteria

- [ ] AC1: Given the refreshed `work_completion.md` and `task_review_spec.md`, when a coordinator follows them, then every unaddressed, partially repaired, or changed unresolved Blocking row in the same ledger is held before routine re-review, and a complete fixed/proposed-refutation payload proceeds without restarting round counting.
- [ ] AC2: Given a genuinely blocked prerequisite, when the coordinator follows the refreshed guidance, then it is recorded and escalated explicitly instead of being submitted as routine re-review, and this path is documented as distinct from the routine submission.
- [ ] AC3: Given a re-review submission, when the coordinator assembles the handoff per the refreshed checklist, then it carries record identity/path, fixed base, prior and current reviewed revisions, the complete ledger with per-finding responses, changed targets, affected checks/results, requested pair/round, unchanged non-blocking exclusions, and any escalation — and both independent axes receive this identical actual record/ledger/acceptance payload on one held target.
- [ ] AC4: Given `source_revision` unchanged across a context revision, when the coordinator follows the refreshed guidance, then the changed nested record/context is rechecked and the handoff is re-frozen — guidance explicitly states `source_revision` excludes nested Project record bytes and cannot stand in for the payload snapshot.
- [ ] AC5: Given the refreshed round semantics, when review proceeds, then Round 1 is a full review, one complete Standards + Spec pair on the held snapshot consumes exactly one round, worker repairs and partial callbacks consume none, changes-requested at Round 2 continues into Round 3, and no fourth round starts — the cap yields an explicit human decision packet with existing ledger, attempted resolutions, and concrete decision ask.
- [ ] AC6: Given a later round after the full Round 1, when scoping review per the refreshed guidance, then it covers unresolved findings, changed behavior/affected checks, linked fix-introduced `REG`, and evidence-backed critical `LATE` findings that explain why Round 1 missed them; ordinary unchanged-code/style findings remain non-blocking follow-ups.
- [ ] AC7: Given a worker refutation, when the coordinator/reviewer follows the refreshed guidance, then reviewer acceptance closes via existing `resolved` with optional `resolution: refuted`, and rejection leaves the row open/Blocking with rationale retained — identical to the native semantics Story 003 validates; the guidance introduces no new closure status.
- [ ] AC8: Given a real producer/coordinator episode, when readiness, two-axis same-payload handoff, pair-round counting, Round-2→3 continuation, and cap behavior are exercised, then actual agent/producer traces demonstrate each observable and no permanent prose/source-text/mock-echo test is added to the suite for these policy behaviors.
- [ ] AC9: Given the source-doc/runtime overlap with Story 003's seam and shared Usage-note/publication surfaces, when this story lands, then same-episode integration of any genuinely changed bounded shared paths is executed under the parent single-writer integration with baseline checks, and no conflicting duplicate guidance is left in the refreshed files.

## Tasks

### Phase 1: Research

- [ ] Read the current review/completion guidance in the owned reference files and `SKILL.md`; map where round counting, barriers, and handoff are described today (PRD cites `:284-286` three-round allowance and `kosmic_completion.py:371-409` review_round 1–3 enforcement as the existing anchors).
- [ ] Confirm Story 003's landed validation semantics (depends_on gate) so the guidance matches native behavior exactly; do not author guidance ahead of the seam.
- [ ] ACTIVATION (before any edit or review): implementation owner pins the real clean-writer baseline for this story in `review_base` (intentionally absent — no placeholder). Review uses that fixed base.
- [ ] Bounded activation check: identify all current internal cross-references between the owned files that the refresh must keep coherent (no runtime probes).

### Phase 2: Policy traces (evidence-first, not TDD code tests)

- [ ] TRACE-001: hold trace — an episode where a partial Blocking repair is withheld from re-review, and one where a complete payload proceeds.
- [ ] TRACE-002: escalation trace — a genuine blocked prerequisite recorded and escalated rather than submitted.
- [ ] TRACE-003: handoff trace — the same frozen payload (identity, base, revisions, full ledger/responses, changed targets, affected checks, round, exclusions) delivered to both axes; plus a revised-context case where `source_revision` is unchanged and the target is rechecked/re-frozen.
- [ ] TRACE-004: round traces — pair counted as one round; repair consuming none; Round-2 changes-requested continuing to Round 3; cap producing the human decision packet with no fourth round.

### Phase 3: Implementation

- [ ] IMPL-001: encode the readiness barrier, blocked-escalation path, and frozen same-payload handoff checklist in `work_completion.md` and `task_review_spec.md`, aligned to architecture ADR-003 wording.
- [ ] IMPL-002: align `task_implement_story.md`, `task_quick_task.md`, and `SKILL.md`/`README.md` references so worker-response expectations, later-round scope (`REG`/`LATE`/follow-ups), and round semantics are consistent everywhere they are mentioned.
- [ ] IMPL-003: update `templates/template-story.md` guidance for the review/handoff fields a story must carry (base pinning, ledger references) without adding placeholder progress rows.
- [ ] IMPL-004: declare and execute the bounded same-episode integration of genuinely changed shared surfaces (`notes/cli-projection-commands.md`, affected published-note projections) within the parent integration coordinator's single-writer pass, reconciled against the parent baseline; no conflicting duplicate guidance remains.

### Phase 4: Review

- [ ] Actual smoke: one real mini re-review episode against a scratch Project ledger exercising barrier, two-axis handoff, and round counting end-to-end, retained as the trace evidence.
- [ ] Independent fixed-base Standards review and Spec review against the pinned `review_base`; stable ledger, one round per complete pair, max three rounds with human packet at cap; native receipt completion per existing completion gates.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed. This story documents ordinary private Project review workflow — coordinator validation/reporting guidance and caller behavior — not registered routine compilation or `uses_routines` edges. If implementation turns out to change routine edges or registered reusable mechanics, that scope must be updated and reapproved rather than silently expanded.

## Technical Notes

- Known facts: architecture ADR-003 fixes the protocol — hold incomplete responses, escalate genuine blockers, carry the full payload to both axes on one held target, Round 1 full, later rounds bounded, pair = one round, cap = explicit packet. `source_revision` excludes nested Project record bytes, so it cannot freeze acceptance context.
- This story is policy-only: its observable behavior is how real coordinator/producer episodes run; permanent prose, source-text, import, wiring, and mock-echo tests are prohibited. Runtime guards for annotation shape and final metadata/freshness already exist from Story 003 and are reused.
- No new CLI: the [CLI projection commands](../../../../notes/cli-projection-commands.md) surface stays unchanged unless a documented command's Usage genuinely changes; [CLI extension conventions](../../../../notes/cli-extension-conventions.md) apply if it does.
- `review_base` is deliberately absent from frontmatter; pinned by the implementation owner at activation, before edits and review.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Story 003's seam semantics are landed before guidance is authored | ⬜ | depends_on gate |
| Existing three-round anchor points are where the PRD cites | ⬜ | Phase 1 research |
| Cross-references among owned files are enumerable pre-edit | ⬜ | Activation check |

## Definition of Done

- [ ] All acceptance criteria met, with real producer/coordinator traces as policy evidence
- [ ] Guidance coherent across all owned files; no conflicting duplicate guidance vs runtime
- [ ] Fixed-base Standards + Spec review completed within round cap
- [ ] No new CLI, engine, persistent artifact, or upstream/installed skill edits
- [ ] No regressions introduced

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-22 | Created | Initial draft (approved Epic 002; depends on Story 003) |
