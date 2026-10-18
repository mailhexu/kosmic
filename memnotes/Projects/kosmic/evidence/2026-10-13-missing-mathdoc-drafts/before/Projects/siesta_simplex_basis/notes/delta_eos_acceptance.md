---
artifact_role: knowledge
type: Project Knowledge
title: Delta EOS Acceptance
status: stable
audience: development
usage_stale: false
confidence: 1.0
created: 2026-08-25
updated: 2026-08-25
validation_procedure: "Focused regression test injects a negative bulk modulus into run_delta_one and verifies that delta computation is not called; seven-volume multi-element ecut evidence exercises invalid-fit classifications."
project: siesta_simplex_basis
tags: [delta, EOS, validation, Birch-Murnaghan, SIESTA]
---

# Delta EOS Acceptance

## Overview

A numeric Birch–Murnaghan parameterization is not necessarily a physically usable equation of state. `run_delta_one` must reject an invalid fit before passing its parameters to the delta-code comparison, so reports never label a pathological E–V curve as a basis-quality result.

## Acceptance rule

For fitted parameters $E_0$, $V_0$, $B_0$, and $B'$, accept a delta result only when all four are finite, $B_0 > 0$, and the fitted $V_0$ lies within the sampled per-atom volume interval:

$$
V_{\min} \le V_0 \le V_{\max}.
$$

The rule is enforced in `autonao.campaign.delta_test.run_delta_one`; rejection returns `None`, so callers must record the absent value as invalid evidence rather than zero or a numeric delta.

## Evidence

The multi-element ecut sweep exposed the missing gate. Ge at 25 Ha produced $B_0=-1749.9$ GPa, while Fe at 25 Ha produced $V_0=8.955$ Å³/atom outside the sampled 9.448–13.548 Å³/atom interval; neither value is a usable basis comparison. The targeted regression test verifies that an injected negative $B_0$ stops before `_compute_delta`.

## Conventions

- A failed EOS fit and an invalid EOS fit are distinct outcomes, but neither produces a delta-quality datum.
- A finite delta number alone is not validation evidence.
- Do not extend the sampled interval merely to make an invalid result fit; use an element-appropriate, physically motivated E–V protocol.

## Linked Concepts

- [PAO Basis Acceptance Constraints](pao_basis_acceptance_constraints.md): Independent periodic validation is required after WFK-based optimization.
- [ABACUS v3 SIAB Bessel Cascade](abacusv3_siab_bessel_cascade.md): The reference-generation and cascade workflow using delta as an independent check.
- [Notation](notation.md): Equation-of-state symbols and units.
