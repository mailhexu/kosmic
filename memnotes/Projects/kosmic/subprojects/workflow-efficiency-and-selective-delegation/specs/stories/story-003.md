---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: "draft"
record_kind: "story"
local_id: "003"
created: "2026-10-19"
updated: "2026-10-19"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-002.md"
linked_architecture: "../architecture.md"
depends_on: []
related_notes: ["notes/cli-projection-commands.md", "notes/note-writing-style.md", "notes/shared-domain-skill-library.md"]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
completion_observations: []
completion_review: {}
---

# Story 003: Lean Workflow and Accessible Artifact Handoffs

## User Story

As a Kosmic Project contributor and the approving human,
I want the approved safety machinery exercised leanly — one authorizing record reused across a bounded episode, risk-proportional two-axis review packets, justified delegation only, batched completion, and every spec handoff carrying an individually clickable full-absolute-path link,
So that coordination overhead drops without weakening any gate and each created or finished artifact opens directly from the handoff message.

## Acceptance Criteria

- [ ] AC1: Given an existing record that already authorizes the work, when the episode starts once and resumes across steps on that record and its existing worktree without restart, extra record, fresh worktree, or recorded-scope widening, then questions, code search, and unchanged-input checks stay record-free and the Quick Task vs full-spec choice follows actual scope and risk.
- [ ] AC2: Given a mid-episode scope or approval change, when the next mutating CLI invocation runs, then it re-derives identity, ancestry, scope, and approval live at invocation and rejects the stale or over-broad attempt instead of proceeding on cached permission.
- [ ] AC3: Given a low-risk change under its pinned fixed review base, when its review packet is produced, then the packet bounds to the actual delta plus acceptance context (base, criteria, checks, adverse facts) while two distinct independent Standards/Spec reviewers, stable finding identifiers, rounds 1–3, and the fixed base all remain, and re-review keeps existing findings and checks only changed evidence, so unchanged inputs receive no fresh audit round.
- [ ] AC4: Given a simulated full-review failure and a numerics/scientific, methods, security, or API/data/schema/publication/receipt-class change, when review converges, then the failure escalates under the existing three-round limit instead of downgrading to a light pass, and domain risk judged from content and blast radius is never excused by line count.
- [ ] AC5: Given discretionary subagent checkpoints in the exercised traces, when each is audited, then it is justified only by genuine independence, useful parallelism, or context isolation with a bounded question/slice, explicit input/output, and a named integration owner in the existing launch trace; coupled work has one owner, host/proposer/reviewer mandates are untouched, and no new delegation artifact is created.
- [ ] AC6: Given one episode's verification work, when checks are scheduled, then focused checks run during work and integrated verification runs once after affected changes stabilize, reruns cover only changed inputs/contracts or previously failed checks, and scientific validation is never skipped.
- [ ] AC7: Given one authorized episode's knowledge notes, log entries, and publication completion, when the episode completes, then they are batched into one pass with one appropriate canonical refresh that includes a changed published note source, nothing is forced so a zero-note episode is a legitimate outcome, and dataset-only metadata stays native-adjacent.
- [ ] AC8: Given every created or presented PRD, Architecture, Epic, or Story — individually or batched — and the cutover of this Story's owned guidance, when a human handoff is produced, then each artifact carries an individual Markdown link whose visible label is its full absolute path and whose target opens the actual file, receipted finished Stories are re-linked with final canonical locations after integration, no future/nonexistent/relative/index/directory substitute appears, CLI JSON stays unchanged, approval is never presented as completion, and the updated skills/SKILL.md, task_quick_task, task_implement_story, task_review_spec, task_add_note, task_review, task_create_spec, and work_completion guidance plus README match exercised behavior with historical receipts and pins byte-immutable and no installed-copy or live/global vault change.

## Tasks

### Phase 1: Research

- [ ] Survey the guidance surfaces named in AC8 for current statements on reuse/authority, packet sizing, delegation, verification cadence, batching, and handoff links; record the delta list in Technical Notes before any edit.
- [ ] Verify related-note metadata is current (cli-projection-commands, note-writing-style, shared-domain-skill-library — stable usage/both) and locate the FR-012 cutover points owned here versus Stories 001/002.
- [ ] Fix integration ownership for shared files (skills/SKILL.md, README.md, work_completion.md): runtime-behavior docs follow Story 001/002 landed contracts; policy, delegation, batching, and handoff-link guidance is owned here; nothing documents unavailable runtime as existing.
- [ ] Verify every assumption and record findings and open questions in Technical Notes; work starts only after this Story is approved.

### Phase 2: Verification-First Exercise Plan

- [ ] TEST-001: Define the per-AC observed exercises before guidance edits: a real small/resumed workflow with a stale-authority rejection probe; a low-risk two-axis packet with re-review and an unchanged-input no-recheck; escalation and domain-risk probes; a delegation trace audit; a batched episode including a changed published note source plus a zero-note episode; a handoff link audit over batched presentations and multiple receipted Story completions.
- [ ] TEST-002: Fix the evidence rule up front: exercises are observed via real producer/handoff traces recorded in Technical Notes and completion_observations; failing-before proof is required only for NEW changed-behavior regressions — existing passing safety tests are never forced to fail; no permanent prose, source-text, import, wiring, or incidental-wording tests; scoped managed scratch only during implementation and removed after; a throwaway CLI smoke wherever runtime behavior is exercised.

### Phase 3: Implementation

