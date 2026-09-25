---
type: Project Knowledge
title: ABINIT Fixture Bistability Screening
description: Screen SCF fixtures for multi-start bistability before FD/DFPT oracle campaigns; start-cure recipes, branch-aware comparator rules, and displacement tooling traps.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, scf, fixtures, bistability, fd-oracle, campaign-hygiene]
---

# ABINIT Fixture Bistability Screening

## Scope

Use BEFORE committing a fixture to any finite-displacement or DFPT
comparison campaign, and whenever "converged" results disagree across
representations. Born from two 2026-09 campaigns: a 4-atom PBE cell with
an intrinsic limit cycle (story-550) and a 16-atom LDA supercell with
two-state density bistability (LdaFix).

## Core lesson: converged is not the correct branch

A run at vres2 7.6e-13 can sit 36 mHa/cell ABOVE the true ground state on
a bistable fixture. SCF convergence certifies the fixed point, not the
branch. Every comparator (FD row vs DFPT DDB) is valid only
branch-consistently.

## Multi-start screen (cheap, run it first)

Run the ground state from at least 3 starts at identical settings:
- atomic-superposition default start;
- FM spinat kick (+0.3 per atom);
- AFM staggered spinat;
- optional: density-kick restart from a displaced-geometry run.
STABLE: all starts agree to floating-point noise (1e-9 Ha or below).
BISTABLE: etot spread beyond that (real case: a 3e-3 Ha band). Also test
one displaced geometry. Some branches exist only displaced.

## Mixer sweeps are not a cure

The LDA case survived 12 mixer families (iprcel 21/141, iscf 2/3/7,
diemac 12/40, diemix 0.04-0.15, npulayit, smearing, ecut changes). If a
plateau floor scales with displacement amplitude, suspect the dielectric
preconditioner: iprcel 21 (RPA) cleared a leg that 9 other recipes failed
(59 steps to tolvrs 1e-9).

## Exoneration control

Run a pure no-U (or no-feature) control. If it cycles identically, the
port, build, and feature machinery are exonerated at low cost.

## Cures that worked

- Start change: a spinat FM kick (+0.3 per atom) reached a branch the
  atomic start could never leave (deterministic across restarts).
- DEN-anchored chains (iomode 3) for displaced legs, all anchored to the
  same branch.
- AFM starts may reach a DISTINCT second branch (recorded +4.3 uHa).
  Pick branches explicitly. Do not average.

## Representation-dependence is often physical

A branch reachable ONLY in the supercell representation is usually a
symmetry-broken superstructure. Verify: density Fourier content on
supercell folding vectors, staggered PAO projector moments, index-2
magnetic cell (L-point-like SDW). Check the U=0 channel is exactly dead
before blaming the U machinery. Adjudicate with: density symmetry audit,
occupations cross-check across representations, fixed-density FFT-grid
shift test. If physical, run BOTH comparison sides in the supercell
representation anchored to the same branch. Never compare across branches.

## Displacement tooling traps (check once per campaign)

- Displacement builders with a wrong-scale gprimd silently halve
  amplitudes. Validate force/h against 2dE/h^2 (about 0.2% expected).
- Fold phase conventions: use the certified phase (for example
  exp(i pi n1), NOT n3) and the TRUE displacement span in central
  differences.
- `iscf=-3` echoes the DEN header etot and can write zero-filled DENs.
  No usable single-point energies exist on that path.

## Operations

Shield long runs with setsid (external reapers exist). Sweep OUT.nc, GSR,
and WFK regenerables at high disk usage. Keep .abi, .abo, DDB, and the
analysis outputs.
