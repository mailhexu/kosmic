---
type: Domain Topic
id: methods/development/gram-accumulator-exactness
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Diagnose Gram-matrix accumulators that drop cross-chunk terms and produce negative quadratic objectives or wrong least-squares solves.
triggers: [gram matrix, chunked fit, negative quadratic form, least squares accumulator, streaming fit]
source_project: native
source_sha256: empty
aliases: [gram accumulator]
---

# Gram-Accumulator Exactness

Use this procedure when a least-squares or Gram-matrix accumulator in a fitting pipeline
produces impossible values: a negative quadratic form, NaN under a square root, or a solution
that does not reduce the residual.

## Diagnosis

1. Evaluate the quadratic form at the exact minimizer and at three random vectors. A negative
   value at the minimizer proves the accumulators are inconsistent. The true form is positive
   semidefinite (PSD).
2. Recompute the right-hand side, diagonal, and target norm from the design columns: `rhs_j = g
   <residual, X_j>`, `diag_j = g ||X_j||^2`, `target_norm = g ||residual||^2`. Diagonal
   agreement with off-diagonal disagreement identifies cross-chunk terms dropped by a blockwise
   streaming accumulation.

## Fix

3. Store the design matrix `Xc` with shape (ncoeff, feature_dim) when `feature_dim^2` is much
   smaller than `ncoeff^2`. Derive every contraction from it: submatrix, matvec, column,
   quadratic form. Keep a dense Gram cache only under an explicit byte budget.

## Regression test

4. Assert that the accumulator quadratic equals the explicit residual norm `||dK - Xc c||^2` at an
   arbitrary `c` and after index slicing.
