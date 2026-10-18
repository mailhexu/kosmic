---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: done
record_kind: "story"
local_id: "001"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
related_notes: ["notes/project-status-file.md", "notes/cli-projection-commands.md"]
created: "2026-10-18"
updated: "2026-10-18"
consumer_interface_change: true
review_base: "0b29a99"
review_round: 2
completion_review:
  reviewer: "coordinator OMP/Main"
  review_base: "0b29a99"
  review_round: 2
  reviewed_revision: "e48ddd2ed7021adcc9f297b77c336a35cae02760e29d9ec6607195b3056ea18c"
  decision: "approved"
  axes:
    standards:
      decision: "approved"
      reviewer: "Review001Standards"
    spec:
      decision: "approved"
      reviewer: "Review001Spec"
  findings:
    - id: "ST-001-01"
      disposition: "Blocking"
      status: "resolved"
      note: "Round-1 Standards finding resolved in the pre/post digest before Round 2; the corrected behavior is in the reviewed source and covered by the final 19-test parent run."
    - id: "01SPEC-1"
      disposition: "Non-blocking"
      status: "retracted"
      note: "Retracted: the finding was a misreading, not a source defect and not a runtime defect — the selected draft-Story STATUS-only generate-status grant conforms to AC3 as approved; the stale Technical Notes wording was clarified to state that this explicit planning grant intentionally overrides the default implementation denial for draft Stories."
    - id: "01SPEC-2"
      disposition: "Blocking"
      status: "resolved"
      note: "Ancestry guard added: every planning grant resolves its declared parent chain owner-locally through SpecCatalog.ancestry at the seam (_generate_status_denial), refusing WORK_PHASE_DENIED before any render work; covered by tests.test_status_planning_authority in the final 19-test parent run."
  scope:
    - "worktree:skills/scripts/"
    - "worktree:skills/references/"
    - "worktree:tests/"
    - "project:skills/"
    - "project:impact.md"
    - "project:subprojects/knowledge-first-notes-and-evidence-retirement/specs/stories/story-001.md"
