---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: "approved"
record_kind: "prd"
local_id: "prd"
---

# Review convergence and optional historical validation

## Problem Statement

Review stalls on two axes. (1) No worker-response barrier: re-reviews run
while Blocking findings in the same ledger are unaddressed or partial,
worker repair claims pass as reviewer closure, and no handoff payload stops
a fresh full audit over unchanged inputs — partial repairs can look like
consumed rounds. (2) Older records predate modern receipt, review and pin
semantics and surface as uniform gate failures or one stale pin blocking
whole-Project validate, with no split between claimed history and current
integrity. Product scope approved by the user on 2026-10-21.
Architecture and implementation remain separately gated.

## Verified Baseline

- `task_review_spec.md:160-169` forbids new findings on unchanged code except
  evidence-backed critical `LATE` (fix-introduced defects link as `REG`);
  `:284-286` allows three rounds; round aggregation has no explicit
  coordinator barrier. `task_implement_story.md:363-373` mandates the
  convergent Task 7 review and stable ledger but has no per-finding
  worker-readiness gate or re-review payload; the generic method always
  launches a full audit.
- `kosmic_completion.py:371-409` enforces `review_round` 1–3, rejects open
  Blocking rows, closes them only via `resolved` or annotated
  `risk-accepted` (a `refuted` status is rejected), and accepts `resolved`
  without response evidence.
- `kosmic_project_skills.py:3114-3115` enables historical input handling only
  for `status: done`; `:3347-3351` scans all proposal files, drafts included;
  legacy receipts still require immutable originals.
- Causal limits: the `_checked_review` probe used synthetic metadata plus a
  real source hash, unpublished — it bounds the metadata gate, not the
  user's specific stalled session; source/installed hashes matched on the
  four key files, so stale installation is not established.
- Catalog: 169 records (123 raw done, 102 receipt_pending) — historical
  claims, not unfinished tasks. [Projected link rewriting](../../../specs/quick-tasks/2026-09-02-projected-link-rewriting.md)
  is raw done while public check-completion exits 2 (`COMPLETION_PENDING`,
  receipt `106968a09d8d5cdb` missing); [bootstrap registration](../../../specs/quick-tasks/bootstrap-working-directory-registration-for-kosmic-original.md)
  and [library inventory](../../../specs/quick-tasks/materialize-shared-skill-library-inventory.md)
  predate modern review fields; the [day-delta proposal](../../../specs/skill-proposals/2026-09-24-day-delta-harvest-routine.md)
  is draft/pending; the [dream-reflection-workflow](../../../notes/dream-reflection-workflow.md)
  stale pin previously blocked whole-Project validate (adverse fact; no
  rerun claimed).

## Goals

- Ledger-bound worker barrier, complete re-review handoff on one snapshot,
  reviewer-confirmed refutation as closure, bounded later rounds, and
  pair-round semantics under the max-3 cap (FR-001..005).
- Optional historical-integrity policy for inactive history — warnings by
  default, opt-in strict audit, explicit inspectable scope (FR-006).
- Compatibility and retained strictness for executed/published artifacts
  (FR-007/008); lean reuse of existing surfaces (FR-009).

## Non-Goals

- No new artifact classes (sidecars, queues, caches, round records,
  journals); no permanent prose tests.
- No edits to the upstream generic code-review skill or installed copies; no
  source changes or auto-installation in this planning phase.
- No new persistent lifecycle status; no global skip-hashes switch; no
  rewrite of the completed workflow-efficiency / knowledge-first features or
  of historical records, receipts, or pins.
- Technical mechanism (metadata encoding, config/CLI naming, enforcement
  points) is explicitly deferred to Architecture approval, not an unfinished
  placeholder.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Before routine re-review, every Blocking row in the same ledger has a worker response: fixed + observable evidence or proposed refutation + rationale/evidence. Unaddressed or partial repairs cannot be submitted. A genuinely blocked prerequisite is recorded and escalated by the coordinator, not sent as a routine re-review. A worker claim is not reviewer closure. | must |
