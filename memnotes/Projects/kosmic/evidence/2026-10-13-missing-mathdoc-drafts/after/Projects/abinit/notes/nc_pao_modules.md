---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-02-25
last_validated: 2026-04-20
validation_procedure: "Check module files exist in abinit_dev/src/66_ncpao/"
project: abinit
status: draft
validated_by: build_and_test
tags: [nc_pao, dftu, overlap, hamiltonian]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "nc_pao_modules.md display math requires one MathDoc marker per equation"
---

# NC PAO Modules Overview


## Overview
The `m_nc_pao_*` modules provide functionality for Norm-Conserving (NC) pseudo-atomic orbital (PAO) calculations used in DFT+U. These modules compute overlap matrices, Hamiltonian matrices, and occupation matrices for NC pseudopotentials.

## Module Organization

| Module | Purpose | Key Functions |
|--------|---------|--------------|
| `m_nc_pao_types` | Data types and initialization | `nc_pao_hs_type`, `init_nc_overlap`, `free_nc_overlap`, `get_phi_kpg`, `get_nproj_tot` |
| `m_nc_pao_hamiltonian` | Hamiltonian and overlap computation | `compute_pao_hamiltonian_nc`, `compute_pao_hamiltonian_direct_nc`, `compute_all_overlaps_nc` |
| `m_nc_pao_io` | NetCDF I/O | `save_nc_overlap_netcdf` |
| `m_nc_dftu` | DFT+U calculations | `compute_occmatrix_nc`, `compute_dftu_energy_nc`, `symmetrize_nc_occmatrix`, `get/set_nc_dftu_vmatrix` |
| `m_nc_overlap_utils` | Utility functions | `compute_pw_pao_projections`, `rotate_overlap_matrix_nc`, `compute_overlap_realspace` |

**Note:** `m_nc_dftu_hamiltonian` was moved from `66_ncpao/` to `66_wfs/` (2026-04-20) to break a circular dependency. See [dftu-psps-decoupling](dftu-psps-decoupling.md).

## Directory Location
`abinit_dev/src/66_ncpao/` (renamed from `67_ncpao/` on 2026-04-20)

**Important:** The directory was renamed from `67_ncpao` to `66_ncpao` to place it at the same level as `66_nonlocal` and `66_wfs`. However, this creates an alphabetical ordering issue in the build system — `66_ncpao` sorts before `66_nonlocal` and `66_wfs`, causing build failures with parallel make. The build order must be manually patched in `build/src/Makefile` after running `configure`. See [abinit-build-system-directory-dependencies](abinit-build-system-directory-dependencies.md).

## Dependencies
- `defs_basis`, `m_abicore`, `m_errors` - Core ABINIT modules
- `m_splines` - Spline interpolation for PAO radial functions
- `m_nctk`, `netcdf` - NetCDF I/O
- `m_fft`, `m_fftcore` - FFT for real-space transformations
- `m_paw_sphharm` - Spherical harmonics (setsym_ylm)
- `m_geometry` - Metric tensor calculations
- `m_mkffnl`, `m_kg`, `m_initylmg` - Plane wave operations

## Typical Usage Flow

1. Initialize data structure: `call init_nc_overlap(nc_ovl, ...)`
2. Compute overlaps: `call compute_all_overlaps_nc(nc_ovl, ...)`
3. Compute Hamiltonian: `call compute_pao_hamiltonian_nc(nc_ovl, ...)`
4. For DFT+U: `call compute_occmatrix_nc(..., occ_matrix, energy_dftu)`
5. Save results: `call save_nc_overlap_netcdf(nc_ovl, ...)`
6. Clean up: `call free_nc_overlap(nc_ovl)`

## Key Concepts

### Pseudo-Atomic Orbitals (PAO)
The modules work with pseudo-atomic orbitals φ_{nlm}(r) which are the atomic-like basis functions from the NC pseudopotential. Each orbital is characterized by:
- n: Principal quantum number (pseudo)
- l: Angular momentum (0=s, 1=p, 2=d, 3=f)
- m: Magnetic quantum number (-l to +l)

### Overlap Matrix
$$
S_{ij}(k) = ⟨φ_i|φ_j⟩_k = Σ_G φ*_i(k+G) φ_j(k+G)
$$

### Hamiltonian Matrix
H_{ij}(k) = ⟨φ_i|H|φ_j⟩_k computed via spectral representation:
H_{ij}(k) = Σ_n ε_nk ⟨φ_i|ψ_nk⟩⟨ψ_nk|φ_j⟩

## Linked Concepts
- [nc_pao_hs_type](nc_pao_hs_type.md) - Main data structure
- [nc_dftu_module](nc_dftu_module.md) - DFT+U specific routines
- [nc_overlap_utils](nc_overlap_utils.md) - Utility functions
- [nc_pao_io](nc_pao_io.md) - NetCDF output format
