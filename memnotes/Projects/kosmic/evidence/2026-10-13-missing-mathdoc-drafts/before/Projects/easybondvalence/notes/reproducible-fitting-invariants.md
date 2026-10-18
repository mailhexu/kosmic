---
type: reference
status: stable
audience: both
artifact_role: knowledge
---

# Reproducible Fitting Invariants

---
confidence: 0.9
created: 2026-08-09
last_validated: 2026-08-09
validation_procedure: "Run the package fitting tests: they verify frozen dataset fingerprints/provenance, canonical complete fit plans, physical data-Jacobian diagnostics, coverage, and normalized termination."
tags: [bond-valence, fitting, provenance, reproducibility]
related_files:
 - ../../../../easybondvalence/src/easybondvalence/fitting.py
 - ../../../../easybondvalence/tests/test_fitting.py
---

## Definition

A conventional fitting dataset freezes its structure, signed valence assignment, contact membership, periodic-image identities, and site weights before optimization. Its `fingerprint` hashes this canonical numerical content only. Dataset `provenance` identifies the source records; `descriptor_version` identifies the frozen contact/descriptor builder. Neither replaces the other.

A fit plan has one explicit entry for every model parameter field (`identifier:r0` and `identifier:b`). Entries are in canonical key order. A field is free, fixed, or tied. Tied entries have the same physical field, initial value, transform, and bounds as their free representative.

The initial conventional residual is

$$
r_i=\sqrt{w_i}\left(V_i-|z_i|\right).
$$

The local sensitivity and available covariance use the **data-only** residual Jacobian at the solution in physical free-parameter coordinates. Regularizer rows, robust-loss weighting, and raw optimizer coordinates are excluded. Covariance is unavailable unless the loss is linear, the fit has no regularizer, the data Jacobian is full rank, bounds are inactive, and residual degrees of freedom remain.

`CoverageReport` records complete model/plan-key coverage, selected contact count, observed parameter identifiers, unobserved parameter identifiers, and covered `(structure_id, site_index)` residuals. `FitResult` separately records a normalized termination reason and function/Jacobian evaluation counts.

## Rationale

A numerical fit is interpretable only when the data being optimized, parameterization, provenance, local identifiability diagnostic, and solver exit mode can be reconstructed without exposing a live SciPy optimizer object.

## Linked Concepts

- [[bond-valence-model-boundaries]]: Descriptor and fitting boundaries.
- [[notation]]: $V_i$, $z_i$, and fitting-target conventions.
