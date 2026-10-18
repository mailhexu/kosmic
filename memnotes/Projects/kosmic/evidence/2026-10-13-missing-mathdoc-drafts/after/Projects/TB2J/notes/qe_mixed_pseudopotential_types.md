---
audience: both
okf_version: "0.2"
type: Project Knowledge
artifact_role: knowledge
status: draft
created: 2026-10-02
updated: 2026-10-02
project: TB2J
tags: ["quantum-espresso", "pseudopotential", "paw", "ultrasoft", "norm-conserving", "projector-green", "interface-design"]
related_files:
  - "Refs/q-e-7.4/PW/src/setup.f90"
  - "Refs/q-e-7.4/Modules/read_pseudo.f90"
  - "Refs/q-e-7.4/upflib/pseudo_types.f90"
  - "Refs/q-e-7.4/upflib/read_upf_v1.f90"
  - "Refs/q-e-7.4/upflib/read_upf_new.f90"
  - "Refs/q-e-7.4/upflib/qrad_mod.f90"
  - "Refs/q-e-7.4/upflib/qvan2.f90"
  - "Refs/q-e-7.4/upflib/init_us_1.f90"
  - "Refs/q-e-7.4/PW/src/newd.f90"
  - "Refs/q-e-7.4/PW/src/addusdens.f90"
  - "Refs/q-e-7.4/PW/src/compute_becsum.f90"
  - "Refs/q-e-7.4/PW/src/add_paw_to_deeq.f90"
  - "Refs/q-e-7.4/PW/src/paw_onecenter.f90"
  - "Refs/q-e-7.4/PW/src/paw_init.f90"
  - "Refs/q-e-7.4/PW/src/paw_symmetry.f90"
  - "Refs/q-e-7.4/PW/src/xdm_dispersion.f90"
  - "Refs/q-e-7.4/PW/src/input.f90"
related_functions:
  - "readpp"
  - "read_pseudo_nl"
  - "read_pp_paw"
  - "set_upf_q"
  - "init_tab_qrad"
  - "qvan2"
  - "compute_qqr"
  - "newd"
  - "newq"
  - "addusdens_g"
  - "compute_becsum"
  - "sum_bec"
  - "add_paw_to_deeq"
  - "PAW_potential"
  - "PAW_atomic_becsum"
validation_procedure: |
  Read the QE 7.4 source at Refs/q-e-7.4 for every claim, then run seven mixed
  and control pw.x 7.4 calculations (PAW+NC, PAW+US+NC, PAW+US spin-polarized,
  PAW+US+DFT+U, PAW+NC noncollinear, US+US, XC-mismatch abort) and a
  same-element superposition identity (PAW+PAW / US+US / PAW+US). Validated
  2026-10-02.
validation_date: 2026-10-02
links_to: ["paw_partial_wave_projector_choices", "projector_greens_netcdf_schema", "paw_projector_greens_function", "norm_conserving_pao_tb2j_research"]
linked_from: []
math_provenance: missing
math_provenance_reason: "qe_mixed_pseudopotential_types.md display math requires one MathDoc marker per equation"
---

# QE Mixed Pseudopotential Types (NC + US + PAW in one run)

## Answer

QE accepts any mixture of norm-conserving, ultrasoft, and PAW pseudopotentials
across species in a single calculation, with **no input switch** and no
cross-type consistency requirement. The type is read from each UPF file, and
the augmentation machinery is switched on per species.

## Mechanism

Two `ANY` reductions over the per-species `upf` array
(`PW/src/setup.f90:117-118`):

```fortran
okvan = ANY( upf(1:ntyp)%tvanp )
okpaw = ANY( upf(1:ntyp)%tpawp )
```

There is no `pseudotype`/`uspp`/`paw` variable in `PW/src/input.f90`. The type
lives in the UPF header, dispatched in `upflib/read_upf_v1.f90:265-283`:
`PAW` sets **both** `tvanp = .true.` and `tpawp = .true.`, so PAW is a strict
superset of ultrasoft — a PAW run is a US run plus a per-atom one-center term.

Per-species payload in `upflib/pseudo_types.f90`: `tvanp`, `tpawp`, `nlcc`,
`nbeta`, `nqf`, `nqlc`, `kkbeta`, and a `paw` component (`ae_vloc`,
`ae_rho_atc`, `pfunc`, `ptfunc`, `augmom`, `core_energy`, `raug`, `iraug`,
`augshape`).

## Global maxima, not uniformity requirements

`lmaxkb`, `lmaxq = 2*lmaxkb+1`, `nhm`, `nbetam` are maxima over types;
`deeq`, `becsum`, `rho%bec`, `ddd_paw`, `tab_qrad` are sized to them.
`nkb = Σ nh(ityp(na))` is unconditional, so **NC species keep their beta
projectors in the nonlocal operator even inside a US/PAW run**. No `nqf`,
`nqlc`, `nbeta`, or radial-mesh value must agree across species; each type's
`nqlc` is independently clipped to the global `lmaxq`
(`upflib/init_us_1.f90:72-75`).

## Per-type guards

