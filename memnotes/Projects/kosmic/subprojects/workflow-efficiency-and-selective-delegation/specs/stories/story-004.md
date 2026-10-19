---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: done
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
review_base: "b3301180cbaebebcf033d9922a7ed79efb6c126b"
review_round: 2
completion_observations:
  - criterion: "Given Stories 001–003 receipted `done`, when this Story's finish runs, then the existing dependency gate passes on the qualified IDs declared in this record's `depends_on`, and the integrated walkthroughs consume the landed unified finish (FR-003), read-only prefill (FR-005) and terminal-receipt retry (FR-004) instead of re-implementing them."
    observation: "All three dependency records and immutable receipts were integrated byte-for-byte; each real integrated check-completion --work-record passed. Their qualified IDs match this record depends_on list, so the existing dependency gate is satisfiable before this final finish transaction."
    source: "Story004 bounded primary-source comparison; actual dependency receipts and canonical terminal checks; integrated JUnit/targeted results; real CLI S1–S7 and affected S1; independent Story004 Round2 decisions."
  - criterion: "Given a real small or resumed episode in scoped managed scratch, when a mid-episode scope/approval change precedes the next mutating call, then the observed call rejects the stale/over-broad attempt with the existing error codes instead of proceeding on cached permission (FR-001/FR-002, ADR-A)."
    observation: "Actual S6 used one clean start and a successful mutating generate, revoked the bound fixture record to draft, then observed WORK_PHASE_DENIED on the next generate without restart or any projected-byte change."
    source: "Story004 bounded primary-source comparison; actual dependency receipts and canonical terminal checks; integrated JUnit/targeted results; real CLI S1–S7 and affected S1; independent Story004 Round2 decisions."
  - criterion: "Given the same walkthrough covers both receipt routes, when a terminal retry follows a receipted completion and a precheck runs against stale STATUS, then the valid retry validates the completed record and immutable receipt originals and repairs only the derived STATUS reports, while the nonterminal precheck surfaces stale STATUS as explicit diagnostics without auto-repair or repinning (FR-003/FR-004, ADR-B/ADR-C)."
    observation: "Actual S3/S4 produced a receipt, tolerated subsequent linked-data evolution with unchanged receipt bytes and one completion-log entry, repaired derived STATUS, rejected record tampering and accepted the restored original. Nonterminal stale-STATUS refusal and declared formal failures passed separately in the integrated regressions."
    source: "Story004 bounded primary-source comparison; actual dependency receipts and canonical terminal checks; integrated JUnit/targeted results; real CLI S1–S7 and affected S1; independent Story004 Round2 decisions."
  - criterion: "Given low-risk and domain-risk packets in the walkthrough, when reviews run, then every packet still shows two distinct independent reviewers on the fixed base with stable finding IDs, unchanged inputs receive no fresh audit round, line count alone never excuses domain review, and a simulated full-review failure escalates rather than downgrading (FR-006/FR-007, ADR-E)."
    observation: "Two real independent reviewer agents retained the fixed bases and stable SPEC-001 finding from Round1 through resolution in Round2. The small API-structure defect was not exempted by line count. S7 refused a round-3 changes-requested review with record/ledger bytes unchanged and no receipt; no automatic light fallback occurred."
    source: "Story004 bounded primary-source comparison; actual dependency receipts and canonical terminal checks; integrated JUnit/targeted results; real CLI S1–S7 and affected S1; independent Story004 Round2 decisions."
  - criterion: "Given the walkthrough's delegation and batched completion, when checkpoints and the batched pass are exercised, then observed traces show each checkpoint justified by independence, parallelism or context isolation with bounded I/O and a named integration owner (FR-008), and one batched pass completes notes/log/publication with one appropriate canonical refresh including a changed published source, no forced note/proposal, and native-adjacent data-only metadata (FR-009/FR-010, ADR-F/ADR-G)."
    observation: "Bounded task requests and retained reviewer contexts show purposeful delegation and Main as integration owner. Native generation batched changed-note bookkeeping, pair and library refresh; S5 proved changed-content refresh/no-churn, and S3 required no new knowledge note. External campaign data and metadata were read only at their native sources."
    source: "Story004 bounded primary-source comparison; actual dependency receipts and canonical terminal checks; integrated JUnit/targeted results; real CLI S1–S7 and affected S1; independent Story004 Round2 decisions."
  - criterion: "Given the three representative cases (small coding fix, exploratory research campaign, substantial feature), when the single bounded comparison is recorded in this Story's Technical Notes, then cases use actually available traces, elapsed is observed or UNKNOWN, mandatory manual copy/record/start/CLI/handoff counts distinguish observations from expected new-flow counts, receipt timestamps are never durations, and any necessary replay is bounded, in scope and explicitly non-comparable to missing history — never a fabricated baseline (FR-011, ADR-H)."
    observation: "The single comparison section cites real small-fix, governed NiO campaign and substantial-feature traces. Its per-case observed/expected table accounts for copy, record reservation, work start, Kosmic CLI and human handoff operations; unsupported totals are UNKNOWN, named source subsets are bounded and conditional expectations are explicit. No count comes from an artifact total or receipt instant; 24 smoke calls remain QA probes, not steady-state admin cost."
    source: "Story004 bounded primary-source comparison; actual dependency receipts and canonical terminal checks; integrated JUnit/targeted results; real CLI S1–S7 and affected S1; independent Story004 Round2 decisions."
  - criterion: "Given that same section, when time is reported, then foreground Kosmic admin active time, approval-wait/handoff delay, primary coding/analysis, necessary scientific validation and background compute appear as separated categories, overlapping workers are never summed, no speedup target or percentage is claimed, and no new report class, per-task log or framework is created (FR-011, NFR-003)."
    observation: "Foreground admin, approval/handoff, primary coding/analysis, necessary validation and background compute remain separate. Historical foreground and campaign-compute durations are UNKNOWN; 188.99s and 275.769s are software validation durations, not physics runtime or administrative savings. No overlapping worker times are summed and no speedup percentage is claimed."
    source: "Story004 bounded primary-source comparison; actual dependency receipts and canonical terminal checks; integrated JUnit/targeted results; real CLI S1–S7 and affected S1; independent Story004 Round2 decisions."
  - criterion: "Given all landed changes, when current docs, CLI guidance, examples and consumer contracts are re-exercised, then they agree with observed behavior with no consumer left on a removed mandatory flow, remaining drift gets only targeted in-scope corrections (`consumer_interface_change: true` anticipates this; [notes/cli-projection-commands.md](../../../../notes/cli-projection-commands.md) is refreshed only on observed drift, never force-rewritten), and every created/presented PRD/Architecture/Epic/Story is individually linked by its full absolute path to the actual file with receipted finished Stories re-linked at the final handoff, while historical receipts/input pins stay byte-unchanged with no historical pin refresh, install, live/global vault change or background-campaign launch (FR-012/FR-013, ADR-I)."
    observation: "Current code and guidance were integrated without touching the user index. Native canonical generate-library and validate-library passed; the updated hash-pinned CLI guideline loaded (11914 bytes) and actual canonical Story004 preparation returned eight criteria. The first three receipted Stories were individually handed off using existing full-absolute-path links; this Story own receipt/link remain the next transaction. The unrelated stale proposal validation limit was preserved, not repinned or claimed green."
    source: "Story004 bounded primary-source comparison; actual dependency receipts and canonical terminal checks; integrated JUnit/targeted results; real CLI S1–S7 and affected S1; independent Story004 Round2 decisions."
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
  review_base: "b3301180cbaebebcf033d9922a7ed79efb6c126b"
  reviewed_revision: "44136fa355b3678a1146ad16f7e8649e94fb4fc21fe77e8310c060f61caaff8a"
  findings:
    - id: "SPEC-001"
      axis: "spec"
      disposition: "Blocking"
      introduced_round: 1
      status: "resolved"
      evidence: "Story004 AC6 and ADR-H require per-case observed-versus-expected copy/record/start/CLI/handoff operation accounting; the existing table omitted several count categories or explicit UNKNOWN values."
      required_resolution: "Add compact five-operation accounting for every case, with supported observed counts or UNKNOWN and explicit expected counts/conditions; distinguish operations, artifacts, validation probes and time."
      resolution: "Added one five-category per-case observed/conditional-expected accounting table with explicit UNKNOWN totals, bounded non-probe source subsets and distinct operation/artifact/message/time units; both original reviewers approved the changed comparison in Round2."
  scope:
    - "project:subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-004.md"
    - "project:subprojects/workflow-efficiency-and-selective-delegation/specs/INDEX.md"
    - "project:subprojects/workflow-efficiency-and-selective-delegation/specs/epics/epic-001.md"
    - "project:subprojects/workflow-efficiency-and-selective-delegation/specs/epics/epic-002.md"
    - "project:notes/cli-projection-commands.md"
    - "project:skills/"
    - "worktree:memnotes/Skills/"
