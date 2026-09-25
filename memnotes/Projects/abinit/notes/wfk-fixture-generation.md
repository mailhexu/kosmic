---
type: Project Knowledge
title: ABINIT WFK Unfolding Fixture Generation
description: Generate dense ABINIT non-SCF WFK band-path fixtures for unfolding examples and render validated EBS figures.
confidence: 0.8
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Re-run the numeric validation battery on a regenerated fixture before promotion."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, wfk, unfolding, fixtures, nic6]
---

# ABINIT WFK Unfolding Fixture Generation

## Scope

Generate dense non-self-consistent-field (SCF) wavefunction-file (WFK) band-path fixtures for the `unfolding` repo examples: Si, Si:P, Si8, antiferromagnetic (AFM) NiO. Then render the example figures. Runs execute on nic6 under `/scratch/hexu/unfolding-abinit-si-fixtures` with module `abinit/dev@d5380e0cb-gcc`. This note merges two managed skills. `abinit-wfk-unfolding-fixture-gen` supplies the deck and traps; `abinit-wfk-example-fixture-pipeline` supplies the run, render, and publication pipeline.

## Input deck (two-dataset pattern)

Inputs live in `tests/data/abinit_si/`. Use `ndtset 2`. Dataset 1, SCF: `kptopt 1`; a Gamma-only mesh for the Si family, or a 4x4x4 mesh for AFM NiO with `spinat` initialization; `tolvrs 1e-10`; `prtden 1`. Dataset 2, non-SCF band path: `iscf2 -2`; `getden2 1`; `tolwfr2 1e-16`; `nstep2 500`; `kptopt2 0`; explicit `kpt2`; `istwfk2 1`; `prtwf2 1`; `iomode 3`; `chkprim 0`. `nstep2 40` is not enough. Scattered k-points stall near residual 3e-7, and single eigenvalues jag by up to 0.9 eV; band figures fragment.

## Constraints ABINIT enforces

- Wrap each `kpt2` component into [-1, 1]. Transform path points with `K = k_prim @ M.T`, then `np.mod(K + 1.0, 2.0) - 1.0`. A component like 1.25 aborts in chkinp.
- Keep `rprim` right-handed: require `(R1 x R2) . R3 > 0`. Swap two vectors when ABINIT rejects the cell.
- Magnetic examples need `nsppol 2`, `nspden 2`, and `spinat`. A forgotten `nsppol` aborts (`spinat/=0 not allowed when nspden=1`). `occopt 3` with `tsmear 0.01 Ha` sustains type-II AFM NiO local moments, Ni plus/minus 1.36 mu_B in Perdew-Burke-Ernzerhof (PBE).
- Patch inputs by wrapping only the `kpt2` to `wtk2` block. Naive line heuristics miss k lines and produce a 125-error abort.

## Path and execution

- Replicate the SIESTA example path: face-centered-cubic special points in Setyawan-Curtarolo order Gamma-X-W-Gamma-L-W-X, spaced proportional to Cartesian segment length. Helper: `docgen/abinit_si_common.py`, `siesta_style_path`.
- Stage pseudopotentials with `tail -n +2` to strip the Dojo marker line. Source: Dojo-NC-SR PBE under `/home/hexu/projects/ABACUS-orbitals/generated/Dojo-NC-SR/PBE/`.
- Launch remote runs with `nohup sh -c "..." </dev/null >/dev/null 2>&1 &` so the ssh call returns. Poll for a DONE marker file. Copy the WFK files back with `scp`.

## Repository hygiene

Dense WFK files reach 258 MB (Si7P), 268 MB (Si8), and 1.2 GB (NiO). Keep them external; never commit them. The user forbade large data after an 86 MB push. Commit only 4-point corner fixtures (Gamma/X/W/L, 3.5-15 MB) plus the `.abi` generator inputs. Restore tracked small fixtures with `git checkout` after local rendering.

## Rendering and validation

- The WFK stores k-points in a different order than the path. Segment reversals occur, and components like 1.0 appear. Match stored k-points to path indices by periodic distance, then sort into path order before plotting.
- Render Gaussian-smeared effective band structure (EBS) heatmaps: sigma near 0.045 eV, Blues colormap, vmax 2. Scatter or alpha styles read as dotted. Clip semicore windows; Dojo scalar-relativistic Ni with `zion=18` places Ni-3s near -60 eV.
- Validate numerically before accepting a figure: Parseval state norms; branch-following adjacent-k gaps; per-k weight statistics; supercell spectra against a primitive-cell run at all folds; symmetry pairs `E(0,t,0) = E(t,0,0)`.
- Pristine unfolded 8-atom Si matches primitive bands to 0.083 eV after one constant shift. Type-II AFM NiO spin channels coincide band-for-band, below 0.05 eV, because inversion plus time-reversal-times-sublattice-translation relates them. Identical panels are correct physics.
- Do not use the workstation vision model to judge figure continuity. It labels plain line plots of pristine Si as fragmented. Validate numerically, or let the user judge the figure.

## Publication

After rendering, `git checkout` the small WFK files. Run `pytest tests/ -q`; the docs-link tests require the referenced PNG files. Commit code, inputs, the small fixture, and PNG files. Push. Poll the gh-pages workflow. Verify the live pages have exactly one `h1` element.
