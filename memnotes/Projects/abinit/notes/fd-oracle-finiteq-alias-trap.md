---
type: Project Knowledge
title: FD-Oracle Finite-q Alias Trap
description: Diagnose DFPT-vs-FD finite-q residuals that fail closure — FD-target alias defect at supercell-Nyquist-violating q, Hermitized-target confirmation, envelope-inert checks, and co-occurring traps.
created: '2026-09-25'
updated: '2026-09-25'
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nc-dftu, dfpt, fd-oracle, alias, finite-q]
---

# FD-Oracle Finite-q Alias Trap

## Scope

Use when a DFPT-vs-FD finite-q residual fails closure despite a correct
DFPT chain. Validated end-to-end on the story-539/W8 PBE q50 chain
(2026-09-18/19): the residual was an FD-oracle alias artifact, and the
DFPT chain was exact within its logged basis.

## Order of operations

1. Run the term-level regression first (two-q de-degeneration; see the
   wave8 owner-oracle note). Full-span residual above 0 across two q means
   the owner class is absent from the logged basis.
2. Derive the identity, name the class, then validate env-gated with a
   bitwise OFF control. Before believing either confirmation or refutation,
   check envelope applicability. A class real in the general convention can
   be inert under the port's input guards. Worked example: Delta_HERM, a
   transpose-pairing defect, is unconditionally inert because
   `usedftu_nc=1` forces `istwfk=1` at the chkinp input layer; complex-k
   exposure probes abort at DS1.
3. Run the zero-cost Hermitized-target refit BEFORE any compute campaign.
   Refit with the suspect-q target Hermitized:
   `1/2*(t + conj(t(transposed)))`. If the residual collapses to the SCF
   floor (story-539: 0.3154 Ha, 21.3% -> 0.000007), the FD target is
   aliased and the DFPT side was exact.

## The alias mechanism

Setup: a 2x2x2-supercell oracle on a 4x4x4 q-mesh. `fd_dynmat` folds the
supercell `phi_c` over a restricted image set n in {0,1}^3. With real IFCs,
that fold is exactly Hermitian at q=1/2 (+/-1 weights, real by symmetry)
and generally non-Hermitian at q=1/4 (e^{i pi n/2} weights): the
unresolved tail enters coherently. Measured: q25 target pure-imaginary
defect 31.2% of target scale, versus q50 clean at 5.8e-6. This matches the
observed residual split (q25 21.3% vs q50 4.6%). The alias defect is
pure-imaginary and reproduces at 2x the half-defect under the raw
(unhermitized) pair convention.

## Fix

Regenerate `phi_c` on a supercell whose repetition matches the q-mesh. A
q=1/4 target on a 4x4x4 mesh needs the 4x4x4 repetition of the primitive
cell. Count image CELLS, not atoms: a "4x4x4 supercell" of a 2-atom cell
has 128 atoms and 64 image cells. The corrected fold is Hermitian by
construction at both q. Alternative: Hermitize the target explicitly and
document the dropped tail if the physics permits.

## Co-occurring traps (each silently invalidates a campaign)

- Half-scale displacement builder: a kxred displacement with a half-scale
  gprimd moves legs +/-h/2 in Cartesian while decks believe +/-h. Central
  differences then overstate force constants by 2x. Validate force/h
  against 2dE/h^2 (0.2% class) before trusting any FD row.
- Wrong fold phase index: `exp(i*pi*n3)` vs the certified `exp(i*pi*n1)`.
  The smoke run works but never tests the real quantity. Round-trip a
  synthetic DDB (parse -> reduced -> cartesian -> fold) at 1e-12 before
  comparing.
- Envelope-inert fixes: validate the OFF control bitwise (DDB md5) after
  every source touch. Silent build prerequisites (cmake-3.31 -O3 default,
  ABINIT_ENABLE_ZDOT_BUGFIX, reference BLAS/LAPACK vs MKL, stale .mod
  races) can break the control before the physics is tested.
- Bistable fixtures: an atomic-superposition start can limit-cycle forever
  while a magnetic-kick start (spinat FM +0.3/atom + iomode-3 DEN chain +
  iprcel 21) converges to tolvrs 1e-9 on the same cell, sampling, and
  pseudos. The branch must match on BOTH sides. A "certified" DDB
  converged to 7.6e-13 sat on a branch 36 mHa/cell higher, and the lower
  branch can be supercell-only (an index-2 SDW superstructure unreachable
  in the primitive representation by construction). Confirm branch
  identity via the translation identity: displaced-pair etotals agree to
  about 1e-10.

## Interpretation rules

A coefficient of -1 on a leg means double count; production must subtract.
Full-span residual above 0 across two q means the owner class is absent
from the basis — but the absence can be the ORACLE's: the identity is
complete and the target is aliased. The Hermitized refit separates the two
cases. Exact refit: oracle-side defect. Refit stuck above floor: genuine
DFPT-side hunt, with the alias confound removed.
