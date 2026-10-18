---
artifact_role: knowledge
audience: both
title: GPAW PAW SOC Matrix Is Not a Replacement Descriptor
id: gpaw_paw_soc_descriptor_limit
date: 2026-08-03
project: siesta_simplex_basis
status: draft
validated_by: source-audit
source_memo: ../specs/research/2026-08-03-gpaw-paw-soc-parameters.md
tags: [gpaw, paw, soc, descriptor, validation]
links_to: [soc_strength_descriptor, gpaw_independent_validation_reference]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "gpaw_paw_soc_descriptor_limit.md display math requires one MathDoc marker per equation"
---

# GPAW PAW SOC matrix is not a replacement descriptor

## Finding

GPAW constructs the PAW on-site Pauli SOC tensor with
`gpaw.spinorbit.soc(setup, xc, D_sp)`. It returns

$$
H^{\mathrm{SO},a}_{v,ij}=\frac{\alpha^2}{4}
\left\langle\phi_i^a\middle|\frac{1}{r}\frac{dU_\mathrm{eff}^a}{dr}L_v\middle|\phi_j^a\right\rangle,
$$

in an all-electron PAW partial-wave basis. The implementation forms only equal-$l$ blocks and
uses an SCF effective potential containing nuclear, Hartree, and normally XC-gradient terms.
`gpaw.spinorbit.soc_eigenstates()` projects that matrix through PAW projectors into a
scalar-relativistic KS basis, adds it to KS eigenvalues, and diagonalizes non-self-consistently.

## Decision

Do **not** substitute the GPAW radial matrix element $\xi_{nl}$ for the project descriptor

$$
\Delta\varepsilon_{nl}=\varepsilon_{nl}^{j=l+1/2}-\varepsilon_{nl}^{j=l-1/2}.
$$

The former is a first-order Pauli matrix element, depends on density/environment and PAW setup,
and is dominated by inner-core all-electron behaviour. The latter is a direct FR
norm-conserving-pseudopotential $j$-channel eigenvalue difference. The two agree only under a
restricted first-order central-potential approximation:
$\Delta\varepsilon\approx(2l+1)\xi$.

This independently reproduces the project's earlier conclusion in [soc_strength_descriptor](soc_strength_descriptor.md):
inner-region SOC matrix elements are not a robust periodic descriptor. GPAW does expose them,
but exposure does not make them comparable or stable.

## Valid use

Use GPAW SOC at the observable level: run matched scalar-relativistic calculations, apply
`gpaw.spinorbit.soc_eigenstates(calc, scale=1.0)`, and compare clearly identified SOC band
splittings at common k-points against SIESTA's SOC calculation. This independently validates
SOC consequences while leaving `pypao.analysis.soc` bare $j$-channel splitting as the atomic
strength descriptor.

## Evidence

- PAW radial operator and equal-$l$ blocks: `/home/hexu/projects/TB2J_PAW/Refs/gpaw/gpaw/spinorbit.py:571-598`.
- Effective-potential derivative: `spinorbit.py:618-656`.
- Projected KS SOC Hamiltonian diagonalization: `spinorbit.py:55-95`, `475-568`.
- GPAW's documented PAW-projector expansion: `doc/tutorialsexercises/electronic/spinorbit/spinorbit.rst:7-53`.
- Full research memo: [2026-08-03-gpaw-paw-soc-parameters](2026-08-03-gpaw-paw-soc-parameters.md).
