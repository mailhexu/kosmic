---
artifact_role: knowledge
audience: both
title: All-Electron SOC Reference from oncvpspr.x
id: ae_soc_oncvpspr_reference
date: 2026-08-04
project: siesta_simplex_basis
status: draft
validated_by: computation
tags: [soc, all-electron, oncvpsp, dirac, pseudopotential, transferability, magnetic-descriptor]
related_files:
  - scripts/compute_ae_soc_strengths.py
  - papers/magnetic_descriptor/ae_soc_strengths.json
  - papers/magnetic_descriptor/pp_vs_ae_soc_comparison.json
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "ae_soc_oncvpspr_reference.md display math requires one MathDoc marker per equation"
---

# All-Electron SOC Reference from oncvpspr.x

## What

The ONCVPSP generator executable `oncvpspr.x` (ONCVPSP-4.0.1 with libxc) runs a
self-consistent fully-relativistic (Dirac) all-electron atom calculation before generating
any pseudopotential. Its reference-configuration eigenvalue table prints, for each $(n,l)$
shell, two $j$-resolved eigenvalues for $l>0$: $\varepsilon^{\rm AE}_{j=l+1/2}$ and
$\varepsilon^{\rm AE}_{j=l-1/2}$ in Hartree. The AE SOC splitting

$$
\Delta\varepsilon^{\rm AE}_{nl}
= \varepsilon^{\rm AE}_{j=l+1/2} - \varepsilon^{\rm AE}_{j=l-1/2}
$$

is the pseudopotential-independent atomic baseline: it uses the full nuclear Coulomb
potential, so it depends only on $Z$, the electronic configuration, and XC — not on
pseudopotential construction choices (core radius, projectors, NLCC, etc.).

## How

`scripts/compute_ae_soc_strengths.py` batch-runs `oncvpspr.x` on the PseudoDojo PDv0.4 PBE
`.in` files (85 elements), parses the eigenvalue table, applies the same 11 eV
deep-and-closed-shell semicore rule, and emits `ae_soc_strengths.json` (88 valence $l\ge1$
channels).

Binary: `/home/hexu/.local/src/oncvpsp-psml-cmake-4/_build/src/oncvpspr.x`.
libxc: `LD_LIBRARY_PATH=/home/hexu/.local/src/esl-bundle-master/build/install/lib`.
Inputs: `/home/hexu/projects/pseudo_dojo/pseudo_dojo/pseudos/ONCVPSP-PBE-PDv0.4/{Element}/`.
Parallel run (8 workers) completes all 85 elements in ~12 min.

## Finding: PP descriptor overestimates the AE splitting

The NC-FR PP direct-$j$ descriptor (bare unscreened semilocal PP channels) systematically
overestimates the AE Dirac splitting:

| channel | PP (eV) | AE (eV) | ratio |
|---|---:|---:|---:|
| Si $3p$ | 0.056 | 0.032 | 1.8 |
| Se $4p$ | 0.776 | 0.375 | 2.1 |
| Sn $5p$ | 3.947 | 0.444 | 8.9 |
| Tl $6p$ | 8.340 | 1.036 | 8.0 |
| Bi $6p$ | 11.848 | 1.921 | 6.2 |

Across 85 matched channels: median PP/AE ratio 2.0 for $l=1$, 3.2 for $l=2$, $\approx1.3$ for
$l=3$.

## Physical origin

The bare PP channel removes valence Hartree/XC screening, pulling the orbital inward where
the spin-orbit potential is strongest. The AE Dirac calculation includes this screening,
giving values consistent with experimental atomic fine structure (Si $3p\sim 0.03$ eV;
Pb $6p\sim 1.3$ eV; Bi $6p\sim 1.5$ eV).

## Implication

The PP descriptor retains its value as a deterministic, monotonic, PP-intrinsic ranking
proxy. But it is not a quantitative measure of the atomic SOC splitting. The AE reference
from `oncvpspr.x` is the correct pseudopotential-independent atomic baseline. For
solid-state SOC validation, a converged FP-LAPW calculation (FLEUR) remains the acceptance
anchor ([pp_independent_soc_validation](pp_independent_soc_validation.md)).

## Evidence

- `ae_soc_strengths.json`: 85 elements, 88 valence $l\ge1$ channels.
- `pp_vs_ae_soc_comparison.json`: 85 matched PP-vs-AE channels.
- `methods.md` updated with AE reference section.
- `main.tex` compiles (16 pages) with AE comparison table.
- `py_compile` passed.
