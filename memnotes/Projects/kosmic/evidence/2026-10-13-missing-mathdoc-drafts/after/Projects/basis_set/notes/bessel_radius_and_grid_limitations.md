---
type: reference
status: draft
audience: both
artifact_role: knowledge
math_provenance: missing
math_provenance_reason: "bessel_radius_and_grid_limitations.md display math requires one MathDoc marker per equation"
---

# Bessel Radius And Grid Limitations

## Overview
The limitation is not that truncated spherical Bessel functions with different radii are mathematically impossible. The real issue is that in the current ABACUS-CSW-NAO implementation, the cutoff radius `rcut` enters the **definition of the primitive basis**, the **dimension of the coefficient space**, and the **exported radial grid / file format**.

So using different radii is a change of basis construction, not just a metadata change.

## 1. Raw truncated spherical Bessel basis

In the code, the raw radial primitive is

$$
f_{lq}(r; r_c) =
\begin{cases}
j_l\!\left( \dfrac{z_{lq}}{r_c} r \right), & r \le r_c \\
0, & r > r_c
\end{cases}
$$

where:
- `j_l` is the spherical Bessel function
- `z_{lq}` is the `q`-th zero of `j_l`
- `r_c` is the cutoff radius

This is exactly the structure used in `SIAB/spillage/radial.py:171-229`.

The corresponding wave number is

$$
k_{lq} = \frac{z_{lq}}{r_c}
$$

So changing `r_c` changes the whole primitive basis.

## 2. Energy cutoff changes the number of Bessel primitives

The code selects the number of Bessel primitives by

$$
n_{\mathrm{bes}}(l; r_c, E_{\mathrm{cut}})
= \# \left\{ q : \left(\frac{z_{lq}}{r_c}\right)^2 < E_{\mathrm{cut}} \right\}
$$

This is implemented in `SIAB/spillage/radial.py:361-377`.

So if two channels use different radii `r_c^{(l)}` and `r_c^{(l'))}`, then in general

