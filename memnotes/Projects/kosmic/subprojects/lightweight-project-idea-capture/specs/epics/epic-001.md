---
project_id: "kosmic"
subproject_id: "lightweight-project-idea-capture"
status: "approved"
record_kind: "epic"
local_id: "001"
linked_prd: "../prd.md"
linked_architecture: "../architecture.md"
created: "2026-10-24"
updated: "2026-10-24"
linked_stories: ["../stories/story-001.md", "../stories/story-002.md"]
---

# Lightweight Project and general idea capture

## Description

Deliver one lightweight `kosmic idea` action for ideas belonging to a Project and ideas belonging to no Project. The command creates the selected missing destination, saves one title-named Markdown note with dated in-note history, and returns its full-path link without launching an implementation workflow.

Requirements: [PRD FR-001–007](../prd.md). Design: [approved Architecture ADR-001–002 and storage/publication contract](../architecture.md), including title-only filenames, dated history and vault-root `GeneralIdeas/`. The user approved this Epic in the conversation. Each Story still requires separate approval before implementation.

## Scope

### In Scope

- One supported `idea` subcommand of the existing Projection CLI, with mutually exclusive explicit Project or general-vault targets.
- Project destination: `{VAULT}/Projects/{TARGET}/ideas/`. General destination: `{VAULT}/GeneralIdeas/`, without requiring, inventing or initializing a Project.
- Lazy destination-directory creation and reuse; title-only filenames with safe numeric suffixes for separate same-title ideas.
- A note title, minimal scope-appropriate metadata and `History` entries containing the supplied text under its real addition date. History is the content, not a duplicate changelog; later explicit additions preserve earlier entries.
- No-follow, complete-file, no-replace publication; meaningful refusals for unsafe targets, invalid input/identity, missing roots and filesystem failures.
- Capture-only authority in the CLI inventory, orchestrator entry process and generated guidance; unrelated commands retain their existing gates.
- A compact conversational procedure, documented layouts/examples, current canonical Consumer knowledge and governed Skill Pair regeneration during development.

### Out of Scope

- Implementing, approving, verifying or automatically promoting the ideas; Project or vault initialization; installation, Git push or router replacement.
- Automatic title-based merging, deduplication, an append/overwrite command, arbitrary output paths, a generic note editor, or a new executable.
- Eager directory backfill, historical idea/note/dream migration, idea indexes, logs, evidence packs, receipts, scheduled jobs or review rounds per capture.
- A new database, journal, lock registry, reservation protocol or generic filesystem framework.

## Story Responsibilities

The responsibilities below map to the actual records linked in Story Records. Each Story needs its own approval; Story002 starts after Story001's successful receipt.

| Slice | Deliverable | Dependency |
|-------|-------------|------------|
| Capture command and safe storage | Native Project/general selection, minimal identity checks, lazy directories, title-only names, dated History content, distinct collision handling, complete-file publication, result/refusal behavior and actual CLI proof. | None |
| Conversational capture and guidance cutover | Route explicit Project/general requests through the native command; preserve ambiguous-target clarification, capture-only authority and one-call/full-path handoff; update layouts, references, canonical knowledge and generated guidance consistently. | Receipted capture-command slice |

Use one integration owner for shared CLI and guidance edits. Classify new deterministic mechanics through the existing Task P policy when authoring implementation Stories; classification never automatically publishes a skill or adds work to individual captures.

## Story Records

| Story | Title | Dependency |
|-------|-------|------------|
| [001](../stories/story-001.md) | Native Project and general idea capture | None |
| [002](../stories/story-002.md) | Conversational idea capture and guidance cutover | Story001 receipt |

## Success Criteria

- [ ] Actual Project capture creates/reuses `ideas/`; actual general capture creates/reuses vault-root `GeneralIdeas/` without a Project entry, record or initialization.
- [ ] Both modes save title-only filenames without dates, preserve both same-title captures, and retain the complete supplied text exactly once under a dated History entry with real creation time.
- [ ] Project A, Project B, general ideas, canonical knowledge and dreams remain isolated; missing/invalid targets and unsafe paths are refused without overwriting existing data or reporting false success.
- [ ] Concurrent captures preserve distinct complete notes. Publication-failure behavior is exercised without claiming atomic rollback or silently replaying an uncertain save.
- [ ] Explicit capture needs no work record, clean writer, review, STATUS refresh, skill/router repair or per-capture sidecar. Unrelated gated mutations still refuse missing authority.
- [ ] The conversational walkthrough chooses the requested destination, invokes the supported command once, returns the actual full-absolute-path Markdown link and stops.
- [ ] Documentation, canonical Consumer knowledge and generated guidance match the exercised implementation; affected integration, actual smoke and independent Standards/Spec review pass, and each implemented Story has a native completion receipt.

## Approval and Progress

The Epic is approved; the actual Story records are linked above. Current lifecycle navigation is maintained in the [owner index](../INDEX.md), not duplicated as another mutable progress ledger here. Each Story requires approval before implementation; its native receipt is the completion authority. Planning creates no feature source, runtime data, installed package or automatic publication.
