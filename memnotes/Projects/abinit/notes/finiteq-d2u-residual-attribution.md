---
type: Project Knowledge
title: NC DFT+U Finite-q D2U Residual Attribution
description: Slot-key parse rules, probe order, and un-audited residual class for scalar finite-q DDB-vs-FD campaigns.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc-dftu, finite-q, ddb, fd-oracle, d2u]
---

# NC DFT+U Finite-q D2U Residual Attribution

## Scope

Use after the bucket admission step. The scalar finite-q U/U0 campaign still
misses the finite-displacement (FD) oracle. Learned 2026-09-16, story-541.

## Slot-key parse rule

AUDIT-O1 keys are `(lam_d, lam_p, idir1, ipert1)`. Positions 1-2 are lambda.
Positions 3-4 are mu. A probe that varies mu must vary positions 3-4.
Varying positions 1-2 varies lambda. A conclusion "partner is stale or
mu-identical" from a positions-1-2 probe is a misparse. Frozen-partner occ1
is mu-dependent by design: occ1 is zeroed per build, and displacement d arms
exist only on the displaced atom.

## Probe order

1. Run the U0 gate first (`closure_scalar_finiteq.py`). A U0 twin failure
   voids every finite-U score. The defect is upstream: FD extraction or
   DFPT local channels.
2. Decompose the gap per mu-atom, lambda-atom, and direction. A constant
   gap across a whole (lambda, mu) 3x3 direction block is a site-diagonal
   constant mis-added or mis-subtracted.
3. Fit the gap on the 52-column ledger with rank (complex `lstsq`). If the
   gap leaves the span while the pre-change gap was in span, the residual
   lives outside the harvested space. Do not hunt coefficient signs.
4. Rule out, in order:
   - frozen pair leg `frz = -U Tr[S F]` from AUDIT-O1 partner blocks;
   - `d2nl_u` subtraction (add/remove worsens the gap => not the cause);
   - constant offset (count distinct values);
   - small-rational signed combinations (exhaustive +/-1, +/-1/2 grids).
5. If all probes fail, the residual is un-audited content. For story-541
   the class is the rho1-driven local/Hartree/xc/Ewald U-response: the
   U-perturbation of the density response feeding the local Hessian. The
   audited FQ2X d2nl channel differs from the production DDB slot by more
   than the whole gap (3.2504 vs 2.04).

## Key numbers (q50 frame, U scale 8.5333)

Post-admission gap (bkt+miss+KET, identity coefficients): 2.0411.
U0 gate: 5.4e-4, PASS.
`frz` alone: max 0.39, uncorrelated with the gap.
`rv1` audit value: 0.574 at slot (1,1,1,1); not admitted, not sufficient.
The `-q` mirror of `rv1` is not the conjugate class: `fold(rv1) - rv1_q`
is about 2e-1 (displaced-sphere phase dressing). Use the honest `fold(rv1)`
in assemblies.

## Trunk build notes

Local trunk debug build: `/home/hexu/projects/abinit_git/abinit_dev/build-debug`
(CMake Debug, `-O0 -g -fcheck=all`). Known trunk bug, fixed there but not in
the port: `m_dfpt_scfcv` `vtrial1_mq` hardcodes 4-column spinor indexing for
collinear `nsppol=2` at two sites. The bug corrupts the heap silently at
`-O2` and aborts bounds checks at `-O0`. Do not use the old
`/home/hexu/projects/abinit_git/abinit_dev/build` binary: it is a
foreign-host build and aborts with malloc corruption.
