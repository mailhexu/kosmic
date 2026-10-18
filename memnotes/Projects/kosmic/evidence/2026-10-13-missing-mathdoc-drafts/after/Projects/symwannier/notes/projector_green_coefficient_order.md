---
artifact_role: knowledge
type: reference
audience: both
title: Projector Green coefficient bra-ket order
project: symwannier
status: draft
created: 2026-08-05
last_validated: 2026-08-05
validated_by: BiFeO3 direct full-BZ exchange regression
tags: [tb2j, projector-green, abinit, symmetry, bifeo3]
math_provenance: missing
math_provenance_reason: "projector_green_coefficient_order.md display math requires one MathDoc marker per equation"
---

# Projector Green Coefficient Bra-Ket Order

The committed `TB2J-GPAW` Green kernel expects the projector coefficient
$C_{np}=\langle\phi_p|\psi_n\rangle$ and assembles

$$
G_{pq}(z) = \sum_n C_{np} (z-\epsilon_n)^{-1} C_{nq}^*.
$$

Commit `b982c85` corrected this convention in the shared Green kernel and its
PAW/GPAW regression tests.

ABINIT NC-PAO `PAO_HS.nc` explicitly stores the opposite convention,
$\langle\psi_n|\phi_p\rangle$, as documented in `abinao.pao_hs_io`. The
current ABINIT loader returns those values unchanged, so applying the shared
kernel convention directly reproduces the BiFeO3 split: -1.853/-0.832 meV.
The ABINIT loader must conjugate or otherwise normalize its coefficients at
the interface while keeping population contractions consistent with that
chosen representation.

This is the same interface-class problem fixed for GPAW in `b982c85`: one
shared Green kernel requires one coefficient convention. The ABINIT fix must
be localized to `_load_abinit_nc_pao_hs_v2`: conjugate decoded
`coefficients_ibz` and `coefficients_bz` to recover
$\langle\phi_p|\psi_n\rangle$. Its ABINIT-specific population contractions
must then change from `coeff.conj(), coeff` to `coeff, coeff.conj()` so they
continue to form the same density matrix.

## Linked Concepts

- [[green-function-conventions]]: Covariant and contravariant PAO Green matrices.
- [[abinao_ibz_to_bz_symmetry]]: PAO coefficient and basis-transform convention.
