---
type: Project Knowledge
title: ABINIT Makemake Build Tree Pitfalls
created: '2026-09-25'
updated: '2026-09-25'
status: draft
audience: development
artifact_role: guideline
---

# ABINIT Makemake Build Tree Pitfalls

## Scope

This note covers the `build-waveN-makemake` out-of-tree builds of the
`abinit_dftu_nc_dev` tree. These builds compile from a mirror source root,
`/STORAGE1/hexu/projects_bak/ABINIT_dev_data/scratch/u0_gga_frame_probe/abinit`,
not from the active tree. The Makefiles know only the mirror.

## After you edit sources in the active tree

1. Copy each edited file into the mirror tree with
   `cp active/src/... /STORAGE1/.../abinit/src/...`. The build never sees the
   active tree, so a skipped copy silently rebuilds old code.
2. If a module public interface changed, also `touch` every consumer source in
   the mirror, for example `m_dfpt_scfcv.F90`. The generated Makefiles do not
   track `.mod` dependencies. Consumers then keep stale objects that reference
   bare external names, and the link fails with `undefined reference to name_`.
3. Build with `make -j2` and never higher. The machine runs under memory pressure.

## Public symbols in private-by-default modules

`m_nc_dftu_data.F90` and similar modules declare `private` plus explicit
`public ::` lists. A new procedure without a `public ::` line compiles with the
warning `defined but not used`. gfortran then drops the symbol from the object
file, and the link fails. Always add the `public ::` line for a new public kernel.

## Verify a new symbol

After the build, run
`nm build/src/66_nc_dftu/m_nc_dftu_data.o | grep <new_symbol>`.
The gfortran mangled name has the form `__m_nc_dftu_data_MOD_<name>`.
A hit proves the object file exports the symbol.
