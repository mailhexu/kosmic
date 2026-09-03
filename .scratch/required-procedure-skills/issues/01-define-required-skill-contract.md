# 01 — Define required-skill dependency contract

**What to build:** Provide one deterministic, adapter-aware dependency check that accepts only a complete curated Matt Pocock skill set, reports every missing required skill with an actionable installation remedy, and rejects unsupported adapters without beginning a contributor workflow.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] The curated set includes `tdd`, `code-review`, `diagnosing-bugs`, `research`, `domain-modeling`, `codebase-design`, `grill-with-docs`, `grilling`, and `prototype`.
- [x] Each supported adapter has an explicit skill-location contract.
- [x] Complete, incomplete, and unsupported-adapter outcomes are behaviorally verified in isolated homes.
