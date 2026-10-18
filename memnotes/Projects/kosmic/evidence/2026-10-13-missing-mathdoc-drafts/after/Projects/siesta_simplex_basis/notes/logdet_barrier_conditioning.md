---
artifact_role: knowledge
type: Project Knowledge
title: Log-Det Barrier Conditioning Experiment
status: draft
audience: development
usage_stale: false
project: siesta_simplex_basis
created: 2026-08-28
updated: 2026-08-28
confidence: 0.95
validation_procedure: "Finite-difference check of the analytic barrier gradient for one- and two-atom contractions; Ge Gamma-point bulk E-V plus atom fit at mu=1e-4 and 1e-3."
tags: [spillage, overlap, conditioning, logdet, bessel]
math_provenance: missing
math_provenance_reason: "logdet_barrier_conditioning.md display math requires one MathDoc marker per equation"
---

# Log-Det Barrier Conditioning Experiment

## Purpose

The kinetic-spillage objective does not penalize linear dependence among
contracted zetas. This experiment evaluates a log-determinant barrier for a
Ge DZP Bessel basis fitted to one atom plus seven bulk E-V references.

## Objective and derivative

For primitive overlap $A_k$ and a full contraction $C$, define
$S_k=C^{\mathsf H}A_kC$. The scale-sensitive barrier is

$$
J_{\log\det}=-\frac{\mu}{N}\sum_{e=1}^N\sum_k w_k\log\det S_{e,k}.
$$

For real block coefficients, its full-contraction gradient is

$$
\frac{\partial J_{\log\det}}{\partial C}=
-\frac{2\mu}{N}\sum_{e,k}w_k\operatorname{Re}\left[A_{e,k}C S_{e,k}^{-1}\right].
$$

The implementation reduces that gradient by summing identical atom blocks
and tracing the magnetic identity factor in
$\operatorname{kron}(C_l,I_{2l+1})$. Central finite differences verified the
result to relative error at most $1.1\times10^{-5}$ for one- and two-atom
contractions.

## Ge result

| Fit | kinetic spillage | raw $\lambda_{\min}(S)$ | normalized $\lambda_{\min}(R)$ | $\kappa(R)$ |
|---|---:|---:|---:|---:|
| Unregularized | 0.00338 | 4.08e-4 | 5.40e-4 | 8.36e3 |
| $\mu=10^{-4}$ | 0.00485 | 2.92e-2 | 5.39e-4 | 7.34e3 |
| $\mu=10^{-3}$ | 0.00841 | 0.541 | 1.01e-3 | 3.96e3 |

The stronger barrier halves the scale-invariant condition number and raises
the normalized minimum eigenvalue by 1.86×, but raises kinetic spillage by
2.5×. The weaker barrier primarily rescales the contracted columns.

## Decision

Do not promote raw $-\log\det S$ into the shared objective: spillage is
column-scale invariant while raw log-det is not. The correct next candidate
is the normalized barrier

$$
-\mu\left(\log\det S_k-\sum_i\log(S_k)_{ii}\right)
=-\mu\log\det R_k,
$$

which penalizes only correlation/linear dependence and is invariant under
independent contraction-column rescaling.

## Postscript: the SIESTA crashes were an export bug, not degeneracy

All "degenerate Ge basis" SIESTA aborts (MKL DLASCL/DSTEQR, Fermid
non-convergence) traced to `channel_ns` in `_export_ionnc` receiving zeta
counts instead of principal quantum numbers, which zeroed `orbnl_pop` and
corrupted `vna` in the initial Hamiltonian. After the fix the
unregularized Ge basis (Γ minimum eigenvalue 4e-4) runs a clean EOS:
delta 6.22 meV/atom, B0 59.8 GPa. The barrier basis runs too but scores
104 meV with a jagged E-V curve: over-regularization costs SCF quality,
so the unregularized fit is the production choice. The normalized barrier
itself worked exactly as designed (kappa(R) 8359 → 3.6 at mu=1e-3).

## Evidence

- [Barrier metrics](../../../../.tmp/autoresearch/ge-logdet-barrier/conditioning-metrics.json)
- [Bulk E-V fitting report](../../../../papers/autoresearch/bulk-ev-reference-fitting.md)
- [Notation](./notation.md)
