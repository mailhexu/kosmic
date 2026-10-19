---
project_id: "kosmic"
subproject_id: "workflow-efficiency-and-selective-delegation"
status: done
record_kind: "story"
local_id: "001"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
related_notes: ["notes/cli-projection-commands.md"]
created: 2026-10-19
updated: 2026-10-19
consumer_interface_change: true
review_base: "48160c74ef5a3f081b50cb4ae948c170640f2643"
review_round: 2
completion_observations:
  - criterion: "AC1: Given a qualifying feature Story with all gates satisfiable, when one ordinary `python3 skills/scripts/kosmic_project_skills.py work finish --project ... --worktree ... --work-record ... --scope ...` runs, then every applicable completion gate is exercised in the normative order and the existing publication order record done → indexes → completion log → receipt → derived STATUS completes with the current CLI JSON receipt schema returned unchanged."
    observation: "Integrated real CLI S3 completed one finish with a successful record-bound receipt; shared prechecks, publication order and idempotence were exercised by the 20 finish regression cases and existing work-record suite."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
  - criterion: "AC2: Given injected invalid dependency, retired-input, missing `consumer_interface_change`, unstable/missing related note, projection, STATUS-drift, or math/proposal/routine state, when `work finish` runs, then it refuses before any publication — record not done, no receipt file — for each gate individually."
    observation: "Individual dependency, retired-input, consumer declaration, note currency, projection, STATUS, mathematical closure and proposal refusals passed in the integrated suite; S2 refused an existing unfinished dependency with no receipt."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
  - criterion: "AC3: Given a domain failure inside the shared precheck, when finish rejects, then the public error is `COMPLETION_PRECHECK_FAILED` retaining the original diagnostic and cause; existing authority/scope/proof/review codes (`RECORD_NOT_AUTHORIZED`, `WORK_PHASE_DENIED`, `ACCEPTANCE_INVALID`, `RETIRED_INPUT`, `SCOPE_DENIED`, `REVIEW_INVALID`, `COMPLETION_PENDING`, `COMPLETION_DRIFT`) are unchanged; a missing or unreadable Project config is reported, not swallowed, on this finish path."
    observation: "Domain failures retained actionable diagnostics through COMPLETION_PRECHECK_FAILED. Reachable Project-config collision and primary-scope precedence checks passed; existing authority/proof/review codes remained intact."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
  - criterion: "AC4: Given mis-scoped finish claims plus independently invalid review evidence, when finish runs, then `SCOPE_DENIED` is raised before review validation is consulted, the domain precheck runs after proof/scope/review so its diagnostics never mask them, and no receipt exists until every gate has passed."
    observation: "Mis-scoped claims with independently invalid review and config were refused as SCOPE_DENIED before later gates; refusal left the record uncompleted and receipt absent."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
  - criterion: "AC5: Given changed record bytes, a changed `source_revision` binding, or stale mid-episode identity/ancestry/scope/approval authority introduced after the gates ran, when the immediate-before-write freshness rechecks observe it, then the invocation rejects with no partial publication — no atomicity is promised and the caller reruns."
    observation: "API timing-injection exercises ran the real precheck then mutated actual record/source files; pre-write checks rejected drift without repinning. Captures precede proof and the final source hash compares against the validated reviewed_revision."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
  - criterion: "AC6: On the terminal route, ordinary linked-note/data evolution and review-base aging leave a valid receipt valid — no mutable note/data rehash, no current dirty-source review rehash, no pin refresh — while tampered record bytes, missing/changed immutable originals, or failing declared formal math/proposal/routine checks reject the retry."
    observation: "S3/S4 tolerated linked-data evolution with immutable receipt bytes, while record tampering failed. Real SymPy closure loss rejected retry and both plain and record-bound completion entry modes; legacy-original byte checks remained green."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
  - criterion: "AC7: Given a present but unreadable or inconsistent receipt, when finish runs, then it rejects (`COMPLETION_PENDING`/`COMPLETION_DRIFT`) without re-blessing, repinning, or falling through to a fresh completion attempt."
    observation: "Unreadable or inconsistent existing receipts were refused without replacement or historical repinning; the corresponding real-CLI and existing legacy receipt regressions passed."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
  - criterion: "AC8: Given an absent receipt, finish enters the full nonterminal path so an interrupted pre-receipt or unreceipted-done episode recovers only by rerunning every gate (never conflated with terminal success); a valid retry returns the receipt and completion log bytes unchanged and repairs only derived STATUS, and legacy inputs are honored solely through the terminal historical route's byte-verified recorded originals."
    observation: "Absent-receipt interruption/recovery regressions passed through the full gates. Valid S3 retry retained its receipt and unique completion log while repairing derived STATUS; historical originals remained the only legacy byte-checked inputs."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
  - criterion: "AC9: At cutover, the current docs, CLI guidance, examples, and consumer contracts describing finish/completion match the landed behavior coherently, and historical receipt/pin bytes are untouched."
    observation: "Integrated runtime guidance and consumer-note publication were reviewed on both independent axes. Native generate-library refreshed the source note/pair/topic pins; validate-library and hash-pinned recipe load passed. Historical receipts and pins were not rewritten."
    source: "Integrated pytest finish/legacy/math cases; actual CLI S1–S7 smoke; independent Round2 review."
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
  review_base: "48160c74ef5a3f081b50cb4ae948c170640f2643"
  reviewed_revision: "870ae1c573251862a656ba71fe2928823e496208300004983683046d8987ac83"
  findings: []
  scope:
    - "worktree:skills/scripts/kosmic_completion.py"
    - "worktree:skills/scripts/kosmic_project_skills.py"
    - "worktree:tests/test_unified_finish_completion.py"
    - "worktree:tests/test_kosmic_work_records.py"
    - "worktree:skills/references/work_completion.md"
    - "worktree:skills/references/task_implement_story.md"
    - "project:notes/cli-projection-commands.md"
    - "project:skills/"
    - "worktree:memnotes/Skills/"
    - "project:subprojects/workflow-efficiency-and-selective-delegation/specs/stories/story-001.md"
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
---

