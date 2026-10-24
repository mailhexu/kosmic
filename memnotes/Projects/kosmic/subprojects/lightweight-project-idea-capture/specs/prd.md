---
project_id: "kosmic"
subproject_id: "lightweight-project-idea-capture"
status: "approved"
record_kind: "prd"
local_id: "prd"
created: "2026-10-24"
updated: "2026-10-24"
linked_research: []
linked_epics: ["epics/epic-001.md"]
---

# Lightweight Project idea capture

## Problem Statement

Users need to save ideas while coding or doing research without turning a tentative thought into validated knowledge, an implementation task, or a lengthy workflow. Some ideas belong to a Project; others do not. Kosmic currently has canonical `notes/` and a separate vault-level dream idea backlog, but no explicit lightweight capture action for Project ideas or general ideas.

## Goals

- Recognize `kosmic idea` as an explicit request to save the supplied idea.
- Save one self-contained Markdown note per idea under `{VAULT}/Projects/{TARGET}/ideas/` for Project ideas, or `{VAULT}/GeneralIdeas/` for ideas that do not belong to a Project.
- Create the selected `ideas/` or `GeneralIdeas/` directory automatically on first capture when absent.
- Keep capture quick: save the note and return its actual path; no implementation workflow or administrative confirmation loop.

## Non-Goals

- Implementing, approving, verifying, or automatically researching the captured idea.
- Automatically promoting ideas into canonical knowledge, specs, skills, or skill-curation inputs.
- Moving or rewriting existing notes, dream records, or the vault-level dream idea backlog.
- Bulk-creating directories across existing Projects, initializing a missing Project, installing skills, or adding another standalone executable.
- Mandatory idea indexes, logs, evidence packs, receipts, scheduled jobs, or review rounds for individual captures.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-001 | Expose the `kosmic idea` capture action in the skill, backed by a supported saving command through the existing Projection CLI. Resolve an explicit Project selection or the configured current Project for Project ideas. Explicit general-idea requests select the configured vault's `GeneralIdeas/`, without requiring or creating a Project. Clarify an ambiguous destination instead of guessing. Architecture defines the exact CLI arguments. | must |
| FR-002 | Create only the selected Project's `ideas/` or the selected vault's `GeneralIdeas/` directory if missing and write the idea note in the same invocation. Reuse an existing directory without reinitialization or migration; do not initialize a missing Project or vault. | must |
| FR-003 | Accept an ordinary idea description without requiring a spec template. Derive a short title when none is supplied. Record creation time and place the complete supplied idea/context under a dated `History` entry inside the note, so it is clear which day what was added. Later additions retain earlier entries and carry their own date; never invent evidence or present speculation as verified knowledge. | must |
| FR-004 | Use only the normalized title in the Markdown filename, with no date prefix or suffix. Capturing a separate idea with the same title uses a numeric collision suffix and preserves both notes without silently replacing, truncating, or merging an existing file. | must |
| FR-005 | The explicit capture request authorizes only one idea note at the selected Project or general destination and its missing containing directory. Individual captures need no Quick Task, Story, `work start`, implementation review, or `work finish`; they grant no authority to implement the idea or modify other Project/vault state. | must |
| FR-006 | Successful command output identifies the saved file. The agent returns an individual Markdown link labelled with its full absolute path, then stops; no confirmation-only listing, validation, STATUS refresh, or extra bookkeeping follows success. Errors identify the failure and never claim that an unsaved idea was saved. | must |
| FR-007 | Update Project/vault layouts and command guidance. Keep Project and general ideas separate from canonical `notes/`, generated skills, completion checks and existing dream publication; later development or promotion uses its own explicitly requested workflow. General ideas carry no fabricated Project identity. | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Capture adds one idea file and, only when needed, its directory; no per-capture sidecar or duplicate store. Existing ideas and unrelated files remain untouched. | must |
| NFR-002 | Writes stay within the selected Project's `ideas/` or the selected vault's `GeneralIdeas/`; refuse unsafe path/symlink targets, a non-directory destination entry and file collisions rather than escaping the selected root or overwriting data. Same-title captures use distinct safe destinations. | must |
| NFR-003 | Use existing Project identity, Markdown, command-result, and safe-file-publication conventions; avoid a new database, generic transaction framework, or required external dependency. | must |

## Success Criteria

- [ ] Actual Project capture creates a missing `ideas/` and saves there; actual general capture creates a missing vault-root `GeneralIdeas/` and saves there without requiring or creating a Project.
- [ ] A subsequent capture reuses the directory, and two captures with the same title preserve both idea bodies.
- [ ] Project A capture never writes into B, a feature subproject, canonical `notes/` or `GeneralIdeas/`; general capture never writes into any Project or the dream backlog.
- [ ] The filename is title-based without a date; the note contains a usable title, creation time and a dated `History` entry holding the supplied idea/context without duplication, fabricated findings or forced spec fields.
- [ ] Unsafe directory/file targets are refused without overwriting existing data or reporting false success.
- [ ] Capture returns the saved file link without creating a work record, review, evidence artifact, STATUS update, or implementation approval.

## Context

- User request: Project-root `ideas/` capture, plus a vault-root `GeneralIdeas/` for ideas that do not belong to any Project; both use title-only filenames and dated in-note history.
- [Current CLI conventions](../../../notes/cli-projection-commands.md): trust successful command outputs and preserve explicit Project identity.
- [Existing dream workflow](../../../notes/dream-reflection-workflow.md): its vault-level idea backlog remains unchanged; explicit general capture uses `GeneralIdeas/`, not dreams.
- Directories are created lazily, not through eager initialization or vault-wide migration. Captured ideas remain tentative; canonical knowledge and approved work retain separate authority.
- [Architecture](architecture.md) contains the previously approved design, title/history amendment, and the proposed explicit Project-versus-general target amendment.

## Approval Gate

The user approved the PRD and initial Architecture on 2026-10-24, then explicitly requested title-only filenames, dated history and vault-root `GeneralIdeas/`. These product requirements incorporate those instructions. The expanded Project/general command contract returns to Architecture approval; Epic approval remains required before Story creation. Planning authorizes no implementation or installation.
