---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: done
record_kind: "story"
local_id: "001"
created: 2026-10-22
updated: 2026-10-22
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
related_notes: [notes/cli-projection-commands.md]
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_round: 3
review_base: "aac7e9e2f41c4f36821c776016493568dfdef6ec"
completion_observations:
  - criterion: "AC1: Given a Project without `history_integrity` or with `records: []`, when real `kosmic_project_skills.py validate --project …` runs against the captured pre-change baseline, then exit code, diagnostics and generated canonical STATUS bytes are unchanged and all existing CLI guards pass unmodified."
    observation: "Compared the same unconfigured Project through clean baseline writer002 and the changed CLI: exit, stdout, stderr and generated STATUS bytes were identical. The empty-list parity regression also passed."
    source: "history-parity-and-pins-smoke.py pinned-baseline comparison; HistoryIntegrityTest absence/empty case"
  - criterion: "AC2: Given `history_integrity` containing malformed YAML, an unknown/stale path, a duplicate, a noncanonical or uncontained path, or a wrong-owner reference, when `validate` loads the Project, then it fails as a hard configuration/identity/containment error with a specific diagnostic and never silently drops or broadens scope."
    observation: "Malformed policy shapes, unknown keys/modes, duplicate/noncanonical/absolute/traversal/uncontained/unknown/wrong-owner subjects were refused with hard diagnostics and exit2 after fixing the Python __main__ exception-identity boundary. Existing malformed-YAML guards remain passing."
    source: "HistoryIntegrityTest invalid-policy subcases; focused CLI module existing guards"
  - criterion: "AC3: Given default warn mode with the old done receipt-less `specs/quick-tasks/2026-09-02-projected-link-rewriting.md` configured, when `validate` runs, then it follows its normal success path with a visible per-record diagnostic saying `unverified` and `not audited` (never \"verified\"), the row keeps claimed `done` lifecycle instead of reopening, and record/receipt/pin bytes are bit-identical after the run."
    observation: "A selected receipt-less done claim validated in warn with its exact path and unverified/not-audited diagnostics, preserved its done claim without reopening it, and kept record bytes unchanged. A deliberately corrupt selected receipt was not sent to either the catalog settlement or narrow receipt reader."
    source: "Real CLI history-boundary-before-fix.py after repair; configured warn consumer regression"
  - criterion: "AC4: Given warn mode with old approved/draft history configured (bootstrap-registration and library-inventory quick tasks, the draft day-delta skill proposal), when `validate` and `generate-status` run, then each selected record appears as an inspectable unverified warning in output and canonical STATUS with its claimed lifecycle, unfinished approved/draft history stays visible (scope never done-only), and no diagnostic claims completion proof."
    observation: "Four actual legacy byte fixtures—projected-link rewrite done, both bootstrap registration and library inventory approved, and day-delta proposal draft—appeared with unverified/not-audited diagnostics. Validation preserved record and STATUS bytes; unfinished claims remained visible, and live ProjectEntry/history were untouched."
    source: "history-real-records-smoke.py on disposable fixtures copied from live historical record bytes; live files and ProjectEntry never edited"
  - criterion: "AC5: Given warn mode with the known stale-pin fixture (the day-delta proposal referencing `dream-reflection-workflow`) selected, when `validate` runs, then skip-before-read yields only the generic `unverified — not audited` warning that claims no pin inspection or drift discovery, whole-Project validate is not blocked, and the direct strict loader (`validate-proposal`/`load_skill_proposal`) still detects the actual stale-pin drift under its existing strict semantics."
    observation: "A selected draft proposal with an actually stale curated source pin validated under warn without inspecting that pin. Direct validate-proposal still refused it, and configured strict inspection refused it as HISTORY_INTEGRITY. The clean-pin restoration case passed without claiming an unaudited proposal."
    source: "history-parity-and-pins-smoke.py; test_strict_mode_fails_stale_selected_proposal_pin (correct pinned/stale byte snapshots)"
  - criterion: "AC6: Given configured `mode: strict`, when `validate` runs and a selected record actually lacks or mismatches retrospective proof (e.g. the missing done receipt), then validation fails with an integrity-specific diagnostic while claimed lifecycle/status and receipt bytes remain unrewritten."
    observation: "Configured strict refused a missing selected done receipt, including flat bootstrap with no receipt store, and refused a present envelope-matching receipt carrying corrupt recorded proof. It also refused selected stale proposal pins; raw record/receipt/manifest/source bytes stayed unchanged."
    source: "Actual receipt boundary and curated-pin CLI smokes; strict-mode and strict-flat consumer regressions"
  - criterion: "AC7: Given any history configuration, when `render_status`, `_spec_rows`, `status_drift` and `_write_status_reports` produce canonical STATUS, then all four use the same configured view with invocation-independent bytes, and unselected/current rows keep their existing receipt/authority checks with no relaxed row."
    observation: "Configured generate-status/drift views agreed; selected warn claims stayed unverified while unselected qualified missing receipts remained pending/open. A valid closed current record stayed done in the degraded bounded view. Strict canonical markers reflect inspection; audit override is not a renderer input. Round2 independently resolved bounded-policy lookup: foreign selections are excluded before resolution without discovering other owners; missing in-scope subjects still fail hard."
    source: "HistoryIntegrityTest configured-view and degraded-current-receipt cases; actual legacy-record STATUS generation/validation; pinned-baseline parity; bounded foreign-policy intersection consumer regression; both Round2 review axes"
  - criterion: "AC8: Given any history configuration, when operational consumers run (`work finish`, `check-completion`, `validate-proposal`, operational loaders), then behavior, exit codes and `--help` surfaces are unchanged — no history flag appears on them, no `HistoryReport` value is accepted where a `SpecCatalog`/`SkillProposal` is required, and no skip/lax flag exists in any operational or catalog API (report/inspection APIs are permitted)."
    observation: "No operational history flag was added; actual work finish rejects --history-audit. Direct proposal admission remained strict on stale input pins; strict constructors retain receipt settlement while configured reporting uses structural DTOs, not an unsettled catalog. Existing catalog guards passed. R1 SPEC-001 was repaired by restoring both original successful-pin aggregation and the original nonempty aggregate guard; actual no-policy blank/comment-only proposal manifests are refused while valid inputs pass."
    source: "test_operational_surfaces_gain_no_history_flags; direct loader smoke; test_record_scoped_catalog (16 tests); fixed-base source review; actual empty-manifest/direct-loader and clean-pin regressions; independent Round2 closure"
  - criterion: "AC9: Given warn mode on a faithful disposable Project copy under managed scratch, with a selected record whose retrospective artifact is corrupted or unreadable, when the disposable instrumented smoke runs, then the retrospective reader is provably never invoked for selected records (skip-before-read: validation still succeeds as unverified) while the same corruption on an unselected record still fails exactly as the unconfigured baseline, and the live Project is untouched."
    observation: "The disposable instrumented actual validate entry rejected any selected-subject catalog settlement or narrow receipt-reader call; with a corrupt selected receipt, warn still exited0. Unselected missing/stale receipt semantics remained strict, and strict inspection exposed the same integrity gaps instead of warning them away. The identical corrupt unselected receipt was also exercised against configured warn and the clean pinned baseline: both returned2 STATUS_STALE, preserving record/receipt/STATUS bytes during validation."
    source: "history-boundary-before-fix.py constructor+narrow-reader guards (throwaway only); current/unselected receipt consumer regressions; unselected-receipt-parity-smoke.py actual two-CLI comparison"
