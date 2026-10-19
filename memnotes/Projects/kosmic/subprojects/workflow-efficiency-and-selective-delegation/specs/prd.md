---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: "draft"
record_kind: "prd"
local_id: "prd"
---

# Workflow Efficiency and Selective Delegation

## Problem Statement

Kosmic already permits reuse of authorized records, record-free questions and
sessions with no new notes. The common path still requires manual criterion
copying and separately orchestrated completion prechecks and finish; review
packets have no explicit proportionality rule. Repeated orientation and
phase-based delegation can add avoidable foreground coordination when the
instructions are applied mechanically. Coding, scientific analysis and
necessary verification must remain the primary work.

The user approved this direction, not this PRD or implementation. Initial
retrieval found partial case logs and receipts, not a comparable elapsed-time
baseline. Successful scratch logs are ephemeral; receipt timestamps are not
durations. Missing measurements must remain UNKNOWN, with observable
coordination-operation counts reported separately.

## Goals

- One bounded episode: reuse the existing authorizing record when it already
  covers the work; otherwise choose Quick Task vs full spec by actual scope
  and risk, with questions, searches, and unchanged-state checks always
  record-free.
- One unified safe completion invocation covers all required prechecks and
  scope/proof/review gates before done or receipt publication. Necessary
  authority and source-freshness rechecks remain; redundant manual
  orchestration is removed, not safety checks.
- Deterministic criterion prefill from the governing record and
  risk-proportional review packets, eliminating manual exact copying without
  generating any result/reviewer/approval claims.
- Discretionary, justified subagent use; batched knowledge/log/publication
  completion; honest three-case measurement.
- Direct artifact access: creation and Story-completion reports expose each
  actual record file through a Markdown link displaying its full absolute path.
- Preserve all existing safety invariants: two independent review axes,
  fixed review base, source-revision pins, record/worktree isolation, human
  gates, and terminal-receipt retry invariance.

## Non-Goals

- No collapsing the two independent review axes into one reviewer or reducing
  reviewer count. The prior approved design retains independence;
  proportionality changes packet scope, depth and convergence.
- No new artifact classes: no per-task timing logs, telemetry pipelines,
  dashboards, report files, sidecars, or completion dossiers.
- No skip paths: no skipped math/scientific, proposal, related-notes,
  projection, STATUS, or dependency gates; no self-exemption; no light-mode
  fallback when full review fails; no autopromotion, approval, repinning, or
  out-of-scope publishing to green.
- No change to mandatory fresh-context global/shared proposers, independent
  reviews, host/harness mandatory delegation, review round structure
  (rounds 1–3, fixed base), or source_revision semantics.
- No permanent baseline-capture/replay framework. Bounded comparisons belong
  in this feature's approved research or implementation scope after the PRD
  gate; no live/global vault or installation changes.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Single-episode work start: if an existing record already authorizes the work, reuse it — no new record. Otherwise pick Quick Task (bounded, low-risk, well-understood change) or full spec by actual scope and risk. Questions, code search, and verification that inputs are unchanged are record-free. A record starts work once; resuming continues within its own scope and edits without restarting, extra records, or a fresh worktree per step. | must |