---

# Three-Case Efficiency Assessment and Integrated Cutover

## User Story

As the kosmic maintainer,
I want the landed efficiency mechanics (unified finish, criterion prefill, terminal-receipt retry, lean workflow, batched completion, full-path handoffs) exercised as one integrated whole and measured honestly across three representative cases,
So that efficiency findings recorded in existing notes are grounded in observed traces with explicit UNKNOWNs, and current docs, CLI guidance, examples and consumer contracts agree with actual behavior without weakening any safety gate or touching historical or global data.

This Story lands last in [Epic 002](../epics/epic-002.md) and consumes the receipted results of [Story 001](story-001.md), [Story 002](story-002.md) and [Story 003](story-003.md); their successful receipted completion is required before this Story may finish. It owns FR-011 (ADR-H) and the final FR-012 coherence check (ADR-I), exercises FR-001–FR-010 as landed behavior, and closes FR-013 on every handoff. It is the integrator, not a re-implementer: no new runtime feature, artifact class, telemetry, review-axis change, historical pin change, or install; the approved preservation guarantees (two independent axes, fixed base, stable findings under the existing max-3 ledger, terminal immutability, human gates) are consumed unchanged. Existing background scientific campaigns are untouched; no costly unrelated calculation is launched to fill a measurement gap.

