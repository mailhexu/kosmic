---
type: Project Knowledge
title: Orbmag Lambda-Augmentation Stress Channel (ORBMAGAUG)
description: Wiring, packing conventions, traps, matched-control finite-difference protocol, and sign-flip verdict for the constraint_kind 21 aug-stress term.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, orbmag, paw, stress, fd-protocol]
---

# Orbmag Lambda-Augmentation Stress Channel (ORBMAGAUG)

## Scope

The on-site orbital-moment constraint (`constraint_kind 21`) deviatoric-diagonal stress term in the `abinit_local_orbmag` tree. The term is a stress-only, environment-gated switch: `ABINIT_ORBMAG_AUGSTRESS=1`.

## Wiring (landed; clean build; `t85`-`t87` pass)

- `pawtab%orbcon_augrad(ij_size)` = integral of `(φφ−φ̃φ̃) dr`, filled in `m_paw_init` section 5.
- `m_paw_correlations` module state `orbcon_lambda_st(3,natom)` plus `orbcon_augrad_st` refreshes on every `orbcon_add_dij` call.
- `nonlop_ylm` (choice==3, signs==1, paw_opt==2, cplex_enl==2) builds `enl_aug(dimenl1,natom,nspinor²,1)`, the lambda-weighted packed `L^aug`, with exactly the `orbcon_add_dij` block conventions; it then calls `opernlc_ylm(paw_opt=1, λ=0)` giving `gxfac_aug`, and `opernld_ylm` giving `enlout_aug` (occupation-weighted; no eigenvalue gauge; no `enlk` subtraction); `strconv` without the gauge term.
- `m_nonlop` threads the optional `enlout_aug`; guard `enlout_aug_present` BEFORE the OpenMP (OMP) region, `firstprivate`.
- `forstrnps` exports the optional `npsstr_aug_out(6) = npsstr_aug/ucvol`.
- Critical handoff: the outer `forstr` adds `nlstr_aug` AFTER `pawgrnl` (pawgrnl overwrites `nlstr`) and BEFORE `stress(...)`.

## Traps (each one bit the campaign)

- gfortran does not short-circuit `.and.`: `any()` on a possibly-unallocated module array causes a segmentation fault at `np=8` inside the OMP region; use nested ifs.
- `nonlop_ylm` enumerates `iatm` in `atindx1`-sorted space: the lambda lookup needs the inverse permutation of `atindx1`; `enl` rows use `atindx1` directly.
- `indlmn(4)` is the GLOBAL `ilm`; the m offset is `ilm−l(l+1)−1`.
- Sign chain: `E_leak = −λ·m` gives `σ_aug = +(1/V)λ·dm/dη`, so `npsstr_aug` enters with PLUS.
- Adding into `nlstr` inside `forstrnps` silently dies at `pawgrnl`.

## Finite-difference protocol (matched controls; the only valid comparison)

Derive the unconstrained controls from the constrained decks: same basis, grids, starts; set `constraint_kind 0 0`, `orbcon_lambda 0`, `orbcon_lambda_init 0 0 0`. The stored `u*` decks reference the unavailable `28ni.paw`; version 2 lacks the ±2 percent unconstrained decks.
Energies: use the converged in-loop `ETOT`, never the final `etotal` (the direct-scheme slot differs for constrained runs).
FD `σ_dev = (E(+)−E(−))/(2ηV₀)` with `V₀ = 7.92³/4 = 124.198`.
FD lambda part = FD(constrained) − FD(unconstrained); analytic lambda part = mean `σ_dev`(con) − mean `σ_dev`(un).
Compare the analytic and FD means (constants), NOT slopes; the slope channel was always clean.

## Verdict (2026-09-21, matched controls)

- Slopes (con versus un) agree to 0.02 percent: the base response is correct.
- The constant lambda coupling is SIGN-FLIPPED: analytic +7.3e-6 versus FD −9.9e-6 Ha/bohr³ (robust at ±0.5 and ±2 percent strain).
- The augmentation channel contributes only −3.7e-7 (gate ON minus OFF): two orders of magnitude too small.
- The 0b-era FD lambda part (−5.03e-6) was control-mismatched; the matched value is −9.9e-6.
- Next candidates: the pre-existing +7.7e-6 smooth `D̂_λ` response sign, or the SCF-relaxation (non-frozen-ψ) response.
- Runs: `.tmp/orbmag-constr/fdstress/v2/{handoff_*,final_*,p3_*}`; controls `uncon_*.abi`; comparator `dev_cmp.py`.
