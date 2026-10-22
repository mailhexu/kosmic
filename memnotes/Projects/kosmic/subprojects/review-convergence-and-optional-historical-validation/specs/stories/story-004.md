---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: done
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
review_round: 2
review_base: "591397a56b9f2ae9e8cf278886b837b3a25a59fa"
completion_observations:
  - criterion: "AC1: Given the refreshed `work_completion.md` and `task_review_spec.md`, when a coordinator follows them, then every unaddressed, partially repaired, or changed unresolved Blocking row in the same ledger is held before routine re-review, and a complete fixed/proposed-refutation payload proceeds without restarting round counting."
    observation: "Actual coordinator held the partial REG-001 response with empty evidence and launched no review for that case; a complete proposed refutation proceeded without resetting the seeded round counter."
    source: "agent://ExerciseCoordinator004; Story003 pre-submit repair/hold trace"
  - criterion: "AC2: Given a genuinely blocked prerequisite, when the coordinator follows the refreshed guidance, then it is recorded and escalated explicitly instead of being submitted as routine re-review, and this path is documented as distinct from the routine submission."
    observation: "The coordinator recorded and escalated the genuinely absent owner-supplied certified-reference.tsv prerequisite instead of submitting it to routine review. Parent observed the file absent in the disposable fixture."
    source: "ExerciseCoordinator004 blocked_prerequisite branch; actual filesystem observation"
  - criterion: "AC3: Given a re-review submission, when the coordinator assembles the handoff per the refreshed checklist, then it carries record identity/path, fixed base, prior and current reviewed revisions, the complete ledger with per-finding responses, changed targets, affected checks/results, requested pair/round, unchanged non-blocking exclusions, and any escalation — and both independent axes receive this identical actual record/ledger/acceptance payload on one held target."
    observation: "The producer assembled one complete frozen handoff containing the actual record, stable ledger, source and contract, revisions, changed targets, checks, round and exclusions, then sent the identical packet to two distinct reviewer agents on a held target."
    source: "ExerciseCoordinator004.StandardsReviewerR3 and ExerciseCoordinator004.SpecReviewerR3 live transcripts"
  - criterion: "AC4: Given `source_revision` unchanged across a context revision, when the coordinator follows the refreshed guidance, then the changed nested record/context is rechecked and the handoff is re-frozen — guidance explicitly states `source_revision` excludes nested Project record bytes and cannot stand in for the payload snapshot."
    observation: "Actual native source_revision stayed ab7cdefb865d6f91d83959fc2229df9268200a4efa19ad6fa88d626bf06871d9 across changed nested record observations. The producer rechecked/refroze the context; parent preserved packet bytes outside the trial worktree and confirmed the held source digest afterward."
    source: "Native source_revision before/after fixture context mutation; ExerciseCoordinator004 re-freeze trace; final digest recheck"
  - criterion: "AC5: Given the refreshed round semantics, when review proceeds, then Round 1 is a full review, one complete Standards + Spec pair on the held snapshot consumes exactly one round, worker repairs and partial callbacks consume none, changes-requested at Round 2 continues into Round 3, and no fourth round starts — the cap yields an explicit human decision packet with existing ledger, attempted resolutions, and concrete decision ask."
    observation: "Story003 received a full initial two-axis pair, counted once as Round1. In the explicit seeded-Round2 exercise, one actual completed Round3 pair advanced 2 to3; held repairs/partial callbacks consumed no round. Both axes rejected the refutation, and the coordinator emitted the existing-ledger human decision packet without a fourth pair/reset. The actual feature review then completed Round2: record count stayed1 until both callbacks arrived, and both axes accepted STD-001 before the count advanced to2."
    source: "Story003 Round1 held-payload review; ExerciseCoordinator004 actual Round3 producer/child-agent trace (prior rounds1/2 explicitly seeded fixture input); Review004Standards-2 and Review004Spec-2 actual R2 callbacks"
  - criterion: "AC6: Given a later round after the full Round 1, when scoping review per the refreshed guidance, then it covers unresolved findings, changed behavior/affected checks, linked fix-introduced `REG`, and evidence-backed critical `LATE` findings that explain why Round 1 missed them; ordinary unchanged-code/style findings remain non-blocking follow-ups."
    observation: "The actual later-round pair confined itself to unresolved REG-001 linked to the SPEC-001 zero fix and affected negative/zero checks, with no new unchanged/style findings. The authoritative guidance retains the evidence-backed critical-LATE exception with why missed; no actual critical-LATE defect was introduced/exercised."
    source: "ExerciseCoordinator004 Round3 scope and returned ledgers; task_review_spec.md later-round contract"
  - criterion: "AC7: Given a worker refutation, when the coordinator/reviewer follows the refreshed guidance, then reviewer acceptance closes via existing `resolved` with optional `resolution: refuted`, and rejection leaves the row open/Blocking with rationale retained — identical to the native semantics Story 003 validates; the guidance introduces no new closure status."
    observation: "Story003 actual CLI accepted resolved plus resolution:refuted and retained rationale. In the live coordinator exercise both independent reviewers rejected the proposed refutation and left REG-001 open/Blocking with its rationale retained; SPEC-001 stayed resolved."
    source: "Story003 accepted-refutation CLI smoke; ExerciseCoordinator004 final stable ledger and child decisions"
  - criterion: "AC8: Given a real producer/coordinator episode, when readiness, two-axis same-payload handoff, pair-round counting, Round-2→3 continuation, and cap behavior are exercised, then actual agent/producer traces demonstrate each observable and no permanent prose/source-text/mock-echo test is added to the suite for these policy behaviors."
    observation: "A real producer executed readiness hold, blocked escalation, context re-freeze, identical two-axis handoff and the cap decision. The only live trial review was the actual Round3 pair; prior round history was seeded explicitly, not fabricated product review. No permanent prose/source-text/mock-echo tests were added for this Story."
    source: "agent://ExerciseCoordinator004 and its two live reviewer transcripts; owned delta contains only source guidance files"
  - criterion: "AC9: Given the source-doc/runtime overlap with Story 003's seam and shared Usage-note/publication surfaces, when this story lands, then same-episode integration of any genuinely changed bounded shared paths is executed under the parent single-writer integration with baseline checks, and no conflicting duplicate guidance is left in the refreshed files."
    observation: "Parent compared all ten review-slice destination source hashes with captured baselines, then Git check-applied and applied only the reviewed Story003/004 source deltas into Original without touching its index. Guidance preserves the observed native active-phase contract; the durable Usage invariant was regenerated and inspected in the canonical pair in the same episode."
    source: "Captured destination hashes; successful git apply --check and git apply for ten reviewed source paths; native phase refusal/completion; generated Usage-reference inspection"
