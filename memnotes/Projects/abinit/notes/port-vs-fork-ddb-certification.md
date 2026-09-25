---
type: Project Knowledge
title: Port-vs-Fork DDB Certification (NC DFT+U)
description: Certify an NC DFT+U port DFPT perturbation family against the fork binary via matched-tolerance twin DDBs, family-wise diffs, U0/native bitwise controls, and expected-abort guards.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
tags: [abinit, dftu, dfpt, ddb, port, certification]
---

# Port-vs-Fork DDB Certification (NC DFT+U Port)

Use when certifying a new DFPT (density-functional perturbation theory) perturbation
family or wave of the NC DFT+U manual port in `abinit_dftu_nc_dev` against the fork
reference binary.
## Procedure
1. **Binaries**: port `build-wave7-makemake/src/98_main/abinit`; fork
   `abinit_aicoding/abinit_dev_clean/build_wann/src/98_main/abinit` plus its `anaddb`.
2. **Build mirror trap**: the port build compiles from the mirror
   `/STORAGE1/hexu/projects_bak/ABINIT_dev_data/scratch/u0_gga_frame_probe`. After editing
   any file in the port tree, `cp` it to the mirror and `rm -f` the mirror's `.o` before
   `make -C build-wave7-makemake`. Other files may also have drifted; `diff -rq` the
   changed directories and sync everything that differs before trusting a result.
3. **Twin fixtures**: run the identical `.abi` on both binaries with matched tolerance
   (`tolvrs` identical on both sides). Fork legacy runs at looser tolerance give ~1e-5
   agreement; matched tolerance gives ~1e-7.
4. **Family-wise DDB diff**: parse both DDBs (the `parse_ddb` helper; keys
   `(idir1,ipert1,idir2,ipert2)`). Classify records into atom-atom, atom-strain, or
   strain-strain by `ipert` vs `natom`. Compare real and imaginary parts per family.
   Gates: <= 1e-6 to 1e-7 per family; imaginary part exactly 0.
5. **U0/native bitwise control**: twin `usedftu_nc 1, dftu_u 0` vs `usedftu_nc 0` must be
   bit-identical. This isolates the U-free response/XC chain.
6. **Coupling coverage rule**: validate cross-perturbation ledger terms on a system where
   the coupling is physically nonzero (example: Si internal strain). NiO rocksalt
   atom-strain rows are structural zeros and mask missing terms; this hid a 0.137 Ha
   defect.
7. **Transpose asymmetry**: large DDB asymmetry (1e-2 to 1) can be intrinsic to the ledger
   in BOTH codebases. Always run the fork before diagnosing a port defect.
8. **Expected-abort guards**: mutate the fixture per unsupported combination and assert
   abort plus message. Check whether upstream silently neutralizes the input first
   (example: spinor runs force `istwfk=1`) before calling a guard gap.
9. Record results in `port_report/debug/`. Flip `deferred_flags.yaml` and
   `coverage-map.md`. Append the kosmic log.
## Fortran gotchas in this build
- Conditionally-allocated locals with `if (allocated(x)) ABI_FREE(x)` trip gfortran
  `-fcheck=all` deallocate errors on never-allocated paths. Allocate unconditionally
  instead.
- Mixed perturbation pairs: check per-routine early `return` guards (`ipert > natom` and
  similar). A silently-zero call stays invisible until a physically-nonzero fixture
  exercises it.
