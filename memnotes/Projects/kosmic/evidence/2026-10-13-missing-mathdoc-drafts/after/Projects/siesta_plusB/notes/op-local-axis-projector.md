---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-08-09
last_validated: 2026-08-11
validation_procedure: "sympy derivation + SIESTA fixed-DM one-step covariance (unrotated, z→x, theta=phi=90°) agree to the same six-decimal output (<1 µeV) at B=0.5 eV"
project: siesta_plusB
status: draft
validated_by: automatic
tags: [op, local-axis, majority-projector, rotational-invariance, over-polarization]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "op-local-axis-projector.md display math requires one MathDoc marker per equation"
---

# Local-spin-axis (LSA) majority-spin projector for +B


## Overview

A rotationally-covariant generalization of the "apply +B only to the major spin channel"
fix, to make it work for arbitrary (non-collinear) spin direction. Derives and verifies
that the LSA majority projector is (i) rotationally invariant, (ii) reduces to the
collinear majority-only mode, and (iii) caps the $|L|$ over-polarization runaway.

## Motivation

The spin-scalar $V^{OP}$ (total-moment mode) drives both spin channels; at the large $B$
needed to reach the Hund moment it **over-polarizes** (promotes electrons into the
unoccupied minority channel, $|L|\to8{-}12$). The collinear per-channel fix (apply $+B$
to the majority-z channel only) partly fixes this but is **z-axis-bound** and breaks for
off-$z$ spin. The LSA projector removes the z-axis assumption.

## Formulation

