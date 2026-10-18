---
artifact_role: knowledge
type: reference
audience: both
title: ABINIT indsym convention and NC-PAO overlap phase
project: symwannier
status: stable
confidence: 0.95
created: 2026-07-31
last_validated: 2026-07-31
validated_by: ABINIT source trace and CrI3 C3 coordinates
tags: [abinit, indsym, pao, overlap, symmetry, phase]
---

# ABINIT indsym Convention And NC-PAO Overlap Phase

`symatm` builds `indsym` with the inverse space-group operation. For output
atom $a$, its parent $b=\mathrm{indsym}(4,s,a)$ and integer translation $L$
satisfy

$$
x_b = \operatorname{symrec}_s^T(x_a-t_s)-L.
$$

Since $R_s=\operatorname{symrec}_s^T$, this is $R_s(x_a-t_s)=x_b+L$.
Thus `indsym(1:3,s,a)=L` is the integer part of the transformed output atom
minus its parent, and is subtracted to return the parent to the reference cell.

`abinao.symmetry.compute_indsym` uses the same output-to-parent atom direction
for symmorphic operations: `mapping[s,a]=b` and
$L=R_s x_a-x_b$. Its nonsymmorphic equation is not ABINIT's equation: it uses
$R_s x_a+t_s=x_b+L$, whereas ABINIT uses $R_s(x_a-t_s)=x_b+L$.

For CrI3's C3 real-space operation $R=[[0,-1,0],[1,-1,0],[0,0,1]]$, with atoms
in the NSCF ABO order, the output-to-parent map is `[1,2,6,5,8,7,3,4]` and the
translations are `[[-1,-1,0],[-1,0,0],[-1,-1,0],[-1,-1,0],[-1,0,0],[-1,0,0],[0,0,0],[0,0,0]]`.
There is no nonsymmorphic translation, so the two constructions agree for this
case and neither a reversed atom mapping nor a translation-sign flip explains
the rerun discrepancy.

`rotate_overlap_matrix_nc` applies

$$
\exp\left[+i2\pi k_{\mathrm{BZ}}\mathbin{\cdot}(L_a-L_b)\right].
$$

Although its dummy argument is named `k_rot`, every caller passes `kpt_bz`.
The abinao basis construction instead uses the IBZ parent
$k_{\mathrm{parent}}=\operatorname{symrec}_s k_{\mathrm{BZ}}$ internally.
After $B^\dagger S B$, its overlap phase has the same positive sign but uses
$k_{\mathrm{parent}}$. Therefore a sign-only patch can match the direct abinao
algebra while still disagreeing with an ABINIT rerun: the momentum is different.

## Falsifiable Check

For one non-Gamma CrI3 C3 BZ record, use an $s$--$s$ PAO block (so `zarot=1`) to
predict the stored overlap from its IBZ parent twice. The source-exact formula
with $k_{\mathrm{BZ}}$ must reproduce the rerun; replacing only that momentum
by $k_{\mathrm{parent}}$ tests the direct-abinao convention without angular
rotation ambiguity.

## Linked Concepts

- [[abinao_ibz_to_bz_symmetry]]
- [[cri3_tb2j_symmetry_operator]]
