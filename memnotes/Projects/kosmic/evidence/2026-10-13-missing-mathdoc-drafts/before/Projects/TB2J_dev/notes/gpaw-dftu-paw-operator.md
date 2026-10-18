---
artifact_role: knowledge
type: reference
audience: both
confidence: 0.95
created: 2026-08-10
last_validated: 2026-08-10
validation_procedure: "GPAW 26.7.0 source audit plus physical symmetry-on FeO PAW covariance and exchange-shell probes."
project: TB2J_dev
status: stable
validated_by: automatic
tags: ["gpaw", "paw", "dft-u", "projector-green", "exchange"]
related_files: ["TB2J/TB2J/interfaces/gpaw_projector.py", "gpaw/hubbard.py", "gpaw/old/hamiltonian.py", "gpaw/new/pot_calc.py"]
---

# GPAW DFT+U PAW Exchange Operator

## Overview

For a GPAW 26.7.0 symmetry-reduced collinear PAW +U calculator state, the
raw stored `dH_asp` spin difference is not an authoritative TB2J exchange
operator: it violates PAW rotational covariance even though GPAW's explicit
XC and Hubbard evaluators are covariant. Build the complete operator once
from those evaluators and the converged `D_asp`.

## Principles

- `setup.hubbard_u` is the capability and provenance source for a GPAW PAW +U
  setup. It stores the correlated angular momenta, internal-Hartree $U$ values,
  and scaling convention.
- `HubbardU.calculate(setup, D_sii)` returns the Hubbard potential
  `dHU_sii` in the PAW projector/partial-wave basis.
- `xc.calculate_paw_correction` returns the explicit XC PAW derivative matrix.
- For each supported correlated site, evaluate the Hubbard potential **once**
  using `unpack_density(D_asp)` and construct

$$
\Delta^a =
\Delta_{\mathrm{xc}}^a +
\left(dH_{\mathrm{U}}^{a,\uparrow} - dH_{\mathrm{U}}^{a,\downarrow}\right).
$$

- Do not add `dHU` to raw total `dH_asp`: that would double count when the
  raw payload is already valid. Instead, the explicit composition replaces raw
  `dH_asp` as the +U operator source for the affected GPAW 26.7 state.

## Validation

The symmetry-on FeO $7^3$ Gamma probe expands 20 IBZ points to 343 BZ points.
For a nontrivial PAW rotation, `delta_xc` has covariance residual
$7.0\times10^{-14}$ eV and direct `dHU` has residual
$3.9\times10^{-16}$ Ha. Raw
`dH_asp^\uparrow-dH_asp^\downarrow` has residual $56.51$ eV and produces a
17.1729 meV first-shell spread. The explicit composition produces 0.0009 meV
first-shell and 0.0 meV second-shell spread.

## Variables

| Symbol | Description | Units |
|---|---|---|
| $\Delta^a$ | Complete on-site PAW exchange splitting at site $a$ | eV |
| $\Delta_{\mathrm{xc}}^a$ | Explicit PAW XC spin difference | eV |
| $D_{sii}$ | GPAW spin-resolved PAW density matrix | dimensionless |
| $dH^U_{sii}$ | GPAW Hubbard potential derivative | Hartree internally |

## Conventions

- Detect supported +U via `setup.hubbard_u is not None` for every correlated
  setup.
- Preserve the existing no-+U `delta_xc` route unchanged.
- Reject noncollinear, densityless, or evaluator-less calculator state rather
  than silently omitting the Hubbard term.
- Record GPAW version, correlated site/shell, $U$, scaling, explicit
  composition, and one Hubbard evaluation per site in output metadata.

## Linked Concepts

- [[abinit-paw-wfk-vxc-exchange|ABINIT PAW WFK+Vxc exchange]]: analogous
  complete on-site PAW spin-splitting route.
- [[tb2j-paw-exchange-terms|PAW exchange terms]]: term-by-term XC and Hubbard
  provenance.
- [[paw-basis-choices-lkag|PAW basis choices]]: shared dual-projector Green
  convention.