completion_observations:
  - criterion: "AC1: Given a Project with a bound status root and an **approved** PRD record, when `python3 skills/scripts/kosmic_project_skills.py generate-status --project <ROOT> --work-record <qualified PRD reference>` runs, then it exits 0, the only mutated path is `<status-root>/STATUS.md`, and the file is the deterministic generated render for the catalog as it stands; STATUS_STALE on that path clears."
    observation: "Observed in the supplied managed-scratch real-CLI smoke (fresh synthetic Project below the run scratch): the approved-PRD generate-status run exited 0, public status_drift flipped True->False on the bound STATUS.md (stale cleared), and per-step whole-sandbox digests showed STATUS.md as the only mutated path. That the written file is the deterministic catalog render is a content judgment supported by the rendered rows (identity and status columns matching recorded state), not by a byte-for-byte renderer oracle. Unit support from the supplied green run: test_approved_owner_prd_refreshes_bound_status_only drives the real CLI and asserts rc 0, the stale marker gone, status_drift False, exactly one mutated path, and the PRD row at its recorded approved status. Limitation: full validate was not exercised in the smoke (needs unrelated projection/library fixtures)."
    source: "Parent-supplied real-CLI smoke, managed scratch run 20261018T164034Z-kosmic-kf-001-planning-s-678fc317… (recorded in this record's Technical Notes; not rerun); parent-run 'python3 -m unittest tests.test_status_planning_authority tests.test_status_file -v' — 19 tests OK in the parent's final round-2 run (the pre-review run of the same modules passed 17), including tests/test_status_planning_authority.py::test_approved_owner_prd_refreshes_bound_status_only"
  - criterion: "AC2: An **approved** Architecture record grants the same single-target derived-output refresh as AC1."
    observation: "Observed in the same supplied smoke: the approved-Architecture generate-status run exited 0 with the identical single-target refresh — status_drift True->False and whole-sandbox digests showing only STATUS.md mutated. Unit support from the supplied green run: test_approved_owner_architecture_refreshes_bound_status_only drives the real CLI and asserts the architecture row at its recorded approved status with the single-target mutation check."
    source: "Parent-supplied real-CLI smoke, managed scratch run 20261018T164034Z-kosmic-kf-001-planning-s-678fc317… (recorded in this record's Technical Notes; not rerun); parent-run 'python3 -m unittest tests.test_status_planning_authority tests.test_status_file -v' — 19 tests OK in the parent's final round-2 run (the pre-review run of the same modules passed 17), including tests/test_status_planning_authority.py::test_approved_owner_architecture_refreshes_bound_status_only"
  - criterion: "AC3: Given a `draft` planning record of subproject S, when `generate-status` refreshes STATUS during S's planning using that record, then the refresh succeeds through the **existing** status-root/directory semantics unchanged: the derived output path and its existing view (including any fixed-subproject binding) are preserved — the record's ancestry governs the derived output path; a narrowed hierarchy-only listing never replaces a bound Project-wide STATUS, and no new projection shape is introduced."
    observation: "Observed: the draft-story (approved-ancestry) refresh exited 0 and preserved the bound Project-wide view — both subprojects' rows stayed visible with identity and status columns matching recorded state, and the fixed-subproject constraint line rendered from the registry binding; whole-sandbox digests show STATUS.md as the only mutated path, so no second output path or shape appeared. The no-narrowing property was not separately probed with an adversarial narrowed listing in the smoke; it is supported by the supplied passing real-CLI tests test_draft_record_refreshes_project_wide_render (own and other subprojects' rows both present under a fixed-subproject binding) and test_draft_hierarchy_records_refresh_through_valid_ancestry (draft epic and draft story refresh; approved epic still denied)."
    source: "Parent-supplied real-CLI smoke, managed scratch run 20261018T164034Z-kosmic-kf-001-planning-s-678fc317… (recorded in this record's Technical Notes; not rerun); parent-run 'python3 -m unittest tests.test_status_planning_authority tests.test_status_file -v' — 19 tests OK in the parent's final round-2 run (the pre-review run of the same modules passed 17), including tests/test_status_planning_authority.py::test_draft_record_refreshes_project_wide_render and ::test_draft_hierarchy_records_refresh_through_valid_ancestry"
  - criterion: "AC4: Given a planning record whose ancestry does **not** govern the derived output path — an owner/subproject mismatch against a fixed-subproject bound directory, or a foreign owner/scope — the command refuses (`WORK_PHASE_DENIED`) and writes nothing; conversely, a draft record is not refused for an otherwise valid refresh of the existing Project-wide derived render that includes its own hierarchy."
    observation: "Observed refusal branch: the wrong-fixed-owner probe (a record owned by the other subproject against the directory fixed to main) exited 2 with WORK_PHASE_DENIED and wrote nothing — whole-sandbox digests unchanged and the prior hand edit left intact. The converse is observed: the draft story was not refused for the Project-wide refresh that includes its own hierarchy. Supplied passing real-CLI test test_foreign_planning_record_against_fixed_directory_denied additionally asserts the refusal for draft and approved planning records against a directory fixed to another subproject. Gap: the distinct foreign owner/scope variant without a fixed-subproject binding was probed neither in the smoke nor by a dedicated assertion in this test module."
    source: "Parent-supplied real-CLI smoke, managed scratch run 20261018T164034Z-kosmic-kf-001-planning-s-678fc317… (recorded in this record's Technical Notes; not rerun); parent-run 'python3 -m unittest tests.test_status_planning_authority tests.test_status_file -v' — 19 tests OK in the parent's final round-2 run (the pre-review run of the same modules passed 17), including tests/test_status_planning_authority.py::test_foreign_planning_record_against_fixed_directory_denied"
  - criterion: "AC5: Given no bound status root (or a bound root that is not a directory), `generate-status` refuses for any planning record (`STATUS_ROOT_UNBOUND` / `STATUS_ROOT_MISSING`); planning authority never creates, replaces, or silently drops a status-root binding."
    observation: "Not exercised in the supplied smoke — no unbound or non-directory status-root probe ran there. Unit-level evidence only, from the supplied green run: test_planning_refresh_requires_bound_status_root and test_planning_refresh_requires_existing_status_root_directory drive the real CLI and assert rc 2 with STATUS_ROOT_UNBOUND and STATUS_ROOT_MISSING respectively, no STATUS.md created, and the binding never created, replaced, or dropped. This criterion therefore has no CLI-smoke observation; the passing unit assertions are its evidence."
    source: "Parent-run 'python3 -m unittest tests.test_status_planning_authority tests.test_status_file -v' — 19 tests OK in the parent's final round-2 run (the pre-review run of the same modules passed 17), including tests/test_status_planning_authority.py::test_planning_refresh_requires_bound_status_root and ::test_planning_refresh_requires_existing_status_root_directory; no corresponding probe exists in the managed-scratch smoke"
  - criterion: "AC6: `work start`/`work finish` still refuse planning records (`WORK_PHASE_DENIED`); no receipt is written or validated for a planning record; `resolve_work_record`'s implementation kinds/statuses are unchanged for every other caller."
    observation: "Observed in the smoke: work start and work finish with the planning record both exited 2 with WORK_PHASE_DENIED, and .kosmic/work-receipts was never created across all steps (whole-sandbox digests). Supplied passing test test_implementation_authority_boundary_unchanged additionally asserts resolve_work_record's default denial for the planning record, a quick-task positive control still resolving, draft quick-task and in-progress PRD denials at this seam, the legacy approved and in-progress quick-task refresh still working through the seam, and no work-receipts directory after the sequence."
    source: "Parent-supplied real-CLI smoke, managed scratch run 20261018T164034Z-kosmic-kf-001-planning-s-678fc317… (recorded in this record's Technical Notes; not rerun); parent-run 'python3 -m unittest tests.test_status_planning_authority tests.test_status_file -v' — 19 tests OK in the parent's final round-2 run (the pre-review run of the same modules passed 17), including tests/test_status_planning_authority.py::test_implementation_authority_boundary_unchanged"
  - criterion: "AC7: Receipt-aware rendering is preserved: with a mixed catalog (approved, draft, done-with-receipt, done-without-receipt rows), the regenerated STATUS reflects each row's actual recorded state, counts unreceipted done as open (`done (receipt pending)`), and mutates no record/receipt/source file."
    observation: "Partially observed in the smoke: every regeneration rendered the present rows at their recorded state (approved and draft rows; identity and status columns) and digests proved only STATUS.md mutated — no record, receipt, or source file touched. The scratch catalog contained no done rows, so the receipted-versus-unreceipted done rendering (plain done vs done (receipt pending)) was not observed at CLI level; supplied passing test test_receipted_and_unreceipted_rows_render_recorded_state covers it with a validator-verified successful receipt fixture and asserts receipted done plain, unreceipted done carrying the pending marker, draft and approved rows at recorded state, and the single-mutated-path check."
    source: "Parent-supplied real-CLI smoke, managed scratch run 20261018T164034Z-kosmic-kf-001-planning-s-678fc317… (recorded in this record's Technical Notes; not rerun); parent-run 'python3 -m unittest tests.test_status_planning_authority tests.test_status_file -v' — 19 tests OK in the parent's final round-2 run (the pre-review run of the same modules passed 17), including tests/test_status_planning_authority.py::test_receipted_and_unreceipted_rows_render_recorded_state"
  - criterion: "AC8: The existing hand-edit invariant holds: a manually edited STATUS.md is never preserved or merged — the next authorized run regenerates over it (demonstrated in smoke; no new enforcement or permanent wording pins)."
    observation: "Observed in the smoke: the hand-edited STATUS.md was never preserved or merged — the next authorized run regenerated over it wholesale and status_drift returned clean, while the refusal probes confirm a refused run leaves the hand edit untouched. Supplied passing tests re-assert both halves: the shared assert_refreshed helper rejects stale hand-edit text after every authorized refresh, and test_foreign_planning_record_against_fixed_directory_denied asserts the stale hand edit survives a refused run verbatim."
    source: "Parent-supplied real-CLI smoke, managed scratch run 20261018T164034Z-kosmic-kf-001-planning-s-678fc317… (recorded in this record's Technical Notes; not rerun); parent-run 'python3 -m unittest tests.test_status_planning_authority tests.test_status_file -v' — 19 tests OK in the parent's final round-2 run (the pre-review run of the same modules passed 17), including tests/test_status_planning_authority.py::test_foreign_planning_record_against_fixed_directory_denied and the shared assert_refreshed helper"
