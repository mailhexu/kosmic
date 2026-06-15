# kosmic

**Knowledge-Oriented, Spec-driven Infrastructure for Coding.**

Kosmic is a Markdown-based AI-agent skill/workflow that gives coding agents persistent project memory and a disciplined, spec-driven process. It is designed for scientific and engineering codebases where correctness depends on context that lives outside any single source file: project conventions, domain assumptions, validation practice, and the hard-won experience of existing developers.

## Why kosmic?

AI coding tools are good at producing code that compiles and runs. In scientific codebases, that is not enough: correctness often depends on conventions, assumptions, validation data, and domain knowledge that are not visible in one local code snippet.

When AI is asked to implement a large scientific change in one task, it may make plausible but wrong assumptions. The code can compile, run, and still produce an incorrect result. The same trap catches human developers too; it is just slower and less visible.

Two problems repeat across scientific software projects:

1. **Hidden conventions.** Correctness depends on knowledge that is implicit in the code, the physics, or the developers' experience.
2. **Too much context at once.** Even when the right information exists, a single large task overloads the context window (and human working memory), so essential assumptions slip through.

Kosmic addresses both by coupling a **spec-driven workflow** that decomposes large tasks with a **knowledge base** that captures and validates hidden conventions.

## The framework

![kosmic: a spec-driven workflow coupled to a Markdown knowledge base](assets/kosmic_workflow.png)

Two workflows run in parallel and reinforce each other:

- **The SPEC workflow** (top lane) turns a large, risky change into small, testable tasks: `PRD → Research → Architecture → Story → Tests + coding → Review`. Each stage produces an artifact the user approves before work continues.
- **The knowledge base** (bottom cylinder) is a Markdown / Obsidian vault of **atomic notes** — one concept per note — with explicit links, source files, validation status, and confidence levels.

The arrows tell the story:

- **Dashed arrows** are *queries*. PRD, Architecture, and Story stages pull facts and conventions from the knowledge base before deciding what to build.
- **Solid arrows** are *updates*. Research, Tests + coding, and Review feed new discoveries and validation results back into the vault.

The knowledge base is not a side artifact. It is what makes the next task safer than the first.

## Key principles

- **Research before coding.** Search the vault, read the relevant code, and write notes before implementation. No unjustified assumptions.
- **Decompose before implementing.** Break features into small stories, each with a clear goal, a bounded context, and an acceptance check.
- **Tests define the target.** For each story, write the checks first; AI output is accepted or rejected by evidence, not by whether it compiles.
- **Knowledge is atomic and validated.** One concept per note. Every note carries a status (`draft`, `validated`, `stale`, `deprecated`) and is updated when implementation or review changes what is true.
- **Mandatory review.** No story is marked `done` without code review. AI proposals are first-class input, not automatic answers.

## What it gives you

For AI-assisted development:

- fewer hidden assumptions, because conventions are written down and linked;
- smaller, safer slices of work, each with its own context and check;
- clear acceptance criteria, so AI output can be trusted or rejected on evidence;
- a growing, self-correcting record of *why* the code is the way it is.

For human developers and maintainers:

- better onboarding into difficult code paths;
- clearer review of scientific changes;
- safer incremental development on long-lived codebases;
- reusable knowledge that survives staff turnover and AI session boundaries.

## Installation

Kosmic is installed as a Markdown-based AI-agent skill. The source skill directory is [`skills/`](skills/), and the installed skill name should be `kosmic`.

There are two supported paths:

1. **AI-agent install.** Paste the ready-to-use install prompt from [docs/installation.md](docs/installation.md) into Claude Code, Codex, OpenCode, or another coding agent and let it install Kosmic into the correct local skill/instruction location.
2. **Manual install.** Copy the Markdown skill files into your agent's custom skill or persistent-instructions directory. For OpenCode, that is typically:

   ```bash
   mkdir -p ~/.config/opencode/skill/kosmic
   cp -R skills/* ~/.config/opencode/skill/kosmic/
   ```

See [docs/installation.md](docs/installation.md) for detailed instructions, verification steps, and notes for agents that do not support named skills.

## Quick start

The skill identity is `kosmic`. In agents with named skills, load or invoke `kosmic` using that agent's normal mechanism. For OpenCode:

```
/skill kosmic
```

The knowledge vault directory is `memnotes` by default, so existing notes, specs, and logs keep their location. Kosmic organizes work per project under `{VAULT}/Projects/{TARGET}/`, with `notes/`, `log/`, and `specs/` subdirectories.

For the full task catalogue (Task 0: Quick Task through Task 7: Review Spec), templates, the spec-approval gate flow, and the directory layout, see the [docs](docs/README.md), [skills/README.md](skills/README.md), and [skills/SKILL.md](skills/SKILL.md).

## Scope of this repository

This repository ships the kosmic skill, user-facing Markdown docs, and the assets needed by those docs.

## License

MIT.
