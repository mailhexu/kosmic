---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-07-15
last_validated: 2026-07-15T00:00:00
validation_procedure: |
  Cross-checked the companion manuscript workflow description against
  autonao campaign/stage0 sources, pypao and abinao public docs,
  existing workflow notes, and a successful two-pass pdflatex build.
validation_test: "/home/hexu/projects/mypapers/optimize_siesta_basis/main.tex"
successful_usage_count: 1
last_used_successfully: 2026-07-15T00:00:00
usage_stale: false
related_files:
  - "/home/hexu/projects/mypapers/optimize_siesta_basis/main.tex"
  - "/home/hexu/projects/autosiestabasis_dev/autonao/autonao/campaign/campaign.py"
  - "/home/hexu/projects/autosiestabasis_dev/autonao/autonao/campaign/stage0_production.py"
  - "/home/hexu/projects/autosiestabasis_dev/pypao/src/pypao/session.py"
  - "/home/hexu/projects/autosiestabasis_dev/abinao/src/abinao/validate.py"
tags: [manuscript, workflow, spillage, energy, multi-structure]
project: siesta_simplex_basis
status: draft
validated_by: automatic
validation_date: 2026-07-15T00:00:00
links_to: [multi_structure_objective, three_bridge_validation_blocker, optimization_algorithm_comparison]
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "manuscript_workflow_scope.md display math requires one MathDoc marker per equation"
---

# Manuscript Workflow Scope

The companion paper must describe two distinct paths, not interchangeable objectives inside one ordinary campaign.

## Standard Energy Campaign

`autonao` evaluates a shared trial basis with SIESTA. For multiple structures, it minimizes the atom-normalized weighted energy

$$
F_\mathrm{multi} = \frac{\sum_s w_s(E_s/N_s)}{\sum_s w_s} + P V_\mathrm{basis}.
$$

The pressure term is added once after aggregation. The automatic path seeds DZP from SIESTA's default basis with `PAO.EnergyShift 0.001 Ry`, then warm-starts TZP and TZDP from compatible prior results; failed levels stop escalation. Delta-factor E--V sweeps are independent validation, not a generic multi-volume campaign objective.

## Stage 0 Spillage Workflow

Stage 0 is independently invoked. `pypao` converts PSML pseudopotentials into candidate radial PAOs, while `abinao` projects those candidates against precomputed ABINIT WFK manifests and evaluates spillage. A multi-WFK manifest can represent structures or volumes, but this does not make the standard energy campaign a multi-volume optimizer. `pypao` is neither an optimizer nor a system-level DFT driver; `abinao` consumes WFKs and does not run ABINIT.

## Reporting Boundary

Report Fortran simplex, Python Nelder--Mead, and BOBYQA as operational backends. GP-BOBYQA remains experimental. Scope the Si$_2$ 74.4\% spillage reduction to its equal-budget comparison; it does not prove universal superiority of per-zeta confinement.

## Linked Concepts

- [multi_structure_objective](multi_structure_objective.md)
- [three_bridge_validation_blocker](three_bridge_validation_blocker.md)
- [optimization_algorithm_comparison](optimization_algorithm_comparison.md)
