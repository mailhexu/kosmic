---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-05-28
last_validated: 2026-05-28T00:00:00
validation_procedure: |
  Cross-checked a SymPy Holstein-Primakoff expansion for one tensor-coupled spin pair against TB2J `Magnon.Hq()` in `TB2J/magnon/magnon3.py`, the existing `magnon_hamiltonian.md`, `magnon_Jq_transform.md`, and `exchange_tensor.md` notes, plus focused explore/oracle consultations.
validation_test: null
successful_usage_count: 1
last_used_successfully: 2026-05-28T00:00:00
usage_stale: false
related_files:
  - TB2J/magnon/magnon3.py
  - TB2J/magnon/magnon_math.py
  - TB2J/interfaces/sprkkr.py
  - docs/src/sprkkr_magnon.md
related_functions:
  - Magnon.Hq
  - Magnon.Jq
  - get_rotation_arrays
  - sprkkr_to_spinio
tags:
  - magnon
  - exchange_tensor
  - LSWT
  - Jzz
project: TB2J
status: draft
validated_by: automatic
validation_date: 2026-05-28T00:00:00
links_to:
  - magnon_hamiltonian
  - magnon_Jq_transform
  - exchange_tensor
  - sprkkr_magnon_implementation
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "jzz_magnon_energy_report.md display math requires one MathDoc marker per equation"
---

# Effect of $J_{zz}$ on Magnon Energies for $z$-Aligned Spins

## Summary

For a pair of spins coupled by a full exchange tensor $J_{ij}^{ab}$, with both spins aligned along $z$, the longitudinal tensor entry $J_{ij}^{zz}$ does affect harmonic magnon energies. It contributes to diagonal onsite number terms in the linear spin-wave Hamiltonian. It does not create intersite magnon hopping or anomalous pairing by itself; those terms come from the transverse block $J_{xx}$, $J_{xy}$, $J_{yx}$, and $J_{yy}$.

In TB2J's `Magnon.Hq()` implementation this appears as the diagonal $C$ term, where the longitudinal local-axis vector $V$ projects the exchange tensor as $V_i^T J_{ij}(0) V_j$. For spins along $z$, this projection selects $J_{zz}$.

## Pair Derivation

Use the pair Hamiltonian convention

$$
H_{ij} = -\mathbf{S}_i^T J_{ij} \mathbf{S}_j
= -\sum_{a,b=x,y,z} S_i^a J_{ij}^{ab} S_j^b .
$$

For a ferromagnetic reference state along $+z$, the Holstein-Primakoff expansion to harmonic order is

$$
S_i^z = S - a_i^\dagger a_i,
$$

$$
S_i^x = \sqrt{\frac{S}{2}}(a_i + a_i^\dagger),
$$

$$
S_i^y = -i\sqrt{\frac{S}{2}}(a_i - a_i^\dagger),
$$

and similarly for site $j$.

The $zz$ contribution is

$$
H_{ij}^{zz} = -J_{ij}^{zz} S_i^z S_j^z
= -J_{ij}^{zz}(S - n_i)(S - n_j),
$$

with $n_i=a_i^\dagger a_i$. Expanding gives

$$
H_{ij}^{zz}
= -S^2 J_{ij}^{zz}
+ S J_{ij}^{zz}(n_i+n_j)
- J_{ij}^{zz} n_i n_j .
$$

At linear spin-wave level the quartic term is dropped, so

$$
\boxed{H_{ij}^{zz,(2)} = S J_{ij}^{zz}(a_i^\dagger a_i+a_j^\dagger a_j).}
$$

Thus $J_{zz}$ changes the diagonal harmonic energy for sites $i$ and $j$.

The mixed longitudinal-transverse components produce linear terms around a $z$-axis reference state:

$$
H_{ij}^{\mathrm{mix},(1)}
= -S\sqrt{\frac{S}{2}}
\left[
J_{ij}^{xz}(a_i+a_i^\dagger)
- iJ_{ij}^{yz}(a_i-a_i^\dagger)
+ J_{ij}^{zx}(a_j+a_j^\dagger)
- iJ_{ij}^{zy}(a_j-a_j^\dagger)
\right].
$$

