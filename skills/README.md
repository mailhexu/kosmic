# Kosmic Skill

Spec-driven Project knowledge for reliable AI-assisted development and usage across agents. Kosmic maintains a bounded Shared Skill Library and compiles repeated deterministic procedure mechanics into governed, tested Python routines while preserving judgment in prose.

## Features

- **Knowledge Management**: Atomic notes for capturing patterns, decisions, and learnings
- **Quick Tasks**: Lightweight path for small, low-risk implementation work
- **Optional Research**: Discovery memo for uncertain features before Architecture
- **Spec-Driven Development**: PRD → optional Research → Architecture → Epics → Stories workflow 
- **Test-Driven Implementation**: Research → Tests → Code → Review pipeline
- **Mandatory Code Review**: No story is "done" without review
- **Progress Tracking**: Status lifecycle and daily logging
- **Shared Skill Library**: One authoritative `memnotes/Skills/` tree with one dynamically loaded `SKILL.md` per maintained domain
- **Bounded Recipe Packets**: Deterministic route/query resolution, dependency closure, exact byte budgets, and hash-pinned loading
- **Single Native Router**: Constant discovery footprint across OpenCode, Claude Code, Codex, and OMP
- **Dual-Native Knowledge**: Authoritative Markdown works directly in Obsidian and through Kosmic's validated schemas
- **Deterministic Projection CLI**: Project validation, evidence, proposals, library catalogs, migration, atomic publication, and Install Adapters
- **Procedure Compilation**: Static routine inventory, reuse-first Task P decisions, tested source hashes, and routine-bearing Recipe Packets

## Quick Start

```
# Load or invoke the skill (OpenCode example)
/skill kosmic

# First time? Initialize
Task 1: Initialize

# Existing Project? Migrate identity and audience-scoped knowledge
Task 8: Migrate Project Skills

# Before implementing anything
Task 3: Search

# Found knowledge? Capture it
Task 2: Add Note

# Small, low-risk implementation
Task 0: Quick Task

# Uncertain feature direction before architecture
Task R: Research → Architecture

# Build a feature (spec-driven)
Create PRD → Review PRD → optional Task R → Create Architecture → Review Architecture → Create Stories → Review Story → Implement Story → Code Review
```

Contributor workflows require a named-skill adapter (opencode, claude-code, codex, omp); agents without named skills are supported as consumers through the pointer adapter (`install --adapter pointer`).

## Required procedure skills

Install the reviewed Matt Pocock skill set globally in the active adapter: `tdd`, `code-review`, `diagnosing-bugs`, `research`, `domain-modeling`, `codebase-design`, `grill-with-docs`, `grilling`, and `prototype`. Use the upstream standalone named-skill installer; do not use its managed Claude plugin or project-local installation. Pin the upstream revision recorded by your Kosmic release, and review compatibility before updating it.

Verify from this installed Kosmic directory:

```bash
python3 scripts/kosmic_project_skills.py check-required-skills --adapter opencode
python3 scripts/kosmic_project_skills.py check-required-skills --adapter claude-code
python3 scripts/kosmic_project_skills.py check-required-skills --adapter codex
```

## Directory Structure

```
{VAULT}/Projects/{TARGET}/
├── ProjectEntry.md              # overview + immutable project_id
├── notes/                       # authoritative Obsidian + OKF v0.2 bundle
│   ├── index.md                 # reserved OKF progressive-disclosure index
│   ├── notation.md
│   └── {topic}.md               # line-1 YAML; stable notes declare Audience Scope
├── mathdocs/                   # vault-only executable SymPy authorities
│   ├── index.md
│   ├── {slug}.py
│   └── {slug}.md
├── log/
│   └── {TARGET}-{DATE}.md
├── specs/
│   ├── INDEX.md
│   ├── prd.md
│   ├── research/
│   ├── architecture.md
│   ├── quick-tasks/
│   ├── epics/
│   └── stories/
└── skills/                      # generated atomically; never hand-edit
    ├── {PROJECT_ID}-usage/
    └── {PROJECT_ID}-development/
```

## Tasks

### Task Selection Matrix

