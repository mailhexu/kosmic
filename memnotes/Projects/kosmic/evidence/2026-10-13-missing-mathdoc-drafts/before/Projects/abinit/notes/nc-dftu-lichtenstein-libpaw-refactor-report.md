---
artifact_role: knowledge
audience: both
confidence: 0.86
created: 2026-05-06
last_validated: 2026-05-06
validation_procedure: "Inspected ABINIT source: src/65_paw/m_paw_correlations.F90, shared/libpaw/src/m_pawdij.F90, src/66_nc_dftu/m_nc_dftu.F90, PAW input documentation, and existing NC DFT+U MemNotes."
project: abinit
status: stable
validated_by: automatic
tags: [nc_dftu, paw_u, lichtenstein, liechtenstein, libpaw, refactor]
type: Project Knowledge
---

# NC DFT+U Lichtenstein LibPAW Refactor Report


## Overview

ABINIT already has norm-conserving DFT+U for the Dudarev effective interaction. This report uses "Lichtenstein" and "Liechtenstein" as spelling variants for the same rotationally invariant DFT+U formulation cited in ABINIT documentation as Liechtenstein et al. The current NC implementation computes pseudo-atomic-orbital occupations, then uses

$$
E_U = \frac{1}{2} U_{\mathrm{eff}} \sum_\sigma \mathrm{Tr}\left[n^\sigma - n^\sigma n^\sigma\right]
$$

and

$$
V_{ij}^\sigma = U_{\mathrm{eff}}\left(\frac{1}{2}\delta_{ij} - n_{ji}^\sigma\right)
$$

in `src/66_nc_dftu/m_nc_dftu.F90::compute_dftu_energy_nc` and `compute_dftu_vmatrix_nc`. This is compatible with the already validated PAO-basis NC DFT+U Hamiltonian, force, and stress paths, but it does not expose the full rotationally invariant Lichtenstein form or PAW's double-counting options.

The PAW implementation contains the desired Lichtenstein/FLL/AMF logic, but it is not yet organized as a reusable orbital-space library. The best implementation path is to extract the PAW+U orbital kernels into a new logically separated LIBPAW module, then make both PAW and NC call that module from thin representation-specific wrappers.

## Existing Code Map

| Responsibility                                                                                 | Current Location                                 | Reuse Status                                                                                                                        |
| ---------------------------------------------------------------------------------------------- | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| Build four-index interaction tensor `vee` from `U`, `J`, Slater ratios, and Gaunt coefficients | `src/65_paw/m_paw_correlations.F90::calc_vee`    | Reusable formula, but currently in PAW source and takes `pawang_type`                                                               |
| Compute Lichtenstein interaction energy and double-counting energy terms                       | `src/65_paw/m_paw_correlations.F90::pawuenergy`  | Reusable orbital math, but takes `pawtab_type` and PAW print/error conventions                                                      |
| Compute matching Hubbard potential matrix                                                      | `shared/libpaw/src/m_pawdij.F90::pawpupot`       | Closest reusable kernel, but takes `pawtab_type` and has PAW-specific diagnostics                                                   |
| Build PAW occupations                                                                          | `src/65_paw/m_paw_correlations.F90::setnoccmmp`  | Not reusable for NC because it contracts PAW augmentation densities and PAW radial overlaps                                         |
| PAW `dijU` path                                                                                | `shared/libpaw/src/m_pawdij.F90::pawdiju_euijkl` | Not directly reusable for NC because it depends on `pawrhoij_type`, `pawtab%indklmn`, `pawrhoij%rhoijselect`, and PAW pair indexing |
| NC occupations, Dudarev energy/potential, forces, stress                                       | `src/66_nc_dftu/m_nc_dftu.F90`                   | Current NC entry point; should become a caller of generic Hubbard energy/potential kernels                                          |

## PAW Formulas Worth Extracting

The PAW code implements the full rotationally invariant interaction by looping over orbital indices and the screened Coulomb tensor:

$$
E_{ee} = \frac{1}{2}\sum_{m_1m_2m_3m_4\sigma}
\left[
n_{m_1m_2}^{\sigma} n_{m_3m_4}^{-\sigma} V_{m_1m_3m_2m_4}
+ n_{m_1m_2}^{\sigma} n_{m_3m_4}^{\sigma}
\left(V_{m_1m_3m_2m_4} - V_{m_1m_3m_4m_2}\right)
\right]
$$

For collinear spins this is implemented in `pawuenergy` around its four nested `m` loops. The matching potential is implemented in `pawpupot` with the same direct and exchange contractions. Non-collinear spin support is present in both routines as extra spin-density channels for `ndij == 4`/`nspden == 4`.

PAW double-counting options include:

| `usepawu` Option | Meaning In PAW |
|------------------|----------------|
| `1` | Full localized limit (FLL) double counting with spin-polarized exchange-correlation |
| `2` | Around mean field (AMF) double counting; not valid for `nspinor=2` in documentation |
| `3` | Alternative AMF-style occupancy subtraction used internally/tests |
| `4` | FLL double counting but exchange-correlation is not spin polarized |
| `10`, `14` | DMFT modes using related double-counting infrastructure, not normal DFT+U modes |