| FR-002 | Every mutating CLI re-derives fresh identity, scope, and approval checks at invocation — context may be reused while valid, permission is never cached. Existing worktree and record isolation are preserved; a resumed episode may not silently widen its recorded scope. | must |
| FR-003 | Unified safe completion: one ordinary non-terminal finish invocation runs every currently required full precheck plus scope/proof/review gates before publishing done or a receipt. Standalone precheck remains diagnostic/fail-fast. Preserve math/scientific, proposal/routine, related-note, projection, STATUS, dependency and authority checks, existing publication order and legacy compatibility. Freshness rechecks needed to prevent races remain; users need not choreograph two commands. | must |
| FR-004 | Terminal-receipt retry invariance: verify the completed record and applicable immutable receipt originals without re-hashing evolving raw notes/data, recomputing the current dirty-source review binding or refreshing historical pins. Preserve existing identity/ancestry and declared formal math/proposal/routine contracts; reject changed record bytes or invalid/missing receipt originals. A receipt records completion history, not perpetual scientific correctness. | must |
| FR-005 | Deterministic criterion prefill: completion pulls each criterion verbatim from the governing record, so no manual exact copying; authored observations and adverse findings are retained and prefilled alongside. The mechanism generates no results, reviewer statements, or approval claims; an entry lacking required content is still rejected at finish. No sidecar or new dossier artifact; exact API/flag shape is an Architecture decision. | must |
| FR-006 | Risk-proportional review packets: low-risk Quick-Task-class changes carry a bounded packet of the actual delta plus acceptance context, and unchanged inputs receive no fresh audit round. Findings stay on the fixed base with stable identifiers and the max-3 bound. Numerics/scientific claims, methods, security, and API/data/schema/publication/receipt changes get stronger domain review. Risk is judged from content and blast radius, never line count alone. | must |
| FR-007 | Retain two distinct independent review axes, the fixed base, stable finding ledger and rounds 1–3. Re-review keeps its existing findings and checks the changed evidence rather than resetting context into a fresh audit. Fresh-context shared/global proposers remain separate. Failed review escalates under the existing limit; it never downgrades to a light pass. | must |
| FR-008 | Subagent checkpoints are used only for genuine independence, useful parallelism, or context isolation. Discretionary delegation requires a concrete bounded question or slice with explicit input/output and a named integration owner; no phase-default fanout, tiny clerical delegation, nested exploration without benefit, or authority expansion. Coupled work has one owner; fresh-context proposer independence and host-mandated delegation are untouched; avoid unnecessary extra workers. | must |
| FR-009 | Focused checks run during work; integrated verification runs once after affected changes stabilize. Re-run only checks whose inputs or contracts changed or previously failed — never reuse a pass over changed inputs and never skip scientific validation to save time. | must |
| FR-010 | Batched completion: knowledge notes, log entries, and publication completion for the same episode are batched into one pass (one appropriate canonical refresh per batch; content changes to published note sources still count and refresh). Optional curation and skill proposals stay off the primary critical path unless correctness requires immediate action. No forced note/proposal/publication, no extra queues or dashboards; single-dataset context remains native-adjacent per the knowledge-first PRD. | must |
| FR-011 | Honest measurement: assess three representative cases — small coding fix, exploratory research campaign, substantial feature — using existing traces/records/logs first. Where elapsed time is unavailable, record UNKNOWN and count mandatory manual copy/record/start/CLI/handoff operations; never infer elapsed overhead from receipt completion timestamps. Foreground KOSMIC admin/approval/handoff delay is separated from primary coding/analysis and necessary validation/background compute; overlapping workers do not add duration. Findings land in one bounded comparison in existing feature Research/Story Technical Notes (or one reusable note if a general insight emerges) — not new per-task logs. Existing traces are partial; gaps are reported as unknown, not reconstructed. | must |
| FR-012 | Documentation/contract cutover: at implementation time, current docs, CLI guidance, examples, and contract tests are updated coherently; historical receipts and input pins remain byte-immutable; no live/global vault or install changes outside existing approval boundaries. | must |
| FR-013 | Accessible artifact handoffs: whenever a PRD, Architecture, Epic or Story is created or presented for approval, the human-facing response must include a Markdown link whose visible label is that file's full absolute path and whose target opens the actual file. List every created file individually in a batch; a directory, index link, shortened filename or relative path is not a substitute. After successful receipted Story completion, repeat the full-path link for every finished Story. Use the actual persistent record location; if integration changes that location, report its final canonical link too. Do not invent future paths, replace machine-readable CLI output, or imply that review approval alone means completion. | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Efficiency: fewer avoidable coordination steps in small-fix and research cases; no duplicated review rounds over unchanged inputs; batched rather than item-by-item completion. | must |
| NFR-002 | Safety: all strong guards unchanged — two independent axes, fixed base, full prechecks, human gates, terminal-receipt immutability; efficiency never weakens a gate, only removes redundant repetition of the same check over the same inputs. | must |
| NFR-003 | No artifact growth: zero new mandatory artifact classes, sidecars or telemetry files; measurement reuses existing traces and at most one bounded comparison section in an existing feature record. | must |
| NFR-004 | Coherence: at cutover, runtime behavior, docs, and contract tests agree; no consumer left on removed mandatory flows. | should |

