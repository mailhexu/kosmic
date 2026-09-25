---
type: Domain Topic
id: methods/development/risb-solver-recipes
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Convergence recipes (U-continuation, corridor plus kappa-drop, warm transfer across orbit regroupings), normalizer status, and grid pitfalls for the TBUpy RISB solver.
triggers: [risb convergence, slave boson solver, u continuation, kappa drop, warm start transfer]
source_project: native
source_sha256: empty
aliases: [risb recipes]
---

# RISB Solver Convergence Recipes

Operational recipes for the rotation-invariant slave-boson (RISB) solver `tbupy/risb.py`
(`RisbSolver`, `UnrestrictedRisbSolver`, `solve_afm_twosublattice`); the derivation identities
live in `docs/derivations/risb_derivation.py` (checks IU1 to IU8).

## Convergence

Cold Levenberg-Marquardt (LM) starts fail at physical coupling for large M. Example: M = 10
Kanamori at physical U stalls off the metallic basin with residuals near 1; fix with
U-continuation (solve at smaller U, warm-start the next step). Warm transfer across orbit
regroupings: the Kanamori energy classes regroup as U crosses 2J, so map warm vectors per
configuration: `y_tgt[o] = mean over tgt.orbits[o] of src per-config amplitudes`, with the src
amplitude `sqrt(phi_prob[o]/orb_mult[o])` broadcast over src orbits. Never copy y vectors per-
orbit across different clusterings; shape and semantics both break. Lambda and lambda0 transfer
directly.

Multiorbital saddles (LaMnO3 d-d block at physical filling) converge only through corridor plus
kappa-drop: walk the metallic corridor `kappa = -U/2` (each 1 eV step stays metallic, Z near
0.97), then halve the |kappa| down to the physical kappa_d with warm transfers. Cold or naive
warm starts at physical kappa_d land on a Z = 0 collapsed branch with stalled residuals 1e-2 to
6e-2; do not mistake this for a normalizer problem (check IU8).

## Normalizer

The frozen scalar `M_bar = [Delta(1-Delta)]^-1/2` is the exact constraint-manifold value of the
matrix normalizer `M(y) = [s Delta_p - Delta_p^2]^(-1/2)` for any M; do not replace it with
uncorrelated-inverse candidates. The story-074 M > 2 collapse was a K1 basis-mixing bug (fixed:
`conj(u0)` versus `u0` in the atomic/eigen-basis bilinear), not a normalizer defect.

## Performance and numerics

The M = 10 LM hung in the finite-difference (FD) Jacobian on a 6.5 GB tensordot; `_s1` and
`_s1_grad` now use reshaped matmul contractions and `_omega_grad` a diagonal-only Delta^(p)
path, with full Delta^(p)/Delta^(h) matrices computed once at result assembly. LM root
selection is path-dependent near degenerate stationary points: cross-version same-start digests
can diverge spuriously with several roots at residuals near 0, so compare energies and
observables, not pointwise solutions. One-band RISB: Z stays spin-symmetric at polarized
saddles; the spin splitting lives in Lambda_sigma.

Grid statistics on a cubic epsilon grid with even nk: the (pi,pi,pi)-shift particle-hole
pairing is exact, but the cos(pi/2) degenerate set splits at 1e-16 across sign classes; round
|eps| below 1e-10 to zero and drop before any occupied-mean statistic. Then `S(0,1) = -2
kappa_h` exactly in the reduced-zone convention; the factor 2 counts the two sites of the
folded cell.
