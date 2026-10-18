---
project_id: "kosmic"
subproject_id: null
status: "approved"
record_kind: "quick-task"
local_id: "materialize-shared-skill-library-inventory"
---

# Materialize shared skill library inventory

## Intent

The authoritative Shared Skill Library belongs to this repository vault,
memnotes/Skills/, not the separate shared-vault path inspected earlier.
Regenerate its deterministic catalogs and routine inventory. The earlier claim
that the library did not exist anywhere on this machine was not established.

## Scope

- `generate-library --vault {VAULT}` only; no library document content edits.
- Verification: `validate --project {PROJECT}` passes with zero errors, including
  the two 2026-09 routine-pinned proposals.

## Acceptance — met 2026-10-15

- `Skills/.kosmic/routines.json` exists and contains `kosmic/atomic-publish-tree`.
- `kosmic_project_skills.py validate --project memnotes/Projects/kosmic` exits 0.

## Result (2026-10-15)

- Library generated under this record: root router, 8 domain indexes,
  `.kosmic/{catalog,manifest,routines}.json`; `kosmic/atomic-publish-tree` present.
- Historical proposal pins were changed during the preceding validation repair.
  Passing validation after repinning does not independently prove historical
  acceptance or authorize rewriting earlier approvals. Those edits are not
  certified by this record's generation-only scope.
- Whole-project and library validation passed on 2026-10-15.
- Lifecycle remains approved: no acceptance_evidence/review_record contract has
  been published for checked completion of this record. This is not a reason to
  toggle lifecycle fields manually. Work finish is the supported publication
  path; its separate receipt/STATUS ordering defect is tracked by
  keep-completion-status-coherent-with-terminal-receipts.