$$
n_{\mathrm{bes}}(l; r_c^{(l)}, E_{\mathrm{cut}})
\neq
n_{\mathrm{bes}}(l; r_c^{(l')}, E_{\mathrm{cut}})
$$

This means the coefficient vector length changes with radius.

That is one core reason mixed radii are awkward: changing radius changes the dimension of the optimization variables.

## 3. Orthogonality is simple only when the cutoff is shared

For a fixed `l` and a fixed cutoff `r_c`, the raw truncated Bessel functions satisfy an orthogonality relation of the form

$$
\int_0^{r_c} r^2 \,
j_l\!\left( \frac{z_{lq}}{r_c} r \right)
j_l\!\left( \frac{z_{lq'}}{r_c} r \right)
\, dr
\propto \delta_{qq'}
$$

This clean structure depends on using the same boundary radius `r_c` for the whole primitive set.

If two functions use different radii `r_a` and `r_b`, then one instead gets

$$
\int_0^{\min(r_a, r_b)} r^2 \,
j_l\!\left( \frac{z_{lq}}{r_a} r \right)
j_l\!\left( \frac{z_{lq'}}{r_b} r \right)
\, dr
$$

which is no longer the standard same-cutoff orthogonality relation.

So mixed radii destroy the simple primitive-space structure the current code relies on.

## 4. Reduced basis also depends on cutoff radius

The reduced basis is constructed from the raw basis so that the resulting functions have vanishing derivatives at the cutoff. In the code, the transformation matrix depends on `rcut` through normalization and derivative-at-boundary conditions; see `SIAB/spillage/radial.py:251-308`.

Schematically,

$$
\mathbf{e}^{(l)}(r; r_c) = \mathbf{f}^{(l)}(r; r_c) \, T^{(l)}(r_c)
$$

where:
- `\mathbf{f}^{(l)}` is the raw truncated-Bessel basis
- `T^{(l)}(r_c)` is the cutoff-dependent reduction matrix

So even the reduced basis changes if `r_c` changes.

## 5. Numerical radial orbitals are expanded on that cutoff-dependent basis

The numerical radial functions are built as

$$
\chi_{lz}(r)
= \sum_q c_{lzq}
j_l\!\left( \frac{z_{lq}}{r_c} r \right)
g(r; r_c, \sigma)
$$

where the smoothing/truncation factor in the code is

$$
g(r; r_c, \sigma) =
\begin{cases}
1 - \exp\!\left[-\dfrac{(r-r_c)^2}{2\sigma^2}\right], & r < r_c \\
0, & r \ge r_c
\end{cases}
$$

See `SIAB/spillage/radial.py:140-168` and `SIAB/spillage/radial.py:444-530`.

So if one changes `r_c`, one changes:
- the primitive functions
- the truncation point
- the normalization
- the coefficient dimension

## 6. Why the grid becomes a problem

When the code exports orbitals, it uses one radial grid built from one `rcut`:

$$
r_i = i \, dr,
\quad i = 0, 1, \dots, N
$$

with

$$
N = \left\lfloor \frac{r_c}{dr} \right\rfloor
$$

This is exactly what `SIAB/orb/orb.py:397-413` does.

So one orbital object currently implies one shared grid:

$$
\{r_i\}_{i=0}^{N}
\quad \text{with a single } r_c
$$

If different channels use different cutoffs `r_c^{(l)}`, then naturally each channel wants a different grid length:

$$
N_l = \left\lfloor \frac{r_c^{(l)}}{dr} \right\rfloor
$$

Hence

$$
\chi_{lz}(r_i^{(l)})
$$

would live on different arrays for different `l`.

## 7. Why the ABACUS `.orb` format blocks this in practice

The writer stores a single header with
- one `Radius Cutoff(a.u.)`
- one `Mesh`
- one `dr`

See `SIAB/spillage/orbio.py:12-70`.

So the file format is effectively assuming

$$
\text{one common } r_c, \quad
\text{one common } N, \quad
\text{one common } dr
$$

for all radial functions in the file.

If one wants mixed radii inside one file, one would need either:

### Option A. Common outer grid with zero padding

Choose

$$
r_{\max} = \max_l r_c^{(l)}
$$

and a common grid

$$
r_i = i \, dr,
\quad i=0,\dots,N_{\max},
\quad N_{\max} = \left\lfloor \frac{r_{\max}}{dr} \right\rfloor
$$

then define each channel by

$$
\chi_{lz}(r_i) = 0, \quad r_i > r_c^{(l)}
$$

This is mathematically possible, but the ABACUS format/parser must explicitly support the interpretation.

### Option B. Per-channel mesh metadata

Store for each channel its own

$$
r_c^{(l)}, \; N_l, \; dr_l
$$

but this requires a different file format or parser logic.

## 8. Bottom line

The limitation comes from three coupled facts:

1. **Basis-definition limitation**

   `rcut` enters the primitive functions as

   $$
   j_l\!\left( \frac{z_{lq}}{r_c} r \right)
   $$

   so changing `rcut` changes the basis itself.

2. **Dimension limitation**

   the number of primitives is

   $$
   n_{\mathrm{bes}}(l; r_c, E_{\mathrm{cut}})
   $$

   so changing `rcut` changes the number of coefficients.

3. **Grid / file-format limitation**

   the exported orbital file assumes one common

   $$
   (r_c, N, dr)
   $$

   for all channels.

Therefore, mixed-radius truncated-Bessel orbitals are not forbidden mathematically, but they are incompatible with the current ABACUS-CSW-NAO implementation and the ABACUS orbital-file convention it targets.

## Code References
- `SIAB/spillage/radial.py:171-229` raw truncated spherical Bessel functions
- `SIAB/spillage/radial.py:251-308` reduced basis construction
- `SIAB/spillage/radial.py:361-377` number of Bessel primitives under cutoff
- `SIAB/spillage/radial.py:444-530` build numerical radial functions on a grid
- `SIAB/orb/orb.py:397-413` one `rcut` gives one exported grid
- `SIAB/spillage/orbio.py:12-70` ABACUS orbital file header uses one cutoff and one mesh