# Story 001: Unified Safe Completion and Immutable Retry

## User Story

As an agent or operator finishing authorized work,
I want one ordinary `work finish` invocation to run every currently required completion gate — embedded proof, primary scope (`SCOPE_DENIED` first), reviewed scope/source binding, the complete shared read-only domain precheck, and last-moment freshness rechecks — and terminal retries to verify only the unchanged receipt record and its immutable originals plus the declared formal contracts,
so that completion is safe by default and idempotent without re-blessing drifted bytes, mutable re-verification, or a second choreographed command.

Covers FR-002 as exercised by these invocations, FR-003, FR-004, and this Story's FR-012 cutover slice. ADR-B and ADR-C are binding; ADR-A authority semantics are consumed as given (no redesign). No prefill, workflow-policy/delegation, or measurement ownership; this Story has no depends_on.

## Acceptance Criteria

- [ ] AC1: Given a qualifying feature Story with all gates satisfiable, when one ordinary `python3 skills/scripts/kosmic_project_skills.py work finish --project ... --worktree ... --work-record ... --scope ...` runs, then every applicable completion gate is exercised in the normative order and the existing publication order record done → indexes → completion log → receipt → derived STATUS completes with the current CLI JSON receipt schema returned unchanged.
- [ ] AC2: Given injected invalid dependency, retired-input, missing `consumer_interface_change`, unstable/missing related note, projection, STATUS-drift, or math/proposal/routine state, when `work finish` runs, then it refuses before any publication — record not done, no receipt file — for each gate individually.
- [x] AC3: Given a domain failure inside the shared precheck, when finish rejects, then the public error is `COMPLETION_PRECHECK_FAILED` retaining the original diagnostic and cause; existing authority/scope/proof/review codes (`RECORD_NOT_AUTHORIZED`, `WORK_PHASE_DENIED`, `ACCEPTANCE_INVALID`, `RETIRED_INPUT`, `SCOPE_DENIED`, `REVIEW_INVALID`, `COMPLETION_PENDING`, `COMPLETION_DRIFT`) are unchanged; a missing or unreadable Project config is reported, not swallowed, on this finish path.
- [ ] AC4: Given mis-scoped finish claims plus independently invalid review evidence, when finish runs, then `SCOPE_DENIED` is raised before review validation is consulted, the domain precheck runs after proof/scope/review so its diagnostics never mask them, and no receipt exists until every gate has passed.
- [x] AC5: Given changed record bytes, a changed `source_revision` binding, or stale mid-episode identity/ancestry/scope/approval authority introduced after the gates ran, when the immediate-before-write freshness rechecks observe it, then the invocation rejects with no partial publication — no atomicity is promised and the caller reruns.
- [x] AC6: On the terminal route, ordinary linked-note/data evolution and review-base aging leave a valid receipt valid — no mutable note/data rehash, no current dirty-source review rehash, no pin refresh — while tampered record bytes, missing/changed immutable originals, or failing declared formal math/proposal/routine checks reject the retry.
- [x] AC7: Given a present but unreadable or inconsistent receipt, when finish runs, then it rejects (`COMPLETION_PENDING`/`COMPLETION_DRIFT`) without re-blessing, repinning, or falling through to a fresh completion attempt.
- [ ] AC8: Given an absent receipt, finish enters the full nonterminal path so an interrupted pre-receipt or unreceipted-done episode recovers only by rerunning every gate (never conflated with terminal success); a valid retry returns the receipt and completion log bytes unchanged and repairs only derived STATUS, and legacy inputs are honored solely through the terminal historical route's byte-verified recorded originals.
- [ ] AC9: At cutover, the current docs, CLI guidance, examples, and consumer contracts describing finish/completion match the landed behavior coherently, and historical receipt/pin bytes are untouched.

