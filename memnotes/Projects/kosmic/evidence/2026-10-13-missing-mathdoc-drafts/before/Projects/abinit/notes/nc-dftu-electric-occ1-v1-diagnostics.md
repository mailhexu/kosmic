---
artifact_role: knowledge
audience: both
created: 2026-06-15
updated: 2026-06-15
status: stable
tags: [nc-dftu, dfpt, electric-field, ddk, story-446]
type: Project Knowledge
---

# NC DFT+U Electric-Field `occ1^E` And `V_U^E` Diagnostics

Story 446 added the fixed-projector electric-field response path for NC DFT+U diagnostics.

Changed source files:

- `abinit_dev/src/66_nc_dftu/m_nc_dftu.F90::compute_nc_dftu_response_from_wfs`
- `abinit_dev/src/72_response/m_dfpt_vtorho.F90::dfpt_vtorho`
- `abinit_dev/src/72_response/m_dfpt_scfcv.F90::dfpt_scfcv`

The response routine now accepts two supported perturbation classes:

- atomic displacement: `ipert=1..natom`
- Gamma electric field/DDK: `ipert=natom+2`

For electric-field/DDK perturbations, PAO projectors are fixed. The electric path explicitly sets first-order projector derivatives to zero:

```fortran
dphi0_kpg = czero
```

This means the diagnostic response computes the wavefunction-driven localized occupation and linearized Hubbard potential:

$$
n^{E}_{mm'} = \langle \psi^{E} | \phi_m \rangle \langle \phi_{m'} | \psi^{0} \rangle
             + \langle \psi^{0} | \phi_m \rangle \langle \phi_{m'} | \psi^{E} \rangle
$$

$$
V_U^{E} = \frac{\partial V_U}{\partial n} : n^{E}
$$

without adding any electric-field PAO displacement derivative. Atomic displacement still uses the existing displacement helper only when `is_atomic_pert .and. iatom == ipert`.

Story 446 intentionally keeps the electric result diagnostic-only. The electric `occ1^E`/`V_U^E` response is computed, but not yet associated into the Sternheimer Hamiltonian/source path:

```fortran
if (has_nc_dftu_response .and. nc_dftu_is_atomic_pert) gs_hamkq%nc_dftu => nc_dftu_response
```

This preserves Story 447 as the dedicated fixed-projector electric-source integration step. Story 446 also keeps DDB/source side effects atomic-only in `dfpt_scfcv`, so dielectric and BEC DDB insertion remain assigned to Stories 448 and 449.

Important Fortran safety detail: `nc_dftu_is_atomic_pert` and `nc_dftu_is_electric_pert` must be initialized before any compound `.and.` guard, because Fortran does not guarantee short-circuit evaluation.

Validation:

- `make` in `abinit_dev/build` passed after implementation.
- Post-fix code-quality review passed after the boolean-initialization fix.
- Earlier Story 446 review lanes passed for goal/constraints, security, QA/build, and context mining.
- Fortran LSP diagnostics were unavailable because no `.F90` LSP server is configured.
