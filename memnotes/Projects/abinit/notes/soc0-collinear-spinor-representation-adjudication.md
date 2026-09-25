---
type: Project Knowledge
title: SOC=0 Collinear-vs-Spinor Representation Adjudication
description: Diagnostic ladder for matched collinear versus spinor ground-state mismatches at SOC=0, with the GGA XC-kernel root cause and representation conventions.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, soc, spinor, xc, adjudication]
---

# SOC=0 Collinear-vs-Spinor Representation Adjudication

## When to use

A matched `nsppol=2, nspinor=1` pair and `nsppol=1, nspinor=2, nspden=4` pair with `so_psp=0` disagree in energy, density, or moments.
Candidate causes: self-consistent-field (SCF) basin, wavefunction-file (WFK) state transfer, Hubbard chain, exchange-correlation (XC) functional, base Hamiltonian.

## Diagnostic ladder (proven on NiO antiferromagnetic, Dojo fully relativistic UPFs)

Run the steps in order; each step kills one hypothesis.
1. Exact state map first. Build a bitwise collinear-to-spinor WFK map: band `2j-1 = (|up_j>, 0)`, band `2j = (0, |dn_j>)`. For multi-k npw padding, use MASKED netCDF reads; `np.asarray` materializes the ~1e36 `_FillValue`. Verify coefficients bitwise on valid slots, Gram blocks near 1e-15, cross-spin exactly 0, eigenvalue/occupation multisets bitwise.
2. Same-state energy (Harris). Run `nstep 0` with `irdwfk 1` and `irdden 1`; this recomputes `etotal` fresh. Do NOT use `iscf=-2` (its `etotal` is inherited restart metadata). Same-state energy equal near 1e-13 Ha means the functional is fine; the defect lives in the SCF iteration map.
3. H1 basin test. Continue the exact mapped state with `iscf 7`, `irdwfk 1`, `wfinit 0`. Re-landing on the collinear state means basin; drifting to the spinor basin means a genuine chain mismatch. A one-step (`nstep 1`) probe is NOT same-state: the collinear restart takes step-1 magnetization from `spinat`-scale input, while the spinor restart rebuilds density and magnetization from the WFK. That asymmetry is a restart-convention artifact, not a seam.
4. H2/H3 surgical probes. Use a disposable `rsync --exclude .git` source copy, an environment-gated patch, and a VPATH autotools build identical to the reference build. H2: zero `V_ud`/`V_du` after the potential build. H3: force the collinear XC input `mx=my=0` in `rhotoxc`. Measure gap survival in percent.
5. U=0 control. Run the `usedftu_nc=0` pair plus mapped continuation; a mismatch persisting at U=0 exonerates the whole NC DFT+U chain.
6. First-density-update trace. Instrument S1 (state), S2 (after `vtorho`), S3 (after `rhotov`), S4 (after `newvtr`), plus per-XC-call kernel-input dumps. In the proven run, everything upstream was bitwise; the first non-equivalent array was the XC kernel spin-up channel.

## Known root cause (upstream develop, commit 6f4006bb5c)

The `nspden=4` GGA path in `src/56_xc/m_rhotoxc.F90` feeds the kernel |m|-majority channels and re-attaches the sign pointwise at write-back AFTER the global FFT-divergence operator. For collinear magnetization changing sign across the cell, this gives a boundary-localized exchange-field error of about 0.1 Ha: `vxc1_S − v_up_C = −div[(F_up−F_dn)χ+]`.
The LDA `ngrad=1` path is exact; `m_norm` floor and the PW91 kernel are exonerated.
Fix (in the projwannpao Refs fork): detect a `collinear_frame` with a rotation-covariant covariance-axis finder and `collinear_axis_tol=1e-5`. The gate MUST be tolerance-based; a bitwise gate silently reverts at SCF step 2 from ~1e-14 transverse noise.
Use signed projection channels for BOTH value and gradient (partial swaps make the error worse); write back directly: `dvdz=(V1−V2)/2`.

## Conventions and gotchas

- Spinor DEN component 4 equals `-m_z`; adjudicate the sign empirically.
- OCCDUMP spinor spin-block order: 1=uu, 2=dd, 3=du, 4=ud.
- At `istep==1`, `cg_from_atoms` clobbers read-in WFKs unless `wfinit 0` (in-tree FIXME).
- A spinor DEN carries no `dftu_nc` persistence payload; `iscf<0` with `nspinor=2` is input-guarded, so fixed-state non-SCF replay does not exist for spinor.
- Record the rebuilt binary SHA; identical configure does not give an identical binary.