## Tasks

### Research (before implementing)

- [ ] Read [PRD](../prd.md) FR-002/003/004/012, [Architecture](../architecture.md) ADR-B/ADR-C (ADR-A as given), and [Epic 001](../epics/epic-001.md) scope; survey the current `finish_work` terminal/full paths, `check_done_record_gates`/`check_completion_gates`, `check_completion`'s plain-done formal block, `_check_existing_completion` gates, `validate_receipt_payload` current-vs-legacy binding, and the `kosmic_work` authority contract (`resolve_work_record`, `_ancestry_approved`, `check_record_changes`) — touch `kosmic_work.py` only if that contract requires.
- [x] Classify routine mechanics and reuse under the existing Task 9 / Task P triggers; record the classification and any interface decisions in Technical Notes; no forced proposal and no canonical skill edit.
- [x] Write failing-first regression tests for the changed completion behavior; retain passing guard/legacy tests without forcing them to fail (behavior only: no source-text, import, wiring, or call-count assertions).

### Tests (verification-first)

- [x] TEST-001: unified single-invocation success (AC1) and each AC2 gate refusal leaving record not-done and no receipt; standalone `check-completion` stays diagnostic/fail-fast.
- [x] TEST-002: precedence and translation — `SCOPE_DENIED` over review validation, precheck-after-review ordering, `COMPLETION_PRECHECK_FAILED` cause retention, retained codes, config-not-swallowed (AC3/AC4).
- [x] TEST-003: freshness drift (record bytes, `source_revision`, authority) detected at the pre-write recheck (AC5).
- [x] TEST-004: terminal invariance — evolution-tolerant retry vs record/original tampering and formal math/proposal/routine failure, invalid-receipt rejection, absent-receipt full recovery, retry receipt/log byte-invariance with STATUS-only repair, legacy terminal-historical route (AC6–AC8); the same formal checks hold through both `check-completion` entry modes.

### Implementation

