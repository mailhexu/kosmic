---
type: Project Knowledge
title: Historical ABINIT MPI CG-Reduction Validation
description: Dated record of a legacy topology-matrix validation for CG-derived reductions.
confidence: 0.97
created: '2026-09-08'
updated: '2026-09-08'
validation_procedure: "Supersede with a current execution Evidence Pack before using this material to support a procedure proposal."
project: abinit
status: draft
audience: development
artifact_role: evidence
usage_stale: false
tags: [abinit, mpi, cg, historical-validation, paral-kgb]
evidence: [evidence/2026-09-08-abinit-mpi-source-adoption/provenance.md]
---

# Historical ABINIT MPI CG-Reduction Validation

The migrated source reports agreement below `5e-6 Ha` for a NiO NC DFT+U CG-derived observable across classic k-point parallelism and band-FFT topologies spanning k-point, band, and FFT dimensions.

The historical diagnosis identified five failure modes: omitted `comm_bandspinorfft` reduction; treating local `npwarr` as global; shrinking global `nband_k` in the CG offset; omitting logical band ownership; and omitting final `comm_band` reduction.

## Limitation

This record is dated historical evidence. It is not current execution evidence, does not satisfy the two-sided admission rule, and cannot seed a Shared Domain Library proposal. It exists to preserve provenance and define the future revalidation target.

## Source

[Historical adoption provenance](../evidence/2026-09-08-abinit-mpi-source-adoption/provenance.md).
