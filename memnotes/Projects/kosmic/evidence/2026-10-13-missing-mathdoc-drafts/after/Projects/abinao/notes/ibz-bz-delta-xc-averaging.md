---
type: reference
status: draft
audience: both
artifact_role: knowledge
math_provenance: missing
math_provenance_reason: "ibz-bz-delta-xc-averaging.md display math requires one MathDoc marker per equation"
---

# IBZ-BZ Delta XC Averaging

---
confidence: 0.9
created: 2026-07-31
last_validated: 2026-07-31
validation_procedure: "Focused aggregation tests, full abinao pytest suite, and CrI3 IBZ-to-BZ CLI comparison."
project: abinao
status: validated
validated_by: automatic
tags: [symmetry, delta-xc, pao]
---

## Overview

An IBZ `delta_xc` average cannot be expanded after k-point aggregation because each BZ point has its own PAO basis. The G-space projector exposes unweighted per-k matrices and retains each expansion basis transform.

## Principle

For every BZ point $K$, transform its IBZ-parent contribution once and then average uniformly:

$$
\Delta_{\mathrm{BZ}} = \frac{1}{N_K}\sum_K B_K^\dagger\Delta_{\mathrm{parent}(K)}B_K.
$$

Without BZ expansion, `project_delta_xc_gspace` preserves its existing normalized WFK-weighted aggregation. `delta_U` remains zero and `delta_total` equals the resulting `delta_xc`.

## VXC Pullback

For each BZ record, `transform_vxc_grid` evaluates the parent-coordinate grid
`dv(R^{-1}(x-t))`. It checks that both the direct-space lattice operation and
translation preserve the sampled FFT grid; noncommensurate grids fail rather
than silently interpolate.

## Validation

The CrI3 8x8 IBZ-to-BZ output differs from the direct full-BZ `delta_total` by
`1.6008125380828634e-11 Ha` maximum. TB2J first-shell directional values are
`1.3735`, `1.3515`, and `1.3540 meV`, for a C3 spread of `0.0220 meV`.

## Linked Concepts

- [[abinit-istwfk-symmetry-design-trace]]: Source convention for the IBZ-to-BZ PAO transform.
- [[notation]]: Definitions of $\Delta_k$ and $B_K$.
