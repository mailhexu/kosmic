---
type: Project Knowledge
title: ABINIT GGA Finite-Difference Audit Traps
description: favg net-force-leak and FFT-grid noncovariance traps in ABINIT GGA DFPT-versus-FD audits, plus the uninitialized-collective MPI trap.
confidence: 0.8
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Re-run the raw-force certification and grid-convergence check on a current ABINIT tree before promotion."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, gga, dfpt, fd, phonons, mpi]
---

# ABINIT GGA Finite-Difference Audit Traps

## Scope

Use this note when a density-functional perturbation theory (DFPT) Hessian mismatches a finite-difference (FD) reference under the generalized gradient approximation (GGA). The signature: the mismatch appears only under GGA, concentrates on steep-gradient anions (F, O) or their rows, and vanishes for the local density approximation (LDA). This note merges two managed skills. `gga-dfpt-fd-audit` supplies the mechanism, certification protocol, and collective trap; `abinit-gga-fd-audit-favg-trap` supplies the piece-level attribution and campaign conventions.

## Trap 1: favg subtraction hides the leak

`gred2fcart` (`m_geometry.F90` lines 1677-1683) subtracts the per-direction mean force from printed ground-state forces. Printed forces always sum to zero, so the true net-force leak stays hidden. An FD reference built from printed forces re-imports the leak as fake curvature. Observed on LiF F-x legs: -6.2e-3 Ha/bohr against -1.8e-5 under LDA, a fake +31% F-F stiffness.

## Trap 2: FFT-grid translational noncovariance

GGA gradient stencils on a fixed fast Fourier transform (FFT) grid break exact translational invariance. Raw analytic forces carry a net force near 1e-4 Ha/bohr per uniform translation; LDA sits near 1e-6. The leak oscillates in sign and shrinks with grid density: LiF gives +0.497, -0.056, +0.114 Ha/bohr^2 at `ngfft` 36, 45, 54. DFPT reproduces the leak exactly. The leak is physical, not a code defect.

## Audit protocol

- Never use row sums of printed-force FD Hessians under GGA.
- Certify DFPT against raw favg-free forces. Run `prtvol 10`; `clnup2` prints the force partitions before favg: ewald, nonlocal `synlgr`, local, residual. `synlgr` is the full-self-consistent-field (SCF) nonlocal force, raw and favg-free.
- Build each FD column from one displacement family. Use a Richardson h-to-0 cascade over fine legs, for example plus/minus 0.000625, 0.00125, 0.0025, 0.005 bohr. Coarse legs carry large h^2 anharmonicity; two-point estimates at h of 0.01 or more are biased.
- Acceptance: DFPT matches raw grid forces at 1e-5 or better on all elements. The residual row sum is the physical grid leak, present on both sides.

## Piece-level attribution (from `abinit-gga-fd-audit-favg-trap`)

- Run static displaced SCFs and the response run with `prtvol 10`. `dfpt_dyout` prints Ewald, frozen, local, and nonstationary (`d2nl`) second-order pieces. The identity `d2 = frozen + cross` holds exactly as `dyfrnl + d2nl`.
- Printed DFPT `d2` tables are raw Cartesian grid dots `<rho1|vpsp1>`, potential-index first (`dfpt_nstdy`, `m_dfpt_scfcv.F90` lines 4885-4899). The derivatives-database (DDB) raw block equals the printed `d2matr`; the stationary remainder is zero by construction (`m_respfn_driver.F90` line 1563).
- Validate `vxc1` by FD: `prtvxc 1` in a response run writes the isolated first-order exchange-correlation (XC) potential to `rfo_DS2_VXC1..6`. Expect residual h^2 truncation; fit h^2 plus h^4 over 3-4 h values. Compare native-ixc against libxc `vxc1`; agreement sits near 1e-5 in L2 norm.
- `kxc` inputs (`nkxc=7`, GGA, `nspden=1`) are filled in `m_rhotoxc.F90` lines 1144-1148: `k1 = (dvxc1+dvxc9+dvxc10)/2`, `k2 = dvxc3/2 + dvxc12`, `k3 = dvxc5/4 + dvxc13`, `k4 = dvxc7/8 + dvxc15`; per-spin inputs use rho/2 and g^2/4. The libxc path is oracle-clean. Native `ixc=11` Perdew-Burke-Ernzerhof (PBE) correlation second-derivative columns carry 5e-6 to 1e-4 errors; exchange-correlation cancellation amplifies one column to about 2.7e-2 on `k2` at low rho. Phonons are identical; the inputs are not exact.

## Production remedies

Use a dense FFT grid. Use standard `asr 1 chneut 1` in anaddb. Acoustic branches are exactly zero by projection. Optics converge fast: 0.04 per cm between `ngfft` 45 and 54 on LiF SG15 PBE. Check that the ASR-cleaned result is grid-converged.

## Related trap: uninitialized rank-divergent collectives

Symptom: `MPI_ERR_TRUNCATE` in an `MPI_Allreduce` right after early response-setup prints (`getcut`), only with more than one Message Passing Interface (MPI) rank. Cause: a logical flag assigned only inside a feature gate and read outside it. Ranks that read a garbage-true value post one world collective; other ranks post another with a different count, 16 against 11 in the proven case. The specific defect: uninitialized `has_nc_dftu_ddk_source` in `m_dfpt_vtorho.F90`, fixed by initializing it `.false.` before the `usedftu_nc` gate. Diagnose with an `LD_PRELOAD` PMPI intercept that logs per-rank collective sequence and counts. Rule: initialize every flag that gates a world collective at its declaration site.

## Campaign conventions (from `abinit-gga-fd-audit-favg-trap`)

Build `build-l0`; binary `build-l0/src/98_main/abinit`; anaddb lives in the same tree. Runs use `OMP_NUM_THREADS=1 mpirun -np 8`; the project mandates MPI, not serial. First-order DDK (d/dk) wavefunctions: copy `ddko_1WF{7,8,9}` to `rfi_DS2_1WF{7,8,9}`. Seed WFKs: copy to `rfi_DS1_WFK` and `rfi_DS2_WFK`; `nband` must reach `nelect` for packed spinor `nspden=4`. The anaddb files file needs 7 lines including the `.fif` name. Reports live in `<workspace>/reports/`; the fact matrix is `abinit/docs/nc-dftu-dfpt-fact-matrix.md`; the reference write-up is `abinit/docs/nc-dftu-pbe-net-force-leak.md` with campaigns `scratch/{d2nl_probe,vxc1_probe,lifsg15_ngfft45,lifsg15_ngfft54}`.
