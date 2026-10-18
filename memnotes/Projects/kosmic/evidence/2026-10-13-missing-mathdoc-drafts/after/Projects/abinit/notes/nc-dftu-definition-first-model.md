---
artifact_role: knowledge
audience: both
status: draft
created: 2026-08-11
updated: 2026-08-11
project: abinit
tags: [nc-pao, dftu, sympy, domain-model]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "nc-dftu-definition-first-model.md display math requires one MathDoc marker per equation"
---

# NC PAO DFT+U definition-first model

## Decision

The next foundational symbolic derivation starts from periodic Kohn--Sham spinors, zero-temperature insulating weights, normalized translation-covariant site-local orthonormal PAOs, and an effective local Hermitian screened kernel. It does not derive norm-conserving pseudopotential generation, PAO radial construction, or screening generation.

The primary correlated-subspace label is the combined orbital-spin index $a=(m,s)$. The full interaction is an antisymmetrized Hartree--Fock functional built from a Slater-integral four-index orbital tensor and a Hermitian spinor occupation matrix. FLL, AMF, alternative AMF, and Dudarev are separate double-counting/reduction branches.

## Response model

A shared Hermitian-directional variation derives

$$
\delta n \rightarrow \delta V \rightarrow \delta H \rightarrow \delta E,
$$

with $H_U=\Phi V_U\Phi^\dagger$. Atomic displacement, DDK, fixed-PAO electric field, homogeneous symmetric strain, and explicit finite-$q$ q/$-q$ pairing are specializations. Metallic response and finite-$q$ q-star reconstruction are explicit boundaries.

## Evidence model

Every result must carry independent formal, source, and runtime status. The deliverable is a dedicated executable foundation module plus a self-contained report; the current audit remains its implementation-evidence companion. Exact SymPy identities and targeted defect mutants validate algebra only and must not be presented as ABINIT numerical equivalence or as `nspinor=2` DFPT support.

## Related

- [nc-dftu-derivation-audit](nc-dftu-derivation-audit.md)
- [notation](notation.md)
- `papers/DFTU_NC/CONTEXT.md`
