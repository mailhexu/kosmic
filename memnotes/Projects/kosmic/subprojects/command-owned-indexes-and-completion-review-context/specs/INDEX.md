# Command-owned indexes and completion review context Specs

- [PRD](prd.md) — approved by the user; native owning-index publication and read-only CLI review fingerprints.
- [Architecture](architecture.md) — approved by the user.
- [Epic 001: Native indexed spec creation and recovery](epics/epic-001.md) — approved; PRD FR-001–004 and creation/index FR-008.
- [Epic 002: Read-only completion fingerprints](epics/epic-002.md) — approved; PRD FR-005–007 and fingerprint FR-008.

## Stories

| Story | Status | Dependency | Scope |
|-------|--------|------------|-------|
| [Story 001: Indexed spec creation and deterministic recovery](stories/story-001.md) | done | none | Native creation/recovery implemented; verification and independent review precede receipt-backed completion. |
| [Story 002: Finish index coordination and native workflow cutover](stories/story-002.md) | done | Story 001 | Shared index lock/current-content guard and native caller/reference cutover. |
| [Story 003: Explicit-writer completion preparation and caller cutover](stories/story-003.md) | done | none | Explicit writer and caller cutover implemented; verification and independent review precede receipt-backed completion. |

All three Stories are user-approved. Only successful native finish receipts establish completion.
