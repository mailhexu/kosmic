# Kosmic Integration Template

This section is added to a project's AGENTS.md during Kosmic initialization.

**Note**: Headers are one level deeper (## instead of #) to fit within existing AGENTS.md structure.

---

## Kosmic Integration

This project uses **Kosmic** for persistent memory and knowledge management.

### Configuration
- **Vault**: `{KOSMIC_VAULT}`
- **Target**: `{TARGET}` (vault Project folder)
- **Project ID**: `{PROJECT_ID}` (immutable)
- **Usage Skill**: `{USAGE_SKILL}`
- **Development Skill**: `{DEVELOPMENT_SKILL}`
- **Canonical Pair**: `{KOSMIC_VAULT}/Projects/{TARGET}/skills/`

### Skills

The `kosmic` skill is the workflow orchestrator. Contributor work loads `{DEVELOPMENT_SKILL}`, which in turn requires `{USAGE_SKILL}` for consumer and shared behavior. Consumers may invoke `{USAGE_SKILL}` directly. If named skills are unsupported, persistent instructions must point to both canonical packages.

### Work Record Authority

- Project root: `{KOSMIC_VAULT}/Projects/{TARGET}/`; register the exact working root.
  A fixed subproject constrains the directory, never selects an agent task.
- Before substantive source/docs/vault/config/experiment changes, select/create
  an approved owner-local Story hierarchy or standalone approved Quick Task.
- Routine initialization is record/review-free: it performs only bounded bootstrap
  (identity and structure scaffold plus status binding) and creates no Quick Task,
  work record, code review, or work finish; it does not create `STATUS.md` and does
  not install adapters. Adapter installation is a separately requested, approved
  operation; substantive changes remain governed by the normal work-record workflow.
- Explicit `kosmic idea` capture is also record-free and precedes bootstrap/Contributor prerequisites: follow `references/task_idea.md` in the Kosmic skill. Resolve a Project for Project ideas or the vault for explicit general ideas; clarify ambiguity. Capture writes only one note and its missing `ideas/` or `GeneralIdeas/` child, then returns the full-path link and stops. No Project identity is required for general ideas; no Git, repair, review, STATUS or note/log/index publication follows capture. Implementing an idea retains normal approval gates.
- Inspect the governing record with `work show --project {KOSMIC_VAULT}/Projects/{TARGET} --work-record QUALIFIED_RECORD`; no shared mutable task pointer is used.
- Start record-governed writes with `work start --project PROJECT_ROOT --worktree ROOT --work-record REF`. It refuses a dirty worktree; use one clean worktree per record and one writer.
- Record-governed mutating commands take `--work-record` and recheck ownership, ancestry and status. Declare scope at `work finish`; out-of-scope Git paths block completion.
- Read-only queries remain record-free. Raw editor/shell guarantees are agent compliance, not an OS sandbox.
- Complete with `work finish --work-record REF --worktree ROOT --scope worktree:PATH` after actual acceptance and review. A successful receipt marks completion; after interruption, rerun finish.
- Installation/migration require their own approved target plans. Do not edit installed user-authored skills.

### Project Knowledge Format

`{KOSMIC_VAULT}/Projects/{TARGET}/notes/` is the authoritative Obsidian-compatible OKF v0.2 bundle. Use `index.md` for discovery. Concept notes require YAML frontmatter on line 1, non-empty `type`, `status: draft | stable | deprecated`, and relative Markdown links. Do not create or hand-maintain a second OKF export.

### When to Use Kosmic Tasks

#### Capture an idea
**When**: Explicit request to save a tentative thought, not implement it.
**Reference**: `references/task_idea.md`
**Stores**: Project-root `ideas/` or vault-root `GeneralIdeas/`, created lazily; title-only filenames with numeric collision suffixes and complete content once under dated History. Never merge or promote automatically.

#### Use Task: Initialize
**When**: The vault Project, immutable Project Identifier, conformant Knowledge bundle, or canonical Skill Pair is missing
**Reference**: `references/task_init.md`
**Check**: Does `{KOSMIC_VAULT}/Projects/{TARGET}/ProjectEntry.md` define `{PROJECT_ID}`, does `notes/index.md` declare OKF v0.2, and does `skills/` contain both valid projections?

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

A successful `work finish` receipt is sufficient — no post-success re-validation; read-only questions and checks need no record or durable cleanup.

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

Outdated knowledge or returning after an absence may justify suggesting a targeted review; neither pre-empts the foreground request automatically. Read-only or no-discovery sessions create no note, log, index update or validation chore.

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

#### Before Planning

1. **Identify uncertain areas**: What context or background knowledge do I need?

2. **Search existing notes**: Check if relevant knowledge already exists

3. **If not found in notes**: Research the codebase
   - Read relevant source files
   - Understand existing patterns
   - Document findings as notes (Add Note task)

4. **Add notes BEFORE finalizing plan**: Capture any new discoveries

#### During Planning

1. **Include related notes in task context**: Reference relevant notes when describing the plan

2. **Link notes to plan**: Mention which notes informed the decision

#### Example

    Planning: Implement user authentication
    
    1. Search notes for: "authentication", "user", "session"
    2. Found: [Authentication Flow](./memnotes/Projects/{TARGET}/notes/auth_flow.md), [Session Management](./memnotes/Projects/{TARGET}/notes/session_management.md)
    3. Read notes → understand existing patterns
    4. Research codebase for: password hashing, token generation
    5. Add note `password_hashing_convention.md` if a new discovery
    6. Create plan with context from notes

### Typical Session

1. **Start**: Search for relevant knowledge
2. **Plan**: Check notes, research if needed, add new notes, include in plan
3. **During**: Add notes whenever you understand something
   - Reading code → capture the understanding
   - Writing docs → also create atomic notes
   - Implementing → document decisions
   - Debugging → document root causes
4. **End**: If durable changes occurred, review, log, and complete; a read-only session has no logging or bookkeeping

**Status file**: `STATUS.md` at the working-directory root is generated from vault spec state (`generate-status --project {VAULT}/Projects/{TARGET}`). Initialization records only the status binding, so the file may not exist until the first normal spec/work event. Read it when present; never edit it by hand.
