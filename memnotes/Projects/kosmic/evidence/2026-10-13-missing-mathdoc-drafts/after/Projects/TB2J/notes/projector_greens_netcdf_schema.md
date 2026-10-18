---
artifact_role: knowledge
audience: both
confidence: 0.8
created: 2026-05-11
last_validated: 2026-05-11T00:00:00
validation_procedure: |
  Searched TB2J MemNotes for NetCDF, Green-function, projector, PAW, and schema
  conventions. Reused the existing magnon NetCDF convention in
  TB2J/TB2J/magnon/eigenstates.py: optional netCDF4 dependency and explicit
  final complex dimension with components [real, imag]. Extended the prior
  PAW projector Green-function research note into a code-agnostic schema for
  PAW and norm-conserving plane-wave projector workflows. Revalidated the v1
  spectral-only subset by implementing TB2J/TB2J/projector_green.py and running
  tests/tests/test_projector_green.py on 2026-05-11. Extended validation with
  backend protocol, projector exchange-trace helpers, the GPAW PAW bcc Fe
  workflow, TB2J-style exchange.out writing, and existing DMFT exchange
  regression tests. Revalidated on 2026-05-12 after adding first-class
  coefficient/channel/operator metadata attributes and roundtrip tests.
  Revalidated on 2026-05-16 after adding optional `efermi_spin(nspin)` storage,
  runtime reconstruction, GPAW export, VASP XML import, and focused regression
  tests.
validation_test: "tests/tests/test_projector_green.py"
successful_usage_count: 6
last_used_successfully: 2026-05-16T00:00:00
usage_stale: false
related_files:
  - "TB2J/TB2J/magnon/eigenstates.py"
  - "TB2J/TB2J/green.py"
  - "TB2J/TB2J/exchange.py"
  - "TB2J/TB2J/projector_green.py"
  - "tests/tests/test_projector_green.py"
related_functions:
  - "MagnonEigenstateData.save_netcdf"
  - "MagnonEigenstateData.load_netcdf"
  - "TBGreen.get_Gk"
  - "TBGreen.get_GR"
  - "ProjectorGreenData.save_netcdf"
  - "ProjectorGreenData.load_netcdf"
  - "ProjectorGreen.get_Gk_all"
  - "ProjectorGreen.get_GR"
  - "validate_green_backend"
  - "projector_exchange_trace"
  - "project_potential_to_hij"
  - "pack_site_hij"
  - "compute_projector_exchange_jdict"
  - "write_projector_exchange_out"
tags: [netcdf, schema, green-function, projectors, plane-wave, paw]
project: TB2J
status: draft
validated_by: automatic
validation_date: 2026-05-16T00:00:00
links_to: ["notation", "paw_projector_greens_function", "magnon_eigenstate_file_schema"]
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "projector_greens_netcdf_schema.md display math requires one MathDoc marker per equation"
---

# Projector Green Function NetCDF Schema


## Overview

TB2J should use a code-agnostic NetCDF4 schema for storing projector-based electronic Green functions and the related quantities needed for magnetic-force-theorem exchange calculations. The schema should not be GPAW-specific and should not assume PAW augmentation. It should support PAW projector overlaps, norm-conserving plane-wave projectors, pseudopotential beta projectors, pseudo-atomic-orbital projections, and future projector families as long as each code can provide coefficients

$$
C^{p}_{n\mathbf{k}\sigma} = \langle p | \psi_{n\mathbf{k}\sigma}\rangle.
$$

The v1 core design stores the compact spectral ingredients: eigenvalues, occupations, full-BZ k-points, k-point weights, projector metadata, spin-resolved projector Hamiltonian/potential matrices `H_ij=<p_i|H|p_j>` stored as `hij`, and projector coefficients. From those data, TB2J can reconstruct

$$
G^{pq}_{\sigma}(\mathbf{k}, E) = \sum_n
\frac{C^{p *}_{n\mathbf{k}\sigma} C^q_{n\mathbf{k}\sigma}}
{E + E_{F,\sigma} - \epsilon_{n\mathbf{k}\sigma}}.
$$

Precomputed $G(\mathbf{k},E)$ and $G(\mathbf{R},E)$ are intentionally not part of the v1 storage subset. They are runtime-derived arrays so a single file can be reused for arbitrary energy integration points.

