---
project_id: "kosmic"
subproject_id: "lightweight-project-idea-capture"
status: "approved"
record_kind: "architecture"
local_id: "architecture"
linked_prd: "prd.md"
created: "2026-10-24"
updated: "2026-10-24"
linked_research: []
linked_stories: []
---

# Lightweight Project idea capture

## Scope and Status

Implements the [approved PRD](prd.md). The user approved the initial Project capture design on 2026-10-24, then requested title-only filenames, dated history and vault-root `GeneralIdeas/`. At the explicit Architecture-amendment approval gate, the user's “next” was taken as permission to advance this amended design. No feature code or installed skill has changed. Existing code and knowledge resolved the design questions; no research memo or evidence sidecar is needed.

A Project Idea is tentative input, not Project Knowledge or a Work Record. Capturing one does not verify its claims, select work, or authorize implementation.

## ADR-001: One Capture Operation

**Status:** Accepted. The amended one-operation interface has mutually exclusive Project and general targets without another command or arbitrary output-path interface.

Use one `idea` subcommand of the existing Projection CLI:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py idea \
  --project /absolute/memnotes/Projects/example \
  --text "Try using symmetry to reduce the sampling cost." \
  --title "Symmetry-reduced sampling"
```

Exactly one of `--project PROJECT_ROOT` or `--vault VAULT_ROOT` is required, together with non-blank `--text`; `--title` is optional. `--project` selects that Project's `ideas/`. `--vault` selects that vault's `GeneralIdeas/` and needs no Project. For general capture, replace the example's `--project ...` with `--vault /absolute/memnotes`. Text may contain multiple lines in the argument. There is no interactive prompt, input-file mode, output-path override, overwrite flag, work-record argument, or new executable.

The skill recognizes `kosmic idea <description>` or an equivalent explicit capture request. For a Project idea it resolves the configured or explicitly selected Project; for an explicit general idea it resolves the configured or explicitly selected vault. It never silently classifies an unclear destination or invents a Project for general capture. Clarify ambiguity before invoking the command. Preserve supplied text/context without inventing research or evidence.

Three designs were considered:

- **Selected: one capture command with direct text.** Small interface; identity, naming and safe publication are hidden from the caller.
- **Generic `note create --kind idea --output ...`.** Flexible, but exposes arbitrary output choices and confuses tentative ideas with canonical knowledge. Rejected.
- **Agent-only file editing.** Avoids a CLI addition but repeats naming, containment and collision handling across agents. Rejected.

## Module Design

| Location | Responsibility |
|----------|----------------|
| `skills/scripts/kosmic_ideas.py` | One deep operation, `capture_idea(text, *, project_root=None, vault_root=None, title=None) -> dict`: require exactly one target, validate inputs and target identity/directory, render the note, allocate a safe name, publish without replacement, and return the saved path. Private filesystem helpers stay local. |
| `kosmic_project_skills.py` | Argparse entry, early capture dispatch, existing JSON/error rendering, and explicit mutation-inventory/exemption classification. No generic work-record or managed-run wrapper for individual captures. |
| `skills/references/task_idea.md` | One compact owning capture procedure with the complete invocation, output contract and refusal handling. The orchestrator routes explicit capture before development/bootstrap prerequisites. |
| Existing skill/README/layout references, `record_first_contract()`, canonical CLI note and generated Skill Pair | Explain the narrow capture exception and tentative-data separation consistently. Developing this feature still uses approved Stories, verification and review. |

For Project capture, reuse no-follow `read_document` and Project Identifier slug syntax to read that root's regular `ProjectEntry.md`; require a valid non-empty `project_id`. For general capture, require only the explicitly selected existing vault directory: do not read, require or create a Project entry, or assign a fake Project Identifier. Resolve the selected root once, never infer it from a basename or feature entry.

Neither path enumerates specs, inspects receipts/history policy, loads projections/library packets, invokes Git, registers a writer, or initializes a missing Project/vault. Capture works without a clean Git worktree, a current work item, or complete generated guidance. An invalid Project identity or missing selected root is a refusal, not permission to repair it. Other commands keep their existing loaders and gates unchanged.

## Storage Contract

Store Project notes at `PROJECT_ROOT/ideas/<slug>.md` and general notes at `VAULT_ROOT/GeneralIdeas/<slug>.md`. Preserve the exact `GeneralIdeas` directory spelling. Do not put a date in the filename. The title-derived slug follows the existing bounded lowercase ASCII/hyphen normalization convention; use `idea` if no usable slug remains. Keep the slug at most80 characters so the collision suffix fits ordinary filename limits.

For existing regular-file collisions try `-2`, `-3`, and subsequent suffixes. Every explicit capture creates a distinct note, even when its title or text repeats. There is no deduplication or idempotent replay promise.

Both scopes use the following minimal frontmatter; `project_id` is present only on Project ideas and omitted entirely on general ideas:

```yaml
type: idea
status: draft
project_id: example
title: "Symmetry-reduced sampling"
created: "2026-10-24T12:34:56.123456Z"
```

The timestamp above illustrates the format, not an asserted capture time. Render a top-level title and a `## History` section. Its initial `### YYYY-MM-DD` entry contains the complete supplied idea text, using the UTC day from the same real clock read as `created`. The dated entries are the idea content, not a duplicate changelog or a second copy of the body. Later explicit additions belong under another dated entry in the same note and preserve earlier entries; no automatic title-based merge or append command is introduced by this format rule. If the title is omitted, derive it deterministically from the first non-empty text line, collapsing heading/whitespace decoration and limiting it to80 characters. Preserve the complete text, including Unicode, equations and uncertainty; title/filename shortening never truncates the idea. Use existing quoted YAML-scalar conventions, not raw user text interpolated into frontmatter.

