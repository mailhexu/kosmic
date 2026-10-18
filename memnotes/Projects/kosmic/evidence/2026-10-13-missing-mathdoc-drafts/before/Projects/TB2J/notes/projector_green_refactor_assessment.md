---
audience: both
okf_version: "0.2"
type: research
artifact_role: knowledge
status: stable
created: 2026-10-03
updated: 2026-10-04
---

# Projector Green refactor: runtime evidence and complex convention

## Existing runtime cost

In `TB2J/projector_green.py`, `ProjectorGreen.get_Gk` and `get_Gk_all` call `_contravariant_Gk` and `_inverse_overlap` at every energy and spin. The spinor implementation in `SPLIT_SOC` repeats the overlap/filter construction through `get_Gk_spinor`. The overlap, mode, and cutoff are energy independent. PAW already bypasses overlap dressing when `overlap_k` is absent; the runtime does not identify projector orthogonality from PAW augmentation matrices.

The local checked-out repo was detached at `3903710`; it lacks the spinor path present in the integrated `SPLIT_SOC` branch. A separate branch `projector-green-unified` was created from `SPLIT_SOC` at `0ee942c` with worktree `/home/hexu/projects/TB2J_dev/.tmp/wt-projector-green-unified`. No implementation changes have been applied there.

## Complex coefficient convention

The actual code uses $G_{pq}=\sum_n C_{np}C_{nq}^*g_n$, i.e. $G=C^TgC^*$, not $C^\dagger gC$. For Hermitian $F$, coefficient-side dressing in this storage convention is

$$
D=CF^T,\qquad D^TgD^*=FGF.
$$

An exact SymPy calculation with complex rational matrices verified this identity and rejected the naive $D=CF$ replacement. The October 2 unification script used real matrices and therefore did not distinguish those conventions. Any refactor must preserve the production conjugation placement; the coefficient-side notation in the October 2 paper section needs a convention-aligned correction if used as implementation guidance.

## Executed assessment

A throwaway probe exercised the actual `ProjectorGreen` backend with three k points, two spins, 48 bands, 16 channels, twelve complex energies, complex Hermitian overlaps, distinct spin Fermi levels, and optional band masks. Inverse, SVD, Lowdin, Tikhonov, and plain modes all agreed with coefficient-side dressing, including R-space Green matrices and an actual exchange-trace invocation. Maximum matrix absolute difference: $8.539\times10^{-16}$.

Each dressed mode constructed its filter 72 times for 24 energy/spin calls across three k points. A prepared implementation needs only three filters for this workload. Measured existing contraction plus metric processing took 0.0118–0.0139 s; a contraction over pre-dressed coefficients took 0.0040–0.0045 s. Those latter timings exclude preparation and extra coefficient storage: they are not an end-to-end exchange benchmark or a promised speedup. Plain mode showed no meaningful expected gain.

## Conservative refactor scope

Cache energy-independent channel filters and share their use between collinear and spinor spectral paths. Do not allocate a second full band/coefficient tensor by default. Preserve raw coefficients for populations, the existing overlap modes/cutoffs/precedence, phase conventions, Fermi shifts, operator-component selection, and NetCDF/CLI behavior. Evaluate full coefficient preparation only with memory and end-to-end timing evidence.

## QE leverage

The real seam is exporter-specific channel/operator interpretation versus a code-independent spectral/trace runtime. A QE adapter can provide either canonical dual coefficients or primal coefficients and their declared channel Gram. QE's `qq_at` generalized-wavefunction augmentation must not be used automatically as that Gram; native beta-channel operator factors and basis covariant operator matrices must not be interchanged without transforming both. Smooth spin-dependent potentials and US/PAW one-center contributions remain QE-specific work.

Related: [metric unification research](../subprojects/projector-green-unified/specs/research/2026-10-02-projector-green-metric-unification.md), [refactor PRD](../subprojects/projector-green-unified/specs/prd.md).

## Architecture investigation: live cache semantics and fixtures

The approved PRD now has a [draft architecture](../subprojects/projector-green-unified/specs/architecture.md). Source inspection and an actual-backend probe confirmed that reconstruction observes overlap matrix edits and public mode/rcond/condition-threshold changes after first use. A cache prototype retains exact per-k source snapshots with one active settings configuration. It reused two filters across repeated energies/spins, rebuilt only the edited k-point filter, handled replacement/settings transitions, and preserved the error after a valid-to-singular matrix change. This is a throwaway instance-level prototype, not a package implementation.

A complex nonorthogonal spinor probe exercised masks, all five modes, Green/R-space reconstruction, and tangent traces. Cached and uncached results agreed exactly in that probe; it built three filters for three k points, or zero for plain mode. No permanent test was added during architecture research.

Real exported fixtures loaded and produced finite traces on the isolated integrated baseline:

- `mypapers/TB2J_projector/data/bccFe/abinit_upf/TB2J_results/PAO_HS.nc`: `load_abinit_nc_pao_savetb2j`; `(2,343,24,10)` coefficients; k-dependent overlap; scalar trace with Tikhonov/rcond `1e-4`.
- `mypapers/TB2J_projector/data/bccFe/gpaw/gpaw_bccfe.nc`: `ProjectorGreenData.load_netcdf`; `(2,343,24,18)` dual coefficients; scalar trace.
- `mypapers/TB2J_projector/data/soc_consistency/CrI3/GPAW/nc_soc/cri3_nc_soc.nc`: `ProjectorGreenData.load_netcdf`; `(1,64,240,2,114)` dual spinor coefficients; tangent trace.

These fixture runs used one complex energy and three R vectors. They establish supported loader/trace reachability, not full contour-integrated exchange equivalence or production performance. The initial canonical-reader invocation used the wrong method name and was corrected to the source-defined `load_netcdf` before the PAW/spinor probes succeeded.

Default design keeps Green-side dressing with cached filters, rather than a second full coefficient tensor. Filter snapshots add matrix-sized memory and an exact equality scan; benchmark both cold and warm runtime plus memory during implementation. No code or schema cutover has happened yet.

## Outcome (2026-10-06)

Implemented on `projector-green-unified` (commits `38018a0`, `5ad338e`). Measured on the real NC fixture (343 k, 12 energies, 2 spins): 343 filter builds cold (vs 8232 repeated pre-refactor), zero on warm pass, +3.15 MiB peak extra; contour/population/tangent values on NC, PAW, and spinor fixtures identical to the pristine `0ee942c` baseline. Review: approve-with-nits, nits fixed (private cache pins removed from permanent tests; helper deduplicated into `tests/utils/projector_filters.py`). See `log/TB2J-2026-10-06.md`.