| FR-002 | Handoff carries fixed base, previous reviewed revision, stable full ledger with per-finding responses, changed targets/affected checks; both axes review one snapshot; later rounds never restart the initial full audit; no new artifact class or journal. | must |
| FR-003 | Reviewer-confirmed refutation closes a Blocking row beside fixed and risk-accepted, preserving finding, rationale and judgement; no retroactive resolver/hash mandates on existing rows; encoding is an Architecture decision. | must |
| FR-004 | Later rounds limited to unresolved rows, changed behavior/affected checks, fix-introduced `REG` (linked), or critical `LATE` with concrete new evidence plus why Round 1 missed it; ordinary unchanged-code/style issues are non-blocking follow-ups. | must |
| FR-005 | One complete Standards + Spec pair is one round; worker repairs and partial child messages neither consume a round nor end an episode; Round 2 changes-requested continues into Round 3 absent a real blocker; max 3 rounds, stable IDs, fixed base; at cap an explicit decision packet — no fresh audit, reset, or fake approval. | must |
| FR-006 | Historical-integrity policy for inactive history: configured default reports missing/stale retrospective hashes/proofs as visible unverified warnings, not blockers; explicit strict audit fails on actual missing/mismatch; covers old unfinished approved/draft and done records; scope explicit and inspectable, never done-only, never auto-verifying new missing hashes; naming deferred to Architecture. | must |
| FR-007 | Historical inspection/audit never rewrites old bytes/status, invents receipts, repins, or asserts verified completion; claimed lifecycle is separate from integrity state, with no new persistent lifecycle status. Separately authorized work may resume an unfinished old record under current authority/review/proof requirements, without inventing proof of past phases. | must |
| FR-008 | Strict freshness, identity/ancestry/scope/containment and all pins retained for artifacts actually executed or published; a historical flag never bypasses an active dependency or grants mutation authority; no global skip-hashes switch. | must |
| FR-009 | Lean surfaces: same record, ledger, and configuration surfaces; no new sidecars, queues, caches, or round records; no permanent prose tests. | should |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Safety: two independent axes, fixed base, stable IDs, max-3 cap, current-operation receipt/source integrity and active-record strictness remain. Historical inspection follows FR-006; a warning or unaudited old receipt never grants active authority or verified completion. | must |
| NFR-002 | Historical inspection/audit preserves existing record, receipt and pin bytes. Ordinary changes to resumed unfinished work require separate live authority under FR-007; compatibility mode itself performs no backfill or rewrite. | must |
| NFR-003 | Inspectability: historical scope/classification and per-finding response states are visible in existing record/ledger surfaces. | must |
| NFR-004 | Lean: no new persistent artifacts or mandatory prose tests; the mechanism reuses existing surfaces. | should |

## Success Criteria

- [ ] **Partial repair held:** routine re-review is refused while any Blocking row is unaddressed or only partly repaired; a real blocked prerequisite produces an explicit coordinator escalation. A complete fixed/proposed-refutation payload proceeds to bounded review without restarting round counting.
- [ ] **Refutation both ways:** a worker may submit a complete evidence-backed proposed refutation for bounded review, but it closes nothing by itself. Reviewer acceptance preserves the original finding and rationale as resolved; rejection leaves that finding Blocking for further repair.
- [ ] **Later-round scoping:** a newly noticed ordinary unchanged-code/style issue stays a non-blocking follow-up, while fix-introduced `REG` links to its cause and evidence-backed critical `LATE` records why Round 1 missed it; only the latter two block.
- [ ] **Pair-round counting and cap:** partial worker repairs between axes consume no round and end no episode; changes-requested at Round 2 continues into Round 3; a fourth automated round never starts — the cap yields an explicit decision packet.
- [ ] **Old done, no receipt:** [projected link rewriting](../../../specs/quick-tasks/2026-09-02-projected-link-rewriting.md) reports raw done with a visible unverified warning by default and fails explicit strict audit on the missing receipt, with no historical write.
- [ ] **Old approved/draft warn vs strict fail:** [bootstrap registration](../../../specs/quick-tasks/bootstrap-working-directory-registration-for-kosmic-original.md) and [library inventory](../../../specs/quick-tasks/materialize-shared-skill-library-inventory.md) warn on missing modern review fields instead of blocking; the [day-delta draft proposal](../../../specs/skill-proposals/2026-09-24-day-delta-harvest-routine.md) and the [dream-reflection-workflow](../../../notes/dream-reflection-workflow.md) stale pin appear as inspectable warnings rather than a wholesale validate block; strict audit fails on the actual mismatches.
- [ ] **Active tamper refuses; no audit rewrites:** stale or tampered artifacts currently executed or published are refused even with historical compatibility configured. History-only inspection/audit leaves old bytes, status, receipts and pins identical; separately authorized resumed work may change under current rules without fabricated proof of past work.

## Open Questions

- Metadata encoding for refuted / blocked-prerequisite dispositions and
  reviewer confirmation, backward-compatible with pre-existing rows.
- Historical scope classification rules, config/CLI naming, warning surfaces.
- Which parts of the coordinator barrier are mechanical CLI checks versus
  prose workflow requirements.

## Related Knowledge

- [Architecture](architecture.md) — proposed design; draft awaiting separate user approval.
- [Owner specs index](INDEX.md); current CLI invariants in
  [cli-projection-commands](../../../notes/cli-projection-commands.md) and
  [cli-extension-conventions](../../../notes/cli-extension-conventions.md).
- Baseline sources (repo-relative): `skills/references/task_review_spec.md`
  (`:160-169`, `:284-286`), `skills/references/task_implement_story.md`
  (`:363-373`), `skills/scripts/kosmic_completion.py` (`:371-409`),
  `skills/scripts/kosmic_project_skills.py` (`:3114-3115`, `:3347-3351`).
