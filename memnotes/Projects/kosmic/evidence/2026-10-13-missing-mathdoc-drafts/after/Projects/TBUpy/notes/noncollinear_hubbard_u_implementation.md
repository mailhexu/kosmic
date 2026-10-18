---
artifact_role: knowledge
audience: both
confidence: 0.85
created: 2026-05-06
last_validated: 2026-05-06T00:00:00
validation_procedure: |
  Implemented stories 016-021 and ran full TBUpy tests plus TB2J interface tests:
  source /home/hexu/projects/myenvs/mydev/bin/activate && PYTHONPATH=/home/hexu/projects/TB2J_dev/Refs/Refs pytest -q
  source /home/hexu/projects/myenvs/mydev/bin/activate && PYTHONPATH=/home/hexu/projects/TB2J_dev/TBUpy:/home/hexu/projects/TB2J_dev/HamiltonIO pytest -q TB2J/TB2J/tests/test_tbupy_interface.py TB2J/TB2J/tests/test_tbupy_cli.py
successful_usage_count: 1
last_used_successfully: 2026-05-06T00:00:00
usage_stale: false
related_files:
  - TBUpy/tbupy/density.py
  - TBUpy/tbupy/occupations.py
  - TBUpy/tbupy/hubbard.py
  - TBUpy/tbupy/model.py
  - TBUpy/tbupy/analysis.py
  - TBUpy/tbupy/io.py
  - TB2J/TB2J/tests/test_tbupy_interface.py
tags:
  - hubbard-u
  - non-collinear
  - spinor
  - implementation
project: TBUpy
status: draft
validated_by: automatic
validation_date: 2026-05-06T00:00:00
links_to:
  - noncollinear_hubbard_u_design
linked_from: []
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "noncollinear_hubbard_u_implementation.md display math requires one MathDoc marker per equation"
---

# Non-Collinear Hubbard U Implementation

## Overview

TBUpy now has an explicit `spin_mode="spinor"` path for non-collinear +U calculations. The collinear path remains the default and preserves the existing `rho[nspin, norb, norb]` data model.

## Implemented Behavior

Spinor mode stores density as a full Hermitian matrix `rho[nbasis, nbasis]` in spin-interleaved order. `SCFResult` is union-like: `spin_mode="collinear"` keeps the existing shapes, while `spin_mode="spinor"` uses `evals[nkpt, nbasis]`, `evecs[nkpt, nbasis, nbasis]`, and `rho[nbasis, nbasis]`.

The spinor SCF loop diagonalizes the full generalized eigenproblem `H_eff(k) C = S(k) C epsilon`. It uses a spinor occupation adapter with one electron per spinor state and no extra spin degeneracy factor.

## Hubbard Terms

Spinor Dudarev uses the rotationally invariant compact form on each correlated site:

$$
E = \frac{U_{eff}}{2}\mathrm{Tr}(\rho - \rho^2), \quad V = U_{eff}(\frac{1}{2}I - \rho)
$$

The returned Hubbard energy follows the existing TBUpy convention for SCF total energy by subtracting `Tr(V rho)` from the functional contribution because band energies are computed from `H0 + V`.

Spinor Kanamori and Liechtenstein use full local spinor four-index contractions. The Hartree charge density is the spin trace `sum_s rho[m,s,n,s]`, so spin coherence does not enter the charge channel. Exchange keeps spin indices and can generate spin-flip potentials.

## I/O and TB2J

Spinor `.tbupy.nc` files record `spin_mode="spinor"` and preserve full spinor `rho`, `V_U`, and effective Hamiltonian arrays. Legacy collinear files without `spin_mode` load as collinear. Collinear split helpers reject spinor files to avoid dropping spin-flip blocks. The TB2J handoff contract is documented in [tb2j-spinor-handoff-contract](../specs/tb2j-spinor-handoff-contract.md).

## Validation

- TBUpy full suite: `205 passed`.
- TB2J TBUpy interface/CLI tests: `6 passed`.
- Mandatory code review found no remaining high/medium findings after fixes.

## Linked Concepts

- [noncollinear_hubbard_u_design](noncollinear_hubbard_u_design.md): Design rationale and formulas.
