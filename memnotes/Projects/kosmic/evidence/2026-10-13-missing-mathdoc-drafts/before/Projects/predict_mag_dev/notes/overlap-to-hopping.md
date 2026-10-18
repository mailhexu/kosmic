---
type: reference
status: stable
audience: both
artifact_role: knowledge
---

# Overlap-to-hopping for the periodic valence model

---
confidence: 0.9
created: 2026-08-19
last_validated: 2026-08-19
validation_procedure: "Cross-check rotated pair-table overlaps against direct pypao S(R), solve generalized eigenproblems, and verify Hermiticity/conditioning on representative structures."
project: predict_mag_dev
status: validated
validated_by: automatic
sources:
  - "Wolfsberg and Helmholz, DOI 10.1063/1.1700580"
  - "Hoffmann, DOI 10.1063/1.1734456"
  - "Slater and Koster, DOI 10.1103/PhysRev.94.1498"
tags: [tight-binding, overlap, hopping, pao, wolfsberg-helmholtz]
---

## Overview

PredictMag has validated, m-resolved PAO overlaps but no validated two-center Hamiltonian
integrals. The v2 primary hopping rule is therefore the Wolfsberg–Helmholtz conversion
applied to the real PAO overlap, with one bounded global factor fitted inside training
folds.

This choice retains distance and orbital-orientation information already present in the
PAOs while avoiding per-element or per-bond hopping parameters.

## Definition

For two retained valence orbitals, use

$$
H_{\mu\nu} = K_{\rm WH}\,S_{\mu\nu}\,
\frac{\varepsilon^{\rm eff}_{\mu}+\varepsilon^{\rm eff}_{\nu}}{2}.
$$

The periodic nonorthogonal problem is

$$
H(\mathbf k)c = \epsilon\,S(\mathbf k)c.
$$

The same shifted onsite energies used on the Hamiltonian diagonal must be used in the
off-diagonal conversion, preserving internal consistency.

## Principles

- `pypao.overlap.compute_overlap` already provides finite-support
  $S_{\mu\nu}(\mathbf R)$ and $S(\mathbf k)$ with basis provenance, Hermiticity residuals,
  and condition numbers.
- Include every symmetry-allowed block among retained shells: s–s, s–p, s–d, p–p, p–d,
  and d–d. Otherwise the retained metal s electron reservoir cannot transfer into ligand p
  states.
- $K_{\rm WH}$ is global and bounded. The classical extended-Hückel value and the existing
  `bond_model.py` value are initialization references, not transferable constants: they
  use different orbital shapes and overlap definitions.
- The generalized eigenproblem is mandatory. Treating the PAOs as orthogonal after using
  their overlap to construct hopping is inconsistent.
- Ill-conditioned $S(\mathbf k)$ must produce an explicit failure or a predeclared basis
  treatment; never hide it with an unreported diagonal regularizer.

## Alternatives and decision

- Direct kinetic-plus-potential integrals would be more physical but no validated local
  implementation exists; choosing an effective potential would introduce a separate
  research project.
- Slater–Koster/Harrison universal hopping is useful as a magnitude check but discards the
  validated element-specific PAO radial information.
- Scalar analytic overlap, currently used in `bond_model.py`, loses sigma/pi/delta and
  crystal-orientation structure.

Therefore the primary v2 path uses m-resolved PAO overlap plus one Wolfsberg–Helmholtz
factor. Direct integrals and universal scaling are not coequal implementation branches.

## Portable artifacts

The builder may use pypao, but prediction-time code must use saved artifacts. Two forms are
possible:

1. bond-frame element/shell-pair overlap tables versus distance, rotated into the crystal
   frame at runtime;
2. direct per-structure serialized $S(\mathbf R)$ caches.

Architecture must choose the canonical form. If pair tables are selected, their rotated
blocks must be cross-checked against direct pypao results before use.

## Linked concepts

- [[active-space-electron-counting]] — why all retained valence shells need connected
  hopping.
- [[ligand-open-shell-soc-anisotropy]] — ligand-SOC mechanisms enabled by d–p and p–p
  hopping.
- [[mae-descriptor-inventory]] — available PAO and onsite inputs.
- [[notation]] — symbol definitions.
