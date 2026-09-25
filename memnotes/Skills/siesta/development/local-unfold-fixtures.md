---
type: Domain Topic
id: siesta/development/local-unfold-fixtures
domain: siesta
audience: development
artifact_role: guideline
status: draft
summary: Build a local serial SIESTA binary on this workstation and regenerate unfolding Si fixtures with a k-grid SCF (SIESTA 5.4 fdf rules).
triggers: [local siesta build, unfolding fixtures, SaveHS TSHS crash, siesta 5.4 fdf]
source_project: native
source_sha256: empty
aliases: [siesta local build]
---

# Local SIESTA Build + Unfolding Fixture Regeneration

Use when the unfolding project needs SIESTA-produced fixtures
(HSX/WFSX/EIG) on this workstation, or a local binary for small SCF runs.
## Local binary
- Working build: `~/projects/siesta_git/siesta_spinor/_build/build_gcc13/Src/siesta`
  (serial, gfortran-13).
- Configure:
  ```bash
  cmake -S ~/projects/siesta_git/siesta_spinor \
        -B ~/projects/siesta_git/siesta_spinor/_build/build_gcc13 \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_Fortran_COMPILER=gfortran-13 -DCMAKE_C_COMPILER=gcc-13 \
        -DSIESTA_WITH_MPI=OFF -DSIESTA_WITH_LUA=OFF -DSIESTA_WITH_CDF=OFF
  cmake --build <build_dir> -j 16
  ```
- MPI=OFF is required: the system OpenMPI mpi.mod is gfortran-15-built
  and gfortran-13 cannot read it. Lua=OFF: no system lua.h. CDF=OFF: HSX
  runs need no netcdf-fortran.
- Si.psf lives at
  `~/projects/siesta_git/siesta_spinor/Examples/Si_Optical/Si.psf`.
## fdf rules (SIESTA >= 5.4)
- Write `SaveHS true`. NEVER `SaveHS TSHS`: fdf_boolean rejects the value
  and the crash surfaces as a libfdf "End of record" internal-write error
  in the error branch, masking the real message. A gfortran-15 build
  crashes identically.
- Put `WaveFuncKPointsScale ReciprocalLatticeVectors` before any
  `%block WaveFuncKPoints` in non-orthorhombic cells. The default pi/a
  scale fails the orthorhombic check on fcc cells and silently zeroes the
  k-point list (nwk=0, no WFSX).
- Run as `siesta file.fdf` (argument form). The binary is serial; do not
  wrap in mpirun (scratch-file races).
## Unfolding fixture rule

Gamma-only SaveHS runs write a Gamma-collapsed Hamiltonian (nsc=1,
single R=0 shell): H(k) is k-independent and generic-k unfolding plots
flat bands. Supercell fixtures for unfolding MUST use a k-grid SCF
(2x2x2 on the 8-atom Si cell gives a 125-shell HSX). Regenerate the
whole fixture pair (prim + sc) from the same build and pseudopotential so
seals stay self-consistent; verify with the project test suite
(story-010 seals in tests/test_siesta_example.py).
## Weight method

`LCAOUnfolder.compute(kpts, method="ring")` is exact only at
torus-commensurate momenta. Generic k-paths need `method="ideal"`
(Popescu-Zunger/Lee). Ring is fine for Gamma-only seals.
