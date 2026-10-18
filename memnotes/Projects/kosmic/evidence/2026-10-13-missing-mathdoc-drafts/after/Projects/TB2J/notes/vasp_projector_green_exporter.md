---
artifact_role: knowledge
audience: both
confidence: 0.95
created: 2026-05-12
last_validated: 2026-08-13T00:00:00+00:00
validation_procedure: |
  Explored local VASP 6.4.1 CPU source tree at vasp.6.4.1_cpu using the
  OpenCode explore subagent. Compiled the VASP XML writer with `make std`.
  Validated generated TB2J XML from scratch NiO testsuite runs at
  `/tmp/opencode/vasp_tb2j_validation` for `ISYM=0` and `ISYM=2`; both XML files
  loaded through `load_vasp_projector_xml()` and passed
  `ProjectorGreenData.validate(exchange_ready=True)`. Re-ran focused TB2J parser
  tests, ruff, and `git diff --check` in both TB2J and VASP trees. Later
  confirmed that the TB2J exchange path now rejects `ISYM>0` XML by default,
  while allowing an explicit diagnostic override. Later found and fixed that VASP
  `POSION` is direct/scaled but TB2J positions are Cartesian Angstrom. Ran bcc Fe
  `ISYM=2` XML diagnostics in `/tmp/opencode/bcc_fe_symmetry_validation` with
  single-radial and fuller `s p d` `Pr 1`/`Pr 2` bases; the fuller basis improves
  Green-vs-OUTCAR populations but still narrowly fails the default charge
  tolerance, so the `ISYM>0` exchange guard remains in force. A matched bcc Fe
  `ISYM=0` fuller-basis run is population-safe but still gives exchange shells
  far smaller than GPAW, showing that the remaining mismatch is not only the
  symmetry-expanded coefficient path. Research then showed the operator mismatch
  comes from pairing `LPRJ_COVL` LOCPROJ trial-orbital coefficients with native
  PAW `CDIJ`; native `W%CPROJ` is the closer coefficient source for `CDIJ`, but
  raw `W%CPROJ` has a normalization/metric mismatch that fails population checks.
  A WAVECAR-based export fixes the spurious low LORBIT moment seen in random-wave
  one-step export and improves the first-shell exchange, but VASP Delta remains
  much smaller than GPAW. A 9x9x9 k-mesh brings WAVECAR-based VASP `W%CPROJ`
  first-shell exchange closer to GPAW, but raw `W%CPROJ` populations remain
  unphysical.
  A source audit ranked the main remaining issues as PAW metric/dual treatment
  for `W%CPROJ`, inconsistent `LPRJ_COVL`/`CDIJ` bases, and fragile native CPROJ
  indexing in parallel/multi-ion cases.
validation_test: null
successful_usage_count: 12
last_used_successfully: 2026-05-13T23:23:12+02:00
usage_stale: false
related_files:
  - "vasp.6.4.1_cpu/src/wave_struct.F"
  - "vasp.6.4.1_cpu/src/nonl.F"
  - "vasp.6.4.1_cpu/src/nonl_high.F"
  - "vasp.6.4.1_cpu/src/locproj.F"
  - "vasp.6.4.1_cpu/src/sphpro.F"
  - "vasp.6.4.1_cpu/src/mkpoints_struct.F"
  - "vasp.6.4.1_cpu/src/pseudo_struct.F"
  - "vasp.6.4.1_cpu/src/us.F"
  - "vasp.6.4.1_cpu/src/vhdf5.F"
  - "vasp.6.4.1_cpu/src/tb2j_projector_xml.F"
  - "vasp.6.4.1_cpu/src/main.F"
related_functions:
  - "PROJ"
  - "PROALL"
  - "LPRJ_PROALL"
  - "LPRJ_WRITE"
  - "SPHPRO"
  - "SETDIJ"
  - "SETDIJ_"
  - "vh5_write_projectors"
  - "TB2JXML_READER"
  - "TB2JXML_WRITE_SKELETON"
tags: [vasp, projector-green, paw, xml, exporter]
project: TB2J
status: draft
validated_by: automatic
validation_date: 2026-05-13T23:23:12+02:00
links_to: ["projector_greens_netcdf_schema", "paw_partial_wave_projector_choices"]
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "vasp_projector_green_exporter.md display math requires one MathDoc marker per equation"
---

# VASP Projector Green Exporter Research

VASP 6.4.1 contains most ingredients needed for a TB2J projector Green NetCDF
exporter, but not in one existing output file. A robust exporter likely requires
VASP source hooks rather than post-processing only existing outputs.

## Available Internal Data