| Situation | Use Task | Required Output | Gate Behavior |
|-----------|----------|-----------------|---------------|
| New project/package or missing Kosmic structure | Task 1: Initialize | Project identity, real audience-scoped notes, canonical Skill Pair, instructions, specs index | Block publication until useful Usage exists |
| Existing Project missing identity, Audience Scope, or canonical pair | Task 8: Migrate Project Skills | Immutable identity, classification report, valid pair when Usage exists | Unscoped Knowledge remains Development-only |
| Need existing knowledge or context | Task 3: Search | Relevant notes/specs read | Mandatory before implementation |
| Small, low-risk implementation | Task 0: Quick Task | Quick task record, verification, log/notes | Approval unless user explicitly requested implementation |
| Uncertain direction after PRD | Task R: Research | Research memo linked from Architecture | No new gate; feeds PRD/Architecture review |
| New feature or project planning | Task 5: Create Spec | PRD, optional Research, Architecture, Epics, Stories, specs index | PRD, Architecture, and Story approval gates |
| Approved story ready for code | Task 6: Implement Story | Tests, implementation, story updates, notes | Code review required before `done` |
| Review or approval requested | Task 7: Review Spec | Spec decision, research completeness check, or code review | Required for spec approval and story completion |
| Durable knowledge learned | Task 2: Add Note | Atomic note, TOC update, log entry | Required after learning durable knowledge |
| End/session maintenance | Task 4: Review | Extracted notes, stale note updates, log hygiene | Periodic maintenance |
| Reusable symbolic result or equation defect | Task M: Math Note | Executable derivation, paired note, registry row, source links | Derivation-first; check, review, and completion gates |
| Implemented work yields a proven executable procedure or reusable deterministic mechanics | Task P: Propose Skill Change | One role-declared skill result plus one routine action per canonical routine ID | Shared targets require fresh context, human authority, behavioral evidence, and review; reuse precedes extension and creation |

### Task 0: Quick Task
Plan and execute a small, low-risk implementation task.

**When**:
- Concrete fix, small change, or narrow addition
- Scope fits one focused session
- No new architecture, data model, public API, or broad user-facing workflow

**Flow**: Search → Quick Task record → Approval → Implement/verify → Review → Log/notes

**Guardrail**: If scope or risk is unclear, use Task 5: Create Spec instead.

### Task 1: Initialize
Set up Kosmic for a new project.

**When**: First time working on a project
**Check**: Does `{VAULT}/Projects/{TARGET}/` exist?

### Task 2: Add Note
Capture knowledge in atomic notes.

**When**: 
- Reading code and understanding something
- Making architectural decisions
- Fixing bugs and finding solutions
- Writing documentation
- End of session

**Principle**: Knowledge in your head → must be in notes

### Task 3: Search
Find existing knowledge before implementing.

**When**: 
- BEFORE implementing new features
- BEFORE making architectural changes
- When encountering a problem
- When unsure how something works

**MANDATORY**: Run before any implementation

### Task 4: Review
Periodically review and validate notes.

**Schedule**:
- **Daily**: 5-minute scan at end of session
- **Weekly**: Review week's notes
- **Monthly**: Check stale notes, notation consistency

### Task R: Research
Run optional discovery before Architecture when Search is not enough.

**When**:
- Technical feasibility is unclear
- Multiple architecture approaches are plausible
- Unfamiliar libraries, services, or protocols may be needed
- Risky assumptions would make Architecture speculative

**Flow**: Search → Research memo → Findings/recommendation → Link from Architecture

**Gate**: No new approval gate. Research feeds PRD or Architecture review.

### Task 5: Create Spec
Create specification documents (BMAD-method).

**Hierarchy**: `PRD → optional Research → Architecture → Epics → Stories`

**When**:
- Starting a NEW project
- Adding a NEW feature
- User requests spec creation

**Optional Research**: When Search is not enough, run Task R before Architecture. Research is not a new approval gate; it feeds PRD and Architecture review.

**Gate Points**: Agent MUST pause for user approval after each spec document (PRD, Architecture, Stories). See "Spec-Driven Development Workflow" in SKILL.md for full rules.

### Task 6: Implement Story
Execute story implementation with TDD.

**Flow**:
```
1. RESEARCH    → Search notes, explore codebase, verify assumptions
2. TESTS (TDD) → Write failing tests first
3. IMPLEMENT   → Write code to pass tests
4. REVIEW      → Code review (MANDATORY)
5. DONE        → All tests pass + code reviewed
```

