---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
record_kind: architecture
local_id: architecture
status: draft
created: 2026-10-21
updated: 2026-10-21
linked_prd: prd.md
linked_research: []
linked_stories: []
---
# Architecture: Review convergence and optional historical validation

## System Overview

This draft proposes two independent seams: read-only, configuration-scoped historical integrity reporting; and a coordinator-owned barrier for bounded re-review on the existing completion ledger. Historical display never grants authority or changes lifecycle; review annotations never authenticate the full review process. The PRD is approved; this Architecture and all ADRs remain draft/proposed pending the user gate.

Approved input: [PRD](prd.md). Navigation: [owner specs index](INDEX.md).


## Technical Decisions (ADRs)

### ADR-001: Exact configured history scope

**Status**: Proposed

**Context**: Historical warning scope must be explicit, inspectable, stable for canonical STATUS, and unable to weaken active operations.

**Decision**: Add optional `history_integrity` configuration to ProjectEntry and an immutable optional policy at the end of frozen `Project` (which currently has `working_state` and `status_root`). Configuration parsing must not recursively construct a catalog; resolve identities at structural discovery/report boundaries.

```yaml
history_integrity:
  mode: warn             # warn (default) | strict
  records:
    - specs/quick-tasks/2026-09-02-projected-link-rewriting.md
    - specs/quick-tasks/materialize-shared-skill-library-inventory.md
    - specs/skill-proposals/2026-09-24-day-delta-harvest-routine.md
```

Accept exact canonical Project-relative paths only; reject unknown, duplicate, noncanonical, uncontained or wrong-owner references using existing no-follow containment/canonical checks. Absent policy or empty list preserves current behavior. Path moves require a separately governed ProjectEntry edit; never auto-rewrite it.

The only proposed flag is read-only `validate --history-audit`: force retrospective strict audit of configured records for that invocation. Empty scope is a clear configuration/usage refusal, not an audit. Keep existing validate exit conventions; warn success may be 0 but diagnostics must say `unverified`/`not audited`, never “all history verified.” No history flags on operational loaders, work finish/check-completion, or other commands.

**Alternatives (brief)**:

1. **Selected — exact configured paths:** `records: [specs/quick-tasks/old.md]`. Hidden cost: canonical/owner/symlink/stale-path checks and explicit move maintenance. Benefit: stable, inspectable STATUS scope without date inference.
2. **Rejected — per-call selector:** `validate --history-record PATH`. Hidden cost: callers repeat scope, partial invocations may look comprehensive, and no stable STATUS policy. Benefit: convenient one-off targeting.
3. **Rejected — created-date cutoff plus undated exceptions:** `history_before: DATE; history_exceptions: [PATH]`. Hidden cost: missing/mutable dates and a second list make classification less predictable. Benefit: bulk convenience.

### ADR-002: Structural reporting before retrospective readers

**Status**: Proposed

**Context**: `SpecRef.effective_status` is receipt-aware. `SpecCatalog.__init__` calls `_settle_receipts`; `_spec_rows` calls `try_project_catalog` (constructing that catalog) and separately calls `pending_terminal_receipts`; bootstrap-flat `_spec_rows` also settles receipts. A post-render label override still incurs historical integrity work.

**Decision**: Factor/reuse private structural discovery of identity, owner and claimed lifecycle before receipt settlement. Preserve strict default behavior and interfaces of `SpecCatalog.__init__` and `.bounded()`; only refactor their shared private scanner. Add no generic skip-receipts flag or lax operational catalog. Structural reporting data must not be accepted as an operational catalog.

Resolve configured subjects at the reporting boundary before any retrospective integrity/hash reader. In `warn`, skip those audits and display raw claimed lifecycle plus `unverified — not audited`; do not run checks and then downgrade their failures. A selected done row is not open solely for missing modern proof; unfinished approved/draft history remains visible. Unselected/current records retain required checks. Configured `strict` mode or explicit audit uses narrow integrity-only readers; failed retrospective checks remain diagnostics and make validation fail, without rewriting lifecycle or admitting operational objects.