---

# Story 1: Bounded planning-phase STATUS rendering

## User Story

As a kosmic maintainer bootstrapping a subproject through `spec-create`,
I want `generate-status` to accept approved PRD/Architecture records — and a
draft planning record refreshing its own hierarchy during planning — as the
sole authority for rewriting the derived STATUS.md,
So that planning progress is visible in derived status without granting
`work finish` capability, any source mutation beyond the one derived output, or
receipt semantics (ADR-E; FR-008 renderer seam; Epic slice 1, no dependencies).

## Acceptance Criteria
- [ ] AC1: Given a Project with a bound status root and an **approved** PRD record, when `python3 skills/scripts/kosmic_project_skills.py generate-status --project <ROOT> --work-record <qualified PRD reference>` runs, then it exits 0, the only mutated path is `<status-root>/STATUS.md`, and the file is the deterministic generated render for the catalog as it stands; STATUS_STALE on that path clears.
- [ ] AC2: An **approved** Architecture record grants the same single-target derived-output refresh as AC1.
- [ ] AC3: Given a `draft` planning record of subproject S, when `generate-status` refreshes STATUS during S's planning using that record, then the refresh succeeds through the **existing** status-root/directory semantics unchanged: the derived output path and its existing view (including any fixed-subproject binding) are preserved — the record's ancestry governs the derived output path; a narrowed hierarchy-only listing never replaces a bound Project-wide STATUS, and no new projection shape is introduced.
- [ ] AC4: Given a planning record whose ancestry does **not** govern the derived output path — an owner/subproject mismatch against a fixed-subproject bound directory, or a foreign owner/scope — the command refuses (`WORK_PHASE_DENIED`) and writes nothing; conversely, a draft record is not refused for an otherwise valid refresh of the existing Project-wide derived render that includes its own hierarchy.
- [ ] AC5: Given no bound status root (or a bound root that is not a directory), `generate-status` refuses for any planning record (`STATUS_ROOT_UNBOUND` / `STATUS_ROOT_MISSING`); planning authority never creates, replaces, or silently drops a status-root binding.
- [ ] AC6: `work start`/`work finish` still refuse planning records (`WORK_PHASE_DENIED`); no receipt is written or validated for a planning record; `resolve_work_record`'s implementation kinds/statuses are unchanged for every other caller.
- [ ] AC7: Receipt-aware rendering is preserved: with a mixed catalog (approved, draft, done-with-receipt, done-without-receipt rows), the regenerated STATUS reflects each row's actual recorded state, counts unreceipted done as open (`done (receipt pending)`), and mutates no record/receipt/source file.
- [ ] AC8: The existing hand-edit invariant holds: a manually edited STATUS.md is never preserved or merged — the next authorized run regenerates over it (demonstrated in smoke; no new enforcement or permanent wording pins).
## Tasks

