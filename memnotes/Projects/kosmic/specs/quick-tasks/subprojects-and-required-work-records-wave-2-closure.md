---
project_id: "kosmic"
subproject_id: null
status: "done"
record_kind: "quick-task"
local_id: "subprojects-and-required-work-records-wave-2-closure"
created: "2026-10-14"
updated: "2026-10-15"
closure_of: "historical Subprojects and Required Work Records discussion; original records not located"
---

# Subprojects and required work records: wave-2 closure

> Historical closure summary selected by the user on 2026-10-14. The original
> 067–080 record files were not located in the inspected worktree, Git history,
> or migration inventory. This does not establish when or how they disappeared.
> The archived delivery claims below are not a verified inventory of current APIs.

## Archived delivery claims (not current API inventory)

- **Catalog** (`SpecCatalog`, `kosmic_specs.py`): single owner-aware qualified-id
  catalog; owner-local ancestry; declared dependencies; immutable checked records;
  `MIGRATION_REQUIRED` fallback for flat feature specs.
- **Creation** (`create_spec`): journal-first reservation (`.kosmic/create.lock`
  flock + operation-ID resume), atomic staging (fsync + link/rename), shared
  quick-tasks without PRD, derived records carry `work_handle` only.
- **Registry** (`kosmic_work.py`): `begin_registration`/`register_workdir`;
  registry `kosmic.workdirs/1` + worktree binding; live authority recheck;
  fail-closed bounded reads.
- **Shared boundaries** (stories 069): `SHARED_ROOTS`, `shared_root_conflicts`,
  `validate_shared_roots`/`validate_project_specs`, write/read scope matrix;
  leaf-symlink/special-file denial; unsafe inventories fail closed.
- **Navigation** (story 070): catalog-backed STATUS owner grouping, Work Context
  section, pending terminal receipts (`kosmic.work-receipt/1`), flat-mode
  byte-identical output.
- **Sessions** (story 072): `begin_work`/`work_show`/`delegate_work`/`amend_work`
  /`finish_work`/`abort_work`; claims under `.kosmic/work-sessions.json` with lock;
  reauthorization against persisted reservations; claims survive finalization.
- **Attribution** (story 073): `ScopeTarget`/`parse_scope`/`authorize_write`/
  `observe_write`/`record_write`/`check_change_attribution`; unconditional vault
  baseline at begin; union amendments; approval-carrier digests; lexical paths.
- **Migration planning** (story 078): `migration_plan` — snapshot inventory,
  ambiguities, rewrites with before/after sha, expected outputs, fingerprint
  before/after, `MIGRATION_INPUT_DRIFT` recheck; CLI `migrate-subprojects-plan`.

## Review outcome

The archived conversation reports Standards/Spec review rounds and user decisions.
Those historical reports do not substitute for current pinned review artifacts or
prove acceptance of every lost requirement. Current completion still requires
observed acceptance evidence, real review decisions, scope checks and a receipt.

## Archived verification reports (not rerun by this record)

- Full suite green on the current worktree: **673 tests OK** (2026-10-14), including
  `test_kosmic_specs`, `test_kosmic_spec_creation`, `test_kosmic_shared_roots`,
  `test_kosmic_workdirs`, `test_kosmic_work_sessions`, `test_kosmic_navigation`,
  `test_kosmic_attribution`, `test_kosmic_migration_plan`.
- Real smokes performed at delivery time per story (concurrency, cross-worktree,
  pre-dirty files, ambiguous same-file edits, receipt validation).

## Known losses / follow-ups

- The original feature records were not recovered by the inspected searches. Do
  not reconstruct missing requirements or approvals from implementation guesses.
- The earlier statement that Waves 3–4 were never implemented was incorrect.
  Current source contains live mutation gates (`require_work_record`), qualified
  provenance (`record_run_provenance`), checked completion (`kosmic_completion`),
  workflow/adapter guidance, and migration apply/recover (`kosmic_migration`).
  Replacement migration stories and acceptance/review artifacts also survive under
  `subprojects/deterministic-flat-spec-migration/specs/`. This establishes existing
  mechanisms, not certification of every unavailable original Story 080 criterion.
- The archived session/attribution API list above is not present as listed in the
  current stateless record workflow. Do not recreate it without an approved need.
- The historical `done` frontmatter has no successful checked receipt; STATUS
  correctly treats this summary as receipt-pending. No receipt was fabricated.
