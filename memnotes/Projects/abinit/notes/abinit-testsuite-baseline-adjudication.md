---
type: Project Knowledge
title: ABINIT Test Baseline Adjudication
created: '2026-09-25'
updated: '2026-09-25'
status: draft
audience: development
artifact_role: guideline
---

# ABINIT Test Baseline Adjudication

Run ABINIT test censuses and judge each failure against a saved clean-trunk
baseline, not against stash cycles. Compare deterministically with
`compare_test_results.py` (tab-separated value (TSV) diff), never by eyeballing
HTML. Never trust raw failure counts; cosmetic header lines inflate them.

## Census workflow

1. Snapshot the clean baseline (build plus references at a known commit)
   before a risky landing.
2. Run the census; compare with `compare_test_results.py`.
3. Adjudicate each failure: pre-existing or new. Only new failures gate a landing.

## Chronic red families: the T/S/R drift classes

More than one tree feeds the `tests/v10` namespace; references pinned on
toolchain A run red on toolchain B. Classify each failure from its diff first.

- **Class T, toolchain floating-point noise**: energy and Derivative DataBase
  (DDB) deltas of at most about 1e-8 Ha (last-digit drift on large records),
  plus version-string, date, and zero-flip (1e-35) cosmetics. Verify by
  scanning plus/minus pairs for the maximum matched delta.
- **Class S, structural**: pure line-count drift from version or print
  changes, for example 780 versus 782 lines. Safe to regenerate after you
  confirm no numeric pairs changed.
- **Class R, degenerate representation flip**: per-atom or per-field tables
  reordered between reference and run (atom-2 rows in place of atom-1 rows,
  component-permuted YAML arrays) while energies agree. Benign on symmetric
  fixtures, but it hides spinor convention defects. Eyeball every R flip;
  never blanket-regenerate an R.

## Procedure for a suspicious landing

1. A/B by reverting only the landing. Sibling work in progress compiled into
   the build stays in both arms, so that A/B cannot exonerate it; check its
   diff separately for env-gating.
2. Record per test: reference vintage, toolchain string, signature, class.
3. Regenerate only after classification: run on the target toolchain, diff
   against the old reference, verify the delta matches the ledger, then
   replace and commit with the toolchain string in the message.

## Known drift ledger (develop tree, build-l0, 2026-09-18)

t220: T, etotal 1.4e-9. t221: R, atom-order flip, ETOT 6e-11. t222 and t234: S.
t227_MPI1: T at count level. t230 to t233: T, DDB 4e-9 on 14 to 198 Ha records.
t235: T plus component-permuted YAML arrays. t237, t238, t239: green.
Full table: `port_report/debug/v10-ref-drift-ledger.md`. Pin references per
tree: develop references from the develop build, parity references from the
parity build. Track arbitration in INDEX.