The implemented schema supports an optional `/bands/efermi_spin(nspin)` array for collinear calculations with separate spin-channel Fermi energies. If `efermi_spin` is present, `ProjectorGreen` uses `efermi_spin[ispin]` in the denominator. If it is absent, all spin channels use scalar `efermi`. `ProjectorGreenData` stores scalar `efermi` as the mean of `efermi_spin` when the spin-resolved array is provided, preserving a fallback value for legacy scalar consumers.

## Design Principles

- Use NetCDF4 groups so the same file can store metadata, projector definitions, spectral ingredients, optional Green functions, and optional exchange outputs without name collisions.
- Use one global projector axis `nproj` instead of ragged per-atom arrays. Per-projector metadata maps each projector to a site, atom, angular momentum, radial channel, species, projector family, and code-specific label.
- Store all complex arrays with a final dimension `complex = 2`, where index `0` is real and index `1` is imaginary. This follows the existing TB2J magnon NetCDF convention.
- Make `netCDF4` optional in TB2J, with clear import errors when users request NetCDF functionality without the dependency.
- Separate source-code-specific raw data from TB2J-normalized common arrays. Code-specific extras belong in `/source/extras` or per-code attributes, not in the core arrays.
- Treat Green functions as derived data unless explicitly requested. Projector coefficients and eigenvalues are usually smaller and more reusable.

## Required Global Attributes

The root group should contain these attributes:

| Attribute | Example | Meaning |
|-----------|---------|---------|
| `schema_name` | `tb2j.projector_green` | Schema identifier |
| `schema_version` | `1.0` | Version for parser compatibility |
| `creator` | `TB2J` or `GPAW` | Program that wrote the file |
| `source_code` | `gpaw`, `quantum_espresso`, `abinit`, `vasp`, `siesta`, `unknown` | Electronic-structure source |
| `projector_basis_type` | `paw`, `norm_conserving`, `uspp`, `pseudo_atomic_orbital`, `custom` | Projection basis family |
| `spin_mode` | `collinear`, `noncollinear`, `spinor` | Spin representation |
| `kpoint_convention` | `fractional_reciprocal` | K-point coordinate convention |
| `r_lattice_convention` | `integer_lattice_vector` | R-point convention for Fourier-transformed Green functions |
| `energy_zero` | `fermi` or `absolute` | Meaning of energy-grid values |
| `complex_component` | `["real", "imag"]` | Complex encoding convention |
| `units_json` | JSON string | Units for arrays |
| `metadata_json` | JSON string | Miscellaneous structured metadata |

The default energy convention should be explicit. TB2J currently often evaluates denominators as `E + E_F - eps`; a portable file should record whether stored energy-grid values are relative to the Fermi level or absolute energies.

## Dimensions

The root or relevant groups should define these dimensions as needed:

| Dimension | Meaning |
|-----------|---------|
| `three` | Cartesian/fractional coordinate length 3 |
| `complex` | Real/imag component length 2 |
| `nspin` | Number of spin channels for collinear data, usually 1 or 2 |
| `nspinor` | Spinor dimension, usually 2 for noncollinear spinor wave functions |
| `nkpt` | Number of full-BZ k-points |
| `nband` | Number of Kohn-Sham bands included |
| `nproj` | Number of projector channels in the common projector basis |
| `nsite` | Number of magnetic or local sites |
| `natom` | Number of atoms in the structure |
| `nenergy` | Number of real or complex energy points for Green functions |
| `nR` | Number of lattice vectors used for real-space Green functions |
| `nq` | Number of q-points for exchange outputs |
| `ncart` | Cartesian tensor dimension 3 |

If different spins have different band counts, the writer should either pad to a common `nband` with a `band_mask` variable or write separate spin groups. The preferred first version is a common `nband` with `band_mask` because it keeps the schema simple.

## Core Groups

### `/structure`

This group stores code-independent structural data.

| Variable | Shape | Units | Meaning |
|----------|-------|-------|---------|
| `cell` | `(three, three)` | Angstrom | Lattice vectors as rows or columns, recorded by `cell_convention` attribute |
| `positions` | `(natom, three)` | Angstrom or fractional | Atomic positions, recorded by `position_convention` |
| `atomic_numbers` | `(natom,)` | dimensionless | Atomic numbers |
| `atom_site` | `(natom,)` | dimensionless | Site index for each atom, or `-1` if not a magnetic/local site |
| `site_positions` | `(nsite, three)` | Angstrom or fractional | Site centers used by TB2J |
| `site_atom` | `(nsite,)` | dimensionless | Representative atom index for each site, or `-1` |

