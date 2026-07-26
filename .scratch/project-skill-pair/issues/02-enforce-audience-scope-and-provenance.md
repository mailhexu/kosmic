# 02 — Enforce Audience Scope and Projection Provenance

**What to build:** Extend projection so only Projection-Eligible Knowledge reaches the correct audience, while every projected topic remains traceable to its authoritative validated note.

**Blocked by:** 01 — Generate a minimal atomic Skill Pair.

**Status:** done

- [x] Usage contains `usage` and `both` knowledge and excludes `development` and Unscoped Knowledge.
- [x] Development contains `development` knowledge directly and reaches shared guidance through Usage rather than duplicating it.
- [x] Draft, stale, non-note, and otherwise ineligible material is excluded from both projections.
- [x] Every projected topic records source-note identity and a deterministic content hash.
- [x] Changing an authoritative note causes CLI drift validation to fail and identify the affected source.
- [x] Black-box fixture tests cover every Audience Scope and eligibility state through the CLI seam.
