# 03 — Make Skill Pair publication transactional

**What to build:** Make regeneration deterministic and failure-safe so a complete validated Skill Pair replaces the prior pair as one unit, while incomplete or invalid output is never exposed.

**Blocked by:** 02 — Enforce Audience Scope and Projection Provenance.

**Status:** done

- [x] Identical Project Knowledge produces byte-for-byte equivalent canonical packages across repeated runs.
- [x] Generation validates both skills and their relationship before either becomes canonical.
- [x] An injected failure while producing the second skill leaves the previous valid pair unchanged.
- [x] Publication is blocked when no genuine validated Consumer knowledge can produce a useful Usage Skill.
- [x] Temporary generation artifacts are removed after success and failure.
- [x] CLI exit statuses and diagnostics distinguish invalid knowledge, empty Usage, broken references, drift, and publication failure.
