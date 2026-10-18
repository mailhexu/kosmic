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
    created: '{UTC_TIMESTAMP_OR_DATE}'
    updated: '{UTC_TIMESTAMP_OR_DATE}'
    skill_candidate: {true|false}
    skill_resources: []
    project: {TARGET}
    status: draft
    audience: {development|usage|both}
    ---

    # {Topic Title}

    ## Current Takeaway
    {The supported current conclusion, stated first. Superseded readings are
    labeled below, never deleted.}

    ## Overview
    This note describes {the concept and its purpose}.

    ## Assumptions and Conditions
    {Where this holds; where it does not; known uncertainty.}

    ## Details
    {Content written in full sentences explaining the concept clearly.
    Include examples where helpful. Use relative Markdown links such as
    [display text](./note_name.md) when referencing related concepts.}

    ## Sources
    - [{Reproducibility source}](https://...): {what it shows}

    ## Linked Concepts
    - [Related note](./related_note.md): {How this note relates}
    - [Notation](./notation.md): {Standard variable definitions used}

### Curation Metadata (required on creation)

New notes emit exactly:

- `skill_candidate`: `true` only when you judge at creation that the note is
  suitable to evolve into skill material; otherwise `false`. The default is
  `false`. Candidacy never forces a skill proposal, and an explicit
  no-proposal outcome is valid.
- `skill_resources`: `[]` until an approved skill actually publishes (or
  removes) a use of this note; then list the stable skill-topic ids. It is
  never a wish list. A note may be in use and still `skill_candidate: true`;
  the two fields are independent.

Legacy notes without the fields stay valid: readers treat missing
`skill_candidate` as `false` and missing `skill_resources` as `[]`. Never
bulk-rewrite legacy frontmatter.

**Timestamp bump rule**: setting `skill_candidate` false→true, or clearing it
for reassessment, is a semantic change — bump `updated` with a real UTC
instant so the note enters the next curation window. Syncing
`skill_resources` after approved publication/removal, and any check- or
bookkeeping-only write, never bumps `updated`.

**Timestamps**: `created`/`updated` take a real UTC instant
(`YYYY-MM-DDTHH:MM:SS[.ffffff]Z`) or, for legacy values, a date
(`YYYY-MM-DD`). Never invent or round a past instant.

### Principles

- **One Concept**: Each note covers ONE concept only
- **Current Truth First**: The supported current conclusion opens the note; superseded readings stay labeled, never deleted
- **Self-Contained**: Assumptions, conditions, uncertainty, and sources are present or explicitly bounded; no external context required
- **No Length Cap, No Confidence Scores**: Note length is unbounded; confidence metadata is banned
- **Full Sentences**: Use complete sentences, not just bullet points
- **Links**:
  - Use relative standard Markdown links: `[Note](./note_name.md)`
  - URL-encode spaces and preserve explicit heading fragments
  - Do not use Wikilinks, Obsidian embeds, or block references in Project Knowledge
  - Record reproducibility as ungated `sources:` links in the note body; an old `evidence: []` frontmatter value stays valid

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

Reproducibility links are ungated `sources:` links in the note body (see the
template). A stable note is never rejected for missing `evidence:` metadata;
existing notes that carry `evidence:` values keep them valid, and the
`validate` command still resolves those legacy paths. Evidence packs
themselves are a legacy mechanism: no new pack, sidecar, or distillation is
required for a note, and criterion-specific observations belong compactly in
the existing work record.

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
8. **Curation fields**: Are `skill_candidate` and `skill_resources` emitted with their declared shapes (boolean / list of stable ids), and was the timestamp bump rule applied if candidacy changed?
9. **Index**: Is `notes/index.md` updated using its reserved OKF structure?
10. **Notation**: Consistent with notation.md?
11. **Projection**: Did the atomic Skill Pair regenerate and validate?

### Check Command

Run the Projection CLI's `validate` command from `references/task_project_skills.md`. It checks line-1 YAML, non-empty `type`, lifecycle values, the reserved `index.md`, portable links, provenance, and projection drift.

### If Issues Found

- Fix immediately before considering note complete
- If referenced note doesn't exist, create it or adjust link
- If notation inconsistent, update this note or notation.md + all related notes
