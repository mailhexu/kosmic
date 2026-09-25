---
type: Project Knowledge
title: ABINIT Wave-6 Build and Runtime Validation
created: '2026-09-25'
updated: '2026-09-25'
status: draft
audience: development
artifact_role: guideline
---

# ABINIT Wave-6 Build and Runtime Validation

Validate NC DFT+U port changes on both build systems, CMake and makemake/configure; each catches different failures.

## Sync source registrations

- CMake: add the file to the `add_library` list in `src/<dir>/CMakeLists.txt`.
- Autotools: add the file to the alphabetical `sources = [...]` list in
  `src/<dir>/abinit.src`; regenerate with `python config/scripts/makemake`.
- Checkers/programs: declare in abinit.src, e.g. `checkers = {"name": ["39_libpaw"]}`; never hand-edit a generated `Makefile.am`.

## CMake build failures

- The 66_nc_dftu and 66_nonlocal targets form a link cycle. Split
  `m_nc_dftu_data.F90` into its own `66_nc_dftu_data` STATIC target; both link it.
- `m_fft.mod` is missing in 65_pao. Add `abinit::53_ffts` to `target_link_libraries`.
- `if (allocated(x)) ABI_FREE(x)` guards only the first macro statement; the
  unguarded deallocate aborts with `Attempt to DEALLOCATE unallocated`. Use
  `ABI_SFREE(x)` (guarded block) or explicit if/then/endif; freeing an array
  of types still needs an explicit element-wise loop plus a block.

## GNU Make validation flow (serial, resumable)

```bash
python config/scripts/makemake
mkdir -p build-wave6-makemake && cd $_
FC=mpif90 CC=mpicc CXX=mpicxx ../abinit/configure
make -j 1        # full ordered build; 15 min or more
make check       # in src/<dir>, runs the declared checkers
```

A partial `make -C src/66_nonlocal` fails on missing prerequisite `.mod` files; build at the
top level. Launch long builds through the hub daemon; incremental resume after a fix works.

## Runtime smoke and Gamma acceptance (two-atom NiO)

A deprecated `.files` input needs exactly 6 lines: abi, abo, input root, output root, tmp
root, then one pseudo path per pseudo type. A wrong count aborts at outvars with the NetCDF
error `Parallel operation on file opened for non-parallel access` (MPI_ABORT, exit 14).

Gamma packed-spinor DFPT acceptance: `wave6_smoke/gamma_u.abi` (U on, dftu_u=0.294) plus
`gamma_u0.abi` (U=0 control), ndtset 2 (ground state plus Gamma rfphon); `wave6_smoke/check_gamma_smoke.py` asserts:

- source-FD relative error below 1e-6 (current 5.09e-13);
- U-on source norm above 1e-8 (current 8.92e-3);
- U=0 source and V1 identically zero;
- 36 Derivative DataBase (DDB) entries per run;
- nonzero U-on/U=0 DDB delta (current 83.62 Ha).

Re-run from the current binary for any rebaseline; never promote saved pre-refactor artifacts.