Strings such as chemical symbols should be stored either as NetCDF string variables or inside `metadata_json`, depending on backend portability.

### `/kpoints`

This group stores the full-BZ integration mesh.

| Variable | Shape | Meaning |
|----------|-------|---------|
| `kpoints` | `(nkpt, three)` | Full-BZ scaled k-points |
| `weights` | `(nkpt,)` | Integration weights; should sum to 1 unless `weight_normalization` says otherwise |
| `bz_to_ibz` | `(nkpt,)`, optional | Source IBZ index for each full-BZ k-point |
| `symmetry_operation` | `(nkpt,)`, optional | Symmetry operation used to unfold the k-point |

The first schema version should require full-BZ k-points for Green-function files intended for TB2J exchange. IBZ data can be stored as source metadata, but TB2J should not need to reapply source-code symmetries to read the common representation.

### `/bands`

This group stores spectral data.

| Variable | Shape | Units | Meaning |
|----------|-------|-------|---------|
| `eigenvalues` | `(nspin, nkpt, nband)` or `(nkpt, nband)` | eV | Kohn-Sham eigenvalues |
| `occupations` | same as `eigenvalues` | electrons or occupation fraction | Occupations |
| `band_mask` | same as `eigenvalues`, optional | boolean | Valid bands when padding is used |
| `fermi_energy` | scalar | eV | Fermi level in source-code absolute energy convention |
| `efermi_spin` | `(nspin,)`, optional | eV | Spin-channel Fermi energies for Green-function reconstruction |

For spinor noncollinear data without separate spin channels, `eigenvalues` should be `(nkpt, nband)` and `spin_mode = spinor`. Spinor character is then in the projector coefficients and operators, not in duplicate spin eigenvalue arrays.

### `/projectors`

This group defines the common local projector axis.

| Variable | Shape | Meaning |
|----------|-------|---------|
| `coefficients` | `(nspin, nkpt, nband, nproj, complex)` or `(nkpt, nband, nproj, nspinor, complex)` | Projector coefficients $C^p_{nk\sigma}$ |
| `projector_site` | `(nproj,)` | Site index for each projector |
| `projector_atom` | `(nproj,)` | Atom index for each projector, or `-1` |
| `projector_l` | `(nproj,)` | Angular momentum, or `-1` if not applicable |
| `projector_m` | `(nproj,)` | Magnetic/angular component index, or `-999` if not applicable |
| `projector_radial` | `(nproj,)` | Radial/projector-channel index, or `-1` |
| `projector_family` | `(nproj,)` | Encoded family ID: PAW, beta, pseudo-atomic, custom |
| `projector_label` | `(nproj,)` | Human-readable label if NetCDF string support is used |
| `overlap_metric` | `(nproj, nproj, complex)`, optional | Projector-basis overlap or metric if not identity |

For PAW, `coefficients` are normally $\langle \tilde{p}_i | \tilde{\psi}_{nk}\rangle$. For norm-conserving plane-wave projector workflows, `coefficients` may be $\langle p_i | \psi_{nk}\rangle$ for pseudopotential beta projectors, pseudo-atomic orbitals, or user-defined localized projectors. The schema should record `projector_basis_type` and `projector_normalization` so users know whether the metric is orthonormal, dual, PAW-like, or custom.

The implemented v1 schema also records optional `/projectors` attributes for
projector-channel provenance:

- `coefficient_source`: source-code object or formula used for `coefficients`.
- `coefficient_projector`: local object used in the overlap, such as
  `dual_paw_projector`.
- `channel_interpretation`: local interpretation of the channel index for
  matrices and reporting, such as `paw_partial_wave_channel`.
- `population_metric`: population/moment contraction convention, such as GPAW
  `N0_p` packed-density contraction.

`/projectors/overlap_metric` carries a `definition` attribute, and
`/operators/hij` carries an `operator_basis` attribute. These additions avoid
overloading the same channel index when spectral coefficients are dual-projector
overlaps but the local operator is a native PAW projector Hamiltonian, pseudo
partial-wave matrix, or all-electron corrected matrix.

### `/operators`

This group stores local operators in projector space. All variables are optional except metadata describing what was written.

