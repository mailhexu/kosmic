---
type: Domain Topic
id: abinit/development/nio-elastic-stress-fd-cross-code
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Run matched ABINIT-versus-QE stress-FD elastic-tensor campaigns with exponential strain paths, Bernasconi QE cutoffs, and U-delta Hubbard controls.
triggers: [NiO elastic tensor cross-code, stress FD elastic constants, Bernasconi ecfixed, clamped-ion C11 C12 C44]
aliases: [NiO elastic cross-code]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: 45a0e06d6223e7a34ae1bd820fb41dc398249b8699334ea60a4849f9e92f3593
---

# NiO Elastic Stress-FD Cross-Code Campaign

Run a matched clamped-ion elastic-constant comparison between ABINIT and Quantum ESPRESSO (QE) on the same cell, pseudopotentials, and occupations. The recipe comes from the NiO U=8 scalar-FM campaign (2026-09).

## Fixture matching (do all of these or the comparison is void)

- Same UPF pseudopotentials, same cell (14-digit Angstrom), same fixed occupations, same total magnetization, same U convention: Dudarev with J=0, `HUBBARD atomic` in QE versus `usedftu_nc/dftu_*` in ABINIT reading the same UPF pswfc orbitals.
- Exponential strain path only: `F = expm(L)` with L symmetric and engineering shear h/2 on both entries. Verify det(F) = exp(h) (normal) and det(F) = 1 (shear) symbolically with sympy.
- Strain families: h in {±0.005, ±0.0025, ±0.00125}; C11/C12 from the n1 family, C44 from the s6 family; Richardson estimator `(4*FD(h/2) − FD(h))/3`.
- ABINIT: `ecutsm 0.5` mandatory; nsym 1 with tolsym 1e-12; check `ngfft` is identical across all legs (it is, per ecut; verify in each run.out), because a grid jump would fake stress discontinuities.
- QE: a plain fixed `ecutwfc` does not converge stress-FD (h-drift of tens of GPa). Use the Bernasconi modified functional: `ecfixed` = converged cutoff, `qcutz` about 2x ecutwfc, `q2sigma` about 0.1x ecutwfc. Then h-drift <= 1 GPa.
- QE prints compression-positive stress and ABINIT prints tension-positive; flip one side before differencing and state the flip in the analyzer.

## Convergence adjudication (before comparing codes)

Each code's own h-series must be flat (Richardson pairs agreeing) before any cross-code delta is meaningful. If one side's Richardson pairs disagree by more than the code gap, the comparison is BLOCKED on that side's convergence; say so, and do not re-pin or adjust the other side. Cross-check the base state: base stresses must match after the sign flip to about 0.1 GPa.

## U-delta control (isolates the Hubbard channel)

Run a U=0 twin series in both codes with identical decks and the Hubbard block stripped. Compare U8−U0 per leg: the base stress delta (isotropic for cubic) and dC per channel. Agreement of the U-delta exonerates the Hubbard and projector implementation; any residual gap then lives in the U=0 baseline (cutoff convergence or stress formulation).

## Known fixture pathology

PBE packed-spinor (nspinor=2) NiO strain and electric response diverges (SCF limit cycle). Use the scalar collinear representation (nspinor=1, nsppol=2, fixed occupations 13/5 and 11/7) for elastic work; exact M is achievable and all SCFs converge at tolvrs 1e-10.

## Reference numbers (NiO 2-atom FM, PBE, U=8, 4x4x4 shifted, exp-strain Richardson)

- QE converged: C11 308.0, C12 117.8, C44 82.8 GPa; U0: 256.6/112.7/60.2.
- ABINIT ecut 40: not converged (238→298→318 on C11 across the h-series); ecut 80 legs shift stresses 0.24-0.5 GPa.
- U-delta: base −8.5 GPa isotropic on both codes; dC about +52/+5/+23 GPa on both codes (Hubbard channel consistent).

## Operational notes (nic6)

- Build runner scripts fresh per variant; sed-renaming an existing runner's paths double-substitutes and produces execve failures.
- sbatch job logs: use `-D <writable dir> -o name.%j.log`; default -o paths can land on an unwritable home and the log vanishes.
- 2-rank jobs always fit under QOSMaxCpuPerUserLimit; 6/8-rank jobs queue when sibling sessions hold quota.
