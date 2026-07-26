# 07 — Refresh projections and gate Consumer Interface changes

**What to build:** Integrate projection freshness with knowledge maintenance and implementation workflows so eligible note changes refresh the pair and Consumer Interface changes cannot complete with stale or missing Usage guidance.

**Blocked by:** 03 — Make Skill Pair publication transactional.

**Status:** done

- [x] Adding or updating Projection-Eligible Knowledge regenerates the canonical pair through the shared Projection CLI contract.
- [x] Review reports Unscoped Knowledge, provenance drift, missing sources, and broken Skill Pair relationships.
- [x] Stories that change a Consumer Interface cannot complete until corresponding Project Knowledge is validated and regeneration passes.
- [x] Quick tasks that change a Consumer Interface enforce the same completion gate.
- [x] Work that does not affect a Consumer Interface is not blocked by an irrelevant Usage refresh.
- [x] A behavioral scenario fails the completion gate before knowledge refresh and passes after validated knowledge and successful regeneration.
