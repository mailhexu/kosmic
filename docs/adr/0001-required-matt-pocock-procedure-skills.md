---
status: accepted
---

# Require selected Matt Pocock procedure skills

Kosmic requires the independently installed Matt Pocock skills `tdd`, `code-review`, `diagnosing-bugs`, `research`, `domain-modeling`, `codebase-design`, `grill-with-docs`, and `prototype`. Kosmic remains the sole orchestrator for Project Knowledge, approval/status gates, specifications, logs, Project Skill Pair generation, and Projection CLI validation; these upstream skills are bounded methods invoked within Kosmic procedures. We rejected a wholesale upstream workflow import because its router, tracker, publishing, and implementation conventions would compete with Kosmic's vault-based lifecycle. We also rejected optional fallbacks because a required shared procedure is more predictable than agents silently using divergent native substitutes.

## Consequences

Kosmic installation must verify this dependency set and fail with actionable setup instructions when any required skill is unavailable. `tdd` must be available together with its shared `codebase-design` and `domain-modeling` vocabulary; `grill-with-docs` must retain access to its `grilling` subroutine. The integration references upstream skills instead of copying them, so the upstream MIT license is not redistributed by Kosmic; dependency changes require explicit compatibility review.

Kosmic deliberately adapts `prototype`'s artifact lifecycle: prototype code runs under the disposable `.tmp/` area and is deleted after its verdict, question, and supporting evidence are captured in the relevant Kosmic research memo, Quick Task, or Story Technical Notes. Kosmic does not require an implementation issue or a committed throwaway branch.