### Phase 1: Research

- [ ] Map the authorization path at HEAD: `resolve_work_record`
  (`skills/scripts/kosmic_work.py:414`; `kinds=IMPLEMENTATION_KINDS` :59,
  `IMPLEMENTATION_STATUSES` :58, denials :449–450/:452–453),
  `require_work_record` (`kosmic_project_skills.py:1773`, call :4204),
  `generate_status` (:4195–4216), `generate-status` parser (:4500–4502) and
  dispatch (:4666–4669); verify via `SpecCatalog.ancestry(record)`,
  `dependencies(record)`, `validate()` (reviewer-verified public API) how a
  record's ancestry governs the derived output path and its bound directory.
- [ ] Verify the **current** view semantics that AC3/AC4 must preserve: bound
  directory / `fixed_subproject_id` handling, the strict vs record-scoped
  `status_drift` fallbacks (:4163–4190), and the completion-side bounded
  publication (`kosmic_completion.py:302–309`); document how a record-bound
  view, if one already exists, stays coherent with directory/render/drift —
  without mandating a new projection shape.
- [ ] Confirm the ADR-E gap at HEAD: `spec-create` bootstraps planning records
  with no work-record gate (bounded `spec-create` exemption in
  `kosmic_project_skills.py`), so a fresh draft cannot refresh STATUS today;
  check memnotes for prior renderer/authorization knowledge; document the
  chosen planning-mode shape in Technical Notes.

### Phase 2: Tests (TDD — write first, red before green)

- [ ] TEST-001: authorization matrix — approved PRD and Architecture pass; a
  `draft` planning record passes for the derived output its own hierarchy
  governs; owner/subproject mismatch against a fixed-subproject bound
  directory and foreign owner/scope refuse with nothing written (AC1–AC4).
- [ ] TEST-002: authority boundary — `work start`/`work finish` with a planning
  record still raise `WORK_PHASE_DENIED`; implementation kinds/statuses
  unchanged for all other `resolve_work_record` callers; no receipt path
  touched (AC5, AC6).
- [ ] TEST-003: consumer catalog states — with approved / draft / receipted /
  unreceipted rows, the regenerated STATUS shows each row's actual state and
  pending counts, and no record, receipt, or source file is mutated (only
  STATUS.md changes). Renderer wording (marker, exact suffix, help text) is
  exercised only in throwaway smoke, never pinned by permanent tests (AC7).

### Phase 3: Implementation

