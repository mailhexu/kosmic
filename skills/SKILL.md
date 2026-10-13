---
name: kosmic
description: Orchestrate Project knowledge and spec-driven work, maintain a governed Shared Skill Library, and compile repeated deterministic procedure mechanics into tested reusable routines.
version: 6.0.0
license: MIT
compatibility: markdown-agent-skill, python>=3.11
---

# Kosmic

## Overview

Knowledge-oriented, spec-driven infrastructure for coding. Kosmic manages authoritative Project Knowledge and a vault-level Shared Skill Library. One installed router dynamically loads bounded Usage/Development topics and any hash-pinned deterministic routines their procedures use. Task 9 classifies mechanics; Task P governs reuse, extension, or creation. Judgment and approval stay in prose. Kosmic works with OpenCode, Claude Code, Codex, or OMP.

**Documentation**: See `README.md` for complete guide.

---

## Vault Detection (MANDATORY FIRST STEP)

Before any task, resolve `{VAULT}`, `{TARGET}`, and `{PROJECT_ID}`:

```
1. Search project instructions for the Kosmic Vault, Target, and Project ID fields.
2. If Vault is absent: check env $KOSMIC_VAULT, then default to ./memnotes.
3. TARGET = configured vault Project folder; otherwise use the current package name.
4. Verify {VAULT}/Projects/{TARGET}/.
   - Missing → run Task 1: Initialize.
   - Present but ProjectEntry.md has no project_id → run the migration in references/task_project_skills.md.
5. PROJECT_ID = immutable project_id from ProjectEntry.md.
6. USAGE_SKILL = {PROJECT_ID}-usage.
7. DEVELOPMENT_SKILL = {PROJECT_ID}-development.
```

**STOP**: Do not proceed until the vault Project and immutable Project Identifier resolve. Contributor workflows must also resolve a valid Shared Skill Library. **Exception (bootstrap)**: Task 1 initializes a Project, and the migration procedure in `references/task_project_skills.md` establishes the library; those exact operations are exempt from the prerequisite they establish.

## Required Procedure Skills (MANDATORY)