Only retrospective integrity absence/drift (including missing modern completion proof on selected old records) is warning-eligible. Malformed YAML, identity/owner, containment, parsing and authority errors stay hard; no blanket `KosmicError` catch or string matching. Direct `load_skill_proposal` remains strict, including its rejected-proposal equivalence scan; audit must not invoke that loader or return a permissive proposal. Do not retroactively impose blanket receipt rules on every old `depends_on`.

`render_status`, `_spec_rows`, `status_drift`, and `_write_status_reports` use the same configuration-derived display policy. Audit override never renders alternate canonical STATUS or writes history. `SpecRef.effective_status`/`receipt_pending`, active dependencies and authority remain unchanged. Resumed records remain strict; classification changes only through separately governed configuration. Work finish/check-completion, terminal retries, proposal/routine publication, executable math, migration and library/package validation retain current domain checks and recorded-facts semantics (no retired raw-artifact rehashing).

**Consequences**: Warning and audit remain read-only and scoped; STATUS is config-derived. Explicit path maintenance is required. Empty/unconfigured Projects keep current behavior.

### ADR-003: Coordinator barrier and additive finding response

**Status**: Proposed

**Context**: Re-review must carry the stable ledger and fixed base to both independent axes, avoid consuming rounds on partial work, and stop at three rounds. This is coordinator/host workflow, not new CLI, engine or state store.

**Decision**: Before routine re-review, require every unresolved Blocking row to have a complete worker response: fixed plus observable evidence, or proposed refutation plus rationale/evidence. A genuinely blocked prerequisite is recorded and escalated, not submitted as routine review; incomplete responses are held. Worker assertions never close findings. Carry the base, prior/current reviewed revision, full ledger and responses, changed targets and affected checks to both axes on one held target. Round 1 remains full; later checks cover unresolved findings, changed behavior/affected checks, linked fix-introduced `REG`, and evidence-backed critical `LATE` with why missed. Ordinary unchanged/style issues remain follow-ups. Changes-requested at Round 2 continues to Round 3 absent a real blocker; partial child results consume no round. Target changes invalidate stale approval and rerun affected verification. At cap, issue a decision packet, never reset or begin endless audits.

One completed Standards + Spec pair on the held snapshot is **one** automated round, never two. Worker repairs and partial callbacks do not consume another round. After Round 3, unresolved blockers require the existing ledger, attempted resolutions and a concrete human decision; there is no automatic fourth round or reset.

Same-snapshot is a coordinator guarantee, not authenticated by `source_revision`: its hash excludes nested Project record bytes and therefore does not freeze acceptance observations, ledger or context. Supply the identical actual record/ledger/acceptance payload to both reviewers; hold the target stable and recheck changed context even if source revision is unchanged. No persistent context hash or sidecar. Native metadata does not authenticate full review history.

Optional backward-compatible finding fields; this is an illustrative worker claim, not an approval:

```yaml
- id: STD-001
  disposition: Blocking
  status: open
  worker_response:
    kind: fixed              # fixed | refuted | blocked
    detail: "Guard applied; awaiting independent reviewer verification."
    evidence: "Malformed-review CLI case returned REVIEW_INVALID without publishing a receipt."
```

For `fixed`/`refuted`, detail and evidence are non-empty. `blocked` records prerequisite and escalation rationale/evidence. Reviewer acceptance of a fix or refutation uses existing `status: resolved`, optionally `resolution: fixed|refuted`; preserve the original finding and refutation rationale/judgment. Rejected refutation remains open/Blocking. Existing `risk-accepted` fields and old closed rows remain valid. Do not add a `refuted` status or mandatory old-row version/identity/hash/resolver fields. Validate shape/coherence when annotations are supplied.

