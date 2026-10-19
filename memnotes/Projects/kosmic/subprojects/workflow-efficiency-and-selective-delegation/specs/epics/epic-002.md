---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: "approved"
record_kind: "epic"
local_id: "002"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories:
  - "../stories/story-003.md"
  - "../stories/story-004.md"
---

# Lean Workflow, Accessible Handoffs and Measured Overhead

## Description

Leaner exercise of the approved safety machinery, not new machinery: reuse the existing authorizing record, worktree, and
still-valid context; risk-proportional packets that keep both independent axes, the fixed base, and the max-3 bound;
discretionary justified subagent use; batched note/log/publication completion; honest measurement in existing notes; and
individually clickable full-absolute-path links on every human handoff. Grounded in ADR-A/E/F/G/H/I, covering
FR-001/002/006/007/008/009/010/011/013 plus FR-012 source-guidance/examples/contract cutover. The runtime completion
engine (unified finish, terminal-receipt route, criterion prefill — ADR-B/C/D) is owned by [Epic 001](epic-001.md);
this Epic consumes that behavior, no duplicate implementation. Specs: [PRD](../prd.md), [Architecture](../architecture.md).
Policy and handoff improvements can land independently; the final integrated
assessment and cutover require Epic 001's mechanics and both Epics' results.

## Scope

### In

- Reuse-before-create inside the existing record's scope; resume continues without restart, extra records, or a fresh
  worktree and never widens recorded scope; questions, code search, and unchanged-input checks stay record-free; every
  mutating CLI re-derives identity, ancestry, scope, and approval live — permission is never cached (ADR-A).
- Risk-proportional packets: delta plus fixed context (base, criteria, checks, adverse findings); exactly two distinct
  independent Standards/Spec reviewers; stable findings, max 3 rounds unchanged on the fixed base; no fresh audit over
  unchanged inputs, only changed/failed inputs rerun; failed full review escalates, never light fallback; domain risk
  (science/numerics, methods, security, API/data/schema, publication/receipt) never excused by line count (ADR-E).
- Discretionary delegation only for independence, useful parallelism, or context isolation, each with bounded
  question/slice and I/O, a named integration owner in the launch trace, one owner for coupled work; host/proposer/
  reviewer mandates untouched; no new delegation artifact. Cadence: focused checks during work, integrated verification
  once changes stabilize, reruns for changed inputs/contracts or failed checks, scientific validation never skipped (ADR-F).
- Batched note/log/publication completion for one episode, one appropriate canonical refresh per batch including changed
  published source bytes/content/status/audience/staleness; nothing forced; optional curation off the critical path
  unless correctness requires; data-only metadata native-adjacent (ADR-G).
- One bounded three-case comparison (small fix / research campaign / substantial feature) in existing feature Research
  or Story Technical Notes: traces first, observed timing or UNKNOWN, explicit observed-vs-expected operation counts,
  no receipt-timestamp durations, no invented percentages; admin/approval-handoff/coding-analysis/science-validation/
  background reported separately; overlapping workers never sum (ADR-H).
- Cutover of source docs, CLI guidance, examples, and contract tests to the exercised behavior; receipts and pins
  byte-immutable; no live/global vault or install changes (ADR-I, FR-012).
- FR-013: every created/presented PRD/Architecture/Epic/Story is individually linked — full absolute path as visible
  label, actual file as target; receipted finished Stories re-linked with final canonical paths after integration; no
  future/relative/index/dir substitutes; machine CLI JSON untouched; approval is not completion.

### Out

- Runtime completion engine implementation (unified finish, terminal-receipt route, criterion prefill CLI — Epic 001
  owns, consumed here); reviewer reduction or single-axis consolidation, which needs revised approval.
- Permission caching, new telemetry, queues, schedulers, completion dossiers, timing logs, or new artifact classes;
  installation, live/global vault, or historical receipt/pin changes.

## Stories

- [Story 003: Lean Workflow and Accessible Artifact Handoffs](../stories/story-003.md) — draft; can progress independently of runtime mechanics.
- [Story 004: Three-Case Efficiency Assessment and Integrated Cutover](../stories/story-004.md) — draft; depends on Stories 001–003.

## Success Criteria

- [ ] A real small or resumed workflow starts once on the right existing record and continues across steps without
      restart, extra record, or fresh worktree; after a mid-episode scope/approval change the next mutating call
      rejects the stale/over-broad attempt instead of proceeding on cached permission.
- [ ] A two-axis fixed-base re-review on a low-risk packet shows two distinct independent Standards/Spec reviewers with
      stable finding identifiers and no fresh audit over unchanged inputs; a simulated full-review failure escalates
      rather than downgrades; an API/schema-class change is not exempted from domain review by line count.
- [ ] Existing traces show discretionary delegation: each checkpoint justified by independence, parallelism, or context
      isolation, with bounded input/output, a named integration owner in the launch trace, coupled work under one
      owner, and no new delegation artifact.
- [ ] One episode's notes, log, and publication complete in a single batched pass whose canonical refresh includes a
      changed published note source; nothing forced; data-only metadata native-adjacent.
- [ ] Every created or presented PRD/Architecture/Epic/Story in the exercised flows carries an individual
      full-absolute-path link to the actual file; receipted finished Stories are re-linked including final canonical
      paths after integration; machine CLI JSON unaltered.
- [ ] The three-case comparison exists as one bounded section in existing feature Research/Story Technical Notes:
      observed timings or UNKNOWN with explicit observed-vs-expected operation counts and separated time categories —
      no receipt-timestamp durations or invented percentages.
- [ ] Current docs, CLI guidance, examples, and contract tests are coherent with the exercised behavior, no consumer
      left on a removed mandatory flow; historical receipts and pins byte-unchanged.

## Progress

Approved by the user; two draft Stories, neither implemented nor receipted.
Each Story needs its own approval. Success evidence comes from observed flow
exercises, never source-text or wording checks; criteria remain unchecked.
