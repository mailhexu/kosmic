---
type: Domain Topic
id: methods/development/cross-implementation-contract-comparison
domain: methods
audience: development
artifact_role: guideline
status: draft
summary: Numerically compare two independent implementations of one physics contract and classify every difference by class and owner.
triggers: [cross-implementation comparison, implementation parity, verdict table, python fortran parity]
source_project: native
source_sha256: empty
aliases: [contract comparison, parity audit]
---

# Cross-Implementation Contract Comparison

Compare a prototype (Python) against a port (Fortran semantics) of the same physics. The goal
is a verdict table that classifies every difference. Do not stop at the first mismatch.

## Procedure

1. Build the aspect table. List every convention axis: normalization, phase side and sign, 2 pi
   bookkeeping, harmonic ordering and signs, conjugation placement, units, on-disk layout. Fill
   one verdict per axis per implementation.
2. Find the noise floor first. Each quantity has a floor from mesh or spline differences (measured
   2e-7 to 3e-7 for different spline meshes in the abinao/ABINIT case). Residuals at the floor
   are matches. Report them as matches, not as diffs.
3. Apply the self-consistency gate. Before calling two stored artifacts inconsistent, recompute
   each artifact from its own stored inputs. Example: rebuild H from stored C and eigenvalues.
   Gauge-inconsistent fixtures produce phantom 1e-4 mismatches. Recomputation reduced one case
   to 3e-9.
4. Check range claims. Compare the accepted range against the implemented range. Example: istwfk
   accepts 1-9, and only 1-2 is implemented. A silent wrong path is a real finding without any
   failing fixture.
5. Compare metadata semantics, not names. The same field name can carry a record index in one
   implementation and a per-l counter in the other.

## Verdict format

Split findings into five classes:

- REAL: a physics defect.
- METADATA: a semantics difference in bookkeeping fields.
- COVERAGE: one implementation accepts or produces a different range.
- GAUGE: a fixture-internal convention difference, not a defect.
- BENIGN: equivalent by construction.

Each finding states the decisive number, the owner side (which implementation is wrong), and
one downstream action: port item, fix item, or none.
