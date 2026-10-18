---
artifact_role: knowledge
audience: both
confidence: 0.75
created: 2026-05-06
last_validated: 2026-05-06T00:00:00
validation_procedure: |
  Inspected TBUpy source files tbupy/hubbard.py, tbupy/density.py, tbupy/model.py,
  and tbupy/analysis.py. Compared the existing full spin-interleaved Hubbard
  boundary against the current spin-separated SCF loop and the reference
  Refs/Refs/electron/Hubbard_4ind.py implementation.
successful_usage_count: 0
usage_stale: false
related_files:
  - TBUpy/tbupy/hubbard.py
  - TBUpy/tbupy/density.py
  - TBUpy/tbupy/model.py
  - TBUpy/tbupy/analysis.py
  - Refs/Refs/electron/Hubbard_4ind.py
related_functions:
  - TBUpyModel.run_scf
  - DensityMatrix.from_eigenvectors
  - HubbardTerm.V_and_E
  - _int_site_4index
tags:
  - hubbard-u
  - non-collinear
  - spinor
project: TBUpy
status: draft
validated_by: automatic
validation_date: 2026-05-06T00:00:00
links_to:
  - notation
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "noncollinear_hubbard_u_design.md display math requires one MathDoc marker per equation"
---

# Non-Collinear Hubbard U Design

## Overview

Non-collinear Hubbard U in TBUpy requires a full spinor density matrix, not only a modification to the Hubbard term formulas. The current public architecture stores the SCF density as `rho[nspin, norb, norb]`, which represents separate collinear up and down density blocks. A non-collinear state needs spin-flip density blocks `rho_{m up, m' down}` and `rho_{m down, m' up}` inside a single spinor matrix.

## Current Behavior

`tbupy.hubbard` already defines the Hubbard boundary as a spin-interleaved matrix ordered `orb0 up, orb0 down, orb1 up, orb1 down, ...`. The site extraction helper preserves any off-diagonal spinor blocks if they are present in the input matrix.

The current SCF path does not produce or preserve those spin-flip blocks. `DensityMatrix` stores only `rho[nspin, norb, norb]`, `to_spin_interleaved()` places the two spin channels into only the up-up and down-down blocks, and `from_spin_interleaved()` discards spin-flip blocks. `TBUpyModel.run_scf()` also diagonalizes `nspin=2` Hamiltonians as separate up and down blocks, so any off-diagonal spin potential would be ignored by the eigenproblem path.

## Formula Implications

The Liechtenstein four-index contraction is the most natural starting point for non-collinear support because it can act on a full local spinor density matrix. The rotationally invariant Hartree-Fock contraction should operate on `rho_site[2*dim, 2*dim]` rather than only on collinear diagonal occupations. The current `_int_site_4index()` includes Hartree from total spin density and Fock from same-spin blocks only, which is sufficient for collinear density but incomplete for spinor exchange fields because it ignores spin-flip density contributions to the exchange potential.

The Dudarev limit can be implemented as a spin-rotationally invariant projector formula on each correlated shell:

$$
E_U = \frac{U_{eff}}{2} \mathrm{Tr}[\rho - \rho^2]
$$

$$
V_U = U_{eff}\left(\frac{1}{2}I - \rho\right)
$$

where `rho` is the full local orbital-spin density matrix. This form naturally creates spin-flip potential terms when the density has spin-flip components.

Double counting needs an explicit choice. The charge-only `FLL-ns` path is spin-rotationally invariant because it depends only on `n_tot = Tr(rho)`, and it should be the default. A spin-dependent `FLL-s` path is basis-axis dependent if it uses only up/down diagonal occupations; non-collinear `FLL-s` should require user-specified input defining the local spin convention before it is accepted.

## Implementation Consequence

The minimal robust feature shape is a new spinor mode that keeps the existing collinear API working unchanged. In spinor mode, TBUpy should store `rho_spinor[2*norb, 2*norb]`, diagonalize the full `2*norb` generalized eigenproblem, compute occupations over one spinor band axis, and mix the full Hermitian spinor density. Collinear mode can continue to use the existing `rho[nspin, norb, norb]` representation. `SCFResult` should become a union-like result with an explicit `spin_mode` field instead of introducing a separate spinor result type.

Spinor Dudarev is the first implementation target because its rotationally invariant formula is compact and easy to validate. Spinor Kanamori and full Liechtenstein should be implemented afterward. Spinor `.tbupy.nc` files should preserve the full spinor Hamiltonian and density so a later TB2J spinor interface can consume them without dropping spin-flip terms.

## Linked Concepts

- [notation](notation.md): Standard symbols for `U`, `J`, `rho`, and spin indices.
