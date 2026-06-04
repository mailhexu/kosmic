# Task: Search

**MANDATORY: Run BEFORE** implementing features, making changes, or when unsure.

Find existing knowledge and specs before implementing new features.

## Strategy

1. **Quick**: Search TOC first
2. **Deep**: If not found, search all notes
3. **Specs**: Also search specs for existing PRDs, architecture, epics, stories

## 1. Search TOC

TOC can be long, use grep instead of reading entire file:

```bash
# Search TOC for keywords (case-insensitive)
grep -i "keyword\|another_keyword" {VAULT}/Projects/{TARGET}/notes/TOC.md

# Example: search for "interface" and "batch"
grep -i "interface\|batch" {VAULT}/Projects/{TARGET}/notes/TOC.md

# List all categories
grep "^## " {VAULT}/Projects/{TARGET}/notes/TOC.md
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

# Stale notes
git grep "usage_stale: true" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Recently created
git grep "created: 2025-02" -- "{VAULT}/Projects/{TARGET}/notes/*.md"
```

## Workflow

```
1. grep -i "keywords" TOC.md
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
