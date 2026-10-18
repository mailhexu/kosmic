---
artifact_role: knowledge
audience: both
title: Pseudopotential-Independent SOC Validation
id: pp_independent_soc_validation
date: 2026-08-03
project: siesta_simplex_basis
status: draft
validated_by: research
source_memo: ../specs/research/2026-08-03-pp-independent-soc-observables.md
tags: [soc, pseudopotential, all-electron, fleur, transferability, validation]
related_files:
  - pypao/src/pypao/analysis/soc.py
  - /home/hexu/projects/siesta_dev/siesta/Docs/tex/sections/Options/Pseudopotentials.tex
  - /home/hexu/projects/pseudo_dojo/pseudo_dojo/ppcodes/oncvpsp.py
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "pp_independent_soc_validation.md display math requires one MathDoc marker per equation"
---

# Pseudopotential-Independent SOC Validation

## Decision

Do not require agreement of individual pseudoatomic eigenvalues or direct-$j$ NC-FR
splittings across pseudopotentials. Treat these as pseudopotential-provenance diagnostics.
Validate a pre-registered, fixed-geometry **solid-state energy difference** against a
converged all-electron FP-LAPW calculation, with a second pseudopotential family as a
sensitivity check.

## Reason

A norm-conserving pseudopotential deliberately replaces the core. Its core radius, frozen
core/semicore partition, reference configuration, local channel, projectors, nonlinear core
correction, and potential zero vary by construction. Therefore its bare pseudoatomic
spectrum is not a shared observable. `pypao.analysis.soc` reconstructs and separately solves
the bare $j=l\pm1/2$ channels; that result omits KB separabilization, PAO confinement,
screening, hybridization, and solid-state self-consistency.

PseudoDojo itself keeps all-electron and pseudo radial waves and energy-dependent logarithmic
derivatives as a same-generator transferability test. It does not establish equality between
two independently generated pseudopotential spectra.

## Required comparison

1. Fix geometry, XC, charge, valence/semicore partition, magnetic state, spin direction,
   smearing, fractional $\mathbf{k}$ target, and SOC definition.
2. Pre-register a symmetry/manifold-resolved splitting or a SOC-on/off gap shift. Match
   states by irrep/character/subspace—not printed band index.
3. Independently converge that target in SIESTA NC-FR for each PP family, including the PAO
   basis, mesh, $k$ mesh, SCF, smearing, and band window.
4. Compute the matched target with converged FLEUR FP-LAPW. This removes the
   pseudopotential/frozen-core approximation but still requires explicit basis and
   second-variation-SOC convergence.
5. Report PP-to-all-electron residuals and PP spread. Do not average values or fit a universal
   NC-to-PAW SOC scale factor.

For a predeclared application tolerance $T_Q$ and independently estimated numerical
uncertainties $u_i$, accept a PP result only when

$$
|Q_i-Q_{\rm AE}|\le T_Q+u_i+u_{\rm AE}.
$$

Without the FP-LAPW row, agreement of two PP families is only provisional reproducibility:
they can share a bias.

## Boundary

Atomic total-energy fine-structure differences can preflight an element, but are not a
substitute for a solid observable. Kohn-Sham eigenvalues are not experimental excitation
energies. GPAW PAW in converged PW/FD mode is a useful independent control, but it retains
PAW setup and frozen-core approximations, so it is not the all-electron acceptance anchor.

## Evidence

- [2026-08-03-pp-independent-soc-observables](2026-08-03-pp-independent-soc-observables.md): source-cited research memo and full
  FLEUR-anchored protocol.
- [soc_strength_descriptor](soc_strength_descriptor.md): direct-$j$ definition and its first-order matrix-element
  limitation.
- [gpaw_independent_validation_reference](gpaw_independent_validation_reference.md): GPAW PW/FD cross-code controls and boundary.
