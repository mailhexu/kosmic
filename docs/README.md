# Kosmic docs

This directory contains user-facing Markdown documentation for installing and using Kosmic.

## Start here

- [Installation](installation.md) - install Kosmic either by asking an AI agent to do it or by copying the skill files manually.
- [Skill reference](../skills/README.md) - complete task catalogue, directory layout, and daily workflow.
- [Skill rules](../skills/SKILL.md) - the executable Markdown skill definition used by AI agents.

## Basic usage

After installation, load or invoke the skill using your agent's normal mechanism. In OpenCode:

```text
/skill kosmic
```

If your agent does not support named skills, add `skills/SKILL.md` to its persistent instructions and keep `skills/README.md` plus `skills/references/` available in the project.

Then initialize Kosmic once per project:

```text
Task 1: Initialize
```

Kosmic will create or use a Markdown vault, defaulting to `./memnotes`, and organize project knowledge under:

```text
{VAULT}/Projects/{TARGET}/
├── ProjectEntry.md
├── notes/
├── log/
└── specs/
```

For normal work, use this loop:

1. **Search** existing notes/specs before acting.
2. **Plan** with a quick task or full spec depending on risk.
3. **Implement** with tests/checks before code whenever possible.
4. **Review** before marking work done.
5. **Capture** durable knowledge as atomic notes.

See [../skills/README.md](../skills/README.md) for the full task list.
