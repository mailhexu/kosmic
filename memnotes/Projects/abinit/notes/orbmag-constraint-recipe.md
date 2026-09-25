---
type: Project Knowledge
title: On-Site Orbital-Moment Constraint (constraint_kind 21/22/23)
description: Wiring, sign calibration, energy slot, finite-difference stress validation, root-cause status, and ABINIT input gotchas for the lambda·L constraint field.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, orbmag, paw, dij, stress-fd]
---

# On-Site Orbital-Moment Constraint (constraint_kind 21/22/23)

## Scope

Exact on-site orbital-moment constraint (the `λ·L` field) in ABINIT projector-augmented-wave (PAW) + Hubbard-U (DFT+U) + spin-orbit coupling (SOC). Working tree: `abinit_local_orbmag`; feature validated 2026-09-16.

## Wiring map (numbered src/ layout)

- Observable `loc_orbmom_cal` (`65_paw/m_paw_correlations.F90`); occupations `setnoccmmp`; L elements `slxyzs` (real-Y basis; bra = second index pair).
- Field injection: add the `λ·L` block to `paw_ij%dij` AFTER `pawdij` + `symdij` in `94_scfcv/m_scfcv_core.F90`, every SCF step. `pawdij` overwrites `%dij`; after `symdij` the block is never symmetrized; `pawdenpot` on-site energies are component-based and never see it.
- Block builder `orbcon_add_dij` (same module): `il==jl` pairs only (`indklmn(3)==0`); radial integral of `phiphj`; angular `slxyzs`; complex packing `cplex_dij=2`; spin-diagonal (idij 1 -> 2, 3 = 4 = 0); `ilm>jlm` flip (pawdijso convention); NO spinaxis rotation (spin-independent field: `U†1U=1`).
- Multiplier state: `constrained_dft_t` fields `orb_lambda`, `orb_resid`, `orbat`, `orbcon_lambda`, `orbcon_active`; updater `orbcon_update` called at BOTH `loc_orbmom_cal` sites in `scfcv_core`; damped integral controller `λ ← λ − ½·gain·(m−t)`.
- Message Passing Interface (MPI): `orb_mom_atom` from `loc_orbmom_cal` is valid only on the gather-master rank; run `xmpi_bcast(orb_mom_sum, 0, comm_atom)` before the update, otherwise ranks diverge.
- Inputs `orbat(3,natom)`; `orbcon_lambda` (gain; 0 = fixed-field mode); `orbcon_lambda_init(3,natom)` (seeded λ). Read `orbat`/`orbcon_lambda_init` in the `nobj==0`/`natrd` branch of `m_ingeo.F90`. Both `constrained_dft_ini` callers must stay in sync (`m_scfcv_core` and `m_setvtr`).

## Sign calibration (do not trust derivations blindly)

The naive `dij = −λ·<L>` sign diverges the moment away from the target. Correct: `dijλ = +amat·rad` with the `ilm>jlm` flip; `amat` mirrors `loc_orbmom_cal`'s transposed `op_l` convention.
Verify: under kind 21 the moment must move TOWARD the target within 2-3 self-consistent-field (SCF) steps.

## Energy slot (resolved)

The dc-scheme in-loop `ETOT` carries the eigen-side field term `−Σλ·m` exactly once, uncancelled. Correct slot in `orbcon_update`: `e_constrained_dft = +Σλ·m` (leak cancellation) `+ Σλ·(t−m)` (envelope); this equals `Σλ·t` at convergence and keeps forces consistent.
The final `total_energy` print (direct scheme) has its own λ-dependence; use the in-loop `ETOT` for constrained-energy work.

## FD stress validation (2026-09-17): trace ok, shear ok, deviatoric bad

