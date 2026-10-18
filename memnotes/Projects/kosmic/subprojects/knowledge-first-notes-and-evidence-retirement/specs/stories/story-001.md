---
project_id: "kosmic"
subproject_id: "knowledge-first-notes-and-evidence-retirement"
status: "approved"
record_kind: "story"
local_id: "001"
linked_prd: "../prd.md"
linked_epic: "../epics/epic-001.md"
linked_architecture: "../architecture.md"
depends_on: []
created: "2026-10-18"
updated: "2026-10-18"
consumer_interface_change: true
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

- [ ] AC1: Given a Project with a bound status root and an **approved** PRD
  record, when `python3 skills/scripts/kosmic_project_skills.py generate-status
  --project <ROOT> --work-record <qualified PRD reference>` runs, then it exits
  0, the only mutated path is `<status-root>/STATUS.md`, and the file is the
  deterministic generated render for the catalog as it stands; STATUS_STALE on
  that path clears.
- [ ] AC2: An **approved** Architecture record grants the same single-target
  derived-output refresh as AC1.
- [ ] AC3: Given a `draft` planning record of subproject S, when
  `generate-status` refreshes STATUS during S's planning using that record,
  then the refresh succeeds through the **existing** status-root/directory
  semantics unchanged: the derived output path and its existing view (including
  any fixed-subproject binding) are preserved — the record's ancestry governs
  the derived output path; a narrowed hierarchy-only listing never replaces a
  bound Project-wide STATUS, and no new projection shape is introduced.
- [ ] AC4: Given a planning record whose ancestry does **not** govern the
  derived output path — an owner/subproject mismatch against a fixed-subproject
  bound directory, or a foreign owner/scope — the command refuses
  (`WORK_PHASE_DENIED`) and writes nothing; conversely, a draft record is not
  refused for an otherwise valid refresh of the existing Project-wide derived
  render that includes its own hierarchy.
- [ ] AC5: Given no bound status root (or a bound root that is not a directory),
  `generate-status` refuses for any planning record (`STATUS_ROOT_UNBOUND` /
  `STATUS_ROOT_MISSING`); planning authority never creates, replaces, or
  silently drops a status-root binding.
- [ ] AC6: `work start`/`work finish` still refuse planning records
  (`WORK_PHASE_DENIED`); no receipt is written or validated for a planning
  record; `resolve_work_record`'s implementation kinds/statuses are unchanged
  for every other caller.
- [ ] AC7: Receipt-aware rendering is preserved: with a mixed catalog (approved,
  draft, done-with-receipt, done-without-receipt rows), the regenerated STATUS
  reflects each row's actual recorded state, counts unreceipted done as open
  (`done (receipt pending)`), and mutates no record/receipt/source file.
- [ ] AC8: The existing hand-edit invariant holds: a manually edited STATUS.md
  is never preserved or merged — the next authorized run regenerates over it
  (demonstrated in smoke; no new enforcement or permanent wording pins).

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
  status check at :452–453. ADR-E extends authorization at this one seam only;
  a draft **Story** stays denied (Stories authorize via approval).
- Authorization scope = the derived output path plus record ancestry governing
  it; existing directory/status-root view semantics (fixed-subproject binding,
  strict vs record-scoped `status_drift`) are preserved, not redefined — a
  draft record authorizes the ordinary refresh, it does not narrow the output.
- The planning-mode authorization (ADR-E) is approved design, explicitly not
  implemented anywhere at runtime; do not anticipate Story 003's record-
  embedded completion fields or Story 005's cutover.
- Error surface unchanged: `STATUS_ROOT_UNBOUND`, `STATUS_ROOT_MISSING`,
  `WORK_PHASE_DENIED`, `WORK_RECORD_REQUIRED`; no new error codes.

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
