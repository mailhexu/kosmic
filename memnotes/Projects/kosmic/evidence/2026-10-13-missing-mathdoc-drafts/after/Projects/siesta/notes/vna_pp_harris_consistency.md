---
artifact_role: knowledge
audience: both
confidence: 0.98
created: 2026-07-19
last_validated: 2026-07-19T10:23:00
validation_procedure: |
  Compare the recorded equal-geometry external .orb SCF runs for Si, SiO2,
  and Ni FCC with Vna.Source shell_sum and Vna.Source pseudopotential at
  800 Ry and DM.Tolerance 1e-5. Separately inspect the permanent nine-run
  three-mode band benchmark in papers/siesta_basis_consistency/benchmarks/
  vna_pp_density_bands/inputs/, data/, and plot_three_mode_bands.py.
related_files:
  - "siesta/Src/atom.F"
  - "siesta/Src/rhooda.F"
  - "siesta/Src/broadcast_basis.F"
related_functions:
  - "Vna"
  - "rhooda"
  - "store_pp_rhoatm"
tags: ["vna", "harris-density", "external-basis", "psml", "mpi", "bands"]
project: siesta
status: draft
validated_by: automatic
validation_date: 2026-07-19T10:23:00
links_to: ["Vna_definition", "Vna_external_basis", "external_basis_implementation"]
linked_from: ["rhoatm_scf_bootstrap"]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "vna_pp_harris_consistency.md display math requires one MathDoc marker per equation"
---

# Vna and Harris Atomic Density Must Match

SIESTA decomposes the local electrostatic potential as:

$$
V_{\mathrm{eff}} = V^{\mathrm{na}} + V^{\mathrm{H}}[\rho_{\mathrm{SCF}} - \rho_{\mathrm{atm}}] + V_{\mathrm{xc}}[\rho_{\mathrm{SCF}}].
$$

Therefore the density used to construct the neutral-atom potential,

$$
V^{\mathrm{na}} = V^{\mathrm{local}} + V^{\mathrm{H}}[\rho_{\mathrm{atm}}],
$$

must be the same $\rho_{\mathrm{atm}}$ used by the Harris-density routine `rhooda`.

`rhooda` normally constructs its mesh density from free-atom basis populations:

$$
\rho_{\mathrm{atm}}(\mathbf r) = \sum_i D_i^{\mathrm{atm}} |\phi_i(\mathbf r)|^2.
$$

Changing only `Vna()` to use PSML `vp%chval` leaves an unphysical fixed term $V^{\mathrm H}[\rho_{\mathrm{PP}} - \rho_{\mathrm{shell}}]$ in the SCF Hamiltonian. This caused false 13–629 eV energy shifts and made the Ni FCC test converge to a non-magnetic state.

The `vnafrompsp` implementation adds opt-in `Vna.Source pseudopotential`. For external `.orb` species it truncates and renormalizes `vp%chval` at the basis cutoff, uses it in `Vna`, and stores the equivalent three-dimensional density in `spp%rhoatm_pp`. `rhooda` interpolates that field on the real-space mesh and skips its basis shell sum for that species. `Vna.Source shell_sum` is the default and preserves prior behavior.

At 800 Ry and `DM.Tolerance 1e-5`, `pseudopotential` minus `shell_sum` total-energy differences are -2.036 meV/cell for Si, -2.203 meV/cell for SiO2, and -1.995 meV/atom for Ni FCC. Both modes converge in 8, 23, and 31 SCF iterations respectively; Ni remains ferromagnetic with 0.68354 μB in both modes. A two-rank MPI Si PP run matched serial exactly after broadcasting `rhoatm_pp` and its flag.

The original equal-geometry SCF records retain absolute energies, raw Fermi references, and per-mode iteration counts. Shell and PP energies are -229.905978/-229.908014 eV for Si, -3033.467195/-3033.469398 eV for SiO2, and -4565.256040/-4565.258035 eV for Ni. The respective counts are 8/8, 23/23, and 31/31.

Raw Fermi references are descriptive only. The original Ni logs report a common spin Fermi value, whereas fixed-spin Ni band logs report EFup and EFdown separately. Neither set supports a physical Fermi-shift, work-function, or chemical-potential claim without a shared potential reference.

The permanent band benchmark is distinct from the original SCF validation. It compares default DZP, shell_sum, and pseudopotential at 800 Ry for each material. Default DZP is a basis reference, not a Vna variant. Ni uses `FixSpin .true.` and `TotalSpin 1.0` there, unlike the original unconstrained Ni runs.

After alignment to the maximum occupied eigenvalue on the sampled path (not the global VBM), Si and SiO2 shell-versus-PP maximum/RMS band differences are approximately 0.0001/0.00005 eV and 0.0002/0.00005 eV. Spin-resolved Ni, aligned by each mode's scalar `.bands`-header reference shared across spins, gives approximately 0.0071/0.00047 eV. The three figures and their inputs, data, logs, and script are documented in `papers/siesta_basis_consistency/vna_pp_density_validation.md`.
