---
artifact_role: knowledge
audience: both
confidence: 0.82
created: 2026-05-11
last_validated: 2026-05-11T00:00:00
validation_procedure: |
  Searched local GPAW reference source under Refs/gpaw for PAW projector
  Hamiltonian matrices. Confirmed old GPAW stores atomic Hamiltonian matrices
  in hamiltonian.dH_asp, constructs them from setup PAW correction terms and
  XC PAW correction derivatives, and applies them by unpacking dH_asp[a][s]
  to dH_ii and multiplying projector overlaps P_ni @ dH_ii. Confirmed new GPAW
  paths expose equivalent dH_asii/dH_saii arrays used with P_ani.
validation_test: "tests/tests/test_projector_green.py"
successful_usage_count: 2
last_used_successfully: 2026-05-11T00:00:00
usage_stale: false
related_files:
  - "Refs/gpaw/gpaw/old/hamiltonian.py"
  - "Refs/gpaw/gpaw/new/lcao/hamiltonian.py"
  - "Refs/gpaw/gpaw/new/fd/hamiltonian.py"
  - "Refs/gpaw/gpaw/new/pwfd/diropt.py"
  - "TB2J/TB2J/projector_green.py"
related_functions:
  - "apply_non_local_hamilton"
  - "Hamiltonian.calculate_atomic_hamiltonians"
  - "Hamiltonian.apply"
  - "CollinearHamiltonianMatrixCalculator._calculate_matrix_without_kinetic"
  - "ProjectorGreenData.get_hij_spin_difference"
  - "project_potential_to_hij"
  - "pack_site_hij"
  - "build_site_projector_indices"
tags: [paw, projector, hamiltonian, hij, gpaw, green-function]
project: TB2J
status: draft
validated_by: automatic
validation_date: 2026-05-11T00:00:00
links_to: ["paw_projector_greens_function", "projector_greens_netcdf_schema"]
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "paw_projector_hamiltonian_dij.md display math requires one MathDoc marker per equation"
---

# Projector Hamiltonian Matrix `d_ij` / `H_ij`

Within PAW, the local nonlocal-Hamiltonian correction in projector space is already computed by DFT codes such as GPAW. GPAW's old backend stores it as packed atomic matrices `hamiltonian.dH_asp`; the new backend exposes equivalent unpacked matrices such as `potential.dH_asii` or `dH_saii`.

This matrix is not a density or density matrix. For a selected PAW/projector channel basis, it is the projector-channel Hamiltonian or potential matrix:

$$
H^a_{ij,\sigma}=\langle p_i^a|H_\sigma|p_j^a\rangle.
$$

For collinear exchange-like traces, TB2J should use the spin-dependent part

$$
\Delta^a_{ij}=H^{a,\uparrow}_{ij}-H^{a,\downarrow}_{ij},
$$

and may disregard the spin-independent part of `H_ij`.

## GPAW Evidence

In `Refs/gpaw/gpaw/old/hamiltonian.py`, `calculate_atomic_hamiltonians()` constructs `dH_sp` from setup PAW terms such as `K_p`, `M_p`, `MB_p`, Coulomb terms, `Delta_pL @ W_L`, Hubbard-U derivatives, external PAW corrections, and XC PAW correction derivatives. It stores the result as `dH_asp` via `update_atomic_hamiltonians()`.

The same file's `apply_non_local_hamilton()` and `Hamiltonian.apply()` unpack `dH_asp[a][spin]` into `dH_ii` and apply it through projector overlaps `P_ni @ dH_ii`, then adds the result back through PAW projectors. This is precisely the form needed for a projector-channel Green-function trace.

New GPAW code uses the same concept with different containers. `new/lcao/hamiltonian.py` adds `(P_Mi @ dH_ii).conj() @ P_Mi.T` to the potential matrix. `new/pwfd/diropt.py` forms `c_ani[a] = P_ni[bands] @ dH_ii` from `potential.dH_asii` before adding projector contributions back to wave functions.

## Other Projector Families

For projector families that do not already have a PAW-like nonlocal Hamiltonian matrix, the DFT-code-side converter must compute the same normalized object directly. Given chosen projectors `p_i`, it should project the relevant spin-dependent potential or Hamiltonian onto that basis:

$$
H^a_{ij,\sigma}=\langle p_i^a|V_\sigma|p_j^a\rangle
\quad \text{or} \quad
\langle p_i^a|H_\sigma|p_j^a\rangle,
$$

depending on what the projector Green-function trace is intended to use. The spin-independent part may be stored for auditability but the first TB2J trace uses

$$
\Delta^a_{ij}=H^{a,\uparrow}_{ij}-H^{a,\downarrow}_{ij}.
$$

This projection belongs in the DFT exporter because it requires access to the real-space or reciprocal-space potential representation and the exact projector definitions used by that code. TB2J should validate and consume the resulting `hij`; it should not try to reconstruct source-code-specific potentials from the portable spectral file.

TB2J now provides small exporter-side helper functions for simple discrete representations: `project_potential_to_hij(projectors, potential, weights)` computes the projection, `build_site_projector_indices(projector_site)` builds the padded site map, and `pack_site_hij(hij_global, site_projector_indices, site_nproj)` packs global projector matrices into the v1 site-local NetCDF layout. Real DFT exporters may use these helpers only if their projector and potential arrays are already represented on a compatible grid or quadrature.

## TB2J Schema Implication

The normalized TB2J field should be called `hij`/`H_ij` because TB2J consumes it as a Hamiltonian/potential matrix. For PAW exporters, the source metadata can record that this normalized `hij` came from a code-native `d_ij`, `dH_asp`, or `dH_asii` matrix. For non-PAW exporters, metadata should record that `hij` was computed by explicit projection of the chosen potential/Hamiltonian onto the projectors.

NetCDF `hij` variables should include `definition`, `units`, and, when available, `source` and `projection` attributes. For example, a PAW exporter may set `source="GPAW dH_asp"` and `projection="native PAW projector Hamiltonian matrix"`; a non-PAW exporter may set `source="projected DFT potential"` and `projection="<p_i|V_up/down|p_j> on real-space grid"`.

For exchange use, validation should reject density-like definitions and accept only definitions that identify projector Hamiltonian/potential semantics, such as `paw_dij_projector_hamiltonian`, `paw_dh_asp_projector_hamiltonian`, or `projected_spin_dependent_potential`.

## Linked Concepts

- [paw_projector_greens_function](paw_projector_greens_function.md)
- [projector_greens_netcdf_schema](projector_greens_netcdf_schema.md)