## Success Criteria

Observable whole-workflow checks (each includes the stated negative boundary):

- [ ] Small coding fix: bounded work starts once on the right record, resumes across steps without restart/extra record/worktree, and finishes through the unified path with a risk-proportionate packet — no second fresh audit round over unchanged inputs and no new record per step.
- [ ] Mutating CLI mid-episode: after scope/approval change, the next mutating call re-checks and rejects a stale/over-broad attempt rather than proceeding on cached permission.
- [ ] Unified finish on a feature story: one invocation exercises every applicable completion gate before done/receipt publication; deliberately invalid dependency, authority, scientific, proposal or projection state blocks finish without a completion receipt. Standalone precheck remains available, and no internal call-count assertion substitutes for these behaviors.
- [ ] Criterion prefill supplies exact criterion text without manual copying but requires actual authored observations and review before finish. It preserves adverse findings, invents no result or approval, rejects incomplete/unknown coverage and refuses to rewrite a completed record.
- [ ] Terminal retry: ordinary linked-note/data evolution does not revoke a valid historical receipt or rewrite its pins; record-byte tampering and missing/changed immutable originals still fail. Existing declared formal contracts remain checked.
- [ ] Two-axis preservation: every review in the packet — including a low-risk one — shows two distinct independent reviewers on the fixed base; a simulated full-review failure escalates rather than downgrading to a light pass; a line-count-only "trivial" label does not bypass domain review for an API/schema change.
- [ ] Existing execution traces or the bounded assessment show discretionary delegation tied to independence, useful parallelism or context isolation, with bounded inputs/outputs and ownership; no new per-task delegation report is required, and mandatory proposer/reviewer independence remains.
- [ ] Batched completion: one episode's note + log + publication complete in one batched pass with one canonical refresh; no forced note/proposal; measured three-case assessment reports observed timings where traces exist and UNKNOWN (with operation counts) where they do not — no fabricated baseline or percentage.
- [ ] Creating or presenting a PRD, Architecture, Epic or Story produces an individually clickable full-absolute-path link to each existing record file. Completing one or several Stories repeats those links for all receipted finished Stories, including final canonical locations after integration; filename-only, directory-only, relative or nonexistent links do not satisfy the requirement.

## Open Questions

- Architecture must choose comparable bounded cases and any necessary replay within approved scope; missing historical timings must not be reconstructed from completion timestamps.
- Exact prefill API/flag surface and packet-sizing heuristics — Architecture decisions.
- Reviewer-count consolidation is excluded; changing the prior independence decision requires explicit approval of a revised scope.

## Related Knowledge

- [Knowledge-first PRD](../../knowledge-first-notes-and-evidence-retirement/specs/prd.md) — compact completion, immutable history and incremental curation.
- [Knowledge-first Architecture](../../knowledge-first-notes-and-evidence-retirement/specs/architecture.md) — ADR-B's independent-review and record-embedded proof boundaries.
- [Terminal-receipt coherence Quick Task](../../../specs/quick-tasks/keep-completion-status-coherent-with-terminal-receipts.md) — existing retry semantics.
- [Note writing style](../../../notes/note-writing-style.md) and [Shared Skill Library](../../../notes/shared-domain-skill-library.md) — conditional capture and coherent publication.
