# Installing Kosmic

Kosmic is distributed as a Markdown-based AI-agent skill/workflow. The install target is the `skills/` directory in this repository, copied into the place where your agent loads custom skills, reusable instructions, or persistent project workflows.

The canonical skill name is `kosmic`. Agents with named skills should expose it under that name. In OpenCode, load it with:

```text
/skill kosmic
```

## Option 1: Install with an AI agent

Use this when you are already working inside an AI coding agent such as Claude Code, Codex, OpenCode, or another agent that supports persistent instructions. Paste the following prompt into the agent from the root of this repository:

```text
Install the Kosmic skill from this repository.

Requirements:
1. Treat ./skills as the source skill directory. It contains SKILL.md, README.md, and references/.
2. Install it as a skill named kosmic in the current AI agent's custom skill directory.
   - For OpenCode, use ~/.config/opencode/skill/kosmic/ unless this environment has a different configured skill path.
   - For Claude Code, Codex, or another agent, detect the local convention for user skills or persistent project instructions and use the closest equivalent. If the agent does not support named skills, copy or reference the Markdown instructions from skills/SKILL.md and skills/README.md in the agent's persistent instruction mechanism.
3. Preserve the full directory structure under ./skills, especially references/ and references/templates/.
4. Do not modify the source repository except to report what you did.
5. After installing, verify that the installed directory contains SKILL.md, README.md, and references/.
6. Tell me the exact install path and how to load or invoke kosmic.
```

After the agent reports success, load or invoke `kosmic` using that agent's normal mechanism. In OpenCode, test with:

```text
/skill kosmic
```

Then initialize it in a project by asking the agent to run the Kosmic initialize task:

```text
Task 1: Initialize
```

## Option 2: Manual install for OpenCode

From the root of this repository:

```bash
mkdir -p ~/.config/opencode/skill/kosmic
cp -R skills/* ~/.config/opencode/skill/kosmic/
```

Verify the installed files:

```bash
ls ~/.config/opencode/skill/kosmic
```

You should see at least:

```text
SKILL.md
README.md
references/
```

Load the skill in OpenCode:

```text
/skill kosmic
```

## Option 3: Manual install for other agents

If your agent supports custom skills, copy the `skills/` directory into that agent's skill directory and name the installed skill `kosmic`.

The installed directory should keep this structure:

```text
kosmic/
├── SKILL.md
├── README.md
└── references/
    ├── agents_template.md
    ├── task_init.md
    ├── task_search.md
    ├── task_add_note.md
    ├── task_quick_task.md
    ├── task_research.md
    ├── task_create_spec.md
    ├── task_implement_story.md
    ├── task_review.md
    ├── task_review_spec.md
    └── templates/
```

If your agent does not support named skills, use the Markdown files as persistent instructions instead:

1. Add the contents of `skills/SKILL.md` to the agent's persistent instruction file or project instruction file.
2. Keep `skills/README.md` and `skills/references/` available in the project so the agent can read the task details and templates.
3. Tell the agent: "Use Kosmic from `skills/SKILL.md` before planning or implementing work."

## Project initialization

Installation only makes the skill available. Each project still needs a Kosmic vault.

Ask your agent to initialize Kosmic for the project. In OpenCode, one way is:

```text
/skill kosmic
Task 1: Initialize
```

Kosmic resolves the vault in this order:

1. Existing `AGENTS.md` entry (`KOSMIC_VAULT:` or a Kosmic `Vault:` path)
2. `KOSMIC_VAULT` environment variable
3. Default `./memnotes`

It then records the project integration in `AGENTS.md` using this shape:

```markdown
## Kosmic Integration

This project uses **Kosmic** for persistent memory and knowledge management.

### Configuration
- **Vault**: `./memnotes`
- **Target**: `{project-name}`
```

The initialized vault structure is:

```text
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

## Updating Kosmic

To update an existing installation, replace the installed `kosmic` skill directory with the current repository's `skills/` contents, preserving any project vaults such as `memnotes/`. The vault is project data; it is not part of the installed skill.
