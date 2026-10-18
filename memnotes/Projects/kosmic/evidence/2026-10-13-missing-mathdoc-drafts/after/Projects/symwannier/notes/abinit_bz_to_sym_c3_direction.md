---
artifact_role: knowledge
type: reference
audience: both
title: ABINIT PAO BZ-to-sym direction fails only on CrI3 C3 operations
project: symwannier
status: draft
confidence: 0.95
created: 2026-07-31
last_validated: 2026-07-31
validated_by: direct abinao comparison and scalar rerun probe
tags: [abinit, pao, bz-to-sym, symmetry, c3, phase]
math_provenance: missing
math_provenance_reason: "abinit_bz_to_sym_c3_direction.md display math requires one MathDoc marker per equation"
---

# ABINIT PAO BZ-to-sym Direction Fails Only On CrI3 C3 Operations

The phase-fixed experimental file `cri3_abinit_fixed/cri3_pao_nscfo_PAO_HS.nc`
agrees with direct abinao at all self-inverse symmetry labels, but not at
`bz_to_sym = 5, 6, 9, 10`. These labels are the inverse pairs $5\leftrightarrow9$
and $6\leftrightarrow10$; they are the only non-involutory operations in the
CrI3 spatial group. Their maximum overlap residuals against the abinao
convention are $0.7658$, $0.7658$, $0.7032$, and $0.7032$, respectively.

For a BZ output point $k$ and the output-to-parent real-space operation $R_s$,
the required convention is

$$
k_{\mathrm{parent}}=R_s^{-T}k,
\qquad
B_{p(a),a}=D_s^T\exp\left[+i2\pi k_{\mathrm{parent}}\cdot(t_s-L_{s,a})\right].
$$

Thus overlap rotation uses the relative phase

$$
\exp\left[+i2\pi k_{\mathrm{parent}}\cdot(L_{s,a}-L_{s,b})\right].
$$

The residual is inter-atom only: same-atom blocks are below $5.5\times10^{-10}$,
whereas the largest Cr1--Cr2 $s$--$s$ block is $0.7658$. Cr coefficient blocks
are phase-aligned to numerical precision and iodine blocks are not. This proves
the remaining fault is the atom permutation/translation gauge, not `zarot`.

`compute_all_overlaps_nc` discovers a parent with `symrel(:,:,irot) * k_bz` and
stores that `irot` as `bz_to_sym`. The rotation callers later consume that label
with `indsym` and `zarot`, whose ABINIT convention is inverse-operation based.
The direction ambiguity is invisible for involutions but exchanges each C3 pair.
The parent wave-vector must be passed as the already matched IBZ point
`kpt(:,ikibz)`, not recomputed by applying a potentially transposed `symrel`.

## Falsifiable Minimal Patch

At BZ-parent discovery, retain the matched `ikibz`, store the group inverse of
the BZ-to-IBZ label for the rotation consumers (swap 5/9 and 6/10 for this
CrI3 group), and pass `kpt(:,ikibz)` to every rotation phase. Re-run the 8x8
case. The check passes only if all 64 overlap residuals against direct abinao
fall below the existing numerical floor (about $2\times10^{-5}$ file-to-file),
including the 21 currently bad C3-labelled records; merely changing a phase
sign or using `symrel*k_bz` will not pass because the iodine atom permutation is
also wrong.

## Scalar Rerun Anchor

At BZ record 22, $k_{BZ}=(-3/8,1/4,0)$ and its matched IBZ parent is record 7,
$k_{parent}=(1/4,1/8,0)$.  For the Cr1-s/Cr2-s projectors (1 and 11), the
fresh serial rerun emitted label 9 and gave

$$
\frac{S_{BZ}}{S_{parent}}=+i.
$$

This is the label-9 output-to-parent map (Cr1$\to$Cr1, Cr2$\to$Cr2), with
$L_{Cr1}-L_{Cr2}=(1,0,0)$ and

$$
\exp\left(+i2\pi k_{parent}\cdot\Delta L\right)=+i.
$$

Direct abinao gives $-2.8\times10^{-11}+0.999999999921i$ for the same ratio.
The older overwritten experiment emitted label 5 and $-i$, exactly its
source-exact $k_{BZ}$ phase. This proves the apparent disagreement was file
provenance, not a residual sign ambiguity.

## Fresh Coefficient Projector Check

The fresh `scalar-phase-rerun-current` file has IBZ PAO projectors within
$1.572\times10^{-4}$ of both direct and IBZ-to-BZ abinao.  Its BZ projectors
instead differ by $0.9215$ maximum ($0.2090$ median).  `P=C^\dagger C` was
formed after named-dimension normalization as
`(nsppol,nkpt,nband,nproj)`; this removes all band U(1) gauge ambiguity.

Keeping distinct contiguous radial channels is necessary: Cr is ordered
`s,p,d,s`, so grouping every `l=0` entry into one rotation block is invalid.
With the verified output-to-parent atom map, the only reconstruction matching
direct and abinao IBZ-to-BZ is the real-SH $D^T$ channel rotation with the
conjugated parent-k phase for stored `C=<psi|phi>`:

$$
C_{BZ}=C_{IBZ}\,D^T\exp[-i2\pi k_{parent}\cdot L].
$$

It reaches $1.572\times10^{-4}$ maximum / $4.190\times10^{-5}$ median, the
IBZ file-to-file floor.  `D`, reversed atom mapping, and positive phase all
remain at least $0.5428$, $0.5445$, and $0.9215$ maximum respectively.  The
remaining defect is therefore coefficient expansion convention, not angular
orientation, PAO channel order, atom permutation, or band mixing.

Fresh `H_ibz` equals $C_{IBZ}^\dagger\epsilon C_{IBZ}$ to
$3.11\times10^{-15}$, but stored `H_bz` differs from both stored and
direct-matching reconstructed coefficient spectral sums by $0.4747$ maximum.
Thus no coefficient-only production patch is safe until BZ Hamiltonian and
coefficient expansion share one convention.

## Linked Concepts

- [[abinit_indsym_overlap_phase]]
- [[abinao_ibz_to_bz_symmetry]]