completion_review: {"reviewer":"Main","axes":{"standards":{"decision":"approved","reviewer":"Review001Standards-2"},"spec":{"decision":"approved","reviewer":"Review001Spec-2"}},"decision":"approved","review_base":"aac7e9e2f41c4f36821c776016493568dfdef6ec","reviewed_revision":"5238b22d42218fe7ad913544da9af71b1ca12b487cc94331fe896c1c0973b91e","findings":[{"id":"STD-001","axis":"standards","disposition":"Blocking","introduced_round":1,"status":"resolved","evidence":"Bounded _spec_rows calls structure_subjects with the entire configured policy although only shared/current-owner records were discovered; a valid foreign-owner selection becomes unknown/stale.","required_resolution":"Intersect logical bounded scope before subject resolution; keep missing in-scope subjects hard and do not scan unrelated owners in degraded rendering.","worker_response":{"kind":"fixed","detail":"Bounded policy paths are intersected lexically with shared/current-owner scope before structural subject lookup; missing in-scope paths remain hard, foreign-owner discovery is not required.","evidence":"All14historyCLI/report tests pass, including bounded foreign-selection omission plus missing-in-scope hard-error control; actual receipt-reader/baseline/legacy-byte smokes stillpass."},"resolution":"fixed","resolution_note":"Both independent Round2 axes accepted the complete repair on the original baseline; worker response alone did not close this finding."},{"id":"SPEC-001","axis":"spec","disposition":"Blocking","introduced_round":1,"status":"resolved","evidence":"The curated input-manifest refactor dropped the existing nonempty-entries guard, allowing a blank/comment-only input manifest through the direct operational proposal loader even without history configuration.","required_resolution":"Restore the original nonempty-pinned-input requirement and canonical diagnostic in the shared reader, with actual no-policy validate-proposal regression.","worker_response":{"kind":"fixed","detail":"Restored BOTH the original entries[source_ref]=recorded_hash assignment after successful pin verification and the original post-aggregation nonempty entries guard with canonical diagnostic. No-policy operational loader remains strict.","evidence":"Actual empty/comment-only manifest validate-proposal refusal and strict-history refusal pass; valid clean-pin restorationpasses; all14historytests and actual stale-pin/direct-loader/reallegacy-byte smokespass."},"resolution":"fixed","resolution_note":"Both independent Round2 axes accepted the complete repair on the original baseline; worker response alone did not close this finding."}],"scope":["worktree:skills/scripts/kosmic_history.py","worktree:skills/scripts/kosmic_specs.py","worktree:skills/scripts/kosmic_project_skills.py","worktree:skills/scripts/kosmic_completion.py","worktree:skills/scripts/kosmic_dreams.py","worktree:skills/references/task_project_skills.md","worktree:tests/test_project_skills_cli.py"]}
depends_on: []
---

