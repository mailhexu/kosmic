---
type: Project Knowledge
title: Widening a chkinp Input Guard (NC DFT+U Port)
description: Mechanism verification, dead-letter route checks, rebuild attribution, and commit scope for guard widening in src/57_iovars/m_chkinp.F90.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, chkinp, guards, nc-dftu, testing]
---

# Widening a chkinp Input Guard (NC DFT+U Port)

## Establish the guard's real mechanism first

`chkinp` is ONE subroutine in `src/57_iovars/m_chkinp.F90` (span about lines 80-5218); locals such as `xc_is_gga` (set near lines 175-184 from legacy `ixc` ranges plus `libxc_functionals_isgga`) are in scope everywhere.
`dt%usedftu_nc` is NOT reliably resolved at the generic guard points (near line 3000).
The clause that historically admitted the port's DFT+U response decks is the `nspden=4` spinor strain twin clause: `rfstrs==3 .and. nspinor==2 .and. nspden==4 .and. ixc==1`. A lift keyed on `dt%usedftu_nc` breaks known-green tests: `t230` failed with "nspinor must be 1".
Verify empirically which clause admits the target decks: run a revert-style A/B of the candidate condition against a known-green deck BEFORE committing the lift.

## Probe the admitted route end-to-end (dead-letter check)

A guard can admit a route that aborts downstream. Example: the native (`usedftu_nc=0`) LDA spinor strain twin was never executable; the frozen second-order nonlocal strain term has no `nspinortot=2` support (`m_nonlop_pl` choice=6 raises ABI_BUG).
Trial-run the widened deck on the real binary before committing the lift.
A fail-loud upstream ABI_BUG in a never-run path is a finding, not a regression.
Document dead-letter exceptions in the guard comment; never admit them silently.

## Rebuild and regression protocol

Rebuild the shared dev build (`build-l0`) incrementally. The binary picks up OTHER lanes' uncommitted source WIP; attribute family diffs before blaming your own change: check `git status src/`, file modification times, and total-energy deltas. Toolchain noise shows about 1e-12 Ha on `etotal`; physics changes show slot-structured shifts.
Run the guard's test family plus the new pinned test.
Runner syntax: `python tests/runtests.py "v10[237]" "v10[238]" -b <build> -j4 --no-colors`; the specs are space-separated and quoted; bracket ranges and comma lists (`v10[230-238]`) fail with "Wrong or unknown argument".
Reference failures on tests owned by another lane or toolchain are false-positive noise: version strings differ (v10.9.3 versus v10.9.3.2) and amplify past `tolabs` across derivative-database (DDB) records; the regen duty belongs to the family owner on their reference toolchain.

## Commit scope

Commit only the guard file, the new or owned test files, and the `tests/v10/__init__.py` registration; never sweep sibling WIP into the commit.
Note in the commit message when pinned references include sibling in-flight changes; the regen duty lands with them.
