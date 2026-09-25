---
status: done
created: 2026-09-25
updated: 2026-09-25
related_notes: []
related_specs: []
related_files: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
---

# Quick Task: Managed-skill consolidation (abinit)

## Request

Unify OMP managed skills with the Kosmic vault. Phase 1: consolidate the 49
managed `abinit-*` skills in `~/.omp/agent/managed-skills/` into Project
Knowledge notes and shared-library topics, then retire the managed copies.

## Approved triage

- A. 33 skills → `memnotes/Projects/abinit/notes/` (build/test infra 7,
  certification protocols 15, port waves 7, debug recipes 4)
- B. 9 skills → 4 merged notes (instrumented dumps, GGA FD audit, WFK
  fixtures, G7 DDK cutover)
- C. 3 skills → `memnotes/Skills/abinit/development/` topics
- D. 6 skills → 1 authoritative `v10-test-workflow.md`
- E. 3 drops (buildbot OOM replay, gitlab-migration-docs, migrate-branch-debug)

Books: 49 skills → 44 notes/topics + 3 deletions.

## Verification

- Notes follow the STE subset (`notes/note-writing-style.md`, kosmic project).
- `generate` + `validate --project memnotes/Projects/abinit` green.
- Library regenerated and validated after batch C.
- Retired managed skills absent from `~/.omp/agent/managed-skills/`.
- Vault committed per batch (commit-cadence rule).

## Outcome

Done 2026-09-25: 49 triaged skills produced 39 project notes + 1 merged v10 note + 3 library topics; 51 managed abinit directories (incl. 2 name-variants) retired; library and pair regenerated and validated.
