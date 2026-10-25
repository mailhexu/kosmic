---
project_id: kosmic
subproject_id: null
record_kind: quick-task
local_id: bound-completion-status-publication-and-ancestry-rendering
status: done
approved_by: user
approved_on: 2026-10-24
approval_provenance: "User explicitly selected 'Authorize bounded Kosmic fix'."
created: 2026-10-24
updated: 2026-10-24
consumer_interface_change: true
related_notes: ["notes/cli-projection-commands.md"]
related_specs: []
related_files:
  - skills/scripts/kosmic_completion.py
  - skills/scripts/kosmic_project_skills.py
  - tests/test_record_scoped_completion.py
  - tests/test_unified_finish_completion.py
  - tests/test_status_planning_authority.py
  - tests/test_kosmic_work_records.py
  - skills/references/cli-projection-commands.md
  - skills/references/work_completion.md
  - skills/references/task_quick_task.md
  - memnotes/Projects/kosmic/notes/cli-projection-commands.md
  - memnotes/Projects/kosmic/skills/.kosmic-pair.json
  - memnotes/Projects/kosmic/skills/kosmic-development/SKILL.md
  - memnotes/Projects/kosmic/skills/kosmic-usage/.kosmic-projection.json
  - memnotes/Projects/kosmic/skills/kosmic-usage/SKILL.md
  - memnotes/Projects/kosmic/skills/kosmic-usage/references/cli-projection-commands.md
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: 159004d1df3abd76a615ea7a44aaf772f37a2048
review_round: 2
completion_observations:
  - criterion: "Completion and valid-receipt retry update only the configured bound STATUS root; at least two other registered roots' sentinel bytes remain unchanged, and no unbound foreign STATUS is created."
    observation: "Main's affected-suite run passed 95 tests and 8 subtests. The bound finish/retry and unbound foreign-STATUS regressions passed. The literal disposable CLI completion smoke restored only the deleted bound STATUS; the original receipt and completion-log bytes, both foreign STATUS sentinel byte strings, and exact record proof remained unchanged."
    source: "Main verification report for tests/test_record_scoped_completion.py, tests/test_unified_finish_completion.py, tests/test_status_planning_authority.py, and tests/test_kosmic_work_records.py; managed-run scratch/completion_smoke.py output (3 PASS lines)."
  - criterion: "`generate-status` succeeds with a clearly labeled bounded scope for a valid active record when unrelated-owner ancestry is malformed, preserving unrelated record bytes; full catalog remains the healthy-path output."
    observation: "The disposable real-CLI fixture case passed with healthy full-catalog output before the unrelated ancestry defect and a labeled bounded owner view afterward, leaving unrelated record bytes unchanged. The separate real CLI smoke on the isolated TB2J Project showed the bounded/current-owner label; only exchange-shell-001 STATUS changed among six registered roots, and foreign sentinel/presence hashes and unrelated records were unchanged."
    source: "tests/test_status_planning_authority.py::StatusPlanningAuthorityTest.test_active_story_falls_back_to_bounded_view_for_unrelated_ancestry; Main report for generate-status on the isolated TB2J Project."
  - criterion: "Same-owner/current-record hierarchy defects and authority failures still refuse; proof, receipt, identity, and approval admission remain unchanged."
    observation: "The selected Story's own malformed ancestry and authority failures still refuse. After R1 repairs, the same-owner sibling missing linked_epic and owner SubprojectEntry linked_prd real-CLI regressions both refuse with ANCESTRY_INVALID and preserve STATUS plus the affected record/owner bytes. The retained hierarchy checks are after existing current-record admission; proof, receipt, identity, and approval gates were not changed."
    source: "Main repaired verification: tests/test_status_planning_authority.py, tests/test_note_curation_metadata.py, and tests/test_kosmic_curation_stages.py (62 passed, 5 subtests); original four-module completion/receipt suite (95 passed, 8 subtests); Main's R1 red report for the two tests."
  - criterion: "Real CLI regression tests cover these behaviors and preserve receipt integrity/idempotence."
    observation: "Both new real-CLI retained-hierarchy regressions pass after the fix. The original completion/receipt suite passed, and the disposable finish/retry smoke preserved receipt, completion-log, record-proof, and foreign STATUS bytes."
    source: "Main repaired 62-test/5-subtest run including tests/test_status_planning_authority.py; original four-module 95-test/8-subtest report; managed-run scratch/completion_smoke.py (3 PASS lines)."
  - criterion: "Existing affected suites and a disposable real CLI end-to-end smoke pass in main-agent verification; current guidance no longer claims all-directory STATUS publication."
    observation: "Main reports the original four-module suite at 95 passed and 8 subtests, the repaired status/curation suite at 62 passed and 5 subtests, and the disposable real-CLI completion smoke passed. The separate isolated TB2J Project generate-status smoke succeeded with an honest bounded label and all five foreign registered STATUS byte/presence hashes unchanged. Current guidance describes bound-only publication and retained-hierarchy refusals."
    source: "Main verification report for the named suites, managed-run scratch/completion_smoke.py (3 PASS lines), isolated TB2J Project generate-status smoke, and current command/completion/Quick Task guidance plus Project pair."
  - criterion: "Notes updated only for the durable current guidance correction; no historical receipts or records rewritten."
    observation: "The current CLI projection note now has the precise UTC instant 2026-10-24T07:07:36.460754Z; the native Project Skill Pair was regenerated. The actual curation parser reports an exact zero-width interval and uncertain=false. No historical receipt or record was edited."
    source: "Main's STD-002 parser report and note_curation_metadata/kosmic_curation_stages verification (part of 62 passed, 5 subtests); native Project generate output; isolated writer scope."
