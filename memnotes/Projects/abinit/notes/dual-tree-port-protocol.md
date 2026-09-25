---
type: Project Knowledge
title: Dual-Tree NC DFT+U Port Protocol
description: Test-number namespace, build, test-runner, restart-chain, and envelope-lift rules for porting between the pao-proj-parity worktree and the develop tree.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc-dftu, v10-tests, porting, runtests]
---

# Dual-Tree NC DFT+U Port Protocol

## Trees

Under `/home/hexu/projects/abinit_git/abinit_dftu_nc_dev/`: `abinit/` is the develop integration tree (branch `develop`; toolchain pin `wave0_autotools`, ABINIT 10.9.3.1, platform `x86_64_linux_gnu15.2`). `abinit_pao_proj/` is the pao-proj-parity worktree (branch `pao-proj-parity`; local build `build-mk`, makemake, ABINIT 10.9.3).

## Test-number namespace (shared across trees)

The v10 test numbers form one namespace; each tree assigns independently. As of 2026-09-17 both trees own `t220`-`t233` with different content: develop's G8 strain chain takes `t230`-`t233`; pao-proj pins `t230`/`t231` (buildbot refs `v10[230]`/`v10[231]`) and `t234` is the GAP-F1c DEN-restart test.
Before adding a test, search BOTH trees' `tests/v10/Input/` and `tests/v10/__init__.py`. Never reuse a number that exists in either tree. Renumbering a buildbot-pinned test requires the user's arbitration.

## Porting a test

Copy `tests/v10/Input/tNNN.abi`, re-pin references by RUNNING on the target toolchain, register in `tests/v10/__init__.py`.
Build: develop uses `cmake --build build-l0 -j14` (binary `build-l0/src/98_main/abinit`); pao-proj uses `make -j14 multi` in `build-mk`.
Run the suite from the BUILD tree only; the source `tests/` directory fails with "Cannot find the ABINIT build tree".
Invocation: `cd build-l0 && python ../abinit/tests/runtests.py "v10[220:233]" -b $PWD -j3 --no-colors`. Suite arguments are Python slices only; `v10[220,221]` fails with "Wrong or unknown argument". Outputs land in `<build>/Test_suite/v10_tNNN/`; source-tree `tests/Test_suite/` is stale.

## Reference toolchain drift

References pinned on one toolchain fail fldiff on the other: self-consistent-field (SCF) total-energy lines drift 1e-5..1e-8, derivative-database (DDB) entries drift less, version/platform headers differ (10.9.3 CMake vs 10.9.3.1 wave0_autotools).
Committing refs from `build-l0` is accepted WITH an explicit commit note that a `wave0_autotools` regen is expected (established flow, develop commit ac42b3e8e4). `t220`/`t221` failing fldiff on `build-l0` is this class, not a regression.

## Restart chains inside one deck

Positive `getwfk`/`getden`/`getddk` values are ABSOLUTE dataset numbers, never "previous dataset": `getwfk5 1` reads DATASET 1 output.
A U-on/U=0 twin chain (datasets 1-3 U-on, 4-6 U=0) needs `getwfk5 4`, `getddk6 5`; the `t212` pattern (`getddk3 2`) does not generalize by copying.
Wrong indexing lets the twin datasets consume the U-on state silently; all `etotals` then shift together.
Indexed-variable edits (`dftu_u4`, `getwfk5`) collide with PUT-style line edits: re-read the block after editing and verify with the parser (duplicate keywords abort the input).

## Envelope-lift equivalence protocol

Removing an `iscf<0` / restart / mode guard needs a consumer-visible equivalence witness: SCF state, then ordinary non-SCF (`iscf=-3`), then WFK+DEN restart; all three `etotals` bitwise equal (GSR.nc `etotal` delta exactly 0.0).
Bitwise equality is also the restoration proof when the missing path shifts the observable by a known amount (example: `Tr[V_U n]` about 0.09 Ha).
The DEN write requires `iomode 3` (ETSF) and `prtden 1`; the read fails closed on state-version, geometry, and projector metadata.
Scalar twin tests: `t220`/`t221`. Packed-spinor twin test: `t234`.
