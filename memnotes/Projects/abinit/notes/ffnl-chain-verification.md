---
type: Project Knowledge
title: ABINIT ffnl Chain Verification
description: Verify the ABINIT nonlocal ffnl/stress chain end-to-end with rank-gated same-kpt triple dumps and verified conventions.
confidence: 0.8
created: '2026-09-25'
updated: '2026-09-25'
validation_procedure: "Re-run the NiO triple-dump chain check on a current ABINIT tree before promotion."
project: abinit
status: draft
audience: development
artifact_role: guideline
usage_stale: false
tags: [abinit, nonlocal, ffnl, stress, verification]
---

# ABINIT ffnl Chain Verification

## Scope

`ffnl` is the ABINIT nonlocal form-factor array. Use this procedure to prove or refute that the nonlocal stress
chain is self-consistent. The chain is `mkffnl` -> `gs_hamk%ffnl_k` -> `opernla_ylm`. Typical trigger: a stress
defect in a projector-augmented wave (PAW) run.

## Dump protocol

1. Rank-gate every instrumented dump. Use `my_rank==0` in `mkffnl` and `mpi_enreg%me==0` in `nonlop_ylm` and
   `opernla_ylm`. Without the gate, 8 Message Passing Interface (MPI) ranks interleave into one file: duplicate
   rows, binary bytes, and bogus discrepancies.
2. Gate the dump to one k-point by content. Use `mod(kpg(1,1),one)`, the fractional part of the k-point, or a
   match on the nonlop `npwin` plane-wave count. A call-order gate lands on different k-points or datasets;
   strain datasets change `acell`, the plane-wave count, and the q scales.
3. Place the dump inside the `ilmn` loop. Gate it on `indlmn(1,ilmn)` and `indlmn(2,ilmn)`. A dump placed after
   the loop contains only the last `ilmn` arrays. The spline column key is `indlmn(5)` (`iln`), not `indlmn(4)`
   (the `ilm` composite index).
4. Match rows across dumps by reduced `kpg` triplets, rounded to 1e-4. Never match by row order or by value;
   `ffnl1` values collide across symmetric G vectors.
5. Parse Fortran `es14.6` / `es15.6` output tolerantly. Denormals print without the exponent letter, for example
   `9.881313-324`. Unpopulated array columns print the literal string `NaN`.

## Verified reference forms (PAW, useylm=1)

- `ffnl(1) = ylm * wk_ffnl1`; `dffnl_red(mu) = ylm * wk_ffnl2 * kpgn(mu) + ylm_gr(mu) * wk_ffnl1`.
- `wk_ffnl1` and `wk_ffnl2` are spline value and derivative at `|q|`. The spline is `splfit`: a plain Numerical
  Recipes cubic on a uniform q grid. `ffspl(:,2)` holds second derivatives.
- Real spherical harmonics for `l=2`: `m=-2` is the `xy` form, `sqrt(15/4pi) * qx * qy / q^2`; `m=+2` is the
  `x^2-y^2` form. The harmonic gradient includes the chain-rule derivative of the `q^-2` factor; contract with
  `rprimd` for reduced components.
- Conventions: `rprimd = (rprim * acell)^T`, row i holds Cartesian component i of lattice vector j in column j;
  `gmet = (rprimd^T rprimd)^-1`; `qcart = kpg_red @ rprimd^T`; `kpgn = qhat_cart @ rprimd`; `gprimd` holds
  reciprocal vectors without the `2*pi` factor; `mkkpg` returns plain reduced k-point plus `kg`.
- Stress path: `forstr` uses `choice=23`, `signs=1`, `idir=0`, `ndgxdt=9`, `dimffnl=4`; `choice = 2*optfor +
  3*stress_needed`. Strain columns 1-6 carry strain; columns 7-9 carry forces. The strain assembly lives in
  `m_opernla_ylm` in the `choice` in {3, 6, 23, 55} with `signs=1` block.

## Common pitfalls

- `npw` reaches about 1e5. A partial-row dump cannot reproduce full-npw buffer sums.
- Allocate contraction scratch buffers per call. `nincat` varies per atom block; a once-only allocation corrupts
  the heap (`corrupted size vs. prev_size`).
- Fortran write buffers are lost on a segfault. Call `flush(unit)` after each write when you chase a crash.
- Edit-tool line anchors drift after multi-line edits. Re-read the region after every warning.

## Reference result

Fixture: NiO PAW plus DFT+U plus spin-orbit coupling (SOC), ecut 32 Ha, k-point 0.25^3, `npw` 2140. The `mkffnl`
output equals `gs_hamk%ffnl_k` equals the `opernla_ylm` input. Rows match exactly (0.000e+00) by `kpg` triplets.
The chain-rule identity closes at 1e-6. If your run shows differences, suspect your dump first: rank gating,
k-point identity, or `ilmn` gating. Only a rank-gated, self-consistent dump that still contradicts a verified
identity is a real lead.
