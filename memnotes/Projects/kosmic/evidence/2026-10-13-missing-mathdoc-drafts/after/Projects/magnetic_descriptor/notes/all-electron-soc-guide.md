---
artifact_role: knowledge
type: Project Knowledge
status: draft
audience: both
usage_stale: false
created: 2026-08-24
last_validated: 2026-08-24
math_provenance: missing
math_provenance_reason: "all-electron-soc-guide.md display math requires one MathDoc marker per equation"
---

# All-electron SOC guide

## Purpose

The project now has a non-specialist entry point at
`~/projects/mypapers/magnetic_descriptor/docs/soc_and_mae_guide.md`.
It explains the all-electron atomic SOC periodic table and the physics-led MAE descriptor work without presenting a scalar model as a replacement for a solid-state calculation.

## Atomic reference

- `ae_soc_strengths.json` stores the self-consistent neutral-atom all-electron Dirac shell energy span

  $$
  s_{nl}=\left|\varepsilon_{nl}^{j=l+1/2}-\varepsilon_{nl}^{j=l-1/2}\right|.
  $$

- It contains 85 usable elements and 88 valence $p/d/f$ channels. This is the element-side SOC scale, not a crystal MAE, pseudopotential projector coefficient, or band-structure calculation.
- `s` shells are gray/zero because $l=0$ has no orbital-angular-momentum SOC partner.
- Neutral-atom all-electron values are independently checked against suitable NIST one-electron cases; the median AE/NIST ratio is 1.17.

## Descriptor interpretation

The retained v3.3 model separates an atomic SOC factor from the structure factors that let a material use it:

- metal sites: second-order SOC scale $s_d^2$ times the electron-hole symmetric carrier count $\min(n_d,10-n_d)$;
- ligand sites: SOC-weighted spin-transfer covalency times a non-cancelling directional quadrupole;
- all formally open shells, not only transition-metal d shells, are considered after molecular-ion-aware charge allocation;
- intrasite and intersite DFT channels are predicted as magnitudes separately because their signs can cancel.

The leading correction was the user-supplied second-order SOC scaling. It replaced linear $s_d$ and eliminated unphysical ionicity gates. The other supplied central hypothesis—covalency activates SOC where spin density is deposited—was supported for the ligand channel. A full additive metal–ligand mixing square $s_{\mathrm{eff}}^2=(s_d+w s_p)^2$ did not generalize; the remaining itinerant/strong-SOC/sign effects require Fermi-level-resolved information.

## Scope boundary

The 337 valid SOC-bearing labels give a v3.3 pooled leave-element-out composite rank correlation of about $+0.470$. This is a mechanism and ranking result, not exact numerical MAE or sign prediction. It cannot resolve channel-sign cancellation, detailed orbital degeneracy, or itinerant Fermi-surface mechanisms.

## Regeneration status

`~/projects/mypapers/magnetic_descriptor/scripts/README.md`
provides the retained NIST and covalency-analysis pipeline. The original all-electron ONCVPSP batch driver and its periodic-table plotter are not retained in the paper repository; `ae_soc_strengths.json` and `soc_periodic_table_ae.png` are an explicitly frozen, verified release. Do not substitute a heuristic reconstruction for the AE artifact.
