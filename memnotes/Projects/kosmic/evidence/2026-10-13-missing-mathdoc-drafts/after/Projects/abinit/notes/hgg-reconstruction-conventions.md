---
artifact_role: knowledge
audience: both
type: note
status: draft
created: 2026-10-03
last_validated: 2026-10-03
stale_after: 2027-10-03
tags: [abinit, hgg, nonlocal, spinor, conventions]
project: abinit
math_provenance: missing
math_provenance_reason: "hgg-reconstruction-conventions.md display math requires one MathDoc marker per equation"
---

# HGG nonlocal reconstruction conventions (spinor / SOC)

Conventions needed to re-apply the exported factored Kohn–Sham Hamiltonian (`prtham`)
outside ABINIT, learned implementing story 604 (spinor export).

## Basis ordering for spinor

For `nspinor 2` the packed basis is $(G, s)$ with **spinor as the slow index**:

$$
\mathrm{index} = i_G + n_{pw}\,(s-1)
$$

This is the flat index used by `m_getghc`, and it matches the GPU gather in `m_fft`
(`ig = ipw + npw*offset`, `offset = (idat-1)*nspinor + (ispinor-1)`). A spinor operator is
therefore $2 n_{pw}$ square in $(G,s)$, with the spinor blocks contiguous.

## The nonlocal amplitude

The KB/SOC coupling is assembled in **projector space**, not per-G. In `m_opernla_ylm`
(and `m_opernlc_ylm_allwf`):

```fortran
gxfac_(1,ilmn,ia,1) -= ekb_so*ls_uu_im*gx(2,jlmn,ia,1)
```

So `gxfac(i)` accumulates $A_{ij}\,gx(j)$, with $A^{ss'}_{ij}$ built from the real-Ylm
$L\!\cdot\!S$ matrices in `ls_ylm(ls_mat, lmax)`. `ls_ylm` depends only on $l$, so $A$ is
**G-independent** and the operator stays separable:

$$
\langle Gs|V|G's'\rangle = \sum_a \sum_{ij} \beta_i(G)\,A^{ss'}_{ij}\,\overline{\beta_j(G')}
$$

## `indlmn` row meanings (this is the trap)

| Row | 0-based index | Meaning |
|-----|---------------|---------|
| 1 | 0 | $l$ |
| 4 | 3 | magnetic quantum number $m$ |
| 5 | 4 | **radial index** into `ekb` |
| 6 | 5 | channel flag: 1 = scalar, 2 = spin-orbit |

Reading row 4 instead of row 5 as the radial index yields a plausible-looking `ekb` vector
and silently contaminates every downstream reconstruction. Related note identifier: `hgg-eigenvalue-certificate-python-reader` (not present in the current Project bundle).

## Structural identities the SOC blocks satisfy

For a correct export:

- $A^{dd} = -A^{uu}$ exactly (the spinor blocks are anti-Hermitian in spin, as $L\!\cdot\!S$ requires)
- $\operatorname{Re}\operatorname{diag} A^{uu} = 0$ (only the imaginary part contributes)
- $A^{du} = -\overline{A^{ud}}$ — note this is **anti**-conjugate, not conjugate

These are cheap, convention-independent checks that validate an export without knowing the
application convention.

## Why the collinear path cannot calibrate a spinor convention

For collinear runs the amplitude is a real diagonal, so $A$ and $A^T$ are indistinguishable.
Any change to the projector-space contraction is therefore invisible to the collinear
fixtures (which certify at $\sim10^{-15}$ Ha) and must be checked against spinor data.