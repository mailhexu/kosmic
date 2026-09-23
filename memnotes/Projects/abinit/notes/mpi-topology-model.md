---
type: Project Knowledge
title: ABINIT MPI Topology Model
description: Conceptual model of ABINIT communicator and ownership dimensions relevant to MPI CG reductions.
confidence: 0.75
created: '2026-09-08'
updated: '2026-09-08'
validation_procedure: "Confirm communicator membership and ownership mappings against the current MPI_type implementation when using this knowledge in a change."
project: abinit
status: draft
audience: development
artifact_role: knowledge
usage_stale: false
tags: [abinit, mpi, mpi-type, communicators, ownership]
evidence: [evidence/2026-09-08-abinit-mpi-source-adoption/provenance.md]
---

# ABINIT MPI Topology Model

ABINIT separates k-point, band, FFT, and spinor distribution. A value can be physically split over one communicator while its final ownership is partitioned along another dimension. For CG-derived quantities, distinguish:

- `comm_bandspinorfft`: ranks holding complementary G-vector/spinor pieces of one k-point contribution;
- `comm_kpt`: ranks contributing distinct k-points to the global value;
- `comm_band`: ranks owning different logical bands when band parallelism is active.

Communicator selection follows the dimensions that split the partial value, not the loop that happens to consume it. A future implementation procedure must identify those dimensions explicitly and verify the selected communicator against `MPI_type` and `proc_distrb` in the target source revision.

## Evidence Boundary

This is explanatory knowledge distilled from historical provenance. It does not prescribe a current implementation sequence.
