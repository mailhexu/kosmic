---
type: Project Knowledge
title: NC DFT+U Rotation-Convention Oracle
description: Adjudicate ABINIT symmetry-rotation conventions (symrel vs symrec, zarot orientation, indsym direction, Bloch phases) against first-principles overlap oracles for the NC DFT+U port.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc-dftu, symmetry, zarot, indsym, overlap]
---

# NC DFT+U Rotation-Convention Oracle

## Scope

Use when porting or validating ABINIT k-space symmetry machinery: BZ
expansion, symmetrization, zarot/setsym_ylm usage, indsym bookkeeping.
Covers Waves 2/3/5 of the NC DFT+U port and any overlap/Hamiltonian
rotation code.

## Ground truth

Oracle: `~/projects/mypapers/DFTU_NC/math/pao_projection.py` (sympy;
variants V4a/V4b). Validated identity:

S(k_BZ)_{A lm, B l'm'} =
  e^{-2 pi i k_par . (t_A - t_B)}
  * sum_{mi mj} D^l_{mi m} D^{l'}_{mj m'} S(k_par)_{pi(A) l mi, pi(B) l' mj}

with these conventions:
- k_par = symrec . k_BZ, where symrec = (symrel^-1)^T. The Cartesian
  action of symrec is the ORTHOGONAL Rcart = rprimd . symrel . rprimd^-1.
- D = D(Rcart) enters TRANSPOSED on both sides.
- Rows sit at symrel-forward atom images: tau_pi(A) = symrel . tau_A + t_A,
  with t UNREDUCED.
- The phase sits at the parent k, with a MINUS sign.
- Symmorphic operations only.

## Known fork bugs (adjudicated)

- `rotate_overlap_matrix_nc`: the symrel-based chain fails at O(1) on
  nonsymmetric symrel. `setsym_ylm` fed symrel builds the non-orthogonal
  rot = gprimd . symrel . rprimd. Re-seat the chain on symrec at port time.
- `istwfk=2` fac-2 shortcut: produces spurious odd-parity S blocks
  (0.53 max on the NiO fixture). The exact form is star pairing
  h(G) + (-1)^(l+l') h(G)*, with G=0 counted once.

## Variant-scan recipe (what made V4b decisive)

1. Pick a geometry that actually discriminates: NON-cubic cell plus a
   NONSYMMETRIC integer operation (hex C3z:
   symrel = [[0,-1,0],[1,-1,0],[0,0,1]]), atoms in a genuine permutation
   orbit, and integer lattice offsets so translations are NONZERO. Zero
   translations make the phase degenerate under +/-.
2. Use m-degenerate shells only. Per-m coefficients break the identity.
   Use the same reduced translation per orbit.
3. Close the |n|-ball G set under the group action on n (the reciprocal
   index action is the contragredient n -> symrec . n). Truncation then
   cancels exactly between the two sides.
4. Build the D matrices by exact polynomial solve
   P_lm(R q) = sum D_{mm'} P_{m'}(q). Assert D(R^-1) = D(R)^T and
   orthogonality before use.
5. Brute-force scan ALL convention axes: map fwd/bwd, t-source, phase k
   bz/par, zarot D/D^T, sign +/-. Assert a UNIQUE match below 1e-14.
   Cubic-only tests cannot adjudicate: S^-T = S collapses the axes.
6. Debug ladder when nothing matches: single-atom-on-axis via the exact
   Poisson dual (no G set) -> operator orthogonality -> phi(R q) = D phi(q)
   pointwise -> set bijection. Cartesian-2 pi trap: a phase in Cartesian
   units has NO extra 2 pi (q_cart already contains it); spline arguments
   and kinetic terms are 2-pi-less.

## Reference chain facts

ABINIT symatm: `indsym(4,irot,A)` = symrel^-1 image.
symrec = (symrel^-1)^T. The `setsym_ylm` docstring recommends symrec
input (rot is then orthogonal). `m_paw_sphharm` `setsym_ylm` rot =
gprimd . sym . rprimd (Blanco formula 47).