The NC implementation should initially target the normal DFT+U options `1`, `2`, and possibly `4`. Options `10` and `14` are DMFT-specific and should not be exposed through NC DFT+U unless a later NC+DMFT feature exists.

## Proposed Shared Kernel Split

Create a new shared Hubbard module under `shared/libpaw/src`, for example `shared/libpaw/src/m_hubbard_orbital.F90`. The directory location is only a build and distribution choice: the module must be logically independent of LIBPAW and PAW. Its public names and arguments should not contain `paw`, should not take PAW/LIBPAW derived types, and should not depend on `pawtab_type`, `pawang_type`, `paw_ij_type`, `pawrhoij_type`, or ABINIT dataset types.

LIBPAW and ABINIT PAW code should call this independent module through thin PAW wrappers. NC DFT+U should call the same independent module through NC wrappers. This keeps the orbital Hubbard math shared without making NC code conceptually depend on PAW.

Suggested public API:

```fortran
subroutine hubbard_build_interaction(l_hub, u_hub, j_hub, f4of2, f6of2, &
                                     gntselect, realgnt, interaction_tensor, prtvol)

subroutine hubbard_energy_dc(occ_matrix, occ_trace, interaction_tensor, l_hub, u_hub, j_hub, &
                             dc_mode, spin_interaction_mode, e_interaction, e_dc, e_dcdc, &
                             e_minus_dc, e_band_correction)

subroutine hubbard_potential(occ_matrix, occ_trace, interaction_tensor, l_hub, u_hub, j_hub, &
                             dc_mode, spin_interaction_mode, potential_matrix)
```

Where:

| Argument                         | Meaning                                                                                          |
| -------------------------------- | ------------------------------------------------------------------------------------------------ |
| `occ_matrix(cplex,norb,norb,nspin)` | Occupation matrix in the shared Hubbard convention |
| `occ_trace(nspin)` | Trace of occupations per spin channel, or charge/magnetization components for non-collinear spin |
| `interaction_tensor(norb,norb,norb,norb)` | Screened Coulomb tensor |
| `l_hub` | Correlated angular momentum |
| `u_hub`, `j_hub` | Hubbard `U` and Hund `J` |
| `dc_mode` | Generic double-counting mode, with wrapper-level mapping from PAW `usepawu` or NC input options |
| `spin_interaction_mode` | Generic non-collinear interaction convention, with wrapper-level mapping from PAW `option_interaction_pawu` |
| `gntselect`, `realgnt` | Plain Gaunt coefficient lookup arrays; PAW wrappers can pass these from `pawang`, NC or tests can build/pass their own |
| `potential_matrix(cplex,norb,norb,nspin)` | Hubbard potential in the same orbital basis as `occ_matrix` |

The new module should define its own generic integer parameters for double-counting modes, for example `HUBBARD_DC_FLL`, `HUBBARD_DC_AMF`, and `HUBBARD_DC_FLL_NOSPIN_XC`. PAW-specific values such as `usepawu=1`, `2`, or `4` should be translated in PAW wrapper code, not inside the independent module.

## PAW Migration Plan

1. Move the body of `calc_vee` into `hubbard_build_interaction`; keep `m_paw_correlations::calc_vee` as a thin PAW wrapper at first.
2. Move the core of `pawuenergy` into `hubbard_energy_dc`; keep the old `pawuenergy` API and have it translate PAW names/options into generic names/options before calling the shared routine.
3. Move the core of `pawpupot` into `hubbard_potential`; keep the old `pawpupot` API and have it call the generic routine.
4. Keep PAW occupation construction in `setnoccmmp` unchanged because NC occupations are not PAW augmentation occupations.
5. Keep `pawdiju_euijkl` unchanged for PAW algorithm 2 because it is tightly coupled to PAW `rhoij` and pair indexing.

This preserves PAW behavior while making the orbital energy and potential code callable from NC DFT+U without importing PAW concepts into the shared API.

## NC Integration Plan

NC DFT+U should keep its PAO-specific occupation, Hamiltonian application, force, and stress code. Only the map from occupation matrix to Hubbard energy/potential should be generalized.

Recommended NC changes:

