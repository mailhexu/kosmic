---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: "approved"
record_kind: "story"
local_id: "004"
created: "2026-10-19"
updated: "2026-10-19"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-002.md"
linked_architecture: "../architecture.md"
depends_on:
  - "kosmic/workflow-efficiency-and-selective-delegation/story/001"
  - "kosmic/workflow-efficiency-and-selective-delegation/story/002"
  - "kosmic/workflow-efficiency-and-selective-delegation/story/003"
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
related_notes: ["notes/cli-projection-commands.md"]
---

# Three-Case Efficiency Assessment and Integrated Cutover

## User Story

As the kosmic maintainer,
I want the landed efficiency mechanics (unified finish, criterion prefill, terminal-receipt retry, lean workflow, batched completion, full-path handoffs) exercised as one integrated whole and measured honestly across three representative cases,
So that efficiency findings recorded in existing notes are grounded in observed traces with explicit UNKNOWNs, and current docs, CLI guidance, examples and consumer contracts agree with actual behavior without weakening any safety gate or touching historical or global data.

This Story lands last in [Epic 002](../epics/epic-002.md) and consumes the receipted results of [Story 001](story-001.md), [Story 002](story-002.md) and [Story 003](story-003.md); their successful receipted completion is required before this Story may finish. It owns FR-011 (ADR-H) and the final FR-012 coherence check (ADR-I), exercises FR-001–FR-010 as landed behavior, and closes FR-013 on every handoff. It is the integrator, not a re-implementer: no new runtime feature, artifact class, telemetry, review-axis change, historical pin change, or install; the approved preservation guarantees (two independent axes, fixed base, stable findings under the existing max-3 ledger, terminal immutability, human gates) are consumed unchanged. Existing background scientific campaigns are untouched; no costly unrelated calculation is launched to fill a measurement gap.

## Acceptance Criteria

- [ ] Given Stories 001–003 receipted `done`, when this Story's finish runs, then the existing dependency gate passes on the qualified IDs declared in this record's `depends_on`, and the integrated walkthroughs consume the landed unified finish (FR-003), read-only prefill (FR-005) and terminal-receipt retry (FR-004) instead of re-implementing them.
- [ ] Given a real small or resumed episode in scoped managed scratch, when a mid-episode scope/approval change precedes the next mutating call, then the observed call rejects the stale/over-broad attempt with the existing error codes instead of proceeding on cached permission (FR-001/FR-002, ADR-A).
- [ ] Given the same walkthrough covers both receipt routes, when a terminal retry follows a receipted completion and a precheck runs against stale STATUS, then the valid retry validates the completed record and immutable receipt originals and repairs only the derived STATUS reports, while the nonterminal precheck surfaces stale STATUS as explicit diagnostics without auto-repair or repinning (FR-003/FR-004, ADR-B/ADR-C).
- [ ] Given low-risk and domain-risk packets in the walkthrough, when reviews run, then every packet still shows two distinct independent reviewers on the fixed base with stable finding IDs, unchanged inputs receive no fresh audit round, line count alone never excuses domain review, and a simulated full-review failure escalates rather than downgrading (FR-006/FR-007, ADR-E).
- [ ] Given the walkthrough's delegation and batched completion, when checkpoints and the batched pass are exercised, then observed traces show each checkpoint justified by independence, parallelism or context isolation with bounded I/O and a named integration owner (FR-008), and one batched pass completes notes/log/publication with one appropriate canonical refresh including a changed published source, no forced note/proposal, and native-adjacent data-only metadata (FR-009/FR-010, ADR-F/ADR-G).
- [ ] Given the three representative cases (small coding fix, exploratory research campaign, substantial feature), when the single bounded comparison is recorded in this Story's Technical Notes, then cases use actually available traces, elapsed is observed or UNKNOWN, mandatory manual copy/record/start/CLI/handoff counts distinguish observations from expected new-flow counts, receipt timestamps are never durations, and any necessary replay is bounded, in scope and explicitly non-comparable to missing history — never a fabricated baseline (FR-011, ADR-H).
- [ ] Given that same section, when time is reported, then foreground Kosmic admin active time, approval-wait/handoff delay, primary coding/analysis, necessary scientific validation and background compute appear as separated categories, overlapping workers are never summed, no speedup target or percentage is claimed, and no new report class, per-task log or framework is created (FR-011, NFR-003).
- [ ] Given all landed changes, when current docs, CLI guidance, examples and consumer contracts are re-exercised, then they agree with observed behavior with no consumer left on a removed mandatory flow, remaining drift gets only targeted in-scope corrections (`consumer_interface_change: true` anticipates this; [notes/cli-projection-commands.md](../../../../notes/cli-projection-commands.md) is refreshed only on observed drift, never force-rewritten), and every created/presented PRD/Architecture/Epic/Story is individually linked by its full absolute path to the actual file with receipted finished Stories re-linked at the final handoff, while historical receipts/input pins stay byte-unchanged with no historical pin refresh, install, live/global vault change or background-campaign launch (FR-012/FR-013, ADR-I).

