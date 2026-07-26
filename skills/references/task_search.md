# Task: Search

**MANDATORY: Run BEFORE** implementing features, making changes, or when unsure.

Find existing knowledge and specs before implementing new features.

## Load the Audience Skill First

- Contributor search: load `{PROJECT_ID}-development`; follow its required `{PROJECT_ID}-usage` reference for shared and consumer-facing behavior.
- Consumer-only search: load `{PROJECT_ID}-usage` directly and do not enter implementation workflow.
- If either canonical projection is missing or stale, stop and run the validation or migration procedure in `references/task_project_skills.md`.

## Strategy

1. **Quick**: Search the OKF index first
2. **Deep**: If not found, search all notes
3. **Specs**: Also search specs for existing PRDs, architecture, epics, stories

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

Use `git grep` (faster in git repos):

```bash
# Search all notes
git grep -i "query" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# With line numbers
git grep -ni "keyword" -- "{VAULT}/Projects/{TARGET}/notes/"

# Search by tag
git grep "tags:.*api" -- "{VAULT}/Projects/{TARGET}/notes/"

# Search for file references
git grep "related_files:.*auth.ts" -- "{VAULT}/Projects/{TARGET}/notes/"

# Cross-project search
git grep -i "keyword" -- "{VAULT}/Projects/*/notes/*.md"

# Search notation
git grep "symbol.*x" -- "{VAULT}/Projects/{TARGET}/notes/notation.md"
```

## 3. Search Specs

**Always check specs before creating new ones or implementing features.**

```bash
# Search all specs (PRD, architecture, epics, stories)
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/specs/"

# Search only stories
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/specs/stories/"

# Find stories by status
git grep "status: approved" -- "{VAULT}/Projects/{TARGET}/specs/stories/"
git grep "status: in_progress" -- "{VAULT}/Projects/{TARGET}/specs/stories/"

# Find epics
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/specs/epics/"

# Check if a PRD already covers this feature
git grep -i "keyword" -- "{VAULT}/Projects/{TARGET}/specs/prd.md"
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
3. git grep -i "keywords" specs/
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