`vasp.6.4.1_cpu/src/wave_struct.F` defines wavefunction/projector storage:

- `W%CPROJ(:,:,:,:)`: PAW projector overlaps / orbital character, documented as
  `<p_alpha|phi_n,k>`.
- `W%CELTOT(NB_TOT,NKPTS,ISPIN)`: eigenvalues.
- `W%FERTOT(NB_TOT,NKPTS,ISPIN)`: occupations.
- `WDES%VKPT`, `WDES%WTKPT`, `WDES%NKPTS`, `WDES%NB_TOT`, `WDES%ISPIN`,
  `WDES%NCDIJ`, and `WDES%NRSPINORS`: k-point, spin, and band metadata.

Projector overlaps are computed in:

- `nonl.F`: `PROJ`, `PROJ1`, `PROJMU`, and related routines.
- `nonl_high.F`: `PROALL`, `W1_PROJALL`, `W1_PROJ`.

The source comments identify the PAW projector contraction form as a sum over
plane waves involving the projector functions and wavefunction coefficients.

## LOCPROJ as the Closest Existing Path

`vasp.6.4.1_cpu/src/locproj.F` is the closest analogue to the GPAW projector
workflow:

- `LPRJ_COVL(NBANDS,NK,ISP,NPROJ)` stores complex local projections.
- `LPRJ_functions(:)` stores local projector/orbital metadata.
- `LPRJ_PROALL` computes projections and can use `KPOINTS_FULL` plus symmetry
  rotations.
- `LPRJ_WRITE` writes `PROJCAR`, `LOCPROJ`, and `vasprun.xml` `locprojected`
  data.

Existing `LOCPROJ` output can support a prototype for eigenvalues,
occupations, complex local projections, and rough metadata, but it misses the
complete PAW matrices and structured full-BZ metadata needed for robust TB2J
NetCDF export.

## PAW Setup and Onsite Matrices

`vasp.6.4.1_cpu/src/pseudo_struct.F` defines `TYPE potcar` fields relevant to
PAW projector Green export:

- `PSPNL`, `PSPNL_SPLINE`, `PSPRNL`, `BETA`: projector data.
- `WAE`, `WPS`: all-electron and pseudo partial waves.
- `DION`, `DION_ORIG`, `DIJ`: PAW nonlocal/onsite Hamiltonian data.
- `QION`, `QPAW`, `QIJ`: PAW augmentation/overlap-related data.
- `LPS`, `LMAX`, `LMMAX`, `LMDIM`: angular/projector metadata.

`vasp.6.4.1_cpu/src/us.F` contains onsite PAW matrix construction:

- `SETDIJ` / `SETDIJ_` compute `CDIJ(LMDIM,LMDIM,NIONS,NCDIJ)`, a candidate
  analogue of GPAW's native onsite PAW Hamiltonian matrix.
- `CQIJ(LMDIM,LMDIM,NIONS,NCDIJ)` is a candidate PAW overlap/augmentation
  matrix.

For collinear spin, `CDIJ(:,:,ion,up) - CDIJ(:,:,ion,down)` is the most direct
candidate local spin-dependent onsite PAW Hamiltonian matrix. It is not
currently written with the metadata TB2J needs.

## Existing Outputs and Gaps

- `WAVECAR` contains wavefunction coefficients, eigenvalues, occupations, and
  k-points, but not `W%CPROJ`, PAW metadata, or onsite matrices.
- `PROCAR` / `sphpro.F` primarily provides projected weights and optional phase
  data, not a complete robust complex projector coefficient set.
- `vasprun.xml` can include eigenvalues, k-points, and `locprojected` data, but
  not PAW onsite overlap/operator matrices.
- VASP HDF5 support in `vhdf5.F::vh5_write_projectors` writes PROCAR-like
  projector data, not a full TB2J projector Green dataset.

## Recommended Implementation Phases

1. Prototype parser from existing `LOCPROJ`/`vasprun.xml` outputs to test
   projection/eigenvalue conversion. This will be incomplete because onsite PAW
   matrices and exact metadata are missing.
2. Add VASP write hooks near `locproj.F::LPRJ_PROALL`/`LPRJ_WRITE` to export
   `LPRJ_COVL`, full k-point metadata, eigenvalues, occupations, and local
   projector labels.
3. Add PAW matrix write hooks near `us.F::SETDIJ`/`SETDIJ_` to export `CDIJ`,
   `CQIJ`, and spin-dependent onsite operators with `potcar` metadata.
4. Prefer a dedicated structured exporter, modeled on VASP's HDF5 or a new
   NetCDF path, over fragile post-processing from multiple text/XML files.

