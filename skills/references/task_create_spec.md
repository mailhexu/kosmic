# Task: Create Spec

Create specification documents following BMAD-method workflow: PRD → optional Research → Architecture → Epics → Stories.

## When to Use

- Starting a NEW project (create all specs)
- Adding a NEW feature (create feature-level specs)
- User requests: "create PRD", "create architecture", "create epics", "create story"

Pre-Architecture uncertainty, discovery, spikes, and option investigation are
Task R's bounded research branch (`references/task_research.md`), not this task.

## Spec Hierarchy

```
PRD (Product Requirements)
    │
    ├── optional Research (Discovery + Recommendations)
    │
    ├── Architecture (Technical Decisions + ADRs)
    │
    └── Epics (Major deliverables)
        │
        └── Stories (Implementable units)
            │
            └── Tasks (Research → Tests → Code → Review)
```

## Directory Structure

```
{VAULT}/Projects/{TARGET}/specs/
├── INDEX.md
├── prd.md
├── research/
│   └── {YYYY-MM-DD}-{slug}.md
├── architecture.md
├── quick-tasks/
│   └── {YYYY-MM-DD}-{slug}.md
├── epics/
│   └── epic-{N}-{slug}.md
└── stories/
    └── story-{N}-{slug}.md
```

## Commands

```bash
# Create specs directory
mkdir -p "{VAULT}/Projects/{TARGET}/specs/research"
mkdir -p "{VAULT}/Projects/{TARGET}/specs/quick-tasks"
mkdir -p "{VAULT}/Projects/{TARGET}/specs/epics"
mkdir -p "{VAULT}/Projects/{TARGET}/specs/stories"
```

Create `{VAULT}/Projects/{TARGET}/specs/INDEX.md` from `references/templates/template-specs-index.md` if missing.

---

## MANDATORY: Pre-Creation Checks

Before creating ANY spec, the agent MUST:

1. **Search** (Task 3) for existing specs covering the same topic
2. **Verify prerequisites** exist (see each step below)
3. **Confirm with user** what they want before writing

```
STOP CHECK: Have I searched for existing specs?
  → grep -i "keyword" {VAULT}/Projects/{TARGET}/specs/*.md
  → grep -i "keyword" {VAULT}/Projects/{TARGET}/specs/**/*.md
  If similar spec exists → inform user, ask whether to update or create new
```

---

## Step 1: Create PRD

**File**: `{VAULT}/Projects/{TARGET}/specs/prd.md`
**Template**: `references/templates/template-prd.md`
**Prerequisites**: None (this is the starting point)

### Process

1. Discuss the problem and goals with the user
2. Write the PRD using the template
3. Set `status: draft`
4. Update `specs/INDEX.md`
5. Present to user for review

**Spec-event step**: after writing the spec and updating `specs/INDEX.md`, run `generate-status --project ...` so the working-directory STATUS.md reflects the new spec.

### GATE: User Approval Required

```
STOP: Present PRD to user. Do NOT proceed to Architecture until user says:
  - "approved" / "looks good" / "go ahead" → set status: approved
  - "change X" → update PRD, present again
  - "reject" → major rework needed
```

### Principles