- [ ] IMPL-001: add the bounded planning authorization at the renderer seam
  only — a planning-mode kind/status set applied by `generate_status`'s
  `require_work_record` call, enforcing the ADR-E scope rule (approved PRD/
  Architecture; `draft` while its own hierarchy governs the derived output
  path), reusing the existing binding/view machinery rather than adding a
  second scoping mechanism or output shape.
- [ ] IMPL-002: keep every other gate untouched — implementation kinds/statuses,
  `work start`/`finish`, ancestry checks, receipt validation, `render_status`
  row semantics, `_row_is_open`, `RECEIPT_PENDING_SUFFIX`,
  `STATUS_GENERATED_MARKER`, and the existing status-root binding behavior.

### Phase 4: Review

- [ ] Real CLI smoke: one approved-PRD regenerate, one draft own-hierarchy
  refresh, one owner-mismatch refusal, and one hand-edit overwrite (AC8),
  then the Project's drift/validate check to confirm agreement.
- [ ] Update this Story's owned consumer docs (the `generate-status` sections
  of `skills/references/cli-projection-commands.md`); Story 005 reconciles the
  remaining cross-cutting docs; independent two-axis review (Standards + Spec)
  recorded per the current review process.

## Non-Goals

- No relaxation of `work start`/`work finish` phases; no planning-phase
  completion channel; no receipt semantics for planning records (ADR-E).
- No new or narrowed STATUS projection shape, no status-root binding changes,
  no collision-detection changes; planning authority never writes any other
  target than the existing derived output path.
- No change to `render_status` content semantics beyond the authorization;
  no doc/projection cutover beyond the `generate-status` doc slice (Story 005);
  no dead-error-table or unrelated cleanup.

## Routine Decision

No reusable deterministic procedure mechanics are introduced; an existing
deterministic renderer is re-authorized for planning-phase records within
ADR-E's bounds.

## Technical Notes

