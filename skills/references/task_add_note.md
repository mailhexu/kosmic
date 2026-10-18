# Task: Add Note

Create or update atomic notes, and log daily progress.

Before durable note/log edits, use the current compatible governing record and declared shared-note scope, or establish a standalone low-risk Quick Task and obtain approval. Reading existing knowledge is record-free; finding useful knowledge does not silently authorize publication. Preserve pre-dirty work and follow SKILL.md Record-first authority.

## When to Use This Task

**AUTO-TRIGGERS - Run Add Note IF:**

| If you... | Then add note for... |
|-----------|---------------------|
| Read source code | Algorithm/pattern learned |
| Make a decision | Decision + rationale |
| Fix a bug | Cause + solution |
| Write docs | Core concepts |
| Finish session | Session summary |

**Rule**: Capture only durable, reusable knowledge not already represented; session summaries and one-off activity belong in the log, not notes.

## Step 1: Check Existing

Search first by concept, not just by filename — the same knowledge may live
under a different slug:

```bash
grep -rni "{keywords}" "{VAULT}/Projects/{TARGET}/notes/" && grep -i "{keywords}" "{VAULT}/Projects/{TARGET}/notes/index.md"
```

- **Concept already covered** (any slug): update that note and `updated`; record trustworthy verification metadata when available. Choose `{TOPIC}` only when no existing note covers the concept.
- **Exists & Conflict**: Append `## Conflict` section or create `{TOPIC}_conflict.md`
- **Not covered**: Create new note

## Step 2: Check Notation

Before writing, read [Note writing style](note-writing-style.md) and follow it: short sentences, active voice, one word per concept, explicit names, no session-context shorthand. The note must be readable without conversation context.

Before writing, check notation.md for existing variable definitions:

    cat {VAULT}/Projects/{TARGET}/notes/notation.md

**Rules**:
- If notation exists, use the same symbol and definition
- If new notation, add to notation.md first
- If existing notation is wrong, update notation.md AND all related notes

## Step 3: Create Note

### Template

    ---
    type: Project Knowledge
    title: {Topic Title}
    description: {One-sentence description}
    confidence: 0.8
    created: '{TIMESTAMP}'
    updated: '{TIMESTAMP}'
    validation_procedure: "How to verify"
    project: {TARGET}
    status: draft
    audience: {development|usage|both}
    usage_stale: false
    evidence: []
    ---

    # {Topic Title}
    
    ## Overview
    This note describes {brief description of the concept and its purpose}.
    
    ## Principles
    This concept follows these key principles:
    - {Principle 1 with explanation}
    - {Principle 2 with explanation}
    
    ## Details
    {Main content written in full sentences explaining the concept clearly. 
    Break into paragraphs for readability. Include examples where helpful.
    Use relative Markdown links such as [display text](./note_name.md) when referencing related concepts.}
    
    ## Variables
    The following variables are used in this note (see [Notation](./notation.md) for full definitions):
    
    | Symbol | Description | Units |
    |--------|-------------|-------|
    | `x` | The position of the object in space | meters (m) |
    
    ## Equations
    The fundamental equation for this concept is:
    
    $$
    E = mc^2
    $$
    
    In this equation, E represents the energy, m represents the mass, and c represents the speed of light.
    
    ## Workflow
    The following diagram shows the workflow for this process:
    
        ```mermaid
        flowchart TD
            A[Start: Initialize variables] --> B[Process: Apply equation]
            B --> C[End: Return result]
        ```
    
    ## Conventions
    When implementing this concept, follow these conventions:
    - {Convention 1}: {Explanation of why and how}
    
    ## Linked Concepts
    - [Related note](./related_note.md): {Brief explanation of how this note relates}
    - [Notation](./notation.md): Standard variable notations used in this note

### Principles

