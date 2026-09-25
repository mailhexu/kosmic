---
type: Domain Topic
id: abinit/development/qe-abinit-dftu-parity-slices
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Run matched QE 7.4 versus ABINIT DFT+U parity slices on the AFM NiO fixture with U-delta isolation and a discrepancy classification taxonomy.
triggers: [QE ABINIT DFT+U parity, NiO cross-code Hubbard, dftu_proj keyword map, U-delta isolation]
aliases: [QE parity slices]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: 39c97f9655b40213a254238ed0a4ac6f95a24af24c2161a3259298a1e032ba03
---

# QE-vs-ABINIT DFT+U Parity Slices

Run matched Quantum ESPRESSO (QE) 7.4 versus ABINIT DFT+U parity cross-checks on the AFM NiO fixture. Story-548 established the recipe (`scratch/story548/CROSSCHECK.md`, 2026-09-17); reuse it for any cross-code DFT+U validation.

## Matched deck conventions

- QE 7.4: `/home/hexu/.local/qe74_release/bin/pw.x`; UPFs `abinit_pao_proj/tests/Pspdir/{Ni_nc_dftu,O_nc_dftu}.upf`.
- XC: ABINIT `ixc=11` is the PBE Teter fit, not PZ. Use QE `input_dft='PBE'` and treat the residual (0.1-0.5 mHa) as formula-difference noise. `ecut 20 Ha` = 40 Ry; `ecutrho 320 Ry` is grid-converged (160→320 moves QE by +11.9 mHa; 320→640 moves by <= 5e-9). Never compare at default grids.
- k-mesh equivalence: ABINIT `kptopt 3, nsym 1, istwfk *1` on a shifted 2x2x2 mesh equals QE `K_POINTS automatic 2 2 2 1 1 1` plus `nosym=.true. noinv=.true.` (verified identical 8-point set and weights). The ABINIT `shiftk 0.5`/`nshift 8` per-IBZ trick reproduces the QE shifted-unreduced mesh.
- Occupations: QE `occupations='fixed'` requires `tot_magnetization=0.0`, the exact analogue of ABINIT `occopt 1` plus `spinat`; smearing adds about 5e-3 Ha.
- Hubbard card (lowercase syntax, pw.x 7.4): `HUBBARD (ortho-atomic) U(Ni)=8.0 J(Ni)=0.0`.
- Convergence: default QE convergence on both sides equals the ABINIT `toldfe 1e-10` setting. U-on SCF takes about 27-28 steps; U=0 about 19.

## QE 7.4 projector keyword map

The card parser rejects `(DFT+U)`.

| QE keyword | meaning | ABINIT twin |
|---|---|---|
| `(atomic)` | not orthogonalized | `dftu_proj 0` (raw) |
| `(norm-atomic)` | normalized, not orthogonalized | `dftu_proj 2` |
| `(ortho-atomic)` | global Loewdin | `dftu_proj 1` |
| `(DFT+U)` | rejected by 7.4 card_hubbard | - |

The "norm-atomic not supported" string belongs to the deprecated `lda_plus_u` namelist path, not the HUBBARD card. First-look comparisons between different frames show about +33 mHa etotal and +3e-2 Ha E_U frame shifts; identify the twin with a fresh control run before calling anything a defect.

## Isolation and classification

- Compare U-delta observables `X(U-on) − X(U=0)` to cancel non-Hubbard formula differences; compare deltas-of-deltas for frame shifts.
- Classification taxonomy, applied per discrepancy: (a) implementation-numerics floor, about 0.85 mHa etotal and 2e-5 Ha E_U (Teter versus original PBE, radial-interpolation grids, and QE density-grid residuals that move with ecutrho); (b) the QE 3-decimal eigenvalue print resolution for occupations; (c) k-sampling physics (state shifts, identical on both codes); (d) defect.
- Known QE-side defect (candidate upstream report): pw.x 7.4 computes the ortho-atomic Hubbard stress silently and wrongly — grid-converged, max 4.6e-4 Ha/bohr³ versus FD truth, wrong sigma_zz sign, shears 0-25% off; forces and energies are clean.
- Reference parity achieved (8 k-points, fixed occupations): etotal 0.825-0.869 mHa; E_U 1.5-2.3e-5; occupations <= 2e-4; U-delta forces 4.5e-6 Ha/bohr.