completion_review: {"reviewer":"Main","axes":{"standards":{"decision":"approved","reviewer":"Review004Standards-2"},"spec":{"decision":"approved","reviewer":"Review004Spec-2"}},"decision":"approved","review_base":"591397a56b9f2ae9e8cf278886b837b3a25a59fa","reviewed_revision":"f8ee3e4b7a3be95dc8932abf940172537f076be49f632f374ef496f434371ade","findings":[{"id":"STD-001","axis":"standards","disposition":"Blocking","introduced_round":1,"status":"resolved","evidence":"template-story defines review_round as completed pairs (0 before first), while Work Completion initializer still instructed upfront1; pending feature packet showed the conflict.","required_resolution":"Initialize0 and advance only after both axes complete; requested pairnumber travels inhandoff, not preincremented completedcount.","worker_response":{"kind":"fixed","detail":"Work Completion initializer now0; advance only after both axes complete. Task7 distinguishes requested pair from completed record count; finish-time1..3 unchanged. No newcounterfield.","evidence":"Worker coherent-source audit of owned guidance: Story/QuickTask alreadyinitialize0; templatecompletedcounteragrees; changed WorkCompletion §1/§3 and Task7 §2.6. Submitted for independent verification, not worker closure."},"resolution":"fixed","resolution_note":"Both independent R2 axes accepted the counter coherence fix; worker claim did not close the finding."}],"scope":["worktree:skills/SKILL.md","worktree:skills/README.md","worktree:skills/references/work_completion.md","worktree:skills/references/task_review_spec.md","worktree:skills/references/task_implement_story.md","worktree:skills/references/task_quick_task.md","worktree:skills/references/templates/template-story.md"]}
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

