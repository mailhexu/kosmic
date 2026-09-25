---
type: Domain Topic
id: methods/development/dm-response-identity-verification
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Verify mean-field density-matrix response identities on a seeded toy Hubbard model before trusting or porting any response module.
triggers: [density matrix response, response identity, 2n+1 theorem, matsubara sum, hubbard toy model]
source_project: native
source_sha256: empty
aliases: [response identity verification]
---

# Density-Matrix Response Identity Verification

Use this procedure when implementing, reviewing, or porting code that computes the energy
response to density-matrix (DM) changes: the TBUpy response module, SIESTA probe workflows, or
DFT+U occupation response. Canonical implementation:
`memnotes/Projects/DMModel/specs/research/2026-09-17-supporting/verify_identity_checks.py`; all
checks pass on 2026-09-17. Port that script as the regression suite, keep the seeds fixed, and
run in the mydev environment (numpy/scipy).

## Toy model

Seeded spinless mean-field Hubbard model, orthogonal basis, T=0 projector occupations, self-
consistent field (SCF) converged to 1e-14: `E_int(P) = Re Tr[P h0] + 1/2 sum_i U_i P_ii^2` with
small U_i (0.15 at most) and split levels; `H[P,lambda] = h0 + diag(U_i P_ii) + lambda V` with
Hermitian probe V. The total energy under the probe is `E_tot = E_int(P) + lambda Re Tr[P V]`;
never report `E_int` alone. Measure every response by central finite differences (FD) of
converged SCF runs with delta = 1e-5, and treat the analytic formulas as the code under test.

## Checks V1 to V5

1. V1: `grad_P E = H_SCF[P]`. Compare directional derivatives against `Tr[H A]` for 30 random
   Hermitian matrices A at tolerance 1e-7.
2. V2 (2n+1 theorem): fit the odd part of paired plus and minus lambda runs to `[lambda,
   lambda^3]`; `c1 = <P0,V>`. Fit the even part to `[lambda^2, lambda^4]`; `c2 = 1/2 <V,P1>`
   with P1 the FD derivative. Note the factor 1/2. Report the nonzero c3 and c4, and that the
   frozen curvature (re-diagonalize bare h0 + lambda V) differs from the relaxed.
3. V3: build the response matrices chi0 and chi column by column as `dn_i/dlambda_j`. chi0 comes
   from frozen-potential re-occupation around the converged `H[P0]`, never the bare h0. Verify
   `chi = (I - chi0 diag(U))^-1 chi0` at 1e-8, reciprocity `chi = chi^T`, and the uniform-shift
   null mode `chi . 1 = 0`. Invert only on the quotient space; `1/chi0_ii - 1/chi_ii` equals
   U_i only in the single-site limit.
4. V4 Matsubara: `f(xi) = 1/2 + (1/beta) sum_(n=-M)^(M-1) (i omega_n - xi)^-1` with a plus sign
   and a symmetric sum. Accelerate the 1/M tail with Richardson extrapolation at M = 1e5 and
   2e5, tolerance 1e-9.
5. V5: at the SCF solution with `Sigma = diag(U_i P_ii)`, `E_int = Re Tr[P h0] + 1/2 Re Tr[P
   Sigma]` holds to machine precision.

## Known traps

Each trap produced a real bug that these checks caught: a probe term missing from the total
energy; a wrong chi0 baseline (bare h0 instead of converged H[P0]); a wrong Matsubara sign or
one-sided sum; `np.diag(np.eye(N))[j]` being a scalar that silently broadcasts into an all-
elements perturbation; and fixed-point chi solves that diverge when the spectral radius of
`chi0 U` exceeds 1 (use FD SCF instead).
