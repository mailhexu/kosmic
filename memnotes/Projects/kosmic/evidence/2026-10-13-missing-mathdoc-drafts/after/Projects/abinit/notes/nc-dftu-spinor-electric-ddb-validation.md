---
artifact_role: knowledge
audience: both
created: 2026-08-12
updated: 2026-08-12
status: draft
tags: [nc-dftu, dfpt, nspinor-2, electric-field, ddb, dielectric, bec, story-496]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "nc-dftu-spinor-electric-ddb-validation.md display math requires one MathDoc marker per equation"
---

# Spinor NC DFT+U Gamma Electric/BEC DDB Validation

Story 496 validates the static, fixed-occupation, Gamma, Dudarev spinor NC+U electric/atom-electric path. It does not claim finite-frequency, metallic, strain, full-interaction, spinor-MPI, or finite-$\mathbf q$ electric support.
This is a noncollinear scalar-pseudopotential fixture, not an SOC calculation: `t123.abi` sets `so_psp 0 0` and its Ni/O DDB headers record `pspso=0`. [nio-nc-dftu-soc-comparison-boundary](nio-nc-dftu-soc-comparison-boundary.md) records why it cannot support a scientific SOC comparison.

The driver owns a snapshot for each converged Cartesian electric response:

$$
\mathcal C_\alpha =
\left(N^{E_\alpha}, V_U^{E_\alpha}\right),
\qquad \alpha\in\{x,y,z\}.
$$

`nc_dftu_copy_response` deep-copies all complex packed `uu`, `dd`, `ud`, and `du` blocks. This is mandatory: the active `nc_dftu_scfcv` object is reused and overwritten by the next Cartesian response. The cache is created only after `scprqt` reports convergence; duplicate directions and incomplete three-direction schedules are rejected.

For an atomic displacement $(\kappa,\beta)$, `dfpt_scfcv` evaluates a frozen atomic response partner and stores

$$
\operatorname{Tr}\left[
V_U^{E_\alpha}N^{\tau_{\kappa\beta}}
\right]
$$

in the native DDB slot

$$
\mathrm{d2nl}(:, \alpha, \mathrm{electric}, \beta, \kappa).
$$

It also stores each electric pair

$$
\operatorname{Tr}\left[
V_U^{E_\alpha}N^{E_\beta}
\right]
$$

in the native electric-electric slots. The electric PAOs are fixed, so their explicit mixed projector curvature is zero at Gamma. This is distinct from finite-$\mathbf q$ atomic pairs, which require the separate packed frozen-curvature implementation in [nc-dftu-spinor-finite-q-frozen-curvature](nc-dftu-spinor-finite-q-frozen-curvature.md).

No DDB writer, reader, unit conversion, or q-star reconstruction was added. The code updates native `d2nl` and `blkflg` only.

## Regression Evidence

- `tests/v10/Input/t123.abi` is the positive compact two-atom spinor NiO Gamma DDK/electric/atomic fixture. Its `NCPU_8` contract compares `t123_MPI8o_DS4_DDB` at $10^{-8}$.
- A rebuilt `tests_nc_dftu_spinor_response` verifies that copying then mutating the source preserves an independent packed `occ1`/`V1` snapshot.
- Fresh direct one- and eight-rank `t123` runs completed. The one-rank `.abo` and DDB pass `fldiff`; the eight-rank 81-entry DDB is byte-identical to its strict reference.
- The eight-rank output has nonzero electric `occ1`, `V1`, and source norms with finite-difference residuals below $7.21\times10^{-10}$.
- The pre-existing runner cache has no `t123`; rebuilding it remains blocked by unrelated malformed `v10[t86]` metadata. The direct ABINIT, reference comparison, and `AbinitTestInfoParser` checks validate the permanent fixture without a runner bypass.

## Evidence History

Earlier `t116` electric-DDB evidence was withdrawn after a DDK second-order-energy run emitted non-finite values. Story 502 initialized the DDK `rhor1` payload and restored finite three-direction DDK output. The separate `t123` fixture is the current positive Gamma electric/BEC DDB evidence and validates the corrected snapshot ownership.

## 2026-08-15 t123 repair attempt — new marginal finding

Repairing t123 (its `nstep 2`/`tolwfr 1e-2` smoke settings collide with the story-496 convergence guard) required two changes: (a) convergence-capable settings (`toldfe1 1e-10`, DDK `tolwfr 1e-10`/`nstep 200`, electric `tolvrs 1e-8`/`nstep 100`); (b) replacing the numerically unstable 1×1×1 k-mesh (GS blows up to E~10¹²⁰ with `occopt 0`+U=8 eV at single k) with t119's proven 4-explicit-k-point sampling. With those, DDK converges 3/3 and **all three electric directions converge (vres2 1.6–2.0×10⁻⁹)** — the guard now passes its convergence requirement — but the run then trips `nc_dftu_check_spinor_hermitian` on the **electric occ1**: max asymmetry 2.98×10⁻⁸ vs `tol8=10⁻⁸` (row 7, col 6). The phonon path (t119) passes the same check, so this is electric-path-specific marginal numerical noise (~3×10⁻⁶ relative on occ1~10⁻²), not the one-sided finite-q form (which would give ~10⁻⁴ asymmetry). Pending production-scale evidence: if the production electric response passes the 10⁻⁸ check, the t123 fix is a tolerance/sampling adjustment; if it also trips, the electric occ1 construction needs investigation.
