---
project_id: "kosmic"
subproject_id: "deterministic-flat-spec-migration"
status: "approved"
record_kind: "prd"
local_id: "prd"
created: "2026-10-11"
updated: "2026-10-11"
linked_research: []
linked_epics: ["epics/epic-001.md"]
related_notes: ["../../../notes/cli-extension-conventions.md"]
---

# Deterministic Flat Spec Migration

## Problem Statement

Migrating legacy flat feature specs into owner-local subprojects currently requires agents to perform mechanical file and metadata edits. This is slow, costly, and exposes otherwise deterministic work to inconsistent manual edits. The existing `migrate-subprojects-plan` command produces candidate mappings and rewritten bytes but cannot apply them.

## Goals

- Migrate one explicitly selected Project through offline Python commands without model calls.
- Reuse the existing planner and catalog rather than introduce another migration convention.
- Restrict human input to ambiguous ownership and explicit approval of the exact plan.

## Non-Goals

- Approving work records, inventing acceptance evidence or code-review decisions, or converting historical completion into new implementation authority.
- Migrating notes or Shared Skill Library topics, installing adapters, or changing installed skills.
- Automatically migrating every Project in a vault or inferring owners from prose when declared links are ambiguous.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-M01 | Retain the read-only planning command. Emit a reviewable source-to-target map, exact rewritten bytes and hashes, shared-record disposition, and unresolved ambiguities. | must |
| FR-M02 | Provide a companion apply command consuming a saved plan, its explicitly approved digest, and an approved shared Quick Task in the selected Project. Applying a plan must not depend on the owner-aware catalog it establishes. | must |
| FR-M03 | Resolve owners from declared ancestry; require explicit assignments for unresolved or conflicting ownership. Refuse application with ambiguities or destination collisions. | must |
| FR-M04 | Recheck the complete input inventory, source hashes, Project identity and destination state before publishing. Stale, tampered, incomplete, escaping or symlinked plans must fail without overwriting unrelated work. | must |
| FR-M05 | Move feature records to owner-local specs; create SubprojectEntry and owner indexes; canonicalize shared Quick Tasks and proposals in place; rewrite live ancestry, dependency, metadata and Markdown links. Preserve lifecycle status and content not required by the mapping. | must |
| FR-M06 | Rewrite active Project and owner indexes and live inbound references so removal of old feature files does not leave broken active links. Preserve historical evidence and logs unchanged, and record the old-to-new identity/path map. | must |
| FR-M07 | Validate the complete candidate with SpecCatalog before cutover. Publish with a defined recoverable transaction, backups and a receipt; ordinary failure restores the prior state, and interrupted execution has a deterministic safe recovery path. | must |
| FR-M08 | Repeating the same completed migration reports the existing verified outcome without duplicating owners, records or receipts. Concurrent migration or record creation cannot race publication. | must |
| FR-M09 | Regenerate STATUS only at an existing bound working directory. Report an unbound STATUS without inventing a binding. Any changed proposal fingerprint must retain its original decision and be marked for review when equivalence is not mechanical. | must |

## Non-Functional Requirements

- Python 3.11+, standard library only, offline, and no agent or model invocation.
- A fixed Project snapshot and assignments produce deterministic plans and outputs.
- Installation and migration execution approvals remain separate from approval to implement this tool.
- Runtime follows Project inventory size; no scan of unrelated repositories or vault Projects.

## Success Criteria

- [ ] A representative Project with multiple features, shared tasks and cross-owner dependencies migrates via actual CLI commands and passes catalog validation.
- [ ] All live links resolve to the intended records; unrelated notes, immutable evidence and lifecycle decisions retain their original content.
- [ ] Ambiguous ownership, changed inputs, tampered plans, collisions and path escapes refuse mutation.
- [ ] Injected publication failure restores the original state; interrupted application can recover safely.
- [ ] Rerunning a completed plan makes no additional content changes.
- [ ] Documentation gives a plan → review/approve → apply → verify workflow requiring no agent during execution.

## Existing Evidence

The current CLI planner ran read-only against the Kosmic Project on 2026-10-11. It planned 112 feature-record moves and 13 shared records, producing 125 rewritten documents with zero reported ownership ambiguities. This proves planning automation on that snapshot, not safe application or complete inbound-link coverage.

## Approval Boundary

The user approved this PRD on 2026-10-11. Architecture and Story approval remain required before implementation. Building the executor does not approve migrating any live Project. Each actual migration requires a reviewed plan and explicit Project-scoped work authority.
