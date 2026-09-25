---
type: Project Knowledge
title: NC DFT+U SOC Ground-State Comparison
description: Input recipe and moment-collapse pitfalls for matched spin-orbit-on versus spin-orbit-off ground states of norm-conserving DFT+U magnetic insulators.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc-dftu, soc, nspinor, occopt]
---

# NC DFT+U SOC Ground-State Comparison

## Scope

Compare spin-orbit coupling (SOC) on versus off for ground-state properties of norm-conserving (NC) Hubbard-U (DFT+U) magnetic insulators, for example NiO and MnO.

## Prerequisites

Use fully relativistic NC pseudopotentials: `relativistic="full"`, `has_so="T"`.
Use the same pseudopotentials for the SOC arm and the scalar control arm.

## Input recipe (two-dataset)

```
ndtset 2
jdtset 1 2
nsppol 1
nspden 4
nspinor 2
so_psp1 0 0   # scalar control
so_psp2 1 1   # SOC
getwfk2 1     # read DS1 WFK
useylm 0
occopt 7
tsmear 0.002
toldfe 1.0d-6
diemixmag -4.0
```

## Pitfalls (root causes)

1. `m_chkinp` rejects `pspso!=0` with `nspinor=2` and `useylm=1`; SOC NC pseudopotentials therefore require `useylm 0`.
2. `occopt=0` with `nspinor=2` collapses the ferromagnetic (FM) moment: each spinor band receives equal up and down weight, so the state goes nonmagnetic. Use `occopt 7` (metallic) so the DFT+U exchange splitting can establish the FM state.
3. Reading a collinear WFK into an `nspinor=2`, `occopt=0` run collapses the moment for the same equal-weight reason.
4. Density-functional perturbation theory (DFPT) for NC DFT+U with `nspinor=2` is guarded: only Gamma atomic displacement is supported (Story 494). DDK, electric-field, dielectric, Born-effective-charge (BEC), and finite-q phonon perturbations are NOT available.

## Validation checklist

- The scalar noncollinear energy matches the collinear `nsppol=2` result.
- The total moment magnitude matches the target (example: 2.0 µ_B for FM NiO).
- The Ni local moment survives in the atomic sphere (about 1.7 µ_B).
- The SOC energy stabilization is negative and physically reasonable (10-100 meV).