# Story 1: Configured historical inspection and canonical reporting

## User Story

As a Project maintainer,
I want an optional, explicitly scoped `history_integrity` policy whose default warn mode surfaces selected legacy-record gaps as visible unverified warnings in `validate` and canonical STATUS — and whose configured strict mode fails on actual missing/mismatched retrospective integrity,
So that historical claims stay inspectable and truthful without weakening any active authority, receipt, or pin check.

## Scope

### In Scope
- Optional `ProjectEntry.history_integrity` (`mode: warn|strict`, default warn; exact canonical Project-relative `records`), parsed into an immutable optional field appended to the frozen `Project` constructor; absent/empty preserves current behavior exactly.
- Selection of configured subjects at the reporting boundary before any retrospective hash/proof reader; warn mode skips those audits and reports claimed lifecycle plus `unverified — not audited`; strict mode fails on actual missing/mismatch while never rewriting lifecycle or bytes.
- One configuration-derived canonical view across `render_status`, `_spec_rows`, `status_drift`, `_write_status_reports`; unselected/current records keep existing checks.
- Proposed new `skills/scripts/kosmic_history.py` (policy + `HistoryReport`); shared private structural discovery in `skills/scripts/kosmic_specs.py`; reporting wiring in `skills/scripts/kosmic_project_skills.py`; one narrow publication touchpoint in `_write_status_reports`.
- Current consumer guidance updated for the genuinely changed contract in the same episode, with native projection refresh of the published note.

### Out of Scope
- The `validate --history-audit` override (Story 002); writes/backfills/auto-repins/receipt invention/lifecycle rewrites; global skip flags or lax operational catalogs; new persistent status/artifact classes; changes to active identity/ancestry/containment/freshness/pin/execution/publication checks; retroactive blanket receipt rules on old `depends_on`.

