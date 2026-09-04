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

## Determine Project Boundary and Identity

- **Single Project**: Target = configured vault folder or the current package name.
- **Multi-Package**: Each independently managed package is a Project with its own vault folder and Skill Pair.
- Assign an explicit immutable, globally unique lowercase slug as `{PROJECT_ID}` (for example, `acme-billing-api`).
- Check sibling vault Projects and installed skills for collisions before recording the identifier.
- Skill names are `{PROJECT_ID}-usage` and `{PROJECT_ID}-development`.

## Verify Required Procedure Skills

Before creating or migrating a Project, verify the active Install Adapter:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py check-required-skills --adapter {opencode|claude-code|codex}
```

Missing skills or an unsupported adapter stop initialization. Follow the required-procedure-skills section of the installed `README.md`; do not substitute persistent instructions or a native fallback.

## Create Structure

Create the following:

```
{VAULT}/Projects/{TARGET}/
├── ProjectEntry.md
├── notes/                       # Obsidian-compatible OKF v0.2 bundle
│   ├── index.md
│   └── notation.md
├── specs/
│   ├── INDEX.md
│   ├── research/
│   ├── quick-tasks/
│   ├── epics/
│   └── stories/
├── log/
└── skills/                       # generated atomically after real notes exist
    ├── {PROJECT_ID}-usage/
    └── {PROJECT_ID}-development/
```

### ProjectEntry.md

```markdown
---
project_id: {PROJECT_ID}
working_state: working-tree
---

# {TARGET}

## Overview
{Brief description of the Project}

## Tech Stack
- {Technology 1}
- {Technology 2}

## Directory structure
{Project directory}
├── README.md
├── {dir 1}: {short description}
│   └── {file 1}

## Knowledge Base
- [Project Knowledge index](notes/index.md)
- [Notation Reference](notes/notation.md)

## Project Skills
- Usage: `skills/{PROJECT_ID}-usage/`
- Development: `skills/{PROJECT_ID}-development/`

## Recent Activity
- [Latest Session](log/{TARGET}-{DATE}.md)
```

### index.md

```markdown
---
okf_version: "0.2"
---

# Project Knowledge

## Reference
* [Notation](notation.md) - Standard variable notations and symbols.
```

### notation.md

```markdown
---
type: Project Notation
title: Project Notation
status: draft
audience: both
tags: [notation]
---

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

## Seed Real Projection-Eligible Knowledge

Before publishing skills, inspect the Project and create:

1. At least one stable note with `audience: usage` or `audience: both` describing a real Consumer task through a supported Consumer Interface.
2. At least one stable note with `audience: development` describing real Contributor workflow or conventions.

Do not mark identity-only, placeholder, inferred, or unverified guidance `stable` merely to satisfy publication.

Every concept under `notes/` must start on line 1 with YAML frontmatter, declare a non-empty `type`, use `status: draft | stable | deprecated`, and use relative standard Markdown links. Keep Project workflow logs in the sibling `log/` directory; `log.md` is reserved by OKF.

## Initialize and Publish the Skill Pair

Resolve the Projection CLI from the installed Kosmic skill directory, then run:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py init \
  --project "{VAULT}/Projects/{TARGET}" \
  --project-id "{PROJECT_ID}"
```

Initialization succeeds only after it validates and atomically publishes exactly `{PROJECT_ID}-usage` and `{PROJECT_ID}-development`. A failure leaves no partial pair.

## Update Project Instructions

Add the Kosmic integration section to the Project's persistent instructions.

**Template**: Use `references/agents_template.md`

**Process**:
1. Check whether the Project instruction file exists.
2. Check whether a Kosmic Integration section already exists.
3. Add or update the section from the template.
4. Replace placeholders:
   - `{KOSMIC_VAULT}` → actual vault path
   - `{TARGET}` → current vault Project folder
   - `{PROJECT_ID}` → immutable Project Identifier
   - `{USAGE_SKILL}` → `{PROJECT_ID}-usage`
   - `{DEVELOPMENT_SKILL}` → `{PROJECT_ID}-development`
5. Install the atomic pair through the selected adapter, or install persistent pointers for an agent without named skills.

If no Project instruction file exists, create it with the Kosmic integration section.