The re-review request carries record identity/path, base, prior and current reviewed revision, complete ledger and responses, changed targets, affected checks/results, requested pair/round, unchanged non-blocking exclusions, and any escalation. Coordinator assembles and freezes the handoff; worker supplies responses/evidence; each reviewer owns its axis decision. Completion still validates structured final metadata and freshness, not the agent process.


## Internal Interfaces and Domain Terms (Proposed)

`Project` gains an immutable optional `HistoryPolicy(mode, records)` at the end of its existing constructor. Proposed `skills/scripts/kosmic_history.py` owns policy/report logic; it does not import the CLI during module initialization or return operational gate objects. Existing receipt/proposal code supplies reusable narrow integrity readers, not publication/rejection-equivalence admission.

```text
_collect_spec_structure(project_root, owner_scope=None) -> _SpecStructure
inspect_history(structure, policy, strict_audit=False) -> HistoryReport
```

The private structural inventory reuses no-follow scans without settling receipts. Strict catalog construction still settles required receipts; reporting checks unselected/current rows normally and omits selected retrospective audits only in `warn`. `HistoryReport` contains display rows and diagnostics, not an authority resolver. Existing bounded-report fallbacks keep their scope disclaimer and inspect only the in-scope intersection, without requiring discovery of unrelated owners.

**Historical scope** is explicit administrative selection, not age or completion proof. **Integrity assessment** is a computed inspection result, not a lifecycle status. **Worker response** is a claim; **reviewer resolution** is its independent acceptance or rejection. Candidate glossary additions wait for approved implementation before changing canonical `CONTEXT.md`.

The only new consumer option remains `validate --history-audit`; canonical STATUS always follows configuration. Native final review/freshness checks remain structural: old closed finding shapes stay accepted, while supplied response/resolution annotations must be coherent. The coordinator—not a new engine, context hash, or sidecar—enforces the pre-submit protocol.

## Test Strategy

Exercise consumer behavior at CLI/seams; no permanent prose or call-count/wiring tests:

- Done without receipt; approved/draft records lacking modern proof; stale historical pins (including the selected proposal's stale `dream-reflection-workflow` reference): warn versus explicit audit failure.
- Absent/empty policy unchanged; unknown/duplicate/noncanonical/uncontained/wrong-owner paths, malformed YAML and invalid identity remain hard errors.
- Active pins/dependencies, work finish, publication and direct proposal rejection-equivalence checks stay strict even when selected.
- Audit leaves STATUS and history/receipt/pin bytes unchanged; canonical render is invocation-independent; claimed status and unverified diagnostics are separate; unfinished history remains visible.
- Old resolved rows accepted; worker refutation cannot close; accepted refutation preserves rationale; rejected remains Blocking. Real coordinator/agent traces exercise blocked escalation, same held payload for both axes, changed-context invalidation, pair-round count, Round-2-to-3 continuation and max-3 packet.
- Skip-not-hash may use disposable instrumented smoke; no permanent mock-echo assertion.

## Risks and Dependencies

| Risk | Mitigation |
|---|---|
| Stale configured path | Reject it; require explicit governed update, never broaden or auto-edit. |
| Warning still hashes/settles history | Resolve selection before all readers, including catalog construction, `_spec_rows` settlement and flat bootstrap settlement. |
| Report leaks into authority | Distinct report type; strict catalog and operational loaders remain unchanged. |
| Worker claim mistaken for closure/snapshot | Reviewer-only closure; identical payload, held target, context recheck and max-3 coordinator protocol. |
| Audit mistaken for completion | Explicit unverified label; no status/receipt rewrite or authority grant. |

Existing seams: frozen `Project`/`load_project`; `SpecCatalog` and `SpecRef.effective_status` (`kosmic_specs.py`); `_spec_rows`, `render_status`, `status_drift`, `_write_status_reports`, validate and proposal readers (`kosmic_project_skills.py`); `completion_review.findings`/`_checked_review` (`kosmic_completion.py`); Task 6 two-axis and Task 7 re-review guidance.

