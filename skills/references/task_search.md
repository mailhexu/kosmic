# Task: Search

**MANDATORY: Run BEFORE** implementing features, making changes, or when unsure.

Find existing knowledge and specs before implementing new features.

## Direct Inspection or Operational Routing

- Direct read-only questions search authoritative notes/specs at their configured paths. Missing/stale generated skills, identity or router do not require bootstrap, migration, installation or repair to read these files; report relevant limitations. If the Project is absent, report no recorded knowledge rather than initializing it.
- Before loading generated Contributor/Consumer guidance or using the shared router, resolve the required Project identity, Skill Pair and library state through the entry process in `SKILL.md`. Missing/stale prerequisites stop that operation; this read-only path authorizes no execution or mutation.
- Contributor work loads `{PROJECT_ID}-development` and its required Usage companion; Consumer operations load `{PROJECT_ID}-usage`. Reuse already loaded guidance while its inputs are unchanged.

## Strategy

1. **Math authority**: Search `mathdocs/index.md` first when equations, symbols, or formula-derived implementation are involved
2. **Quick**: Search the OKF notes index
3. **Deep**: Search all notes by concept, then filename
4. **Specs**: Also search specs for existing PRDs, architecture, epics, stories

## 1. Search the Knowledge Index

`index.md` is the OKF progressive-disclosure entry point. Search it before opening concepts:

```bash
# Search the index for keywords (case-insensitive)
grep -i "keyword\|another_keyword" {VAULT}/Projects/{TARGET}/notes/index.md

# Example: search for "interface" and "batch"
grep -i "interface\|batch" {VAULT}/Projects/{TARGET}/notes/index.md

# List all categories
grep "^# " {VAULT}/Projects/{TARGET}/notes/index.md
```

## 2. Deep Search (Notes)

Search the vault filesystem directly — the vault may live outside any git
repository, and git-index search misses untracked or ignored notes:

```bash
# Search all notes (recursive, index-independent)
grep -rni "query" "{VAULT}/Projects/{TARGET}/notes/"

# Search by tag
grep -rn "tags:.*api" "{VAULT}/Projects/{TARGET}/notes/"

# Search for file references
grep -rn "related_files:.*auth.ts" "{VAULT}/Projects/{TARGET}/notes/"

# Cross-project search, only when requested or needed for the question
grep -rni "keyword" "{VAULT}/Projects/"*/notes/

# Search notation
grep -n "symbol.*x" "{VAULT}/Projects/{TARGET}/notes/notation.md"
```

Use the agent's filesystem search tool when available, including untracked
and ignored vault files (disable ignore filtering). The shell examples are
index-independent fallbacks; no Git-tracking probe is needed.

## 3. Search Specs

**Always check specs before creating new ones or implementing features.**

Feature specs live in per-subproject owner roots; Quick Tasks and proposals
are shared at the Project root.

Search only existing owner/shared spec roots; absent roots mean no records
there, not a reason to create them. For example:

```bash
# Feature specs, including research, inside an existing subprojects directory
grep -rni "keyword" "{VAULT}/Projects/{TARGET}/subprojects/"

# Shared Quick Tasks/proposals inside an existing specs directory
grep -rni "keyword" "{VAULT}/Projects/{TARGET}/specs/"

# Narrow an existing owner root by record status
grep -rnE "status:.*(approved|in_progress)" "{SPEC_ROOT}/"
```

## 4. Search by Metadata

```bash
# Low confidence, draft, or stale notes; untracked/ignored notes are included
grep -rnE "confidence: 0\\.[0-5]|status: draft|stale_after:|usage_stale: true" \
  "{VAULT}/Projects/{TARGET}/notes/"
```

## Workflow

1. Search `notes/index.md` and read relevant notes.
2. If the answer is incomplete, search the notes filesystem by concept, filename or metadata.
3. Check relevant specs before creating a record or implementing a feature, even if a note answered the knowledge question.
4. Stop when the requested question and required scope checks are answered. Reuse these results within the unchanged episode; widen only for an unresolved question.

A search miss authorizes no write. Create a note/spec only under its own task and authority; read-only sessions may finish without notes, logs or index updates.