| Quantity | Guard | File:line |
|---|---|---|
| `tab_qrad` fill | `if (upf(nt)%tvanp)` | `upflib/qrad_mod.f90:98` |
| `qq_nt` | `if (upf(nt)%tvanp)` | `upflib/qvan2.f90:199, 242` |
| `deeq` Q·V term | `IF (upf(nt)%tvanp)` | `PW/src/newd.f90:95` |
| `deeq` `dvan` term | **no guard, all atoms** | `PW/src/newd.f90:270-289` |
| augmentation density | `IF (upf(nt)%tvanp)` | `PW/src/addusdens.f90:116` |
| `becp` / `becsum` | **no guard, all atoms** | `PW/src/compute_becsum.f90:213` |
| `ddd_paw` → `deeq` | `IF (.not.upf(nt)%tpawp) CYCLE` | `PW/src/add_paw_to_deeq.f90:32` |
| PAW one-center `d` | `d(:,:,:)=0` then `ifpaw: IF (upf(i%t)%tpawp)` | `PW/src/paw_onecenter.f90:116, 141` |
| atomic `becsum` init | `is_paw: IF (upf(nt)%tpawp)` | `PW/src/paw_init.f90:200` |
| radial integrator alloc | `IF(.NOT. upf(nt)%tpawp) CYCLE` | `PW/src/paw_init.f90:327` |
| all `PAW_symmetrize*` | `IF ( .NOT. upf(nt)%tpawp ) CYCLE` | `PW/src/paw_symmetry.f90:111, 174, 192, 249, ...` |

Consequence: an NC species inside a US/PAW run gets
$\mathrm{deeq}_{ij}^{I} = \mathrm{dvan}_{ij}^{nt}$ exactly — the pure
Kleinman–Bylander operator — while its `becp` coefficients are still computed.

## Constraints

**Hard:**

- All species must declare the same XC (`read_pseudo.f90:223-227`). Verified:
  Cu PAW/PBE + Cu NC/PZ aborts with
  `Error in routine set_dft_from_name (3): conflicting values for icorr`.
- `ecutrho > ecutwfc` (`input.f90:1786`).
- For US/PAW, `ecutrho >= 4*ecutwfc`; below that QE only warns
  (`input.f90:1787`) but the result is wrong.

**Soft:** `infomsg 'no reason to have ecutrho>4*ecutwfc'` only when no species
is US/PAW/NLCC and no RISM (`setup.f90:476-479`).

**Feature gates from any US/PAW species** (not mixing penalties — they apply
to an all-NC run of the same feature set): meta-GGA, noncollinear
Berry-phase/electric field, Tkatchenko–Scheffler vdW, orbital magnetization,
hybrid + forces, hybrid + noncollinear, SCDM, SIC, force-theorem MAE with PAW.

**The one real uniformity assumption in the tree:**
`PW/src/xdm_dispersion.f90:105`, `ispaw = ALL(upf(1:ntyp)%tpawp)`, selecting the
`upf(i)%paw%ae_rho_atc` branch. In a mixed run with `vdw_corr='grimme-d2'`,
non-PAW species silently take the non-PAW branch.

**`check_order` rejects PAW — but only Car–Parrinello.**
`ANY(upf%tpawp) → errore('PAW not implemented')` (`read_pseudo.f90:250`), and
its only caller is `CPV/src/input.f90:69`. `pw.x` never calls it.

## Empirical validation (pw.x 7.4)

All converged unless noted:

| Run | Species | $E_{\rm tot}$ (Ry) |
|---|---|---|
| C PAW + Si NC, Γ | | $-25.66776$ |
| C PAW + H US + Si NC, Γ | | $-26.72359$ (one-center PAW $-6.68959$) |
| Cu PAW + O US, rocksalt, $n_{\rm spin}=2$ | | $-245.04650$ ($m=1.00\ \mu_B$) |
| Cu PAW + O US + `HUBBARD atomic U Cu-3d 4.0` | | $-244.99343$ |
| Cu PAW/PBE + Cu NC/PZ | mixed XC | **abort** |
| C PAW + Si NC, `noncolin=.TRUE.` | | $-25.59370$ (one-center PAW $-6.68432$) |

**Superposition identity** (same element C, 2 atoms 16 bohr apart, 30 bohr cube,
Martyna–Tuckerman):

$$
E(\text{PAW}+\text{US})=-28.54093385\ \text{Ry}
$$
$$
\tfrac{1}{2}\big[E(\text{PAW}+\text{PAW})+E(\text{US}+\text{US})\big]=-28.54091062\ \text{Ry}
$$

Deviation $2.3\times10^{-5}$ Ry $=0.32$ meV, $1.6\times10^{-4}\%$ of the
14.10 Ry PAW–US gap. Per-species augmentation is independent and additive.

**Species-order invariance:** swapping the two `ATOMIC_SPECIES` entries and
positions changes $E$ by $3.6\times10^{-7}$ Ry.

## Consequence for the TB2J projector interface

The obstruction to a QE exporter is **not** PP-type heterogeneity in execution.
It is that the projector *Hamiltonian* is not uniform across species: NC
species have `deeq = dvan` with no augmentation, US/PAW species have the full
$\langle\psi|S|\psi'\rangle$ term, and PAW adds a one-center $ddd$ block. Any
QE-side projector overlap matrix $S(k)$ must therefore be built per species
type, or the exporter must restrict runs to one type family. The existing
`projector_basis_type` metadata already has the `uspp` vs `paw` distinction
needed; `upf%tpawp` should be exported alongside it.

Full memo:
[specs/research/2026-10-02-qe-mixed-pseudopotential-types.md](../subprojects/qe-projector-exporter/specs/research/2026-10-02-qe-mixed-pseudopotential-types.md)

## Linked Concepts

- [paw_partial_wave_projector_choices](paw_partial_wave_projector_choices.md)
- [projector_greens_netcdf_schema](projector_greens_netcdf_schema.md)
- [paw_projector_greens_function](paw_projector_greens_function.md)
- [norm_conserving_pao_tb2j_research](norm_conserving_pao_tb2j_research.md)