| Variable | Shape | Units | Meaning |
|----------|-------|-------|---------|
| `density_matrix` | `(nspin, nsite, nproj_site_max, nproj_site_max, complex)` or global sparse form | dimensionless | Site-local projected density matrix |
| `local_exchange` | `(nsite, nproj_site_max, nproj_site_max, complex)` or global sparse form | eV | Local exchange splitting or exchange field used in MFT trace |
| `local_exchange_spinor` | `(nsite, nspinor, nspinor, nproj_site_max, nproj_site_max, complex)`, optional | eV | Spinor local exchange operator |
| `hij` | `(nspin, nsite, nproj_site_max, nproj_site_max, complex)` | eV | Spin-resolved projector Hamiltonian/potential matrix `<p_i|H|p_j>` |
| `site_pair_energy` | optional | eV | Transition-space site pair energy if stored rather than projector-space operator |

Because each site can have a different number of projectors, two encodings are possible. The preferred portable encoding for dense site-local matrices is padded site blocks with `site_nproj` and `site_projector_indices`. A more compact later version can add a sparse COO encoding with `row`, `col`, and `value` arrays.

The variable `hij` must have an attribute `definition` and units. It is the spin-resolved projector Hamiltonian/potential matrix `<p_i|H|p_j>` or `<p_i|V|p_j>`, not a density or density matrix. TB2J may use only the spin-dependent part `H_ij^up - H_ij^down` for the first exchange-like trace and disregard the spin-independent part.

For PAW files, `hij` may be exported from a native precomputed projector Hamiltonian matrix such as GPAW `dH_asp`/`dH_asii` or a code convention called `d_ij`. For non-PAW projector files, the source-code exporter must compute `hij` by projecting the relevant potential/Hamiltonian onto the selected projectors before writing the portable file.

### `/greens_k`

This optional group stores precomputed reciprocal-space Green functions.

| Variable | Shape | Units | Meaning |
|----------|-------|-------|---------|
| `energy` | `(nenergy,)` | eV | Energy grid, relative or absolute according to `energy_zero` |
| `green` | `(nenergy, nspin, nkpt, nproj, nproj, complex)` or spinor variant | 1/eV | Projector-space $G(k,E)$ |
| `self_energy` | optional | eV | Embedded self-energy if used in Dyson equation |
| `broadening` | `(nenergy,)`, optional | eV | Imaginary broadening used for real-axis Green functions |

This array can be very large. Writers should only include it when users request precomputed Green functions. For most workflows, `/bands` plus `/projectors/coefficients` is sufficient and more portable.

### `/greens_R`

This optional group stores Fourier-transformed real-space Green functions.

| Variable | Shape | Units | Meaning |
|----------|-------|-------|---------|
| `R_vectors` | `(nR, three)` | integer lattice vectors | Lattice vectors used in Fourier transform |
| `green` | `(nenergy, nspin, nR, nproj, nproj, complex)` or block/sparse variant | 1/eV | Projector-space $G(R,E)$ |
| `phase_convention` | attribute | text | Should match TB2J `exp(-2*pi*i*k.R)` by default |

If `green` is stored globally over `nproj`, off-site blocks are available directly. If storage size is an issue, a later extension can store only selected `(R, site_i, site_j)` blocks.

### `/exchange`

This optional group stores quantities derived from the Green functions.

| Variable | Shape | Units | Meaning |
|----------|-------|-------|---------|
| `A_ijR` | implementation-defined | eV or dimensionless before integration | TB2J exchange integrand/tensor before conversion |
| `J_R` | `(nR, nsite, nsite)` or tensor variant | eV or meV | Real-space exchange |
| `J_q` | `(nq, nsite, nsite)` or tensor variant | eV or meV | Reciprocal-space exchange |
| `DMI_R` | `(nR, nsite, nsite, ncart)`, optional | eV or meV | Dzyaloshinskii-Moriya vectors |
| `Jani_R` | `(nR, nsite, nsite, ncart, ncart)`, optional | eV or meV | Anisotropic exchange tensor |

The exchange group should always include attributes recording the method, for example `method = green_trace`, `local_operator = local_exchange`, `energy_integration = contour`, and `normalization`.

The first real workflow writes exchange results through TB2J's existing text output rather than storing `/exchange` in the NetCDF file. `examples/projector_green/gpaw_bcc_fe_projector_green.py` computes a `SpinIO`-compatible `exchange_Jdict` from the controlled projector trace and writes `TB2J_results/exchange.out`. This keeps v1 NetCDF spectral-only while allowing users to inspect projector-trace results in the familiar TB2J output format.

