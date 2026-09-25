---
type: Project Knowledge
title: ABINIT-vs-QE Clamped-Ion Elastic Stress-FD
description: Cross-code elastic certification; QE Bernasconi smooth cutoff mandatory, ABINIT ecut-convergence gate, U-control discriminator, scalar fixture requirement.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
tags: [abinit, qe, elastic, finite-differences, stress, nio]
---

# ABINIT-vs-QE Clamped-Ion Elastic Stress-FD

Cross-code finite-difference (FD) protocol for clamped-ion elastic tensors. Lessons come
from the scalar-FM NiO U=8 campaign (2026-09-25).
## QE side: smooth cutoff is mandatory for stress-FD
Plain `ecutwfc` produces a non-converged strain h-series; Richardson pairs differ by GPa.
Use the Bernasconi modified functional in `&SYSTEM`:
```
ecutwfc = 90.0, ecutrho = 450.0,
ecfixed = 80.0, qcutz = 150.0, q2sigma = 10.0,
```
Convergence gate: h005-vs-h0025 derivative drift <= ~0.7 GPa and Richardson-pair spread
<= ~1.4 GPa. The NiO U=8 4x4x4 fixture achieves both.
## ABINIT side: ecut convergence is the blocker, not the code
At ecut 40 Ha the scalar-FM NiO U=8 stress-FD h-series is unconverged: C11 h005 238 vs
h0025 298 vs Richardson 318.6 GPa; Richardson-pair spread up to 66.7 GPa. Raising ecut
40 to 80 shifts stresses by 0.24 to 0.50 GPa; that matches the ABINIT-QE tensor gap in
order. Run the ABINIT h-series at ecut >= 80 Ha, ecutsm 0.5, h <= 0.0025 before comparing
tensors. Otherwise the residual is a cutoff artifact.
## U-control signature (defect discriminator)
The U8 - U0 base stress delta must be clean isotropic; NiO shows -8.54 GPa on all
diagonal components. The U effect on C comes mostly through the equilibrium state
(C11 318.6 U8 vs 266.5 U0), not a strain-dependent slope defect. A non-isotropic
U8 - U0 base delta is a bug.
## Fixture selection
PBE packed-spinor (nspinor=2) NiO strain/elastic response DIVERGES (vres2 limit cycle).
Use scalar collinear instead: nspinor=1, nsppol=2, occupations
`13*1.0 5*0.0 11*1.0 7*0.0`, spinmagntarget 2.0. All SCF runs converge to tolvrs 1e-10
with exact M=2.0.
## Sign conventions and shear trap
ABINIT prints tensile-positive GPa stress. QE prints compression-positive kbar; multiply
by 0.1 for GPa and flip the sign. Verify through the base-state pressure; both codes gave
|P| ~ 2.9 to 3.0 GPa on this fixture. QE s6 plus-legs can be asymmetric (sigma_xy -0.558
at h=0.005 vs -0.352 at h=0.0025); judge C44 on the Richardson pair, never on a single h.
## nic6 operational
- ABINIT legs: ~6 ranks x 3 to 8 min. QE legs: 2-rank nk2 x ~30 s. Watch
  QOSMaxCpuPerUserLimit; drop to 2-rank jobs when other sessions hold quota.
- SLURM `-o` relative paths land in the submit directory; use `-D` plus an absolute log
  name.
- Never sed-replace the `AB=` build path blindly; double-substitution once produced
  `abinit_dftu_nc_dev/abinit_dftu_nc_dev/`.
