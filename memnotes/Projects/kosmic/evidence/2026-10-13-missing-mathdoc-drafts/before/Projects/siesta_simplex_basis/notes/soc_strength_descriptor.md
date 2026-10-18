---
artifact_role: knowledge
audience: both
title: SOC Strength Descriptor and the Matrix-Element Pitfall
id: soc_strength_descriptor
date: 2026-08-02
project: siesta_simplex_basis
status: stable
validated_by: automatic
tags: [pypao, soc, spin-orbit, descriptor, magnetic, periodic-table, semicore]
related_files:
  - pypao/src/pypao/analysis/soc.py
  - scripts/compute_soc_strengths.py
  - scripts/plot_soc_periodic_table.py
  - papers/magnetic_descriptor/soc_strengths.json
links_to: [psml_full_relativistic_j_averaging, semicore_identification]
linked_from: []
type: Project Knowledge
---

# SOC strength descriptor per (n, l) and the matrix-element pitfall

## What

The primary value is

$$
\Delta\varepsilon_{nl}=\varepsilon_{nl}^{j=l+1/2}-\varepsilon_{nl}^{j=l-1/2},
$$

with each $\varepsilon$ from the bare reconstructed $j$-potential through boxed tridiagonal
diagonalization (`find_eigenvalues_boxed_fem`). Numerov root searching instead lands on spurious
roots for a few channels because $V_{l,j}$ reshapes the near-nucleus potential.
This is the FR PP's own direct-$j$ bare radial splitting, not a SIESTA level or band
splitting: it omits KB separabilization, PAO confinement, hybridization, and self-consistency.
It can show broad within-family $Z$ scaling, but individual PP construction and source-release
differences preclude a globally monotonic elemental trend. The periodic table splits each cell
into shell stripes (s grey = SOC 0) and is emitted to `papers/magnetic_descriptor/soc_strengths.json`.

## The robust descriptor: bare $j$-channel eigenvalue splitting

$$
\Delta\varepsilon_{nl}=\varepsilon_{nl}^{j=l+1/2}-\varepsilon_{nl}^{j=l-1/2},
$$

each $\varepsilon$ from solving the radial Schrödinger equation with the **bare**
reconstructed $j$-potential $V_{l,j}$. It is a PP-level diagnostic, not an onsite-SOC level.
The direct solve is more robust than the first-order matrix element, but a source-consistent
release, grid/box convergence, and state-identity check are required before interpreting local
reversals as physical.

## Key finding: the first-order matrix element is NOT a usable descriptor

The textbook $\xi_{nl}=\langle\phi|V_l^{SO}|\phi\rangle$ (with $\Delta\varepsilon^{(1)}=\tfrac{2l+1}{2}\xi$)
is **unreliable** here. $V_l^{SO}$ is sharply peaked at the nucleus, so the integral is
hyper-sensitive to the orbital's inner-region behaviour: over-bound bare orbitals inflate it
wildly (Ge 4p → 37 eV), SCF-screened orbitals make it erratic and non-monotonic. The direct
$j$-splitting avoids this inner-region matrix-element sensitivity, but it is still subject to
the pseudopotential's own channel construction and finite-box state selection.

## Semicore exclusion

By SCF-eigenvalue depth $> 11$ eV below the HOMO **and closed-shell occupation**
$2(2l+1)$ (not by $n$; see [semicore_identification](semicore_identification.md)). This retains deep post-TM $d^{10}$
shells (Ge 3d, In 4d, $\sim12$ eV) as semicore while preserving chemically active deep
open shells, notably rare-earth 4f/5d channels.

## Deviations from the original PRD (documented)

- Method 1: **bare** direct $j$-solve (PRD said screened; screening breaks the trend).
- Method 2 ($\xi$): flagged **unreliable** (PRD assumed both methods reliable).
- Semicore threshold 15 → **11 eV** (actual $d^{10}$ depths ~12 eV; honors "$d^{10}$=semicore").

## Coverage and source controls

The refreshed mixed-source output has 84 H--Rn elements and 87 non-semicore $l\ge1$ channels:
Ge/Rh v3 files fail header identity and use older raw-$lj$ fallbacks; Dy now fails the direct
solve; At is unavailable. Its Ge--Se, Sn--Sb, and Tl--Pb--Bi p reversals are source/solver
controls, not established atomic trends; see [nc_fr_p_channel_anomalies](nc_fr_p_channel_anomalies.md).

The internally consistent PseudoDojo 0.4 stringent source has 72 valid PSML files, 64
non-semicore $l\ge1$ channels, and restores local p order Ge $<$ Se, Sn $<$ Sb, and
Tl $<$ Pb $<$ Bi; see [dojo04_stringent_ncfr_soc_control](dojo04_stringent_ncfr_soc_control.md). Its table is
`papers/magnetic_descriptor/figures/soc_periodic_table_dojo04_stringent.png`.
