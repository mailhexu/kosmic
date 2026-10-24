---
project_id: "kosmic"
subproject_id: "lightweight-project-idea-capture"
status: "draft"
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

Implements the [approved PRD](prd.md). This Architecture is proposed, not implementation approval. No feature code or installed skill has changed. Existing code and knowledge resolved the design questions; no research memo or evidence sidecar is needed.

A Project Idea is tentative input, not Project Knowledge or a Work Record. Capturing one does not verify its claims, select work, or authorize implementation.

## ADR-001: One Capture Operation

**Status:** Proposed. The common case is one description saved once; a generic note interface or agent-only editor would expose unnecessary choices or duplicate safety mechanics.

Use one `idea` subcommand of the existing Projection CLI:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py idea \
  --project /absolute/memnotes/Projects/example \
  --text "Try using symmetry to reduce the sampling cost." \
  --title "Symmetry-reduced sampling"
```

`--project` and non-blank `--text` are required. `--title` is optional. Text may contain multiple lines in the argument. There is no interactive prompt, alternate input-file mode, output-path override, overwrite flag, work-record argument, or new executable.

The skill recognizes `kosmic idea <description>` or an equivalent explicit capture request, resolves the configured Project, and supplies this command's explicit Project path. An explicit Project selection wins; ambiguity is clarified rather than guessed. It preserves the supplied text and relevant supplied context, without inventing research or evidence.

Three designs were considered:

- **Selected: one capture command with direct text.** Small interface; identity, naming and safe publication are hidden from the caller.
- **Generic `note create --kind idea --output ...`.** Flexible, but exposes arbitrary output choices and confuses tentative ideas with canonical knowledge. Rejected.
- **Agent-only file editing.** Avoids a CLI addition but repeats naming, containment and collision handling across agents. Rejected.

## Module Design

| Location | Responsibility |
|----------|----------------|
| `skills/scripts/kosmic_ideas.py` | One deep operation, `capture_idea(project_root, text, *, title=None) -> dict`: validate inputs and Project identity, render the note, allocate a safe name, publish without replacement, and return the saved path. Private filesystem helpers stay local. |
| `kosmic_project_skills.py` | Argparse entry, early capture dispatch, existing JSON/error rendering, and explicit mutation-inventory/exemption classification. No generic work-record or managed-run wrapper for individual captures. |
| `skills/references/task_idea.md` | One compact owning capture procedure with the complete invocation, output contract and refusal handling. The orchestrator routes explicit capture before development/bootstrap prerequisites. |
| Existing skill/README/layout references, `record_first_contract()`, canonical CLI note and generated Skill Pair | Explain the narrow capture exception and tentative-data separation consistently. Developing this feature still uses approved Stories, verification and review. |

Reuse existing no-follow `read_document` and Project Identifier slug syntax to read the selected root's regular `ProjectEntry.md`; require its valid non-empty `project_id`. Do not enumerate specs, inspect receipts/history policy, load projections/library packets, invoke Git, register a writer, or initialize a missing Project. The selected Project path is resolved once, never inferred from a basename or a feature entry.

Capture therefore works without a clean Git worktree, a current work item, or complete generated guidance. Missing or malformed Project identity is a refusal, not permission to repair it. Other commands keep their existing loaders and gates unchanged.

## Storage Contract

Store each note at `ideas/YYYY-MM-DD-<slug>.md`, relative to the selected Project root. Use UTC date and creation instant from the same real clock read. The title-derived slug follows the existing bounded lowercase ASCII/hyphen normalization convention; use `idea` if no usable slug remains. Keep the slug at most80 characters so the date and collision suffix fit ordinary filename limits.

For existing regular-file collisions try `-2`, `-3`, and subsequent suffixes. Every explicit capture creates a distinct note, even when its title or text repeats. There is no deduplication or idempotent replay promise.

The file has only these frontmatter fields:

```yaml
type: idea
status: draft
project_id: example
title: "Symmetry-reduced sampling"
created: "2026-10-24T12:34:56.123456Z"
```

The timestamp above illustrates the format, not an asserted capture time. Render a top-level title followed by the supplied idea text. If the title is omitted, derive it deterministically from the first non-empty text line, collapsing heading/whitespace decoration and limiting it to80 characters. Preserve the complete body, including Unicode, equations and uncertainty; title/filename shortening never truncates the idea. Use existing quoted YAML-scalar conventions, not raw user text interpolated into frontmatter.

No audience, confidence, skill-resource metadata, approval fields, generated index, log entry, receipt or evidence file is required. `ideas/` remains a sibling of `notes/`, so existing notes-only validation, projection and curation stay structurally separate. No automatic promotion, lifecycle management or dream-backlog migration is added.

## ADR-002: Capture-Only Authority

**Status:** Proposed. Applying the usual implementation-record gate to each idea contradicts the approved lightweight capture requirement. A named, output-limited exception avoids weakening the rest of the workflow.

Add `idea` as a specifically named bounded mutation in `MUTATION_INVENTORY` and `MUTATION_GATE_EXEMPTIONS`: explicit idea capture authorizes only one note and creation of its missing `ideas/` directory. It is not read-only and not an exemption for other commands or arbitrary paths.

The orchestrator's capture fast path resolves the configured Project and runs this operation without a Quick Task, Story, required-procedure-skill check, router/pair repair, `work start`, review, `work finish`, STATUS generation or session bookkeeping. No capture-specific approval flag is needed: the explicit request is its bounded authority. No automatic action follows the save.

This exception must be reflected in the record-first and entry-process guidance, not merely in one CLI branch. Feature development, subsequent implementation of an idea, knowledge promotion and installation keep their normal separate authority.

## Safe Publication and Failure

1. Reject blank input, an explicitly blank title, invalid identity or invalid text encoding before creating the directory.
2. Retain no-follow Project/`ideas` directory descriptors. Create only the literal `ideas` child if absent. Refuse a symlink, non-directory child or unsafe target; never follow them or create other parent directories.
3. Write the complete UTF-8 note into an exclusive destination-sibling staging file and flush/fsync it before publication.
4. Publish with descriptor-relative, no-replace linking, following the existing spec writer's pattern. On a regular-file name collision choose the next suffix; on a symlink, directory or other unsafe candidate refuse. Concurrent captures cannot overwrite one another.
5. Remove owned temporary staging and fsync the containing directory before returning success. No lock, reservation registry, global counter, managed-run manifest or journal is written.

Do not call `_stage_bytes` unchanged: its identical-content collision path returns an existing file as an idempotent success, which conflicts with distinct-per-request captures. Reuse its no-follow/stage/link pattern locally, not its spec reservation or replay semantics; no generic filesystem refactor is needed.

This is local no-replace publication, not an OS sandbox or a transaction against arbitrary external directory moves. Ordinary failures clean their owned temporary file. An interruption can leave a hidden staging file; a late filesystem failure can leave an empty directory or an already-published complete note. Report the affected path and failure rather than promising rollback or automatically retrying an uncertain save. Never sweep another operation's files.

## Result and Error Contract

On success, print JSON containing `project_id`, `idea_path` (the actual full absolute file path), `title`, and `created`, then exit0. No status receipt or operation ID is returned.

The agent uses that returned path for an individual Markdown link whose visible label is the full absolute path, then stops. No help lookup, listing or read-back follows success.

Input, identity and unsafe-target refusals use an idea-specific diagnostic and nonzero exit without success JSON; filesystem failures retain the CLI's existing error treatment. Diagnostics must not recommend spec-operation resume for an idea. No content is claimed saved unless publication succeeded.

## Verification Strategy

| Observable behavior | Verification |
|---------------------|--------------|
| First and subsequent captures | Actual CLI against disposable Projects with and without `ideas/`; observe saved title/body/time and the returned path. |
| Same-title and concurrent requests | Distinct complete notes retain both bodies; existing bytes remain unchanged, including identical-content requests. |
| Project isolation and scope | Capture for A leaves B and unrelated paths unchanged; use an identity-only Project without Git, specs, notes, router or projections. |
| Unsafe targets and failures | Exercise symlink/non-directory `ideas`, unsafe candidate files and controlled write/publication failure; no overwritten existing bytes or false success. |
| No workflow overhead | Real capture succeeds with no work record; unrelated gated mutation still refuses absent authority. Inspect the actual capture footprint, not implementation call counts. |
| Conversational procedure | Walk through an explicit `kosmic idea` request: resolve Project, invoke once, return the full-path link, stop. |

Keep permanent tests for consumer-visible collision, isolation, refusal and publication invariants; use throwaway smoke for procedural/result wiring. Reuse existing test conventions. After implementation stabilizes, run affected integration once, update canonical guidance through normal governed generation, obtain independent Standards/Spec review, and finish the approved Stories natively.

## Dependencies and Next Gate

Standard-library Python and the existing Projection CLI/document parsing conventions only. No new runtime package or scheduled process.

After user approval, create the owner-local Epic and implementable Stories. Until then, only this Architecture, its approval/navigation, the Idea glossary term, planning log and derived STATUS are planning outputs. No source, generated guidance or installed package is changed at this gate.

