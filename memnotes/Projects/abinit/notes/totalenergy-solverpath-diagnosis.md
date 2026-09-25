---
type: Project Knowledge
title: ABINIT Total-Energy Solver-Path Diagnosis
description: Diagnose ABINIT total-energy defects tied to a wfoptalg or band-parallel solver path.
confidence: 0.8
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Re-run the component diff and serial reproduction on a current ABINIT tree before promotion."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, total-energy, wfoptalg, paral-kgb, diagnosis]
---

# ABINIT Total-Energy Solver-Path Diagnosis

## Scope

Use this procedure on a total-energy defect that appears only under one solver path. Proven case: spinor
norm-conserving density functional theory plus Hubbard U (DFT+U), 2026-09-13, `npband=2` with `wfoptalg=114`.
The reported etotal was off by exactly the trace of the DFT+U potential, 2.12 Ha.

## Isolate by component, not by suspicion

Parse the `EnergyTerms` YAML blocks of the failing leg and the reference leg. Diff every component. If the
component deltas sum to the etotal delta, one term owns the defect. Identify the operator of that term. A delta
equal to the negative trace of the DFT+U potential matches the printed `-dftu_nc_potential` value. That signature
is an operator-definition gap: an evaluation dropped the DFT+U potential. It is not a basis, rotation, or
convergence defect.

## Check the double-counting masking trap

`iscf 17` (`optene=1`) assembles etotal from the eigenvalue sum, the double-counting scheme. It is immune to
nonlocal pseudopotential energy errors. `iscf 7` (`optene=0`, direct scheme) uses `e_nlpsp_vfock` and exposes
those errors. A test that passes under `iscf 17` does not clear the direct scheme. Compare both YAML blocks,
`EnergyTerms` and `EnergyTermsDC`.

## Exonerate Message Passing Interface (MPI) by serial reproduction

Run the failing configuration serially at `npband=1`; `paral_kgb` then forces the wfoptalg through `m_mpi_setup`.
A bit-identical serial reproduction exonerates band parallelism. Also compare against `wfoptalg=4`, the old
locally optimal block preconditioned conjugate gradient (LOBPCG) solver with `getghc`-tracked `totvnlx`.
Correctness under `wfoptalg=4` isolates the defect to the specific solver bookkeeping.

## Separate label defects from basin defects

Run `nstep 2` or `nstep 3` continuations on both legs. A constant etotal offset with step-tracking residuals
(`vres2`) means the energy label is wrong and the physics is right. No false basin exists in that case.

## Avoid cg-side fixes under paral_kgb

Under `paral_kgb=1` the `xgTransposer` scatters states. Per-rank `cg` slots hold layout-transformed data:
per-band norms differ from one and depend on the rank. `gs_hamk%kg_k` holds the dilated fast Fourier transform
(FFT) sphere with `npw_fft_k = 2*npw_k`. A direct wavefunction-side operator evaluation is unusable under
`npband`, even when it works serially. Prefer a layout-independent fix at the energy-assembly level. Use exact
matrix identities, for example the equality of `sum_n f_n <psi_n|V|psi_n>` with the trace of `V n`. Apply the
fix in `m_scfcv_core` after `vtorho`.

## Provenance discipline

Different build trees produce version-string differences and denormal differences of order 1e-16 in `.abo`
comparisons. Check physics pins such as the derivatives database (DDB) before you diagnose a reference mismatch.
On a shared worktree, check `git status` and file modification times before editing. On foreign mid-refactor
breakage, build from a snapshot copy and restore foreign files from `HEAD`.