## Tasks

### Phase 1: Research

- [ ] Consume Stories 001–003 landed surfaces and receipts; inventory existing traces (completion logs, receipts, work records, session transcripts) per representative case, select cases by actual complete trace availability, and name the UNKNOWN gaps up front.
- [ ] Map current docs/CLI guidance/examples/consumer contracts naming the affected flows for cutover scope; confirm the routine/proposal classification under the existing Task 9/P triggers.
- [ ] Record findings and any human clarifications in Technical Notes.

### Phase 2: Verification-first exercises

- [ ] Reuse existing behavior proofs while their inputs/contracts remain unchanged. Add a permanent red-first regression only if a newly exposed consumer-visible boundary needs one; never force passing tests red or assert source text, prose, wiring or call counts.
- [ ] Consume the prior Stories' negative-boundary results and exercise changed inputs through real CLI behavior in scoped managed scratch. Delegate only when independence, useful parallelism or context isolation justifies a bounded slice and integration owner; no phase-default fanout.

### Phase 3: Comparison and cutover corrections

- [ ] Execute the integrated walkthrough: single-invocation finish with prefill and a valid terminal retry repairing only derived STATUS; small/resumed work with stale-authority rejection; two-axis risk-proportional reviews; useful delegation; batched refresh with a changed published source, no forced notes, native-adjacent data; full-absolute-path links on every created/presented spec.
- [ ] Record the three-case comparison in the Technical Notes comparison section strictly per ADR-H from actually inspected traces; bounded in-scope throwaway replay only where traces are insufficient, explicitly marked observed vs non-comparable, scratch removed after measurement.
- [ ] Apply targeted final corrections where observed drift exists in docs/CLI guidance/examples/consumer contracts; refresh [notes/cli-projection-commands.md](../../../../notes/cli-projection-commands.md) only on observed drift.

### Phase 4: Review and completion

- [ ] Run integrated checks once all affected changes are stable; rerun only changed/failed inputs or contracts; never skip scientific validation.
- [ ] Complete fixed-base two-axis independent Standards/Spec review with stable finding IDs under the existing max-3 ledger; finish through the existing checked completion contract with a receipt.
- [ ] Repeat the full-absolute-path link for every receipted finished Story (001–004) at the final human handoff.

## Routine Decision

This Story assesses, verifies and corrects guidance; it introduces no new reusable deterministic mechanics or `uses_routines` edge and forces no proposal, note or canonical skill edit. Phase 1 confirms this classification under the existing Task 9/P triggers; if research observes a materially changed reusable mechanic, this declaration is amended and its Task P decision obtained before completion. The draft metadata records the intended classification, not a verified claim.

## Technical Notes

Draft state: this section records method and scope only. The comparison subsection is written here only when actually run; no timing, count, receipt or review result is claimed by this record at draft.

- Ownership: FR-011 (ADR-H) and the final FR-012 coherent-cutover check (ADR-I, NFR-004); consumes FR-001–FR-010 as landed by Stories 001–003 and enforces FR-013 at every creation/presentation handoff.
- Comparison method: existing traces first (completion logs, receipts, work records, transcripts); case selection by actual trace availability; elapsed observed or UNKNOWN; manual operation counts distinguish observed from expected new-flow counts. Receipt `completed_at` is never a duration. Any necessary bounded in-scope replay is labeled observed and non-comparable to missing history; it never reconstructs an absent baseline.
- Accounting method: foreground Kosmic admin active time, approval-wait/handoff delay, primary coding/analysis, necessary scientific validation and background compute reported as separated categories; overlapping workers never summed; no speedup target or percentage anywhere.
- Artifact discipline: one bounded comparison section in this Story (a reusable note only if a general insight actually emerges); no new report class, per-task log, telemetry, dossier or replay framework; scoped managed scratch only during exercises, removed after.
- Safety/preservation: two independent review axes, fixed base, max-3 ledger, human gates and terminal-receipt immutability consumed unchanged; historical receipts and input pins byte-unchanged; no historical pin refresh, install, live/global vault change; existing background scientific campaigns untouched.
- `completion_observations` and review metadata are intentionally absent until actually produced; empty review data at draft is correct, never fabricated.

## Definition of Done

- [ ] User approval of this record precedes implementation; Stories 001–003 are receipted `done` and consumed by the walkthroughs.
- [ ] Integrated walkthroughs are observed, including the safety-failure and history-preservation boundaries.
- [ ] The single bounded three-case comparison exists in Technical Notes with UNKNOWNs, separated accounting and no new artifact.
- [ ] Docs, CLI guidance, examples and consumer contracts agree with observed behavior; every correction is targeted and in scope.
- [ ] Historical receipts/pins byte-unchanged; no live/global vault, install or background-campaign change.
- [ ] Fixed-base two-axis review approved under the existing max-3 ledger; successful checked finish with receipt; final handoff repeats full-absolute-path links for every receipted finished Story.