**Key Principle**: NO unjustified assumptions!

### Task 7: Review Spec
Review specifications and code.

**Spec Review**: PRD, Architecture, Epic, Story approval
**Code Review**: MANDATORY for story completion

**Status**: `draft → approved → in_progress → review → done`

### Task 8: Migrate Project Skills
Assign or validate immutable Project identity, transactionally normalize Project Knowledge to dual-native Obsidian/OKF Markdown, report Unscoped Knowledge, and publish the Skill Pair after reviewed Usage knowledge exists.

**Reference**: `references/task_project_skills.md`

**Gate**: Never infer Consumer guidance, guess ambiguous Wikilinks, or publish an empty Usage Skill.

### Task D: Dream

Previous-day whole-vault reflection via `dream-harvest` / `dream-publish` / `dream-abort`; writes only `memnotes/dreams/`.

**Reference**: `references/task_dream.md`

### Task P: Propose Skill Change
Classify a reusable Pattern as one skill result (`create`, `update`, `no_action`) and, when applicable, one routine action (`reuse`, `extend`, `create`, `keep_as_prose`, `none`) per canonical routine ID. Search the generated inventory first. Proposal artifacts remain reviewable under `specs/skill-proposals/`; they never mutate canonical or installed artifacts before approval and behavioral comparison.

**Reference**: `references/task_propose_skill.md`

**Gate**: Shared/global scope requires a dedicated proposer subagent. Accepted procedural changes require execution Evidence, human approval, and Task 7 review. Routine create/extend additionally requires owning and consuming Domain Maintainer approvals; equivalent rejected fingerprints require materially new evidence.

### Task M: Math Note
Create and maintain one executable SymPy derivation plus its paired Math Derivation note. Search `mathdocs/index.md` first, execute trusted code through `check-math`, review assumptions/units/conventions, and link dependent notes and implementation with stable `MathDoc:` identifiers.

**Reference**: `references/task_math_note.md`

**Gate**: The executable file is authoritative. `check-math --update` alone does not establish physical correctness; human review precedes stable promotion.

## Project Knowledge Format

`notes/` is one authoritative Obsidian-readable OKF v0.2 bundle—not an authoring tree plus an export tree. Its `index.md` contains only the required `okf_version: "0.2"` frontmatter. Every other concept starts with YAML on line 1, declares `type`, uses `status: draft | stable | deprecated`, and links with relative standard Markdown. Kosmic-specific fields such as `audience`, confidence, validation procedure, and provenance remain valid extension fields.

## Shared Domain Skill Library

`memnotes/Skills/SKILL.md` is the single installed library entry point. Each maintained software domain has one compact domain `SKILL.md`; detailed Usage and Development topics are ordinary Markdown. `resolve-library` selects a bounded dependency closure plus declared routines and emits a hash-pinned plan. `load-library` verifies manifest, topic, routine-source, and exact packet hashes. `generate-library` statically discovers literal routine declarations without importing source modules; `query-routines` is the reuse-first search seam. Cross-project Evidence stays with its source Project, and Task P governs both shared procedures and `routine://domain/slug` decisions.

Legacy Project Skill Pairs remain migration inputs in their Project vaults, not installed compatibility aliases. `install-library` exposes only `memnotes-skills` and removes managed installed pairs after successful byte and identity verification. See `references/task_project_skills.md`.



## Typical Session Flow

### Knowledge Work
1. **Start**: Search (Task 3) for relevant knowledge
2. **Work**: Add Note (Task 2) whenever you understand something
3. **End**: Review (Task 4) session notes, update log

### Simple Implementation Work (Quick Task)
1. **Scope**: Create Quick Task (Task 0) with acceptance criteria
2. **Gate**: Get approval unless the user already gave explicit implementation approval
3. **Implement**: Make the minimal change, test, and review
4. **Capture**: Update log and notes for durable knowledge

### Feature Development (Spec-Driven)
1. **Plan**: Create Spec (Task 5) - PRD → optional Research → Architecture → Epic → Story
2. **Gate**: Review Spec (Task 7) - Agent pauses for user approval at each stage
3. **Implement**: Implement Story (Task 6) - Research → Tests → Code → Review
4. **Capture**: Add Note (Task 2) - Document what you learned

