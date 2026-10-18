---
artifact_role: knowledge
confidence: 0.9
created: 2026-08-13
last_validated: 2026-08-13
validation_procedure: "Apply these feasibility gates to pypao-generated PAOs, then evaluate ordinary and kinetic spillage across the canonical WFK set and confirm with SIESTA periodic validation."
project: siesta_simplex_basis
status: draft
audience: both
usage_stale: false
validated_by: automatic
tags: [PAO, basis, constraints, spillage, SIESTA]
links_to: [abacusv3_siab_bessel_cascade, si_abacusv3_external_orb_per_structure_spillage]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "pao_basis_acceptance_constraints.md display math requires one MathDoc marker per equation"
---

# PAO Basis Acceptance Constraints


## Overview

A good PAO basis is not defined by one optimized scalar. Hard constraints prevent an invalid or numerically unstable basis; soft objectives rank feasible candidates; independent periodic calculations establish physical usefulness.

## Hard feasibility constraints

- **Pseudopotential identity:** element symbol, atomic number, valence charge, exchange-correlation functional, relativity treatment, and projector data must agree with the WFK reference semantically. A filename is not evidence of identity.
- **Declared cardinality:** include every occupied valence angular channel and the prescribed polarization channels without duplicate or omitted shells.
- **Radial validity:** each radial function is finite, normalized in the common reduced-radial convention, regular at the origin, and smoothly reaches zero at its finite cutoff.
- **Atomic linear independence:** radial zetas in a common angular channel have a nonsingular atomic overlap matrix.
- **Structure-level conditioning:** the full multi-atom overlap matrix is positive definite with a calibrated conditioning margin at every training and held-out geometry. The 16-projector Si diagnostic union has a minimum eigenvalue near $3\times10^{-4}$ and is a known example that requires pruning or regularization.
- **Finite-support budget:** cutoff radii and basis size obey the explicit efficiency budget.

## Quality objectives

For every reference structure, report both ordinary and kinetic spillage:

$$
\mathcal S_\psi = 1-\frac{\sum_iw_i\langle\psi_i|P_\Phi|\psi_i\rangle}{\sum_iw_i},
\qquad
\mathcal S_T=\frac{\sum_iw_i\langle r_i|T|r_i\rangle}{\sum_iw_i\langle\psi_i|T|\psi_i\rangle}.
$$

Neither has universal priority. A candidate should be selected from a Pareto set that also includes overlap conditioning, projector count, and cutoff volume.

## Transferability acceptance

A training-set optimum is accepted only after it retains quality for held-out bond lengths, volumes, spin states, or charge states relevant to the intended use. Final acceptance uses SIESTA observables: converged energy differences, forces where relevant, and periodic EOS/delta validation. A low projection metric alone is not physical validation.

## Linked Concepts

- [abacusv3_siab_bessel_cascade](abacusv3_siab_bessel_cascade.md): The current reduced-Bessel cascade and its frozen-subspace optimization.
- [si_abacusv3_external_orb_per_structure_spillage](si_abacusv3_external_orb_per_structure_spillage.md): Demonstrates why ordinary spillage, kinetic spillage, and conditioning must be assessed together.
- [notation](notation.md): Project-wide notation and units.
