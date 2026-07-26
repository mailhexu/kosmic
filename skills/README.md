# Kosmic Skill (v3.0.0)

Spec-driven Project knowledge for reliable AI-assisted development and usage across agents. Kosmic remains the workflow orchestrator while a deterministic Projection CLI generates each Project's atomic Usage and Development Skill Pair.

## Features

- **Knowledge Management**: Atomic notes for capturing patterns, decisions, and learnings
- **Quick Tasks**: Lightweight path for small, low-risk implementation work
- **Optional Research**: Discovery memo for uncertain features before Architecture
- **Spec-Driven Development**: PRD → optional Research → Architecture → Epics → Stories workflow 
- **Test-Driven Implementation**: Research → Tests → Code → Review pipeline
- **Mandatory Code Review**: No story is "done" without review
- **Progress Tracking**: Status lifecycle and daily logging
- **Project Skill Pair**: Exactly `{project}-usage` and `{project}-development` generated from stable notes
- **Dual-Native Knowledge**: One authoritative notes tree works directly in Obsidian and as an OKF v0.2 bundle
- **Deterministic Projection CLI**: OKF validation, audience filtering, provenance, drift checks, atomic publication, migration, and Install Adapters

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

If your agent does not support named skills, use `SKILL.md` as persistent instructions and keep this `README.md` plus `references/` available for task details and templates.

## Directory Structure

```
{VAULT}/Projects/{TARGET}/
├── ProjectEntry.md              # overview + immutable project_id
├── notes/                       # authoritative Obsidian + OKF v0.2 bundle
│   ├── index.md                 # reserved OKF progressive-disclosure index
│   ├── notation.md
│   └── {topic}.md               # line-1 YAML; stable notes declare Audience Scope
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

## Project Knowledge Format

`notes/` is one authoritative Obsidian-readable OKF v0.2 bundle—not an authoring tree plus an export tree. Its `index.md` contains only the required `okf_version: "0.2"` frontmatter. Every other concept starts with YAML on line 1, declares `type`, uses `status: draft | stable | deprecated`, and links with relative standard Markdown. Kosmic-specific fields such as `audience`, confidence, validation procedure, and provenance remain valid extension fields.

## Project Skill Pair Lifecycle

Stable notes declare `audience: development`, `usage`, or `both`. Usage receives `usage` and `both`; Development receives `development` and requires Usage for shared behavior. Run the Projection CLI through the commands in `references/task_project_skills.md` to generate, validate, review, migrate, check completion, or install the pair.

Canonical packages remain in the Project vault and are themselves OKF v0.2 bundles. OpenCode, Claude Code, and Codex adapters expose them through native skill directories; the pointer adapter supports agents without named skills.


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

- Classify new files before creating them: commit artifact, scratch/runtime output, recoverable pending tests, or generated output.
- Use `.tmp/<task-slug>/` only for disposable scratch and runtime output.
- Use `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` for tests awaiting later commit.
- Add `MANIFEST.md` with restore command and contents, and commit pending-test packages before ending the session.
- Delete generated ABINIT outputs (`*.nc`, `*_DDB`, `*.agr`, run-output `*.abo`) and patch scratch unless explicitly promoted.
- Finish by running `git status --short` and classifying every remaining file.

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
