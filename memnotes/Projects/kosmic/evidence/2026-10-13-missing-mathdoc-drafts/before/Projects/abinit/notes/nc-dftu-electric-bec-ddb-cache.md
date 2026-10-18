---
audience: both
artifact_role: knowledge
created: 2026-06-15
updated: 2026-10-02
status: stable
tags: [nc-dftu, dfpt, electric-field, ddb, bec, story-449]
type: Project Knowledge
---

# NC DFT+U Atom-Electric BEC DDB Cache

Story 449 inserts the Gamma electric-field NC DFT+U atom-electric response-energy contribution into the native Born-effective-charge DDB block.

Changed source files:

- `abinit_dev/src/72_response/m_dfpt_scfcv.F90`
- `abinit_dev/src/95_drive/m_dfpt_looppert.F90`

The implementation reuses the Story 448 driver-owned electric response cache. During the electric-active pass (`ipert = natom + 2`), `dfpt_scfcv` computes each atomic-displacement partner response on demand with `frozen_displacement_only=.true.` and contracts the active electric Hubbard potential with the partner atomic density:

$$
\mathrm{Tr}\left[V_U^{E_\beta} n^{\tau_{\kappa\alpha}}\right].
$$

This follows the `compute_nc_dftu_response_energy_pair(lambda, mu)` convention: the first response builds the linearized Hubbard potential, and the second response supplies the density contraction.

The DDB storage remains native atom-electric BEC orientation:

```fortran
d2nl(:, atom_dir, atom, electric_dir, natom + 2)
blkflg(atom_dir, atom, electric_dir, natom + 2) = 1
```

No custom BEC extraction path was added; native DDB extraction continues to read the standard atom/electric blocks and reverse permutation when available.

Diagnostics are gated by `dtset%prtvol > 0` and print atom index, atom Cartesian direction, electric-field direction, and real/imaginary NC DFT+U atom-electric BEC contribution.

Unsupported cache modes fail loudly before cache allocation/use:

- non-Kramers-degenerate perturbations,
- perturbation-parallel processing (`mpi_enreg%paral_pert == 1`),
- partial `rfdir` electric direction requests,
- symmetry-reduced schedules where actual `pert_calc` does not contain all three electric directions.

Validation:

- `make` in `abinit_dev/build` passed after implementation and after guard fixes.
- Initial review found pair-order, diagnostic, and cache-completeness blockers.
- Direct API inspection confirmed the final pair order computes `Tr[V_U^E n^tau]`.
- Final focused code-quality, reliability, context, and QA/build reviews passed.
- Test fixture commits remain deferred to Story 450 per user instruction.

## Current fullUJ-NC correction (Story 567; certification open)

The preceding cache description is historical. Current fullUJ-NC keeps the live electric occupation/V1 and direction-completion flags, not write-only electric occupation copies. Differentiating the explicit Hubbard force has two arms: the native frozen atomic H1/wavefunction contraction and the frozen atomic occupation paired with the full electric response through the shared local Hessian. The ordered native atom-electric row receives the latter once with the electric-row sign used by dfpt_nstwf; electric-electric receives no extra local Hessian bucket. Uncorrelated atomic partners are skipped before projector work.

Independent current-source finite-J p-shell U=.35/J=.08 moving-state gradient FD requires both arms (scalar force<=7.60e-12, packed<=2.26e-11); frozen-H1-only omission is detectable. The same witness exposed and fixed scalar spin-down cg0/cg1 rereading spin up; kg resets per physical spin, wavefunction offsets do not. NiO LDA/PZ collinear ecut30 one-k(.5,.5,.5) full36 force-Hessian recertification<=6.57e-7 and ordinary MPI2 parity0 pass. Source build and actual LiF/NiO electric DDB replays converge, but coarse LiF LDA/PW92 ecut40 shifted4x4x4 dielectric/Born versus independent fields remains discrepant. No tensor certification is inferred from these local identities or convergence.

Evidence: .tmp/fulluj-story567/mixed-gradient-witness.log, collinear-recert.log; [current feature matrix](nc-dftu-porting-feature-matrix.md).
