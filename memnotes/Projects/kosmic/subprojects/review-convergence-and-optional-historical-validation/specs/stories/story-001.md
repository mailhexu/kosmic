---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
status: "approved"
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
review_round: 0
completion_observations: []
completion_review: {}
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

## Acceptance Criteria

- [ ] AC1: Given a Project without `history_integrity` or with `records: []`, when real `kosmic_project_skills.py validate --project …` runs against the captured pre-change baseline, then exit code, diagnostics and generated canonical STATUS bytes are unchanged and all existing CLI guards pass unmodified.
- [ ] AC2: Given `history_integrity` containing malformed YAML, an unknown/stale path, a duplicate, a noncanonical or uncontained path, or a wrong-owner reference, when `validate` loads the Project, then it fails as a hard configuration/identity/containment error with a specific diagnostic and never silently drops or broadens scope.
- [ ] AC3: Given default warn mode with the old done receipt-less `specs/quick-tasks/2026-09-02-projected-link-rewriting.md` configured, when `validate` runs, then it follows its normal success path with a visible per-record diagnostic saying `unverified` and `not audited` (never "verified"), the row keeps claimed `done` lifecycle instead of reopening, and record/receipt/pin bytes are bit-identical after the run.
- [ ] AC4: Given warn mode with old approved/draft history configured (bootstrap-registration and library-inventory quick tasks, the draft day-delta skill proposal), when `validate` and `generate-status` run, then each selected record appears as an inspectable unverified warning in output and canonical STATUS with its claimed lifecycle, unfinished approved/draft history stays visible (scope never done-only), and no diagnostic claims completion proof.
- [ ] AC5: Given warn mode with the known stale-pin fixture (the day-delta proposal referencing `dream-reflection-workflow`) selected, when `validate` runs, then skip-before-read yields only the generic `unverified — not audited` warning that claims no pin inspection or drift discovery, whole-Project validate is not blocked, and the direct strict loader (`validate-proposal`/`load_skill_proposal`) still detects the actual stale-pin drift under its existing strict semantics.
- [ ] AC6: Given configured `mode: strict`, when `validate` runs and a selected record actually lacks or mismatches retrospective proof (e.g. the missing done receipt), then validation fails with an integrity-specific diagnostic while claimed lifecycle/status and receipt bytes remain unrewritten.
- [ ] AC7: Given any history configuration, when `render_status`, `_spec_rows`, `status_drift` and `_write_status_reports` produce canonical STATUS, then all four use the same configured view with invocation-independent bytes, and unselected/current rows keep their existing receipt/authority checks with no relaxed row.
- [ ] AC8: Given any history configuration, when operational consumers run (`work finish`, `check-completion`, `validate-proposal`, operational loaders), then behavior, exit codes and `--help` surfaces are unchanged — no history flag appears on them, no `HistoryReport` value is accepted where a `SpecCatalog`/`SkillProposal` is required, and no skip/lax flag exists in any operational or catalog API (report/inspection APIs are permitted).
- [ ] AC9: Given warn mode on a faithful disposable Project copy under managed scratch, with a selected record whose retrospective artifact is corrupted or unreadable, when the disposable instrumented smoke runs, then the retrospective reader is provably never invoked for selected records (skip-before-read: validation still succeeds as unverified) while the same corruption on an unselected record still fails exactly as the unconfigured baseline, and the live Project is untouched.

## Tasks

### Phase 1: Research
- [ ] **Activation task (mandatory, before any edit):** the implementation owner pins `review_base` in this record to the real clean-writer baseline (current `git rev-parse HEAD` of a clean tree). The draft deliberately omits `review_base` — no placeholder value is written now.
- [ ] Known facts: `Project` is frozen (`kosmic_project_skills.py:184-190`: root/entry/project_id/working_state/status_root); `load_project` parses ProjectEntry metadata (~`:1046-1055`); `SpecCatalog.__init__` (`kosmic_specs.py:156`) and `.bounded()` (`:188`) settle receipts via `_settle_receipts` (`:250` → `kosmic_dreams.py:521 pending_terminal_receipts`); `try_project_catalog` (`kosmic_dreams.py:411`); `_spec_rows` (`kosmic_project_skills.py:3768`), `render_status` (`:3914`), `status_drift` (`:4026`), `_write_status_reports` (`kosmic_completion.py:483`); validate parser (`kosmic_project_skills.py:4185`) and STATUS_STALE dispatch (~`:4831-4848`); done-only historical input handling `:3114-3115`; proposal scan including drafts `:3347-3351`; accepted interfaces `_collect_spec_structure(project_root, owner_scope=None) -> _SpecStructure` and `inspect_history(structure, policy, strict_audit=False) -> HistoryReport` (ADR-002).
- [ ] Bounded activation checks (read-only): confirm no existing `history_integrity` handling; capture baseline `validate` stdout/stderr/exit and `generate-status` bytes for the kosmic Project; hash the three representative records plus `STATUS.md`; confirm `validate --help` exposes no history flags today; locate `SpecRef.effective_status` receipt logic.

