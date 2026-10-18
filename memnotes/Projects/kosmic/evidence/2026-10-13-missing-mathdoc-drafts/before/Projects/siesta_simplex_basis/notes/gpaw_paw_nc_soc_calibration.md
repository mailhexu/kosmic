---
artifact_role: knowledge
audience: both
title: GPAW PAW to NC-FR SOC Calibration
id: gpaw_paw_nc_soc_calibration
date: 2026-08-03
project: siesta_simplex_basis
status: stable
validated_by: primary-source research
related_specs:
  - ../specs/research/2026-08-03-gpaw-paw-siesta-nc-soc-calibration.md
related_notes:
  - gpaw_paw_soc_comparison_dataset
  - soc_strength_descriptor
type: Project Knowledge
---

# GPAW PAW to NC-FR SOC Calibration

GPAW PAW `xi_eV` and PseudoDojo NC-FR `delta_eps_eV` have no universal physical conversion. The former is a density/setup/configuration-dependent on-site all-electron PAW first-order coefficient; the latter is the bound-state splitting from bare NC-FR $j$-channel pseudopotentials.

For one diagonal isolated $l$ PAW block, convert GPAW's internal convention to its own first-order multiplet split with

$$
\Delta\varepsilon^{\mathrm{PAW,1st}}_{nl}=(2l+1)\,\xi_{nl}^{\mathrm{PAW}}.
$$

A useful approximate relationship is only an empirical, same-family calibration: use at least five matched non-semicore atomic channels with the same $l$, valence partition, XC functional, atomic charge/spin/configuration, and pseudopotential/setup releases. Report every signed pair and the median ratio $\Delta\varepsilon^\mathrm{NC}/\Delta\varepsilon^\mathrm{PAW,1st}$, 16th--84th-percentile range, and leave-one-out error. Do not pool $p$, $d$, and $f$ or extrapolate outside the calibrated family.

Before using the ratio as a materials proxy, validate one fixed-geometry GPAW-vs-SIESTA SOC band splitting at a pre-registered band/$k$ point and compare SOC-on/SOC-off band-edge shifts. Failure vetoes the conversion for that environment. Keep NC-FR `delta_eps_eV` as the primary descriptor.

See [2026-08-03-gpaw-paw-siesta-nc-soc-calibration](2026-08-03-gpaw-paw-siesta-nc-soc-calibration.md) for source citations and the full protocol.
