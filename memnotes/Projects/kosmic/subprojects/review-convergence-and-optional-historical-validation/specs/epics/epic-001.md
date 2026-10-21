---
project_id: "kosmic"
subproject_id: "review-convergence-and-optional-historical-validation"
record_kind: "epic"
local_id: "001"
status: "draft"
created: 2026-10-21
updated: 2026-10-21
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
linked_stories: []
---

# Epic 1: Optional historical validation with strict active integrity

## Description

Give Project maintainers a useful, read-only view of explicitly selected legacy-record integrity without treating historical claims as current proof or weakening active operations. Default warning mode is independently useful: ordinary validation and canonical STATUS expose selected history as unverified rather than blocking on retrospective gaps. Configured strict mode and the explicit audit provide a way to fail on actual historical mismatches. All current authority, execution, publication, and integrity gates remain strict.

## Scope

### In Scope

- An optional `ProjectEntry.history_integrity` policy with `mode: warn|strict` and exact canonical Project-relative record paths. Absent configuration or an empty list preserves current behavior. Invalid or missing configured subject paths, duplicates, noncanonical/uncontained paths, and wrong-owner references are configuration errors; retrospective proof/hash drift follows the selected mode.
- Selected old `done`, `approved`, and `draft` records are in scope. In warning mode, missing or stale retrospective proofs, receipts, or pins are visible as `unverified — not audited`; claimed lifecycle remains distinct from computed integrity, and no warning claims verified completion.
- Discover record identity, owner, and claimed lifecycle before receipt/catalog settlement. Resolve selected scope before any retrospective hash or proof reader: warning mode skips those audits rather than running them and downgrading failures. Unselected/current records retain normal checks.
- Keep structural reporting data and its report type separate from operational `SpecCatalog`/`SkillProposal` authority. Operational catalog construction, bounded authority, direct proposal loading (including rejected-proposal equivalence), dependencies, and resumed work remain strict.
- Keep `render_status`, `_spec_rows`, `status_drift`, and `_write_status_reports` on one configuration-derived canonical view. The one proposed override, `validate --history-audit`, is read-only, forces strict audit only for configured records, and refuses an empty scope clearly. It never renders an alternate canonical STATUS or writes history.
- Update the affected current consumer guidance and projection/knowledge surfaces within the authorized Story scope; verify behavior through actual consumer commands and canonical STATUS behavior, not only private helper seams.

### Out of Scope

- Writes, backfills, auto-repins, receipt invention, lifecycle rewrites, migration, or inferred verification performed by historical inspection/audit. Separately authorized resumed work retains its current mutation and completion rules.
- A global hash/receipt skip, permissive operational loader/catalog, new persistent status, sidecar, cache, journal, or other artifact class.
- Changing active identity, ancestry, containment, scope, freshness, pins, execution/publication checks, or recorded-facts semantics; introducing retroactive blanket receipt requirements for old dependencies.
- New history selectors or flags beyond `validate --history-audit`, alternate STATUS modes, changes to the separate review-convergence Epic, or implementation during this Epic-planning task.

## Stories

| Story outline (title only; unreserved) | Dependency |
|---|---|
| Configured historical inspection and canonical reporting | None |
| Read-only strict-audit override and compatibility cutover | Configured historical inspection and canonical reporting |

The Story titles are planning outlines only: no Story IDs or files are reserved, and `linked_stories` remains empty until after Epic approval.

## Requirement and Decision Coverage

- PRD [FR-006–008](../prd.md#functional-requirements): explicit inactive-history scope and warn/strict behavior; read-only, truthful compatibility; strictness for active and executed/published artifacts.
- PRD [FR-009 and NFR-001–004](../prd.md#non-functional-requirements): reuse existing record/config/report surfaces; preserve safety and bytes; make scope/results inspectable without new persistent artifacts or permanent prose tests.
- Architecture [ADR-001](../architecture.md#adr-001-exact-configured-history-scope), [ADR-002](../architecture.md#adr-002-structural-reporting-before-retrospective-readers), and [ADR-003](../architecture.md#adr-003-coordinator-barrier-and-additive-finding-response): adopt the accepted history-scope, reporting-separation, and strict-active boundaries; the review-coordinator design is not implemented by this Epic.
- Existing consumer guidance: [Projection CLI experience commands](../../../../notes/cli-projection-commands.md) and [Projection CLI extension conventions](../../../../notes/cli-extension-conventions.md).

## Success Criteria

- With no policy or an empty configured record list, existing validation and canonical STATUS behavior are unchanged. Configured records use exact inspectable Project-relative scope; invalid scope is rejected rather than broadened.
- In warning mode, actual `validate` and canonical STATUS consumers expose selected historical gaps with the claimed lifecycle and explicit unverified/not-audited diagnostics, without blocking solely on those retrospective gaps or implying completion proof. Selection occurs before retrospective reads; unselected/current records still receive their existing checks.
- Configured strict mode and `validate --history-audit` fail on actual missing/mismatched historical integrity; an audit with no configured scope is refused. Read-only inspection/audit preserves historical record, receipt, pin, and STATUS bytes. Existing authorized generators/publication paths may write canonical STATUS using the configured view, never the audit override.
- Actual active consumers still refuse stale/tampered in-scope artifacts and preserve strict authority and publication/execution checks under either history mode. A history warning or audit result never grants authority or relaxes resumed-work requirements.
- Consumer verification covers representative old-done/no-receipt, old-approved/draft-without-modern-proof, and stale-pin cases through the real CLI/report paths, including the visible canonical STATUS view and unchanged unselected/current behavior. Reuse runtime guards and real consumer traces; do not add permanent prose tests or seam-only call-count tests.

## Integration and Verification Plan

Implementation and verification require approved Stories. Each Story owns its declared source and consumer-facing documentation/knowledge/projection outputs, captures the destination baseline, and reconciles drift. The parent is the single integration owner; reconcile shared `kosmic_completion.py`, `work_completion.md`, CLI knowledge, generated-publication paths and navigation against one baseline, with one writer per shared path and no blind whole-file edits. After slices stabilize, run integrated verification once across actual consumers and active strictness boundaries.

## Progress

- Stories: 0/2 done; Story files have not been created and await Epic approval.
