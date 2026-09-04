# kosmic repository instructions

## Kosmic Integration

This project uses **Kosmic** for persistent memory and knowledge management.

### Configuration
- **Vault**: `./memnotes`
- **Target**: `kosmic` (current vault Project folder)
- **Project ID**: `kosmic` (immutable)
- **Usage Skill**: `kosmic-usage`
- **Development Skill**: `kosmic-development`

### Skill

The `kosmic` skill/workflow is available to the coding agent. If the agent supports named skills, load or invoke `kosmic` through that mechanism. If not, use the installed Markdown instructions as persistent project guidance.

### When to Use Kosmic Tasks

#### Use Task: Initialize
**When**: First time working on this project (no Kosmic structure exists)
**Reference**: `references/task_init.md`
**Check**: Does `./memnotes/Projects/kosmic/` exist?

#### Use Task: Search
**When**:
- BEFORE implementing new features
- BEFORE making architectural changes
- When encountering a problem
- When unsure how something works

**Reference**: `references/task_search.md`

#### Use Task: Quick Task
**When**:
- Small, low-risk implementation work
- Concrete fix, narrow change, or simple addition
- Scope and acceptance criteria are clear
- Full PRD → optional Research → Architecture → Epics → Stories workflow would be disproportionate

**Do not use when**: The task introduces architecture changes, data models, public APIs, security-sensitive behavior, broad user-facing workflows, or unclear requirements.

**Workflow**: Search → Quick Task record → Approval → Implement/verify → Review → Log/notes

**Reference**: `references/task_quick_task.md`

#### Use Task: Add Note
**When**:
- **Any time knowledge is found** (new OR existing - document what you learn)
- Reading code to understand a system, algorithm, or pattern
- Writing documentation (capture core concepts as notes too)
- Made an architectural decision
- Found a solution worth remembering
- Validating or re-verifying existing knowledge
- At end of session to log progress

**Key Principle**: Document knowledge whenever you FIND it, not just when you CREATE it.

**Reference**: `references/task_add_note.md`

#### Use Task: Review
**When**:
- End of work session (quick daily review)
- End of week (weekly review)
- Knowledge seems outdated
- Returning to project after absence

**Reference**: `references/task_review.md`

#### Use Task R: Research
**When**:
- Optional discovery is needed after PRD and before Architecture
- Task Search found that existing notes/specs are not enough
- Technical feasibility, library choice, or architecture direction is uncertain

**Workflow**: Search → Research memo → Findings/recommendation → Link from Architecture

**Gate**: No new approval gate. Research feeds PRD or Architecture review.

**Reference**: `references/task_research.md`

#### Use Task: Create Spec (Spec-Driven Development)
**When**: Building a new feature or planning a project

**Workflow** (agent MUST follow in order, pausing at each gate for user approval):
1. Create PRD → **WAIT for user approval**
2. Optional Task R: Research → no new gate; feed findings into Architecture
3. Create Architecture → **WAIT for user approval**
4. Create Epics + Stories → **WAIT for user approval**
5. Implement approved stories (TDD) → **Code review MANDATORY**

**Reference**: `references/task_create_spec.md`

### Planning Workflow

When planning a task, always integrate knowledge retrieval:

1. Identify uncertain areas and search `./memnotes/Projects/kosmic/notes/index.md` first.
2. Search specs under `./memnotes/Projects/kosmic/specs/` before creating new ones.
3. Include relevant notes as task context and link them from specs.

### Typical Session

1. **Start**: Search for relevant knowledge
2. **Plan**: Check notes, research if needed, add new notes, include in plan
3. **During**: Add notes whenever you understand something
4. **End**: Review and log progress
