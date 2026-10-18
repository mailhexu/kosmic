---
type: reference
status: draft
audience: both
artifact_role: knowledge
math_provenance: missing
math_provenance_reason: "active-space-electron-counting.md display math requires one MathDoc marker per equation"
---

# Active-space electron counting for periodic PredictMag v2

---
confidence: 0.95
created: 2026-08-19
last_validated: 2026-08-19
validation_procedure: "Sum non-semicore element-table occupations for every unit cell; verify capacity bounds, charge neutrality, generalized-eigen filling, and FeBr2 count 18."
project: predict_mag_dev
status: validated
validated_by: automatic
tags: [electron-counting, active-space, pao, ligand-hole, tight-binding]
---

## Overview

The periodic v2 model must conserve all transferable valence electrons. A basis containing
only metal d and ligand p orbitals is not sufficient because nominal metal s electrons can
transfer into metal d or ligand p states. The primary basis is therefore every
non-semicore valence PAO shell in `element_descriptors.yaml`; SOC analysis remains focused
on metal d and ligand p.

## Counterexample: FeBr2

A neutral d+p-only count gives Fe 3d6 plus two Br 4p5 shells, or 16 electrons. The expected
ionic/covalent active occupation is Fe d6 plus two Br p6 shells, or 18 electrons. The two
missing electrons originate from Fe 4s. Removing that orbital and its electrons before
filling makes a ligand p hole unavoidable for bookkeeping reasons rather than physics.

Retaining Fe 4s alongside Fe 3d and Br 4p gives the correct 18-electron valence manifold.
The common Fermi level then decides whether the electron weight is metal-s, metal-d, or
ligand-p character.

## Exact count

For the retained non-semicore valence basis,

$$
N_{\rm cell} = \sum_{i\in\mathrm{cell}}
\sum_{nl\,\notin\,\mathrm{semicore}} \mathrm{occ}_{nl}(i).
$$

This is a stoichiometric invariant. QEq and formal charges may shift onsite energies and
thereby redistribute the electrons, but they must not create or remove electrons from the
neutral cell.

## Occupations and ligand holes

One Fermi level fills the periodic generalized eigenstates. Orbital populations are then
projected back onto the nonorthogonal PAO basis with a Mulliken population analysis. For a
ligand p shell, the reported hole population is $h_p=6-n_p$.

A nonzero $h_p$ is therefore an output of hybridization, level alignment, and filling—not an
input forced from formal oxidation. Required ablations are forced-p6 filling, d+p-only
counting, and formal-charge versus QEq onsite shifts.

## Coverage and size

Measured over the 341 reference CIFs, the complete non-semicore basis has:

- 28 spatial orbitals at the median;
- 76 at the 95th percentile;
- 236 at the maximum;
- spin-Hamiltonian dimensions 56 at the median and 472 at the maximum;
- zero elements without the required saved PAO data.

The basis is therefore computationally plausible, subject to a declared k-mesh policy and
an explicit runtime rule for the largest cells.

## Conventions

- Keep every retained shell's saved occupation, energy, PAO provenance, and semicore flag.
- Include all hopping blocks among retained shells; otherwise the electron reservoir is
  disconnected.
- Use charge models only for level shifts and ablations.
- Count each periodic unit-cell orbital once; do not distribute shared-ligand electrons
  among overlapping metal clusters.
- Report overlap conditioning and ambiguous Fermi-level filling explicitly.

## Linked concepts

- [[overlap-to-hopping]] — periodic nonorthogonal Hamiltonian construction.
- [[ligand-open-shell-soc-anisotropy]] — interpretation of ligand p-hole populations.
- [[bond-descriptor-physics]] — formal and covalent charge-transfer estimates used as
  onsite-shift alternatives.
- [[mae-status-and-roadmap]] — project decision sequence.
- [[notation]] — shared symbols.
