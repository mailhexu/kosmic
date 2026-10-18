---
artifact_role: knowledge
type: Project Knowledge
title: ASE Consumer Interface
description: Supported consumer workflow for exchange and MCA calculations through ASE calculators.
confidence: 0.9
created: 2026-09-20
updated: 2026-09-20
validation_procedure: Run a backend calculation from an ASE Atoms object and collect its exchange or MCA summary.
project: fourstate
status: draft
audience: usage
usage_stale: false
evidence: []
math_provenance: missing
math_provenance_reason: "ase_consumer_interface.md display math requires one MathDoc marker per equation"
---
# ASE Consumer Interface

`fourstate` is consumed through ASE. A caller supplies an `ase.Atoms` structure, selects a supported calculator backend, and invokes the exchange or MCA workflow. Results are ordinary energy-derived summaries rather than backend-specific output parsing requirements.

## Supported workflow

1. Prepare an `ase.Atoms` object with species, cell, coordinates, and initial magnetic moments.
2. Construct a supported backend calculator with the DFT executable, pseudopotentials, and convergence settings.
3. Run the exchange workflow for the selected magnetic sites or the MCA workflow for selected spin directions.
4. Read the emitted result summary. Exchange uses the convention below; MCA reports a total-energy difference and per-magnetic-atom value.

## Exchange convention

For the N+2 four-state path, the consumer receives $J_nS^2$ from the reference, one-flip, and neighbour-specific two-flip energies:

$$
J_nS^2 = \frac{E_{\mathrm{ref}} + E_{\mathrm{2flip},n} - 2E_{\mathrm{1flip}}}{4}.
$$

The reported $J_n$ is $J_nS^2/S^2$, with the package convention $H=-2\sum_n J_n\,\mathbf S_i\cdot\mathbf S_j$.

## Consumer requirements

- The chosen DFT backend, pseudopotentials, XC functional, cell, k-point grid, and cutoffs must be held fixed across every magnetic configuration compared.
- A primitive-cell two-site run is a workflow check only. Use a sufficient supercell to isolate physical neighbour shells for production exchange parameters.
- A result is usable only when every participating DFT state converges; missing or unconverged states must not be replaced with zero energy.
