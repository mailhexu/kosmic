---
type: Project Knowledge
title: Noncollinear initspinden Port
description: Porting the legacy initspinden feature to a filtered ABINIT branch and extending it from collinear to arbitrary noncollinear DEN-restart targets.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc, spinat-cart, paw, v10-tests]
---

# Noncollinear initspinden Port

## Baseline

Start an isolated worktree from `origin/collinear_spin_constrain`.
Apply only the legacy feature patch `56d1f0a090..d5380e0cb2`; exclude `ba62111e5e` (CMake-only follow-up).
Confirm `git apply --check --whitespace=error` before applying.

## Representation invariants

The canonical user target is `dtset%spinat_cart(:,iatom)`; do not reinterpret local-basis `spinat` when `spinaxis` is nontrivial.
In `nspden=4`, `calcdenmagsph` integrates `rhor(:,1:4)` as `(rho, mx, my, mz)`; `pawrhoij_type%rhoijp(:,1:4)` and `%rhoij_(:,1:4)` use the same scalar-plus-magnetization layout.
Nonzero source and target: rotate components `2:4` with a proper SO(3) rotation; this equals `D' = U D U†` for the SU(2) lift; component 1 stays unchanged.
Zero target: zero components `2:4` inside the atom sphere and in its PAW block.
Antiparallel target: pick a deterministic normalized axis orthogonal to the source and rotate by pi.
Apply sphere smoothing to the grid rotation, and the exact same rotation to PAW `rhoijp` and allocated `rhoij_` blocks.

## Implementation seam

Place the action immediately after `read_rhor` in `src/95_drive/m_gstate.F90`, before the SCF loop.
Widen the `m_chkinp.F90` guard from `nspden=2` to `nspden=2 or 4`; keep the no-DEN warning; preserve the legacy `nspden=2` block behind a branch.
Update `abimkdocs/variables_abinit.py`, `m_dtset.F90`, `m_invars2.F90`, and `m_outvar_o_z.F90` from the legacy patch.

## Fast v10 regression

Scan every active sibling tree before claiming a shared v10 number; `t88` was free after the `t86`/`t87` collisions.
Fixture: one-atom PAW F in a 20 bohr box; `nspinor 2`; `nsppol 1`; `nspden 4`; `ecut 5`; `pawecutdg 10`; `nband 8`; `nstep 12`; `toldfe 1d-5`.
DS1 writes a z-directed DEN; DS2 reads it and requests `spinat_cart` proportional to `(3,4,5)`.
Register in `tests/v10/__init__.py`, pin the generated `t88.abo`, then run: `ABI_PSPDIR=<source>/tests/Pspdir python3 tests/runtests.py 'v10[88]' -b <build>`.
The fixture must fail before the guard widening and pass after implementation. Validated serial runtime: 8.62 seconds.
Smoke zero and antiparallel targets from a disposable `.tmp/` directory; inspect the printed action and the before/after vector.

## Build without a CMake source change

For CMake 3.31+, avoid the excluded CMake patch with an external top-level include file containing `include(CheckIncludeFile)`; run `config/scripts/make-cppopts-dumper` first.
Configure: `cmake -S <src> -B <build> -DABINIT_FFT_FLAVOR=GOEDECKER -DCMAKE_PROJECT_TOP_LEVEL_INCLUDES=<build>/bootstrap-include.cmake`. Keep the bootstrap and build outputs outside the source worktree.

## Verification and cleanup

Build the full tree after source changes; run `git diff --check`; run the new v10 slice and record the wall time.
Existing `v10/t85` may show 10.9.0-reference versus 10.9.3 toolchain drift; do not repin it unless the user requests it.
Delete `Test_suite/`, `tests/test_suite.cpkl`, temporary control decks, generated `ustream.demo`, and transient patch files before final status.
