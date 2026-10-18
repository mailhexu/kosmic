---
artifact_role: knowledge
audience: both
created: 2026-06-15
updated: 2026-06-15
status: draft
tags: [nc-dftu, dfpt, electric-field, ddk, sternheimer, story-447]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "nc-dftu-electric-fixed-projector-source.md display math requires one MathDoc marker per equation"
---

# NC DFT+U Fixed-Projector Electric-Field Source

Story 447 activates the self-consistent NC DFT+U electric-field source for Gamma electric-field/DDK perturbations.

Changed source files:

- `abinit_dev/src/66_wfs/m_nc_dftu_hamiltonian.F90`
- `abinit_dev/src/72_response/m_dfpt_cgwf.F90`
- `abinit_dev/src/72_response/m_dfpt_vtorho.F90`

The new source routine is:

- `m_nc_dftu_hamiltonian.F90::apply_dftu_h1_electric_nc`

It is electric-specific and returns unless `ipert == natom + 2`. It also requires active NC DFT+U response data with allocated static `V` and first-order `V1` matrices.

For the electric source, the routine uses fixed PAO projectors only:

$$
H_U^{E}\psi^0 = \sum_{I,m,m'} |\phi_{Im}\rangle\, V^{E}_{U,Im m'}\, \langle \phi_{Im'} | \psi^0 \rangle
$$

Implementation details:

- builds fixed `phi0_kpg_tot` and `phi1_kpg_tot` projectors,
- computes the fixed-projector ground-state projection `proj=<phi0|psi0>`,
- forms `ctemp_v1 = V1 * proj`,
- adds `phi1_kpg_tot * ctemp_v1` into the Sternheimer source array `gh1c`.

The electric source routine intentionally does **not** allocate or use displacement-only terms:

- no `dphi0_kpg_tot` / `dphi1_kpg_tot`,
- no `dproj`,
- no `V0*dproj`,
- no `dphi*V0`,
- no call to `build_nc_dftu_displacement_dphi_gamma`.

The self-consistent Sternheimer insertion point is in:

- `m_dfpt_cgwf.F90::dfpt_cgwf`

The call is placed immediately after `getgh1c(...)` and before overlap subtraction / `getdc1`. The existing atomic-displacement source hook is now explicitly atomic-only, while the electric branch is separate:

```fortran
if (gs_hamkq%usepaw == 0 .and. associated(gs_hamkq%nc_dftu) .and. ipert == natom + 2) then
  call apply_dftu_h1_electric_nc(..., gh1c, ..., ipert)
end if
```

Story 447 also updates `m_dfpt_vtorho.F90` so `gs_hamkq%nc_dftu` is associated with the computed NC DFT+U response for either atomic perturbations or supported Gamma electric perturbations. Without this association, the electric source branch in `dfpt_cgwf` would compile but never activate.

Scope boundaries preserved:

- `m_dfpt_nstwf.F90` remains unchanged.
- DDB/dielectric/BEC paths remain unchanged for Stories 448 and 449.
- Existing atomic displacement source behavior remains separated from the electric source path.
- Test fixtures remain deferred per user instruction and Story 450 validation ownership.

Validation:

- `make` in `abinit_dev/build` passed after the implementation and after the activation-association fix.
- Fortran LSP diagnostics were unavailable because no `.F90` LSP server is configured.
- Five-lane post-implementation review passed after QA clarified that unrelated dirty test/source files were pre-existing and not Story 447 changes.