completion_review:
  reviewer: main-assistant-coordinator
  axes:
    standards:
      decision: approved
      reviewer: CompletionIsolationStandards
    spec:
      decision: approved
      reviewer: CompletionIsolationSpec
  decision: approved
  review_base: 159004d1df3abd76a615ea7a44aaf772f37a2048
  reviewed_revision: 32713bb20e5a72a1b038e793cfe9463e3e8e99ee665df8e269dd01c72ffb6f9d
  findings:
    - id: STD-001
      disposition: Blocking
      status: resolved
      resolution: fixed
      detail: "The unconfigured bounded fallback validates the retained owner's linked_prd and every retained owner/shared record ancestry before publication."
      worker_response:
        kind: fixed
        detail: "Added bounded owner-entry and retained-record ancestry checks before STATUS rendering; the configured-history structural fallback is unchanged."
        evidence: "Main's repaired real-CLI hierarchy regressions passed in the 62-test/5-subtest run; the isolated TB2J smoke emitted a bounded label and left all five foreign STATUS paths unchanged."
    - id: STD-002
      disposition: Blocking
      status: resolved
      resolution: fixed
      detail: "The current projection note now carries a precise UTC instant and its Project-owned Skill Pair was regenerated through the native CLI."
      worker_response:
        kind: fixed
        detail: "Set updated to 2026-10-24T07:07:36.460754Z from datetime.now(timezone.utc) and regenerated the Project-owned pair."
        evidence: "Main's _parse_note_instant report showed the exact zero-width interval and uncertain=false; the note and curation suites passed."
    - id: SPEC-001
      disposition: Blocking
      status: resolved
      resolution: fixed
      detail: "The bounded fallback refuses same-owner sibling ancestry and owner SubprojectEntry linked_prd defects before publication."
      worker_response:
        kind: fixed
        detail: "Validated owner linked_prd and the ancestry of every retained owner/shared record; both real-CLI regressions preserve STATUS and record bytes."
        evidence: "Main's repaired status-planning suite passed both new cases; independent R2 review approved the corresponding guard."
  scope:
    - worktree:skills/scripts/kosmic_completion.py
    - worktree:skills/scripts/kosmic_project_skills.py
    - worktree:skills/references/cli-projection-commands.md
    - worktree:skills/references/work_completion.md
    - worktree:skills/references/task_quick_task.md
    - worktree:tests/test_record_scoped_completion.py
    - worktree:tests/test_unified_finish_completion.py
    - worktree:tests/test_status_planning_authority.py
    - worktree:tests/test_kosmic_work_records.py
    - project:notes/cli-projection-commands.md
    - project:skills/.kosmic-pair.json
    - project:skills/kosmic-development/SKILL.md
    - project:skills/kosmic-usage/.kosmic-projection.json
    - project:skills/kosmic-usage/SKILL.md
    - project:skills/kosmic-usage/references/cli-projection-commands.md
    - project:specs/quick-tasks/bound-completion-status-publication-and-ancestry-rendering.md
registration_root: /home/hexu/projects/TB2J_dev/worktrees/kosmic-shell-completion-isolation
registration_outputs:
  - .kosmic/working-directories.json
  - worktree:.kosmic/workdir.json
---

# Quick Task: Bound completion STATUS publication and ancestry rendering

