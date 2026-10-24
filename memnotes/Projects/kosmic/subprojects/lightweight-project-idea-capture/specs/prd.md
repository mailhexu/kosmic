---
project_id: "kosmic"
subproject_id: "lightweight-project-idea-capture"
status: "approved"
record_kind: "prd"
local_id: "prd"
created: "2026-10-24"
updated: "2026-10-24"
linked_research: []
linked_epics: []
---

# Lightweight Project idea capture

## Problem Statement

Users need to save project ideas while coding or doing research without turning a tentative thought into validated knowledge, an implementation task, or a lengthy workflow. Kosmic currently has canonical `notes/` and a separate vault-level dream idea backlog, but no explicit lightweight Project-local idea capture action.

## Goals

- Recognize `kosmic idea` as an explicit request to save the supplied idea.
- Save one self-contained Markdown note per idea under `{VAULT}/Projects/{TARGET}/ideas/`, beside `notes/` and `specs/`, not inside a feature subproject.
- Create `ideas/` automatically on first capture when absent, for both new and existing Projects.
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
| FR-001 | Expose the `kosmic idea` capture action in the skill, backed by a supported saving command through the existing Projection CLI. Resolve the current owning Project or an explicitly selected Project; never guess a different Project or use a feature-local directory. Architecture defines the exact CLI arguments. | must |
| FR-002 | Create the selected Project's root-level `ideas/` directory if missing and write the idea note in the same invocation. An existing directory is reused without reinitialization or migration. | must |
| FR-003 | Accept an ordinary idea description without requiring the user to complete a spec template. Derive a short title when none is supplied; retain the supplied idea and enough supplied context to understand it independently. Record the creation time; never invent evidence or present speculation as verified knowledge. | must |
| FR-004 | Save a new Markdown file using a readable filename. Capturing another idea with the same title must preserve both notes without silently replacing, truncating, or merging an existing file. | must |
| FR-005 | The explicit capture request authorizes only the idea note and its missing containing directory. Individual captures need no Quick Task, Story, `work start`, implementation review, or `work finish`; they grant no authority to implement the idea or modify other Project state. | must |
| FR-006 | Successful command output identifies the saved file. The agent returns an individual Markdown link labelled with its full absolute path, then stops; no confirmation-only listing, validation, STATUS refresh, or extra bookkeeping follows success. Errors identify the failure and never claim that an unsaved idea was saved. | must |
| FR-007 | Update the documented Project layout and command guidance. Keep idea captures separate from canonical `notes/`, generated skills, completion checks, and existing dream publication; later development or promotion uses its own explicitly requested workflow. | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-001 | Capture adds one idea file and, only when needed, its directory; no per-capture sidecar or duplicate store. Existing ideas and unrelated files remain untouched. | must |
| NFR-002 | Writes stay within the selected Project's `ideas/`; refuse unsafe path/symlink targets, a non-directory `ideas` entry, and file collisions rather than escaping the Project or overwriting data. Same-title captures use distinct safe destinations. | must |
| NFR-003 | Use existing Project identity, Markdown, command-result, and safe-file-publication conventions; avoid a new database, generic transaction framework, or required external dependency. | must |

## Success Criteria

- [ ] A real `kosmic idea` request against an existing Project with no `ideas/` creates the directory and saves the supplied idea there.
- [ ] A subsequent capture reuses the directory, and two captures with the same title preserve both idea bodies.
- [ ] Capturing for Project A never writes into Project B, a feature subproject, or canonical `notes/`.
- [ ] The returned file contains the user's idea, a usable title and creation time, without fabricated findings or forced spec fields.
- [ ] Unsafe directory/file targets are refused without overwriting existing data or reporting false success.
- [ ] Capture returns the saved file link without creating a work record, review, evidence artifact, STATUS update, or implementation approval.

## Context

- User request: an `ideas/` directory in each Kosmic Project root and a `kosmic idea` action that creates the directory and note when needed.
- [Current CLI conventions](../../../notes/cli-projection-commands.md): trust successful command outputs and preserve explicit Project identity.
- [Existing dream workflow](../../../notes/dream-reflection-workflow.md): its idea backlog is vault-level and remains unchanged; this feature handles explicit Project-local capture.
- This PRD proposes lazy directory creation, not eager initialization or a vault-wide migration. Captured ideas remain tentative; canonical knowledge and approved work retain their existing separate authority.
- [Proposed Architecture](architecture.md) defines the single capture interface, bounded authority and safe publication design; its approval is a separate gate.

## Approval Gate

The user approved this PRD in the conversation on 2026-10-24. Architecture is the next approval gate; this approval authorizes planning, not feature implementation or installation.