The practical conclusion is that VASP can support a TB2J-compatible projector
Green export, but a production-quality path should be a VASP-side source patch
that writes projections, full k-point/eigenvalue data, PAW metadata, and onsite
operator/overlap matrices in one structured file.

## Writer Skeleton Hook Pattern

The VASP writer skeleton can be added without changing the large `READER`
argument list by following the existing feature-reader pattern used by Wannier
and LOCPROJ code:

- Add a separate module, `src/tb2j_projector_xml.F`, with saved settings for
  `LTB2JXML` and `TB2JXML`.
- Parse those settings through `PROCESS_INCAR` in `TB2JXML_READER(IO)`, called
  from `main.F` after `LPRJ_READER`, and close INCAR with
  `CLOSE_INCAR_IF_FOUND(IO%IU5)` after the reader finishes.
- Keep the writer disabled by default and call `TB2JXML_WRITE_SKELETON(IO)` from
  `main.F` after the standard parameter XML block closes.
- Add `tb2j_projector_xml.o` to `src/.objects` so the module is compiled before
  `main.o`.

Validation note: full `make std` initially failed before reaching the new module
because existing C helpers in `src/lib/timing_.c` and `src/lib/dclock_.c`
redeclared `getrusage` and `gettimeofday` with obsolete K&R-style prototypes.
The fix is to include `sys/time.h` and rely on the system prototypes. After that
fix and the `WRITEXMLINCAR` import correction in `tb2j_projector_xml.F`,
`make std` completed and produced `bin/vasp_std`.

## Spectral XML Writer Hook

The spectral XML writer should run after VASP synchronizes `W%CELTOT` for KPAR
and after the normal `XML_EIGENVALUES` call in `main.F`. At that point the
writer can access the final structure, `W%CELTOT`, `W%FERTOT`, `EFERMI`, and the
current k-point metadata without adding another eigenvalue synchronization path.

For story 004, `TB2JXML_WRITE_SPECTRAL` writes:

- `dimensions` for spin, k-point, band, atom, and zero placeholder projector
  dimensions.
- `structure` with cell, fractional positions, element symbols, and atomic
  numbers estimated from `P(type)%ZCORE + P(type)%ZVALF`.
- `kpoints bz="full"` using `KPOINTS_FULL%VKPT` and `KPOINTS_FULL%NEQUIV` when
  available, mapping full-BZ k-points back to IBZ eigenvalue/occupation rows.
- symmetry-off fallback to current `KPOINTS` only when `ISYM<=0`; if symmetry is
  enabled and no full map is available, the writer refuses to emit ambiguous
  IBZ-only XML.
- `bands` with `efermi`, eigenvalues, and occupations in the parser order
  `nspin nkpt nband`; collinear `ISPIN=2` output honors
  `KPOINTS_FULL%SPINFLIP` by swapping source spin channels for full-map points
  that require a spin flip.
- empty projector arrays with `nproj=0` so the TB2J parser can validate spectral
  shape before story 005 adds real projector coefficients.

Validation note: TB2J parser tests include a generated spectral XML shape with
zero projectors, and implementation review fixed the spin-flip mapping case for
full-BZ spectral rows. VASP `make std` completed after the C helper prototype
fixes and the TB2J XML module import fix.

## Projector And Operator XML Writer Hook

The first coefficient source is `LPRJ_COVL`, not raw `W%CPROJ`, because
`LPRJ_PROALL` already computes full-BZ projections and carries matching
`LPRJ_functions` metadata. `electron.F` calls
`TB2JXML_WRITE_PROJECTORS_OPERATORS` immediately after `LPRJ_PROALL` and
`LPRJ_WRITE`, before `LPRJ_DEALLOC`, while `CDIJ` and `CQIJ` are also available.

The writer now emits:

- `coefficients` from `LPRJ_COVL` in TB2J parser order `nspin nkpt nband nproj`
  with interleaved real/imaginary values.
- projector metadata from `LPRJ_functions`: zero-based atom/site index, angular
  `l`, converted `m`, and radial/channel index.
- `site_nproj` and `site_projector_indices` from the VASP POSCAR site grouping.
- `overlap_metric` as `real(CQIJ)` projected into the LPRJ function basis.
- spin-resolved `hij` as `real(CDIJ)` site-local blocks for collinear
  `NCDIJ>=2`, with `operator_basis="vasp_cdij_paw_hamiltonian"`.

The PAW LM index mapping currently assumes the standard `LPRJ_FROM_PSEUDO`
ordering where `iproj` is the PAW radial channel and `m=1..2*l+1` selects the
magnetic component within that channel. This is the right first implementation
target for `LOCPROJ_AUTO`/pseudo-derived LPRJ functions, but manually supplied
nonstandard `LOCPROJ` definitions need a real-run validation pass.