## Request

Implement the separately authorized narrow Kosmic completion/STATUS isolation
fix. Ordinary completion and receipt retry must publish derived STATUS only to
the owning Project's existing `status_root`. `generate-status` should retain
full-catalog rendering when healthy, but after explicit current-record
authority and ancestry validation may render the bounded owner view when an
unrelated owner's malformed ancestry breaks full rendering.

## Scope

- Change only `skills/scripts/kosmic_completion.py` and
  `skills/scripts/kosmic_project_skills.py` for production behavior.
- Add/adjust real-CLI regressions in the three named modules and migrate the
  existing direct-publisher expectation in `tests/test_kosmic_work_records.py`.
- Update current command, completion, and Quick Task references plus the stable
  CLI projection note and regenerate the Project-owned Skill Pair.
- Register the dedicated writer and this record's own index row.

## Out of Scope

- No TB2J source or record changes, no legacy-record edits, and no STATUS
  writes to foreign registered roots.
- Do not modify `ProjectEntry.status_root`, switch bindings, add skip flags,
  mutate the registry except for registering this writer, or establish another
  publication authority model.
- Do not weaken full-catalog validation, same-owner/current-record ancestry,
  identity, approval, scope, proof, receipt, or strict validation checks.
- Main owns the record-owned fix commit, guarded integration, and native work finish after verification/review; this worker must not do these before the test checkpoint. The isolated source-snapshot baseline commit is not the implementation delta and is never integrated.

## Acceptance Criteria

- [x] Completion and valid-receipt retry update only the configured bound STATUS root; at least two other registered roots' sentinel bytes remain unchanged, and no unbound foreign STATUS is created.
- [x] `generate-status` succeeds with a clearly labeled bounded scope for a valid active record when unrelated-owner ancestry is malformed, preserving unrelated record bytes; full catalog remains the healthy-path output.
- [x] Same-owner/current-record hierarchy defects and authority failures still refuse; proof, receipt, identity, and approval admission remain unchanged.
- [x] Real CLI regression tests cover these behaviors and preserve receipt integrity/idempotence.
- [x] Existing affected suites and a disposable real CLI end-to-end smoke pass in main-agent verification; current guidance no longer claims all-directory STATUS publication.
- [x] Notes updated only for the durable current guidance correction; no historical receipts or records rewritten.

## Routine Decision

No reusable deterministic procedure mechanics are introduced or materially
changed; no routine edge or skill proposal is required.

## Implementation Notes

Reuse the current configured `status_root`, completion's bounded
`SpecCatalog.bounded(record.owner)` and `render_status` machinery, and existing
authority validation order.

The unconfigured bounded fallback validates the retained owner's
`SubprojectEntry.linked_prd` and every retained owner/shared record's ancestry
before publication; the configured-history structural fallback remains
unchanged to preserve its warn contract.

The immutable source baseline is writer snapshot commit
`159004d1df3abd76a615ea7a44aaf772f37a2048`, captured from the current
canonical source tree while its Git HEAD was
`906c0ab716dc3da33d9ddeaee21bf3b9db5b413c`; the snapshot commit itself is
provenance only and is not integration-eligible. This SHA-256 manifest is
stored in this record and contains the pre-fix bytes of its owned source,
test, guidance, projection, and Quick Task files, read from that baseline
commit. Python cache artifacts are excluded.

