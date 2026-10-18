---
audience: both
artifact_role: knowledge
type: reference
confidence: 0.8
created: 2026-05-23
last_validated: 2026-05-23T00:00:00
validation_procedure: "Validated by running the lightweight test harness and python -m compileall in /home/hexu/projects/Fe2O3/magsym."
validation_test: "/home/hexu/projects/Fe2O3/magsym/tests"
successful_usage_count: 1
last_used_successfully: 2026-05-23T00:00:00
usage_stale: false
related_files:
  - "/home/hexu/projects/Fe2O3/magsym/magsym/core.py"
  - "/home/hexu/projects/Fe2O3/magsym/magsym/fixtures.py"
related_functions:
  - "identify_magnetic_symmetry"
  - "alpha_fe2o3_fixture"
tags: [api, implementation, magnetic-symmetry, python]
project: magsym
status: draft
validated_by: automatic
validation_date: 2026-05-23T00:00:00
links_to: ["project_goal", "notation"]
linked_from: ["TOC"]
math_provenance: missing
math_provenance_reason: "core_api.md display math requires one MathDoc marker per equation"
---

# Core API

## Overview

The `magsym` core API implements operation-level magnetic symmetry identification for explicit Python objects. It provides data models for lattices, sites, spin configurations, magnetic structures, symmetry operations, tolerances, and results.

## Principles

- The first implementation uses Python-object inputs rather than file parsers.
- Symmetry operations are candidate operations supplied by the caller or a fixture.
- Results identify accepted and rejected operations, not full magnetic group names.
- Spin transformations use an axial-vector convention, so improper operations multiply transformed spins by the determinant of the spatial rotation.

## Details

The public package exports `Lattice`, `Site`, `CrystalStructure`, `SpinConfiguration`, `MagneticStructure`, `SymmetryOperation`, `ToleranceConfig`, `MagneticSymmetryResult`, `RejectedOperation`, `identify_magnetic_symmetry`, and `alpha_fe2o3_fixture`.

The `identify_magnetic_symmetry` function checks each candidate operation by transforming source site positions, matching transformed sites under periodic boundary conditions, transforming source spins, and comparing transformed spins with target spins using explicit tolerances.

## Variables

The following variables are used in this note (see [[notation]] for full definitions):

| Symbol | Description | Units |
|--------|-------------|-------|
| `Fe2O3` | Initial validation target represented by the alpha-Fe2O3 fixture. | dimensionless |

## Equations

For an axial spin vector `s` and spatial rotation matrix `R`, the spin transformation uses:

$$
s' = \det(R) R s
$$

If time reversal is present, the transformed spin is multiplied by `-1`.

## Workflow

```mermaid
flowchart TD
    A[MagneticStructure] --> C[identify_magnetic_symmetry]
    B[Candidate SymmetryOperation list] --> C
    D[ToleranceConfig] --> C
    C --> E[MagneticSymmetryResult]
```

## Conventions

- Fractional coordinates are wrapped into `[0, 1)`.
- Lattice vectors are stored row-wise in `Lattice.matrix`.
- Site matching uses labels and position tolerance.
- Missing spins are allowed only when both source and target sites are non-magnetic.

## Linked Concepts
- [[project_goal]]: Package goal and spec workflow.
- [[notation]]: Standard notation used in project notes.