Validation: VASP `make std` passed after this hook; TB2J parser tests include a
generated XML fixture with non-empty coefficients, overlap metric, and
spin-resolved `hij` that validates as exchange-ready.

Real-run validation used scratch NiO testsuite inputs in
`/tmp/opencode/vasp_tb2j_validation`: a short seed run generated `CHGCAR`, then
paired `ICHARG=5` XML runs used explicit `LOCPROJ = "1 - 2 : d : Pr 1"` with
`ISYM=0` and `ISYM=2`. Both generated XML files loaded with
`load_vasp_projector_xml()` and passed `ProjectorGreenData.validate(exchange_ready=True)`.
The `ISYM=2` VASP run reported 4 irreducible k-points, while the TB2J XML
contains 8 full-BZ k-points, matching the `ISYM=0` full-BZ size. Both XML files
have finite nonzero coefficients, finite `overlap_metric`, finite spin-resolved
`hij`, matching `nspin=2`, `nband=48`, `nproj=10`, and Ni `d` projector metadata
with `m=-2..2` on the two Ni sites.

Caveat: `LOCPROJ_AUTO=.TRUE.` on the same NiO scratch input failed inside
VASP's LCAO projector construction before XML writing (`lcao_bare.F`, no zeros
in interval). The explicit `LOCPROJ` run validates the writer/parser path, but
broader automatic pseudo-derived projector coverage should be revisited with a
compatible POTCAR/case.

## VASP XML Exchange API And CLI

TB2J can generate a controlled projector exchange output directly from VASP XML
through `TB2J.interfaces.vasp_projector_xml.gen_exchange_vasp_projector_xml()`.
The function loads XML with `load_vasp_projector_xml()`, validates it as
exchange-ready, builds the integer `R` grid, and reuses the existing
`write_projector_exchange_out()` path with VASP-specific description text.

The command-line entry point is `vasp_projector2J.py`, implemented in
`TB2J/scripts/vasp_projector2J.py`. It mirrors the GPAW projector CLI options:
`--input`, `--output_path`, `--Rmax`, `--nz`, `--smearing`, `--elements`, and
`--index_magnetic_atoms`.

For non-GPAW projector data without `paw_N0_p`, `write_projector_exchange_out()`
uses a generic projected-population fallback from the occupied projector density
blocks, contracting with `overlap_metric` when it is present. This is used for
charges/spin moments written to `exchange.out`; the exchange couplings still
come from the controlled projector Green trace and `Delta = H_ij^up-H_ij^down`.

The VASP `hij_definition` string `spin-resolved real(CDIJ) in LPRJ function
basis` is explicitly allowed for the controlled exchange trace. This was needed
because XML validation and exchange-trace operator allowlisting are separate
checks.

The real NiO `ISYM=2` XML from `/tmp/opencode/vasp_tb2j_validation` also runs
through the new API: `gen_exchange_vasp_projector_xml()` with `Rmax=0`, `nz=6`,
and magnetic atom indices `[0, 1]` writes an `exchange.out` with finite entries.
This validates the end-to-end source-writer/parser/Green/operator/exchange path
as a smoke test. The run is intentionally non-benchmark quality (`NELM=1`, short
seed density, explicit `LOCPROJ`) and should only be interpreted as integration
validation.

Follow-up check: adding `LORBIT=11` to the same NiO smoke input shows that the
DFT density itself is not symmetry-broken: VASP reports equal Ni charges
14.487/14.487, opposite Ni moments +1.694/-1.694, equal O charges 4.837/4.837,
zero O moments, and zero total magnetization. The original VASP XML
`exchange.out` example printed wrong charges/moments because TB2J used a generic
projector-population fallback on VASP `LPRJ_COVL` data. That fallback is not a
validated VASP local-population metric. The VASP XML exchange path now parses the
final VASP `LORBIT` site-projected charge/magnetization blocks from a companion
`OUTCAR` when available, or from the explicit `--outcar` CLI option, and copies
those values into `exchange.out`. If no OUTCAR is available, it still writes zero
placeholders and says so in the description.

Green-function population diagnostics were added after the OUTCAR-only fix.
`compare_green_to_vasp_outcar_populations()` computes site populations from the
projector Green function using `projector_charge_moments_from_green()` with
`CFR2`, then compares them with final VASP `LORBIT` charge/magnetization blocks.
`gen_exchange_vasp_projector_xml()` defaults to these Green-derived values and,
when an OUTCAR is available, raises if they do not match within tolerances. The
CLI exposes `--population_source {green,outcar,none}`.