## Acceptance Criteria

- [x] Given Stories 001–003 receipted `done`, when this Story's finish runs, then the existing dependency gate passes on the qualified IDs declared in this record's `depends_on`, and the integrated walkthroughs consume the landed unified finish (FR-003), read-only prefill (FR-005) and terminal-receipt retry (FR-004) instead of re-implementing them.
- [x] Given a real small or resumed episode in scoped managed scratch, when a mid-episode scope/approval change precedes the next mutating call, then the observed call rejects the stale/over-broad attempt with the existing error codes instead of proceeding on cached permission (FR-001/FR-002, ADR-A).
- [x] Given the same walkthrough covers both receipt routes, when a terminal retry follows a receipted completion and a precheck runs against stale STATUS, then the valid retry validates the completed record and immutable receipt originals and repairs only the derived STATUS reports, while the nonterminal precheck surfaces stale STATUS as explicit diagnostics without auto-repair or repinning (FR-003/FR-004, ADR-B/ADR-C).
- [x] Given low-risk and domain-risk packets in the walkthrough, when reviews run, then every packet still shows two distinct independent reviewers on the fixed base with stable finding IDs, unchanged inputs receive no fresh audit round, line count alone never excuses domain review, and a simulated full-review failure escalates rather than downgrading (FR-006/FR-007, ADR-E).
- [x] Given the walkthrough's delegation and batched completion, when checkpoints and the batched pass are exercised, then observed traces show each checkpoint justified by independence, parallelism or context isolation with bounded I/O and a named integration owner (FR-008), and one batched pass completes notes/log/publication with one appropriate canonical refresh including a changed published source, no forced note/proposal, and native-adjacent data-only metadata (FR-009/FR-010, ADR-F/ADR-G).
- [x] Given the three representative cases (small coding fix, exploratory research campaign, substantial feature), when the single bounded comparison is recorded in this Story's Technical Notes, then cases use actually available traces, elapsed is observed or UNKNOWN, mandatory manual copy/record/start/CLI/handoff counts distinguish observations from expected new-flow counts, receipt timestamps are never durations, and any necessary replay is bounded, in scope and explicitly non-comparable to missing history — never a fabricated baseline (FR-011, ADR-H).
- [x] Given that same section, when time is reported, then foreground Kosmic admin active time, approval-wait/handoff delay, primary coding/analysis, necessary scientific validation and background compute appear as separated categories, overlapping workers are never summed, no speedup target or percentage is claimed, and no new report class, per-task log or framework is created (FR-011, NFR-003).
- [x] Given all landed changes, when current docs, CLI guidance, examples and consumer contracts are re-exercised, then they agree with observed behavior with no consumer left on a removed mandatory flow, remaining drift gets only targeted in-scope corrections (`consumer_interface_change: true` anticipates this; [notes/cli-projection-commands.md](../../../../notes/cli-projection-commands.md) is refreshed only on observed drift, never force-rewritten), and every created/presented PRD/Architecture/Epic/Story is individually linked by its full absolute path to the actual file with receipted finished Stories re-linked at the final handoff, while historical receipts/input pins stay byte-unchanged with no historical pin refresh, install, live/global vault change or background-campaign launch (FR-012/FR-013, ADR-I).

