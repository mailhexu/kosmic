# Task: Search

**MANDATORY: Run BEFORE** implementing features, making changes, or when unsure.

Find existing knowledge and specs before implementing new features.

## Bootstrap First, Then Load the Audience Skill

- Before routing, check the bootstrap prerequisites: the Project's immutable `project_id`, its canonical projections (`{PROJECT_ID}-usage` and `{PROJECT_ID}-development`), and, when searching through the shared library, its installed router/library state.
- If any identity, canonical projection, or library artifact is absent or stale, stop routing and run the validation or migration procedure in `references/task_project_skills.md` directly — this is a one-time bootstrap exception and must not re-enter Task Search or any audience-skill routing (no recursion). Resume Step 1 below once the bootstrap completes.
- Contributor search: load `{PROJECT_ID}-development`; follow its required `{PROJECT_ID}-usage` reference for shared and consumer-facing behavior.
- Consumer-only search: load `{PROJECT_ID}-usage` directly and do not enter implementation workflow.

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

# Cross-project search
grep -rni "keyword" "{VAULT}/Projects/*/notes/"

# Search notation
grep -n "symbol.*x" "{VAULT}/Projects/{TARGET}/notes/notation.md"
```

Only when the vault is verified to be a tracked directory inside the current
git repository may `git grep` be used as a faster equivalent.

## 3. Search Specs

**Always check specs before creating new ones or implementing features.**

Feature specs live in per-subproject owner roots; Quick Tasks and proposals
are shared at the Project root.

```bash
# Search all specs across subprojects (PRD, architecture, epics, stories, research)
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/subprojects/*/specs/"

# Search only stories
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/subprojects/*/specs/stories/"

# Find stories by status
git grep "status: approved" -- "{VAULT}/Projects/{TARGET}/subprojects/*/specs/stories/"
git grep "status: in_progress" -- "{VAULT}/Projects/{TARGET}/subprojects/*/specs/stories/"

# Find epics
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/subprojects/*/specs/epics/"

# Check whether a PRD already covers this feature
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/subprojects/*/specs/prd.md"

# Search shared quick tasks
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/specs/quick-tasks/"
```

## 4. Search by Metadata

```bash
# Low confidence notes
git grep "confidence: 0\.[0-5]" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Draft notes
git grep "status: draft" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Stale or Usage-stale notes
git grep -E "stale_after:|usage_stale: true" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Recently created
git grep "created: 2025-02" -- "{VAULT}/Projects/{TARGET}/notes/*.md"
```

## Workflow

```
1. grep -i "keywords" index.md
   ↓ Found?
   → Read specific note(s)
   ↓ Not found?
2. git grep -i "keywords" notes/
   ↓ Found?
   → Read matching notes
   ↓ Not found?
3. git grep -i "keywords" subprojects/*/specs/ specs/quick-tasks/
   ↓ Found?
   → Read matching specs (avoid duplicating existing work)
   ↓ Not found?
4. Knowledge doesn't exist yet - create new note or spec
```

## Why git grep?

- Faster on large repositories
- Respects `.gitignore`
- Better formatted output
- Works with relative paths