The diagnostic also showed that matching VASP LORBIT requires the XML projector
basis to cover the same local channels. The Ni `d`-only smoke XML cannot match
VASP atom charges. A fuller explicit basis with Ni `s p d` radial channels
`Pr 1` and `Pr 2` plus O `s p : Pr 1` behaves differently depending on VASP
symmetry. With `ISYM=0`, Green-derived populations match that run's VASP OUTCAR
closely: charge differences are about `[-0.005, +0.002, -0.089, -0.083]` and
moment differences about `[+0.014, +0.015, +0.001, +0.003]`. With `ISYM=2`, the
VASP OUTCAR is AFM-symmetric but the Green-derived populations from XML differ by
`[+0.071, -0.079, -0.078, -0.116]` in charge and
`[+0.155, +0.167, -0.064, -0.083]` in moment, so the API now rejects that XML by
default. Testing `trace(G S)` and related overlap-metric contractions did not
restore the VASP LORBIT values, pointing to the symmetry-expanded projector
coefficient path rather than the population metric as the immediate issue.

The projector exchange API now supports a physical `Rcut` distance cutoff in
Angstrom, defaulting to `None`. For VASP XML, `Rmax` is optional and only bounds
the generated integer lattice-vector cube when explicitly supplied. A 5x5x5 NiO
`ISYM=0` full radial-channel example with `Rcut=8.0` writes
`/tmp/opencode/vasp_tb2j_validation/TB2J_results_vasp_xml_isym0_k555_Rcut8/exchange.out`
with 208 finite exchange entries.

## ISYM Safety Gate

Inspection of the VASP projection path confirmed that `LPRJ_PROALL` computes
`LPRJ_COVL` on the full k-point list by rotating wavefunctions through
`PEAD_WA_ROTATE`/`WA_ROTATE` before evaluating overlaps with locally generated
trial orbitals. No small writer-side indexing fix was identified during this
pass. Because the real NiO full radial-channel validation still shows that
`ISYM=2` Green-derived populations disagree with VASP OUTCAR while the `ISYM=0`
run agrees within tolerance, TB2J now refuses VASP XML generated with `ISYM>0`
for exchange generation by default.

The API override is `allow_symmetry_expanded=True`, and the CLI override is
`--allow_symmetry_expanded`. These are diagnostic-only escape hatches; the
validated production path remains VASP XML generated with `ISYM=0` until the
symmetry-expanded projector coefficient issue is fixed or otherwise validated.

The bcc Fe symmetry-on diagnostic confirms that both projector-basis completeness
and symmetry expansion matter. A single-radial `LOCPROJ = "1 : s p d : Pr 1"`
`ISYM=2` run in
`/tmp/opencode/bcc_fe_symmetry_validation/vasp_bcc_fe_sym_xml` produced full-BZ
XML with `nkpt=125`, `nband=9`, `nproj=9`, and finite operator data, but the
Green-derived population was far from the VASP OUTCAR value: charge `5.56863723`
versus `6.97600000`, and moment `0.29130100` versus `0.75800000`. A fuller
`s p d` `Pr 1` plus `Pr 2` run in
`/tmp/opencode/bcc_fe_symmetry_validation/vasp_bcc_fe_sym_xml_radial12` improved
the comparison to charge `6.51341489` versus `6.61900000`, and moment
`0.54348296` versus `0.53900000`. The moment is consistent, but the charge
difference `-0.10558511` is just outside the current `0.1` tolerance. The default
guard still raises the intended `ValueError`, while the explicit diagnostic
override writes `TB2J_results_vasp_bcc_fe_sym_radial12_Rcut6/exchange.out` with
65 entries and first-shell mean `0.07068643 meV`.

A matched bcc Fe `ISYM=0` validation in
`/tmp/opencode/bcc_fe_symmetry_validation/vasp_bcc_fe_nosym_xml_radial12` used
the same primitive cell, 5x5x5 k-mesh, `ENCUT=300`, `NBANDS=16`, and fuller
`s p d` `Pr 1` plus `Pr 2` LOCPROJ basis. The XML has `nkpt=125`, `nband=16`,
`nproj=18`, `nspin=2`, and does not need the symmetry override. Green-derived
populations match OUTCAR within tolerance: charge `6.60534173` versus
`6.66500000`, and moment `0.83855609` versus `0.86000000`. However, the exchange
shells remain far smaller than the GPAW PAW-projector result. With both outputs
using the full `Rcut=6.0` vector set (`65` entries), the VASP first-shell mean is
`0.15345 meV`, while GPAW gives `8.28330 meV`; VASP onsite is `42.8254 meV`,
while GPAW onsite is `904.2983 meV`. This indicates a remaining projector/operator
definition mismatch between VASP `LPRJ_COVL` plus projected `real(CDIJ)` and the
GPAW native PAW `P_ani` plus `dH_asp` workflow, not just a VASP symmetry issue.