## Tasks

### Phase 1: Research

- [x] Consume Stories 001–003 landed surfaces and receipts; inventory existing traces (completion logs, receipts, work records, session transcripts) per representative case, select cases by actual complete trace availability, and name the UNKNOWN gaps up front.
- [x] Map current docs/CLI guidance/examples/consumer contracts naming the affected flows for cutover scope; confirm the routine/proposal classification under the existing Task 9/P triggers.
- [x] Record findings and any human clarifications in Technical Notes.

### Phase 2: Verification-first exercises

- [x] Reuse existing behavior proofs while their inputs/contracts remain unchanged. Add a permanent red-first regression only if a newly exposed consumer-visible boundary needs one; never force passing tests red or assert source text, prose, wiring or call counts.
- [x] Consume the prior Stories' negative-boundary results and exercise changed inputs through real CLI behavior in scoped managed scratch. Delegate only when independence, useful parallelism or context isolation justifies a bounded slice and integration owner; no phase-default fanout.

### Phase 3: Comparison and cutover corrections

- [x] Execute the integrated walkthrough: single-invocation finish with prefill and a valid terminal retry repairing only derived STATUS; small/resumed work with stale-authority rejection; two-axis risk-proportional reviews; useful delegation; batched refresh with a changed published source, no forced notes, native-adjacent data; full-absolute-path links on every created/presented spec.
- [x] Record the three-case comparison in the Technical Notes comparison section strictly per ADR-H from actually inspected traces; bounded in-scope throwaway replay only where traces are insufficient, explicitly marked observed vs non-comparable, scratch removed after measurement.
- [x] Apply targeted final corrections where observed drift exists in docs/CLI guidance/examples/consumer contracts; refresh [notes/cli-projection-commands.md](../../../../notes/cli-projection-commands.md) only on observed drift.

### Phase 4: Review and completion

- [x] Run integrated checks once all affected changes are stable; rerun only changed/failed inputs or contracts; never skip scientific validation.
- [ ] Complete fixed-base two-axis independent Standards/Spec review with stable finding IDs under the existing max-3 ledger; finish through the existing checked completion contract with a receipt.
- [ ] Repeat the full-absolute-path link for every receipted finished Story (001–004) at the final human handoff.

## Routine Decision


Research outcome: no Shared Skill Library routine or `uses_routines` edge is created or changed. This approved slice extends the ordinary Project CLI backend or its existing guidance; no Task P proposal trigger was found. The false routine/proposal declarations record that classification, not an exemption from the existing gates. Canonical topics refresh only through the native authorized producer; installed skills stay unchanged.

## Technical Notes

Pre-publication verification: actual CLI exercises and independent Round 2 review are complete. Receipt creation and its final human handoff are the next transaction; their checklist rows are deliberately not claimed before publication and the bound record is not edited afterward merely to tick them.

Draft state: this section records method and scope only. The comparison subsection is written here only when actually run; no timing, count, receipt or review result is claimed by this record at draft.

- Ownership: FR-011 (ADR-H) and the final FR-012 coherent-cutover check (ADR-I, NFR-004); consumes FR-001–FR-010 as landed by Stories 001–003 and enforces FR-013 at every creation/presentation handoff.
- Comparison method: existing traces first (completion logs, receipts, work records, transcripts); case selection by actual trace availability; elapsed observed or UNKNOWN; manual operation counts distinguish observed from expected new-flow counts. Receipt `completed_at` is never a duration. Any necessary bounded in-scope replay is labeled observed and non-comparable to missing history; it never reconstructs an absent baseline.
- Accounting method: foreground Kosmic admin active time, approval-wait/handoff delay, primary coding/analysis, necessary scientific validation and background compute reported as separated categories; overlapping workers never summed; no speedup target or percentage anywhere.
- Artifact discipline: one bounded comparison section in this Story (a reusable note only if a general insight actually emerges); no new report class, per-task log, telemetry, dossier or replay framework; scoped managed scratch only during exercises, removed after.
- Safety/preservation: two independent review axes, fixed base, max-3 ledger, human gates and terminal-receipt immutability consumed unchanged; historical receipts and input pins byte-unchanged; no historical pin refresh, install, live/global vault change; existing background scientific campaigns untouched.
- `completion_observations` and review metadata are intentionally absent until actually produced; empty review data at draft is correct, never fabricated.