| Path | Baseline SHA-256 |
| --- | --- |
| `skills/scripts/kosmic_completion.py` | `b429aa41607046c39ab9604620be42d1014575a50f85741feeb4a0069fa27cd0` |
| `skills/scripts/kosmic_project_skills.py` | `15445c6a1413fdd3e8d16dd110519d125a982731de844683f9882a199916b4e2` |
| `tests/test_record_scoped_completion.py` | `5dc4e374514d8067ca0792e313e034dabab55e0e1aaf2f223332ffaf364d8777` |
| `tests/test_unified_finish_completion.py` | `ba5ebba402f75c2425bbfe436937e373a5e362c1eab0124cdbca72cea8ecf07f` |
| `tests/test_status_planning_authority.py` | `8757d1834b9068fe49d44194b493dc52cabdebccac91269fb1110f48acd1485a` |
| `tests/test_kosmic_work_records.py` | `d6cdd2766914ca62147893e91aa4553d46c5c3b1cb5e74bda647035903c6489b` |
| `skills/references/cli-projection-commands.md` | `a3b815bb4637e502e87f1752cec8b7a2bd660083049f8dc5e1c76ef13b214270` |
| `skills/references/work_completion.md` | `f22df9af803221e0c0d07593d030c3189c82b977973a06bea257714db4243f6c` |
| `skills/references/task_quick_task.md` | `03ee52ad4b8c9a6d89754b1f950ba58644d1b945ec3966be0c0e33796717de31` |
| `memnotes/Projects/kosmic/notes/cli-projection-commands.md` | `6d1adf9029e1984043726ce3fd4cc1c714ba096add1bbce22c7f420c6c7b75f4` |
| `memnotes/Projects/kosmic/skills/.kosmic-pair.json` | `3e381dfb44c1cd96b4fe9ab7c62e7ad34f524b66a67eb9574109fe8c6c72eb7f` |
| `memnotes/Projects/kosmic/skills/kosmic-development/SKILL.md` | `b1590c6851390be548fc8beb3b8b648e521e2c139caa1ac5a94ef65bb4c7b483` |
| `memnotes/Projects/kosmic/skills/kosmic-usage/.kosmic-projection.json` | `a4b75c7d50e93149891dd6ae63a95f743503efb93ffb64ca02f2e7a009db41e8` |
| `memnotes/Projects/kosmic/skills/kosmic-usage/SKILL.md` | `a659c7574ceebbe7f33f7886916ad782566b54245d79b97abc479ee37f16ac2f` |
| `memnotes/Projects/kosmic/skills/kosmic-usage/references/cli-projection-commands.md` | `83f1d929b18664815d6666d46c38a8def0ac854637abe3a01e574a89ff03b78b` |
| `memnotes/Projects/kosmic/specs/quick-tasks/bound-completion-status-publication-and-ancestry-rendering.md` | `bf3c903f625554a5e2a66f8efe421fab822921d1006c37b03ba4bf8ef3384798` |

## Verification

- Main's initial four-module suite passed 95 tests and 8 subtests; after R1 repair, the status-planning and curation suites passed 62 tests and 5 subtests. The disposable completion smoke passed (3 PASS lines); the isolated TB2J Project generate-status smoke succeeded with all five foreign STATUS paths unchanged.
- The R1 sibling and owner-entry regressions were red before the fix and pass now; the curation parser confirms the new note instant is exact and unambiguous.

## Links

- Related notes: [Projection CLI experience commands](../../notes/cli-projection-commands.md)
- Related specs: none; this new Quick Task is the governing record.
- Related files: `skills/scripts/kosmic_completion.py`,
  `skills/scripts/kosmic_project_skills.py`, the three test modules, and CLI
  guidance.

## Review

Round 2 is complete on the original review base. Both independent reviewers
approved the same fixed source revision; all three R1 Blocking findings are
resolved as fixed, with no new REG/LATE or Non-blocking findings.
`review_round` is 2 and `completion_review` records the actual approvals. The
Work Record remains `approved` pending Main's native finish.

Pinned review base: `159004d1df3abd76a615ea7a44aaf772f37a2048`.
R1 reviewed source revision:
`d18e008a607ee066a3fcbd4a4fffdc0cd79e387443a7ec31adaabc1b3f3d9e93`.
R2 reviewed source revision:
`32713bb20e5a72a1b038e793cfe9463e3e8e99ee665df8e269dd01c72ffb6f9d`.

Review scope:
- `worktree:skills/scripts/kosmic_completion.py`
- `worktree:skills/scripts/kosmic_project_skills.py`
- `worktree:skills/references/cli-projection-commands.md`
- `worktree:skills/references/work_completion.md`
- `worktree:skills/references/task_quick_task.md`
- `worktree:tests/test_record_scoped_completion.py`
- `worktree:tests/test_unified_finish_completion.py`
- `worktree:tests/test_status_planning_authority.py`
- `worktree:tests/test_kosmic_work_records.py`
- `project:notes/cli-projection-commands.md`
- `project:skills/.kosmic-pair.json`
- `project:skills/kosmic-development/SKILL.md`
- `project:skills/kosmic-usage/.kosmic-projection.json`
- `project:skills/kosmic-usage/SKILL.md`
- `project:skills/kosmic-usage/references/cli-projection-commands.md`
- `project:specs/quick-tasks/bound-completion-status-publication-and-ancestry-rendering.md`

### Round 2 Review Result

`CompletionIsolationStandards` and `CompletionIsolationSpec` both approved
the bounded packet on the fixed base. Their R2 decisions resolve STD-001,
STD-002, and SPEC-001 as fixed; there are no new findings or advisories. The
two-axis pair is complete and counted once as Round 2.

