---
type: Domain Topic
id: methods/development/sympy-numeric-cross-validation
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Debug a symbolic derivation that disagrees with validated numeric code by comparing operators elementwise under basis permutation.
triggers: [sympy numeric mismatch, symbolic derivation bug, sign flip derivation, factor mismatch, invariance proof]
source_project: native
source_sha256: empty
aliases: [symbolic numeric cross-validation]
---

# SymPy-Versus-Numeric Cross-Validation

Use this procedure when a SymPy derivation disagrees with a validated numeric implementation.
Symptoms: a factor mismatch, a sign flip, or a failed invariance.

## Procedure

1. Do not trust the symbolic term decomposition first. Evaluate the full symbolic expression at
   finite parameter values (example: finite q) and compare against the numeric code at the same
   point. A difference means the bug sits in operator construction or conventions, not in the
   expansion algebra.
2. Compare operators elementwise under basis permutation. Numeric code sorts eigenvalues (numpy
   `eigh` sorts ascending); symbolic eigenvector columns follow diagonalization order. Build
   the permutation that maps sorted to symbolic order and compare `sym[np.ix_(perm, perm)]`
   against numeric. Sign flips of single eigenvectors are unitary and harmless in traces.
   Magnitude differences are real bugs.
3. Isolate the buggy operator with a clean ratio. An exact factor 2 or a sign pattern localized to
   one operator matrix identifies the wrong line directly. Found case: a missing `/2` prefactor
   of `M = -e/2 (r x v)` lost during an edit.
4. Re-derive; do not re-fit. Once the operators match elementwise, the symbolic result equals the
   numeric one to all digits. Verified case: -31.100826446281 matched to 12 digits.
5. Prove invariances exactly. State invariance claims (origin shift, symmetry forbiddance) as
   `assert simplify(diff) == 0`. This is strictly stronger than a numeric tolerance. A numeric
   test that passes at 2.7e-9 against a 1e-9 threshold may assert pure finite-difference noise.
   Check that the symbolic result is exactly zero before keeping such a test.

## SymPy gotchas

- `sum()` over matrix generators needs a matrix start: `sum(gen, sp.zeros(n, n))`. The default
  int start 0 raises TypeError.
- `symbol - Matrix` is invalid. Build elementwise with `sp.Matrix(n, n, lambda a, b: ...)`.
- Solve the eigenstructure by hand for small structured matrices with sign patterns; this avoids
  radicals. Verify `H*U - U*diag(eps) == 0` exactly.