### Phase 1 research record (2026-10-19)

Scope: existing durable traces only — work receipts, completion logs, daily logs, evidence packs, work records, generated STATUS. Agent session memory/transcripts are not durable records and are not used as timing sources. Sources inspected (absolute paths under the original repo `/home/hexu/projects/myagentskills/kosmic/`):

- Receipts: `memnotes/Projects/kosmic/.kosmic/work-receipts/` — 14 receipts, schema `kosmic.work-receipt/1`, `completed_at` instants 2026-10-11T14:03:55Z → 2026-10-18T21:07:53Z; none contains a duration.
- Logs: `memnotes/Projects/kosmic/log/kosmic-2026-10-17.md`, `-18.md`, `-19.md`; completion logs `log/2026-10-11/12/13/18-work-completion.md` — one line per receipted record.
- Small-fix evidence: `memnotes/Projects/kosmic/evidence/2026-10-15-completion-status-coherence/` (`MANIFEST.md`, `smoke-before.json`, `acceptance.json`, `review.json`, retained code/test snapshots).
- Records: `memnotes/Projects/kosmic/specs/quick-tasks/keep-completion-status-coherent-with-terminal-receipts.md`; `memnotes/Projects/kosmic/subprojects/knowledge-first-notes-and-evidence-retirement/specs/` (prd, architecture, epic-001, stories 001–005 with completion_observations); this subproject's prd/architecture/epics/stories 001–004.
- Research-adjacent evidence: missing-mathdoc-drafts pack (scratch evidence copies) before/after = 109/109 files with byte-identical bodies; story-005 bounded-copy demonstrations (demo1–demo4) referencing the abinit NiO J₀² campaign report read-only.

Case selection by actual complete trace availability: (1) small coding fix — `kosmic/quick-task/keep-completion-status-coherent-with-terminal-receipts` (2026-10-15); (2) exploratory scientific research/campaign — `abinit/quick-task/nio-eight-cube-dielectric-comparison-and-elastic-dfpt-paper-upda` (2026-10-16→19; real governed NiO physics campaign in the global vault, read-only); (3) substantial feature — `kosmic/knowledge-first-notes-and-evidence-retirement` (2026-10-17→18, stories 001–005 receipted).

Case 2 sources (full paths, all observed; external vault read-only, never edited): governing record `/home/hexu/projects/memnotes/memnotes/Projects/abinit/specs/quick-tasks/nio-eight-cube-dielectric-comparison-and-elastic-dfpt-paper-upda.md` (quick-task, `done`, created/updated 2026-10-16, 6 acceptance criteria, composite paper+writer+project review base, `review_round: 2`); review `/home/hexu/projects/memnotes/memnotes/Projects/abinit/evidence/2026-10-16-nio-eight-cube-comparison/review.json` (round 2 approved; 3 blocking findings STD-001/STD-002/SPEC-001 all resolved; the re-review history separately tracks an initial-partial round-1 pass, a complete round-1 pass, and round 2 — round count ≠ finding count); acceptance `/home/hexu/projects/memnotes/memnotes/Projects/abinit/evidence/2026-10-16-nio-eight-cube-comparison/acceptance.json` (6/6 criteria passed); completion receipt `/home/hexu/projects/memnotes/memnotes/Projects/abinit/.kosmic/work-receipts/1179b419ed7e3616.json` (successful, `completed_at` 2026-10-19T07:47:03Z — an instant, not a duration); logs `/home/hexu/projects/memnotes/memnotes/Projects/abinit/log/abinit-2026-10-16.md`, `log/abinit-2026-10-19.md`, `log/2026-10-19-work-completion.md`. Characterization: matched shifted 8³ DFPT vs Berry-field finite-difference dielectric comparison plus elastic DFPT-vs-FD across three DFT+U models on the frozen AFM-II NiO cell, feeding a manuscript update; explicit `work start` recorded; one `scratch begin` CLI failure recorded as failed; pre-launch executable review finding STD8-1 fixed before compute and closed by restricted re-review; Main-Slurm background compute explicitly separated from the documentation-only foreground slice; failed attempts retained at source. All job IDs, evidence/archive counts, and model parameters live adjacent to the data at those sources and are deliberately not repeated here; all wall, foreground, and compute durations are UNKNOWN.

