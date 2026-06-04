# Task: Initialize

Run this once per project or package to set up Kosmic.

## Find Vault Path

Determine the vault location in this order:

1. **Check AGENTS.md**: Look for `KOSMIC_VAULT:` or a Kosmic `Vault:` path
2. **Check Environment**: `KOSMIC_VAULT` environment variable
3. **Default**: Use `./memnotes`

Ask the user only when multiple plausible vaults or targets exist.

**Store**: Record in AGENTS.md:
```markdown
### Configuration
- **Vault**: {VAULT_PATH}
- **Target**: {TARGET}
```

## Determine Context

- **Single Project**: Target = `basename $PWD`
- **Multi-Package**: Target = specific package name (ask user if needed)

## Create Structure

Create the following:

```
{VAULT}/Projects/{TARGET}/
├── ProjectEntry.md
├── notes/
│   ├── TOC.md
│   └── notation.md
├── specs/
│   ├── INDEX.md
│   ├── research/
│   ├── quick-tasks/
│   ├── epics/
│   └── stories/
└── log/
```

### ProjectEntry.md

```markdown
# {TARGET}

## Overview
{Brief description of the project}

## Tech Stack
- {Technology 1}
- {Technology 2}

## Directory structure
{Project directory}
├── README.md 
├── {dir 1} : {short description to dir 1}
│   └──{file 1}
....

## Knowledge Base
- [[notes/TOC|Table of Contents]]
- [[notes/notation|Notation Reference]]

## Recent Activity
- [[log/{TARGET}-{DATE}|Latest Session]]
```

### TOC.md

```markdown
# Table of Contents

## Overview
{Add categories as notes are created}

## Reference
- [[notation]] - Standard variable notations and symbols.
```

### notation.md

```markdown
# Notation

This file defines the standard notations used across all atomic notes.

## Mathematical Symbols

| Symbol | Description | Units | First Used In |
|--------|-------------|-------|---------------|

## Subscripts

| Subscript | Meaning | Example |
|-----------|---------|---------|

## Superscripts

| Superscript | Meaning | Example |
|-------------|---------|---------|

## Conventions

- Use Greek letters for angles: α, β, γ, θ, φ
- Use uppercase for matrices: A, B, M
- Use lowercase for scalars: x, y, z, t
- Use bold for vectors: **v**, **F**

## Notes

When adding new notation:
1. Check this file first to ensure consistency
2. If notation already exists, use the same definition
3. If new notation is needed, add it here before using in notes
4. If changing existing notation, update ALL related notes
```

## Commands

```bash
TARGET="my_project"
VAULT="./memnotes"

# Create directories
mkdir -p "$VAULT/Projects/$TARGET/notes"
mkdir -p "$VAULT/Projects/$TARGET/log"
mkdir -p "$VAULT/Projects/$TARGET/specs/research"
mkdir -p "$VAULT/Projects/$TARGET/specs/quick-tasks"
mkdir -p "$VAULT/Projects/$TARGET/specs/epics"
mkdir -p "$VAULT/Projects/$TARGET/specs/stories"

# Create files (use write tool with templates above)
```

Create `{VAULT}/Projects/{TARGET}/specs/INDEX.md` from `references/templates/template-specs-index.md`.

## Update AGENTS.md

Add Kosmic integration section to the project's AGENTS.md.

**Template**: Use `references/agents_template.md`

**Process**:
1. Check if AGENTS.md exists in project root
2. Check if "## Kosmic Integration" section already exists
3. If not, append the template content to AGENTS.md
4. Replace placeholders:
   - `{KOSMIC_VAULT}` → actual vault path
   - `{TARGET}` → current target name

**If AGENTS.md doesn't exist**: Create it with the Kosmic integration section

**Note**: The template uses `##` as the top-level header to fit as a section within existing AGENTS.md.