- [x] AC1: Given the refreshed `work_completion.md` and `task_review_spec.md`, when a coordinator follows them, then every unaddressed, partially repaired, or changed unresolved Blocking row in the same ledger is held before routine re-review, and a complete fixed/proposed-refutation payload proceeds without restarting round counting.
- [x] AC2: Given a genuinely blocked prerequisite, when the coordinator follows the refreshed guidance, then it is recorded and escalated explicitly instead of being submitted as routine re-review, and this path is documented as distinct from the routine submission.
- [x] AC3: Given a re-review submission, when the coordinator assembles the handoff per the refreshed checklist, then it carries record identity/path, fixed base, prior and current reviewed revisions, the complete ledger with per-finding responses, changed targets, affected checks/results, requested pair/round, unchanged non-blocking exclusions, and any escalation — and both independent axes receive this identical actual record/ledger/acceptance payload on one held target.
- [x] AC4: Given `source_revision` unchanged across a context revision, when the coordinator follows the refreshed guidance, then the changed nested record/context is rechecked and the handoff is re-frozen — guidance explicitly states `source_revision` excludes nested Project record bytes and cannot stand in for the payload snapshot.
- [x] AC5: Given the refreshed round semantics, when review proceeds, then Round 1 is a full review, one complete Standards + Spec pair on the held snapshot consumes exactly one round, worker repairs and partial callbacks consume none, changes-requested at Round 2 continues into Round 3, and no fourth round starts — the cap yields an explicit human decision packet with existing ledger, attempted resolutions, and concrete decision ask.
- [x] AC6: Given a later round after the full Round 1, when scoping review per the refreshed guidance, then it covers unresolved findings, changed behavior/affected checks, linked fix-introduced `REG`, and evidence-backed critical `LATE` findings that explain why Round 1 missed them; ordinary unchanged-code/style findings remain non-blocking follow-ups.
- [x] AC7: Given a worker refutation, when the coordinator/reviewer follows the refreshed guidance, then reviewer acceptance closes via existing `resolved` with optional `resolution: refuted`, and rejection leaves the row open/Blocking with rationale retained — identical to the native semantics Story 003 validates; the guidance introduces no new closure status.
- [x] AC8: Given a real producer/coordinator episode, when readiness, two-axis same-payload handoff, pair-round counting, Round-2→3 continuation, and cap behavior are exercised, then actual agent/producer traces demonstrate each observable and no permanent prose/source-text/mock-echo test is added to the suite for these policy behaviors.
- [x] AC9: Given the source-doc/runtime overlap with Story 003's seam and shared Usage-note/publication surfaces, when this story lands, then same-episode integration of any genuinely changed bounded shared paths is executed under the parent single-writer integration with baseline checks, and no conflicting duplicate guidance is left in the refreshed files.

## Tasks

### Phase 1: Research

- [x] Map the existing round/handoff guidance and preserve the native three-round boundary.
- [x] Confirm Story 003's native receipt and terminal completion check before authoring; its source commit was integrated into this clean writer.
- [x] Pin `review_base: 591397a56b9f2ae9e8cf278886b837b3a25a59fa` before guidance edits.
- [x] Map affected guidance references; keep the full coordinator protocol authoritative in Task 7 and native proof/phase mechanics authoritative in Work Completion.

### Phase 2: Policy traces (evidence-first, not TDD code tests)

- [x] TRACE-001: actual producer held the incomplete REG-001 response and submitted only the complete proposed-refutation case.
- [x] TRACE-002: actual producer escalated the absent owner-supplied certified-reference prerequisite without opening a review.
- [x] TRACE-003: actual producer delivered the identical full held packet to two independent axes after re-freezing changed record context with unchanged native source_revision.
- [x] TRACE-004: actual complete pair advanced seeded prior-round count 2 → 3; partial callbacks/held repairs consumed none; rejected refutation produced the cap human decision packet, not a fourth pair.