Before Contributor work, verify the required procedure-skill set for the active Install Adapter:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py check-required-skills --adapter {opencode|claude-code|codex|omp}
```

Missing skills or an unsupported adapter → stop and follow the required-procedure-skills section of the installed `README.md`. Kosmic is the sole workflow orchestrator: required skills supply bounded methods and never replace Kosmic's vault records, approval gates, Shared Skill Library, or Projection CLI.

---

## Paths

| Item | Path |
|------|------|
| Vault | `{VAULT}` |
| Target | `{TARGET}` |
| Project ID | `project_id` in `{VAULT}/Projects/{TARGET}/ProjectEntry.md` |
| Shared Skill Library | `{VAULT}/Skills/` |
| Shared Skill Router | `{VAULT}/Skills/SKILL.md`; installed as `memnotes-skills` |
| Domain Skill | `{VAULT}/Skills/{DOMAIN}/SKILL.md` |
| Skill Topics | `{VAULT}/Skills/{DOMAIN}/{usage|development}/*.md` |
| Legacy migration pair | `{VAULT}/Projects/{TARGET}/skills/` |
| Projection CLI | `scripts/kosmic_project_skills.py` in the installed Kosmic skill |
| Notes | `{VAULT}/Projects/{TARGET}/notes/{TOPIC}.md` |
| Knowledge Index | `{VAULT}/Projects/{TARGET}/notes/index.md` |
| Notation | `{VAULT}/Projects/{TARGET}/notes/notation.md` |
| Log | `{VAULT}/Projects/{TARGET}/log/{TARGET}-{YYYY-MM-DD}.md` |
| Specs | `{VAULT}/Projects/{TARGET}/specs/` |
| Specs Index | `{VAULT}/Projects/{TARGET}/specs/INDEX.md` |
| PRD | `{VAULT}/Projects/{TARGET}/specs/prd.md` |
| Research | `{VAULT}/Projects/{TARGET}/specs/research/{YYYY-MM-DD}-{slug}.md` |
| Architecture | `{VAULT}/Projects/{TARGET}/specs/architecture.md` |
| Quick Tasks | `{VAULT}/Projects/{TARGET}/specs/quick-tasks/{YYYY-MM-DD}-{slug}.md` |
| Epics | `{VAULT}/Projects/{TARGET}/specs/epics/epic-{N}-{slug}.md` |
| Stories | `{VAULT}/Projects/{TARGET}/specs/stories/story-{N}-{slug}.md` |

**CLI invocation**: every command shown in this skill (`work start`, `generate-status`, `validate-library`, …) is a **subcommand of the single Projection CLI** — never a standalone executable. Run it as `python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py <subcommand> …`; see `<subcommand> --help` for flags.

## Project Skill Routing (MANDATORY)

Kosmic remains the workflow orchestrator; Project skills provide audience-specific knowledge.

1. **Contributor work** — before planning, changing, testing, reviewing, or releasing Project code, load `{DEVELOPMENT_SKILL}`. Follow its required reference to `{USAGE_SKILL}` whenever the work invokes or changes a Consumer Interface.
2. **Consumer work** — load `{USAGE_SKILL}` for invocation/configuration/integration/troubleshooting that does not change implementation. Read-only questions/checks need no spec workflow. Persistent configuration or experiment outputs still need compatible bounded record/scope authority; this never implies feature implementation approval.
3. **Knowledge/spec maintenance** — use Kosmic tasks and load the Project skill matching the knowledge audience.
4. Missing, stale, mismatched, or unresolved pair → stop and run validation or migration. Never continue contributor work without Project guidance.

## Record-first authority (MANDATORY)

Before a substantive source, docs, vault, configuration, or experiment change,
select or create its governing record. Feature implementation needs an approved
owner-local Story → Epic → Architecture → PRD chain. A standalone low-risk
change needs an approved Quick Task; PRD creation/success never approves code.

- Questions, searches and unchanged checks need no new record and remain
  read-only. Never hide durable cleanup, publication, or installation in them.
- Planning creates only its draft hierarchy and bounded planning outputs.
  Initial Project/registration bootstrap first establishes a bounded governing
  Quick Task; its scope does not authorize unrelated implementation.
- Use one owner-aware catalog. Feature records live under
  `subprojects/{SUBPROJECT_ID}/specs/`; shared Quick Tasks/proposals under `specs/`.
  Existing flat feature specs stay bootstrap until separately approved migration.
- Keep notes, mathdocs and canonical skills shared at the Project root. Register
  each exact working directory. A fixed subproject constrains a directory, never
  selects its task. Never persist selection in a shared mutable pointer.

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py work start --project {PROJECT_ROOT} --worktree {REGISTERED_ROOT} --work-record {QUALIFIED_RECORD}
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py work show --project {PROJECT_ROOT} --work-record {QUALIFIED_RECORD}
```

Run `work start` before writable changes. It resolves ownership, approved
ancestry and lifecycle at invocation time, then refuses a dirty worktree and
lists the conflicting paths. Each mutating command takes the same explicit
`--work-record`; it re-resolves authority and never caches approval.

Use one clean worktree per record and one writer per worktree. Declare intended
outputs with `--scope` on `work finish`; it checks the Git diff against those
claims. Preserve user work by committing/stashing it or using a separate
worktree. Raw editor/shell writes remain agent compliance, not an OS sandbox.

Declare actual acceptance results/artifact hashes in `acceptance_evidence` and
the real pinned two-axis decision in `review_record` (formats in
`references/task_project_skills.md`). Never edit `done` by hand. Use
`work finish --work-record REF --worktree PATH --scope worktree:PATH` after
review; the receipt is the completion marker, so unreceipted `done` is pending.
If interrupted, rerun finish; there is no recovery journal or `work recover`.

Reports name qualified identity, canonical path, and observed acceptance/smoke/
review results. A checkbox or command exit code alone is not acceptance evidence.
Migration and installation retain their separate approved target plans, including
disposable adapter validation. Never edit installed user-authored skills.

Record-first checks are on by default for supported mutating commands. Each
command re-resolves the explicit record. Raw editor/shell remains an agent
compliance boundary, never claimed as OS sandbox enforcement.

## Project Knowledge Format (MANDATORY)

`{VAULT}/Projects/{TARGET}/notes/` is one authoritative bundle that is both Obsidian-readable and OKF v0.2 conformant. `index.md` is the reserved progressive-disclosure entry point. Every other note starts with YAML frontmatter on line 1, declares a non-empty `type`, uses `status: draft | stable | deprecated`, and links with relative standard Markdown. Do not create a separate OKF export tree.

---

## Math Formatting

Always write display equations in Markdown using `$$` delimiters, with the equation on its own lines:

```markdown
$$
E = mc^2
$$
```

Do not leave standalone LaTeX equations as raw paragraphs without delimiters. Use inline `$...$` only for short symbols or expressions embedded in prose.

---

## File Hygiene Before Coding and Before Final Status

### Managed Run Before Scratch (MANDATORY)

Before creating Kosmic-owned scratch, runtime output, generated intermediates, or a temporary Git index, run:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py scratch begin --project {VAULT}/Projects/{TARGET} --purpose {task-slug}
```

**Done when:** JSON reports `code: OK`; write all disposable material only below the returned run path. `NO_GIT_WORKTREE` is a stop condition: place the vault in a Git worktree whose root ignores `.tmp/`. Before final status run `scratch succeed` or `scratch fail`; **done when** it reports `code: OK` and the run has terminal Git evidence.

Durable source and documentation remain in the project tree. Pending tests remain under `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` with `MANIFEST.md` and must be committed; Evidence Packs, specs, and logs retain their own governance.

**Vault commit cadence**: when a story or epic reaches `done`, or a session
ends after any vault change, commit the *entire* vault tree
(`git add -A && git commit`) — memnotes records, specs, evidence, logs, and
generated Skill Pairs together with source. Never accumulate multi-session
uncommitted vault history: dream harvesting, Git-derived provenance, and
input-manifest pinning all degrade silently on uncommitted state. Destination-sibling atomic-publication staging is not run scratch. Load [Managed Run Lifecycle](references/managed_run_lifecycle.md) only when retention, promotion, status, or recovery detail is needed.
## Tasks

### Task Selection Matrix

| Situation | Use Task | Required Output | Gate Behavior |
|-----------|----------|-----------------|---------------|
| New project/package or missing Kosmic structure | Task 1: Initialize | Project structure, immutable Project Identifier, dual-native OKF/Obsidian notes, AGENTS.md integration, specs index | Block completion until real stable knowledge exists |
| Existing Project missing identity, OKF conformance, or Shared Library migration | Task 8: Migrate Project Skills | Immutable Project Identifier, transactional note migration, explicit domain/topic assignments, valid library catalog | Unscoped Knowledge remains Project-local; never infer a reusable domain route |
| Need existing knowledge or context | Task 3: Search | Relevant notes/specs read | Mandatory before implementation |
| Small, low-risk implementation | Task 0: Quick Task | Quick task record, verification, log/notes | Approval unless user explicitly requested implementation |
| Uncertain direction after PRD | Task R: Research | Research memo linked from Architecture | No new gate; feeds PRD/Architecture review |
| New feature or project planning | Task 5: Create Spec | PRD, optional Research, Architecture, Epics, Stories, specs index | PRD, Architecture, and Story approval gates |
| Approved story ready for code | Task 6: Implement Story | Tests, implementation, story updates, notes | Code review required before `done` |
| Review or approval requested | Task 7: Review Spec | Spec decision, research completeness check, or code review | Required for spec approval and story completion |
| Durable knowledge learned | Task 2: Add Note | Atomic note, TOC update, log entry | Required after learning durable knowledge |
| End/session maintenance | Task 4: Review | Extracted notes, stale note updates, log hygiene | Periodic maintenance |
| Work item declared `evidence_packs`, or captured experience awaits consolidation | Task 9: Distill | Draft notes/updates/deprecations with `evidence:` links | `check-completion` fails until every declared pack has a linking draft-or-stable note |
| Reusable symbolic result or equation-level defect | Task M: Math Note | Executable SymPy derivation, paired note, index row, verified links | Derivation-first; `check-math`, structural validation, review, and completion linkage gate |
| Distillation creates or materially updates a proven executable procedure | Task P: Propose Skill Change | One role-declared, validated create/update/no_action proposal | Knowledge, guidelines, and evidence never trigger publication; shared procedures require a fresh-context proposer, human approval, behavioral evidence, and target-Maintainer authority |

---

### Task 0: Quick Task

**Load**: `references/task_quick_task.md`

**When**: Small, low-risk implementation work that does not justify PRD → optional Research → Architecture → Epics → Stories.

**Use only if**: Scope is concrete, acceptance criteria are obvious, and the change does not introduce new architecture, data models, APIs, or broad user-facing workflows.

**Flow**: Search → Quick Task record → Approval → Implement/verify → Review → Log/notes

**Template**: `references/templates/template-quick-task.md`

---

### Task 1: Initialize

**Load**: `references/task_init.md`

**When**: Starting work on a NEW Project, adding a NEW package, or no Kosmic structure or Project Identifier exists.

**Check**: Verify the vault Project, `ProjectEntry.md` identity, and Shared Skill Library. Run this task if Project prerequisites are missing.

---

### Task 2: Add Note

**Load**: `references/task_add_note.md`

**When**: Verified knowledge emerges that is durable, reusable, and not already represented — a root cause, a convention, a decision, a correction to an existing note.

**Rule**: One-off activity, session state, and bare error text stay in the log or an Evidence Pack (Task 9), never in notes. One concept = one authoritative note; update rather than duplicate.

**Always do**: Update log + Update TOC.

---

### Task 3: Search

**Load**: `references/task_search.md`

**When**: BEFORE implementing, BEFORE making changes, when unsure. **MANDATORY before any implementation.**

**Always do**: Search TOC first → deep search notes → search specs.

---

### Task 4: Review

**Load**: `references/task_review.md`

**When**: End of session, end of week, returning to a project, knowledge seems outdated.

---

### Task R: Research

**Load**: `references/task_research.md`

**When**: Optional discovery is needed after PRD and before Architecture because Task 3 Search was not enough.

**Use only if**: The feature has unclear feasibility, unfamiliar libraries/services, competing technical approaches, risky assumptions, or architecture-impacting open questions.

**Flow**: Search → Research memo → Findings/recommendation → Link from Architecture

**Gate**: No new approval gate. Feed findings into PRD or Architecture review.

---

### Task 5: Create Spec

**Load**: `references/task_create_spec.md`

**When**: Starting a new project, adding a new feature, user requests spec creation.

**Hierarchy**: `PRD → optional Research → Architecture → Epics → Stories`

**Templates**: `references/templates/` (template-specs-index.md, template-prd.md, template-research.md, template-architecture.md, template-epic.md, template-story.md)

**Always do**: Link specs bidirectionally, update log, start with `draft` status.

---

### Task 6: Implement Story

**Load**: `references/task_implement_story.md`

**When**: Story status is `approved` and ready for implementation.

**Flow**: Research → Tests (TDD) → Implement → Review (mandatory) → Done

---

### Task 7: Review Spec

**Load**: `references/task_review_spec.md`

**When**: Reviewing spec documents, code review after implementation, user says "review" or "approve".

**Status transitions**: `draft → approved` (spec review), `review → done` (code review)

---
### Task 8: Migrate Project Skills

**Load**: `references/task_project_skills.md`

**When**: An existing vault Project lacks an immutable Project Identifier, contains nonconformant Knowledge, or has procedures not yet assigned to the Shared Skill Library.

**Flow**: Assign/validate identity → normalize `notes/` → inventory stable projected procedures → require explicit domain/topic assignments → stage and validate Shared Library → compare behavior → publish atomically → install one router

**Gate**: Migration may record identity and normalize notes, but Shared Library publication requires a complete explicit assignment map and valid atomic catalog. Ambiguous Wikilinks or unassigned legacy references stop migration without partial authoritative changes.

---

### Task 9: Distill

**Load**: `references/task_distill.md`

**When**: A work item declared `evidence_packs` (gated — `check-completion` enforces linkage), or captured experience should become knowledge.

**Rule**: Evidence → root-cause analysis → draft notes. Never duplicate an existing note; update it. Promotion to stable is human-gated.

---
### Task P: Propose Skill Change

**Load**: `references/task_propose_skill.md`

**When**: Task 9 yields or materially updates a reusable Pattern, or a work item declares `proposal_required: true`.

**Rule**: A curated, fresh-context proposer emits exactly one atomic `create`, `update`, or `no_action` artifact. It never edits canonical or installed skills. Repeated failure is a Task P signal only when a general invariant, recovery, reproducer, and verification matrix show that the repair generalizes; it never causes automatic publication. Shared/global proposals require a separate proposer subagent; accepted procedural proposals require behavioral evidence, human approval, and Task 7 review.

**Gate**: New work declares `proposal_required`. A true value requires one valid proposal before completion; rejected equivalent interventions require materially new evidence before reconsideration.

---

### Task M: Math Note

**Load**: `references/task_math_note.md`

**When**: A reusable symbolic result is created or corrected, a note or implementation relies on a mathematical equation, or an equation-level discrepancy appears.

**Rule**: Derivation first. The executable SymPy file is authoritative; generated results are never hand-edited. Human review remains mandatory for assumptions, units, domains, and physical conventions.

**Gate**: Stable dependent notes require exact result/exposition markers. Math-derived implementation requires declared derivations and finite implementation files before completion.

---




## Spec-Driven Development Workflow

**This section defines the mandatory workflow for feature development. The agent MUST follow these steps in order. Skipping steps is not allowed for feature work.** Small, low-risk work may use Task 0: Quick Task when it satisfies the Quick Task guardrails.

### User Guide

Human-facing walkthroughs, example prompts, and gate-by-gate session scripts
live in the installed `README.md` — load them only when guiding a user through
the workflow. Gate points and compliance rules below are the authoritative
agent contract.

### Agent Compliance Rules

```
RULE 1: NEVER skip the spec hierarchy.
        PRD must exist before Architecture.
        Optional Research may happen after PRD and before Architecture.
        Architecture must exist before Epics.
        Epic must exist before its Stories.

RULE 2: NEVER implement feature work without an approved story.
        Story must be status: approved before writing feature code.
        Small, low-risk work may use an approved Quick Task instead.

RULE 3: NEVER mark a story "done" without convergent code review.
        Task 7 is MANDATORY. Pin one review base, run complete Standards and Spec axes,
        preserve stable finding IDs, and restrict re-review to fixes and regressions.
        Non-blocking suggestions do not prevent approval. After three automated rounds,
        escalate the remaining ledger instead of starting a fresh review.

RULE 4: ALWAYS pause for user approval at gate points.
        Gate points: PRD review, Architecture review, Story approval.
        Present the spec to the user and WAIT for their decision.

RULE 5: ALWAYS search (Task 3) before implementing.
        Check existing notes AND specs before creating new ones.

RULE 6: ALWAYS update log after any spec or implementation work.
```

### Optional Research Step

Use Task R when Task 3 Search finds that the feature needs deeper discovery before architecture: unfamiliar libraries, unclear feasibility, competing technical options, risky assumptions, or questions that would make Architecture speculative. Research produces a memo at `{VAULT}/Projects/{TARGET}/specs/research/{YYYY-MM-DD}-{slug}.md` using `references/templates/template-research.md`.

Research is not a new approval gate. It feeds the existing PRD and Architecture gates. If research changes product scope, update and re-approve the PRD. If research changes technical direction, include the findings in Architecture and use the normal Architecture approval gate.

### Quick Task Escape Hatch

Use Task 0 when the user explicitly asks for a simple fix/change or when the task is clearly too small for the full spec hierarchy. Quick Task does not replace the spec workflow for new features. If there is uncertainty about scope, architecture, data shape, API behavior, persistence, security, or multi-step product behavior, use the full spec workflow.

### Workflow with Gate Points

Feature work proceeds strictly in order; each numbered gate requires the
user's explicit decision before the next step (procedure detail lives in the
task references — load only the one you are executing):

1. **PRD** (Task 5) → GATE: user approves the PRD (or requests changes)
2. **Research** (Task R, optional, post-PRD) → feeds Architecture, no new gate
3. **Architecture** (Task 5) → GATE: user approves
4. **Epics + Stories** (Task 5) → GATE: user approves (per story)
5. **Implement Story** (Task 6: Research → TDD → Code) → GATE: convergent code
   review (Task 7) passes — mandatory, no exceptions → story `done`

### Status Lifecycle

```
draft → approved → in_progress → review → done
         ↑             ↓           │
         └─────────────┴───────────┘ (changes requested)
```

| Status | Meaning |
|--------|---------|
| draft | Being written, not ready for work |
| approved | Reviewed by user, ready for implementation |
| in_progress | Currently being worked on |
| review | Implementation complete, awaiting code review |
| done | All tests pass, code reviewed, complete |

---

## Quick Decision Tree

```
Is this a NEW Project/package?
├─ YES → Task 1: Initialize
└─ NO →
    Is identity, Project knowledge, or Shared Library migration missing?
    ├─ YES → Task 8: Migrate Project Skills
    └─ NO →
        Do I need to FIND existing knowledge?
        ├─ YES → Task 3: Search
        └─ NO →
            Is this a SMALL, LOW-RISK implementation task?
            ├─ YES → Task 0: Quick Task
            └─ NO →
                Do I need to CREATE/IMPLEMENT a spec?
                ├─ YES →
                │   Create spec? → Task 5: Create Spec
                │   Research before architecture? → Task R: Research
                │   Implement story? → Task 6: Implement Story
                │   Create/correct reusable math? → Task M: Math Note
                │   Reusable Pattern warrants skill evolution? → Task P: Propose Skill Change
                │   Review spec/code? → Task 7: Review Spec
                └─ NO →
                    Did I UNDERSTAND something?
                    ├─ YES → Task 2: Add Note
                    └─ NO →
                        Is it time to REVIEW (end of session/week)?
                        ├─ YES → Task 4: Review
                        └─ NO → Continue working
```


## Mandatory Checkpoints

**Before ANY task** (except bootstrap Task 1 / migration): Search (Task 3) for keywords

**After ANY task**: 
- Did you learn something? → Add Note (Task 2)
- Update log

**Before finishing session**: Review (Task 4) - verify notes extracted

**For Story completion**: Code review (Task 7) is MANDATORY - no exceptions
**For mathematical work**: Task M runs derivation-first; `check-math` and source linkage must pass before completion
**For reusable Patterns**: Task P records create/update/no_action; shared/global scope requires a fresh-context proposer subagent

**For Quick Task completion**: Review and verification are MANDATORY before status: done

## Status Vocabulary

| Artifact | Statuses | Notes |
|----------|----------|-------|
| Specs and stories | `draft`, `approved`, `in_progress`, `review`, `done` | Approval gates apply to PRD, Architecture, Stories, and code review. |
| Quick tasks | `draft`, `approved`, `in_progress`, `review`, `done` | Lightweight implementation lifecycle; review and verification are still mandatory. |
| Research memos | `draft`, `done` | No approval gate; findings feed PRD or Architecture review. |
| Notes | `draft`, `stable`, `deprecated` | OKF knowledge lifecycle; currentness is represented by `stale_after`, not a fourth status. |

If work is blocked, keep the current status and add a blocker note in the artifact plus a log entry. Do not invent an undocumented `blocked` status.

---

## Distribution

When initializing a new project, use `references/agents_template.md` to add the Kosmic Integration section to that project's AGENTS.md.
The Shared Skill Library is authoritative in the vault. Install only its generated `memnotes-skills` router; Domain Skills and detailed topics load dynamically through a verified Resolution Plan. Never hand-edit generated catalogs, manifests, router packages, or installed copies.
