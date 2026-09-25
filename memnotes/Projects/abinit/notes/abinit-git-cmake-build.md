---
type: Project Knowledge
title: ABINIT CMake Build from Git
created: '2026-09-25'
updated: '2026-09-25'
status: draft
audience: usage
artifact_role: guideline
---

# ABINIT CMake Build from Git

An ABINIT git checkout ships no generated `configure` script; build git checkouts with CMake. Do not run
`autoreconf`: it emits a broken `configure` with unexpanded `ABI_*` macros; delete any generated script. Release tarballs keep a working `configure`; this note does not apply to them.

## Configure

Module stack (example: CÉCI 2025b gcc): load the modules, then run:

```bash
module load <GCC> <OpenMPI> <FlexiBLAS> libxc netCDF-Fortran FFTW.MPI <CMake>
cmake -S <src> -B <build> \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=<prefix> \
  -DCMAKE_Fortran_COMPILER=mpif90 -DCMAKE_C_COMPILER=mpicc -DCMAKE_CXX_COMPILER=mpicxx \
  -DCMAKE_Fortran_FLAGS_RELEASE="-O2 -march=native" \
  -DBLAS_LIBRARIES=$EBROOTFLEXIBLAS/lib/libflexiblas.so \
  -DLAPACK_LIBRARIES=$EBROOTFLEXIBLAS/lib/libflexiblas.so
```

CMake resolves libxc, FFTW, netCDF, netCDF-Fortran, and HDF5 through pkg-config.
GPU, TRIQS, wannier90, and ScaLAPACK default to OFF; leave OFF, because OFF avoids
FetchContent downloads. No-modules workstation (Ubuntu, system Message Passing Interface): same command minus `module load`, with explicit system math libraries:

```bash
cmake -S <src> -B <build> ... \
  -DABINIT_FFT_FLAVOR=GOEDECKER \
  -DBLAS_LIBRARIES=/usr/lib/x86_64-linux-gnu/libopenblas.so \
  -DLAPACK_LIBRARIES=/usr/lib/x86_64-linux-gnu/libopenblas.so
```

The Ubuntu fftw3 package ships the runtime library only, with no headers and no
pkg-config file. `-DABINIT_FFT_FLAVOR=GOEDECKER` selects the internal ABINIT
fast Fourier transform (no external link flags); OpenBLAS covers Basic Linear Algebra Subprograms (BLAS) and Linear Algebra Package (LAPACK).

## Two known configure failures

1. CMake stops at the levmar block near line 578 with `Unknown CMake command
   "check_include_file"`; add `include(CheckIncludeFile)` above the levmar
   `find_library()`. CMake 3.31 hits this bug too, not only CMake 4.
2. `mv: cannot stat .../m_cppopts_dumper.F90`: the `execute_process` pipeline starts
   `mv` while the python writer still runs; run `python3 config/scripts/make-cppopts-dumper`
   in the source root first.

## Build, install, verify

Run heavy compiles on a queue node: `cmake --build <build> -j 64`; pass `--prefix` explicitly
to `cmake --install` if the configured prefix changed. Do not rename source or build
directories after configure (cache holds absolute paths); incremental resume works. At runtime set
`ABI_PSPDIR=<tree>/tests/Pspdir`. Verify with one nsppol=2 branch test (v10/t85; ABINIT 10 chkinp aborts
without `spinmagntarget`) and with `tests/v9/Input/t112.abi`: it reproduces `tests/v9/Refs/t112.abo` to 6 digits in about 2 s at `-np 8`.
