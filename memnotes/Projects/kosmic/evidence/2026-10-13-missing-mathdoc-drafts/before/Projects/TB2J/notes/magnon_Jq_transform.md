---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-02-20
last_validated: 2026-10-04T00:00:00
validation_procedure: |
  Code-only update: inspect Magnon.Jq/Hq and run two reference-update
  regressions plus the before/after Gamma matrix smoke. Negative Fourier
  phase and ordering-Q distinction remain unchanged; no new derivation.
project: TB2J
status: stable
validated_by: automatic
tags: [magnon, fourier, q-space]
type: Project Knowledge
---

# Magnon Jq Transform


## Overview

The Jq transform converts real-space exchange tensors **J**(R) to reciprocal-space
**J**(k), where **k** is the magnon Bloch wave vector sampled relative to a
reference magnetic structure. For a single-Q incommensurate reference structure,
the distinct ordering/propagation vector **Q** defines that reference first; its
rotating-frame transformation is applied to each tensor before the k transform.

## Principles

- **Q** is the fixed ordering/propagation vector of the reference magnetic structure.
- **k** is the independently sampled magnon Bloch wave vector (`kpoints` in code).
- Real-space exchange is summed over all lattice vectors R with the negative
  Fourier phase $\exp(-2\pi i\,\mathbf{k}\cdot\mathbf{R})$.
- For a single-Q reference, rotation accounts for the spin spiral before
  calculating its magnon modes.
- Output tensor has the same shape but is evaluated at each **k**.

## Details

### Basic Fourier Transform

The exchange interaction in reciprocal space for a magnon Bloch wave vector
$\mathbf{k}$ is obtained by Fourier transforming the rotated real-space tensors:

$$
\mathbf{J}'_{ij}(\mathbf{k}) =
\sum_{\mathbf{R}} \mathbf{J}'_{ij}(\mathbf{R})
e^{-2\pi i\mathbf{k}\cdot\mathbf{R}}
$$

This sign matches Toth & Lake's $\sum_\mathbf{d}\mathbf{J}(\mathbf{d})
e^{-i\mathbf{k}\cdot\mathbf{d}}$ convention and `Magnon.Jq()`.

### Non-collinear Magnetic Structures

For a single-Q incommensurate reference structure, **Q** is the magnetic
ordering/propagation vector — normally the known or supplied ground-state
ordering vector. It is not the sampled magnon wave vector **k**. Reference
spins rotate between cells around global axis **n**; the corresponding exchange
tensor is rotated before the Fourier transform.

**Terminology:** the *ordering vector*, *propagation vector*, and
*incommensurate wave vector* are names for the same single vector
$\mathbf{Q}$. The optional subscript $\mathrm{ref}$ merely stresses that this
$\mathbf{Q}$ defines the reference magnetic structure; it is not a second
parameter. The only independent reciprocal-space vector in the calculation is
the magnon Bloch vector $\mathbf{k}$.

In TB2J, the loaded magnetic moments (or `--spin-conf`) provide the reference
vectors $\mathbf{S}_{0j}$. The `--uz-file` values are auxiliary local-frame
directions used to construct transverse axes for the Holstein–Primakoff basis;
they do not replace the global spiral rotation axis $\mathbf{n}$.

$$
\mathbf{J}'_{mn}(\mathbf{R}) =
\mathbf{R}_m^\mathsf{T}\mathbf{J}_{mn}(\mathbf{R})\mathbf{R}_n
$$

where:

- $\phi = 2\pi \mathbf{R} \cdot \mathbf{Q}$ is the reference-structure rotation angle.
- $\mathbf{R}(\phi)$ is the rotation matrix around global axis **n**.

In TB2J, $m$ is in the origin cell, so only the right-side rotation survives:

$$
\mathbf{J}'_{mn}(\mathbf{R}) =
\mathbf{J}_{mn}(\mathbf{R}) \cdot \mathbf{R}_{n}(\phi)
$$

