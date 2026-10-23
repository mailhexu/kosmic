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

Direct read-only questions inspect authoritative notes/specs without initialization, migration, installation or generated-state repair. Missing Project knowledge is reported, not created. This authorizes no execution/mutation and does not bypass its prerequisites. Read-only or no-discovery sessions create no note, log, index update or validation chore.

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
- A verified durable, reusable finding or correction is not already represented.
- Existing knowledge needs a substantive correction, not merely a reread or reconfirmation.

**Key Principle**: Update the owning atomic note instead of duplicating it. Understanding existing material or reaching session end alone creates no note/log obligation; dataset-only metadata stays beside its data.

**Reference**: `references/task_add_note.md`

#### Use Task: Review
**When**:
- Explicitly requested or scheduled knowledge maintenance.

Outdated knowledge or returning after an absence may justify suggesting a targeted review; neither pre-empts the foreground request automatically.

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
2. **Plan**: Reuse relevant notes/specs and resolve factual questions before asking for decisions.
3. **During**: Capture only durable additions/corrections not already represented.
4. **End**: Finish-owned completion bookkeeping covers changed work. Maintenance is requested/scheduled separately; read-only or no-discovery sessions require no durable cleanup.
