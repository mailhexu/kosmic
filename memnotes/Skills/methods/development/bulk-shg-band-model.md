---
type: Domain Topic
id: methods/development/bulk-shg-band-model
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Implement independent-particle bulk electric-dipole second-harmonic generation from tight-binding, Wannier, or non-orthogonal LCAO Hamiltonians.
triggers: [bulk shg, second harmonic generation, aversa sipe, length gauge, nonlinear susceptibility band model]
source_project: native
source_sha256: empty
aliases: [shg band model]
---

# Bulk SHG From a Periodic Band Model

Compute the independent-particle, electric-dipole bulk susceptibility `chi^(2)_abc(-2w; w, w)`
in `P_a(2w) = eps0 chi^(2) E_b(w) E_c(w)`. SHG is second-harmonic generation. Keep excitonic,
quasiparticle, local-field, phonon, magnetic-dipole, electric-quadrupole, and surface physics
out of the baseline. A centrosymmetric bulk has zero electric-dipole `chi^(2)`; band
eigenvalues alone do not determine SHG, so require wavefunctions and the optical geometry
(position and dipole matrix elements).

## Formulation

Use the complete Aversa-Sipe length-gauge expression `chi^(2) = chi_inter + chi_intra +
chi_mod`; do not keep only the three-interband-state term. Prefer the length gauge for finite
tight-binding band sets; the velocity gauge needs completeness sum rules and truncation creates
low-frequency divergences. Use one documented retarded prescription `w -> w + i eta` in every
denominator. Core sources: Aversa/Sipe PRB 52, 14636 (1995); Sipe/Shkrebtii PRB 61, 5337
(2000); Taghizadeh et al. PRB 96, 195413 (2017); Ventura et al. PRB 96, 035431 (2017); Wang et
al. NJP 21, 093009 (2019).

## Model inputs

Orthonormal tight binding or Wannier: lattice and coordinate convention, `H(R)`, orbital
embeddings `tau_alpha`, position matrix elements `<0 alpha|r_a|R beta>`, and band connection
`A^a = i U^dag dU/dk_a + U^dag A^(W),a U`. A point-orbital approximation from orbital centers
only must stay explicit; it does not replace the dipole matrix. Non-orthogonal linear
combination of atomic orbitals (LCAO): require `H(R)`, `S(R)`, and position matrix elements;
solve `H(k) c_n = eps_n S(k) c_n` with `c_m^dag S c_n = delta_mn`; use `A^a = i C^dag S dC/dk_a
+ C^dag A^(L),a C` with local gauge term `<0 alpha|r_a|R beta> - R_a <0 alpha|R beta>`. Never
Loewdin-orthogonalize only H; transform every optical operator and derivative too.

## Covariant derivative and verification

For nondegenerate bands use the covariant derivative `(r^a_nm);b = d r^a_nm/dk_b - i (A^b_nn -
A^b_mm) r^a_nm`; never finite-difference independently diagonalized eigenvectors. Use analytic
derivatives (real-space Fourier interpolation, analytic perturbation theory, gauge-covariant
links) and non-Abelian projectors or parallel transport at degeneracies. Verify: Hermiticity
and normalization; zero electric-dipole tensor for an inversion-symmetric model; invariance
under per-band U(1) phases and under a localized-basis unitary co-transforming H, S, and r;
`chi_abc = chi_acb`. Converge the Brillouin-zone mesh, broadening, band count, and cutoffs
independently. Match the linear dielectric response before trusting SHG. Return 3D `chi^(2)` in
m/V and 2D sheet `chi^(2)` in m^2/V; do not hide a vacuum-thickness convention.
