---
type: Project Knowledge
title: ABINIT Unit Checker Extension
created: '2026-09-25'
updated: '2026-09-25'
status: draft
audience: development
artifact_role: guideline
---

# ABINIT Unit Checker Extension

This note covers extending a checker program (`tests_*.F90`) in an ABINIT
generated build on this workstation. A checker file in `src/<dir>/` does not
build by itself; register it first.

## Build registration

1. Append a `checkers` dict to `src/<dir>/abinit.src`:
   `checkers = { "test_<name>": [], }`. The list holds extra seed
   dependencies; use `[]` when the closure comes from the amf file.
2. Create `src/<dir>/abinit.amf` if absent, with the per-target link closure:
   `<test_name>_LDADD = ../95_drive/lib95_drive.a ... ../02_clib/lib02_clib.a ... $(LIBS)`.
   List the full archive set in abinit-binary link order, twice (module-level
   cycles need a second pass). The relative `../XX_lib/` paths are
   depth-invariant; copy a working amf from another directory and rename it.
3. Run `config/scripts/makemake` from the source root (it refuses elsewhere),
   then `./config.status src/<dir>/Makefile` in the build tree, then
   `make -C src/<dir> <checker_name>`. Only `abinit.src`/`abinit.amf` need a
   commit; `Makefile.am`/`Makefile.in` regenerate byte-identical.
4. CMake ignores checkers; no `CMakeLists.txt` change works or is consumed.

## Compile-rule pitfalls

- Per-target `tests_x_CPPFLAGS`/`_FCFLAGS` lines in abinit.amf do not reach
  the generated compile rule; do not add include directories that way. Expose
  the function through a thin public seam in an abinit-side module, for
  example `nc_dftu_zarot_for_symrec` wrapping `setsym_ylm` in `m_nc_dftu_gs`.
- Fortran forbids an internal procedure inside an internal procedure. Put
  helper subroutines at the program `contains` level, not inside a test
  subroutine.
- Register through `build-dev-autotools` (develop tree), configured with
  `CC=mpicc CXX=mpicxx FC=mpif90` only.

## Fixture hygiene for physics-unit checkers

- A fixed-point test needs a closed group. The set {E, c4z} has no fixed point
  because c4z^2 is missing; use the full cyclic set {E, c4z, c2z, c4z^3}.
- A transpose-convention mutation is invisible for orthogonal real-harmonic
  rotation matrices on a closed group (Z^T n Z versus Z n Z^T is R versus
  R^-1, identified by the average). Catchable classes: harmonic order,
  m-rotation row order, time-reversal conjugation, channel pairing. Keep
  fixtures non-axial (spin-mixed, non-diagonal).
- With `-finit-real=nan`, fill a conjugate-symmetry pair (`n(4,a,b) = conjg(n(3,b,a))`)
  in a second pass; a same-loop fill reads unwritten entries and spreads a NaN (not a number).
- Seed hermiticity needs real parts symmetric in (a,b) and imaginary parts `(a-b)`
  times an (a,b)-symmetric phase; `sin(1.7a+0.5b)` silently breaks hermiticity.
- `-fcheck=all` catches explicit array bounds but not argument-mismatch
  sequence association. gfortran `maxval` can skip NaN; detect NaN with
  `any(x /= x)`.