- **One Concept**: Each note covers ONE concept only
- **Self-Contained**: Understandable without external context
- **Full Sentences**: Use complete sentences, not just bullet points
- **Explicit Variables**: All variables, subscripts, superscripts documented
- **Equations**: Always use Markdown display math with `$$` delimiters for standalone equations. Do not leave raw LaTeX equation paragraphs without `$$`.
- **Workflows**: Use Mermaid diagrams for processes
- **Links**:
  - Use relative standard Markdown links: `[Note](./note_name.md)`
  - URL-encode spaces and preserve explicit heading fragments
  - Do not use Wikilinks, Obsidian embeds, or block references in Project Knowledge

## Step 4: Update the OKF Index

Add an entry under the appropriate heading in `{VAULT}/Projects/{TARGET}/notes/index.md`:

    ## Category
    * [{Topic Title}]({TOPIC}.md) - This note explains {brief description of what it covers}.

## Step 5: Update Daily Log

Append to `{VAULT}/Projects/{TARGET}/log/{TARGET}-{DATE}.md`:

    ## Session {N}
    - Created/Updated: [{TOPIC}](../notes/{TOPIC}.md) - {Brief description}
    - {Other activities}

Also ensure the Project log links to every note created or updated using a standard relative Markdown link.

When a session's claims depend on an exact code state (reproducible results,
behavior tied to uncommitted changes), append a Code state line for the session
(format in `notation.md`): repository directory, machine (`local` or
`user@host`), git HEAD, working-tree hash (`provenance` command), and jj
change id when colocated.

## Step 6: Validate and Refresh the Skill Pair

After review succeeds, change `status: draft` to `status: stable`. A newly detected stale fact remains `status: stable` with the real effective `stale_after: 'YYYY-MM-DD'`; deprecated knowledge uses `status: deprecated`. Never fabricate a stale date or `verified` actor.

Any change to a stable note's content, status, Audience Scope, or staleness can change a Skill Projection. Run `generate` and `validate` from `references/task_project_skills.md`. Both the authoritative `notes/` bundle and generated Skill Pair must pass; publication is atomic.

If the note was distilled from captured experience (Task 9), its `evidence:` frontmatter must list Project-root-relative paths into the motivating Evidence Pack (for example `evidence: [evidence/2026-09-02-debug-socket/evidence.md]`). `validate` fails a **stable** note whose evidence paths do not resolve; drafts may reference pending packs. Evidence packs themselves live outside `notes/`, are append-only, and never project into the Skill Pair.

When creating an Evidence Pack, record the code state it was produced under:
run the Projection CLI's `provenance` command in the source repo and paste its
`git_head:` / `worktree_tree:` lines into the pack's `MANIFEST.md` frontmatter.
`worktree_tree: clean` marks a clean checkout; a hash pins the exact dirty
tree (tracked + untracked, ignoring `.gitignore`). In a jj-colocated repo,
the current working-copy snapshot (`jj log -r @`) gives the same guarantee
with a stable change id.

## Step 7: Review

### Checklist

1. **Completeness**: All required sections present?
2. **Clarity**: Sentences complete and clear?
3. **Variables** (when present): All documented with units?
4. **Equations** (when present): Are all standalone equations wrapped with `$$` display-math delimiters?
5. **Links**: Do all relative Markdown links resolve to their intended concepts?
6. **Workflows** (when present): Mermaid diagrams syntactically correct?
7. **Metadata**: Does line-1 frontmatter contain `type`, a valid OKF status, and explicit Audience Scope?
8. **Index**: Is `notes/index.md` updated using its reserved OKF structure?
9. **Notation**: Consistent with notation.md?
10. **Projection**: Did the atomic Skill Pair regenerate and validate?

### Check Command

Run the Projection CLI's `validate` command from `references/task_project_skills.md`. It checks line-1 YAML, non-empty `type`, lifecycle values, the reserved `index.md`, portable links, provenance, and projection drift.

### If Issues Found

- Fix immediately before considering note complete
- If referenced note doesn't exist, create it or adjust link
- If notation inconsistent, update this note or notation.md + all related notes
