---
type: Project Knowledge
title: ABINIT FFT Distribution Model
description: Conceptual model of local G-vector and FFT-plane storage relevant to CG reductions in band-FFT parallelization.
confidence: 0.75
created: '2026-09-08'
updated: '2026-09-08'
validation_procedure: "Inspect current wavefunction and FFT distribution code for the target path before relying on this model."
project: abinit
status: draft
audience: development
artifact_role: knowledge
usage_stale: false
tags: [abinit, mpi, fft, g-vectors, cg]
evidence: [evidence/2026-09-08-abinit-mpi-source-adoption/provenance.md]
---

# ABINIT FFT Distribution Model

In `paral_kgb=1`, the `cg` representation used by a rank can contain only its local G-vector segment. An inner product accumulated over `ipw = 1..npwarr(ikpt)` is consequently partial even when the band loop visits every global band. The local extent is correct for addressing local storage and for the `icg` stride; it is not evidence that the mathematical G-vector sum is complete.

This distinction explains why the G-vector communicator must reduce a projection before logical band ownership filtering. Any change that touches `fourwf`, `fourdp`, local FFT planes, or CG offsets must check the actual distribution path in the source revision.

## Evidence Boundary

This is historical explanatory knowledge, not current executable guidance.