### Owned Files
- `skills/scripts/kosmic_history.py` (new), `skills/scripts/kosmic_specs.py`, `skills/scripts/kosmic_project_skills.py`; narrow agreed touchpoint in `skills/scripts/kosmic_completion.py::_write_status_reports` (parent integration owner coordinates this shared function — one writer, no blind whole-file edits); `notes/cli-projection-commands.md` consumer-guidance edit plus its projection regeneration.
- `skills/scripts/kosmic_dreams.py` (shared narrow receipt-integrity facts; operational API unchanged), `skills/references/task_project_skills.md` (current consumer contract), and `tests/test_project_skills_cli.py` (public CLI regressions and helper-only fixture reuse).

## Acceptance Criteria

- [x] AC1: Given a Project without `history_integrity` or with `records: []`, when real `kosmic_project_skills.py validate --project …` runs against the captured pre-change baseline, then exit code, diagnostics and generated canonical STATUS bytes are unchanged and all existing CLI guards pass unmodified.
- [x] AC2: Given `history_integrity` containing malformed YAML, an unknown/stale path, a duplicate, a noncanonical or uncontained path, or a wrong-owner reference, when `validate` loads the Project, then it fails as a hard configuration/identity/containment error with a specific diagnostic and never silently drops or broadens scope.
- [x] AC3: Given default warn mode with the old done receipt-less `specs/quick-tasks/2026-09-02-projected-link-rewriting.md` configured, when `validate` runs, then it follows its normal success path with a visible per-record diagnostic saying `unverified` and `not audited` (never "verified"), the row keeps claimed `done` lifecycle instead of reopening, and record/receipt/pin bytes are bit-identical after the run.
- [x] AC4: Given warn mode with old approved/draft history configured (bootstrap-registration and library-inventory quick tasks, the draft day-delta skill proposal), when `validate` and `generate-status` run, then each selected record appears as an inspectable unverified warning in output and canonical STATUS with its claimed lifecycle, unfinished approved/draft history stays visible (scope never done-only), and no diagnostic claims completion proof.
- [x] AC5: Given warn mode with the known stale-pin fixture (the day-delta proposal referencing `dream-reflection-workflow`) selected, when `validate` runs, then skip-before-read yields only the generic `unverified — not audited` warning that claims no pin inspection or drift discovery, whole-Project validate is not blocked, and the direct strict loader (`validate-proposal`/`load_skill_proposal`) still detects the actual stale-pin drift under its existing strict semantics.
- [x] AC6: Given configured `mode: strict`, when `validate` runs and a selected record actually lacks or mismatches retrospective proof (e.g. the missing done receipt), then validation fails with an integrity-specific diagnostic while claimed lifecycle/status and receipt bytes remain unrewritten.
- [x] AC7: Given any history configuration, when `render_status`, `_spec_rows`, `status_drift` and `_write_status_reports` produce canonical STATUS, then all four use the same configured view with invocation-independent bytes, and unselected/current rows keep their existing receipt/authority checks with no relaxed row.
- [x] AC8: Given any history configuration, when operational consumers run (`work finish`, `check-completion`, `validate-proposal`, operational loaders), then behavior, exit codes and `--help` surfaces are unchanged — no history flag appears on them, no `HistoryReport` value is accepted where a `SpecCatalog`/`SkillProposal` is required, and no skip/lax flag exists in any operational or catalog API (report/inspection APIs are permitted).
- [x] AC9: Given warn mode on a faithful disposable Project copy under managed scratch, with a selected record whose retrospective artifact is corrupted or unreadable, when the disposable instrumented smoke runs, then the retrospective reader is provably never invoked for selected records (skip-before-read: validation still succeeds as unverified) while the same corruption on an unselected record still fails exactly as the unconfigured baseline, and the live Project is untouched.

## Tasks

### Phase 1: Research
- [x] Pin the clean-writer baseline before source edits: `aac7e9e2f41c4f36821c776016493568dfdef6ec`.
- [x] Verify the frozen Project/strict catalog/receipt boundaries; factor structural discovery and narrow receipt/curated-input integrity without exposing operational objects.
- [x] Capture actual baseline parity, representative legacy record bytes, native report behavior and unsupported operational flag refusal; the known unrelated live stale-proposal failure was not rerun.

