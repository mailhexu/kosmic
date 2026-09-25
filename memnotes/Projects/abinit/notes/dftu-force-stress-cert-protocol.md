---
type: Project Knowledge
title: NC DFT+U Force/Stress Certification Protocol
description: mpw-vs-npw_k BLAS stride audit, variable-npw multi-k FD protocol, U-delta oracles, DFT+U SCF basin-flip h-convergence, MPI bitwise checks.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
tags: [abinit, dftu, finite-differences, blas, stride, stress, mpi]
---

# NC DFT+U Force/Stress Certification Protocol

Story-546/547 protocol (`abinit_pao_proj`, commit 4502d78): one allocation-stride bug
survived three review rounds; every single-k certification was blind to it. Run the audit first.
## mpw-vs-npw_k stride audit
ABINIT passes per-k plane-wave counts (`npw_k`) while workspaces allocate at the mesh
maximum (`mpw`). A buffer consumed by BLAS (`zgemm`/`dgemm` with `lda/ldb/ldc = npw_k`) or
by an explicit-shape dummy `buffer(npw_k, n)` (sequence association) must hold exactly
`npw_k` rows. An `(mpw, n)` allocation consumed at stride `npw_k` reads column q from
offset `(q-1)*npw_k`: a scrambled mix of adjacent columns. Column 1 stays intact;
`nkpt=1` gives `mpw == npw_k`, so single-k certification cannot see the bug. Audit a new
derivative buffer: grep the `ABI_MALLOC` dimension; grep every `zgemm` lda/ldc; grep every
dummy-argument consumer. Explicit `(1:npw_k, 1:norb)` section passes are safe (contiguous
temporary at stride `npw_k`). The bug is silent (no out-of-bounds when `mpw >= npw_k`);
only a variable-npw mesh exposes it. Known-safe pattern (m_nc_dftu_forces.F90 after
4502d78): allocate `dphi_full`/`dphi_tr` as `(npw_k, nproj_tot)` per k inside the k loop;
free them at the k tail.
## Variable-npw multi-k FD certification
- Certify on a mesh with MIXED `npw_k`. A shifted 8-k-point 2x2x2 mesh gives half npw
  1068, half 1059; read the split from GSR.nc `number_of_coefficients`. Gamma-only masks
  stride bugs.
- Oracle: U-on/U=0 central FD of etotal with h = 0.01 and 0.005 bohr; target residual
  <= 1e-5 Ha/bohr. U=0 mode-1 twins must be bitwise equal to raw U=0 (zero control).
- Locator: env-gated per-k increment dump (KDUMP pattern in m_nc_dftu_forces.F90) against
  isolated single-k decks. The (dPhi)L arm "atom sum" is NOT an exact identity in the full
  chain; never adjudicate on it. Per-k deltas against isolated decks locate the defect.
## Stress chain specifics
- Full transformed derivative: `dPhi' = (dPhi)L + Phi(dL)`. Contract against every
  correlated site's V block. Divide `str_dftu` by ucvol exactly once.
- The first Loewner Frechet derivative dL is linear in dS. Reduce dS before or after the
  map; both are exact. Batch all six strain dS matrices into one `comm_fft` collective,
  then map. The second-order d2L audit is serial-only (bilinear terms).
- proc_distrb gates are uniform across `comm_fft` under `paral_kgb`. Reduce all-k caches
  once over `comm_kpt` after the k loop. Verify serial == `mpirun -np 2` bitwise.
- Conventions: rprim input rows are the primitive vectors; code strain is
  `rprimd' = F rprimd`; input rows equal `R @ F^T` for symmetric F. Voigt order xx, yy,
  zz, yz, xz, xy. `f_red = acell * (Rfile @ F_cart)`, not Rfile^T. When converting FD
  energies of force outputs, `f_red = -acell * (R @ F)`; forces carry a minus sign.
## Basin flip invalidates coarse-strain FD
Central-difference stress FD at h = 0.005 and 0.01 hit multistable DFT+U occupation
solutions: garbage, sign-flipping slopes; h = 0.0025 stays in the analytic basin (8.9e-8).
Always run h-convergence (0.01, 0.005, 0.0025) before judging a residual a code defect. A
residual that is O(1e-3), non-monotone in h, or component-inconsistent is a basin flip.
## Reference numbers (AFM NiO fixture, ecut 20 Ha, U 0.294 Ha, 8 k-points)
FD dFx(Ni1) = +1.238000e-03 Ha/bohr; post-fix analytic residual <= 3.7e-6. Stress
(h=0.0025): U-delta diagonal ~ -3.2e-4, shear ~ +1.78e-4 Ha/bohr^3; analytic residual
<= 8.9e-8. MPI: serial vs np2 bitwise on both channels (etotal, forces, strten).
