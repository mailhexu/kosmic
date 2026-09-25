---
type: Project Knowledge
title: ABINIT Env-Gated Probe Diagnosis
description: Isolate ABINIT numerical defects with disposable env-gated instrumented builds and three mandatory controls.
confidence: 0.8
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Re-run the three-control sequence on a current ABINIT tree before promotion."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, diagnosis, instrumentation, controls]
---

# ABINIT Env-Gated Probe Diagnosis

## Scope

Use this procedure on a self-consistent field (SCF) or response numerical defect that needs root-cause isolation.
The procedure never touches the production tree.

## Procedure

1. Freeze the baseline. Check out a clean worktree at the pinned commit. Hash-lock the pseudopotentials, the
   inputs, and the reference binary. Save converged campaign artifacts for exact-state restarts.
2. Copy the source into scratch with `rsync -a --exclude .git`. Add one env-gated probe per hypothesis. Follow
   the existing `OCCDUMP` / `ABI_NC_DFTU_*` gate pattern: read `get_environment_variable` at the suspected seam,
   apply the modification only when the variable is set, and `write(std_out,*)` a banner on every firing. Expect
   exactly one banner per SCF step or exchange-correlation (XC) call. The banner count proves the instrumentation
   ran.
3. Build a disposable copy. Configure out-of-tree with the same Fortran compiler and flags as the frozen campaign
   build. Run `make -j24`. Confirm the banner strings inside the binary with `strings`.
4. Run three controls. (a) Gate invariance: the probe-ON run must be bit-identical to the OFF run; this proves
   the gate cannot touch the reference path. (b) Inertness: the OFF run must reproduce the frozen baseline
   bit-for-bit. (c) Discrimination: a deliberate mutation that forces the suspected defect must change the
   observable materially.

## State control beats basin control

Never compare two from-scratch SCF runs when a fixed-state comparison exists. Map wavefunction-file (WFK) states
between representations with bitwise coefficients on valid `npw` slots. For multi-k padding, use masked
`np.asarray` reads; the `_FillValue` of about 1e36 corrupts naive reads. Use an `nstep 0` one-shot Harris
evaluator with `irdwfk` and `irdden` for exact-state energy. The `iscf -2` etotal is inherited restart metadata;
do not use it. Use pinned warm-restart continuations for SCF-map questions.

## Hypothesis discipline

Falsify one hypothesis per build. Rank hypotheses before the first build. Expect the culprit below the obvious
layer. In the spin-orbit coupling (SOC)=0 collinear/spinor campaign the defect was an upstream `rhotoxc`
nspden=4 GGA write-back against the global divergence operator. Same-state energy checks agreed to 1e-13 while
the potential carried a 0.1 Ha error.

Design the gate before the build. A tolerance gate survives numerical noise. A bitwise gate silently reverts at
SCF step 2, when transverse components near 1e-14 appear. A partial fix that moves the value but not the gradient
can worsen the seam. Move all kernel inputs together.

## Proof before porting

Build an exact SymPy or NumPy oracle of the code construction and of an independent textbook route. Execute both
routes. Require machine-zero residuals. This oracle is the acceptance evidence for a production port. Keep it
under `mypapers/DFTU_NC/math/`.

## Signals

- Same-state energy exact but potential differs: suspect a write-back or assembly seam, not the functional.
- Deterministic transverse magnetization: suspect initialization machinery; example: Cholesky normalization rounds `cos(pi/2)` spinors to order one.
- A fresh-run mismatch that vanishes under an exact WFK state map indicates a basin or iteration-map issue, not a
  Hamiltonian defect.