These terms vanish only when the chosen collinear reference state is torque-free after summing all neighbors, or when constraining fields cancel the torque.

The transverse block produces the intersite quadratic hopping and pairing terms:

$$
H_{ij}^{\perp,(2)}
= -\sum_{\mu,\nu=x,y}J_{ij}^{\mu\nu}S_i^\mu S_j^\nu.
$$

In explicit bosonic form, the normal and anomalous terms are combinations of $J_{xx}$, $J_{xy}$, $J_{yx}$, and $J_{yy}$ only. Therefore $J_{zz}$ affects the onsite diagonal part, while the transverse block controls the intersite magnon hopping/pairing structure.

## Lattice Interpretation

For a lattice Hamiltonian

$$
H = -\frac{1}{2}\sum_{ij}\mathbf{S}_i^T J_{ij}\mathbf{S}_j,
$$

the classical longitudinal field at site $i$ for collinear $z$ spins is

$$
B_i^z = S\sum_j J_{ij}^{zz}.
$$

Since a spin fluctuation reduces $S_i^z$ by $n_i$, this longitudinal field creates a diagonal harmonic term proportional to

$$
S\sum_i n_i\sum_j J_{ij}^{zz},
$$

up to the sign and factor conventions used for pair counting.

For an isotropic Heisenberg tensor $J_{ij}^{ab}=J_{ij}\delta_{ab}$, the usual ferromagnetic result has the structure

$$
\omega(\mathbf{k}) \propto S\left[J(\mathbf{0}) - J(\mathbf{k})\right].
$$

Here $J_{zz}$ supplies the $J(\mathbf{0})$ diagonal contribution and the transverse block supplies the $J(\mathbf{k})$ hopping contribution. Dropping $J_{zz}$ would generally give incorrect energies and can spoil the Goldstone cancellation at $\mathbf{k}=0$.

## TB2J Implementation Cross-Check

TB2J's current `Magnon.Hq()` builds the harmonic Hamiltonian from full exchange tensors. It computes the local transverse vector $U$ and longitudinal vector $V$, then forms the blocks

$$
A(q) \sim U^T J(q) U^*,
$$

$$
B(q) \sim U^T J(q) U,
$$

and

$$
C_i = 2\sum_l V_i^T J_{il}(0) V_l S_l.
$$

For spins along $z$,

$$
U = (1, i, 0), \qquad V=(0,0,1),
$$

up to the handedness convention for down spins. Therefore:

- $J_{xx}$, $J_{xy}$, $J_{yx}$, and $J_{yy}$ enter the transverse $A$ and $B$ blocks.
- $J_{zz}$ enters the diagonal $C$ block.
- $J_{xz}$, $J_{yz}$, $J_{zx}$, and $J_{zy}$ do not enter the strict harmonic matrix for a torque-free $z$-axis collinear state, but they signal linear torque terms if the reference state is not stationary.

## Consequences for SPRKKR Tensor Policies

For SPRKKR inputs that only provide $J_{xx}$, $J_{yy}$, $J_{xy}$, and $J_{yx}$:

- `transverse-block` sets all unavailable entries, including $J_{zz}$, to zero. This removes the longitudinal diagonal contribution from the tensor part.
- `transverse-block-jzz` keeps the transverse block and sets

$$
J_{zz}=\frac{J_{xx}+J_{yy}}{2}.
$$

This restores the longitudinal diagonal contribution under the assumption that the missing longitudinal coupling is comparable to the average transverse diagonal coupling.
- `isotropic` collapses the interaction to a scalar exchange using $(J_{xx}+J_{yy})/2$, so the same scalar appears in transverse and longitudinal channels.

The safest wording is: $J_{zz}$ is not irrelevant to magnon energies; it is irrelevant only to transverse hopping/pairing terms. It remains relevant to the onsite diagonal part of the LSWT Hamiltonian.

## Linked Concepts

- [magnon_hamiltonian](magnon_hamiltonian.md)
- [magnon_Jq_transform](magnon_Jq_transform.md)
- [exchange_tensor](exchange_tensor.md)
- [sprkkr_magnon_implementation](sprkkr_magnon_implementation.md)