Further VASP-side research isolated the mismatch more precisely. `LPRJ_COVL` is
an overlap with localized LOCPROJ trial functions, while `CDIJ` acts in the
native PAW projector channel basis used by `W%CPROJ`. Exporting native
`W%CPROJ` is therefore more consistent with `CDIJ` than exporting `LPRJ_COVL`.
However, VASP still stores `W%CPROJ` on a time-reversal-reduced `63`-point mesh
for `ISYM=0`; only `ISYM=-1` exposes the full `125`-point native projector mesh
for this Gamma-centered 5x5x5 bcc Fe case. A prototype writer path that uses
`W%CPROJ` when its k-point dimension already matches the XML full-BZ dimension
produces `coefficient_source="vasp.W_CPROJ"` for the `ISYM=-1` run in
`/tmp/opencode/bcc_fe_symmetry_validation/vasp_bcc_fe_nosym_minus1_xml_radial12`.
The first-shell exchange improves from the `LPRJ_COVL` value `0.15345 meV` to
`3.36656 meV`, closer to GPAW's `8.28330 meV`, but Green-derived populations are
unphysical (`green_charge=110.76073101`, `green_moment=52.10147612` versus OUTCAR
`6.672` and `0.976`). Raw `W%CPROJ` therefore still needs the correct VASP
normalization/metric/dual-basis treatment before it can replace `LPRJ_COVL` in a
validated exchange workflow.

The onsite spin potential also differs strongly between codes. For bcc Fe, GPAW
`Delta=dH_asp^up-dH_asp^down` has Frobenius norm `11.42584 eV`, trace
`-26.14578 eV`, and `trace(Delta S)=-47.38849 eV`; VASP `CDIJ^up-CDIJ^down` in
the same selected `s p d` two-radial channel set has Frobenius norm
`5.95871 eV`, trace `-9.94499 eV`, and `trace(Delta S)=-14.83085 eV`. The VASP
Delta is about a factor of two to three smaller in these onsite measures, which
contributes substantially to the smaller exchange even before coefficient-basis
differences are considered.

The low VASP XML-run LORBIT moment (`0.976`) was an artifact of doing the export
from random wavefunctions with `ICHARG=5`, `NELM=1`, and no `WAVECAR`. The
converged seed OUTCAR has total magnetization `1.98013` and site-projected
magnetization `1.977`, as expected for bcc Fe. A WAVECAR-based export in
`/tmp/opencode/bcc_fe_symmetry_validation/vasp_bcc_fe_isym_minus1_wave_xml_radial12`
uses `ISTART=1`, `ICHARG=5`, and reads the converged seed `WAVECAR`. The export
produces `coefficient_source="vasp.W_CPROJ"` and keeps the full `125` k-point
native projector mesh. The one-step export did not reach the final OUTCAR LORBIT
summary within the available runtime, but the XML was written and can be compared
to the completed seed OUTCAR. Relative to the seed OUTCAR, raw `W%CPROJ` Green
populations still fail (`green_charge=24.54214`, `green_moment=14.08383` versus
seed OUTCAR `7.141`, `1.977`), so the native coefficients still require a correct
normalization/metric treatment. The exchange first-shell mean improves to
`4.26968 meV`, closer to GPAW's `8.28330 meV` but still low by about a factor of
two. The VASP onsite Delta remains unchanged at `||Delta||_F=5.95878 eV`,
`trace(Delta)=-9.94500 eV`, and `trace(Delta S)=-14.83102 eV`.

Dense 9x9x9 bcc Fe tests show that k-mesh convergence explains part of the
remaining VASP/GPAW exchange difference. The GPAW 9x9x9 symmetry-on run in
`/tmp/opencode/bcc_fe_symmetry_validation/gpaw_bcc_fe_sym_k999` unfolds 35 IBZ
k-points to 729 full-BZ k-points, gives Green population charge `6.15252868` and
moment `2.14493165`, and writes first-shell exchange mean `8.06541306 meV` with
65 entries. The matching VASP `ISYM=-1`, WAVECAR-based, native-`W%CPROJ` XML run
in `/tmp/opencode/bcc_fe_symmetry_validation/vasp_bcc_fe_k999_wave_xml_radial12`
uses 729 k-points and gives first-shell mean `6.66196132 meV`, much closer than
the 5x5x5 WAVECAR result `4.26968 meV`. Seed OUTCAR has charge `7.154` and
site-projected moment `2.090`, but raw `W%CPROJ` Green populations remain
unphysical (`green_charge=24.82514864`, `green_moment=13.76581762`). The VASP
Delta increases slightly at 9x9x9 to `||Delta||_F=6.27510712 eV`,
`trace(Delta)=-10.46427245 eV`, and `trace(Delta S)=-15.62033648 eV`, still
substantially smaller than GPAW.