Adjacent kosmic-internal knowledge-research episodes (context only, not case material): mathdoc drafts 2026-10-13 (vault scan, 109-file before/after evidence with byte-identical bodies); shared-vault legacy cleanup 2026-10-17 (1,519-file inventory verified, 14 empty shells removed); knowledge-first story-005's four bounded knowledge demonstrations.

Routine/proposal classification confirmed under the existing Task 9/P triggers: this Story introduces no reusable deterministic mechanic and no `uses_routines` edge; the approved declaration stands and forces no proposal.

Docs/CLI cutover scope named by the landed records (consumed, not re-derived): finish/completion behavior docs owned by Story 001 (`work_completion.md`, finish help, README finish sections); prefill docs owned by Story 002 (consumer note invariant, `record_first_contract` guidance line, command-reference examples, contracts); workflow-policy/delegation/batching/handoff guidance owned by Story 003 (`skills/SKILL.md`, `task_quick_task.md`, `task_implement_story.md`, `task_review_spec.md`, `task_add_note.md`, `task_review.md`, `task_create_spec.md`, `work_completion.md` non-runtime parts, README). Story 004 re-exercises these only for observed drift; `notes/cli-projection-commands.md` refreshes only on observed drift.

### Three-case comparison (bounded) — ADR-H

Method: existing durable traces first (full citations in the Phase 1 research record above; external-vault case-2 files read-only, never edited). Elapsed is OBSERVED only where a trace records it, else UNKNOWN — all foreground, approval-wait, and campaign wall/compute durations are UNKNOWN. Authored criterion-entry counts (4 / 6 / 20) are text counts proven by artifacts, NOT hand-copy action counts; copy-action counts are UNKNOWN (no operation trace exists). Receipt `completed_at` values are instants, never durations. Accounting categories stay separated; overlapping workers are never summed; no speedup target or percentage appears anywhere.

Cases: **C1** = terminal-coherence small fix (2026-10-15); **C2** = governed NiO dielectric/elastic campaign (2026-10-16→19); **C3** = knowledge-first five-Story feature (2026-10-17→18). Their primary records, review/receipt state and source logs are cited above; artifact counts are not administrative-operation counts.

Five-category accounting: **O** = observed operations, **E** = conditional expected new-flow operations. Copy means manual exact-criterion copy actions; record means governing-record reservation/create operations; start means `work start` invocations only; CLI means Kosmic invocations, excluding physics commands and verification probes; handoff means human messages, not the number of paths in a batch. Totals are UNKNOWN without a complete trace. Named non-probe subsets below are not extrapolated into totals; the 24 current smoke calls are separate verification probes.

| Category | C1 small fix — O | C1 — E | C2 science — O | C2 — E | C3 feature — O | C3 — E |
|---|---|---|---|---|---|---|
| copy | UNKNOWN; no action trace | 0 with prefill; semantic observation authoring remains | UNKNOWN; no action trace | 0 with prefill; authoring remains | UNKNOWN; no action trace | 0 with prefill per record; authoring remains |
| record | UNKNOWN; one artifact does not prove reservation calls | 0 on valid reuse; else 1 new QT | UNKNOWN; one artifact does not prove reservation calls | 0 on valid reuse; else 1 new QT | UNKNOWN total; 5 explicit `spec-create` reservations documented | 0 on valid reuse; else 8 records for the same fresh five-Story hierarchy |
| start | UNKNOWN production total; fixture probes excluded | 1 for fresh implementation; 0 additional on resume | UNKNOWN total; at least 1 named `work start` (failed `scratch begin` is not a start) | 1 fresh; 0 additional on resume | UNKNOWN production total; smoke probes excluded | 5 for five fresh implementing Stories; 0 additional when all resume |
| CLI | UNKNOWN non-probe total | 1 finish; prefill 0/1; start 0/1; total UNKNOWN | UNKNOWN total; named subset at least 2 (`work start` and failed `scratch begin`) | 1 finish; prefill 0/1; start 0/1; total UNKNOWN | UNKNOWN total; named subsets: 5 `spec-create` reservations and 5 completion prechecks; repeated mentions are not summed | 5 finishes; prefill 0–5; start 0–5; total UNKNOWN |
| handoff | UNKNOWN total; documented entries: record approval; record status-note handoff | total UNKNOWN; individual full-path entries required; batch messages allowed | UNKNOWN total; documented entries: authorizing user request (record authority section); 2026-10-19 handoff log entry | total UNKNOWN; same entry rule | UNKNOWN total; documented approval events (PRD; amended PRD+Architecture; Epic; story batch approval — batch event ≠ per-record gates) | total UNKNOWN; same entry rule |

