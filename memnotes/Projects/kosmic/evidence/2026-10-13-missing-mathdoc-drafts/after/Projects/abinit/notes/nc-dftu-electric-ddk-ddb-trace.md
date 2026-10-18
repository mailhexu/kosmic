---
artifact_role: knowledge
audience: both
created: 2026-06-15
updated: 2026-06-15
status: draft
tags: [nc-dftu, dfpt, electric-field, ddk, ddb, bec, dielectric, story-444]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "nc-dftu-electric-ddk-ddb-trace.md display math requires one MathDoc marker per equation"
---

# NC DFT+U Electric-Field/DDK Source And DDB Trace

Story 444 traced native ABINIT Gamma electric-field/DDK source construction and DDB conventions before adding NC DFT+U electric-field support.

## DDK / Electric-Field Source Flow

- `abinit_dev/src/72_response/m_dfpt_vtowfk.F90::dfpt_vtowfk` sets `test_ddk=1` for Gamma electric field without Berry phase, sets `opt_gvnlx1=1` for `ipert=natom+2`, reads DDK wavefunctions, and multiplies by `+i` for electric-field work.
- `abinit_dev/src/72_response/m_dfpt_cgwf.F90::dfpt_cgwf` owns the main Sternheimer source cadence through `getgh1c`. It calls `getgh1c`, then currently adds NC DFT+U source augmentation before generalized-eigenproblem `S^(1)` subtraction. It skips `S^(1)` subtraction for `ipert=natom+2`.
- `abinit_dev/src/66_wfs/m_getgh1c.F90::getgh1c` owns `gh1c` and optional `gvnlx1`; for `ipert=natom+2`, `gvnlx1` can contain DDK-derived data. The non-Berry path treats `gvnlx1` as `|i du^(0)/dk_band>`, while the Berry branch constructs source terms as a `+i` rotation of `grad_berry`.
- `abinit_dev/src/72_response/m_dfpt_nstwf.F90::dfpt_nstwf` opens DDK WF files, reads DDK band blocks, and applies the DDK sign convention used in nonstationary formulas. Electric-field case ultimately uses the `+i d/dk` convention.
- `abinit_dev/src/72_response/m_ddk.F90` owns native DDK wavefunction/operator infrastructure.
- `abinit_dev/src/72_response/m_dfpt_fef.F90` produces Berry-phase electric-field inputs consumed by `getgh1c`.

## Safe Source Insertion Point

The safest first implementation hook for fixed-projector NC DFT+U electric source is in `m_dfpt_cgwf.F90::dfpt_cgwf`, immediately after `getgh1c` returns and before the `gen_eigenpb`/`S^(1)` subtraction.

The electric-field NC DFT+U source must be fixed-projector only:

$$
\hat V_U^E |\psi^{(0)}\rangle
=
\sum_{a,mm'} |\phi_m^a\rangle V_{mm'}^{E,a}
\langle \phi_{m'}^a | \psi^{(0)}\rangle .
$$

It must not include displacement-only terms:

$$
|\phi^{(1)}\rangle V_U^0\langle\phi|\psi^0\rangle,
\qquad
|\phi\rangle V_U^0\langle\phi^{(1)}|\psi^0\rangle .
$$

## Dielectric Tensor DDB Convention

Gamma electric-electric dielectric data use `ipert1 = ipert2 = natom + 2`.

- `m_dfpt_scfcv.F90` calls `dfptff_die(...)` when Berry/electric-field conditions are active and `ipert == natom+2`, then marks:

```fortran
blkflg(:, natom+2, :, natom+2) = 1
```

- `m_dfpt_fef.F90::dfptff_die` stores dielectric tensor into:

```fortran
d2lo(1, 1:3, ipert, idirpert, ipert)
```

with `ipert = natom + 2`.
- `m_ddb.F90::ddb_set_d2matr` packs DDB order as `ipert2 -> idir2 -> ipert1 -> idir1`, from `flg(idir1,ipert1,idir2,ipert2)` and `d2matr(:,idir1,ipert1,idir2,ipert2)`.
- `m_ddb.F90::ddb_get_block` queries pure dielectric blocks with `rfphon=0`, `rfelfd(1:2)=2`, `rfstrs=0`.
- `m_ddb.F90::dtech9` extracts dielectric tensor as:

```fortran
dielt(elec1, elec2) = blkval(1, elec1, natom+2, elec2, natom+2, iblok)
```

- `m_ddb.F90::ddb_to_d2etot` converts stored dielectric tensor to second derivatives with diagonal `(1 - val) * ucvol / four_pi` and off-diagonal `-ucvol / four_pi * val`.

## Born Effective Charge DDB Convention

Native BEC assembly is atom-active with electric-field partner. Extraction is phonon/atom first and electric second, with reverse permutation symmetrized when available.

- `m_dfpt_scfcv.F90` calls `dfptff_bec(...)` when `ipert <= natom`, then marks:

```fortran
blkflg(:, natom+2, :, 1:natom) = 1
```

- `m_dfpt_fef.F90::dfptff_bec` stores BEC into:

```fortran
d2lo(1, 1:3, natom+2, idirpert, ipert)
```

where `ipert` is an atom and `idirpert` is the active atom-displacement direction.
- `m_ddb.F90::ddb_get_dielt_zeff` searches with `rfphon(1)=1`, `rfelfd(2)=2`.
- `dtech9` reads:

```fortran
blkval(1, depl, iatom, elec, natom+2)
```

and symmetrizes with reverse permutation:

```fortran
blkval(1, elec, natom+2, depl, iatom)
```

- `m_d2frnl.F90` PAW frozen BEC assembly uses `becfrnl(mu,iatom,nu)` with `mu` atom direction and `nu` electric direction, then applies output sign flip `becfrnl_tmp = -becfrnl`.
- `m_dfpt_nstwf.F90` and `m_dfpt_scfcv.F90` comments/sign clues indicate BEC terms correspond to `-D2E` when the partner is electric.

## NC DFT+U Future Insertion Guidance

The existing NC DFT+U mixed response-energy insertion region is in `m_dfpt_scfcv.F90`, inside the `psps%usepaw == 0 .and. dtset%usedftu_nc == 1` branch that computes NC response-energy pairs and accumulates into `d2nl` followed by `blkflg` updates.

Future implementation should:

1. Add electric-field descriptor support first; do not weaken guards globally.
2. Compute `occ1^E`/`V_U^E` from fixed PAO projectors and DDK/electric first-order wavefunctions.
3. Add fixed-projector source in `dfpt_cgwf` source cadence.
4. Insert electric-electric NC DFT+U response energy into native `ipert1=ipert2=natom+2` DDB block after validating bucket/sign/prefactor.
5. Insert atom-electric NC DFT+U response energy in atom-first/electric-second orientation, relying on native reverse-block symmetrization where applicable.
6. Use native `blkflg` conventions; do not write custom dielectric/BEC output.

## Remaining Risks

- Exact localized +U sign/prefactor for electric-electric insertion needs a runnable diagnostic.
- Exact localized +U sign/prefactor for atom-electric insertion must be validated against U=0/no-U controls.
- Do not confuse DDB-stored dielectric tensor with `d2E/dE_i dE_j`; use `ddb_to_d2etot` conventions when converting.
- The dirty `abinit_dev` working tree contains unrelated prior test/reference files; source edits must use per-story allowlists and staged diffs only.