A focused source audit of the VASP exporter ranked the likely remaining bugs as
follows. First, native `W%CPROJ` is being inserted into an orthonormal spectral
Green formula, while VASP PAW projector amplitudes require the correct PAW
metric/dual treatment; this explains the unphysical raw `W%CPROJ` Green
populations. Second, the `LPRJ_COVL` path pairs LOCPROJ trial-function overlaps
with native PAW `CDIJ` subblocks, so the coefficient and operator bases are not
consistent unless `CDIJ` is transformed into the LOCPROJ basis. Third, native
`W%CPROJ` indexing through `LMBASE(poscar_site)+LMI` is fragile for multi-ion or
parallel runs and should be validated against VASP's serial projector indexing
(`NPRO_POS`/local ion maps). Other checks recommended by the audit are testing
the coefficient conjugation order in `ProjectorGreen`, forcing uniform full-BZ
weights, validating `CDIJ` hook timing, and reconstructing VASP's PAW density
using the same convention as `us.F::DEPSUM`.

The VASP XML exchange path now makes that second issue explicit in code. TB2J
rejects `vasp.LPRJ_COVL` coefficients with `vasp_cdij_paw_hamiltonian` operators
by default because this pairs LOCPROJ trial-function overlaps with native PAW
`CDIJ` matrices. Diagnostic runs can opt in with `allow_basis_mismatch=True` or
the `vasp_projector2J --allow_basis_mismatch` flag, but production exchange should
use native `W%CPROJ` with `CDIJ` or a future transformed LOCPROJ operator. The VASP
writer and schema text also now describe `CDIJ` as being in the native PAW
projector basis, not the LPRJ function basis.

Re-testing the 9x9x9 bcc Fe native `W%CPROJ` XML after this guard confirmed that
the native path does not need the basis-mismatch override. QTOT-projected XML
charge/moment `7.14189242`/`2.11876244` match the completed seed OUTCAR
`7.154`/`2.090` within tolerance, and `exchange.out` now writes those QTOT values
instead of the raw projector-Green diagonal population. The first bcc Fe shell mean
remains `6.661975 meV` at `2.477 A`.

## Native `W%CPROJ` population metric: `QTOT`

VASP's native PAW overlaps are $C_{i n\mathbf{k}\sigma} =
\langle\tilde p_i|\tilde\psi_{n\mathbf{k}\sigma}\rangle$.  They are
coefficients in a non-orthonormal all-electron partial-wave expansion, so the
raw projector-coordinate trace $\sum_i |C_i|^2$ is not a physical local charge.

For every pair of radial partial waves having the same angular momentum,
`radial.F::RAD_CHECK_QPAW` constructs VASP's `QTOT` as

$$
Q^{a}_{\mathrm{TOT},\,i l m,\,j l' m'} =
\delta_{ll'}\delta_{mm'}
\int_0^{R_{\mathrm{dep}}}
W^{a,\mathrm{AE}}_{i l}(r)W^{a,\mathrm{AE}}_{j l}(r)\,dr .
$$

Here $W^{\mathrm{AE}}$ is VASP's all-electron radial partial wave and
$R_{\mathrm{dep}}$ is the outermost augmentation radius. `QTOT` is real,
static, spin-independent, and dimensionless; it may have off-diagonal
elements between two radial channels with the same $l$. `writer.F` contracts
the same matrix as $C_i Q_{\mathrm{TOT},ji} C_j^*$ before applying occupations
and k-point weights to form its local PAW projected populations.

`QTOT` is not the PAW norm correction
$\langle\phi_i|\phi_j\rangle-\langle\tilde\phi_i|\tilde\phi_j\rangle$, is not
the compensation/augmentation moment `QPAW`, and is not the onsite potential
`CDIJ`. It reports the all-electron partial-wave population inside the PAW
augmentation sphere, not a whole-cell charge or a correlated-$d$ occupation
unless the channel trace is explicitly restricted to those $d$ channels.

The native VASP exporter version 5 writes each type's radial-channel `LPS`
labels and `QTOT` matrix. TB2J expands it over the matching $m$ channels into
`population_metric_matrix`, then computes contour populations as