### Phase 2: Tests first (new/changed runtime behavior at the CLI seam; extend `tests/test_project_skills_cli.py`; reuse existing passing guards, never forced red)
- [ ] TEST-001: invalid-scope fixtures (malformed YAML, unknown/duplicate/noncanonical/uncontained/wrong-owner paths) fail validate with specific hard diagnostics.
- [ ] TEST-002: absent/empty-policy parity — same exit, diagnostics and STATUS bytes as a baseline fixture.
- [ ] TEST-003: warn validate on a selected done-without-receipt fixture succeeds with `unverified`/`not audited` diagnostics and no reopened row; the same fixture under `mode: strict` fails with an integrity diagnostic.
- [ ] TEST-004: canonical-view unity — `generate-status`/`status_drift` reflect the configured view; unselected rows keep receipt-pending and authority rows.
- [ ] TEST-005: operational parity — `work finish`/`check-completion`/`validate-proposal` on a policy-configured fixture behave as baseline; their parsers gained no flags.

### Phase 3: Implementation
- [ ] IMPL-001: create `skills/scripts/kosmic_history.py` — `HistoryPolicy` parsing/validation (exact canonical Project-relative paths, no-follow containment/owner checks, warn default) plus `_collect_spec_structure` and `inspect_history`; `HistoryReport` carries display rows/diagnostics only, is not an operational object, and the module does not import the CLI at initialization.
- [ ] IMPL-002: `kosmic_specs.py` — factor the shared private structural scanner out of `SpecCatalog.__init__`/`.bounded()` preserving their strict public behavior and receipt settlement; no skip-receipts flag or lax catalog.
- [ ] IMPL-003: `kosmic_project_skills.py` — append the immutable optional history policy at the end of frozen `Project`; parse it in `load_project`; resolve configured subjects at the reporting boundary before any retrospective reader; wire warn/skip and strict behavior into `_spec_rows`, `render_status`, `status_drift` and validate diagnostics (`unverified`/`not audited`, never "verified"; hard errors for parse/identity/containment/authority problems, no blanket `KosmicError` catch or string matching).
- [ ] IMPL-004: narrow publication touchpoint — `_write_status_reports` receives the same configured view via one narrow, parent-coordinated change; unconfigured Projects keep byte-identical behavior.

### Phase 4: Real smoke and same-episode docs
- [ ] Disposable instrumented skip-before-read smoke (corrupt retrospective artifact for a selected record; assert the reader never runs and warn succeeds); throwaway only, not committed.
- [ ] Real CLI smoke on a faithful disposable copy of the kosmic Project under the managed scratch workspace, carrying the representative existing record bytes with `history_integrity` configured only in that copy's ProjectEntry: warn success path with warnings, strict failure on the missing receipt, all bytes bit-identical before/after, unselected/current rows unchanged; the live ProjectEntry and history bytes are never edited and all disposables are removed.
- [ ] Update `notes/cli-projection-commands.md` durable invariants (policy semantics, warn default, unverified wording, selection-before-retrospective-reads) and regenerate the published note's native projection, validating clean in the same episode.

### Phase 5: Independent fixed-base review and native completion
- [ ] One independent Standards + Spec review pair against the pinned `review_base` on one held snapshot, with the stable full findings ledger, changed targets and affected checks; one complete pair is one round; repairs/partial callbacks consume no round; maximum three rounds then an explicit human decision packet; reviewer-only closure (`status: resolved`, optionally `resolution: fixed|refuted`); completion only via native receipt (`work finish` for this record) after convergence.

## Routine Decision

No reusable deterministic routine mechanics are introduced or materially changed: this Story validates and reports on this private Project's own records and guides its CLI callers — ordinary Project validation/reporting, not registered routine compilation or `uses_routines` edges. If implementation actually changes routine edges or reusable registered mechanics, that scope must be updated and re-approved rather than silently expanded.
