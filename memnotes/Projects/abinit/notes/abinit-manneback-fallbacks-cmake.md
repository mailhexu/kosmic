---
type: Project Knowledge
title: ABINIT on Manneback with Fallbacks
created: '2026-09-25'
updated: '2026-09-25'
status: draft
audience: usage
artifact_role: guideline
---

# ABINIT on Manneback with Fallbacks

Build ABINIT (multibinit) on manneback, keira partition, with out-of-tree CMake against `~/mboom/fallbacks-install`; connect with `rtk ssh manneback '...'`. Each blocker below causes a fast, wrong-looking failure.

## Job environment and build

```bash
export PATH="$SLURM_SUBMIT_DIR/fallbacks/m4bin:$PATH"   # m4 fix
source /usr/share/lmod/lmod/init/bash
export MODULEPATH="/opt/sw/noarch/meta_modules:/opt/sw/noarch/easybuild/tis-2018.01/modules/all:/opt/sw/arch/manual/tis-2018.01/modules/all:/opt/sw/noarch/manual/tis-2018.01/modules/all:/opt/sw/arch/easybuild/2024a/modules/all:/opt/sw/noarch/easybuild/2024a/modules/all:/opt/sw/noarch/manual/2024a/modules/all"
module purge
module load GCC/13.3.0 MPICH/4.2.2-GCC-13.3.0 CMake/3.29.3-GCCcore-13.3.0 OpenBLAS/0.3.27-GCC-13.3.0
export PKG_CONFIG_PATH="$SLURM_SUBMIT_DIR/fallbacks-install/libxc/7.0.0/lib/pkgconfig"
pkg-config --modversion libxc || exit 1
```

Submit with `cd ~/mboom && sbatch --chdir=$HOME/mboom jobN.sh` (typical header `-p keira -N 1 -c 32 -t 8:00:00 --mem=100G`).
The login-node module system does not see this MODULEPATH tree. Compute nodes lack m4; `fallbacks/m4bin` holds a
libc-only `/usr/bin/m4` copy, or the fallbacks netCDF configure fails with `Cannot find m4 utility`.

```bash
rm -rf abinit/build-mpi
cmake -S abinit -B abinit/build-mpi -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_Fortran_COMPILER=mpif90 -DCMAKE_C_COMPILER=mpicc -DCMAKE_CXX_COMPILER=mpicxx \
  -DCMAKE_Fortran_FLAGS_RELEASE="-O2 -fbacktrace [-DABINIT_ALLOC_GUARD]" \
  -DCMAKE_PREFIX_PATH="$SLURM_SUBMIT_DIR/fallbacks-install" \
  -DABINIT_FFT_FLAVOR=GOEDECKER -DABINIT_ENABLE_MPI_IO_DEFAULT=ON -DABINIT_ENABLE_PARALLEL_HDF5=ON \
  -DBLAS_LIBRARIES="$EBROOTOPENBLAS/lib/libopenblas.so" \
  -DLAPACK_LIBRARIES="$EBROOTOPENBLAS/lib/libopenblas.so" > cmake_mpiN.log 2>&1 || { tail -40 cmake_mpiN.log; exit 1; }
cmake --build abinit/build-mpi --target multibinit -j 32 > make_mpiN.log 2>&1 || { tail -50 make_mpiN.log; exit 1; }
```

## Blockers and run hygiene (verified 2026-09-24)

1. libxc: ABINIT finds it through pkg-config, not CMake config files. `fallbacks-install` ships only
   `libxc/7.0.0/lib/pkgconfig/libxc.pc`; without the `PKG_CONFIG_PATH` export, configure fails in
   `find_package(Libxc)` and looks like a missing CMake package. Loaded easybuild modules never cover
   fallbacks; set the path explicitly.
2. GCC 13 fails to build two optional fallback components: bigdft (`flib/getadd.f90`) and wannier90
   (`postw90/comms.F90`, MPI_bcast REAL(8)/COMPLEX(8) mismatches); multibinit needs neither. Touch
   `fallbacks/stamps/{bigdft,wannier90}-{build,install}-stamp` so a `make install` resume never
   retries them.
3. No `libhdf5_fortran` in `fallbacks-install`; only C `libhdf5`/`libhdf5_hl` plus netcdf4/netcdf4_fortran
   (4.9.3/4.6.2) in versioned subdirectories. Sanity-check only `libnetcdff libnetcdf libhdf5` in `fallbacks-install/lib/`.
4. Instrumented builds: never trust "no breadcrumb output"; a stale build silently loses call sites. Gate with
   `nm -C $BIN | grep -m3 abi_alloc_guard || exit 1` and confirm linkage with `ldd $BIN | grep -iE 'mpi|netcdf|hdf5|blas'`.
5. Memory attribution: fresh directory per test (copy `.abi` plus `.nc`), `/usr/bin/time -v`, and
   `srun --mem=0 --mpi=pmi2 --exclusive -n 1` to mirror the buildbot launcher; a build plus 4 test runs takes
   1.5 to 2.5 h on 32 cores; poll `/proc/<pid>/status` VmRSS in a background loop. Serialize build phases on one
   tree: a concurrent `make` or `rm -rf abinit/build-mpi` leaves a half-destroyed directory; always `rm -rf` and reconfigure at job start.