$$
N^a_\sigma =
-\frac{1}{\pi}\operatorname{Im}\int_{\mathcal C}
\operatorname{Tr}\!\left[
G^a_\sigma(z)Q^a_{\mathrm{TOT}}
\right]dz,
\qquad
m^a_z=N^a_\uparrow-N^a_\downarrow .
$$

The metric is applied only at this observable readout. It must not be inserted
into the Green-function resolvent, inverted, or inserted into the LKAG
exchange trace, because `CDIJ` and `W%CPROJ` already share their native PAW
projector basis and exchange requires a consistent transformation of every
factor.

For the fresh two-atom bcc Fe run with Fermi--Dirac occupations
(`ISMEAR=-1`, `SIGMA=0.05 eV`), the QTOT-contracted contour gave charges
`7.2064891`, `7.2063932` and moments `2.0112186`, `2.0112240` $\mu_B$ for the
two Fe atoms. The final VASP `LORBIT` summary prints `7.206`, `7.206` and
`2.011`, `2.011` at its three-decimal precision. The earlier disagreement
under `ISMEAR=0` was an occupation convention mismatch: TB2J's CFR contour
implements Fermi--Dirac occupations, whereas VASP's Gaussian smearing does
not.

## Position Units

VASP `POSION` is in direct/scaled coordinates in the code path used by the XML
writer. TB2J `ProjectorGreenData.positions` and `SpinIO` expect Cartesian
Angstrom. The first VASP XML writer emitted `POSION` directly, which made
`exchange.out` distances wrong even though the cell was correct. For NiO this
made same-cell Ni1-Ni2 appear as `0.866 A` instead of a real-cell image distance.

The VASP writer now converts `POSION` to Cartesian positions before writing XML
and tags the array with `coordinate_system="cartesian" units="Angstrom"`. The
TB2J parser also converts legacy VASP XML files whose positions are untagged and
look like direct coordinates. The corrected VASP NiO `Rcut=8.0` output has the
same 270 Ni-Ni exchange entries as the GPAW comparison outputs.


## Stream Padding in Native `W%CPROJ`

VASP's `W%CPROJ` first dimension is the allocated `NPROD`, not necessarily the
physical total of per-ion PAW channels. `fast_aug.F::SETUP_AUG_DES` sets
`NPROD` to the smallest multiple of the band-parallel count `NB_PAR` that can
contain the physical `NPRO`; therefore an FeO run with 26 physical channels and
`NB_PAR=4` writes 28 rows. The exporter preserves that stream leading
dimension because it is the Fortran array stride, while its `ion_nproj` values
correctly describe the physical layout.

`read_vasp_native()` must read all stream rows, then retain exactly
`sum(ion_nproj)` rows before applying phase correction, building site slices,
or constructing the `QTOT` metric. It also ignores negative `LPS` sentinel
entries used to pad type metadata to the largest `LMAX`. The focused regression
test writes a version-5 stream with two padded rows and an `LPS=-1` sentinel.

This was validated on fresh two-atom FM FeO PBE and PBE+$U=5$ eV VASP 6.4.1
runs with `ISYM=-1` and a $7^3$ mesh: both 28-row streams reduce to 26 physical
projectors, and QTOT-contracted contour populations match final `LORBIT` charge
and moment output within $4.9\times10^{-4}$ electrons or $\mu_B$.

## SrMnO3 native-PAW shell-selection validation

The cubic ferromagnetic SrMnO3 PBE+$U=3$ eV calculation at
$a=\SI{3.810}{\angstrom}$ has a sixfold Mn--Mn nearest-neighbor shell at
$d=\SI{3.810}{\angstrom}$, not at $d=\SI{7.620}{\angstrom}$.  The saved
ISYM=-1 native stream gives $J_1=-4.7658$ meV; the ISYM=1 v6 stream gives
$J_1=-4.7677$ meV, a $0.041\%$ difference.

An ad-hoc paper-data extraction regex accepted only unsigned $J_\mathrm{iso}$
values.  It therefore skipped the negative $J_1$, $J_2$, and $J_3$ entries
and incorrectly selected the first positive fourth-shell value,
$+0.561$ meV at $d=\SI{7.620}{\angstrom}$.  This was a reporting error, not a
VASP calculation, native-stream reader, symmetry expansion, or R-grid error.
The existing R-grid contains the $\pm(1,0,0)$, $\pm(0,1,0)$, and
$\pm(0,0,1)$ nearest-neighbor translations.  Any future extraction must parse
a signed scalar and define $J_1$ as the smallest nonzero-distance shell.