---
type: Domain Topic
id: methods/development/nonlinear-response-shg
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Design multipole second-harmonic generation and finite-q nonlinear response kernels in tight-binding and Green-function models, with the spin-spiral generalized-Bloch derivation as reference pipeline.
triggers: [multipole shg, nonlinear response kernel, spin spiral green function, generalized bloch, magnetic force theorem, finite-q response]
source_project: native
source_sha256: empty
aliases: [tb green multipole shg, spiral gbt derivation]
---

# Nonlinear Response and SHG in Tight-Binding and Green-Function Models

Design electric-dipole (E1), magnetic-dipole (M1), and electric-quadrupole (E2) second-harmonic
generation (SHG) and finite-q nonlinear response in tight-binding (TB) and Green-function
models. Declare Fourier phase (prefer `exp(i q r - i w t)`), signed charge, quadrupole
convention, and moment units first. Keep `q1`, `q2`, `Q = q1 + q2` separate; never collapse to
degenerate SHG before deriving every vertex.

Assemble the total finite-q current `J_i(Q,W) = K_i;jk(Q; q1, q2) E_j(q1,w1) E_k(q2,w2)` first;
expand only after assembly: `K = K^(0) + q1l K_l^(1,1) + q2l K_l^(1,2) + O(q^2)`. `K^(0)` is
the E1 SHG kernel, the q-linear response is spatial dispersion, and E2/M1 pieces are
projections under a named origin, not primary solvers. Keep vertex-multipole and emitted-source
classifications separate; replace each vertex in turn and include intrinsic input permutation.
Provide finite-q charge/current vertices, contact vertices, position/dipole matrices, form
factors, and overlap-aware operators; keep the full Green-function topology (contact vertex,
both mixed orderings, triangle, permutation) and enforce Ward identities.

## Spiral generalized-Bloch pipeline
Normative scripts (mydev): `TB2J/docs/sympy/spiral_green_function_mft.py`,
`spin_spiral_generalized_bloch.py`, `spiral_force_theorem_J.py`.

1. Toy model: ring of N cells, L sublattices; signed-R hopping classes with pairing `t(nu,mu,-R) =
   conj(t(mu,nu,R))`; never close classes ad hoc. Bond phase `exp(-i sigma (theta_b -
   theta_a)/2)`; folded pencil with half-angles `alpha_mu = 2 pi q tau_mu + phi_mu`; overlap S
   carries the same phases.
2. Twist gauge (top failure mode): W carries the cell half-twist only, `W[(a mu s),n] = N^-1/2
   exp(-2 pi i k_n a) exp(+i sigma_s pi q a)`; then `W H_s W^dag` is block-diagonal in
   `Hq(k_n)`; derive unfolding from the stored W.
3. Prove identities in order: spectral form with unit residues (`Tr[S G] = sum_n 1/(E-eps)`);
   full-matrix unfolding; contour transform `E(q)-E(0) = (1/2 pi i) ∮ z f(z) Tr[S_q G_q - S_0
   G_0] dz`; curvature `C = (2 pi)^2 a^T M a` with zero mode `sum_b M_ab = 0`; q-shift identity
   with `d = 0`.
4. Physical traps: flux-free z-rotations are an exact gauge, so never build E(q) from them; a
   filled isolated band has zero stiffness, so assert a metallic reference; eigenvalue-sum
   curvature uses `f_n`, relaxed-density curvature `f_n(1-f_m)`.
5. Numerics: SymPy `.charpoly()` sorting crashes on uncombined exponentials; use `sp.det(x*I - H)`
   with `sp.expand`; use a 5-point fourth-order stencil at h = 1e-3; real hoppings for `E(q) =
   E(-q)`.

## Validation ladder

Compare sum-over-states, density-matrix, and Green-function backends on a finite inversion-
symmetric cluster: momentum conservation, input permutation, inversion-zero q^0 E1 response,
analytic q derivative versus centered finite differences, Ward identities, gauge agreement,
origin-shift invariance, resonances, completeness. Then extend to periodic TB, Wannier/LCAO
operators, slabs, and conserving interactions. Keep radiation geometry (surface E1, bulk E2/M1,
Fresnel factors, propagation, phase matching) in a separate boundary layer, not in the
microscopic electronic kernel.