- [ ] IMPL-001: extend `finish_work` in `skills/scripts/kosmic_completion.py` — terminal route first (fresh identity/approved ancestry, receipt validation, shared terminal formal helper, STATUS-only repair); absent-receipt fall-through: `validate_completion_proof` → primary `check_record_changes` scope (`SCOPE_DENIED` precedence) → `_checked_review` reviewed scope/`source_revision`/fixed-base review → complete shared readonly precheck via the established deferred import calling `kosmic_project_skills._check_existing_completion(project, record.path, source_root=worktree, record_scoped=True, record_owner=record.subproject_id)` — not a recursive CLI call — with `KosmicError` translated to `WorkdirError("COMPLETION_PRECHECK_FAILED", …)` keeping the original caus…
- [x] IMPL-002: in `skills/scripts/kosmic_project_skills.py`, extract the shared terminal formal helper (`load_math_registry` restricted to the record's `derivations` + `_check_math_proposal_routine_gates`) used identically by the plain done path and the finish terminal route; public `finish_work` signature and CLI JSON unchanged.
- [ ] IMPL-003: FR-012 slice — update current docs, CLI guidance, examples, and consumer contracts coherently with landed behavior; shared runtime/docs files get one integration owner, not concurrent blind edits; scoped managed scratch is removed after the smoke; no live/global vault or install changes.

### Review / Completion

- [ ] Real throwaway CLI smoke of `work finish` on managed scratch (success plus refusal cases), removed afterward; integrated verification runs once affected changes are stable, rerunning changed/failed inputs; scientific validation never skipped.
- [ ] User approval before implementation; fixed-base two-axis independent review with the existing max-3 findings ledger; successful receipted `work finish`; final human handoff repeats the full absolute Story path link.

## Routine Decision


Research outcome: no Shared Skill Library routine or `uses_routines` edge is created or changed. This approved slice extends the ordinary Project CLI backend or its existing guidance; no Task P proposal trigger was found. The false routine/proposal declarations record that classification, not an exemption from the existing gates. Canonical topics refresh only through the native authorized producer; installed skills stay unchanged.

## Technical Notes

Pre-publication verification: actual CLI exercises and independent Round 2 review are complete. Receipt creation, its final human handoff and managed-scratch finalization are downstream transactions; their checklist rows are deliberately not claimed before publication and the bound record is not edited afterward merely to tick them.

- Frozen surface: `finish_work(project_root, worktree, record_ref, scope, *, detail="") -> dict` and the `work finish` CLI receipt JSON; receipts keep the `{record_path: record_sha256}` binding; historical receipts byte-verify only their recorded immutable originals and are never repinned or re-blessed.
- The precheck is the same helper standalone `check-completion` uses, so finish and the diagnostic stay one implementation; unlike the tolerant STATUS-candidate enumeration, the finish precheck path does not swallow a missing/unreadable Project config.
- The terminal route never re-hashes evolving notes/data, never recomputes the current dirty-source review binding, never refreshes historical pins, and applies the declared formal checks exactly as the plain done path so both check-completion entry modes agree.
- The only new public error code is `COMPLETION_PRECHECK_FAILED`; the nonterminal precheck never auto-repairs stale STATUS/projections or refreshes pins. Valid terminal retry still repairs derived STATUS only. No path automatically rebinds a changed record/source.
- Empty `completion_observations` and review metadata is correct at draft; they are filled only by real exercised outcomes, never fabricated.

### Research record (2026-10-19, pre-implementation checkpoint)

- Current `finish_work` (skills/scripts/kosmic_completion.py) runs proof → primary scope → review → publication and never invokes the shared domain precheck; `depends_on` is not consulted anywhere on the finish path, so a record declaring an unfinished dependency publishes `done` plus a receipt today.
- Discriminated red scenario: valid embedded observations, valid `project:specs/` scope claim, valid two-axis review binding the current `source_revision`; the record declares `depends_on` on a quick task still `approved`. Only the shared precheck's dependency gate can refuse it: the fixture ProjectEntry binds no `status_root`, so the STATUS gate is inert, and no math/proposal/routine declarations exist, so those gates pass trivially.
- Fixture migration need observed for implementation: records in `tests/test_kosmic_work_records.py` and `tests/test_status_planning_authority.py` lack `consumer_interface_change`/derivations declarations and will need fixture updates once finish runs the full precheck; `EmbeddedCompletionFinishTest` records already declare `consumer_interface_change: false`. `tests/test_pack_retirement.py` legacy tests and the `_atomic_write` interruption seam stay untouched.
- Routine classification: the unified gate order, precheck reuse, and the shared terminal formal helper only recompose existing helpers (`_check_existing_completion`, `load_math_registry`, `_check_math_proposal_routine_gates`); no new reusable Pattern and no `proposal_required` trigger observed at this checkpoint.

### Implementation record (2026-10-19, pre-verification)

- IMPL-001 landed in `skills/scripts/kosmic_completion.py`: strict `_completion_precheck` config load (reports, never swallows); terminal route = `check_terminal_receipt` → shared formal helper → STATUS-only repair, refusing unreadable/inconsistent receipts; absent-receipt path = proof → primary scope → review → shared `KosmicError → COMPLETION_PRECHECK_FAILED` precheck translation → pre-write freshness recheck (record bytes/`source_revision`/authority; detect-only, never repins) → unchanged publication order. Obsolete "Verify evidence/review/scope" docstring replaced.
- IMPL-002 landed in `skills/scripts/kosmic_project_skills.py`: new public `check_terminal_formal_gates(project, work_item, source_root)` shared verbatim by the plain done path and the finish terminal route; `finish_work` public signature and CLI receipt JSON unchanged.
- TEST-001..004 scenarios live in `tests/test_unified_finish_completion.py` (19 behavior tests, real-CLI plus two API-level race cases at the established `_atomic_write`-style collaborator seams); fixture migrations in `tests/test_kosmic_work_records.py` add `consumer_interface_change` declarations and per-attempt derived-STATUS refreshes (`refresh_status`), never weakening gates. `tests/test_pack_retirement.py`, the `_atomic_write` interruption seam, and the routine-gate wording pins are untouched.
- IMPL-003 doc slice landed: `skills/references/work_completion.md` (unified gate order + terminal route), `skills/references/task_implement_story.md` 5.1, and the canonical source note `memnotes/Projects/kosmic/notes/cli-projection-commands.md` completion bullet (projection refresh is a parent-integration concern; no generated catalogs edited).
- Truthful verification state: the red regression was confirmed failing by the parent before implementation; none of the new or migrated tests, the focused suite, or the CLI smoke have been executed by this writer — integrated verification, the throwaway smoke plus its scratch removal (the remaining IMPL-003 clause), and independent review are deferred to the parent per the verification contract.
- Post-verification corrections (parent review): freshness snapshot now captured before the first proof/review and compared against the review's own validated `reviewed_revision` (authority recheck last); strict Project load deferred to the precheck step so tolerant candidate enumeration can never mask `SCOPE_DENIED` while valid-scope paths still report config failures (`COMPLETION_PRECHECK_FAILED`, including `KosmicError` collisions); the mock-echo source-drift test was deleted and replaced with a real different-file source mutation at the shared-precheck boundary; incidental frontmatter-string assertions were replaced by parsed lifecycle outcomes; `GIT_CEILING_DIRECTORIES` isolates the invalid-worktree probe; and `check-completion --work-record` done mode now applies the shared terminal formal helper in lockstep with the plain `--work-item` mode and the finish terminal route.
- Fixture corrections after the parent's second partial rerun: the stale-related-note scenario commits its note before writing the record and the config-collision scenario commits the collision input, so both discriminate their intended gate instead of tripping `SCOPE_DENIED` on unclaimed fixture inputs (the scope-precedence companion intentionally keeps the collision unclaimed); the race tests use the actual `kosmic_work.WorkdirError` alias; and the invalid-worktree probe sets `GIT_CEILING_DIRECTORIES` to the fixture's parent so Git discovery is genuinely isolated. Still no tests, suite, smoke, or commits run by this writer.

## Definition of Done

- Every AC exercised through the applicable real CLI/API path; no source-text, import, wiring, or incidental-wording tests.
- New regression tests demonstrate changed behavior failing before and passing after; existing safety guards remain green, with changed or previously failed inputs rerun once stable.
- Actual throwaway CLI smoke performed and its scratch removed; runtime-change claims grounded in observed behavior, not test passes alone.
- User approval before implementation; fixed-base two-axis review approved under the max-3 ledger; successful `work finish` receipt; final handoff links the full absolute Story path again; docs/contracts coherent at cutover with historical bytes untouched.
