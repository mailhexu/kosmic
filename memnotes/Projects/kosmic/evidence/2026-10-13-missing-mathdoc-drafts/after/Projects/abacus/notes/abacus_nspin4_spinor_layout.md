---
artifact_role: knowledge
audience: both
type: reference
status: draft
created: 2026-07-08
updated: 2026-07-08
tags: [abacus, lcao, spin, soc, noncolinear, reference]
related:
  - "[[lcao_hamiltonian_output]]"
  - "[[abacus_soc_in_lcao_codepath]]"
math_provenance: missing
math_provenance_reason: "abacus_nspin4_spinor_layout.md display math requires one MathDoc marker per equation"
---

# ABACUS `nspin==4` Spinor Layout in LCAO Storage

How the noncollinear/SOC (`nspin==4`) Hamiltonian is laid out in `HContainer` and how spin blocks map to indices. Distilled from research in [[2026-07-08-lcao-soc-hamiltonian-output]] and PR [#7513](https://github.com/deepmodeling/abacus-develop/pull/7513).

## Storage: one complex container, doubled basis

For `nspin==4`, `HamiltLCAO` is instantiated as `HamiltLCAO<std::complex<double>, std::complex<double>>` and holds **one** `HContainer<std::complex<double>> hR` (not four). The basis dimension doubles: `CellIndex` sets `npol=2` for `nspin==4` (`source_cell/cell_index.cpp`), so the container dimension is $N_{\rm w} \cdot N_{\rm pol} = 2 N_{\rm orb}$.

- Spinor ordering is interleaved as `(orbital, spin)`: `global_index = orbital * npol + spin`.
- `UnitCell::get_npol()` / `set_iat2iwt()` expose the spin-polarization basis indexing.
- `HamiltLCAO::getHR_vector()` returns a single-element `{hR}` vector for `nspin==4`. Only `nspin==2` splits into two (`hRS2`).
- For comparison: `nspin==1` single channel; `nspin==2` collinear spin-polarized with two real containers.

## Spin-block indexing

The four spin blocks are addressed implicitly by row/column parity inside each dense `BaseMatrix` block:

| `is` | block | Pauli component |
|---|---|---|
| `0` | $H_{\uparrow\uparrow}$ | $V_0 + V_z$ |
| `1` | $H_{\uparrow\downarrow}$ | $V_x - i V_y$ |
| `2` | $H_{\downarrow\uparrow}$ | $V_x + i V_y$ |
| `3` | $H_{\downarrow\downarrow}$ | $V_0 - V_z$ |

Concrete indexing in code:
- `module_operator_lcao/nonlocal.cpp`: `step_trace[is*npol + is2] = col_indexes.size()*is + is2`.
- `LCAO_set_st.cpp` (force/stress): `is = (jj - jj0*npol) + (kk - kk0*npol)*2`.
- `module_gint/gint_common.cpp`: direct Pauli→spinor assembly, same `is=0..3` order.

## Pauli ↔ spinor relations (fixed by [#7513](https://github.com/deepmodeling/abacus-develop/pull/7513), merged 2026-06-30)

$$
H = V_0\,\mathbf{1} + V_x\,\sigma_x + V_y\,\sigma_y + V_z\,\sigma_z,
\qquad
\begin{aligned}
H_{\uparrow\uparrow} &= V_0 + V_z \\
H_{\downarrow\downarrow} &= V_0 - V_z \\
H_{\uparrow\downarrow} &= V_x - i V_y \\
H_{\downarrow\uparrow} &= V_x + i V_y
\end{aligned}
$$

Before [#7513](https://github.com/deepmodeling/abacus-develop/pull/7513) the off-diagonal signs and Hermitian conjugation were wrong; DFT+U Pauli→spinor conversion was also fixed there.

## SOC confinement

Code-verified (2026-07-08): SOC enters the LCAO H **only** through the `Nonlocal` operator's `d_so` projectors. No other operator (`Veff`, `EKinetic`, `Overlap`, `DFTU`, `EXX`, `DeltaSpin`) has SOC code. The spinor structure in `Veff` comes from the XC magnetic field $\mathbf{B}_{XC}\cdot\boldsymbol{\sigma}$ (noncollinear magnetism), not SOC. See [[2026-07-08-lcao-soc-hamiltonian-output]] § Findings F1.

## Related code locations

- `source_lcao/hamilt_lcao.{h,cpp}` — `HamiltLCAO`, `getHR_vector()`, `hRS2` (nspin=2 only).
- `source_lcao/module_hcontainer/hcontainer.cpp` — `nw * npol` sizing.
- `source_lcao/module_gint/gint_info.cpp` — `nspin==4` doubles `nw0 *= 2`.
- `source_cell/cell_index.cpp` — sets `npol_=2` for `nspin==4`.
- `source_cell/unitcell.h` — `get_npol()`, `set_iat2iwt()`.
- `source_lcao/LCAO_HS_Arrays.hpp` — legacy `HR_soc_sparse` / `SR_soc_sparse` sparse containers (not four separate HR matrices).
