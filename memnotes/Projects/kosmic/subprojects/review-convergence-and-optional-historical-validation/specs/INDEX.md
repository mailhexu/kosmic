# Review convergence and optional historical validation Specs

- [PRD](prd.md) — approved.
- [Architecture](architecture.md) — approved design; no implementation is claimed.

## Approved Epics

- [Optional historical validation with strict active integrity](epics/epic-001.md) — approved 2026-10-22.
- [Complete worker responses and convergent review handoffs](epics/epic-002.md) — approved 2026-10-22.

## Draft Stories

| Story | Epic | Dependency | Status |
|---|---|---|---|
| [001: Configured historical inspection and canonical reporting](stories/story-001.md) | [001](epics/epic-001.md) | None | draft |
| [002: Read-only strict-audit override and compatibility cutover](stories/story-002.md) | [001](epics/epic-001.md) | Story 001 | draft |
| [003: Compatible finding-response and refutation annotations](stories/story-003.md) | [002](epics/epic-002.md) | None | draft |
| [004: Coordinator readiness and bounded re-review handoff](stories/story-004.md) | [002](epics/epic-002.md) | Story 003 | draft |

Individual Story approval is required before implementation. Stories 001 and 003 are logically independent; the parent integration owner reconciles shared files and publication against one baseline. No implementation or completion is claimed.