Expected-model conditions: resuming an already-started registered writer within its still-approved scope adds no record or start; a fresh implementation needs one start, even if its governing record already exists. A fresh bounded fix/campaign may need one QT; the same fresh five-Story feature needs eight hierarchy records, while compatible existing records require none. Prefill eliminates exact-criterion copying, not semantic observation authoring. CLI totals remain UNKNOWN because applicable STATUS, publication and formal checks vary; one unified finish replaces the former mandatory precheck+finish pair. Handoff-message totals remain UNKNOWN because approval and batching vary; each required full-path entry still appears individually within a message. Source basis: C1 record/acceptance/status note; C2 `log/abinit-2026-10-16.md` and `log/abinit-2026-10-19.md`; C3 `log/kosmic-2026-10-17.md`, `log/kosmic-2026-10-18.md` and the knowledge-first Story 005 record. No count is inferred from a receipt timestamp, file count or number of paths.

Accounting (separated, never summed): foreground Kosmic admin — UNKNOWN; approval-wait/handoff delay — UNKNOWN (approval events above are events, not durations); primary coding/analysis — UNKNOWN elapsed (artifact proxies only); necessary validation — software test-suite times observed twice: 188.99 s (case-3 cutover suite, 31 modules) and 275.769 s (integrated 934-test run) — not physics runtime and not Kosmic admin time; physics compute — Main-Slurm background, durations UNKNOWN, never summed with the documentation-only foreground slice. Other explicit UNKNOWNs: copy-action counts in every case; review rounds for knowledge-first stories 001/003/004; case-1's terminal receipt instant (documented scope-gate deferral).

Actual new-flow results (integrated smoke, final run parent-executed 2026-10-19): all seven scenarios `ok`, `overall_ok` true, exit 0, 24 real CLI invocations — counted as verification probes, not steady-state admin cost. Observed: S1 prefill exact read-only (authored adverse preserved, blank draft returned), one clean start, full returned draft applied → `ACCEPTANCE_INVALID` refusal, no receipt; S2 existing approved/not-done dependency → `COMPLETION_PRECHECK_FAILED` before publication — the baseline defect (SUCCESS receipt over an undone dependency, artifact 7107) is observed closed; S3 unified single-invocation finish succeeded with a valid receipt → linked-data evolution → terminal retry returned the receipt bytes immutable, exactly one completion-log line, derived STATUS repaired; S4 record-byte tamper refused without repinning, restore → retry valid; S5 changed-source canonical publication refreshed, no churn on unchanged sources; S6 one initial start, bound record flipped to actual draft → next mutating generate refused `WORK_PHASE_DENIED` without restart, projected bytes unchanged; S7 round-3 changes-requested review → `REVIEW_INVALID` with record/ledger bytes unchanged and no receipt, then explicit fixture repair → retry published a receipt — no automatic light fallback. One throwaway-script binding line was corrected by the parent before this final run; fixture reviewer labels remain test identities, never real approvals.

