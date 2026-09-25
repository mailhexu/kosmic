---
type: Project Knowledge
title: ABINIT Unit Checker Registration
created: '2026-09-25'
updated: '2026-09-25'
status: draft
audience: development
artifact_role: guideline
---

# ABINIT Unit Checker Registration

ABINIT standalone unit checkers (sympy-validated invariants, adapter tests) are
`tests_*/test_*` executables registered per source directory; the generated
CMake build ignores them.

## Registration steps

1. Write the checker as `src/<dir>/test_<name>.F90`: one program, raw
   `use mpi` plus MPI_Init/MPI_Finalize, exit status 1 on failure.
2. Append to `src/<dir>/abinit.src`:
   `checkers = { "test_<name>": [], }`. The list holds extra seed libraries;
   abinit.amf completes the closure.
3. Create or extend `src/<dir>/abinit.amf` with the link closure; copy the
   proven pattern from `src/66_nc_dftu/abinit.amf` or
   `src/72_response/abinit.amf`. A `test_<name>_LDADD` carries the full
   internal archive list in abinit-binary link order, listed twice for
   module-level cycles, plus `$(LIBS)`. The `../<lib>/lib<lib>.a` paths are
   depth-invariant; copy them verbatim.
4. Run `config/scripts/makemake` from the source root. It refuses other
   directories and needs no reconfiguration.
5. In the build tree run `./config.status src/<dir>/Makefile`; the amf is
   inlined at configure/config.status time. `Makefile.am`/`Makefile.in`
   regenerate byte-identical when only checkers change.
6. Run `make -C src/<dir> <checker_name>`, then run the binary.

## Gotchas (each one hit in practice)

- The checker target does not rebuild stale `.mod` files (the generated
  Makefile has no mod-dependency edges for checker programs). After a change
  to a used module, run `make -C src/<dir>` first, or the checker compiles
  against a stale mod.
- A hand-added per-target `tests_..._CPPFLAGS` is overridden by the generated
  assignment; amf include directories do not work. Expose the need through a
  thin public wrapper in the checker own directory, for example
  `nc_dftu_zarot_for_symrec` wrapping `setsym_ylm` (avoids libpaw modules).
- Fortran forbids internal procedures inside internal procedures. Put helper
  subroutines at the program `contains` level, after the last test subroutine
  and before `end program`; pass anything from a test scope as an argument.
- With `-finit-real=nan`, a conditionally filled variable (second-pass fills,
  partly written `intent(out)`) reads NaN deterministically; complete fills
  before any earlier-pass read.
- `-fcheck=all` catches explicit array out-of-bounds but not argument mismatch
  or uninitialized reads through sequence association. Do not rely on it.

## Reference implementations

- `src/66_nc_dftu/tests_nc_dftu_spinor_response.F90` (+ abinit.src + amf):
  multi-case checker with a `report()` helper and `stop 1` on failure.
- `src/72_response/tests_ddb_bec_merge.F90` repeats the pattern; `src/64_psp/test_upf2_javerage_chi.F90` is a minimal-dependency adapter test.
