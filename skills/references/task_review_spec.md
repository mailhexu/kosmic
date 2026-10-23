# Task: Review Spec

Review specifications, optional research memos, and code. Mandatory for story completion.

## When to Use

- Reviewing a spec document (PRD, Architecture, Epic, Story)
- Reviewing a Research memo for completeness before Architecture
- Story implementation complete, needs code review
- User says: "review this", "approve spec", "code review"

---

## Part 1: Spec Review

Review spec documents before implementation begins.

### PRD Review Checklist

| Aspect | Check |
|--------|-------|
| Problem | Is the problem clearly stated? |
| Goals | Are goals specific and measurable? |
| Non-goals | Is scope clearly bounded? |
| Requirements | Are FRs/NFRs complete and prioritized? |
| Success Criteria | Can each criterion be objectively verified? |
| Open Questions | Are all blockers identified? |

**Decision**: 
- ✅ **Approve** → status: `approved`
- ⚠️ **Request Changes** → Add comments, keep `draft`
- ❌ **Reject** → Major rework needed

### Architecture Review Checklist

| Aspect | Check |
|--------|-------|
| ADRs | Is every significant decision documented? |
| Context | Is the "why" clear for each decision? |
| Alternatives | Were alternatives considered and evaluated? |
| Consequences | Are trade-offs documented? |
| Test Strategy | Is testing approach defined? |
| Risks | Are risks identified with mitigations? |

**Decision**:
- ✅ **Approve** → status: `approved`
- ⚠️ **Request Changes** → Add comments
- ❌ **Reject** → Fundamental issues

### Research Memo Checklist (Non-Gating)

Research review does not approve or block the main spec lifecycle. It checks whether the memo is useful input for Architecture.

| Aspect | Check |
|--------|-------|
| Question | Is the uncertainty or decision clearly stated? |
| Sources | Are notes, code, docs, or examples cited? |
| Findings | Are findings specific and evidence-backed? |
| Options | Are viable options compared with trade-offs? |
| Recommendation | Is the recommended direction justified? |
| Impact | Is Architecture/ADR impact clearly stated? |
| Open Questions | Are unresolved blockers captured? |

**Decision**:
- ✅ **Complete** → status: `done`, link from Architecture
- ⚠️ **Needs More Research** → keep `draft`, list missing evidence/questions

### Epic Review Checklist

| Aspect | Check |
|--------|-------|
| Value | Does this epic deliver standalone value? |
| Scope | Is in/out of scope clear? |
| Stories | Can this be broken into stories? |
| Success | Are completion criteria defined? |

**Decision**:
- ✅ **Approve** → status: `approved`
- ⚠️ **Request Changes** → Add comments

### Story Review Checklist

| Aspect | Check |
|--------|-------|
| User Story | Is it in proper format (As a... I want... So that...)? |
| Acceptance Criteria | Are all criteria testable? |
| Tasks | Are research/test/impl/review phases present? |
| DoD | Is Definition of Done complete? |
| Links | Are epic/architecture/PRD linked? |

**Decision**:
- ✅ **Approve** → status: `approved`, ready for implementation
- ⚠️ **Request Changes** → Add comments

---

## Part 2: Code Review

**MANDATORY**: Story cannot reach `done` status without one convergent code-review session.

Use `code-review` for the method: pin the fixed base, review Standards and Spec independently, and preserve both axes in the Kosmic ledger. The local Story or Quick Task is the Spec-axis source; do not require an external issue tracker.

### 2.1 Pin the Review Scope

Before reviewing, record a stable `review_base` in the work item and resolve it. Review the complete change between that fixed point and the current implementation. Also identify:

1. **Spec sources** — originating story, acceptance criteria, PRD, and Architecture.
2. **Standards sources** — Project contribution guidance, documented conventions, and applicable ADRs.
3. **Verification evidence** — focused tests, completion gate, diagnostics, and relevant smoke checks.

An invalid base, empty change, or missing originating spec stops the review. Do not let successive rounds silently change the baseline or acceptance criteria.

### 2.2 Bound the Packet to the Actual Risk

The review packet covers the actual delta plus its acceptance context drawn from the governing record and ledger: fixed review base, acceptance criteria, embedded observations, checks, and adverse facts. Proportionality changes packet scope and depth only — every review, including a low-risk one, still shows two distinct independent Standards/Spec reviewers on the fixed base, stable finding IDs, and rounds 1–3 with the existing escalation. A failed review escalates under that limit; it never downgrades to a light pass.

Stronger domain review is triggered by category, never by line count: numerics/scientific claims, methods, security, and API/data/schema/publication/receipt changes always receive the relevant domain review, with risk judged from content and blast radius. Unchanged inputs receive no fresh audit round; a changed input or contract, or a previously failed check, reruns only the affected checks on the fixed base.

### 2.3 Round 1: Complete Two-Axis Review

