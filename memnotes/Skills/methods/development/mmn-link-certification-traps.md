---
type: Domain Topic
id: methods/development/mmn-link-certification-traps
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Certify wannier90-style overlap links on finite grid oracles; five silent convention traps plus oracle design rules.
triggers: [mmn overlap links, wannier90 mmn, spread functional certification, bz wrap phase, link normalization]
source_project: native
source_sha256: empty
aliases: [mmn certification]
---

# MMN Link Certification Traps

Certify wannier90-style overlap links `M(k,b) = <u_m(k)|u_n(k+b)>` on a finite supercell or
grid oracle (example: a Marzari-Vanderbilt spread functional). Check the five conventions below
before trusting any result; each convention silently broke one naive implementation (verified
2026-09-21 on the lawaf non-orthogonal functional certification).

1. Use periodic parts, not Bloch sums. Full Bloch sums `phi(k) = sum_R exp(2 pi i k R) g(x-R)` are
   orthogonal on a finite supercell at different k. Links built from them are structurally
   zero. Build `u(k,x) = exp(-2 pi i k x) phi(k,x)` and form `M = <u(k)|u(k')>`.
2. Apply the Brillouin-zone (BZ) wrap G-phase. For a pair (k_i, k_j) that wraps the zone boundary,
   phase the second state with the reduced representative `k_j_rep = k_i + dk - round(dk)`, `dk
   = k_j - k_i`. The raw mesh value carries a spurious `exp(-2 pi i G x)` that destroys exactly
   the two wrap links: `1-|M_nn|^2` reaches 0.2 there against 1e-4 elsewhere. Symptom: the
   total functional grows linearly with the mesh count while interior links look correct.
3. Use physical wavevector units. `b_cart = 2 pi / NK` for lattice constant a = 1. Using `b =
   1/NK` inflates `Omega_I` by `4 pi^2` and the centre estimator by pi. Keep the weight
   convention `sum_b w_b b_cart^2 = 1`.
4. Do not apply a `1/L` supercell normalization to links. `M(k,k) = I` fixes the scale. Dividing
   by the cell count gives `|B|^2` of order `1/L^2` and an `Omega` of order `NK^2`.
5. Separate centre from variance. The `Omega_D`-style term `mean(w_b b arg B_nn)^2` estimates the
   centre `r_bar_n`, not a variance correction. Compare it against the oracle first moment, and
   `Omega_I` against the variance, separately.

## Oracle design

Size the supercell so inverse-Fourier aliasing is absent: NK = 16 aliases on L = 17 and L = 33
cell supercells, and the exact variance then blows up to supercell scale `(L/2)^2`. Validate
with NK of 32 or more and check that exact moments are NK-stable before blaming the functional.
A Loewdin twin control (orthonormal gauge `G_twin = G (G^dag G)^-1/2`) must pass with the same
machinery; a twin failure means the link construction is wrong, not the non-orthogonal
generalization. Healthy interior links satisfy `1-|M_nn|^2 = b_cart^2 var` to machine
precision; scan all (k,b) pairs for outliers to localize wrap or seam defects.

## Open issue (2026-09-21)

NK = 64 showed a mild uniform link-metric excess on one state (0.0695 against exact 0.0221)
with healthy per-link values on the lawaf Gaussian oracle. The issue is unresolved. Isolation
step: analytic Gaussian-Fourier links `int |g|^2 exp(-2 pi i b s) ds` instead of the grid.
Reference: lawaf vault `specs/research/2026-09-21-mmn-functional.md`.
