---
type: Project Knowledge
title: ABINIT Instrumented-Dump Recipe
description: Per-call Fortran instrumented dumps for isolating ABINIT numerical defects - gating, placement, parsing, analysis, and verified conventions.
confidence: 0.8
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Re-run one gated dump cycle against a verified identity on a current ABINIT tree before promotion."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, instrumentation, dumps, diagnosis, stress]
---

# ABINIT Instrumented-Dump Recipe

## Scope

Attribute a numerical defect, for example a finite-difference (FD) versus analytic stress residual, to a kernel layer. Insert temporary Fortran `write` dumps at the suspected site, rebuild, run a small fixture, and compare against an independent Python reference. This note merges two managed skills. `abinit-instrumented-dump-campaign` supplies the cycle, placement traps, verified conventions, and environment. `abinit-fd-audit-instrumented-dump-recipe` supplies the edit traps and the analysis discipline.

## Cycle (one question per build)

1. Read the suspected kernel region. Pick the narrowest dump that answers one question. Never accumulate instrumentation across questions.
2. Gate every dump twice. First-call counter: `integer,save :: xxx_cnt=0` with an `if (xxx_cnt<2)` test. Rank gate: `mpi_enreg%me==0` or `my_rank==0`. Rank gates are mandatory; without them, 8 Message Passing Interface (MPI) ranks interleave into one file: duplicate rows, missing rows, binary bytes, garbage conclusions.
3. Write a META line (`ilmn`, `l`, `m`, `nincat`, `wt`) plus per-index rows. Dump all inputs needed to rebuild the quantity from first principles: scalars, phases, `kpg`, spline tables, `gmet`. Never dump outputs only; the reference must reconstruct the quantity from the same call's data.
4. Rebuild with `cmake --build .tmp/build-8 -j 24`. Run the fixture, for example `mpirun -np 8 --oversubscribe abinit fixture.abi --netcdf-classic`; the fxtp5 fixture needs 5-13 minutes with dumps.
5. Analyze in the `mydev` Python environment; `scipy` is broken in the default `python3.13`. Parse with the exponent- and NaN-tolerant parser, rebuild the model, and compare per element.
6. Revert with `git checkout -- <file>`. Rebuild. Verify the baseline return code 0.

## Placement traps

- Place the dump inside the innermost loop whose per-iteration arrays you need. A block placed after a loop silently dumps the last iteration's arrays.
- Gate k-point selection by content, not call order: `mod(kpg(1,1),one)` or an `npw` match; call-order gates land on different k-points or datasets.
- The `ffspl` spline column key is `indlmn(5)` (`iln`), not `indlmn(4)` (the `ilm` composite index).
- Never allocate a scratch buffer (`cplex`, `nlmn`, `nincat`, `nspinor`) once. `nincat` varies per atom block; a once-only allocation corrupts the heap (`corrupted size vs. prev_size`). Allocate per call.
- `npw` reaches about 1e5. A truncated dump cannot reproduce full-buffer sums; test only per-element identities from subsets, or cap the dump generously.

## Fortran edit traps (from `abinit-fd-audit-instrumented-dump-recipe`)

- The edit tool's line anchors shift after earlier edits. Re-read the region before each edit and after every warning; multi-line writes can leave orphaned duplicate continuation lines.
- Check for a missing `end do` or `end if` after inserted loops. Watch for duplicate declarations when restoring a line and for loop variables that shadow outer ones.

## Parsing traps

- `es14.6` and `es15.6` print denormals without the exponent letter: `9.881313-324`. Insert the exponent with a regex on the trailing sign and digits. Keep the parser in the campaign log.
- An unpopulated array column prints the literal `NaN`, for example `dgxdt` yy on a diagonal strain. That string is an unpopulated-column signature, not a code defect.

## Analysis discipline (from `abinit-fd-audit-instrumented-dump-recipe`)

- Verify an internal identity first, for example `ffnl1 == ylm*w1`; this validates the parse and the column alignment before you test the real hypothesis.
- For chain-rule references, fit free per-point scale factors. Check the residual distribution, not only medians. Test each basis candidate: `I`, `rprimd`, `-rprimd^T`, the inverse, `gprimd`.
- Suspect your dump first: rank gates, loop placement, or parsing. Only a rank-gated, self-consistent dump that contradicts a verified identity is a real lead.

## Verified conventions (NiO PAW+U+SOC fixture, ecut 32)

- `rprimd = (rprim*acell)^T`; `gmet = inv(rprimd^T rprimd)`; `qcart = kpg_red @ rprimd^T`; `kpgn = qhat_cart @ rprimd`.
- The `m=-2` real harmonic is `sqrt(15/4pi) * x * y`, the `xy` form. `splfit` (`m_splines.F90`) is a plain Numerical Recipes cubic on a uniform grid; `ffspl(:,1)` holds values, `ffspl(:,2)` second derivatives.
- `mkffnl` (`useylm=1`): `iylm = il^2 + il + 1 + im`; `ffnl(1) = ylm*wk_ffnl1`; `dffnl_red(mu) = ylm*wk_ffnl2*kpgn(mu) + ylm_gr(mu)*wk_ffnl1`.
- Projector-augmented wave (PAW) stress: `forstr` uses `choice=23`, `signs=1`, `idir=0`, `dimffnl=4`, `ndgxdt=9`. Strain columns 1-6 (xx, yy, zz, yz, xz, xy) come from `ffnl` columns 2-4 times `kpg` products (`m_opernla_ylm.F90` near lines 487-594). Chain-rule reference, exact to 1e-6: `dffnl_red(mu) = f'(q)*Y*(qhat@rprimd)(mu) + f(q)*(dY/dq_cart@rprimd)(mu)`.

## Environment

Pseudopotentials: `ABI_PSPDIR=abinit/tests/Pspdir`, not `Pspsdir`. Fixture: `.tmp/orbmag-constr/fdstress/v2`. Use the `mydev` Python environment or pure `numpy`.
