---
name: kosmic
description: Spec-driven knowledge management with BMAD-method workflow. Atomic notes, quick tasks, optional research, PRD→Architecture→Epics→Stories, TDD implementation, mandatory code review.
version: 2.0.0
license: MIT
compatibility: opencode
---

# Kosmic

## Overview

Knowledge-oriented, spec-driven infrastructure for coding. Kosmic manages a `memnotes` knowledge base with spec-driven development support. Each task is independent - load only what you need.

**Documentation**: See `README.md` for complete guide.

---

## Vault Detection (MANDATORY FIRST STEP)

Before any task, resolve `{VAULT}` and `{TARGET}`:

```
1. grep -i "vault\|kosmic\|memnotes" AGENTS.md → extract path after "Vault:" or "KOSMIC_VAULT:"
2. If not found: check env $KOSMIC_VAULT
3. If not found: default to ./memnotes
4. TARGET = basename of current project directory (or ask user for multi-package)
5. Verify: ls {VAULT}/Projects/{TARGET}/    → if missing, run Task 1: Initialize
```

**STOP**: Do not proceed with any task until `{VAULT}` and `{TARGET}` are resolved.

---

## Paths

| Item | Path |
|------|------|
| Vault | `{VAULT}` |
| Target | `{TARGET}` |
| Notes | `{VAULT}/Projects/{TARGET}/notes/{TOPIC}.md` |
| TOC | `{VAULT}/Projects/{TARGET}/notes/TOC.md` |
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

## Tasks

### Task Selection Matrix

| Situation | Use Task | Required Output | Gate Behavior |
|-----------|----------|-----------------|---------------|
| New project/package or missing Kosmic structure | Task 1: Initialize | Project structure, AGENTS.md integration, specs index | Ask only if vault/target is ambiguous |
| Need existing knowledge or context | Task 3: Search | Relevant notes/specs read | Mandatory before implementation |
| Small, low-risk implementation | Task 0: Quick Task | Quick task record, verification, log/notes | Approval unless user explicitly requested implementation |
| Uncertain direction after PRD | Task R: Research | Research memo linked from Architecture | No new gate; feeds PRD/Architecture review |
| New feature or project planning | Task 5: Create Spec | PRD, optional Research, Architecture, Epics, Stories, specs index | PRD, Architecture, and Story approval gates |
| Approved story ready for code | Task 6: Implement Story | Tests, implementation, story updates, notes | Code review required before `done` |
| Review or approval requested | Task 7: Review Spec | Spec decision, research completeness check, or code review | Required for spec approval and story completion |
| Durable knowledge learned | Task 2: Add Note | Atomic note, TOC update, log entry | Required after learning durable knowledge |
| End/session maintenance | Task 4: Review | Extracted notes, stale note updates, log hygiene | Periodic maintenance |

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

**When**: Starting work on a NEW project, adding a NEW package, or no Kosmic structure exists.

**Check**: `ls {VAULT}/Projects/{TARGET}/` → if not found, run this task.

---

### Task 2: Add Note

**Load**: `references/task_add_note.md`

**When**: Any time knowledge is found -- reading code, fixing bugs, making decisions, writing docs, end of session.

**Rule**: Knowledge in your head → must be in notes.

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


## Spec-Driven Development Workflow

**This section defines the mandatory workflow for feature development. The agent MUST follow these steps in order. Skipping steps is not allowed for feature work.** Small, low-risk work may use Task 0: Quick Task when it satisfies the Quick Task guardrails.

### User Guide: How to Use the Spec Workflow

When you want to build a new feature or project, tell the agent:

1. **"Create a PRD for {feature}"** → Agent creates PRD, presents it for your review
2. **"Approve the PRD"** (or request changes) → Agent updates status
3. **"Research {topic} before architecture"** (optional, Task R) → Agent writes a research memo with findings and recommendations
4. **"Create architecture"** → Agent creates architecture doc with ADRs
5. **"Approve architecture"** → Agent updates status
6. **"Break into epics and stories"** → Agent creates epics and stories
7. **"Approve story {N}"** → Agent marks story ready for implementation
8. **"Implement story {N}"** → Agent follows TDD workflow
9. **"Review story {N}"** → Agent performs code review

You can also say **"Plan and build {feature}"** and the agent will walk you through each step, pausing for your approval at each gate.

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

RULE 3: NEVER mark a story "done" without code review.
        Task 7 (Review Spec) is MANDATORY before status: done.

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