Majority projector along the local spin direction $\hat s$ (the atom's spin unit vector):

$$
P_{+}(\hat s)=\tfrac12(\mathbf1+\hat s\cdot\boldsymbol\sigma),\quad P_{-}=\mathbf1-P_{+}.
$$

Majority orbital moment of the spinor occupation $N$:

$$
\langle L_\alpha\rangle_{+}=\mathrm{Tr}_{orb,spin}((L_\alpha\otimes P_{+})\,N).
$$

LSA energy and variational potential:

$$
E^{OP}_{LSA}=-B\sum_\alpha\langle L_\alpha\rangle_{+}^{2},\qquad
V^{OP}_{LSA}=-2B\sum_\alpha\langle L_\alpha\rangle_{+}\,(L_\alpha\otimes P_{+}),
$$

with the Euler relation $E^{OP}_{LSA}=\tfrac12\mathrm{Tr}(V^{OP}_{LSA}N)$ (no
double-counting partner).

## Verified properties (sympy, l=1 and l=3)

- **Collinear limit $\hat s=\hat z$:** $P_{+}=|\!\uparrow\rangle\langle\uparrow\!|$ ⇒
  $V^{OP}_{LSA}$ acts only on the $\uparrow\uparrow$ block with $-2B\langle L\rangle_{+}\!\cdot\!L$;
  the other three spin blocks are exactly zero ⇒ the historical "major spin channel only".
- **Minority driving is removed:** $P_{-}V^{OP}_{LSA}P_{-}=0$ identically, so the OP
  term itself never drives the minority/unoccupied subspace. This removes the
  total-mode mechanism behind the $|L|\to8{-}12$ runaway, but is not by itself a
  mathematical bound on total $|L|$ under the full SCF Hamiltonian.
- **Rotational covariance:** $V^{OP}_{LSA}(RNR^{\dagger})=R\,V^{OP}_{LSA}(N)\,R^{\dagger}$
  for $R=R_{orb}\otimes U_{spin}$ ⇒ rotationally invariant for arbitrary spin direction.

## Implementation implication

LSA is non-spin-scalar, so it requires all four spin channels. `m_pot_dftu.F90`
builds `V_B(1..4)`, accumulates `Vi_oc(jo,1..4)`, and uses SIESTA's
globally-Hermitian off-diagonal mapping:

$$
H_{\uparrow\downarrow}\gets\operatorname{conj}(V_{\downarrow\uparrow}),
\qquad
H_{\downarrow\uparrow}\gets\operatorname{conj}(V_{\uparrow\downarrow}).
$$

The same mapping is required in both `H_dftu_so` and `H_dftu_so_oc`.
`H_dftu_so_oc` enters the four-channel trace in `E_dftu_so`; omitting its channels
3,4 leaves the Hamiltonian populated but drops the LSA off-diagonal OP energy,
breaking reported rotational invariance.

### Real-SH convention guardrail

The source of fixed-DM fixtures is `papers/DFT_plus_B/rotate_dm.py`; its active global
rotation is used unchanged by the covariance test.

`derive_op_local_axis.py` and `rotate_dm.py` encode equivalent real-spherical-harmonic
bases with different signed column phases for selected $m$ values. A rotation and the
angular-momentum matrices must remain in the same basis; mixing a $C$ matrix from one
with an $R$ from the other silently changes signs. The production implementation
therefore reuses SIESTA's `int_so_ang` convention, while fixed-DM tests delegate the
entire global rotation to `rotate_dm.py`.

The validated historical Hund seed is $R^{\mathsf T}nR$, not $RnR^{\mathsf T}$.
The existing seed code still uses its x template for arbitrary off-z directions, so
release trajectories are not a valid x/y/z RI diagnostic.

## Fixed-DM validation

With the same saved spinor DM, B=0.5 eV, `OP.UseLocalAxis T`, and one SCF
iteration, the unrotated fixture, the default z→x rotation, and the generic
$(\theta,\phi)=(90^\circ,90^\circ)$ rotation each reported:

$$
E_{\mathrm{total}}=-2410.719525\ \mathrm{eV}.
$$

The pre-fix z→x discrepancy was 1.663902 eV. The B=0 control already agreed within
1 µeV, isolating the missing LSA off-diagonal OP energy trace.

## Free-SCF qualification

The preceding failed release trajectories used the sign-inverted OP potential and are
not physics or mixer evidence. `V_B` is assembled as $V_{\nu\mu}$ and conjugated into
$H_{\mu\nu}$; using `Bval=+B` therefore produced the opposite physical potential.
The two-step fixed-DM regression made this visible: the first update reversed
$\langle\mathbf L\rangle$ by $179.5^\circ$ at unchanged magnitude. With
`Bval=-B`, its normalized consecutive dot product is $0.999812$.

At B=0.5 eV, unrotated, z→x, and $(90^\circ,90^\circ)$ globally rotated high-moment
DMs now follow covariant 100-step free-SCF trajectories with
$4.98438\leq|\langle\mathbf L\rangle|\leq4.98668$, maximum inter-step turn
$1.1124^\circ$, and final totals $-2386.163239$, $-2386.163239$, and
$-2386.163238$ eV. No 8–12 over-polarization occurs. Continuing the unrotated
trajectory for 200 more steps retains $|\langle\mathbf L\rangle|=5.11962$; SIESTA
still reaches its iteration cap despite residuals shrinking to
$dD_{\max}=8.88\times10^{-4}$ and $dH_{\max}=4.35\times10^{-3}$ eV.

## Orbital-moment direction dynamics

`INIT_HUND_REL` records the orbital vector $\langle\mathbf{L}\rangle$, not the spin
direction. The old $179.5^\circ$ sign reversal was a deterministic potential-sign
defect, not a mixer diagnosis: reversing **only** the SCF potential sign changed the
first-step dot product from $-0.999960$ to $+0.999812$. The corrected trajectories
turn continuously rather than alternating signs; their remaining slow rotation is
rotationally covariant across the three globally rotated inputs.


## Linked Concepts

- [notation](notation.md): $B$, $\langle L\rangle$, $V^{OP}$ symbols.
- [scf-convergence-lanthanides](scf-convergence-lanthanides.md): the over-polarization ($|L|\to8{-}12$) this addresses.
- [OP double counting](../specs/research/2026-07-16-op-double-counting.md): the Euler/no-dc structure reused.
- Derivation script: `papers/DFT_plus_B/derive_op_local_axis.py`; writeup `papers/DFT_plus_B/equations.md` §(f).
