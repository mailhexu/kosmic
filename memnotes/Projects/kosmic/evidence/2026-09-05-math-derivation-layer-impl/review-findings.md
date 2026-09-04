# Math Derivation Layer review findings

## Review method

Independent parallel Task 7 review against two axes:

- Standards: repository conventions, maintainability, safety, deterministic execution, atomicity, and failure behavior.
- Spec: approved PRD FR-001..FR-008, NFR-001..NFR-007, Architecture AD-M1..AD-M8, and Stories 010-017.

## First-pass findings and resolutions

| ID | Axis | Severity | Finding | Resolution |
|----|------|----------|---------|------------|
| M-01 | Spec | Major | `notation.md` lacked FR-008 MathDocs vocabulary. | Added `{slug}`, MathDoc result/exposition identifiers, Math Derivation, Verified result, and derivation-first debugging. |
| M-02 | Spec | Major | Initial dogfood used terminal substitutions producing only constants. | Replaced with genuine binary polynomial reduction, four named symbolic/invariant results, exposition, and a Corrections entry. |
| M-03 | Spec | Moderate | `check-math` stopped at the first error rather than reporting each file. | Added failure collection, per-file PASS/FAIL output, and aggregate summary while preserving no-update-on-failure. |
| M-04 | Standards | Major | A staged dependent-note gate inverted the approved FR-007 correction order. | Restored old-registry prevalidation; paired results publish first, then dependent notes are corrected. Added a regression test. |
| M-05 | Standards | Minor | Migration validated notes without the loaded math registry. | Migration now validates the temporary notes tree against `load_math_registry(project)` before publication. |
| M-06 | Spec | Minor | Two notation rows had four cells under a three-column header. | Corrected table shape. |

## Re-review verdict

Both independent reviewers re-inspected their findings and returned PASS with no remaining blockers. The Standards reviewer confirmed FR-007 ordering, pre-publication migration validation, and all-or-none reporting behavior. The Spec reviewer confirmed FR-008 coverage, genuine symbolic dogfood, and per-file reporting.