### Phase 2: Tests first (new/changed runtime behavior at the CLI seam; extend `tests/test_project_skills_cli.py`; reuse existing passing guards, never forced red)
- [x] TEST-001: invalid-scope and malformed policy inputs fail validate with hard diagnostics.
- [x] TEST-002: absent/empty parity and direct pinned-baseline exit/stdout/stderr/STATUS equality.
- [x] TEST-003: warn receipt-less done succeeds as unverified; strict missing/present-corrupt receipts and stale proposal pins fail read-only.
- [x] TEST-004: canonical view unity; unselected pending and valid/degraded current receipt facts preserved.
- [x] TEST-005: operational unsupported-flag refusal and direct proposal pin strictness; existing CLI/canonical catalog guards reused.

### Phase 3: Implementation
- [x] IMPL-001: typed HistoryPolicy/HistoryReport DTOs, exact scope selection and effective strict inspection; no CLI imports at module initialization.
- [x] IMPL-002: shared private structural scanner; strict catalog constructors still settle, with no bypass catalog or generic skip flag.
- [x] IMPL-003: all configured primary/bounded/flat reporting selects before readers; strict existing proof/pin audits and mode-coherent diagnostics, without blanket CLI-error catches.
- [x] IMPL-004: publication fallback uses the same structural reporting scope, never an unverified operational catalog; unconfigured output remains byte-identical.

### Phase 4: Real smoke and same-episode docs
- [x] Disposable instrumented actual CLI skip-before-read smoke passed on a corrupt selected receipt; no permanent call-count test added.
- [x] Real CLI exercised the three representative actual legacy record byte fixtures under managed scratch: warn success, strict missing-proof/pin refusal, unchanged fixture/live record bytes and unchanged live ProjectEntry.
- [x] Durable Usage invariant updated and canonical Skill Pair regenerated in this episode.

### Phase 5: Independent fixed-base review and native completion
- [x] Both independent axes approved bounded Round2 on the fixed baseline after complete repairs; full STD-001/SPEC-001 ledger retained and reviewer-resolved. Native work finish alone publishes completion.

## Routine Decision

No reusable deterministic routine mechanics are introduced or materially changed: this Story validates and reports on this private Project's own records and guides its CLI callers — ordinary Project validation/reporting, not registered routine compilation or `uses_routines` edges. If implementation actually changes routine edges or reusable registered mechanics, that scope must be updated and re-approved rather than silently expanded.

## Progress

- 2026-10-22: user approved all four Stories; native clean-writer start and baseline pin preceded implementation.
- Observed public-CLI red before implementation; held incomplete worker handoffs until constructor-free reporting, strict flat receipt proof, unselected recorded facts and strict nonterminal proposal pins were exercised successfully.
- CLI module: 215 unchanged cases passed; the corrected strict-pin case and 16 existing catalog guards passed afterward. Actual skip-before-read, pinned-baseline parity, stale-pin and real legacy-byte smokes passed. Formal feature Round1 is requested with completed-pair count still0.
- Formal Round1 completed: Standards STD-001 (bounded policy intersection) and Spec SPEC-001 (lost nonempty operational input-pin guard) are Blocking. Both are assigned for complete worker repair before bounded Round2; the fixed baseline and full ledger are retained.
- Complete R1 worker responses received for both Blocking findings without worker closure. Parent observed all14 focused cases and actual constructor/reader, baseline parity, curated-pin and three legacy-byte smokes pass before requesting bounded Round2; completed-pair count remains1.
- Round2 approved by both independent axes; only then did the completed counter advance1→2 and both findings close. Parent baseline-checked and integrated the seven history source paths with the already-reviewed review slices. Additional actual legacy/bootstrap and identical unselected-corruption probes passed; native receipt publication follows.
- Native finish correctly refused generated bytecode outside the reviewed scope. Parent restored ten pre-existing tracked cache files to the clean baseline and removed the one new generated cache; the seven-file reviewed source diff is byte-identical to approved Round2. Child bytecode writes are now disabled. A bounded final source-fingerprint/scope rebind is requested as Round3, without reopening resolved findings or auditing unchanged source again.
- Final bounded Round3 approved the clean source fingerprint by both independent axes; both findings remain resolved and the seven-file source patch is unchanged from R2. Completed-pair count advances2→3 only after both callbacks; final native completion uses the clean revision.