```
┌──────────────────────────────────────────────────┐
│  STEP 1: Create PRD (Task 5)                     │
│  → Write PRD from user's feature description     │
│  → Present to user                               │
└──────────────────┬───────────────────────────────┘
                   │
            ┌──────▼──────┐
            │  GATE: User  │
            │  approves    │ ← Agent MUST wait here
            │  PRD?        │
            └──────┬──────┘
                   │ yes
┌──────────────────▼───────────────────────────────┐
│  OPTIONAL: Research (Task R)                     │
│  → Investigate open questions and options        │
│  → Link findings from Architecture               │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│  STEP 2: Create Architecture (Task 5)            │
│  → Document ADRs, system design, test strategy   │
│  → Present to user                               │
└──────────────────┬───────────────────────────────┘
                   │
            ┌──────▼──────┐
            │  GATE: User  │
            │  approves    │ ← Agent MUST wait here
            │  Arch?       │
            └──────┬──────┘
                   │ yes
┌──────────────────▼───────────────────────────────┐
│  STEP 3: Create Epics + Stories (Task 5)         │
│  → Break into epics, then stories                │
│  → Present story list to user                    │
└──────────────────┬───────────────────────────────┘
                   │
            ┌──────▼──────┐
            │  GATE: User  │
            │  approves    │ ← Agent MUST wait here
            │  Stories?    │
            └──────┬──────┘
                   │ yes (per story)
┌──────────────────▼───────────────────────────────┐
│  STEP 4: Implement Story (Task 6)                │
│  → Research → Tests (TDD) → Code → Review        │
└──────────────────┬───────────────────────────────┘
                   │
            ┌──────▼──────┐
            │  GATE: Code  │
            │  review      │ ← MANDATORY, no exceptions
            │  passes?     │
            └──────┬──────┘
                   │ yes
              Story: done
```

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
Is this a NEW project/package?
├─ YES → Task 1: Initialize
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
            │   Review spec/code? → Task 7: Review Spec
            └─ NO →
                Did I UNDERSTAND something?
                ├─ YES → Task 2: Add Note
                └─ NO →
                    Is it time to REVIEW (end of session/week)?
                    ├─ YES → Task 4: Review
                    └─ NO → Continue working
```

## Typical Session Flow

### For Knowledge Work
1. **Start**: Search (Task 3) for relevant knowledge
2. **Work**: Add Note (Task 2) whenever you understand something
3. **End**: Review (Task 4) session notes, update log

### For Feature Development (Spec-Driven)
1. **Plan**: Create Spec (Task 5) - PRD → optional Research → Architecture → Epic → Story
2. **Gate**: Present each spec to user, wait for approval (Task 7)
3. **Implement**: Implement Story (Task 6) - Research → Tests → Code → Review
4. **Capture**: Add Note (Task 2) - Document what you learned

### For Simple Implementation Work (Quick Task)
1. **Scope**: Create Quick Task (Task 0) with acceptance criteria
2. **Gate**: Get user approval unless the user already gave explicit implementation approval
3. **Implement**: Make the minimal change, test, and review
4. **Capture**: Update log and add notes for durable knowledge

## Mandatory Checkpoints

**Before ANY task**: Search (Task 3) for keywords

**After ANY task**: 
- Did you learn something? → Add Note (Task 2)
- Update log

**Before finishing session**: Review (Task 4) - verify notes extracted

**For Story completion**: Code review (Task 7) is MANDATORY - no exceptions

**For Quick Task completion**: Review and verification are MANDATORY before status: done

## Status Vocabulary

| Artifact | Statuses | Notes |
|----------|----------|-------|
| Specs and stories | `draft`, `approved`, `in_progress`, `review`, `done` | Approval gates apply to PRD, Architecture, Stories, and code review. |
| Quick tasks | `draft`, `approved`, `in_progress`, `review`, `done` | Lightweight implementation lifecycle; review and verification are still mandatory. |
| Research memos | `draft`, `done` | No approval gate; findings feed PRD or Architecture review. |
| Notes | `draft`, `validated`, `stale`, `deprecated` | Knowledge lifecycle only; separate from spec/story statuses. |

If work is blocked, keep the current status and add a blocker note in the artifact plus a log entry. Do not invent an undocumented `blocked` status.

---

## Distribution

When initializing a new project, use `references/agents_template.md` to add the Kosmic Integration section to that project's AGENTS.md.
