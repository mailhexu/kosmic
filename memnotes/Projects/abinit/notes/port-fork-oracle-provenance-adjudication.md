---
type: Project Knowledge
title: Port-vs-Fork Oracle Provenance Adjudication
description: Adjudicate ABINIT port-vs-fork numeric regressions by oracle provenance, cross-build A/B on identical inputs, and per-leg source-norm probes before touching source.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
tags: [abinit, dftu, dfpt, oracle, fork, adjudication]
---

# Port-vs-Fork Numeric Regression Adjudication

Use when a ported ABINIT response observable (DDB elements, eps_inf, Z*, phonons)
disagrees with a fork "oracle". Pin whether the defect is the port, the fork lineage, or
the oracle's run provenance BEFORE editing source.
## Procedure
1. **Oracle provenance first.** Check the oracle's producing log: file mtime, `mpi_nproc`,
   binary banner and version. An oracle produced by an older build under MPI may be
   unreproducible by BOTH trees serially. The published number can be lineage-specific or
   run-specific, not ground truth for the current build.
2. **Cross-build A/B on byte-identical inputs.** Run the ORIGINAL fixture (only absolutize
   `pp_dirpath`; add nothing else) serially on the port binary and the fork binary at a
   reduced mesh (example 4x4x4) for speed. Compare DDB elements elementwise: regex-parse
   `d1 p1 d2 p2 value` lines after the last `2nd derivatives` marker. port == fork !=
   oracle: the port is exonerated; the oracle is run-specific or lineage-specific
   (case iii); do NOT patch the port to chase the oracle. fork == oracle, port differs:
   real port defect; diff deeper.
3. **Fork git archaeology.** Build the fork at the oracle-date commit
   (`git clone --shared` into `.tmp`; mirror the existing build directory's CMakeCache and
   configure). Re-run. Walk commits between the oracle date and HEAD if needed. Record the
   flipping commit and its hunks.
4. **Per-leg source-norm probe.** For response-source suspects (DDK, electric), run a
   single-perturbation leg with `prtvol 20` on both builds reading the SAME GS WFK. Use
   the global `getwfk_filepath`, never the dataset-suffixed `getwfk2_filepath`
   (unregistered), and never chain `getwfkN` together with a global filepath
   (irdwfk/getwfk conflict). Compare the printed `NC DFT+U DFPT local source norm` lines.
   A large norm ratio (example 18x) localizes the defect to that source's construction
   with file:line precision.
5. **Scope fixes by representation.** A formula fix validated on one representation
   (spinor FD oracles) can be a regression on another (scalar QE-consistent oracle). Gate
   corrected formulas by `my_nspinor`; keep each representation's own validated form.
   Regression-check BOTH: spinor fixture vs pinned ref; scalar fixture vs fork oracle.
## Known traps
- The G7 contract item "never apply a gprimd^T gprimd contraction" is right for the
  SPINOR DDK source. The SCALAR DDK source empirically requires the fork-Jun metric
  contraction (`gprimd^T gprimd` plus rprimd limit rows). The direct-component form
  overestimates ~18x and doubles eps_inf and |Z*|.
- Fork oracles `example_NiO_FM/dfpt/outputs/nio_fm_dfpt_noistwfk_*` came from a Jun-25
  20-rank MPI run of an older fork build. Serial re-runs of ANY current build give the BAD
  family.
- Multi-dataset restarts: global `getwfk_filepath` + `getden_filepath` with `getddkN`
  chaining works. Remove chained `getwfkN`/`getdenN`. `rsync` without `-L` copies dangling
  symlinks to nic6.
- `rm -f runo_*` before re-runs also deletes staged GS WFK/DEN restart files living in the
  same directory. Restage them.
- anaddb single-q protocol: `ngqpt 1 1 1` with `q1shft` equal to the DDB's stored q (read
  the ` qpt ` line). Otherwise ABINIT prints "Information is missing in the DDB".
