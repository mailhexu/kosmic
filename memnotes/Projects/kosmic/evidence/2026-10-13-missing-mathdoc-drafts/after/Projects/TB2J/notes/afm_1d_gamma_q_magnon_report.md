---
artifact_role: knowledge
audience: both
confidence: 0.95
created: 2026-08-05
last_validated: 2026-08-05
project: TB2J
status: draft
tags: [magnon, antiferromagnet, zone-folding, one-dimensional, visualization]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "afm_1d_gamma_q_magnon_report.md display math requires one MathDoc marker per equation"
---

# One 1D Antiferromagnetic Magnon at Chemical Γ and Q=1/2

## The short answer

There is only **one physical wobble** and therefore only **one clock**. The
chemical labels Γ and $Q=1/2$ describe two visible parts of that one wobble.
They are not two independent magnons which happen to have the same energy.

Think of a single clock hand. Its left-right shadow and its up-down shadow look
different, but both are made by the same hand and turn at the same rate. In the
AFM chain, chemical Γ and chemical $Q=1/2$ play the role of those two shadows.

![One 1D AFM magnon shown as uniform and staggered time components](assets/one_dimensional_afm_magnon_unfolding.png)

## Start with the resting chain

Imagine equally spaced magnetic atoms in one dimension. The ordinary chemical
crystal has one atom in each small box. Its magnetic ground state is
antiferromagnetic:

```text
small boxes:          A     B     A     B     A     B
resting spins:        up   down   up   down   up   down
```

The *chemical* crystal repeats after one box. The *magnetic* picture does not:
a spin is flipped after one box. It repeats after two boxes. That larger
magnetic repeat is the entire reason two chemical momentum labels can refer to
one magnetic momentum.

## What Γ and Q=1/2 mean in this simple chain

A wave label tells us how neighboring boxes compare.

| Chemical label | Picture from box to box | Everyday description |
|---|---|---|
| Γ, or $k=0$ | same, same, same | uniform |
| $Q=1/2$, or $k=\pi/a$ | plus, minus, plus, minus | alternating/staggered |

Here $a$ is the chemical-cell spacing. In a strictly 1D notation, the edge of
the chemical Brillouin zone is often called X rather than R. We call it
$Q=1/2$ in this report. It is the 1D analogue of the cubic R point
$(1/2,1/2,1/2)$ in the earlier SrMnO3 example.

Because the AFM ground state already alternates with $Q=1/2$, the magnetic
Brillouin zone is half as large as the chemical one. Within that magnetic-zone
bookkeeping,

$$
 k_{
 \rm chemical}=0
 \quad\hbox{and}\quad
 k_{
 \rm chemical}=Q=1/2
$$

name the same magnetic-zone Γ point.

## Watch the one magnon move

A magnon is a very small wobble around the resting arrows. Do not imagine the
arrows making large flips; the arrows in the figure are enlarged solely so the
motion is easy to see.

Take a snapshot at the start of the wobble, $t=0$. The sideways part of the
motion points right on every atom:

```text
sideways motion at t = 0:     right  right  right  right
chemical name:                   Γ      Γ      Γ      Γ
```

This is uniform, so a chemical-cell observer calls this part Γ.

Wait one quarter of a cycle. The same wobble has turned through its transverse
plane. Now the sideways part points alternately up and down:

```text
sideways motion at t = T/4:     up    down    up    down
chemical name:                   Q      Q      Q      Q
```

This is staggered, so the chemical-cell observer calls this part $Q=1/2$.

The two snapshots are not two experiments and not two separate motions. They
are the same motion at two times, separated by one quarter of its period.

## A compact mathematical version

Choose the resting A spin along $+z$, the resting B spin along $-z$, and the
spiral rotation axis along $x$. For an ideal circular magnetic-Γ wobble, the
small transverse displacements can be written as

$$
\delta \mathbf{S}_A(t)
=
\left(\cos\omega t,\;\sin\omega t\right),
\qquad
\delta \mathbf{S}_B(t)
=
\left(\cos\omega t,\;-\sin\omega t\right).
$$

The $x$ component is the same on A and B:

$$
\delta S_A^x=\delta S_B^x,
$$

so it is the uniform, chemical-Γ component. The $y$ component has opposite
signs:

$$
\delta S_A^y=-\delta S_B^y,
$$

so it is the alternating, chemical-$Q$ component. Both contain the same
factor $\omega$: they are two time-quadrature components of one normal mode.

The period is $T=2\pi/\omega$, and the magnon energy is

$$
E=\hbar\omega.
$$

Therefore the chemical labels report one energy:

$$
E_{\rm chemical}(\Gamma)
=
E_{\rm chemical}(Q=1/2)
=
\hbar\omega.
$$

## Folding and unfolding are only a change of labels

These words sound technical but mean simple bookkeeping:

- **Folding:** start with the small chemical boxes. Chemical Γ and chemical
  $Q=1/2$ are placed on the same magnetic-zone Γ point.
- **Unfolding:** start with magnetic-zone Γ. When expressed using small
  chemical boxes, it has representatives at chemical Γ and at chemical
  $Q=1/2$.

Neither operation changes the springs, exchange forces, or frequency. It only
changes the ruler used to label the same mode.

## What should and should not be concluded

**Correct conclusion:** one AFM normal mode can be seen through a uniform
chemical-Γ component and an alternating chemical-$Q$ component. Both have the
same frequency because both belong to that one mode.

**Incorrect conclusion:** Γ and $Q=1/2$ must always be two separately visible
peaks of identical brightness. Scattering experiments measure intensity as
well as frequency. The two components can have different polarization factors
and structure factors, so one can be bright while the other is weak.

**Scope of this picture:** it is the clean two-sublattice, collinear AFM with
the translation-plus-spin-rotation symmetry intact. Anisotropy can make the
wobble elliptical rather than circular; compatible anisotropy does not turn
one mode into two. Terms that break the relevant combined symmetry can change
the simple relation.

## Practical checklist

When Γ and $Q=1/2$ have the same calculated AFM magnon frequency, ask:

1. Does the magnetic ground state alternate from one chemical cell to the next?
2. Is the ordering vector $Q=1/2$ in reciprocal-lattice units?
3. Are the two points related by adding that ordering vector?
4. Is the calculation using the intended AFM reference state and a compatible
   rotation axis?

If all four answers are yes, equal frequencies are expected from magnetic-zone
folding. It is a relabeling of one magnetic normal mode, not an accidental
degeneracy.

## Related Notes

- [magnon_Jq_transform](magnon_Jq_transform.md)
- [magnon_hamiltonian](magnon_hamiltonian.md)
- [magnon_diagonalization](magnon_diagonalization.md)
- [notation](notation.md)
