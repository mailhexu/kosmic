---
type: Domain Topic
id: siesta/development/spinor-dm-seed-rotation
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Build and verify rotated SIESTA spinor DM seeds (x/y from z states): which constructions are exact, verification gates, and known defects.
triggers: [spinor dm seed, rotate density matrix, transverse scf seed, spin-only rotation]
source_project: native
source_sha256: empty
aliases: [dm seed rotation]
---

# SIESTA Spinor DM Seed Rotation

Seed a transverse-axis SCF from a converged z state in the SIESTA fork
(8-real spinor DM storage, col4 = -Im rho12, col8 = +Im rho21).
## Constructions, ranked
1. **Spin-only** (default): D -> (I x W) D (I x W+). Exactly S-unitary
   (S = S_orb x I2), charge-exact, in-pattern, well-conditioned.
   Pipeline: `TB2J.rotate_siestaDM.rotate_file(..., orbital=False)`
   (driver env `SIESTA_ROTATION=spin`). Verified on TmFeO3 x-SCF.
2. **Site-local hybrid** (orbital-quantization seed): on-site blocks
   (R_l x W) D_AA (...)_A+, bond blocks spin-only. Charge-exact
   (intra-atomic S is l,m-diagonal), in-pattern. Warning: currently
   detonates V_U (see defects).
3. **Naive full orbital rotation** R x W everywhere: leaks charge
   proportional to cross-block overlap (TmFeO3: -9.68 e). Never use.
4. **S^(+/-1/2) Loewdin sandwich**: charge-exact but not representable in
   the fixed DM sparsity pattern; truncation is non-PSD and crashes
   cdiag. Dead end for dense solids.
## Verification gates (every seed, before any SCF)
- Tr[D.S] = Qtot to 10 decimals (S and DM from `DMHS.nc`; dense
  kron(S_orb, I2) in spinor space).
- Hermiticity on the torus < 1e-12; write-read roundtrip check.
- Per-atom Mulliken spins rigidly rotated. With orbital rotation: |L|
  preserved AND chirality preserved (S.L angle unchanged; the pipeline
  real_sh_rotation_90 tables rotate L with opposite chirality to the
  spin W — use R_l^T). Wrong chirality puts S parallel L instead of the
  Hund arrangement.
- 1-shot control (MaxSCF 1) from the unrotated z DM reproduces the
  converged energy; the rotated seed matches to meV on isolated atoms.
  For solids compare SCF behavior, not 1-shot energy.
## Known defects (2026-09-18 state)
- V_U breaks on m-coherent on-site occupations (U-off cures the hybrid
  seed; B=0 does not). Historical +U covariance only tested m-diagonal
  occupations. Reproducer: spinphon_native/hybrid_seed_h1/seed_hybrid_v2.DM.
- Pipeline W+ bug FIXED (rotate_density_matrix_supercell right factor
  Wd.conj() -> Wd); phi=0 unaffected, phi != 0 gave Fermid NaN.
- DM/H sparsity is hardwired to the S pattern; out-of-pattern content is
  dropped on read.
## Ops notes
- Ship fdf/scripts as base64 + scp; heredocs mangle %block.
- venv: tb2jflows-native (sisl/netCDF4). Modules dev@<sha>-gcc.