The resulting $\mathbf{J}'(\mathbf{k})$ supplies $A(\mathbf{k})$,
$B(\mathbf{k})$, and $C$ for magnons relative to this reference structure.

### Normalization by Spin Magnitude

The exchange is normalized by spin magnitudes before the transform:

$$
\mathbf{J}^{\text{norm}}_{ij} = \frac{\mathbf{J}_{ij}}{S_i S_j}
$$

## Variables

| Symbol | Description | Units |
|--------|-------------|-------|
| **J**(R) | Real-space exchange tensor | eV |
| **J**(k) | Exchange tensor evaluated at magnon Bloch vector k | eV |
| **k** | Magnon Bloch wave vector relative to the reference structure | reciprocal-lattice units |
| **Q** | Incommensurate reference ordering/propagation vector | reciprocal-lattice units |
| **R** | Lattice vector | fractional lattice units in the phase calculation |
| ϕ | Reference-structure rotation angle | radians |
| **n** | Global reference-spiral rotation axis | dimensionless |

## Implementation and mutable references

Magnon.Jq normalizes JR by current Snorm, rotates each real-space tensor
for the reference Q/n, and performs the Fourier sum with the vectorized
phase array and np.einsum("rq,rijxy->qijxy", exp(-1j*phase), JRprime).
The sampled k vectors remain distinct from the ordering Q.

Magnon.Hq recomputes J(q=0) from current state. An unkeyed instance cache
would mix an old diagonal C term with a newly normalized/rotated J(q) after
set_reference(..., magmoms=...), Q/n changes or in-place JR updates. A
moment-doubling chain regression preserves the Gamma Goldstone matrix and
halves finite-q energies; exchange rescaling and Q/axis updates match fresh
models. The former cached implementation produced a nonzero Gamma H norm
8.485281 after the moment update; the fixed norm is6.28e-16.

Fix59c618c removes the cache without changing Fourier/HP conventions.
Tests/tests/test_magnon_reference_updates.py contains two passing regressions.


## Conventions
- `MagnonParameters.Q` is the ordering vector of the reference structure.
- `Magnon.Jq(kpoints)` receives the distinct sampled magnon vectors **k**.
- The CLI must expose these with distinct names: recommend
  `-Q/--ordering-vector` for **Q**, `--rotation-axis` for **n**, and
  `--kpath`/`--qpoints`/`--kmesh` for **k** sampling.
- Q omitted or equal to `[0, 0, 0]` means a commensurate reference and applies
  the identity rotation.
- When `n` is omitted, `Magnon.load_from_io()` and
  `prepare_magnon_from_params()` default to $[1,0,0]$. This is only a
  convenience default; a physical non-collinear reference requires an axis
  selected from the known spin structure.

For commensurate $\mathbf{Q}$, distinguish the mapping direction: folding maps
chemical representatives $\mathbf{k}$ and $\mathbf{k}+\mathbf{Q}$ to one
magnetic-zone point; unfolding that magnetic point produces both chemical-zone
representatives. For G-type order, magnetic $\Gamma$ therefore unfolds to
chemical $\Gamma$ and R$=\mathbf{Q}$.

For the collinear A/B AFM with B obtained by
$\mathcal{R}_{\hat{x}}(\pi)$, a magnetic-$\Gamma$ circular mode has
$\delta S_A^x=\delta S_B^x$ and $\delta S_A^y=-\delta S_B^y$. The uniform
x-component is chemical $\Gamma$; the staggered y-component is chemical
R$=\mathbf Q$. They are time-quadrature components of one normal mode, hence
share one frequency rather than being independent modes.

## Linked Concepts

- [exchange_tensor](exchange_tensor.md): The real-space exchange tensor being transformed
- [magnon_hamiltonian](magnon_hamiltonian.md): How Jq enters the dynamical matrix
- [notation](notation.md): Standard variable notations