Dependency receipts (observed, integrated): stories 001–003 are receipt-completed, each through ONE unified `work finish` invocation, and the actual records plus immutable receipt bytes now live in this assessment Project; an integrated `check-completion --work-record` passed per record against the current approved ancestry and formal contracts. Successful receipts (`kosmic.work-receipt/1`; `completed_at` instants, never durations): story-001 record sha256 `0be5656c789b80f49cc59912a39294f56635ef658dd92a2937617a717109aac1`, receipt `.kosmic/work-receipts/61bc8ca6c5e8964c.json`; story-002 record sha256 `0b410dae2b8810f86087ffd66865f3301bb93afd097cb6104aa5a2498f98205b`, receipt `.kosmic/work-receipts/98b6d95ba75c148d.json`; story-003 record sha256 `727118d5cfc20707faee6e0b813b1c09ec9fd7ee86b4954b55963a60a5c0483a`, receipt `.kosmic/work-receipts/36ffff61a8de95b5.json`. Owner Index/Epic progress reflects actual 2/2 Epic 001 and 1/2 Epic 002, with only owned feature completion-log lines merged; the three local bootstrap Quick Tasks closed on their local branches (not copied into this Project) and no new global admin records exist. This Story's dependency gate is satisfiable at its own checked finish; the 004-specific two-axis review and receipted finish remain pending and are not claimed here.

Observed review and publication discipline on the integrated stories: independent Round 1 found only SPEC-001 (typed authored-field malformation; red-first new public-CLI failure, 1 failed 0.27 s); the guard fix requires criterion text + source + observation with blanks allowed and extras preserved; 7 prefill tests green in 4.22 s; ONLY the affected actual S1 was rerun while unchanged inputs received no fresh audit round — risk-proportional packets and focused-vs-integrated cadence observed (FR-006/FR-009). Round 2, same Standards and Spec reviewers, approved stories 001–003 and the four local bootstrap Quick Tasks with SPEC-001 resolved and no Standards findings. Integrated native `generate-library` + `validate-library` green; `resolve-library` + hash-pinned load exercised; the updated CLI guideline (11,914 bytes) documents the new API. Preserved limits unchanged: whole-Project `validate` exits 2 on the PRE-EXISTING unrelated stale day-delta Skill Proposal pin — historical drift outside this Story's scope, not repinned, not rewritten, not claimed green; external-vault sources and all historical receipts/pins stay byte-unchanged; no speedup target or percentage is claimed anywhere.

Observed integrated evidence (parent-reported, 2026-10-19; recorded as evidence, not AC claims): integrated pytest ran all 934 tests in 275.769 s with 932 passed and 2 environment-fixture failures (the two probes assume non-Git other-device /tmp; the parent had TMPDIR inside the repo device); the parent reran ONLY those 2 with corrected fixture inputs (`TMPDIR=/tmp`, `GIT_CEILING_DIRECTORIES=/tmp`) → 2 passed in 0.23 s — reported honestly as integrated coverage 932 + 2 with corrected fixture inputs, not one clean-suite invocation, with no runtime changes and no duplicated 932-test rerun. The new-behavior regressions passed in the integrated run: 20 finish tests (Story 001) + 6 prefill tests (Story 002). Real new-API dogfood: the integrated `work prepare-completion` was run on each actual localProject Story 001–004 — 9/6/8/8 criteria enumerated, record hashes unchanged, no generated result claims; draft payloads kept host-side for proof population (no sidecar artifact). Shared Library validation passed; native `generate-library` also succeeded on the finish and guidance roots with warning-only expected unshipped-link demotions. The first smoke run's fixture failures were corrected in the throwaway script; the final all-ok run is recorded under actual new-flow results above.

Governing record — final canonical Original-root location (full absolute path, existing persistent file): [/home/hexu/projects/myagentskills/kosmic/memnotes/Projects/kosmic/subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-004.md](/home/hexu/projects/myagentskills/kosmic/memnotes/Projects/kosmic/subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-004.md). The assessment working copy of this record (same relative path under the managed run scratch) is the pre-integration location where the Phase-1 research and actuals above were recorded; it integrates into the canonical location before this Story's finish.

## Definition of Done

- [x] User approval of this record precedes implementation; Stories 001–003 are receipted `done` and consumed by the walkthroughs.
- [x] Integrated walkthroughs are observed, including the safety-failure and history-preservation boundaries.
- [x] The single bounded three-case comparison exists in Technical Notes with UNKNOWNs, separated accounting and no new artifact.
- [x] Docs, CLI guidance, examples and consumer contracts agree with observed behavior; every correction is targeted and in scope.
- [x] Historical receipts/pins byte-unchanged; no live/global vault, install or background-campaign change.
- [ ] Fixed-base two-axis review approved under the existing max-3 ledger; successful checked finish with receipt; final handoff repeats full-absolute-path links for every receipted finished Story.
