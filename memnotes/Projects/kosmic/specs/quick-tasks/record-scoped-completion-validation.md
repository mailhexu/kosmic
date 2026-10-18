---
project_id: kosmic
subproject_id: null
status: done
record_kind: quick-task
local_id: record-scoped-completion-validation
created: 2026-10-12
updated: 2026-10-12
consumer_interface_change: true
related_notes: ["notes/cli-projection-commands.md"]
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_round: 0
review_base: dc65bc9
---
# Record scoped completion validation

## Request and approval

The user explicitly selected **Scope completion checks to the active record**.
Do not migrate or edit unrelated legacy mathematical notes. Keep full-vault
validation available and strict. This is a bounded correction of an existing
completion gate, not a new publication or authority model.

## Problem and reproduction

`check-completion` for TB2J SIESTA story 003 fails on
`afm_1d_gamma_q_magnon_report.md` display math without markers. That note is
not declared by the active record. The record's own code, hashes, numerical
oracles and independent review pass. `_check_existing_completion` currently
calls full `validate_project_content`, coupling every record to unrelated
legacy knowledge. Named `check-math --slug` also validates unrelated notes,
preventing verification of the record's declared derivation.

## Scope

- Completion validates declared `related_notes`, record derivations, and
  derivations declared by those notes, with the existing validators reused.
- A non-mathematical record needs no unrelated mathdocs registry.
- Declared malformed/missing/stale notes, derivations or source references
  remain failures. Reject escaping paths; do not silently omit dependencies.
- Named check-math verifies its selected derivations without revalidating all
  unrelated regular notes. Unselected math pairs are preserved during update.
- Consumer completion still verifies whole atomic Skill Pair integrity and
  freshness of the record's declared Consumer knowledge; it must not revert
  to global semantic-note validation through projection freshness checks.
- `validate`, full projection generation and unscoped full math validation
  remain strict global audits. No new skip flag or unsafe bypass.
- Work identity, ancestry, acceptance, review and receipt gates remain unchanged.

## Acceptance Criteria

- [x] Unrelated invalid legacy knowledge/math does not block a record-local completion check.
- [x] Declared invalid knowledge/math still blocks completion, including non-interface early-return records.
- [x] Full-vault validate still rejects the same unrelated defects.
- [x] Named math verification/update and relevant Consumer projection checks honor the declared scope while preserving integrity.
- [x] The real TB2J record reaches its own remaining gate instead of failing on the unrelated AFM note.

## Implementation and ownership

Use an isolated clean snapshot of the current in-flight Kosmic source; pin
its baseline hashes. Never commit, stash, overwrite or publish the user's
existing in-flight tree. Bring back only this fix with source-drift checks.
Never directly edit installed user-authored skills; invoke the canonical CLI
for the final real smoke. Follow existing module/test/Markdown conventions.

## Verification and review

Add failing consumer-visible CLI/validation regression scenarios first.
Exercise record completion, selected math and full validate paths. Pin one
review base and independent Standards/Spec ledgers; re-review fixes only.

## Routine Decision

Existing gate correction only; no routine edge or procedural skill publication.

## Outcome

Implemented in the user tree (drift-checked port of the isolated snapshot):
`_validate_record_content` scopes completion to declared related notes and the
record derivation closure (`load_math_registry(only_slugs=...)`); named
`check-math` selection and `--update` scope to selected slugs;
`_validate_record_projection` keeps whole-pair integrity while checking
freshness only for declared Consumer knowledge; evidence-pack discovery
validates candidates before accepting links. Full `validate`, projection
generation and unscoped math stay strict. 26 new real-CLI regressions
(`tests/test_record_scoped_completion.py`, `tests/test_record_scoped_math.py`,
`tests/scoped_completion_support.py`); full suite 660 tests OK.
Reviews: Spec APPROVED (round 1); Standards APPROVED after STD-1..STD-4
fixed and re-verified. Real smoke: TB2J story-003 completion gate passed with
the canonical CLI; full vault validate still rejects unrelated legacy defects.
