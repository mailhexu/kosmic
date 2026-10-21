---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: "draft"
record_kind: "epic"
local_id: "002"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: []
---

# Complete worker responses and convergent review handoffs

## Description

Make re-review converge on complete worker responses and a coordinator-owned, bounded handoff over the existing ledger. Finding annotations remain additive and backward-compatible runtime data; the readiness barrier, unchanged-input exclusions, and two-axis handoff are host workflow responsibilities, not a new execution engine or proof of agent identity.

## Scope

### In Scope

- Add optional per-finding `worker_response` annotations (`fixed`, `refuted`, or `blocked`) with coherent, inspectable detail and evidence. Fixed/refuted claims require non-empty detail and evidence; a blocked response identifies the prerequisite and escalation rationale/evidence. A response is a worker claim, never a reviewer decision.
- Preserve native completion compatibility: validate supplied annotation/resolution shape and coherence while accepting old closed findings and existing risk-accepted fields unchanged. Reviewer acceptance closes a fix or refutation using existing `status: resolved`, optionally `resolution: fixed|refuted`; rejected refutation remains open and Blocking, with the original finding and refutation rationale/judgment retained.
- Establish the coordinator’s pre-submit barrier and handoff on existing records and ledgers: hold unaddressed or partial Blocking findings; escalate a genuine prerequisite blocker instead of submitting routine re-review; carry record identity/path, fixed base, prior and current reviewed revisions, complete ledger and responses, changed targets, affected checks/results, requested pair/round, exclusions, and any escalation.
- Require both independent axes to receive the identical actual record/ledger/acceptance payload on one held target. `source_revision` alone is not a snapshot of nested record bytes or acceptance context; keep the target stable and recheck changed context.
- Keep Round 1 a full review. Later rounds cover unresolved findings, changed behavior and affected checks, linked fix-introduced `REG`, and evidence-backed critical `LATE` findings that explain why Round 1 missed them. Ordinary unchanged-code/style findings remain non-blocking follow-ups.
- Count one completed Standards + Spec pair on the held snapshot as one round. Worker repairs and partial callbacks consume no round; changes-requested at Round 2 continues to Round 3; at the three-round cap, return an explicit human decision packet without a fourth round or reset.

### Out of Scope

- New finding statuses, mandatory retroactive resolver/version/identity/hash fields, or invalidation of existing closed rows and accepted-risk annotations.
- A new review CLI, engine, journal, sidecar, context hash, persistent round artifact, or authentication of the agent process; no edit to the upstream generic code-review skill or installed copies.
- Permanent prose tests. Use real producer/coordinator handoff traces as evidence; retain runtime guards for annotation shape and final metadata/freshness.

## Stories

1. **Compatible finding-response/refutation annotations**
2. **Coordinator readiness and bounded re-review handoff** — depends on **Compatible finding-response/refutation annotations**.

## Requirement Coverage

- **FR-001 / FR-003:** complete responses before routine review; reviewer-owned closure for fixes/refutations and escalation for genuinely blocked prerequisites.
- **FR-002 / FR-005:** complete same-snapshot handoff to both axes; pair-based round count, Round-2 continuation, stable base, and maximum-three decision packet.
- **FR-004:** bounded later-round scope, including linked `REG`, evidence-backed critical `LATE`, and non-blocking ordinary unchanged/style follow-ups.
- **FR-009; NFR-001, NFR-003, NFR-004:** reuse existing ledger/record surfaces, preserve safety and visible response states, and add no persistent artifacts or mandatory prose tests.

## Success Criteria

- [ ] Routine re-review is held for every unaddressed or partial unresolved/changed Blocking finding; a genuine prerequisite blocker is recorded and escalated rather than submitted as routine review. Unchanged previously resolved rows require no retroactive response fields.
- [ ] A worker’s evidence-backed fixed/refuted response closes nothing by itself. Reviewer acceptance uses existing resolution semantics; rejection leaves the finding open and Blocking while retaining its rationale.
- [ ] Both axes receive the same actual record, full ledger/responses, and acceptance payload for one stable target, including base and prior/current reviewed revisions; a source-revision match alone cannot stand in for this payload snapshot.
- [ ] One complete Standards + Spec pair consumes exactly one round; partial repairs consume none; Round 2 changes-requested proceeds to Round 3; no fourth round starts and the cap produces a concrete human decision packet.
- [ ] Later-round review includes only unresolved findings, changed behavior/affected checks, linked fix-introduced `REG`, or critical evidence-backed `LATE` with why it was missed in Round 1; ordinary unchanged/style issues stay non-blocking.
- [ ] Existing closed-row and risk-accepted forms remain valid without retroactive fields; supplied annotations are checked for coherent structure, and worker assertions remain distinct from reviewer resolution.
- [ ] Real producer/coordinator traces demonstrate readiness, same-payload two-axis handoff, pair-round counting, Round-2-to-3 continuation, and cap behavior; no permanent prose-test suite is added.

## References

- [Approved PRD](../prd.md)
- [Approved Architecture](../architecture.md)
- [CLI extension conventions](../../../../notes/cli-extension-conventions.md)
- [CLI projection commands](../../../../notes/cli-projection-commands.md)

## Progress

- Story outlines: 0/2 reserved; no Story files created. Awaiting Epic approval.
