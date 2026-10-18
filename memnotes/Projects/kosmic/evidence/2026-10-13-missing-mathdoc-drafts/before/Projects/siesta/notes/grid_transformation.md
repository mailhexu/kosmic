---
artifact_role: knowledge
audience: both
confidence: 0.9
created: 2026-02-27
last_validated: 2026-02-27T12:00:00
validation_procedure: |
  Run tests/temporal/test_grid_transform/test_grid_transform.x
  Verify round-trip error < 1e-8 for all orbitals
validation_test: "tests/temporal/test_grid_transform/"
successful_usage_count: 5
last_used_successfully: 2026-02-27T12:00:00
usage_stale: false
related_files: ["siesta/Src/read_orb.F90", "siesta/Src/interpolation.f90"]
related_functions: ["transform_linear_to_log_grid", "generate_spline", "evaluate_spline"]
tags: ["grid", "interpolation", "spline", "transformation"]
project: siesta
status: stable
validated_by: automatic
validation_date: 2026-02-27T12:00:00
links_to: ["orb_file_format", "Vna_external_basis"]
linked_from: []
type: Project Knowledge
---

# Grid Transformation


## Overview

Grid transformation converts radial functions from ABACUS uniform linear grid to SIESTA's logarithmic grid using cubic spline interpolation. This is necessary because ABACUS and SIESTA use different grid representations.

## Grid Types

### ABACUS Linear Grid

$$
r_{\text{linear}}(i) = (i-1) \cdot \Delta r
$$

Uniform spacing, simple to generate.

### SIESTA Logarithmic Grid

$$
r_{\text{log}}(i) = a \cdot (\exp(b \cdot (i-1)/(N-1)) - 1)
$$

Parameters:
- $a$: Controls fineness near origin (smaller = finer)
- $b$: Controls grid expansion rate (larger = faster expansion)
- $N$: Number of grid points

## Transformation Process

1. **Generate Spline**: Create cubic spline $S(r)$ from linear grid data
2. **Evaluate Spline**: Evaluate spline at logarithmic grid points
3. **Handle Boundaries**: Extrapolate for points outside spline domain

## Accuracy Requirement

Round-trip interpolation error $\epsilon_{\text{round-trip}}$ must be < 1e-8 (NFR1 requirement from PRD).

Test results show machine-precision accuracy (effectively 0 error).

## Implementation

```fortran
subroutine transform_linear_to_log_grid(r_linear, chi_linear, mesh_size, &
                                        a, b, npoints_log, r_log, chi_log, ierr)
```

Located in `siesta/Src/read_orb.F90`.

Uses SIESTA's `interpolation` module:
- `spline_t`: Spline data structure
- `generate_spline()`: Creates spline representation
- `evaluate_spline()`: Evaluates spline at points

## Variables

The following variables are used in this note (see [notation](notation.md) for full definitions):

| Symbol | Description | Units |
|--------|-------------|-------|
| $r_{\text{linear}}$ | Linear grid points | Bohr |
| $\chi_{\text{linear}}$ | Radial function on linear grid | Bohr⁻³/² |
| $a$ | Log grid fineness parameter | Bohr |
| $b$ | Log grid expansion parameter | Bohr |
| $r_{\text{log}}$ | Logarithmic grid points | Bohr |
| $\chi_{\text{log}}$ | Radial function on log grid | Bohr⁻³/² |
| $S(r)$ | Spline representation of function | - |
| $\epsilon_{\text{round-trip}}$ | Round-trip interpolation error | - |

## Linked Concepts
- [orb_file_format](orb_file_format.md): Source of linear grid data
- [Vna_external_basis](Vna_external_basis.md): Using transformed basis for Vna computation
- [notation](notation.md): Standard variable notations used in this note