1. Freeze-λ runs (`orbcon_lambda 0` plus seeded `orbcon_lambda_init`): the live controller jitters `dij` every step and floors SCF convergence; any fixed λ is self-consistent for an FD-vs-stress audit.
2. `ecut 32`/`pawecutdg 40` mandatory: at `ecut 8` the analytic pressure is 762 GPa (basis garbage) and `E(η)` is non-convex (npw staircase, ±0.03-0.09 Ha jumps). Pressure convergence: −145 GPa (12) to +8.3 GPa (28).
3. Pin BOTH FFT grids: the automatic PAW fine grid switches dimensions with `acell` ((16,16,32) vs (18,18,36) at `pawecutdg 10`; η=0 sits on the boundary), causing energy discontinuities. Use `ngfft` + `ngfftdg` (NOT `ngfftf`; unregistered in this v10.9.3 tree; also no `optene` input; quote `getwfk_filepath`; set `irdwfk 0` with it). Verify boxcut >= 2 per strained run.
4. WFK-chain the strain series (0, ±1, ±2 percent via `getwfk_filepath`) to stay on one DFT+U occupancy branch; `toldfe 1d-10`, `iscf 17`.
5. Verdicts (NiO, V0 = 248.397 Bohr³, λ = ±1.85e-3 Ha): hydrostatic trace ok (2.3 percent, ±1 percent); shear `σ23` ok (0.04 percent); deviatoric `σ11−σ22` SIGN-FLIPPED: FD −1.32e-3 versus analytic +2.08e-3 Ha (robust at ±0.5 and ±2 percent; λ-part about 0.37 GPa).
6. Root cause (2026-09-18): the defect reproduces in COLLINEAR PAW+U (no spinor, no constraint): analytic `σ11−σ22 = −1.07e-2·η` where FD = 0 exactly. It is a base-kernel bug in the classic choice=3 stress contraction (`forstrnps` -> `nonlop_ylm` -> `opernla/opernlc/opernld`, paw_opt=2 `V−εS`): the dev output for an off-diagonal-lmn `D` block equals MINUS its band-energy piece (+1.89e-3 Ha = +2λmₓ, 0.2 percent exact), not the true strain derivative. Exonerated: `pawdij2ekb`, `opernlc` triangle/hermitian handling, `enlk`, the GEMM path, `cprj` `ncpgr` plumbing. Disproven: the `ε·∂S/∂ε` restoration (paw_opt=3 second pass) halves the deviatoric artifact but corrupts the trace by −0.15 per unit η (`sij` mishandled in this stress context); do not retry. Remaining suspect: `opernla_ylm` `cplex=2` `dgxdt` assembly (about lines 484-600) or the paw_opt=2 gauge completion. Next: sympy derivation of the exact `dgxdt` expression, then patch, then full-matrix validation (collinear artifact must vanish; spinor deviatoric to −5.3e-6 constant; trace, shear, forces, `t85`-`t87` unchanged).
7. Practical guidance: under kinds 21-23 trust the analytic stress for the trace (pressure) and off-diagonal/shear channels; for deviatoric diagonal components use FD stresses, or land the kernel fix. Forces are validated (µHa-level FD pair). Use `iscf > 10` (Pulay density mixing); with `iscf 7` the coupled lambda/density iteration oscillates ±0.03 without locking. Gain `orbcon_lambda` about 0.015 works for NiO-scale susceptibility (about 50-82 µB/Ha for Ni-d under U = 4 eV); λ converges early, then the SCF tightens.

## ABINIT gotchas hit in this work

- The parser rejects new inputs that are absent from `list_vars` in `m_dtset.F90`; input-variable names must NOT end in a digit (`orbcon_lambda0` reads as `orbcon_lambda` plus dataset 0, hence `orbcon_lambda_init`).
- `cplex` (angular mesh) differs from `paw_ij(1)%cplex_dij` (2 for spinor); pass the latter.
- `scfcv_core` has TWO `loc_orbmom_cal` convergence blocks (`iscf>=10` and `iscf<10`); patch both.
- `chkinp` exempts kinds 21-23 from the `iscf>10` grid-cDFT guard but still requires `chksymtnons 3`.
- Collinear (`nspden 2`) controls: `spinat` must be parallel to the quantization axis; `nsppol 2` is required when `nsym 1` (AFM `chkinp` check); `spinat` is always 3-vectors per atom in this grammar.
- `runtests.py` takes the test NUMBER (`v10[85]`, not `t85`); the test database is built from git-TRACKED files only, so `git add` new tests before running. Regenerate references after any rebuild (atom-row order and last digits of GPa-scale prints wiggle); keep `tolabs >= 1e-6` (3e-11 fails on the printed 762-GPa stress line); the references' `.Starting date` line matches same-day runs only.
