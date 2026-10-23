---
project_id: "kosmic"
subproject_id: "command-owned-indexes-and-completion-review-context"
status: "approved"
record_kind: "prd"
local_id: "prd"
created: "2026-10-23"
updated: "2026-10-23"
linked_research: []
linked_epics: ["epics/epic-001.md", "epics/epic-002.md"]
---

# Command-owned indexes and completion review context

## Problem Statement

Agents still perform deterministic bookkeeping that belongs in the CLI. The mutation inventory declares that `spec-create` publishes an index entry, but non-PRD creation currently stages only the draft record. Completion changes an existing row's status and does not insert missing rows. Separately, preparing review requires an inline Python program importing `resolve_work_record` and `source_revision`, despite these being deterministic existing mechanics.

The user approved removing avoidable orchestration. The related guidance cleanup is governed by [Remove redundant workflow orchestration](../../../specs/quick-tasks/remove-redundant-workflow-orchestration.md); this PRD covers the two public CLI contract changes and is user-approved.

## Goals

- A successful spec creation publishes its draft record and correct owning index entry, without an agent-written row or a follow-up confirmation.
- A supported read-only CLI returns the exact existing review fingerprint for the selected record/worktree, eliminating inline internal-module imports.
- Keep live authority, ownership, containment, approval, review binding and receipt semantics unchanged.

## Non-Goals

- New workflow tiers, review exemptions, automatic approvals, scheduler/telemetry systems, or a second persistence/evidence framework.
- Historical record migration, receipt/pin rewriting, global router ownership changes, or automatic adapter installation.
- Treating a successful draft, fingerprint calculation or review approval as completed implementation.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Every supported `spec-create` kind publishes the draft plus one canonical entry in its owning index: owner-local for feature records, Project-level for shared Quick Tasks. Existing immutable identity and owner rules remain. | must |
| FR-002 | Entry links resolve to the returned canonical record, with correct title/kind/status. Preserve unrelated index content and avoid duplicate entries during supported resume/recovery. | must |
| FR-003 | Exit success only after the declared record/index outputs are published. Errors identify incomplete work and deterministic recovery; interrupted recovery preserves unrelated/concurrent edits and never silently blesses a conflicting record. Reuse existing safe publication/resume machinery where applicable. | must |
| FR-004 | CLI output identifies the owning record/index paths clearly enough for callers to continue without path discovery, manual row construction or a validation round-trip. | must |
| FR-005 | A supported read-only completion-preparation interface returns the fingerprint for an explicit record and writer using the existing `source_revision` algorithm and exclusions, not Git HEAD or a newly defined hash. Interface details are decided in Architecture. | must |
| FR-006 | Preserve authored observation fields and blank unauthored criteria. Fingerprint/preparation output fabricates no evidence, reviewer decision or approval, writes no Project/writer state, and grants no additional authority. | must |
| FR-007 | Finish still checks current source/review scope and existing safety gates. Source/context drift must still invalidate stale proof; exposing the calculation never caches permission or weakens revision binding. | must |
| FR-008 | Migrate all current callers, command references and generated guidance to native index ownership and CLI fingerprint output. Remove obsolete manual index-creation instructions and internal-Python recipes only when their replacements are implemented and exercised. | must |

## Non-Functional Requirements

- Stdlib-only, deterministic and offline. No new persistent record class, sidecar, cache or framework just to avoid a command.
- Preserve supported owner boundaries, unrelated edits and established command refusal precedence. Reuse current locks/publication seams instead of a parallel convention.
- Tests cover consumer-visible creation/resume/failure behavior, index preservation, source-drift binding and read-only output; actual CLI smoke exercises the final documented sequence.

## Success Criteria

- [ ] Creating each supported spec kind produces a resolvable canonical index entry with no manual row edit.
- [ ] Recovery from an interrupted record/index publication neither duplicates entries nor overwrites unrelated changes, and failures are not reported as success.
- [ ] A real CLI preparation invocation supplies the current review fingerprint without an inline Python script; changed source produces the expected binding change.
- [ ] Preparation leaves Project/writer bytes unchanged and retains authored observations without manufacturing approvals.
- [ ] Existing authorization, review, containment, receipt and scientific-verification behavior remains intact; all affected callers use the new contracts.

## Sources and Context

- [Consumer CLI invariants](../../../notes/cli-projection-commands.md)
- Current owners: `skills/scripts/kosmic_specs.py` record staging, `kosmic_completion.py::_update_indexes` and `source_revision`, and the Projection CLI mutation inventory/parser.
- [Architecture](architecture.md), [indexed creation Epic](epics/epic-001.md) and [completion fingerprint Epic](epics/epic-002.md) are approved; their linked Stories are draft for approval.
- Current caller: `skills/references/work_completion.md` embeds the internal-Python fingerprint recipe.

## Approval Gate

PRD, Architecture and Epics approved by the user in this conversation. Each linked draft Story requires approval before CLI implementation.