- **Problem-first**: Start with the problem, not the solution
- **Measurable**: Success criteria must be verifiable
- **Prioritized**: Use MoSCoW (must/should/could/won't)
- **Bounded**: Non-goals are as important as goals

---

## Optional Research Before Architecture

Before Architecture, optionally run Research if open questions or technical uncertainty would make the architecture speculative.

**Optional Research File**: `{VAULT}/Projects/{TARGET}/specs/research/{YYYY-MM-DD}-{slug}.md`
**Template**: `references/templates/template-research.md`
**Reference**: Task R, `references/task_research.md`

Research is not an approval gate. It is complete when findings, options, recommendation, open questions, and Architecture impact are documented. If findings change product scope, update the PRD and return to the PRD approval gate.

After creating or updating a Research memo, update `specs/INDEX.md`.

---

## Step 2: Create Architecture

**File**: `{VAULT}/Projects/{TARGET}/specs/architecture.md`
**Template**: `references/templates/template-architecture.md`
**Prerequisites**: PRD must exist and be `approved`

```
STOP CHECK: Is PRD approved?
  → grep "status:" {VAULT}/Projects/{TARGET}/specs/prd.md
  If not approved → tell user "PRD must be approved first" → run Task 7 Review
```

### Process

1. Read the approved PRD
2. Read any linked Research memos
3. Identify key technical decisions
   - If material alternatives or unresolved trade-offs remain, invoke `grill-with-docs` before drafting the decision; invoke `codebase-design` for module boundaries or interfaces and `domain-modeling` for domain terminology or ADRs.
   - If research and reasoning cannot resolve a design question, invoke `prototype` inside the mandatory managed run. Capture the question, verdict, and evidence in the relevant Research memo or Story Technical Notes, link that record from Architecture, then finalize the run. It is never production implementation.
4. Write Architecture doc with ADRs using the template
5. Link relevant Research memos in the Architecture frontmatter
6. Set `status: draft`
7. Update `specs/INDEX.md`
8. Present to user for review

### GATE: User Approval Required

```
STOP: Present Architecture to user. Do NOT proceed to Epics until user approves.
  - "approved" → set status: approved
  - "change X" → update, present again
```

### Principles

- **Decision-driven**: Every significant choice is an ADR
- **Consequence-aware**: Document trade-offs explicitly
- **Test-aware**: Define testing strategy upfront
- **Risk-aware**: Identify and plan for risks

---

## Step 3: Create Epic

**File**: `{VAULT}/Projects/{TARGET}/specs/epics/epic-{N}-{slug}.md`
**Template**: `references/templates/template-epic.md`
**Prerequisites**: PRD and Architecture must exist and be `approved`

```
STOP CHECK: Are PRD and Architecture approved?
  → grep "status:" {VAULT}/Projects/{TARGET}/specs/prd.md
  → grep "status:" {VAULT}/Projects/{TARGET}/specs/architecture.md
  Both must be approved → if not, tell user which needs approval first
```

### Process

1. Read PRD and Architecture
2. Break the work into epics (each delivers standalone value)
3. Write epic files using the template
4. Set `status: draft`
5. Update `specs/INDEX.md`
6. Present epic breakdown to user

### GATE: User Approval Required

```
STOP: Present epic list to user. Wait for approval before creating stories.
```

### Principles

- **Value-focused**: Each epic delivers standalone value
- **Story-container**: Epics group related stories
- **Progress-trackable**: Update progress as stories complete

---

## Step 4: Create Story

**File**: `{VAULT}/Projects/{TARGET}/specs/stories/story-{N}-{slug}.md`
**Template**: `references/templates/template-story.md`
**Prerequisites**: Parent epic must exist

```
STOP CHECK: Does parent epic exist?
  → ls {VAULT}/Projects/{TARGET}/specs/epics/epic-{N}-*.md
  If not → create epic first (Step 3)
```

### Process

1. Read parent epic and architecture
2. Write story file using the template
3. Define acceptance criteria (must be testable)
4. Set `status: draft`
5. Update `specs/INDEX.md`
6. Present to user for review

### GATE: User Approval Required

```
STOP: Present story to user. Story MUST be approved before implementation.
  - "approved" → set status: approved, story is ready for Task 6 (Implement)
  - "change X" → update, present again
```

### Principles

- **User-centric**: Start with user story format
- **Test-first**: TDD - write tests before implementation
- **Research-included**: Research is Phase 1 of implementation
- **No assumptions**: All assumptions must be verified
- **Review-required**: Code review is mandatory for "done"

---

## Status Lifecycle

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
| review | Implementation complete, awaiting review |
| done | All tests pass, code reviewed, complete |

---

## Checklist

### Before Creating PRD
- [ ] Searched for existing specs covering this topic
- [ ] Understand the problem space
- [ ] Identified stakeholders
- [ ] Defined clear success criteria

### Before Creating Architecture
- [ ] PRD exists and is `approved`
- [ ] Optional Research completed or intentionally skipped
- [ ] Understand technical constraints
- [ ] Considered alternatives for key decisions

### Before Creating Epic
- [ ] PRD and Architecture are `approved`
- [ ] Epic delivers standalone value
- [ ] Can be broken into stories

### Before Creating Story
- [ ] Parent epic exists
- [ ] Story is small enough to complete in one session
- [ ] Acceptance criteria are testable

---

## Update Log

After creating any spec, update log:

```markdown
## Session {N}
- Created: [PRD](../specs/prd.md) - {brief description}
- Created: [Epic 001](../specs/epics/epic-001-{slug}.md) - {brief description}
- Updated: [Specs Index](../specs/INDEX.md) - {brief description}
```
