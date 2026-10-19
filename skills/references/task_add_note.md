# Task: Add Note

Create or update atomic notes, and log daily progress.

Before durable note/log edits, use the current compatible governing record and declared shared-note scope, or establish a standalone low-risk Quick Task and obtain approval. Reading existing knowledge is record-free; finding useful knowledge does not silently authorize publication. Preserve pre-dirty work and follow SKILL.md Record-first authority.

## Batched Episode Completion

When an authorized episode ends, batch its knowledge notes, daily-log entries, and publication completion into one pass, with one appropriate canonical refresh for the batch (for example, one Skill Pair regeneration covering every changed note). An actual change to an already-published note source — content, status, Audience Scope, or staleness — still counts as a change and refreshes. Nothing here forces a note, proposal, or publication: an episode that produced no durable knowledge legitimately closes with none. Optional curation and skill proposals stay off the critical path unless correctness requires immediate action, and dataset-only metadata stays embedded in or adjacent to its dataset per the Locality rule (ADR-A).

## When to Use This Task

Consider adding a note only when durable, reusable knowledge was found. No
activity mandates a note. Examples of what *may* qualify, only if the knowledge
is durable and reusable and not already represented:

- Reading source code: an algorithm or pattern reusable beyond this session.
- Making a decision: the decision plus its rationale, reusable later.
- Fixing a bug: a cause-and-solution insight reusable beyond this instance.
- Writing docs: a core concept reusable by other readers.

The same activities often produce nothing reusable — then add no note. Capture
session summaries and one-off activity in the log, not notes. Producing no new
knowledge is a valid outcome; never manufacture a note to close a session.

## Step 1: Check Existing

Search first by concept, not just by filename — the same knowledge may live
under a different slug:

```bash
grep -rni "{keywords}" "{VAULT}/Projects/{TARGET}/notes/" && grep -i "{keywords}" "{VAULT}/Projects/{TARGET}/notes/index.md"
```

- **Concept already covered** (any slug): update that note and `updated`; record trustworthy verification metadata when available. Choose `{TOPIC}` only when no existing note covers the concept.
- **Exists & Substance Conflict**: Evolve the existing note by substance, never
  by appending a parallel section or creating a `{TOPIC}_conflict.md`
  duplicate. See [Evolution](#evolution-of-existing-notes) below.
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
    created: '{REAL_CURRENT_UTC_INSTANT}'
    updated: '{REAL_CURRENT_UTC_INSTANT}'
    skill_candidate: false
    skill_resources: []
    artifact_role: knowledge
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
bookkeeping-only write, never bumps `updated`. Nominating a note toward
skill material is optional: the separate curation routine
(`references/curation_routine.md`) may nominate it between runs; nothing
schedules this automatically, and candidacy never forces a proposal.

**Timestamps**: `created`/`updated` take a real UTC instant
(`YYYY-MM-DDTHH:MM:SS[.ffffff]Z`). For a new note, both fields carry the same
real current UTC instant captured at edit time; never write a date-only value
in a fresh note and never invent or round a past instant. Date-only values are
legacy input only: an existing note may keep its historical `YYYY-MM-DD`
values, which read as valid without any rewrite.

**Artifact role**: `artifact_role: knowledge` is the emitted baseline for a
Project Knowledge note. Choose a different existing role only when the note
actually fills that role, and then meet that role's requirements. No new role
values are introduced.

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

## Locality (ADR-A)

Placement is audience-keyed, not path-keyed. Documentation that supports only
one dataset — metadata, units, run settings, schemas, calibration, and
single-dataset interpretation — stays embedded in or adjacent to that dataset
in its native data repository, including a dataset living entirely outside the
memnotes vault. No central pointer stub, per-dataset note, or registry entry is
created or required for it, and no machine scanner classifies placement:
misplacement is caught only by bounded human content review. An independently
reusable insight demonstrated on a dataset — including a qualified negative or
provisional result — is extracted into a concept-named note with precise
source and reproducibility links; the native dataset is never flattened into
Markdown, moved, or destroyed.

## Evolution of Existing Notes

When a note's substance is wrong, superseded, split, or duplicated, evolve the
note itself. Never append a parallel `## Conflict` section, never create a
`{TOPIC}_conflict.md` duplicate, and never introduce a redirect or alias note.

- **Correct / retract**: state the supported current conclusion first; keep the
  superseded interpretation prominently labeled below, never deleted. Preserve
  the failure explanation, the differing settings and conditions that led to
  the wrong reading, and any negative findings — they are content, not noise.
- **Refine**: update the current takeaway in place and bump `updated` with the
  real current UTC instant.
- **Merge** (two notes, one concept): combine the content of both notes into
  a substantively chosen surviving note so the result is one coherent
  current-truth-first note in which
  differing settings, uncertainty, and negative findings all survive. Repair
  every incoming and `index.md` link to either old slug so it resolves to the
  surviving note. One note survives; no redirect or alias file remains.
- **Split** (one note, independently maintainable aspects): create
  self-contained notes, each with its own frontmatter and links; replace the
  duplicated content with cross-references; repair incoming and `index.md`
  links.
- **Deprecate**: set `status: deprecated` when the knowledge no longer holds.
  Keep the note readable in place, and link to its successor note when one
  exists. Never create a new alias or redirect-only note for it.
- **Choosing a merge survivor**: pick the survivor by substantive concept
  coherence — which existing note can hold the combined current truth,
  conditions, and negative findings most coherently — never by older or newer
  timestamp.

**Timestamps and status are never a scientific verdict**: a newer `updated`,
`created`, or a higher status never resolves a conflicting claim between two
notes — only substantive content does. Do not "win" a conflict by stamping a
newer timestamp or promoting status.

**Gate**: promoting `draft` to `stable` (Step 6) requires substantive human
review of the content; checks, formatting, and timestamps never substitute
for it. Merge, split, and retraction edits need bounded substantive content
review under the existing governing record — not an additional approval gate.

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

After a substantive human review of the content — a reviewer reading the note
and judging its conclusions correct — change `status: draft` to `status:
stable`. Passing checks, tests, or elapsed time never promote a note; only
this explicit human substantive review does. A newly detected stale fact remains `status: stable` with the real effective `stale_after: 'YYYY-MM-DD'`; deprecated knowledge uses `status: deprecated`. Never fabricate a stale date or `verified` actor.

Any change to a stable note's content, status, Audience Scope, or staleness can change a Skill Projection. Run `generate` and `validate` from `references/task_project_skills.md`. Both the authoritative `notes/` bundle and generated Skill Pair must pass; publication is atomic.

Reproducibility links are ungated `sources:` links in the note body (see the
template). A stable note is never rejected for missing `evidence:` metadata;
existing notes that carry `evidence:` values keep them valid, and the
`validate` command still resolves those legacy paths. Evidence packs
themselves are a retired mechanism (knowledge-first notes per
`docs/adr/0004-knowledge-first-notes.md`): no new pack, sidecar, or
distillation is required for a note, and criterion-specific observations
belong compactly in the existing work record. Legacy `evidence:` values
remain valid historical metadata; current commands neither require nor bless
them.

Record the code state a note's conclusion was produced under when the
conclusion depends on it: run the Projection CLI's `provenance` command in
the source repo and cite its `git_head:` / `worktree_tree:` values in the
note's source links. `worktree_tree: clean` marks a clean checkout; a hash
pins the exact dirty tree (tracked + untracked, ignoring `.gitignore`). In a
jj-colocated repo, the current working-copy snapshot (`jj log -r @`) gives
the same guarantee with a stable change id.

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
