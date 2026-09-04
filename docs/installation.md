# Installing Kosmic

Kosmic is distributed as Markdown workflows plus a deterministic Python 3.11+ Projection CLI. Install the entire `skills/` directory wherever your agent loads custom skills, reusable instructions, or persistent project workflows.

The orchestrator skill name is `kosmic`. After Project initialization, Kosmic generates one `{project}-usage` and one `{project}-development` skill under the Project vault. In OpenCode, load the orchestrator with:

```text
/skill kosmic
```

## Runtime requirement

The Projection CLI requires Python 3.11 or newer and uses only the standard library:

```bash
python3 --version
python3 skills/scripts/kosmic_project_skills.py --help
```

## Required procedure skills

Kosmic requires independently installed Matt Pocock skills: `tdd`, `code-review`, `diagnosing-bugs`, `research`, `domain-modeling`, `codebase-design`, `grill-with-docs`, `grilling`, and `prototype`. Kosmic does not vendor them and supports only the global named-skill locations for OpenCode, Claude Code, and Codex.

Install the reviewed upstream `mattpocock/skills` revision globally through its standalone named-skill installer. Do not use the managed Claude plugin or a project-local installation: those layouts are intentionally unsupported by Kosmic's deterministic verifier. Record the exact upstream revision in a Kosmic release and review compatibility before any update.

After installation, verify from the installed Kosmic skill directory:

```bash
python3 scripts/kosmic_project_skills.py check-required-skills --adapter opencode
python3 scripts/kosmic_project_skills.py check-required-skills --adapter claude-code
python3 scripts/kosmic_project_skills.py check-required-skills --adapter codex
```

Then smoke-load `kosmic` and one required skill through the adapter's native interaction. The check uses each adapter's global skill location and reports every missing skill. An unsupported adapter or an incomplete set blocks Kosmic initialization and Contributor workflows.

## Option 1: Install with an AI agent

Use this when you are already working inside an AI coding agent such as Claude Code, Codex, OpenCode, or another agent that supports persistent instructions. Paste the following prompt into the agent from the root of this repository:

```text
Install the Kosmic skill from this repository.

Requirements:
1. Treat `./skills` as the source skill directory. It contains `SKILL.md`, `README.md`, `references/`, and `scripts/`.
2. Install it as a skill named `kosmic` in the current AI agent's custom skill directory.
   - For OpenCode, use `~/.config/opencode/skill/kosmic/` unless this environment has another configured path.
   - For Claude Code, Codex, or another agent, detect its user-skill or persistent-instruction convention.
3. Preserve the full directory structure, especially `references/`, `references/templates/`, and `scripts/`.
4. Verify Python 3.11+ and run `python3 scripts/kosmic_project_skills.py --help` from the installed skill directory.
5. Do not modify the source repository except to report what you did.
6. Verify that the installed directory contains `SKILL.md`, `README.md`, `references/`, and `scripts/`.
7. Tell me the exact install path and how to load or invoke `kosmic`.
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
scripts/
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
├── scripts/
│   └── kosmic_project_skills.py
└── references/
    ├── agents_template.md
    ├── task_init.md
    ├── task_search.md
    ├── task_add_note.md
    ├── task_project_skills.md
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
- **Target**: `{vault-project-folder}`
- **Project ID**: `{immutable-project-id}`
- **Usage Skill**: `{immutable-project-id}-usage`
- **Development Skill**: `{immutable-project-id}-development`

The initialized vault structure is:

```text
{VAULT}/Projects/{TARGET}/
├── ProjectEntry.md
├── notes/                       # Obsidian-compatible OKF v0.2 bundle
│   ├── index.md
│   └── notation.md
├── specs/
├── log/
└── skills/
    ├── {PROJECT_ID}-usage/
    └── {PROJECT_ID}-development/
```

Initialization validates line-1 frontmatter, OKF lifecycle values, the reserved index, and portable links; it then requires real stable Contributor and Consumer notes before atomically publishing the pair. Existing Projects use Task 8: Migrate Project Skills; migration is transactional, and Unscoped Knowledge remains Development-only until reviewed.

## Updating Kosmic

To update an existing installation, replace the installed `kosmic` skill directory with the current repository's `skills/` contents, preserving any project vaults such as `memnotes/`. The vault is project data; it is not part of the installed skill.
