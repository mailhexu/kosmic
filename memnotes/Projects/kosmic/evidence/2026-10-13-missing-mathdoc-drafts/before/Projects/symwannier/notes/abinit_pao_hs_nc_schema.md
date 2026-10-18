---
artifact_role: knowledge
type: reference
audience: both
title: ABINIT *_PAO_HS.nc schema (NC-PAO savetb2j output)
topic: abinit-io
project: symwannier
status: stable
validated_by: code_inspection
created: 2026-07-28
updated: 2026-07-28
related_files:
  - /home/hexu/projects/TB2J_dev/abinit/src/68_pao_hamiltonian/m_nc_pao_io.F90
  - /home/hexu/projects/TB2J_dev/abinit/src/68_pao_hamiltonian/m_nc_pao_hamiltonian.F90
  - /home/hexu/projects/symwannier/data/abinit_cri3/cri3_paoo_PAO_HS.nc
tags: [abinit, savetb2j, nc-pao, netcdf, delta_xc, delta_total, tb2j]
---

# `*_PAO_HS.nc` schema (ABINIT NC-PAO `write_pao_HS_nc` / savetb2j)

Output of `save_nc_overlap_netcdf` (`src/68_pao_hamiltonian/m_nc_pao_io.F90:41-504`), driven by
input flag `write_pao_HS_nc 1` (the NC path; `savetb2j` is the PAW-only v1 path). The CrI3
file `data/abinit_cri3/cri3_paoo_PAO_HS.nc` (60 MB) is an instance. `schema_name =
"abinit.nc_pao_hs"`, `schema_version = 2`.

## Dimensions

`nproj, nkpt_ibz, nkpt_bz (if >0), nsppol, three, complex (=2), natom, ntypat, nband, nrpt (if ngkpt+kpt_bz)`.

## Variables (definition sites in `m_nc_pao_io.F90`)

- **Projector metadata** (182-185): `atom_index[nproj]`, `l_quantum[nproj]`, `m_quantum[nproj]`,
  `n_quantum[nproj]` — n is a per-l counter, not principal quantum number.
- **Structure** (187-190): `atom_positions[three,natom]` (reduced), `atom_types[natom]`,
  `atomic_numbers[ntypat]` (znucl), `primitive_vectors[three,three]` (rprimd, bohr).
- **Bands/k** (191-245): `eigenvalues[nband,nkpt_ibz,nsppol]` (Hartree), `occupations`,
  `istwfk[nkpt_ibz]`, `kpoints_ibz[three,nkpt_ibz]`, `kweights_ibz`, and `_bz_` variants.
- **PAO coefficients** (200-215): `coefficients_ibz_real/imag [nproj,nband,nkpt_ibz,nsppol]`
  = `<psi|phi>` per band. **On-disk dim order is reversed (C vs Fortran)**: netCDF4 reads them
  as `(nsppol, nkpt_ibz, nband, nproj)` — transpose when loading. Verified: abinao's
  `project_all_k` (`<phi|psi>`) matches `coefficients_ibz` to ~1.3e-7 on an O-atom NC-PAO run
  once the dim order + conjugation are handled (story-002).
- **Spin-splitting operators** (218-235) — the exchange-relevant ones:
  - `delta_xc_smooth_real/imag [nproj,nproj]` — `<phi_i | vxc_up − vxc_dn | phi_j>` (Hartree).
  - `delta_U_real/imag [nproj,nproj]` — on-site DFT+U block (zero unless `usedftu_nc==1`).
  - `delta_total_real/imag [nproj,nproj]` — `delta_xc + delta_U`, computed at write time (427-434).
- **Overlap/Hamiltonian** (247-285): `overlap_ibz_real/imag [nproj,nproj,nkpt_ibz]`,
  `hamiltonian_ibz_real/imag [...,nsppol]`, plus decompositions `_kinetic/_local/_nonlocal/_dftu/_direct`.
- **Real-space (Wannier-style)** (287-302, only if `ngkpt`+`kpt_bz`): `rpoints[three,nrpt]`,
  `rpoints_weights`, `overlap_r_real/imag`, `hamiltonian_r_*` `[nproj,nproj,nrpt,nsppol]`.

### Fortran/C axis boundary (validated 2026-07-30)

`save_nc_overlap_netcdf` defines and writes the overlap in Fortran order
`(i,j,k)` without an explicit transpose (`m_nc_pao_io.F90:156-157,245-246`).
The C/NetCDF view is consequently `(k,j,i)`. A Python reader must transpose
the two projector axes before interpreting the matrix as $S_{ij}$:

$$
S_{ij}(k) = \mathrm{raw}[k,j,i].
$$

For the Hermitian overlap, omitting this conversion produces $S^T=S^*$ and
looks exactly like an inter-atom phase-sign error. On the current regenerated
CrI3 file, the corrected overlap agrees with direct full-BZ abinao to
`1.95e-5` max-abs across the ten shared IBZ points; the uncorrected read
differs by `0.604`.

## Key global attributes (304-376)

`complex_storage="split_real_imag_variables"`, `operator_spin_convention="up_minus_down"`,
`operator_units="Hartree"`, `operator_components="delta_xc_smooth,delta_U,delta_total"`,
`delta_total_definition="delta_total=delta_xc_smooth+delta_U"`,
`delta_U_status="zero_when_nc_dftu_inactive_or_nsppol_not_2"`,
`overlap_hermiticity_max_abs_ibz` (computed inline).

## What is NOT in this file

No FFT grid, no `ngfftf`, no spin-resolved V_xc(r) on the grid, no density. Only the
PAO-projected matrices. For the raw V_xc grid use `prtvxc` → `_VXC` ([[abinit_vxc_netcdf_dump]]).

## Fortran source anchors (for the Python port)

| quantity | routine | location |
|----------|---------|----------|
| `<phi_i|vxc_up−vxc_dn|phi_j>` | `compute_delta_xc_nc` | `m_nc_pao_hamiltonian.F90:667-847` |
| `<psi_nk|phi_i>` (coefficients) | `compute_pao_hamiltonian_nc` | `m_nc_pao_hamiltonian.F90:61-287` |
| `S_ij=<phi_i|phi_j>` | `compute_all_overlaps_nc` | `m_nc_pao_hamiltonian.F90:490-664` |
| PAO basis/ordering/radial | `init_nc_pao_metadata`, `get_phi_kpg` | `m_nc_pao_types.F90:135-190, 379-409` |
| `delta_U` | `compute_delta_u_nc` | `m_nc_pao_hamiltonian.F90:850-919` |

`phi_i(k+G) = (4π/√Ω) · tphi_l(|k+G|) · Y_lm(k+G) · exp[−i2π(k+G)·τ]`. The V_xc projection
bridges G-space phi and real-space V via `fourwf(option=2)` (G→R, ×V, R→G). Two bug fixes in
this fork are marked with `ponytail:` comments at `m_nc_pao_hamiltonian.F90:730-734, 801-804`.

## Consumers

- TB2J `interfaces/abinit_savetb2j.py:gen_exchange_abinit_nc_pao(..., operator_component="delta_total")`.
- `symwannier/data/abinit_cri3/{run_tb2j.py, plot_delta_xc_smooth.py}` (scratch drivers).
- `symwannier/analysis/abinit.py` (Cr-d Δ reader for the cross-method scalar; fixture-gated).