No audience, confidence, skill-resource metadata, approval fields, generated index, log entry, receipt or evidence file is required. Project `ideas/` is a sibling of `notes/`; vault-root `GeneralIdeas/` is outside every Project. Existing notes-only validation, projection and curation therefore stay structurally separate. No automatic promotion, lifecycle management or dream-backlog migration is added.

## ADR-002: Capture-Only Authority

**Status:** Accepted. Capture-only authority extends to general ideas without a synthetic Project. Applying implementation-record gates to either destination contradicts the lightweight capture requirement; a named, output-limited exception avoids weakening other workflows.

Add `idea` as a specifically named bounded mutation in `MUTATION_INVENTORY` and `MUTATION_GATE_EXEMPTIONS`: explicit capture authorizes one note in the selected Project's `ideas/` or the selected vault's `GeneralIdeas/`, plus that missing child directory only. It is not read-only or authority for other commands, another Project, an arbitrary path, or a new vault.

The orchestrator's capture fast path resolves the selected Project or general vault destination and runs this operation without a Quick Task, Story, required-procedure-skill check, router/pair repair, `work start`, review, `work finish`, STATUS generation or session bookkeeping. No capture-specific approval flag is needed: the explicit request is its bounded authority. No automatic action follows the save.

This exception must be reflected in the record-first and entry-process guidance, not merely in one CLI branch. Feature development, subsequent implementation of an idea, knowledge promotion and installation keep their normal separate authority.

## Safe Publication and Failure

1. Require exactly one target; reject blank input, an explicitly blank title, invalid Project identity, a missing selected Project/vault directory, or invalid text encoding before creating the child directory.
2. Retain no-follow root/destination directory descriptors. Create only the literal `ideas` or `GeneralIdeas` child selected by the command. Refuse a symlink, non-directory child or unsafe target; never follow them or create other parent directories.
3. Write the complete UTF-8 note into an exclusive destination-sibling staging file and flush/fsync it before publication.
4. Publish with descriptor-relative, no-replace linking, following the existing spec writer's pattern. On a regular-file name collision choose the next suffix; on a symlink, directory or other unsafe candidate refuse. Concurrent captures cannot overwrite one another.
5. Remove owned temporary staging and fsync the containing directory before returning success. No lock, reservation registry, global counter, managed-run manifest or journal is written.

Do not call `_stage_bytes` unchanged: its identical-content collision path returns an existing file as an idempotent success, which conflicts with distinct-per-request captures. Reuse its no-follow/stage/link pattern locally, not its spec reservation or replay semantics; no generic filesystem refactor is needed.

This is local no-replace publication, not an OS sandbox or a transaction against arbitrary external directory moves. Ordinary failures clean their owned temporary file. An interruption can leave a hidden staging file; a late filesystem failure can leave an empty directory or an already-published complete note. Report the affected path and failure rather than promising rollback or automatically retrying an uncertain save. Never sweep another operation's files.

## Result and Error Contract

On success, print JSON containing `scope` (`project` or `general`), `idea_path` (the actual full absolute file path), `title`, and `created`, then exit0. Include `project_id` only for Project capture; general output omits it. No status receipt or operation ID is returned.

The agent uses that returned path for an individual Markdown link whose visible label is the full absolute path, then stops. No help lookup, listing or read-back follows success.

Input, identity and unsafe-target refusals use an idea-specific diagnostic and nonzero exit without success JSON; filesystem failures retain the CLI's existing error treatment. Diagnostics must not recommend spec-operation resume for an idea. No content is claimed saved unless publication succeeded.

## Verification Strategy

| Observable behavior | Verification |
|---------------------|--------------|
| First and subsequent captures | Actual CLI against Project/vault roots with and without their destination directories; observe title-only filename, complete content under a dated History entry, creation time and the returned path. |
| Same-title and concurrent requests | Distinct complete notes retain both bodies; existing bytes remain unchanged, including identical-content requests. |
| Target isolation and identity | Project A capture leaves B and `GeneralIdeas/` unchanged; general capture leaves every Project and dreams unchanged and works without any Project entry. Refuse both/neither selector and missing roots; use minimal roots without Git, specs, notes, router or projections. |
| Unsafe targets and failures | Exercise symlink/non-directory `ideas` and `GeneralIdeas`, unsafe candidate files and controlled write/publication failure; no overwritten existing bytes or false success. |
| No workflow overhead | Real capture succeeds with no work record; unrelated gated mutation still refuses absent authority. Inspect the actual capture footprint, not implementation call counts. |
| Conversational procedure | Walk through explicit Project and general `kosmic idea` requests: resolve the requested destination, invoke once, return the full-path link, stop. |

Keep permanent tests for consumer-visible collision, isolation, refusal and publication invariants; use throwaway smoke for procedural/result wiring. Reuse existing test conventions. After implementation stabilizes, run affected integration once, update canonical guidance through normal governed generation, obtain independent Standards/Spec review, and finish the approved Stories natively.

## Dependencies and Next Gate

Standard-library Python and the existing Projection CLI/document parsing conventions only. No new runtime package or scheduled process.

The Project/general Architecture amendment is approved. The [Epic draft](epics/epic-001.md) is the next approval gate: approve it before Story creation, then approve each Story before implementation. Planning outputs remain specs, approval/navigation, glossary, log and derived STATUS only; no feature source, generated guidance or installed package changes at this gate.

