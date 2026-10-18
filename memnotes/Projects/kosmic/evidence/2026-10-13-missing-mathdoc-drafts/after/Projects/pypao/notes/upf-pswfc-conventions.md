---
artifact_role: knowledge
type: reference
audience: both
title: UPF PP_PSWFC conventions for FR ONCV files
id: upf-pswfc-conventions
date: 2026-08-18
project: pypao
status: draft
validated_by: manual
tags: [pypao, upf, oncv, fr, pseudo-energy, rydberg, quadrature]
related_files:
  - pypao/src/pypao/orbital/upf.py
links_to: [orbital_record_unification]
linked_from: []
math_provenance: missing
math_provenance_reason: "upf-pswfc-conventions.md display math requires one MathDoc marker per equation"
---

# UPF PP_PSWFC conventions for FR ONCV files

Validated on `Dojo-NC-FR/PBE/Fe.upf` (ONCVPSP-4.0.1 FR). Applies to `pypao.orbital`
UPF-derived moment/descriptor work.

## Units and tags

- `PP_PSWFC` children are **numbered tags** `PP_CHI.1, PP_CHI.2, ...` (not bare `PP_CHI`);
  `ElementTree.iter("PP_CHI")` finds nothing — iterate `PP_PSWFC` children by prefix.
- Per-child attributes: `label`, `l`, `occupation`, **`pseudo_energy` in Rydberg**
  (1 Ry = 13.605693 eV). Fe 3S: −6.909 Ry = −93.996 eV = the AE 3s eigenvalue exactly.
- `pypao.orbital.read_orbitals` fills label/l/occupation/radials but **not**
  `eigenvalue`/`cutoff` for UPF sources — parse the attributes separately if needed.

## FR j-pairs

Fully-relativistic files list each valence $(n,l>0)$ channel as a **j-pair of PP_CHI
entries** (pypao's per-l zeta counter calls them zeta 1/2). Their occupations are
j-degeneracy fractions of one physical shell (Fe 3D: 3.6 + 2.4 = d⁶; 3P: 4 + 2 = p⁶), and
the `pseudo_energy` difference of the pair equals the AE Dirac $j$-splitting (Fe 3p: 1.542 eV,
matching `ae_soc_strengths.json` to given precision). The $l=0$ channel has a single entry.

## Quadrature

PP_PSWFC radial functions satisfy the **discrete** norm

$$
\sum_i u_i^2\,\mathrm{rab}_i = 1 ,
$$

not a trapezoid integral (trapezoid over $(g, u^2 \mathrm{rab})$ returns 0.01 — the grid
spacing — and similar artifacts). Moments must be computed as plain weighted sums:
$\langle r \rangle = \sum_i r_i\, u_i^2\, \mathrm{rab}_i$.

## Confinement radii

Per-$l$ pseudization cutoffs are in the `PP_INFO/PP_INPUTFILE` text block
(`# l, rc, ep, ncon, nbas, qcut`), not as PP_CHI attributes (PP_BETA/PP_RELBETA carry their
own `cutoff_radius`, which is the KB projector radius, a different quantity).
