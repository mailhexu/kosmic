---
artifact_role: knowledge
audience: both
confidence: 0.95
created: 2026-07-13
last_validated: 2026-07-13
validation_procedure: |
  Verified exact budget failures, deterministic Latin-hypercube starts, fixed remainder splits,
  top-K GP candidate polishing, controls, diagnostics, and optional dependency isolation with
  autonao/tests/test_optimizer_benchmark.py. Ran the full package suite with sibling src
  paths: 472 passed, 2 skipped. Verified sealed Stage 0 benchmark evidence retains controls,
  diagnostics, and selected-result summaries.
validation_test: autonao/tests/test_optimizer_benchmark.py
successful_usage_count: 1
last_used_successfully: 2026-07-13
usage_stale: false
related_files:
  - autonao/autonao/campaign/optimizer_benchmark.py
  - autonao/autonao/campaign/stage0_config.py
  - autonao/autonao/campaign/stage0_production.py
related_functions:
  - run_benchmark
  - bobyqa_strategy
  - gp_bobyqa_strategy
tags: [optimizer, benchmark, bobyqa, gaussian-process, budget-accounting]
project: siesta_simplex_basis
status: draft
validated_by: automatic
validation_date: 2026-07-13
links_to: [optimization_algorithm_comparison]
linked_from: [story-46-stage0-optimizer-benchmark]
type: Project Knowledge
math_provenance: missing
math_provenance_reason: "equal_budget_optimizer_composition.md display math requires one MathDoc marker per equation"
---

# Equal-Budget Optimizer Composition

An equal-budget benchmark must require exact objective consumption, not merely cap calls. Underuse and overuse both invalidate the comparison; histories must never be padded with duplicate evaluations.

For a total budget $B$ split across $N$ starts or polishes, compute:

$$
(q, r) = \operatorname{divmod}(B, N)
$$

The first $r$ runs receive $q+1$ evaluations and the remaining runs receive $q$. Per-run budget wrappers enforce each allocation before the outer benchmark wrapper verifies the total.

Multi-start BOBYQA uses the caller's explicit start count and seed. It retains the configured initial point and generates the remaining bounded points with deterministic NumPy Latin-hypercube strata, records starts and allocations, and selects the lowest backend result.

GP-to-BOBYQA keeps four independent controls: exploration budget, polish-candidate count, random-start count for Ax's Sobol initialization, and seed. After exact-budget exploration, the top $K$ observed candidates receive the remaining budget through the same quotient/remainder rule. Provider diagnostics are retained as available; no uncalibrated early-stop threshold is invented.

The canonical Stage 0 evidence writer persists these controls, diagnostics, selected-result summaries, checkpoint curves, and the unchanged per-evaluation rows into sealed `benchmark.json` evidence.

Finite candidate, objective, control, and diagnostic values are part of the persistence contract: non-finite values are rejected rather than sealed as non-standard `NaN` or `Infinity` JSON tokens.

Production repeats the complete equal-budget comparison independently for each configured compactness point. Aggregate ledger rows carry the point label while sealed evidence keeps per-point curves, controls, diagnostics, and selected results. If GP dependencies are unavailable, that status is recorded and the mandatory BOBYQA comparator still runs.

The Stage 0 comparator list must include BOBYQA. Py-BOBYQA is a core package dependency; Ax/BoTorch remain a lazy optional `optimizer_gp` extra and cannot prevent baseline execution.

Production benchmark reproducibility requires an explicit nonnegative seed; only smoke or injected benchmark configs may omit it. GP exploration and polish controls are required separately when `gp-bobyqa` is selected as either the primary optimizer or a comparator. Baseline-only BOBYQA Stage 0 configs omit both GP controls, an omitted comparator list defaults to BOBYQA only, and production validates GP controls only immediately before constructing the GP strategy.

Ax and BoTorch are imported only when the GP strategy is requested. The mandatory BOBYQA comparator can be loaded without either optional dependency.

## Linked Concepts

- [optimization_algorithm_comparison](optimization_algorithm_comparison.md)
- [Story 46](../specs/stories/story-46-stage0-optimizer-benchmark.md)
