# Project Skill Pair Lifecycle

Use this shared contract whenever a Kosmic task initializes, migrates, refreshes, validates, reviews, or installs Project skills.

## Invariants

- `notes/` is authoritative Project Knowledge and a dual-native Obsidian/OKF v0.2 bundle; generated skill packages are disposable projections.
- The bundle-root `notes/index.md` declares only `okf_version: "0.2"` and groups concepts for progressive disclosure.
- Every other note starts with YAML on line 1, has a non-empty `type`, and uses relative standard Markdown links.
- Each Project has an immutable `project_id` and exactly `{PROJECT_ID}-usage` plus `{PROJECT_ID}-development`.
- Usage projects stable `audience: usage` and `audience: both` notes.
- Development projects stable `audience: development` notes and requires Usage for consumer and shared behavior.
- A stable note without `audience` is Unscoped Knowledge and remains Development-only until reviewed.
- Specs and logs never project directly. Distill durable behavior into stable notes first.
- Both skills describe the same `working_state` from `ProjectEntry.md`.
- The generated `skills/` tree is also OKF v0.2 conformant. Publication and installation are atomic; never edit canonical or installed projections.

## Projection-Eligible Note Metadata

```yaml
type: Project Knowledge
status: stable
audience: development | usage | both
usage_stale: false
# stale_after: 'YYYY-MM-DD'  # optional real effective date
```

`usage_stale: true`, `draft`, `deprecated`, a reached `stale_after`, or material outside `notes/` excludes the document. The Projection CLI copies eligible note bodies under fresh OKF frontmatter and records source path and SHA-256 provenance in each topic reference.

## Commands

Resolve `{KOSMIC_SKILL_DIR}` to the installed Kosmic skill directory.

Generate or refresh the canonical pair:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py generate \
  --project "{VAULT}/Projects/{TARGET}"
```

Validate the authoritative OKF notes bundle, projection provenance, and drift:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py validate \
  --project "{VAULT}/Projects/{TARGET}"
```

Review Unscoped Knowledge and projection drift:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py review \
  --project "{VAULT}/Projects/{TARGET}"
```

Migrate an existing Project:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py migrate \
  --project "{VAULT}/Projects/{TARGET}" \
  --project-id "{PROJECT_ID}"
```

Migration is restartable and transactional for `notes/`. It moves frontmatter to line 1, adds `type`, maps legacy `validated` to `stable`, conservatively maps undated legacy `stale` to `draft`, renames `TOC.md` to `index.md`, and converts unambiguous Wikilinks to relative Markdown links. Ambiguous links, embeds, and block references stop migration without partial note edits. Publication remains blocked until real stable Usage knowledge exists.

Check a story or quick task before completion:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py check-completion \
  --project "{VAULT}/Projects/{TARGET}" \
  --work-item "{WORK_ITEM}"
```

Work items must declare `consumer_interface_change: true | false`. When true, `related_notes` must name current stable `usage` or `both` notes, and the canonical pair must pass drift validation.

## Install Adapters

Install into an isolated or real agent home with:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py install \
  --project "{VAULT}/Projects/{TARGET}" \
  --adapter opencode | claude-code | codex \
  --home "{HOME}"
```

For an agent without named skills, update its persistent instruction file with canonical pointers:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py install \
  --project "{VAULT}/Projects/{TARGET}" \
  --adapter pointer \
  --instructions "{PROJECT_INSTRUCTIONS}"
```

Adapters validate the canonical pair before exposure. A failed adapter operation preserves the previously valid installed pair or pointer section.
