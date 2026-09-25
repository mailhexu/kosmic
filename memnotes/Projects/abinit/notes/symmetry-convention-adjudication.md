---
type: Project Knowledge
title: ABINIT Symmetry-Convention Adjudication
description: Adjudicate disputed rotation/symmetry/index-map conventions (Bloch phases, symrel/symrec, D-matrix orientation, atom-image maps) between code, paper, and oracle via exhaustive variant scans.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, symmetry, conventions, adjudication, zarot]
---

# ABINIT Symmetry-Convention Adjudication

## Principle

Adjudicate convention disputes by exhaustive variant scan on a
discriminating geometry. Never adjudicate by argument.

## Procedure

1. TARGET: derive the convention from first principles. Example: the
   Bloch-phase covariance of the quantity under the space-group operation.
   Write it as a closed formula. Name every ambiguous factor: map
   direction, D orientation, phase sign, which k, translations folded or
   not.
2. GEOMETRY: pick a geometry that DISCRIMINATES all variants:
   - nonsymmetric symrel (for example hex C3z), so symrel != symrec !=
     symrel^T;
   - atoms cyclically permuted by the operator (this exercises indsym
     rows);
   - nonzero unreduced translations (the integer parts carry physical
     Bloch phases; do not fold them);
   - a GENERIC k (non-Gamma). Gamma-only fixtures make all Bloch phases 1.
3. SCAN: enumerate the full variant grid (map fwd/inv, D vs D^T, phase +/-,
   k_parent vs k_BZ, symrel vs symrec) and evaluate each variant against
   the first-principles target. Use a G set closed under the operator's
   reciprocal action (symrec-orbits) so truncation cancels.
4. ASSERT: exactly ONE variant matches to machine precision. Zero matches
   or more than one match means the grid is incomplete. Extend the grid;
   do not pick a winner.
5. CROSS-CHECK the winner in Fortran terms: which matrix the call sites
   actually pass (symrel dummy vs symrec argument), and what the helper
   routines (`setsym_ylm`, symatm/symchk indsym/transl) actually store.
   Conventions there are frequently the NEGATIVE of intuition.
6. DISCHARGE gates empirically, never by assumption. Build a Fortran
   checker that calls the REAL builder (for example `setsym_ylm` with
   symrec) on the discriminating geometry and compares the routine output
   against a direct G-space evaluation. Known answer (adjudicated
   2026-09-08, abinit commit 33585ac695): `setsym_ylm(symrec)` yields
   input-first zarot. `zarot(ii,jj)` holds the rotated harmonic on the
   SECOND index (D(Rcart)^T in oracle terms). A contraction
   `zarot(out,in) . S . zarot(out,in)` is the correct orientation.
   Feeding real-space symrel instead of symrec makes the internal rot
   `gprimd . sym . rprimd^T` non-orthogonal for nonsymmetric operations,
   and `mkeuler` dies. The ABINIT src/NN directories have no checker
   infrastructure: use a standalone program with manual compile commands
   in its header, tracked in git.
7. DOCUMENT the validated formula and its exactness domain (symmorphic
   operations only? m-degenerate shells only? same-parity only?) in the
   module, the md file, and the paper. State nonsymmorphic caveats
   explicitly.

## Anti-patterns

- Adjudicating on a cubic cell: S^T == S hides the symrel/symrec pairing.
- Accepting an "equivalent" form for symmetric operations without testing
  it numerically.
- Replacing an undischarged verification with an assertion.
