---
type: Domain Topic
id: siesta/development/local-density-matrix-response
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Design localized one-body-potential perturbations in SIESTA and build machine-learning datasets from relaxed density-matrix response.
triggers: [dm response dataset, local potential probe, wannier chemical potential, delta K learning]
source_project: native
source_sha256: empty
aliases: [dm response]
---

# Localized Density-Matrix Response
## Core distinction

Physical static response perturbs a maintained Hermitian one-body
Hamiltonian term and measures the relaxed density kernel:
H(lambda) = H0 + lambda P, dK_lambda = K_SCF(lambda) - K_SCF(0).
A modified `.DM` restart is only an SCF initial-condition kick. Use its
history only for mixer, preconditioner, or metastability studies. In the
nonorthogonal AO basis, fixed-charge response obeys Tr(S dK) = 0.
## Stock prototype: Wannier.ChemicalPotential

SIESTA dev commit `71c8602911` ships a maintained localized potential:
- `Src/m_chempotwann.F90` projects diagonal frozen-Wannier shifts into
  the sparse NAO Hamiltonian.
- `Src/setup_hamiltonian.F` adds the term each SCF iteration.
- `Tests/17.Wannier90/w90-chem-h2.fdf` is the regression input.

The route needs Wannier90 and supports diagonal shifts in one Wannier
manifold. Run paired runs at lambda = 0, +/-lambda1, +/-lambda2; pilot
sweep +/-0.01, +/-0.02, +/-0.05 eV. Enable
`Write.DMHS.History.NetCDF true` and `Charge.Mulliken scf`. Extract
K(lambda), S, H(lambda), free energy, occupations, and residual; compute
central response and odd/even parts; check the half-amplitude plateau
and supercell convergence.
## Arbitrary probe extension
1. Read a covariant Hermitian H_probe once per geometry.
2. Enforce real-space pairing H_mu_nu(R) = H*_nu_mu(-R) and the spin
   convention.
3. Add the probe after ordinary SCF Hamiltonian assembly, every
   iteration.
4. Record probe, amplitude, AO ordering, overlap, and code/input hash;
   add consistent source-energy accounting.
5. For force/stress targets, implement and finite-difference-check
   moving-probe derivatives. A Hamiltonian-only hook covers fixed-ion
   response only.
## ML dataset contract

Target: (G, S, K0, P, lambda) -> dK_lambda. Store native localized AO
onsite/pair blocks; evaluate constraints and losses in
dD = S^(1/2) dK S^(1/2). Include full basis, spin, k-point, smearing,
functional, pseudopotential, charge, branch, and probe metadata. Keep all
signs, amplitudes, blocks, replicas, and frames from one parent state in
the same split. Validate Hermiticity, Tr(S dK), occupation bounds,
E(3) covariance, plateau, reciprocity, screening, and supercell
convergence. Report induced-change error separately from total-matrix
error. Use an E(3)-equivariant orbital-block model; raw AO blocks are not
scalar labels.