- [ ] IMPL-001: Update reuse/authority guidance — record-first reuse, record-free questions/searches/unchanged-input checks, Quick Task vs full-spec by scope and risk, live re-derivation at every mutating call — in skills/SKILL.md, task_quick_task.md, and task_implement_story.md.
- [ ] IMPL-002: Update review guidance for risk-proportional packets, unchanged-input no-recheck, domain-category strengthening, and max-3 escalation in task_review_spec.md and the non-runtime parts of work_completion.md.
- [ ] IMPL-003: Update delegation and verification-cadence guidance (FR-008/FR-009) in skills/SKILL.md, task_implement_story.md, and README.md.
- [ ] IMPL-004: Update batching guidance — notes, log, and publication in one pass with one appropriate canonical refresh, nothing forced, native-adjacent dataset metadata — in task_add_note.md, task_review.md, and README.md.
- [ ] IMPL-005: Add the FR-013 full-absolute-path handoff rule at creation, presentation, and Story-completion points in task_create_spec.md, task_implement_story.md, and README.md; keep machine CLI JSON untouched and never edit installed skill copies or live/global vault state.

### Phase 4: Review and Completion

- [ ] Pin review_base before the first edit and run the fixed-base two-axis independent review with two distinct Standards/Spec reviewers, the stable finding ledger, and at most three rounds; failure escalates, never a light fallback; unchanged inputs receive no fresh audit round.
- [ ] Record truthful per-criterion observations with concrete sources in completion_observations; run focused checks during work and integrated verification once the guidance edits stabilize, rerunning only changed/failed checks; scientific validation never skipped.
- [ ] Complete only with the user approval gate passed, exercised smoke evidence, and a successful receipt-backed `work finish` with precise scope claims; then repeat the full-absolute-path links for every receipted finished Story, including final canonical locations after integration.
- [ ] Batch the episode's log, notes, and publication once appropriate; create durable knowledge only under existing Task 2 triggers; no new dossier, engine, telemetry, sidecar, or installed-copy change; close with the final canonical links in the human handoff.

## Routine Decision

No reusable deterministic procedure mechanics are introduced: this Story plans prose guidance updates and observed workflow exercises, adds no routine edge, and changes no `uses_routines` declaration, so `routine_decision_required` stays false. `proposal_required` stays false because no implemented work yet yields a verified reusable procedure and none is manufactured. If implementation materially changes reusable deterministic mechanics or a routine edge, the existing Task P proposal triggers and the `check-completion` proposal gate classify and govern it at that time; canonical and installed skill edits stay behind their existing approvals.

## Technical Notes

- Runtime boundary: unified finish/terminal-receipt route (Story 001) and `work prepare-completion` prefill (Story 002) are approved design, not current behavior; this Story consumes their public contracts and documents no unavailable runtime as existing. Shared surfaces (skills/SKILL.md, README.md, work_completion.md) get one integration owner at implementation instead of concurrent blind edits; Story 004 owns final integrated coherence and the FR-011 three-case comparison — this Story only leaves honest traces.
- Survey 2026-10-19: task_quick_task.md already mandates one record/one worktree, record-free questions, pinned-base review, and receipt-backed finish; task_review_spec.md already carries the two-axis machinery, the stable ledger (STD-/SPEC-/REG-/LATE-), the re-review contract, and the three-round escalation limit; task_add_note.md already forbids forced notes and keeps dataset metadata native-adjacent. Missing today: risk-proportional packet scope with domain categories (FR-006), the unchanged-input no-recheck statement, delegation checkpoint criteria and the integration-owner rule (FR-008), focused-vs-integrated cadence (FR-009), one-pass notes/log/publication batching (FR-010), and any FR-013 link rule in task_create_spec.md, task_implement_story.md, skills/SKILL.md, or README.md.
- FR-013 is deliberately a prose-enforced presenter rule (ADR-I), verified from observed handoffs and never a machine gate; this Story's own approval handoff must already demonstrate it: [/home/hexu/projects/myagentskills/kosmic/memnotes/Projects/kosmic/subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-003.md](/home/hexu/projects/myagentskills/kosmic/memnotes/Projects/kosmic/subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-003.md).
- Review risk stays proportional to content and blast radius (ADR-E): numerics/scientific claims, methods, security, and API/data/schema/publication/receipt changes always receive domain review regardless of line count.
- Related notes verified stable 2026-10-19: [Projection CLI experience commands](../../../../notes/cli-projection-commands.md) (usage) grounds CLI-facing guidance; [Note writing style](../../../../notes/note-writing-style.md) (both) governs guidance prose; [Shared Domain Skill Library](../../../../notes/shared-domain-skill-library.md) (usage) bounds batching and publication to existing library mechanics with no new artifact class.
- Testing contract: behavior-observing exercises only, per the Architecture test strategy; policy, human-link, and delegation behaviors are verified from real producer/handoff traces, not permanent wording tests; passing tests alone are never completion proof.

## Definition of Done

- [ ] All acceptance criteria observed and met, with truthful per-criterion observations and sources recorded in this record
- [ ] Owned guidance files updated coherently with exercised behavior, no consumer left on a removed mandatory flow, historical receipts and pins byte-immutable
- [ ] Fixed-base two-axis independent review approved with the stable ledger preserved; any max-3 escalation is explicitly resolved before completion, never treated as a pass by itself
- [ ] User approval gate, actual exercised smoke, and a successful receipt-backed `work finish` with precise scope claims
- [ ] No new artifact class, dossier, engine, telemetry, sidecar, installed-copy edit, or live/global vault change
- [ ] Final human handoff repeats the individual full-absolute-path link for every receipted finished Story, including final canonical locations after integration
