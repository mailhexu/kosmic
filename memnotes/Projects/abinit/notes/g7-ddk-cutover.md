---
type: Project Knowledge
title: ABINIT G7 DDK Cutover
description: Source contract, DDB ownership, and validation sequence for the NC DFT+U Gamma electric/DDK lane.
confidence: 0.8
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Re-run the NiO packed-spinor Gamma DDK smoke and both-order DDB merge probe before promotion."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, dftu, ddk, bec, ddb, electric]
---

# ABINIT G7 DDK Cutover

## Scope

Use this note to port, validate, or review the norm-conserving (NC) density functional theory plus Hubbard U (DFT+U) Gamma electric and d/dk (DDK) lane. The lane runs with `rfelfd=2` and packed spinors. This note merges two managed skills. `abinit-g7-electric-ddk-cutover` supplies the source contract and review checklist; `abinit-nc-dftu-g7-ddk-cutover` supplies the conventions and the validation sequence. Do not enable only a DDK source: its ownership and DDB lifecycle must agree.

## DDK pseudo-atomic-orbital (PAO) derivative invariants

- `dphi_red_ddk(j)` already equals the partial derivative of `phi` with respect to reduced `k_j`. Select `dphi_red_ddk(idir)` for the requested reduced component. Never apply a `gprimd^T gprimd` contraction; it adds a spurious reciprocal metric factor.
- At `|k+G| -> 0` for real p harmonics, use reciprocal `gprimd` rows, not `rprimd` rows. The established real-harmonic ordering is `(y, z, x)`.
- Apply the derivative on both PAO spheres and on all Hubbard sites.

## H1 ownership

- DDK is a frozen-`V0` commutator source. Suppress `V1`. Do not create a DDK occupancy-response (`occ1`) or potential-response (`V1`) lifecycle. Construct and retain ground-state `n0/V0` for H1.
- Insert the DDK H1 source into `gh1c` only. Do not duplicate it in `gvnlx1`; force `apply_v1=.false.`.
- Keep DDK out of derivatives-database (DDB) partner and row assembly. DDK rows must not enter the DDB.

## Electric story-534 cutover

The explicit NC electric response-pair and frozen-`d2` consumers are removed. The native `nstwf` route owns the frozen `H1_U d1` contribution. The removed pair buckets are not algebraic zeroes; do not claim them as such. Preserve cache, schedule, and convergence guards when removing obsolete electric consumers.

## DDB merge

Port and keep the `ddb_merge_blocks` Born-effective-charge (BEC) preservation logic. A later displacement merge must not overwrite existing electric-route BEC entries. The merge must preserve the electric BEC block in either merge order.

## Review checklist

- Corrected derivative on both PAO spheres and all Hubbard sites.
- DDK in `gh1c` only; the explicit `gvnlx1` skip present.
- No inactive DDK container access to `V1`, q/minus-q pairing, or persisted response state.
- Electric cache and schedule guards may remain. Explicit electric NC pair consumers must be absent.
- BEC merge preserves the electric BEC in either order.
- No unreviewed tolerance relaxations and no unrelated feature bundles.

## Validation

1. Build the changed ABINIT tree.
2. Run a nonorthogonal packed-spinor NiO Gamma DDK smoke: `nspinor=2`, `nspden=4`, `usedftu_nc=1`, `rfelfd=2`, `prtvol=20`, all three reduced directions, plus a U=0 twin.
3. Require nonzero U-on DDK H1 source norms in all directions. Require in-code source finite-difference (FD) residuals below the campaign tolerance. Require exactly zero source norms for the U=0 twin.
4. Compare source norms and second-order observables with the corrected reference binary at the campaign tolerance.
5. Run electric U-on/U=0 DDB controls. Require atom-electric transpose symmetry and no DDK DDB rows.
6. Merge the electric-route DDB with a displacement/phonon DDB in both orders. Require every electric-route BEC element to survive.
7. Re-run a displacement control. The G7 split must not regress ordinary H1 response.

## Scope guard

Keep the packed-spinor NC DFT+U input guard (`npband=npfft=npspinor=1`, no KGB parallelism) and the rejection of unvalidated `wfoptalg` modes until Message Passing Interface (MPI) decomposition is certified. Document the active scope explicitly. This validates focused Gamma electric/DDK ownership only; it does not cover strain, finite-q production DDB, metallic or frequency response, or uncertified MPI layouts.
