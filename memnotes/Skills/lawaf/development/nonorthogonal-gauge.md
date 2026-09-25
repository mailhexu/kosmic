---
type: Domain Topic
id: lawaf/development/nonorthogonal-gauge
domain: lawaf
audience: development
artifact_role: guideline
status: draft
summary: Implement, use, and debug lawaf's raw projected, constant GL, and k-dependent non-orthogonal Wannier gauges; mode matrix, contracts, optimizer math, verification.
triggers: [nonorthogonal gauge, k-dependent gauge, GL spread optimizer, gauge transform]
aliases: [nonorthogonal gauge implementation, nonorthogonal gauge toolbox]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: lawaf
source_sha256: ef859b16727d14f6b716b90a2c1c93149e9e00c71de652206bd25eae119b742f
---

# Non-Orthogonal Gauge Machinery

Implement or debug lawaf's non-orthogonal Wannier gauges in `lawaf/wannierization/` (2026-09-19, commits 0ef42c8..e3a118c): constant G (`nonorthogonal_gauge.py`), k-dependent G(k) (`kdependent_gauge.py`), raw projected (`orthogonal=False`).

## Mode matrix (never silently degrade)

- Raw projected (`orthogonal=False, method="projected"`): finite-range `SwannR`; exact on mesh, truncation cost off mesh. No composition; unity weights and full-rank projections only.
- Constant GL (`nonorthogonal_gauge=G` / `apply_gauge_transform`): overlap `G†G δ_R0`; congruence gives exact bands at every k; composes with any pipeline (mlwf, dis_*, window_bands).
- k-dependent GL (`optimize_kdependent_gauge(..., shells=1)`): exact on mesh only; R-space consumed, warning emitted; composes opt-in.

## Hard contracts

scdm-k always orthonormalizes (raw weighted columns are rank-deficient). Weighted/window bands plus raw gauge give a singular Gram; `Wannierizer.get_wannk_and_Hk` raises a k-context ValueError. `method="mlwf"` refuses Sk parents and `orthogonal=False` (ADR-3). `apply_*_transform` refuses NAC LWFs and non-orthogonal inputs; apply post-pipeline only; the k-dependent apply warns off-mesh and enforces a conditioning floor.

## Design facts and optimizer pitfalls (verified; do not re-derive)

- The orthonormal MV gauge is a stationary point of the GL functional. Use multi-start seeded tilts or constant-G init (`Lambda(0)=logm(G_const)`).
- The unconstrained GL infimum is degenerate (columns collapse, rank 1). Use a logdet barrier; k-dependent needs the scale-invariant per-k `logdet(S/diag S)` (plain `logdet(S)` rewards unbounded growth).
- Moment quadratic forms: einsum `"an,ab,bn->n"`. H congruence: `"kma,kmb,kbl->kal"` (G row contracts H column).
- Wirtinger for real f: `df/dIm z = +2 Im(df/dz*)`; jac `[2 Re c, +2 Im c]`. Penalty adjoint: `d eps_n = 2 Re[(dG w_n)†(H − eps_n I)G w_n]`.
- Batched `np.linalg.slogdet` returns an array sign; guard `np.any(sign<=0)`.
- FT: analysis k_to_R carries 1/nk; synthesis R_to_k carries Rdeg and the MINUS phase adjoint. exp map adjoint-Frechet: `X = dexp(L†)[EG]`.
- Positions: one row per basis function. Phonons: fractional centres, atoms×3. Electrons: `atoms.get_positions()`. Cartesian triples units. Generic optimal G mixes irreps; restrict blocks to keep labels.

## Tests and verification

Tests `test_nonorthogonal_gauge.py`, `test_nonorthogonal_wannier.py` (synthetic OrthoTB/NonOrthoLCAOModel via `sys.path.insert(0,"tests")`), `test_kdependent_gauge.py`. Fixture `tests/fixtures/phonopy/BaTiO3_DM_dip_wang.yaml`. Never run overlapping pytest (shared `phon_cache/` corrupts). FD-check gradients on real and imaginary axes (h=1e-6, tol 1e-5). Assert mesh pencil equality vs the orthonormal control; `SwannR == G†G delta_R0` (constant) or SPD with floor (k-dependent); netCDF round trip preserves `SwannR`.
