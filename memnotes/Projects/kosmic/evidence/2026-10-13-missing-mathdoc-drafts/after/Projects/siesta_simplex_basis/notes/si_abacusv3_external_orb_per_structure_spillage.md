---
artifact_role: knowledge
audience: both
confidence: 0.95
created: 2026-08-13
last_validated: 2026-08-13
validation_procedure: "Rescore every basis against identical four canonical Si PBE ABINIT WFKs for occupation-weighted wavefunction spillage, then reconstruct the cascade's kinetic-spillage scalar for the same imported orbital subspaces."
project: siesta_simplex_basis
status: draft
validated_by: automatic
tags: [ABINIT, abinao, spillage, ABACUS, SIAB, silicon]
related_files: ["Results/benchmarks/Si/abacusv3/Si.abacusv3_rc10.ion.nc", "Refs/ABACUS-CSW-NAO/SIAB/spillage/testfiles/Si_gga_10au_20Ry_1s1p.orb", "Refs/ABACUS-CSW-NAO/SIAB/spillage/testfiles/Si/jy-7au/jy_reduced_7au_100Ry_21s20p20d.orb", ".tmp/autoresearch/abacusv3-external-orb-si/per-structure-spillage.json", ".tmp/autoresearch/abacusv3-external-orb-si/kinetic-objective-diagnosis.json"]
related_functions: ["abinao.validate.run_validation", "abinao.ContractionSpillage.kinetic_value_and_gradient"]
links_to: [abacusv3_siab_bessel_cascade]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "si_abacusv3_external_orb_per_structure_spillage.md display math requires one MathDoc marker per equation"
---

# Si ABACUS v3 and external-orbital per-structure spillage


## Overview

The selected Si `abacusv3` NetCDF basis and two external ABACUS `.orb` bases have been rescored separately for the canonical monomer and three-dimer WFK references. This establishes a geometry-resolved common metric; it is not the kinetic-spillage objective that selected the Bessel cascade.

## Basis and metric

The selected basis is `Si.abacusv3_rc10.ion.nc`, with 12 projectors per Si atom ($1s\,2p\,1d$). The compact external file has four projectors per atom ($1s\,1p$, 10 Bohr). The large external file has 181 projectors per atom ($21s\,20p\,20d$, 7 Bohr).

For a WFK state $\psi_{n\mathbf{k}}$, the reported score is occupation-weighted wavefunction spillage:

$$
\mathcal{S} = 1 - \frac{\sum_{n\mathbf{k}} w_{n\mathbf{k}}\langle\psi_{n\mathbf{k}}|P_\Phi|\psi_{n\mathbf{k}}\rangle}{\sum_{n\mathbf{k}} w_{n\mathbf{k}}}.
$$

All rows use one 50 Ha PBE scalar-relativistic Gamma WFK, bands 1-8, and simultaneous projection over every atom in the structure.

## Results

| Structure | `abacusv3` 12/projectors | External 1s1p, 4/projectors | External 21s20p20d, 181/projectors |
|---|---:|---:|---:|
| Monomer | 0.01049770 | 0.00534998 | 0.00538182 |
| Si2, 3.40 Bohr | 0.00952877 | 0.00561891 | 0.00539078 |
| Si2, 5.29 Bohr | 0.00890479 | 0.00437200 | 0.00436655 |
| Si2, 7.18 Bohr | 0.01081588 | 0.00530640 | 0.00321151 |

## Diagnosed cause

The result is a metric reversal. `abacusv3` selects its Bessel contractions by kinetic spillage; the first comparison used occupation-weighted wavefunction spillage. The latter rewards the external compact 1s1p subspace, but the cascade metric ranks the selected `abacusv3` basis first at every structure:

| Basis | Mean kinetic spillage |
|---|---:|
| `abacusv3` 1s2p1d | **0.00625818** |
| External 1s1p | 0.01916884 |
| External 21s20p20d | 0.10177087 |

The selected pre-export cascade score is 0.00645788; reading the serialized 500-point `.ion.nc` changes it by only -3.09%. That small, favorable difference rules out NetCDF serialization as the source of the wavefunction-metric reversal.

The `abacusv3` plus external-1s1p union gives wavefunction spillages from 0.000589 to 0.001051. Hence both inputs are valid but complementary radial subspaces; extra Bessel zetas do not make the generated basis a superset of the external one.

The two 10-Bohr bases are not otherwise the same generation problem. The external artifact declares 20 Ry, whereas the cascade uses 50-Ha reduced-Bessel primitives and its ABINIT kinetic objective.

## Metric tradeoff

Ordinary spillage measures the omitted $L^2$ wavefunction norm:

$$
\mathcal{S}_\psi =
1-\frac{\sum_i w_i\langle\psi_i|P_\Phi|\psi_i\rangle}{\sum_i w_i}.
$$

It is bounded, representation-invariant for the same PAO subspace, and monotone when that subspace is enlarged. In the current validation path it uses occupations, so it primarily measures valence-state completeness. It does not penalize a small-amplitude but high-kinetic-energy residual.

Kinetic spillage measures the residual in the kinetic quadratic form:

$$
\mathcal{S}_T =
\frac{\sum_i w_i\langle(I-P_\Phi)\psi_i|T|(I-P_\Phi)\psi_i\rangle}
{\sum_i w_i\langle\psi_i|T|\psi_i\rangle}.
$$

It emphasizes short-range and high-$G$ accuracy, which is valuable for transferable radial PAOs and is differentiable for the Bessel-contraction optimizer. In the cascade it also softly weights conduction states. Its disadvantages are reference-cutoff and weighting dependence, weaker direct interpretability, and lack of a general monotonicity guarantee when $P_\Phi$ is the ordinary overlap-metric projector rather than a $T$-orthogonal projector.

Neither score is a bulk or total-energy observable. Report both per structure and use SIESTA energy or delta validation as an independent transferability check.

## Linked Concepts

- [abacusv3_siab_bessel_cascade](abacusv3_siab_bessel_cascade.md): Defines the reference set and the distinct cascade selection objective.
- [notation](notation.md): Defines project-wide distance and basis terminology.