### Phase 3: Implementation

- [x] IMPL-001: encode the full barrier/handoff/round/refutation protocol once in Task 7, with bounded pointers from Work Completion.
- [x] IMPL-002: align worker/Quick Task/SKILL/README guidance, including the observed native finish phase contract without broadening runtime admission.
- [x] IMPL-003: update the existing Story template's field guidance without future/placeholder progress rows or new artifact classes.
- [x] IMPL-004: parent updated the durable Usage phase invariant and atomically regenerated the Skill Pair in this episode; shared source remains isolated for baseline-checked integration.

### Phase 4: Review

- [x] Actual smoke: real coordinator and two live reviewer agents exercised the three readiness cases and one bounded Round-3 pair; earlier rounds were explicitly seeded fixture inputs, not fabricated feature history.
- [x] Independent Standards and Spec axes approved the fixed counter contract at Round2 on the original base; full STD-001 ledger retained and reviewer-resolved. Native work finish alone publishes completion.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially changed. This story documents ordinary private Project review workflow — coordinator validation/reporting guidance and caller behavior — not registered routine compilation or `uses_routines` edges. If implementation turns out to change routine edges or registered reusable mechanics, that scope must be updated and reapproved rather than silently expanded.

## Technical Notes

- Known facts: architecture ADR-003 fixes the protocol — hold incomplete responses, escalate genuine blockers, carry the full payload to both axes on one held target, Round 1 full, later rounds bounded, pair = one round, cap = explicit packet. `source_revision` excludes nested Project record bytes, so it cannot freeze acceptance context.
- This story is policy-only: its observable behavior is how real coordinator/producer episodes run; permanent prose, source-text, import, wiring, and mock-echo tests are prohibited. Runtime guards for annotation shape and final metadata/freshness already exist from Story 003 and are reused.
- No new CLI: the [CLI projection commands](../../../../notes/cli-projection-commands.md) surface stays unchanged unless a documented command's Usage genuinely changes; [CLI extension conventions](../../../../notes/cli-extension-conventions.md) apply if it does.
- `review_base` was pinned at activation. Native finish accepts an authorized `approved`/`in_progress` phase, not `review`; the review decision stays in `completion_review` until native receipt publication. Ephemeral handoff payloads stay outside the reviewed source worktree to avoid changing the source fingerprint.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Story 003 landed before this guidance | Verified | Successful native receipt plus terminal completion check; source commit integrated before baseline pin |
| Existing runtime permits rounds 1–3 | Verified | Source validator and prior focused completion guards |
| Guidance must not strand records in `review` | Corrected | Actual Story 003 finish refusal, then supported active-phase completion; caller guidance aligned |

## Definition of Done

- [x] All acceptance criteria met, with real producer/coordinator traces as policy evidence
- [x] Guidance coherent across all owned files; counter conflict corrected and independently verified
- [x] Fixed-base Standards + Spec review completed within round cap
- [x] No new CLI, engine, persistent artifact, or upstream/installed skill edits
- [x] No regressions observed in the exercised coordinator paths; integrated suite follows after all slices stabilize.

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-22 | Created | Initial draft (approved Epic 002; depends on Story 003) |
| 2026-10-22 | Approved → implemented | Dependency receipted; guidance deduplicated; actual producer held/escalated/re-froze and ran two independent Round-3 reviewers on a disposable target. Both rejected REG-001 refutation; cap packet emitted. Formal feature review pending. |
| 2026-10-22 | Round 1 changes requested | Standards found STD-001 counter initialization conflict; Spec approved. Worker supplied a complete fixed response without self-closing; record count remains one completed pair while Round 2 is requested. |
| 2026-10-22 | Round 2 approved and integrated | Both independent axes accepted STD-001; only then did the completed counter advance 1 → 2. Parent baseline-checked and applied the ten reviewed review-slice source paths; native receipt publication follows. |
