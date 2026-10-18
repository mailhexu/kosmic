---
artifact_role: knowledge
audience: both
created: 2026-06-15
updated: 2026-08-12
status: stable
tags: [nc-dftu, dfpt, electric-field, ddb, dielectric, bec, spinor, story-448, story-496]
type: Project Knowledge
---

# NC DFT+U Electric-Electric Dielectric DDB Cache

Story 448 inserts the Gamma electric-field NC DFT+U electric-electric response-energy contribution into the native dielectric DDB block.

Changed source files:

- `abinit_dev/src/95_drive/m_dfpt_looppert.F90`
- `abinit_dev/src/72_response/m_dfpt_scfcv.F90`

The driver owns a transient three-direction cache for electric NC DFT+U response data. Each supported electric perturbation direction stores its `nc_dftu_response` payload so later electric directions can form pair contractions for the full dielectric `3 x 3` block.

The DDB insertion remains in ABINIT's native electric-electric bucket:

```fortran
d2nl(:, alpha, natom + 2, beta, natom + 2)
```

and marks the corresponding `blkflg` entries when a cached pair is inserted. No custom dielectric extraction path was added; native DDB extraction continues to consume the usual `natom+2` electric-electric blocks.

The contribution is formed as the localized Hubbard response-energy pair contraction between electric-field directions:

$$
\mathrm{Tr}\left[V_U^{E_\alpha} n^{E_\beta}\right].
$$

Implementation boundaries preserved:

- no changes to `m_dfpt_nstwf.F90`,
- no changes to DDB extraction routines,
- no Born-effective-charge insertion in this story,
- no test fixture commits, per user instruction,
- no extra `ucvol/four_pi` scaling at insertion; native DDB conversion remains responsible for dielectric units.

MPI perturbation-parallel handling is deliberately guarded. The cache is local to the DFPT driver process/rank that sees each perturbation direction. Because `mpi_enreg%paral_pert == 1` can split electric directions across perturbation MPI workers and no cross-rank cache exchange is implemented, NC DFT+U electric-electric dielectric cache setup now raises `ABI_ERROR` for that unsupported mode instead of silently producing incomplete off-rank direction pairs.

Validation:

- `make` in `abinit_dev/build` passed after implementation.
- Initial review found the perturbation-parallel cache ownership blocker.
- After adding the `mpi_enreg%paral_pert == 1` guard, focused goal, code-quality, security/reliability, context, and QA/build reviews all passed.
- QA confirmed Story 448 signatures were confined to `m_dfpt_looppert.F90` and `m_dfpt_scfcv.F90`; unrelated dirty files in the worktree were pre-existing.

## Packed-spinor snapshot correction — 2026-08-12

The original electric cache must retain values, not Fortran allocatable-array descriptors. A later Cartesian electric solve overwrites the active `occ1` and `V1`; storing the response object by assignment therefore cannot represent the earlier direction.

`m_nc_dftu_data.F90` now provides `nc_dftu_copy_response(destination, source)`. It requires both response payloads to be allocated with the same complex-component count and shapes, then copies the packed arrays:

$$
\mathcal C_\alpha =
\left(
N^{E_\alpha}_{uu},
N^{E_\alpha}_{dd},
N^{E_\alpha}_{ud},
N^{E_\alpha}_{du};
V^{E_\alpha}_{uu},
V^{E_\alpha}_{dd},
V^{E_\alpha}_{ud},
V^{E_\alpha}_{du}
\right).
$$

`dfpt_scfcv` initializes and snapshots one owned response object for each converged Cartesian electric direction before it evaluates

$$
\operatorname{Tr}\left[V_U^{E_\alpha}N^{\tau_{\kappa\beta}}\right]
\quad\text{and}\quad
\operatorname{Tr}\left[V_U^{E_\alpha}N^{E_\beta}\right].
$$

The raw packed complex blocks stay intact until the native scalar DDB arrays are assembled. At Gamma, fixed PAOs make the mixed/electric frozen-projector term zero; the complete finite-$q$ frozen-curvature path is documented separately in [nc-dftu-spinor-finite-q-frozen-curvature](nc-dftu-spinor-finite-q-frozen-curvature.md).

Evidence:

- The focused Fortran unit test mutates the source after copying and confirms the cached `occ1`/`V1` snapshot remains independent.
- Registered `v10/t123` completes a compact Gamma spinor DDK/electric/atomic schedule. A fresh output and DDB match stored references at $10^{-8}$.
- Its native DDB has 81 finite entries, including 9 electric-electric and 36 mixed electric-atomic entries.
- The ordinary `runtests.py` discovery remains blocked by unrelated malformed `v10/t86` metadata; direct use of its `fldiff` implementation verified the new fixture without adding a bypass.
