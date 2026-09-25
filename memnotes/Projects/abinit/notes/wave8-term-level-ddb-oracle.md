---
type: Project Knowledge
title: Wave-8 Term-Level DDB Owner Oracle
description: Identify which native ledger term owns a failing DFPT+U DDB channel via audit-class extension, linear term-level regression, two-q de-degeneration, and negative controls.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc-dftu, dfpt, ddb, audit, fd-oracle]
---

# Wave-8 Term-Level DDB Owner Oracle

## Scope

Use when a DFPT+U DDB channel (for example finite-q U/U0) fails its
finite-displacement closure. The goal is to find WHICH native ledger term
owns the gap.

## 1. Extend the audit, never production

- Add an env-gated audit block (ABI_NC_DFTU_D2U_AUDIT pattern) in
  `m_dfpt_scfcv.F90` after the existing FQC block. Per ordered (lambda, mu)
  slot, emit `AUDIT-CPAIR` and `AUDIT-CPAIR-M` lines with the unlogged
  q/-q cache-pair classes: rv1, missing-occupation arm, response-square,
  response-frozen, frozen-potential. Emit real and imaginary parts.
- The audit must never mutate `d2nl` or `blkflg`. Keep each write line at
  about 13 or fewer `es22.15` fields. The msg buffer is length 500; more
  fields crash with 'End of record'.
- Extend `parse_log` in the fixture closure to merge both lines into one
  20-value CPAIR record.

## 2. Regress FD targets on logged terms

Script pattern: `derive_slot_owner*.py` in
`tests/pending/story539_scalar_finiteq`. Build per-slot complex columns
from every ledger line, in both orientations: the audit key k and the
transpose tr(k). Stack U-U0 differences. Fit with `lstsq` against FD
targets from `fd_dynmat(phi, q)`. Report: full-span residual, coefficient
portrait, and best sparse subsets (all subsets up to size 4).

## 3. De-degenerate with a second q

One q gives collinear columns for symmetry-equivalent slots. Add a second
campaign at q'=q/2 on a k mesh that q translates. On ngkpt 2x2x2 only
q=0.5 works (the PAO BZ parent search dies otherwise). Use ngkpt 4x4x4
for q=0.25 and q=0.5. The FD oracle (real-space IFC npy plus
`fd_dynmat`) provides targets at any q.

## 4. Negative controls before believing a fit

- DDB Hermitization: score the symmetrized difference
  `0.5*(obs[k] + conj(obs[tr(k)]))`. The FD dynamical matrix is Hermitian;
  raw finite-q blocks are not. If the antisymmetric part is far below the
  residual, Hermiticity is a red herring.
- Reference N1_GAUGE=1 (RS covariant projection restoration): if it makes
  FD agreement worse, gauge is not the missing physics.
- Reference-binary transplant: run the reference binary's own DDB through
  the closure. If the reference also fails FD, porting reference semantics
  is invalid.

## 5. Interpretation rules

- A regression coefficient of -1 on a leg means the harvested row already
  contains it (double count). Production must subtract it.
- Full-span residual above 0 across two q means the owner class is absent
  from the basis entirely. The fix is a fresh term-by-term sympy derivation
  of the 2DTE identity, not more harvesting or fitting.
- Sparse subsets stuck above 15% with huge collinear coefficients give the
  same conclusion.

## Build discipline

The wave7-makemake build compiles the STORAGE1 mirror tree. After every
repo edit, copy the touched sources into the mirror before `make`. Check
`diff repo mirror` for drifted files. A kernel can exist in only one copy.