- Verified at HEAD: an approved PRD reports `WORK_PHASE_DENIED` ("not an
  implementation record", `kosmic_work.py:449–450`); a draft Story fails the
  default implementation status check at :452–453. That default resolver
  contract is unchanged: implementation start/finish still deny a draft
  Story. ADR-E instead authorizes one selective seam — `generate-status`
  explicitly grants a draft Story (with resolving ancestry) the single
  derived STATUS refresh; "stays denied" below refers to implementation
  authority only, never to this renderer grant.
- Authorization scope = the derived output path plus record ancestry governing
  it; existing directory/status-root view semantics (fixed-subproject binding,
  strict vs record-scoped `status_drift`) are preserved, not redefined — a
  draft record authorizes the ordinary refresh, it does not narrow the output.
- The planning-mode authorization (ADR-E) is approved design, explicitly not
  implemented anywhere at runtime; do not anticipate Story 003's record-
  embedded completion fields or Story 005's cutover.
- Error surface unchanged: `STATUS_ROOT_UNBOUND`, `STATUS_ROOT_MISSING`,
  `WORK_PHASE_DENIED`, `WORK_RECORD_REQUIRED`; no new error codes.
- Implemented at HEAD of this worktree (uncommitted, review_base 0b29a99
  preserved), selective matrix per parent GREEN-batch corrections:
  `generate_status` resolves through one `require_work_record` call with
  union kind/status sets and then applies `_generate_status_denial`
  (`kosmic_project_skills.py`): legacy implementation grants (story/
  quick-task with approved/in_progress) stay exact and bypass the planning
  scope guard, so project-level quick-task authority is not retroactively
  denied by a fixed-subproject bound directory; planning grants are
  approved PRD/Architecture plus draft PRD/Architecture/Epic/Story (draft
  story additionally gated on approved ancestry by `resolve_work_record`),
  guarded by the ADR-E hierarchy-governs-output rule reusing
  `load_registry`'s `fixed_subproject_id` entry lookup. Everything else at
  this seam denies `WORK_PHASE_DENIED`: draft quick-task, in-progress
  PRD/Architecture, approved epic, terminal statuses. After review finding
  01SPEC-2, every planning grant additionally requires its declared parent
  chain to resolve owner-locally through `SpecCatalog.ancestry` at the seam
  (`_generate_status_denial`), surfaced as `WORK_PHASE_DENIED` before any
  render work — previously a malformed chain passed authorization and was
  refused only incidentally by the render's whole-Project validation.
  Planning parents need no approved status: the resolver keeps the draft
  Story's approved-ancestry contract, the seam only requires resolution.
  Legacy implementation grants bypass both planning guards unchanged. The flat
  `PLANNING_KINDS`/`PLANNING_STATUSES` constants were removed; the generic
  `statuses` parameter on `resolve_work_record` stays (union sets, defaults
  byte-identical for every other caller). Fixture recipes discovered for the consumer tests: registry
  entry shape (`kosmic.workdirs/1`, `directory_id = "wd-"+sha256(path)[:16]`,
  `authority.record`/`run_id` required, `.kosmic/working-directories.json`
  under the Project root — `kosmic_work.py:155-208`); a successful receipt is
  `.kosmic/work-receipts/<sha256(qualified_id)[:16]>.json` whose `proof`
  equals `validate_completion_proof` (acceptance-evidence + review JSON under
  the Project root, story frontmatter `acceptance_evidence`/
  `review_record`/`review_base`, criteria text identical to `- [x]` lines —
  `kosmic_completion.py:101-163`); receipt schema bytes taken from the
  validator itself in the fixture. (Superseded by the Story 003 cutover: the
  fixture now embeds `completion_observations`/`completion_review` in the
  record itself and the receipt binds exactly `{record_path: record_sha256}`
  via `validate_completion_proof`; no sidecar files.) `work start` resolves the record before
  any worktree check (`check_work_start:614-616`), so planning records are
  refused CLI-level regardless of registration. No
  `cli-projection-commands.md` existed at base in either tree; the owned
  `generate-status` section now seeds `skills/references/cli-projection-commands.md`
  (Story 005 reconciles the rest). Acceptance Criteria normalized to one
  physical `- [ ]` line per criterion (whitespace-only diff, machine-verified)
  so receipt-side proof coverage matches the exact checkbox lines contract.
  All changes statically verified (compile, signatures, call sites, fixture
  protocol parity, symtable); test execution stays with the parent's GREEN
  batch.
- Real-CLI smoke (managed scratch run 20261018T164034Z-kosmic-kf-001-planning-s-678fc317…,
  fresh synthetic Project below the run scratch; no copied registry/user
  data): approved PRD, approved Architecture, draft story (approved
  ancestry), and legacy approved/in_progress quick-task records all refresh
  the bound STATUS.md with rc=0 and status_drift True→False; the
  wrong-fixed-owner probe (other vs main) and `work start`/`work finish`
  with the planning record all exit 2 WORK_PHASE_DENIED writing nothing;
  hand-edit stale → authorized regen → clean drift demonstrated with real
  rows — the Project-wide view survived every step (both subprojects' rows
  visible; identity/status columns match recorded state; "Fixed directory
  constraint: subproject main" rendered from the registry binding).
  Per-step whole-sandbox digests: only STATUS.md ever mutated;
  `.kosmic/work-receipts` never created. Limits: full `validate` not
  exercised (needs unrelated projection/library fixtures) — public
  `status_drift` plus observed rows are the demonstrated surface; synthetic
  fixture approvals are test data, not real feature approvals.

## Assumptions & Verification

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Planning records resolve through `SpecCatalog` with ancestry usable to bind the derived output path | ⬜ | Phase 1 check (`ancestry`/`dependencies`/`validate`) |
| Existing binding/view machinery (fixed-subproject, bounded publication, drift fallbacks) suffices for AC3/AC4 unchanged | ⬜ | Phase 1 check (`kosmic_project_skills.py:4163–4190`, `kosmic_completion.py:302–309`) |

## Definition of Done

- [ ] All acceptance criteria met and demonstrated via the real CLI (Phase 4)
- [ ] All tests pass; no regressions in the existing suite
- [ ] Independent Standards + Spec review recorded
- [ ] Owned consumer docs (`generate-status` sections) updated
- [ ] Scope discipline: only the renderer-authorization seam, its tests, and
  its doc slice changed

## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| 2026-10-18 | Created | Initial draft |
| 2026-10-18 | Approved | User approved this story as part of the full five-story set; awaiting implementation |
| 2026-10-18 | Revised | Review corrections: output-shape neutrality, consumer-state tests, real CLI invocation, scope trims |
| 2026-10-18 | Started | Work start accepted at setup commit 0b29a99; implementation delegated |
| 2026-10-18 | Implemented | Planning-phase authorization staged at the renderer seam + consumer regression suite in `tests/test_status_planning_authority.py`; all changes uncommitted for binding/review; Acceptance Criteria lines normalized to one physical checkbox per criterion per the receipt contract |
