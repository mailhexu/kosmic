---
type: Project Knowledge
title: ABINIT MPI Distribution Invariants
description: Correctness constraints for CG-derived quantities under ABINIT k-point, band, FFT, and spinor parallelization.
confidence: 0.8
created: '2026-09-08'
updated: '2026-09-08'
validation_procedure: "Re-execute the referenced topology matrix on a current ABINIT tree before promotion or projection."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, mpi, cg, paral-kgb, reductions]
evidence: [evidence/2026-09-08-abinit-mpi-source-adoption/provenance.md]
---

# ABINIT MPI Distribution Invariants

## Status

Historical guidance under refresh. This is not executable procedure authority and must not be projected or proposed until current ABINIT execution revalidates it.

## Invariants

1. Treat `npwarr(ikpt)` as the local G-vector extent in `paral_kgb=1`.
2. Treat `nband_k` as global when walking physical `cg` storage; never divide it by `nproc_band` to advance `icg`.
3. Complete each G-vector partial sum on `comm_bandspinorfft` before selecting logically owned bands.
4. Apply band ownership only to contribution accumulation; physical `cg` storage and G-vector reduction are not band-sharded by that decision.
5. Reduce the accumulated result over `comm_kpt`, then over `comm_band` whenever multiple band groups contribute.

## Review Questions

- Which communicator spans every rank holding a partial contribution to this value?
- Is a loop extent local storage, global physical layout, or logical ownership?
- Does the reduction happen before any filter that might discard a required partial contribution?
- Does the verification matrix exercise every modified distribution dimension?

## Evidence Boundary

[Historical adoption provenance](../evidence/2026-09-08-abinit-mpi-source-adoption/provenance.md) documents the source topology matrix. It is insufficient for current operational promotion.
