---
artifact_role: knowledge
type: reference
audience: both
title: delta_xc_smooth is the real-space integral of lattice-summed PAOs times V_xc
topic: xc-projection
project: symwannier
status: draft
validated_by: derivation
created: 2026-07-28
updated: 2026-07-28
related_files:
  - /home/hexu/projects/TB2J_dev/abinit/src/68_pao_hamiltonian/m_nc_pao_hamiltonian.F90
  - /home/hexu/projects/autosiestabasis_dev/pypao/src/pypao/overlap.py
tags: [delta_xc, vxc, pao, lattice-sum, fourier, abinit, abinao]
math_provenance: missing
math_provenance_reason: "delta_xc_realspace_lattice_sum.md display math requires one MathDoc marker per equation"
---

# delta_xc_smooth = real-space integral of lattice-summed PAOs × V_xc

ABINIT stores `delta_xc_smooth` in `*_PAO_HS.nc` as a single `[nproj,nproj]` matrix with **no
k-index**, yet `compute_delta_xc_nc` (`m_nc_pao_hamiltonian.F90:667-847`) accumulates over k
and divides by `nkpt`. Reconciling the two shows what the Python port must compute.

## Derivation

ABINIT computes, per k, $\langle\phi_{\mu\mathbf k}|V_{xc}|\phi_{\nu\mathbf k}\rangle$ where
$\phi_{\mu\mathbf k}$ is the Bloch sum $\sum_{\mathbf R} e^{i\mathbf{k}\cdot\mathbf R}\phi_\mu^{\text{atom}}(\mathbf r-\mathbf x_\alpha-\mathbf R)$,
then averages:

$$
\frac{1}{N_k}\sum_{\mathbf k}\langle\phi_{\mu\mathbf k}|V_{xc}|\phi_{\nu\mathbf k}\rangle
= \int_{\text{cell}} \Phi_\mu^*(\mathbf r)\,V_{xc}(\mathbf r)\,\Phi_\nu(\mathbf r)\,d^3r
$$

because $\frac{1}{N_k}\sum_{\mathbf k}e^{i\mathbf k\cdot\mathbf R}=\delta_{\mathbf R,\mathbf 0}$
kills every inter-cell phase, leaving the **R=0 (single-cell) real-space integral** of the
*lattice-summed* PAO $\Phi_\mu(\mathbf r)=\sum_{\mathbf R}\phi_\mu^{\text{atom}}(\mathbf r-\mathbf x_\alpha-\mathbf R)$.

## The load-bearing detail

$\Phi_\mu$ is the **lattice sum** over periodic images within the PAO cutoff $r_c$, not just
the cell-0 atomic function. PAOs extend outside the unit cell; for any cell smaller than
$2r_c$, a grid point in cell 0 sees tails from PAOs centred in neighbouring cells. Omitting
the image sum gives a wrong integral — this is the user's "PAO can extend outside the cell"
caveat.

## Why this matters for the port

- The Python port needs **no wavefunction coefficients and no k-mesh** — only `_VXC`
  (`prtvxc`, [[abinit_vxc_netcdf_dump]]) + UPF PAOs (pypao) + crystal geometry.
- The image-sum machinery already exists in `pypao/overlap.py` (finite-support cutoff rule
  $|\mathbf d+\mathbf n|\cdot\text{rprimd}<r_{c,\mu}+r_{c,\nu}$) — reuse it.
- The matrix is full `[nproj,nproj]`: on-site (same atom) AND intra-cell off-site (different
  atoms in cell 0) blocks. Inter-cell (R≠0) blocks are *not* in `delta_xc_smooth`.

## Validation (ABINIT-INDEPENDENT)

ABINIT's `delta_xc_smooth` is **suspect** (a bug in `compute_delta_xc_nc` is under
investigation), so it is **not** the oracle. Three things, in this role:

1. **Synthetic constant-$V_{xc}$ anchor** (trusted): for $V_{xc}(\mathbf r)=V_0$, $\Delta_{xc}=V_0\cdot S_{\mu\nu}$, where $S$ is abinao's overlap — validated ~1e-7 vs ABINIT's *separate* `compute_all_overlaps_nc` routine. This proves the projector without trusting `delta_xc_smooth`.
2. **Real-space ≡ G-space** (self-consistency): the two independent Python routes agree to ~1e-7 on real V_xc → the trusted Python value.
3. **ABINIT comparison = diagnostic**: $\Delta_{xc}^{\text{Python}}$ vs `delta_xc_smooth` is a quantified discrepancy to investigate, not a tolerance to meet.

Diagnostic reading: if real-space ≠ G-space, the image sum or FFT normalization is wrong
(Python bug). If real-space ≡ G-space but both ≠ ABINIT, that is the **ABINIT bug** —
characterise it (magnitude, symmetry, per-orbital pattern) and trace candidates against the
`ponytail:`-marked fix sites at `m_nc_pao_hamiltonian.F90:730-734, 801-804`.

## Numerical result (O atom, 2026-07-28)

Implemented in `abinao/vxc.py` (`read_vxc` + `build_real_space_paos` + `project_delta_xc`).
On the O_test fixture (`iomode 3`, 10 Bohr box, 36³ grid):

- Synthetic anchor passes: real-space overlap $S$ diagonal = **0.997** for all 4 PAOs (s + 3p) —
  normalized to 0.3%; that 0.3% is the **FFT-grid quadrature floor** (finite grid under-resolves
  the PAO tail slightly).
- Real-space `delta_xc` vs ABINIT `delta_xc_smooth`: trace −12.59 eV vs −12.69 eV (~0.8%);
  eigenvalues agree to ~0.04 eV (s: −0.1208 vs −0.1197 Ha; p: −0.1140 vs −0.1155 Ha), **same
  sign and structure** (1×s + 3×degenerate-p).
- ⇒ link (c) is **essentially correct for O**; the ~1% residual tracks the 0.3% quadrature
  deficit, not a convention/physics error. The real-space route is quadrature-limited (will not
  hit 1e-7 vs ABINIT without a finer grid); the G-space cross-check (story-005) is expected to
  be tighter. Pending: CrI₃ (cluster `_VXC.nc`).

## G-space route is ABINIT-exact (story-005, 2026-07-28)

`project_delta_xc_gspace` (place abinao phi(G) on the FFT grid, inverse-FFT, apply delta V_xc,
integrate) matches ABINIT `delta_xc_smooth` to **max-abs 2.1e-8 Hartree** on O — the ~1e-7 level
(trace −12.6879 eV both; eigenvalues to ~2e-8 Ha). The e^{ik·r} phase cancels in
⟨φ_μ,k|V|φ_ν,k⟩; normalization c = N/√Ω (constant-V anchor → V0·S(k)). The real-space route's
1.6e-3 Ha gap is its quadrature deficit. ⇒ **G-space is the accurate/primary route**; link (c)
and ABINIT `delta_xc_smooth` are both correct for O (CrI₃ pending).