## Spinor Variant

For noncollinear or SOC calculations, the preferred coefficient shape is

$$
C_{n\mathbf{k},p,s} = \langle p,s | \psi_{n\mathbf{k}}\rangle,
$$

stored as `(nkpt, nband, nproj, nspinor, complex)`. A spinor Green function can then be stored either with explicit spinor axes,

$$
G_{p s, q s'}(\mathbf{k},E),
$$

or flattened into a combined `nproj_spinor = nproj * nspinor` axis. The first schema version should prefer explicit spinor axes in the spectral coefficients and allow flattened Green-function arrays for compatibility with existing TB2J spinor code.

## Norm-Conserving Plane-Wave Support

For norm-conserving plane-wave calculations, there is no PAW augmentation sphere and no all-electron/pseudo partial-wave correction. The same schema still applies if the code supplies projector coefficients. Examples include beta projectors from a norm-conserving pseudopotential, pseudo-atomic orbital projectors used for projected DOS, or localized trial orbitals used for downfolding.

In this case, set `projector_basis_type = norm_conserving` or `pseudo_atomic_orbital`, omit PAW-only variables such as `dO_ii` and `Delta_iiL`, and set `operator_correction = none` in `/operators` metadata. The Green function is then a projected pseudo-wavefunction Green function. Physical quality depends on projector completeness and normalization, so the file must record `projector_normalization` and include `overlap_metric` when the projectors are non-orthogonal.

## PAW-Specific Extension

PAW-specific data should live in a `/paw` group so non-PAW readers can ignore it.

| Variable | Shape | Meaning |
|----------|-------|---------|
| `dO` | `(nproj, nproj, complex)` or site blocks | PAW overlap correction matrix |
| `Delta_iiL` | site blocks | Compensation-charge correction tensor |
| `partial_wave_l` | `(nproj,)` | PAW partial-wave angular momentum |
| `partial_wave_radial` | `(nproj,)` | PAW radial function index |
| `augmentation_radius` | `(nsite,)` or `(natom,)` | PAW/site augmentation radius if known |

The common `/projectors/coefficients` array should still contain the PAW projector overlaps. PAW correction data are optional metadata for reconstructing all-electron operators or validating against a PAW source code.

## Reader Strategy in TB2J

TB2J should implement a reader that first loads `/bands` and `/projectors`, constructs an in-memory projector Green backend, and only uses `/greens_k` or `/greens_R` if requested or if spectral ingredients are missing. The reader should validate:

- `schema_name == "tb2j.projector_green"`.
- Complex arrays use final dimension size 2.
- K-point weights exist and are normalized or explicitly marked otherwise.
- Projector-to-site mapping covers every projector used in magnetic sites.
- Energy convention and phase convention are explicit.
- `hij` variables have a `definition` attribute identifying projector Hamiltonian/potential semantics.

This reader can serve GPAW, Quantum ESPRESSO, ABINIT, and other plane-wave codes as long as a converter writes the common arrays. Code-specific converter responsibility is limited to producing full-BZ k-points, eigenvalues, occupations, projector coefficients, and local operators if available.

## Storage Tradeoffs

The spectral representation scales as `nspin * nkpt * nband * nproj`, while precomputed Green functions scale as `nenergy * nspin * nkpt * nproj^2` or `nenergy * nspin * nR * nproj^2`. The file should therefore make precomputed Green functions optional. For large calculations, the recommended storage levels are:

1. `ingredients`: store `/structure`, `/kpoints`, `/bands`, `/projectors`, and optional `/operators` only.
2. `greens_k`: additionally store `/greens_k/green` for a chosen energy mesh.
3. `greens_R`: additionally store selected real-space Green-function blocks needed for exchange.
4. `exchange`: store only final exchange quantities and enough metadata to reproduce the calculation.

## Linked Concepts

- [paw_projector_greens_function](paw_projector_greens_function.md): Research note motivating projector Green functions for GPAW and PAW.
- [magnon_eigenstate_file_schema](magnon_eigenstate_file_schema.md): Existing TB2J NetCDF convention for complex arrays and optional `netCDF4` dependency.
- [notation](notation.md): Shared symbols and array notation.
