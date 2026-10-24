# Capture an idea

Use for an explicit `kosmic idea <description>` or equivalent save request. An idea is tentative input, not verified knowledge or approval to implement/research it.

## Resolve once

- Project idea: use the configured or explicitly selected `{PROJECT_ROOT}` (the vault Project root, not its source worktree or subproject). Require only an existing root with valid `ProjectEntry.md` identity.
- Explicit general/non-Project idea: use the configured or explicitly selected `{VAULT}`. No Project identity, synthetic Project or bootstrap is needed.
- If the destination is ambiguous, clarify Project versus general, and which root, before writing. Do not guess scope or fall back to general because a Project is missing. Resolve vault paths from project configuration, then `$KOSMIC_VAULT`, then `./memnotes`; resolve the configured target for a Project request.
- Preserve the supplied text, context, equations and uncertainty. Pass a supplied title with `--title`; otherwise omit that argument and let the command derive a title. Do not invent research or supporting evidence.

## Save once

Subcommands of the single Projection CLI; substitute actual paths/text and quote shell arguments safely (or pass an argument array). Project:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py idea \
  --project {PROJECT_ROOT} --text "{IDEA_TEXT}" [--title "{TITLE}"]
```

General:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py idea \
  --vault {VAULT} --text "{IDEA_TEXT}" [--title "{TITLE}"]
```

Exactly one selector; `--text` must be non-blank. The bracketed title argument is optional syntax, not literal shell input. Existing selected root required; only the missing child directory is created lazily:

- Project: `{PROJECT_ROOT}/ideas/<title-slug>.md`.
- General: `{VAULT}/GeneralIdeas/<title-slug>.md`, outside every Project.

No dates in filenames. Same-title and identical captures create distinct notes with `-2`, `-3`, … suffixes, never an overwrite or automatic merge. The note records its title and actual UTC creation time; its `## History` / `### YYYY-MM-DD` entry contains the complete text once, not a duplicate changelog. Only Project notes carry `project_id`. There is no append command or automatic promotion into canonical notes/skills.

## Return and stop

Exit0 JSON supplies `scope`, `idea_path` (absolute), `title`, `created`, and `project_id` only for a Project. Return one Markdown link using the actual returned path as both the full visible label and target: `[/absolute/path/title.md](/absolute/path/title.md)`. Trust the result; no help lookup, confirmation listing/read-back, second save or STATUS refresh.

On nonzero exit, report the actual diagnostic and affected path. Do not claim saved content, repair/init the root, recommend spec-operation resume, or blindly retry: a late filesystem failure can leave an already-published complete note. An abrupt interruption can leave owned staging; do not sweep unrelated files.

This capture-only fast path precedes Contributor/bootstrap prerequisites. It needs no generated pair/router repair, required-procedure-skill check, clean Git/worktree registration, Quick Task/Story, managed run, review, work start/finish, receipt, log/index, projection or curation. It authorizes only one idea and its missing child directory. All subsequent implementation, knowledge promotion and installation keep their separate normal gates.
