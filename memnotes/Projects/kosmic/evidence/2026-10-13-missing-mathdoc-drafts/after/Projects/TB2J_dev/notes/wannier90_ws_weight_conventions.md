---
artifact_role: knowledge
type: reference
audience: both
title: "Wannier90 _hr.dat and _wsvec.dat Wigner-Seitz Weight Conventions"
confidence: 0.95
created: 2026-07-26
last_validated: 2026-07-26T00:00:00
validation_procedure: |
  Read Wannier90 3.1.0 source at /home/hexu/.local/src/wannier90-3.1.0_serial:
  - hamiltonian.F90:478 (writes raw ham_r), :473 (writes ndegen), :738/:746 (_tb.dat same)
  - plot.F90:346 and postw90_common.F90:727,741 (Fourier divides by ndegen, and ndegen*N_T)
  - ws_distance.F90:283-313 (ws_write_vec format)
  Validated by tests: HamiltonIO/tests/test_wannier_ws_weights.py (sum rule on
  CrI3 = 81), HamiltonIO/tests/test_wsvec_parser.py (CrI3 N_T=2, SrMnO3 N_T=8).
validation_test: "HamiltonIO/tests/test_wannier_ws_weights.py, HamiltonIO/tests/test_wsvec_parser.py"
successful_usage_count: 1
last_used_successfully: 2026-07-26T00:00:00
usage_stale: false
related_files:
  - HamiltonIO/HamiltonIO/wannier/wannier_hamiltonian.py
  - HamiltonIO/HamiltonIO/wannier/w90_parser.py
  - HamiltonIO/HamiltonIO/wannier/wsvec_parser.py
  - /home/hexu/.local/src/wannier90-3.1.0_serial/src/hamiltonian.F90
  - /home/hexu/.local/src/wannier90-3.1.0_serial/src/ws_distance.F90
related_functions: ["WannierHam.gen_ham", "parse_ham", "parse_wsvec"]
tags: [wannier90, wigner-seitz, ndegen, wsvec, fourier-transform, convention]
project: TB2J_dev
status: draft
validated_by: automatic
validation_date: 2026-07-26T00:00:00
links_to: [srmno3_nm_qe_wannier_reference, notation]
linked_from: []
math_provenance: missing
math_provenance_reason: "wannier90_ws_weight_conventions.md display math requires one MathDoc marker per equation"
---

# Wannier90 `_hr.dat` and `_wsvec.dat` Wigner-Seitz Weight Conventions

## The core convention (often misunderstood)

Wannier90's `_hr.dat` stores the **RAW** real-space Hamiltonian `ham_r(j,i,R)`,
and a **separate** `ndegen(R)` array. The reader MUST divide by `ndegen(R)`
during the Fourier transform. The values are NOT pre-divided.

Source proof: `hamiltonian_write_hr` (`hamiltonian.F90:473,478`) writes `ndegen`
on its own line and `ham_r(j,i,irpt)` raw. `plot_interpolate_bands`
(`plot.F90:346`) does `fac = exp(ikR) / ndegen(irpt)`.

`_tb.dat` is identical: `hamiltonian_write_tb` (`hamiltonian.F90:738,746`)
writes `ndegen` and raw `ham_r`. One reader convention covers both.

## Scheme 1 — global ndegen (always available)

$$
H_{ij}(\mathbf{k}) = \sum_{\mathbf{R}} \frac{e^{i2\pi\mathbf{k}\cdot\mathbf{R}}}{\text{ndegen}(\mathbf{R})}\, H_{ij}(\mathbf{R})
$$

Sum rule (validation): $\sum_{\mathbf{R}} 1/\text{ndegen}(\mathbf{R}) = N_{k_1}N_{k_2}N_{k_3}$.

## Scheme 2 — per-orbital-pair WS images (`_wsvec.dat`)

When `use_ws_distance=.true.` + `write_wsvec=.true.`, Wannier90 also writes
`_wsvec.dat` with per-`(i,j,R)` image translation lists `T`. The denominator
becomes the **product** `ndegen(R) * N_T(i,j,R)` and the phase is on the full
`R+T` vector:

$$
H_{ij}(\mathbf{k}) = \sum_{\mathbf{R}} \sum_{\ell=1}^{N_T^{ij\mathbf{R}}} \frac{\exp(i2\pi\mathbf{k}\cdot(\mathbf{R}+\mathbf{T}_\ell))}{\text{ndegen}(\mathbf{R})\,N_T^{ij\mathbf{R}}}\, H_{ij}(\mathbf{R})
$$

Source: `postw90_common.F90:727`, `plot.F90:335-340`.

When the header says `.false.`, every block is `N_T=1, T=(0,0,0)` (trivial), so
scheme 2 reduces exactly to scheme 1.

## `_wsvec.dat` format

```
## written on {date} at {time} with use_ws_distance={.true.|.false.}
{Rx} {Ry} {Rz} {iw} {jw}     # 1-based orbital indices
{N_T}
{Tx} {Ty} {Tz}               # N_T lines
...                          # next block; loop order irpt, iw, jw
```

`T` is the supercell translation only (`irdist_ws - irvec`, a multiple of
mp_grid). The full phase vector is `R + T`.

## HamiltonIO state (2026-07-26, after story-026/027/028)

- `WannierHam.gen_ham` now divides by `R_degens.get(R, 1)` (keyed by R-tuple) in
  both conventions. Previously the division was commented out — a bug. Fixed in
  story-026.
- `parse_wsvec` (story-027) reads `_wsvec.dat` into
  `{R: {(i,j): ndarray(N_T,3)}}`.
- Scheme-2 wiring (story-028): `WannierHam` has internal `use_ws`/`ws_shifts`
  attributes; `gen_ham` branches to `_gen_ham_scheme2` when both are set;
  `read_from_wannier_dir` auto-detects `{prefix}_wsvec.dat` (no public param,
  ADR-002); `shift_position` re-keys ws state to shifted R.
- TB2J passthrough (story-029) and docs/validation (story-030): pending.

## Gotchas

- `R_degens` on `WannierHam` is a **dict keyed by R-tuple**, not a list. The
  original commented-out code used the integer loop index `iR`, which would have
  silently returned the defaultdict default (1) for every R — a second latent
  bug. Always look up by `R`.
- **Missing keys**: `gen_ham` uses `R_degens.get(R, 1)` (not `[R]`), because
  `shift_position` relabels R-vectors in `data` (sR = R + shift[j] - shift[i])
  but passes the original `R_degens` (keyed by old R) through. So after
  `shift_position`, the new `data` keys are absent from `R_degens`. `.get(R, 1)`
  falls back to weight 1 instead of raising. Caveat: this means shifted
  hoppings lose their true ndegen weight in the production
  `read_from_wannier_dir → shift_position → gen_ham` path. Whether degeneracy
  should be remapped through the shift is a story-028 question (already flagged
  in its Technical Notes).
- `convention=1` in `gen_ham` has a **separate pre-existing shape bug**
  (`np.dot(k, R + rjminusri)` raises for nbasis > 0). Unrelated to ndegen; out
  of scope for the ws-weights epic. `convention=2` (the default, used by TB2J)
  is correct.
- HamiltonIO `R2kfactor = +2πj` matches Wannier90's `exp(+i*rdotk)`. Same sign.

## Related

- [[srmno3_nm_qe_wannier_reference]] — SrMnO3 wsvec fixture source.
- [[notation]] — transform conventions.
