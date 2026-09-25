---
type: Project Knowledge
title: MPI Equality Certification (NC DFT+U Port)
description: Certify serial-vs-MPI equality for NC DFT+U port observables (ETOT/DDB/forces/stress) without transient or solver-identity false failures.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
tags: [abinit, dftu, mpi, paral-kgb, certification]
---

# MPI Equality Certification for the NC DFT+U Port

Use when certifying that a parallel layout (npband, npfft, nblock_lobpcg, k-parallel)
reproduces the serial result for any port observable: ETOT, DDB entries, forces, stress.
Tree: `abinit_dftu_nc_dev`.
## Hard rules
1. **Same-solver references only.** `paral_kgb 1` auto-forces `wfoptalg 114`. A serial
   reference without `wfoptalg 114` compares CG against LOBPCG. Run BOTH serial references
   (CG and `wfoptalg 114`). Gate each MPI leg against its own solver family. K-parallel
   legs (`paral_kgb 0`) reference the CG serial leg.
2. **One-step pinned-restart forces are transient-noise** (~2e-6 to 1.7e-5 Ha/bohr,
   scaling with partial occupations) while ETOT stays bit-identical. This is not an
   assembly defect. Gate forces on converged SCF runs (tolvrs <= 1e-10). Report one-step
   force values as noise-band data only. Stress and ETOT are exact at one step.
3. **Cross-solver force floor is ~1.3e-5 Ha/bohr** (converged CG vs wf114, both serial).
   Never use cross-solver force comparisons as MPI gates; that floor is 100x the
   parallel-vs-serial difference.
4. **Defect scale is 1e-3 or larger.** A missing or misreduced term (example: Hubbard
   force under npband) shows at the 1e-3 / 10% level. Same-solver converged agreement at
   ~1e-7 excludes defects decisively.
## Controls that pay for themselves
- **Port-off twin** (`usedftu_nc 0`): if a suspicious difference reproduces with the port
  off, it is fixture or solver noise, not a port defect. It also catches fixture bugs
  instantly; a shell clone once left `dftu_u 0.294` in a U=0 leg (vres2 ~25, ETOT off
  ~0.2 Ha, forces 40% wrong).
- **U=0 twin** (`usedftu_nc 1, dftu_u 0`): must be BIT-EXACT vs port-off (dF=0, dS=0).
  Any deviation is a port defect at U=0.
- **Deterministic repeat** (same layout twice): must be byte-identical.
## Measured reference values (nkpt=8 spinor NiO fixture, 2026-09-14)
- Converged same-solver wf114 serial vs np2: dF 1.06e-7 Ha/bohr, dS 2.36e-8 Ha/bohr^3.
- One-step stress: 0.0 exact (np2/np4/npfft2/soc1/u0); 3.3e-10 with nblock_lobpcg 15.
- k-parallel (8 ranks): exact (1e-14 / 0.0) even at one step.
## Gate structure and parsing
```
for each layout L in {np2, np4, npfft2, bb2, k8}:
    ref = ser114 if L uses npband>1 else ser (CG)
    gate: stress exact (<=1e-9) at one-step; forces only reported
converged pair: scf_ser114 vs scf_np2 (same solver) -> dF <= 5e-7, dS <= 1e-7
```
Parse .abo blocks: the forces header is `cartesian forces (hartree/bohr) at end:`. Stress
appears as `sigma(i j)= value` pairs under
`Cartesian components of stress tensor (hartree/bohr^3)`. Stop parsing at the GPa block;
otherwise the GPa values overwrite the Ha/bohr^3 values.