1. Extend NC DFT+U input data to carry a generic double-counting option, for example `dftu_dc_nc`, whose values map to shared constants such as `HUBBARD_DC_FLL` and `HUBBARD_DC_AMF`. Avoid exposing PAW option names in the NC-facing API.
2. Store or build `interaction_tensor` for each correlated type. For Lichtenstein mode this requires `U`, `J`, correlated angular momentum, and Slater ratios. The current NC inputs `dftu_l`, `dftu_u`, and `dftu_j` are enough for default `p`, `d`, and `f` Slater ratios, but exposing generic Slater-ratio inputs should be considered for parity with PAW.
3. Convert NC `occ_matrix(norb,norb,natom,nsppol)` into the generic `occ_matrix(cplex,norb,norb,nspin)` layout expected by the shared kernel. For current collinear NC DFT+U, `cplex=1` and `nspin=nsppol`.
4. Call `hubbard_energy_dc` and `hubbard_potential` instead of `compute_dftu_energy_nc` and `compute_dftu_vmatrix_nc` when Lichtenstein/FLL/AMF mode is selected.
5. Continue storing ABINIT total-energy correction as the band-sum compatible term. Current NC code correctly uses `energies%e_dftu_nc = E_U - Tr[V_U n]`; the generic routine must return enough pieces to keep this accounting explicit.
6. Keep `forstrnps_dftu` as the NC force/stress path. It should contract PAO derivatives with the new `V_U` matrix exactly as it currently does with Dudarev `V_U`.

## Energy Accounting Caution

The PAW routine `pawuenergy` returns two accumulated quantities:

$$
\mathrm{edftumdc} \leftarrow E_{ee} - E_{dc}
$$

and

$$
\mathrm{edftumdcdc} \leftarrow -E_{ee} - E_{dcdc}
$$

NC DFT+U already found that total-energy consistency requires the stored total-energy correction to account for the fact that the Hubbard Hamiltonian contributes to the eigenvalue sum. For Dudarev, the NC code explicitly computes

$$
E_{\mathrm{total\ correction}} = E_U - \mathrm{Tr}[V_U n]
$$

The Lichtenstein implementation must preserve this convention. Do not blindly add PAW's printed `edftumdc` quantity to the NC total energy without checking the band-energy decomposition.

## Non-Collinear And DFPT Implications

The proposed split is useful for non-collinear spin because PAW already has non-collinear interaction and double-counting branches in `pawuenergy` and `pawpupot`. NC non-collinear support would still need separate work to build spinor PAO occupation matrices and apply a spinor Hubbard Hamiltonian.

The proposed split is useful for DFPT because first-order responses can reuse the same derivative of energy with respect to occupation, i.e. the Hubbard potential, but the first-order occupation construction remains representation-specific. PAW DFPT currently uses `pawdiju_euijkl` and PAW `pawrhoij` perturbations. NC DFPT should instead compute first-order PAO occupation matrices and contract them with the generic orbital kernels.

## Risks

| Risk | Mitigation |
|------|------------|
| Matrix orientation mismatch between NC `occ_matrix` and PAW `noccmmp` | Add unit tests comparing Dudarev limit from generic kernel to existing NC `compute_dftu_energy_nc` and `compute_dftu_vmatrix_nc` |
| Total-energy double counting becomes inconsistent with NC band sum | Keep `E_ee`, `E_dc`, `Tr[Vn]`, and total correction separate in the API and tests |
| PAW regression from refactor | Keep old PAW wrapper APIs and bitwise/near-bitwise compare PAW NiO FLL/AMF outputs before and after extraction |
| LIBPAW dependency direction issues | Put generic kernels in `shared/libpaw/src`, not `src/65_paw`, and avoid dependencies on ABINIT-only types |
| Non-collinear conventions differ between PAW and desired NC spinor layout | Defer NC non-collinear activation until collinear parity is validated, but design API dimensions to allow `nspin=4` |

## Validation Matrix

| Stage | Test |
|-------|------|
| Generic kernel unit test | Dudarev spherical limit reproduces current NC energy and potential for random Hermitian collinear occupations |
| PAW wrapper preservation | Existing PAW+U FLL and AMF tests produce unchanged energies and occupancies after wrapper extraction |
| NC collinear FLL | NiO NC DFT+U remains convergent and reproduces current Dudarev behavior when `J` enters only through `U_eff` mode |
| NC Lichtenstein FLL | Compare NC energy/potential against a standalone contraction using the same `vee` and occupation matrix |
| NC AMF | Validate AMF double-counting trends against PAW formulas and, if possible, QE or literature reference cases |
| Force/stress consistency | Branch-preserving finite differences remain consistent after replacing only the occupation-to-potential kernel |

## Recommended First Implementation Story

The safest first story is not to add new NC user-visible behavior. First extract and test the generic LIBPAW kernels while keeping PAW behavior unchanged. Then add a hidden or developer-only NC path that calls the generic kernel in the Dudarev-equivalent limit and must reproduce the existing NC Dudarev results. Only after that should Lichtenstein/FLL/AMF options be exposed to users.

## Linked Concepts

- [paw-dftu-generic-reuse-map](paw-dftu-generic-reuse-map.md) - Previous map of reusable PAW+U routines.
- [nc_dftu_module](nc_dftu_module.md) - Current NC DFT+U Dudarev implementation.
- [nc-dftu-force-energy-consistency](nc-dftu-force-energy-consistency.md) - NC total-energy, force, and stress consistency constraints.
- `specs/prd-dftu-forces-stress-nc.md` - Existing NC DFT+U force/stress specification.