Round 1 must report the complete known finding inventory in one pass. Review both axes independently, then present them side by side without allowing one axis to mask the other.

#### Standards axis

Check the entire scoped change against documented Project standards. Also identify judgement-call smells: mysterious names, duplication, feature envy, data clumps, primitive obsession, repeated switches, shotgun surgery, divergent change, speculative generality, message chains, middle men, and refused bequests.

- Cite the standard and location for a hard violation.
- Label smells as judgement calls; they are non-blocking unless they demonstrate a concrete correctness, security, performance, or maintainability failure required by the spec.
- Skip concerns already enforced and passed by deterministic tooling.
- For mathematical changes, inspect the executable derivation before dependent prose or code. Verify assumptions, domains, units, conventions, generated-result currency, and adjacency of each source `MathDoc:` reference. A green `check-math` proves consistency, not physical correctness.

#### Spec axis

Check the entire scoped change against the originating requirements:

- missing or partial requirements;
- unrequested behavior or scope creep;
- behavior that appears implemented but is incorrect.

Every finding must cite the requirement and concrete implementation evidence.

### 2.4 Stable Finding Ledger

Before requesting changes, publish the complete issue inventory in a persistent ledger. IDs never change between rounds:

- `STD-{NNN}` for Standards findings;
- `SPEC-{NNN}` for Spec findings;
- `REG-{NNN}` for regressions introduced by a fix;
- `LATE-{NNN}` only for a critical correctness or security issue missed in Round 1.

Each finding records axis, blocking disposition, evidence, required resolution, introduced round, and status. Classify findings as:

- **Blocking** — incorrect behavior, unmet acceptance criterion, regression, security/data-loss risk, failing required verification, or a documented standard violation that makes the change unacceptable.
- **Non-blocking** — optional refactor, style preference, speculative hardening, or smell without a demonstrated contract failure.

Only Blocking findings can produce `Changes Requested`. Non-blocking suggestions remain visible but do not prevent approval.

### 2.5 Re-review Contract

Later rounds are verification rounds, not fresh reviews. They may inspect only:

1. unresolved Blocking findings;
2. code changed since the previous reviewed revision;
3. tests and behavior affected by those changes;
4. regressions introduced by a fix.

Do not open a new finding against unchanged code. The only exception is a critical correctness or security defect supported by new concrete evidence; record it as `LATE-{NNN}` with why Round 1 missed it. A fix-introduced defect is `REG-{NNN}` and must link to the finding whose resolution caused it.

Resolve each prior ledger row as `resolved`, `still-open`, or `regressed`; never replace the ledger with a new list. Suggestions cannot be promoted to Blocking without new contract evidence.

### 2.6 Coordinator Readiness Barrier, Handoff, and Round Counting

**Readiness barrier.** Before submitting routine re-review, every unresolved Blocking row needs a complete worker response: `fixed` plus observable evidence, or `refuted` plus rationale and evidence. Unaddressed, partially repaired, or changed-unresolved Blocking rows are **held** — holding consumes no round and does not restart counting; the complete payload proceeds without restarting round counting. Worker assertions never close findings. A genuinely blocked prerequisite is recorded (`kind: blocked` with prerequisite and escalation rationale/evidence) and escalated explicitly to the coordinator; that path is distinct from routine review submission and never enters it.

**Frozen handoff.** The coordinator assembles and freezes one identical actual payload and delivers it to both independent axes on one held target: record identity/path, fixed base, prior and current reviewed revisions, the complete ledger with per-finding responses, changed targets, affected checks/results, requested pair/round, unchanged non-blocking exclusions, and any escalation. Convey the held payload through agent messages or managed scratch **outside the reviewed source worktree** (or existing excluded Project metadata, as applicable) — never as new files inside the reviewed delta, which would change `source_revision` and self-invalidate the fingerprint; no new persistent artifact, sidecar, or storage class. `source_revision` excludes nested Project record bytes and cannot stand in for the payload snapshot: if the nested record/context changed while the computed revision is unchanged, recheck the changed context and re-freeze the handoff. No persistent context hash or sidecar.

**Round counting.** Round 1 is the full review; **one completed Standards + Spec pair on the held snapshot is exactly one automated round**, never two. The requested pair/round number rides the frozen handoff as a request; the record's `review_round` count advances only after **both** axes of that pair complete — never pre-incremented at submission, and never a new counter field. Worker repairs and partial callbacks consume no round. Changes-requested at Round 2 continues into Round 3; no fourth round starts. At the cap the coordinator issues an explicit human decision packet — the existing ledger, attempted resolutions, and a concrete decision ask — never a reset, a fourth round, or a manufactured approval.

**Refutation outcomes.** Reviewer acceptance of a fix or refutation closes via the existing `status: resolved`, optionally `resolution: fixed|refuted`, preserving the original finding and refutation rationale. A rejected refutation leaves the row open/Blocking with the rationale retained. No new closure status is introduced; no retroactive reviewer version/hash/resolver fields are added.