- [x] Diff reviewed against scope
- [x] Acceptance criteria satisfied
- [ ] Status set to `done` only after verification passes

## Code Review

**Review Base**: `159004d1df3abd76a615ea7a44aaf772f37a2048`  
**Current Round**: 2  
**Reviewed Revision**: `32713bb20e5a72a1b038e793cfe9463e3e8e99ee665df8e269dd01c72ffb6f9d`  
**Decision**: approved  
**Standards Reviewer**: `CompletionIsolationStandards` — approved  
**Spec Reviewer**: `CompletionIsolationSpec` — approved

### Standards

| ID | Disposition | Evidence | Required Resolution | Introduced | Status | Resolution | Worker Response |
| --- | --- | --- | --- | --- | --- | --- | --- |
| STD-001 | Blocking (P2, confidence 0.99) | At `skills/scripts/kosmic_project_skills.py:4468-4471`, selected-record admission validates only the active Story. The full-catalog render catches a same-owner sibling with missing `linked_epic`, but `SpecCatalog.bounded` (`skills/scripts/kosmic_specs.py:301-319`) does not check ancestry and supplied catalogs bypass `try_project_catalog` (`skills/scripts/kosmic_project_skills.py:3950-3954`). Main's new sibling regression reproduced exit 0 and STATUS publication instead of `ANCESTRY_INVALID`. | Validate the bounded owner's `SubprojectEntry.linked_prd` and every retained owner/shared record's ancestry before unconfigured bounded publication. Preserve configured-history structural warn fallback. | Round 1 | resolved | fixed | kind=fixed; detail=Added bounded owner-entry and retained-record ancestry checks before STATUS rendering; configured-history structural fallback is unchanged. Evidence=Main's repaired real-CLI hierarchy regressions passed in the 62-test/5-subtest run, and the isolated TB2J smoke emitted a bounded label while all five foreign STATUS paths remained unchanged. |
| STD-002 | Blocking (P2, confidence 0.99) | `notes/cli-projection-commands.md:7` replaced precise `2026-10-23T14:58:50.300Z` with date-only `2026-10-24`. ADR 0004 and `task_add_note.md` require an actual UTC instant; `kosmic_curation.py:131-140,476-490,1086-1092` treats date-only metadata as an uncertain day and can refuse finalization with `CURATION_AMBIGUOUS_BOUNDARY`. | Set `updated` using the actual current UTC instant and regenerate the Project-owned Skill Pair with the native CLI; do not edit installed/shared library outputs. | Round 1 | resolved | fixed | kind=fixed; detail=Set note updated to `2026-10-24T07:07:36.460754Z` from `datetime.now(timezone.utc)` and regenerated the Project-owned pair with native `generate`. Evidence=Main's `_parse_note_instant` report showed the exact zero-width interval and uncertain=false; note/curation suites passed. |

### Spec

| ID | Disposition | Evidence | Required Resolution | Introduced | Status | Resolution | Worker Response |
| --- | --- | --- | --- | --- | --- | --- | --- |
| SPEC-001 | Blocking (P2, confidence 0.99) | The bounded fallback at `skills/scripts/kosmic_project_skills.py:4468-4471` can publish despite a same-owner Story's missing `linked_epic`; Main's real-CLI regression reproduced this. The approved acceptance criterion forbids weakening same-owner hierarchy checks. | Retain owner `linked_prd` validation (`skills/scripts/kosmic_specs.py:453-460`) and per-record ancestry validation (`:462`) before fallback publication; cover sibling missing-epic and owner-entry-link defects; leave configured-history structural fallback unchanged. | Round 1 | resolved | fixed | kind=fixed; detail=Validated owner linked_prd and every retained owner/shared record ancestry before publication; configured-history structural path remains unchanged. Evidence=Main's repaired status-planning suite passed both new cases; independent R2 review approved the corresponding guard. |

### Re-review History

| Round | Reviewed Revision | Findings Checked | New REG/LATE Evidence | Decision |
| --- | --- | --- | --- | --- |
| 1 | `d18e008a607ee066a3fcbd4a4fffdc0cd79e387443a7ec31adaabc1b3f3d9e93` | Complete first-pass inventory | n/a | Changes requested |
| 2 | `32713bb20e5a72a1b038e793cfe9463e3e8e99ee665df8e269dd01c72ffb6f9d` | STD-001, STD-002, SPEC-001 resolved | none | Approved |
