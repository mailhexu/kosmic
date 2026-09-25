---
type: Domain Topic
id: abinit/development/pymultibinit-ifc-projection-ceiling
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Diagnose IFC-fit residual floors with a full-basis lsqr projection probe to separate basis expressivity, data selection, and ncoeff limits.
triggers: [IFC residual floor, lsqr projection ceiling, ncoeff sweep decision, pymultibinit fit capacity]
aliases: [IFC projection ceiling]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: 56064fc5a68c9c32fdb4b2a2720718ba54c97f510ab30d47690abe909a3d709d
---

# pymultibinit IFC Projection-Ceiling Probe

Use this probe when an IFC (interatomic-force-constant) fit leaves target or held-out IFC residuals high and the cause (coefficient count, basis expressivity, data selection) is unclear. The probe decides whether an ncoeff sweep can help at all.

## Procedure

1. Build the channel data for the targets of interest, both fit targets and any held-out reference:
```python
from pymultibinit.training import (PythonFitConfig, _reference_frame_from_ddb,
    build_ifc_fit_data, read_basis_netcdf)
from pymultibinit.pyeffpot.ifc_targets import IfcTargetSpec, load_ifc_target

basis = read_basis_netcdf(basis_nc)
reference = _reference_frame_from_ddb(ddb, ncell)   # ncell must match the training supercell
specs = [IfcTargetSpec(id=..., mode="import", fc_file=..., sidecar_file=...) for d in dirs]
ifc = build_ifc_fit_data(basis, reference, ddb, PythonFitConfig(ncell=ncell),
                         [load_ifc_target(s) for s in specs])
```
   The build takes about 2 min for a 20,507-term basis at 2×2×2 (designs about 2.4 GB per target in RAM).
2. Compute the full-basis lsqr floor per target and for the stacked joint problem. `ifc.designs[k]` is (ncoeff, entries) with operator `matvec = v -> D.T@v` and `rmatvec = y -> D@y`; `ifc.references[k]` and `ifc.fixed[k]` are 2-D (3N,3N), so reshape the right-hand side with `.reshape(-1)`. Solve with `scipy.sparse.linalg.lsqr(A_op, r, atol=1e-12, btol=1e-12, iter_lim=3000)`; report `resid/sqrt(nrow)` and `||c||`. Cost: 25 s to 15 min per solve at 2×2×2 scale; instant for 5 atoms.
3. Interpret:
   - Greedy-n within 5% of its floor: ncoeff does not bind for that objective; do not sweep.
   - Joint multi-target floor far above single-target floors (or 0): the families are jointly unrepresentable in the span (expressivity limit).
   - Held-out floor low (0.04) with tiny ||c|| while trained models sit 6x above: the failure is data selection from the near-null-space, not capacity.
   - Floor with absurd ||c|| (1e27): rank-deficient evaluation point (a cubic reference, u = 0); ignore.

## Reference numbers (ex-10 BaTiO3, ex08 base, ncoeff=40)

T222 fixed 0.685 → floor 0.0696 (greedy 0.0705, 101.3%); O222 0.0873; T+O joint 0.0789 pooled; held-out R 5-atom floor 0.0441 (||c|| = 0.012) versus baseline arm 0.268.
