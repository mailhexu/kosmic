---
artifact_role: knowledge
type: Project Knowledge
title: ABINIT WFK planewave conventions
description: Verified ETSF WFK reader contract, reciprocal-coset weight, and nic6 fixture protocol for ABINIT electronic unfolding.
confidence: 0.99
created: 2026-09-21
updated: 2026-09-21
validation_procedure: 'Run the nic6 Si probes with iomode 3, istwfk 1, chkprim 0; inspect ETSF variables; assert cg normalization, the Parseval sum rule, and primitive-fold-sector spectra.'
project: unfolding
status: stable
audience: development
usage_stale: false
evidence: []
---

# ABINIT WFK planewave conventions

## Overview

ABINIT electronic unfolding uses the native WFK file as the source of
planewave coefficients. The planewave basis is orthonormal, so the
primitive-translation operator is diagonal in the stored G-vector basis:
there is no atom/orbital relabel map and no LCAO overlap metric. The
unfolding weight is a reciprocal-coset projector.

The contract was verified on nic6 with ABINIT development module
`abinit/dev@d5380e0cb-gcc` (10.9.0 base), a 2-atom primitive Si probe,
and an 8-atom conventional-cubic Si probe.

## Weight and translation sectors

Let the row-convention supercell matrix be $S$, with $A_s=S A_p$;
$S$ is already the project notation for this integer matrix. For a
supercell state at $\mathbf{K}$ and a supercell reciprocal vector
$\mathbf{G}_s$ with reduced integer index $\mathbf{n}_s$, define

$$
\mathbf{t} = S^{-T}(\mathbf{K}+\mathbf{n}_s).
$$

The fractional part of $\mathbf{t}$ labels one of
$|\det S|$ primitive fold sectors $\mathbf{k}_m$. The weight of
band $n$ in that sector is

$$
W_n(\mathbf{k}_m) =
\sum_{\mathbf{G}_s \in m}
\left|c_{n\mathbf{K}}(\mathbf{G}_s)\right|^2.
$$

The direct-space character projector gives the same result. With
$\mathbf{R}$ running over primitive translations modulo the supercell
lattice,

$$
P_m(\mathbf{G}_s) = \frac{1}{|\det S|}
\sum_{\mathbf{R}}
\exp\left[2\pi i\left(\mathbf{w}-\mathbf{k}_m\right)\cdot\mathbf{R}\right],
$$

where $\mathbf{w}=S^{-T}(\mathbf{K}+\mathbf{n}_s)$. This
constructs the sector indicator without reciprocal-space labels.

For normalized coefficients, Parseval gives

$$
\sum_m W_n(\mathbf{k}_m) = \sum_{\mathbf{G}_s}
\left|c_{n\mathbf{K}}(\mathbf{G}_s)\right|^2 = 1.
$$

Pristine-supercell eigenstates are binary by **degenerate group**, not
necessarily band by band: cubic SC-Gamma X-fold degeneracies may rotate
among equivalent sectors. This reuses the project's degenerate-group
policy described in [Ring vs ideal unfolding weights](weight-definitions.md).

## ETSF WFK reader contract

ABINIT 10.9 writes ETSF Nanoquanta netCDF WFKs (`file_format_version 3.3`)
when `iomode 3` is set. The direct `netCDF4` reader needs these variables:

| ETSF variable | Meaning | Reader rule |
|---|---|---|
| `reduced_coordinates_of_kpoints` | SC k-points | supercell fractional coordinates |
| `number_of_coefficients` | npw per k | trim padded axes to this count |
| `reduced_coordinates_of_plane_waves` | SC G-vector indices | integer, `(nk,max_npw,3)` |
| `coefficients_of_wavefunctions` | cg | `(nspin,nk,mband,nspinor,max_npw,2)`, convert re/im to complex |
| `eigenvalues` | band eigenvalues | Hartree; convert to eV only at adapter boundary |
| `istwfk` | storage mode | require 1 for every k |
| `primitive_vectors` | cell | Bohr; stored rows equal matching `rprim` in the nonsymmetric probe; preserve row convention |

`istwfk 1` is a strict v1 reader contract. Automatic Gamma storage chose
`istwfk=2` and stored only 266 Gs where full storage held 531; reconstructing
the time-reversed half sphere is intentionally out of scope.

`abipy.abilab.abiopen` can parse WFK structure/spin metadata but abipy 1.0.0
exposes no raw-cg interface; direct `netCDF4` is therefore the implementation
route.

## Nic6 fixture protocol

Load the swmgr-recorded build through a login shell:

```bash
module use ~/privatemodules
module load abinit/dev@d5380e0cb-gcc
```

Fixture inputs must set:

- `iomode 3`: emit ETSF netCDF; this build lacks `HAVE_NETCDF_DEFAULT` and
  otherwise writes a Fortran-binary WFK.
- `istwfk 1`: full G sphere.
- `chkprim 0`: permit the 8-atom conventional cubic supercell.
- `prtwf 1` and nband headroom: avoid top-of-band degeneracy mixing.

Use pseudo-dojo NC-SR PBE **psp8** Si/P potentials staged from the control
machine. The nic6 build has no libpsml, so PSML files are unreadable.

Primitive and supercell reference calculations must use matched SCF sampling:
the primitive k-set is exactly the set that folds onto each supercell k-point.
Otherwise the self-consistent potentials differ; the probe measured
sector-dependent quasi-constant shifts (Gamma −22 mHa, X +5 mHa with
2–5 mHa spread), not an unfolding defect.

## Verified Si seal

For the 8-atom conventional-cubic Si supercell,

$$
S = \begin{pmatrix}
-1 & 1 & 1 \\
1 & -1 & 1 \\
1 & 1 & -1
\end{pmatrix},
\qquad |\det S| = 4.
$$

The SC-Gamma fold images were Gamma and the three primitive X points

$$
(0,\tfrac12,\tfrac12),\quad(\tfrac12,0,\tfrac12),\quad(\tfrac12,\tfrac12,0).
$$

Do not label $(1/2,0,0)$ as X in this fcc-primitive coordinate system:
it is an L-type point. The real-cg probe sealed coefficient normalization
to $4.2\times10^{-15}$ and the Parseval sector sum to
$1.4\times10^{-14}$.

## Linked concepts

- [Module map and conventions](dev-module-map.md): lazy optional-backend and
  public-API conventions.
- [Ring vs ideal unfolding weights](weight-definitions.md): the existing
  degenerate-group and pristine-oracle policy; PW weights differ from
  non-orthogonal LCAO ideal weights at generic k.
- [Notation](notation.md): shared definition of $S$ and the WFK symbols.
- [ABINIT WFK research memo](../specs/research/2026-09-21-abinit-wfk-planewave-unfolding.md): full probe evidence and reader decision.
