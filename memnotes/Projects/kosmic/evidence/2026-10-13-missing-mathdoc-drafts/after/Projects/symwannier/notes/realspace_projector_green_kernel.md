---
type: reference
status: draft
audience: both
artifact_role: knowledge
math_provenance: missing
math_provenance_reason: "realspace_projector_green_kernel.md display math requires one MathDoc marker per equation"
---

# Real-Space Projector Green Kernel

---
confidence: 0.9
created: 2026-08-01
last_validated: 2026-08-01
validation_procedure: "SymPy expansion of the two-plane-wave, two-band projector identity and LaTeX compilation of the TB2J projector manuscript."
project: symwannier
status: validated
validated_by: automatic
tags: [green-function, projector, plane-wave, vxc]
---

## Overview
The plane-wave Green-function kernel can be projected into PAOs or geometric regions directly in real space. This is algebraically identical to forming local overlaps with Kohn--Sham states before the spectral Green-function sum.

## Equations
For normalized k-point weights $w_{\mathbf k}$, the kernel is

$$
g_\sigma(\mathbf r,\mathbf r';E)=
\sum_{\mathbf k n}w_{\mathbf k}
\frac{\psi_{n\mathbf k\sigma}(\mathbf r)\psi^*_{n\mathbf k\sigma}(\mathbf r')}
{E+E_F-\epsilon_{n\mathbf k\sigma}}.
$$

For local functions $w^a_\alpha$, the covariant projected Green matrix is

$$
G^{\mathrm{cov}}_{a\alpha,b\beta,\sigma}(E)=
\int d^3r\,d^3r'\,w^{a*}_\alpha(\mathbf r)
g_\sigma(\mathbf r,\mathbf r';E)w^b_\beta(\mathbf r').
$$

Inserting the spectral kernel gives $G^{\mathrm{cov}}=\sum_{\mathbf k n}w_{\mathbf k}p_{n\mathbf k}^{a\alpha}p_{n\mathbf k}^{b\beta*}/(E+E_F-\epsilon_{n\mathbf k})$, where $p_{n\mathbf k}^{a\alpha}=\langle w^a_\alpha|\psi_{n\mathbf k}\rangle$. A plane-wave Fourier transform evaluates this overlap as a contraction of reciprocal-space local functions with wavefunction coefficients.

The local exchange-correlation splitting uses the same functions:

$$
\Delta^a_{\alpha\beta}=
\int d^3r\,w^{a*}_\alpha(\mathbf r)
[V_{\mathrm{xc},\uparrow}(\mathbf r)-V_{\mathrm{xc},\downarrow}(\mathbf r)]
w^a_\beta(\mathbf r).
$$

## Consequences
- A normalized spherical window is a geometric local projector; PAOs are recovered by using lattice-summed PAO functions.
- Overlapping windows or PAOs require their overlap metric and the same covariant-to-dual Green transformation as [[green-function-conventions]].
- A sphere-window trace is a distinct local-subspace definition, not automatically equivalent to a PAO or PAW trace.

## Linked Concepts
- [[delta_xc_realspace_lattice_sum]]: lattice-summed PAO projection of the real-space VXC field.
- [[green-function-conventions]]: nonorthogonal metric and dual Green matrices.