### 2.7 Preparation and Decision

Use the required tests and focused smoke observations for the changed behavior; run diagnostics only for an actual error or unresolved finding. Checked `work finish` runs the Consumer Interface completion gate internally, so review adds no standalone completion precheck or post-success audit. Approve when all Blocking findings are resolved and verification passes, even if Non-blocking suggestions remain.

**Approve**:
```markdown
## Review Result

**Status**: ✅ Approved

**Summary**: Implementation meets all acceptance criteria.

**Highlights**:
- Good test coverage
- Follows existing patterns
- Clean implementation

**Reviewer**: {name/ai}
**Date**: {DATE}
```

Record the approved decision; retain the live implementation record until receipt-backed `work finish` publishes `done`. A provisional status word is not completion.

**Request Changes**:
```markdown
## Review Result

**Status**: ⚠️ Changes Requested
**Round**: {N}
**Reviewed Revision**: {revision or working-tree fingerprint}

**Open Blocking Findings**:
- {stable finding IDs}

**Resolved This Round**:
- {stable finding IDs}

**Non-blocking Suggestions**:
- {stable finding IDs; do not block approval}

**Reviewer**: {name/ai}
**Date**: {DATE}
```

Update story status back to `in_progress` without discarding the ledger.

**Reject** (rare, major issues):
```markdown
## Review Result

**Status**: ❌ Rejected

**Reason**: {fundamental issue}

**Recommended Action**: {what to do}

**Reviewer**: {name/ai}
**Date**: {DATE}
```

Update story status to `draft` or create new story.

---

## Review Output Format

Keep one ledger in the story or quick-task record and update it in place:

```markdown
## Code Review

**Review Base**: {fixed point}
**Current Round**: {N}

### Standards

| ID | Disposition | Evidence | Required Resolution | Introduced | Status |
|----|-------------|----------|---------------------|------------|--------|
| STD-001 | Blocking | {standard + location} | {required fix} | Round 1 | open |
| STD-002 | Non-blocking | {smell + location} | {optional improvement} | Round 1 | suggested |

### Spec

| ID | Disposition | Evidence | Required Resolution | Introduced | Status |
|----|-------------|----------|---------------------|------------|--------|
| SPEC-001 | Blocking | {requirement + location} | {required fix} | Round 1 | open |

### Re-review History

| Round | Reviewed Revision | Findings Checked | New REG/LATE Evidence | Decision |
|-------|-------------------|------------------|-----------------------|----------|
| 1 | {revision} | complete first-pass inventory | n/a | changes requested |
```

---

## Status Transitions

### After Spec Review

```
draft ──[approve]──→ approved
draft ──[changes]──→ draft (with comments)
```

### After Code Review

```
in_progress ──[approve: decision recorded in completion_review]──→ in_progress (active phase kept; checked finish still required)
review ──[changes]──→ in_progress
approved/in_progress ──[verified work receipt via checked finish]──→ done
```

Checked `work finish` refuses a record set to `review` (`WORK_PHASE_DENIED`); it accepts `approved`/`in_progress` and alone writes `done`. Record the review decision in the embedded `completion_review` mapping while keeping the record in its active phase — never strand a record in `review` expecting finish; a record sitting in `review` returns to `in_progress` before finishing.

### Convergence Limit

Allow at most three automated rounds, counted by completed Standards + Spec pair on the held snapshot: one complete initial review and two re-review rounds. Worker repairs and partial callbacks consume no round. If Blocking findings remain after Round 3, stop autonomous review cycling. Keep the story `in_progress` and escalate the existing ledger — with attempted resolutions and a concrete human decision ask — for a human scope or design decision; do not start another unrestricted review, reset, or begin a fourth round. A failed or incomplete full review never downgrades to a light pass — the escalation is the only exit from the limit.

---

## Update Log

```markdown
## Session {N}
- Reviewed: [Story 001](../subprojects/{SUBPROJECT_ID}/specs/stories/story-001.md) - ✅ Approved
- Reviewed: [PRD](../subprojects/{SUBPROJECT_ID}/specs/prd.md) - ⚠️ Changes requested
```

Before preparing implementation-review proof or completing a record, load
[Receipt completion](work_completion.md). Review decisions and lifecycle
completion are separate; only checked finish publishes the successful receipt.

---

## Checklist

### After Spec Review
- [ ] All checklist items evaluated
- [ ] Decision documented in spec
- [ ] Status updated
- [ ] Log updated

### After Code Review
- [ ] All code reviewed
- [ ] All tests verified passing
- [ ] Review result documented in story
- [ ] Story status updated
- [ ] Log updated

## STATUS.md

After changing any spec or work-item status, run `generate-status --project ...`. Validation fails `STATUS_STALE` while the generated file drifts.
