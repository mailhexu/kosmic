# Kosmic docs

This directory documents Kosmic's Markdown workflows, deterministic Projection CLI, and per-Project Usage and Development Skill Pair.

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

Kosmic creates or uses a Markdown vault, defaults to `./memnotes`, assigns an immutable Project Identifier, and keeps one authoritative Obsidian-compatible OKF v0.2 knowledge bundle plus generated skills under:

```text
{VAULT}/Projects/{TARGET}/
├── ProjectEntry.md
├── notes/                 # index.md + line-1 YAML concept notes
├── log/
├── specs/                 # shared Quick Tasks/proposals
├── subprojects/{ID}/specs/ # feature hierarchy returned by spec-create
└── skills/
    ├── {PROJECT_ID}-usage/
    └── {PROJECT_ID}-development/
```

For normal work, use this loop:

1. **Search** existing notes/specs before acting.
2. **Plan** with a quick task or full spec depending on risk.
3. **Implement** with tests/checks before code whenever possible.
4. **Review** before marking work done.
5. **Capture** a reusable finding in an existing or new atomic note when one emerged; keep dataset-only context beside its data.
6. **Project** stable notes through the atomic Skill Pair and run the Consumer Interface completion gate when applicable.

See [../skills/README.md](../skills/README.md) for the full task list.

The [skill routing table](../skills/SKILL.md#tasks) selects the branch reference.
Before recording observations or completing a Story/Quick Task, load
[Receipt completion](../skills/references/work_completion.md): exact checklist
coverage, record-embedded observations and independent review, computed review
revision, scope claims and a successful record-byte-bound receipt define completion.
Work in an isolated writer and integrate only baseline-checked owned deltas;
installed skills have a separate publication/installation gate.
