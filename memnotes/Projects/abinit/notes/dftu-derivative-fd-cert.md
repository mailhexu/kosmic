---
type: Project Knowledge
title: NC DFT+U Derivative-Channel FD Certification
description: Certify a new norm-conserving DFT+U derivative channel against U-on/U=0 central finite differences; stride audit, deck conventions, h-convergence, v10 pinning.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
tags: [abinit, dftu, finite-differences, certification, forces, stress]
---

# NC DFT+U Derivative-Channel FD Certification

Scope: certify a new analytic derivative channel (force, stress, or response arm) in the
norm-conserving DFT+U code; the oracle is U-on/U=0 central finite differences (FD). Proven:
story-546 forces (8 k-points), story-547 stress (six Voigt); era commit 4502d78, worktree
`abinit_pao_proj`.
## Stride audit first
Workspaces often allocate the mesh maximum (`mpw`) but consume a per-k leading dimension
(`npw_k`). ZGEMM or explicit-shape dummies then read column q from offset `(q-1)*npw_k`;
columns past the first scramble whenever `npw_k < mpw`. Single-k decks have
`mpw == npw_k` and stay bit-exact; they mask the bug. Audit every new buffer: allocation
shape must equal the consumed leading dimension, or slice the call (`buf(1:npw_k, :)`,
matching lda). Certify only on a variable-npw multi-k mesh; `ngkpt 2 2 2` shift 0.5 gives
an npw 1068/1059 mix; check the spread via GSR.nc `number_of_coefficients`.
## Deck conventions
- Each geometry gets twins `{stem}_u1` (U on) and `{stem}_u0` (U=0); the observable is the
  U-delta. The U=0 zero control (mode-1 U=0 vs raw U=0) must be bitwise identical; reuse
  it as the U=0 twin across frames.
- rprim input rows ARE the primitive vectors; code strain acts `rprimd' = F rprimd` on
  rows, so input text rows equal `R @ F^T` for symmetric F. Wrong orientation cost
  story-546 a campaign (shear FD error 4e-6 vs 5e-8).
- Stress FD observable: `(dE(+h) - dE(-h)) / (2 h V)` with `V = acell^3 * |det R|`; Voigt
  order xx, yy, zz, yz, xz, xy. Reduced forces: `f_red = acell * (Rfile @ F_cart)`, not
  Rfile^T. ecutsm is not required for U-delta strain FD (shear matched 5e-8 without it).
- DFT+U SCF is multistable: h=0.005 and 0.01 flipped occupation basins and gave garbage
  diagonal slopes; h=0.0025 matched analytic to 8.7e-8. Always run h-convergence
  (0.01, 0.005, 0.0025 on one component) before adjudicating a residual as a code defect.
  NiO fixture: tolvrs 1e-10, occopt 1, spinmagntarget 0, nsym 1, chksymbreak 0 for
  deterministic serial decks.
## Running and analyzing
- Generate decks with a python generator (one deck per directory). Run 6-way parallel via
  ThreadPoolExecutor against the pinned binary `build-mk/src/98_main/abinit` with
  `ABI_PSPDIR=tests/Pspdir`.
- ABINIT prints `cartesian_stress_tensor: null` when optstress 0. Scan only after the
  marker and assert 3 rows; otherwise the parser reads the xred echo silently.
- Acceptance: residual <= 1e-5 Ha/bohr (forces) and Ha/bohr^3 (stress); the machinery
  typically reaches 1e-7 to 1e-8.
## v10 pinning and dual-build check
Copy the fixture input to `tests/v10/Input/t23x.abi`; register it in
`tests/v10/__init__.py`. Trial-run from a scratch CWD (`abinit t23x.abi`); pin
`tests/v10/Refs/t23x.abo`. Run from `tests/`: `python runtests.py -b ../build-mk
"v10[231]"`. Delete `tests/test_suite.cpkl` to refresh the suite database. fldiff
tolerances live in the input TEST_INFO YAML block. The CMake build (`build-cmake`) also
catches target-dependency errors the makemake build hides (65_pao needed
`abinit::56_recipspace` for m_kg.mod); configure per skill abinit-git-cmake-build.
References: scratch/story546 (forces, CERT_REPORT.md), scratch/story547 (stress,
hconv_h025 table), scratch/story548 (QE crosscheck conventions).