See SKILL.md "Spec-Driven Development Workflow" for the full gate-point flowchart and 6 agent compliance rules.

Expanded gate sequence:

1. Create PRD → review/approve PRD
2. Optional Task R: Research → link findings from Architecture
3. Create Architecture → review/approve Architecture
4. Create Epics and Stories → review/approve Story
5. Implement approved Story → mandatory code review

## Math Formatting

Always write standalone equations as display math using `$$` delimiters:

```markdown
$$
E = mc^2
$$
```

Use inline `$...$` only for short symbols or expressions inside prose.

## File Hygiene

Kosmic-owned scratch starts with the mandatory **Managed Run Before Scratch** step in `SKILL.md`: `scratch begin` returns the sole writable run path below the active worktree’s `.tmp/kosmic/`; `scratch succeed|fail` closes it with Git evidence. Keep durable source/docs in the project tree and pending tests under `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` with `MANIFEST.md`. See `references/managed_run_lifecycle.md` for retention, promotion, status, cleanup, and the destination-sibling staging exception.
## Spec Status Lifecycle

```
draft → approved → in_progress → review → done
         ↑             ↓           │
         └─────────────┴───────────┘ (changes requested)
```

| Status | Meaning |
|--------|---------|
| draft | Being written, not ready |
| approved | Ready for implementation |
| in_progress | Currently being worked on |
| review | Awaiting code review |
| done | Tests pass + reviewed |

## Status Vocabulary

| Artifact | Statuses | Notes |
|----------|----------|-------|
| Specs and stories | `draft`, `approved`, `in_progress`, `review`, `done` | Approval gates apply to PRD, Architecture, Stories, and code review. |
| Quick tasks | `draft`, `approved`, `in_progress`, `review`, `done` | Lightweight implementation lifecycle with mandatory verification. |
| Research memos | `draft`, `done` | No approval gate; feeds PRD or Architecture review. |
| Notes | `draft`, `stable`, `deprecated` | OKF knowledge lifecycle; use `stale_after` for currentness. |

Blocked work should stay in its current status with a blocker note and log entry; do not use an undocumented `blocked` status.

## Configuration

In your project's `AGENTS.md`:

```markdown
### Kosmic Integration
- **Vault**: `./memnotes` (or custom path)
- **Target**: `{vault-project-folder}`
- **Project ID**: `{immutable-project-id}`
- **Usage Skill**: `{immutable-project-id}-usage`
- **Development Skill**: `{immutable-project-id}-development`
```


## Best Practices

### Knowledge Capture
- **One concept per note**: Keep notes focused
- **Self-contained**: Understandable without external context
- **Full sentences**: Clear explanations, not just bullets
- **Link related notes**: Use relative Markdown links such as `[Note](./note_name.md)`
- **Document variables**: Use `notation.md` for consistency

### Spec-Driven Development
- **Use Quick Task for small work**: Keep simple changes lightweight but traceable
- **Use Research for uncertainty**: Create a memo when Search is not enough before Architecture
- **Keep Specs Index current**: Update `specs/INDEX.md` whenever specs, research, stories, or quick tasks change
- **Research first**: No unjustified assumptions
- **Test-driven**: Write tests before implementation
- **Code review mandatory**: No story is "done" without review
- **Traceability**: Link specs bidirectionally
- **Update knowledge**: Capture learnings after implementation

### Daily Workflow
- **Search before acting**: Check existing knowledge
- **Log progress**: Update log at end of session
- **Extract knowledge**: Move insights from log to notes
- **Review regularly**: Keep knowledge fresh and accurate


## Files

```
kosmic/
├── SKILL.md                     # Skill definition
├── README.md                    # This file
├── references/
│   ├── task_init.md
│   ├── task_quick_task.md
│   ├── task_research.md
│   ├── task_add_note.md
│   ├── task_search.md
│   ├── task_review.md
│   ├── task_create_spec.md
│   ├── task_implement_story.md
│   ├── task_review_spec.md
│   ├── agents_template.md
│   └── templates/
│       ├── template-prd.md
│       ├── template-quick-task.md
│       ├── template-research.md
│       ├── template-specs-index.md
│       ├── template-architecture.md
│       ├── template-epic.md
│       ├── template-story.md
│       └── template-log.md
```

## License

MIT
