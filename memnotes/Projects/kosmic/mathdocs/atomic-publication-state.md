---
type: Math Derivation
status: stable
derivation: atomic-publication-state.py
source_sha256: 7e00162783d0b3861226b1b8d8f3f1fcbff41b87d30dbc6cdb8c6ebd58b5f35d
python_version: 3.12.10
sympy_version: 1.14.0
verified_at: 2026-09-05T20:42:36Z
verified_host: phys-ptm40.fsc.uliege.priv
verified_directory: /home/hexu/projects/myagentskills/kosmic
---

# Atomic Publication State

## Purpose

Verify that Kosmic publication exposes exactly one canonical Skill Pair tree after either commit or rollback.

## Assumptions

- `s` is a binary publication outcome satisfying `s² = s`.
- `s = 1` exposes the staged valid tree after commit; `s = 0` restores the prior valid tree after failure.
- The old and new visibility indicators are respectively `1 - s` and `s`.

## Units

- `s`, `1 - s`, and the results are dimensionless counts of visible canonical trees.

<!-- KOSMIC-MATH-RESULTS:START -->
## Verified Results

<!-- MathDoc: kosmic/atomic-publication-state#commit_indicator -->
$$
s
$$
<!-- KOSMIC-SREPR: Symbol('s', integer=True) -->
<!-- MathDoc: kosmic/atomic-publication-state#mixed_visibility -->
$$
0
$$
<!-- KOSMIC-SREPR: Integer(0) -->
<!-- MathDoc: kosmic/atomic-publication-state#rollback_indicator -->
$$
1 - s
$$
<!-- KOSMIC-SREPR: Add(Integer(1), Mul(Integer(-1), Symbol('s', integer=True))) -->
<!-- MathDoc: kosmic/atomic-publication-state#visible_count -->
$$
1
$$
<!-- KOSMIC-SREPR: Integer(1) -->
<!-- KOSMIC-MATH-RESULTS:END -->

## Corrections

<!-- Append: YYYY-MM-DD - error - resolution. -->
- 2026-09-05 - Initial terminal substitutions reduced both outputs to constants - Replaced them with a binary polynomial model that also proves mutual exclusion.
