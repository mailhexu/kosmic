# Task: Implement Story

Execute story implementation following TDD with mandatory research phase.

## When to Use

- Story status is `approved` and ready for implementation
- User says: "implement story", "start story", "work on story"

## Prerequisites

```
STOP CHECK before starting:
  1. Story file exists at {VAULT}/Projects/{TARGET}/specs/stories/story-{N}-{slug}.md
  2. Story status is "approved" OR "in_progress"
     → grep "status:" {story_file}
     → If approved: transition it to in_progress and begin at Phase 1.
     → If in_progress: a resumed session — skip phases already recorded as done in
       the story's checklist, re-verify the last completed step still holds, and
       address any review findings recorded in the story or its evidence packs
       before writing new code.
     → If draft: "Story must be approved first. Run Task 7 (Review Spec)."
  3. Linked epic, architecture, and PRD exist
     → Check linked_epic, linked_architecture, linked_prd in frontmatter
```

**Do NOT write any code until all prerequisites are verified.**

If the story implements mathematical functionality, load Task M before Phase 1. Require both `derivations` and `math_implementation_files` in story frontmatter, run the derivation before writing implementation code, and preserve adjacent `MathDoc:` identifiers in every declared source file.

---

## Implementation Flow

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: RESEARCH (No unjustified assumptions!)        │
│  ├── Search memnotes for existing knowledge             │
│  ├── Explore codebase for patterns                      │
│  ├── Verify every assumption                            │
│  └── Ask human if uncertain                             │
└─────────────────────────────────────────────────────────┘
                          │
                    STOP: All assumptions verified?
                    Any ❓ left? → Ask user before proceeding.
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: WRITE TESTS (TDD)                             │
│  ├── Write failing tests for each acceptance criterion  │
│  └── Tests define expected behavior                     │
└─────────────────────────────────────────────────────────┘
                          │
                    STOP: Do tests fail as expected?
                    If tests pass without implementation → tests are wrong.
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: IMPLEMENT                                     │
│  ├── Write code to pass tests                           │
│  ├── Follow existing patterns from research             │
│  └── Keep it simple (YAGNI, KISS)                       │
└─────────────────────────────────────────────────────────┘
                          │
                    STOP: Do ALL tests pass?
                    If not → fix before proceeding.
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  PHASE 4: REVIEW (Mandatory - NO EXCEPTIONS)            │
│  ├── All tests pass                                     │
│  ├── Code review completed (Task 7)                     │
│  └── Knowledge notes updated                            │
└─────────────────────────────────────────────────────────┘
                          │
                    STOP: Code review passed?
                    If not → back to Phase 3, fix issues.
                          │
                          ▼
                    STATUS: done
```

---

## Step 1: Research Phase

**Goal**: Gather all context needed. NO UNJUSTIFIED ASSUMPTIONS.

This is story-level implementation research. It is mandatory for approved stories and is separate from optional pre-architecture Research in `references/task_research.md`.

If the Story corrects a defect, invoke `diagnosing-bugs` before Phase 2. Establish and minimize a reproducible failure, discriminate cause hypotheses with evidence, and add the regression test at the agreed seam before implementation can complete.

Before changing code, pin a stable review fixed point. Update story status, date, and review metadata:
```yaml
status: in_progress
updated: {DATE}
review_base: {commit, branch, tag, or implementation-start snapshot}
review_round: 0
```

Do not change `review_base` during fix/re-review cycles.

### 1.1 Search Kosmic

```bash
# Search the OKF Knowledge index for relevant topics
grep -i "keyword" {VAULT}/Projects/{TARGET}/notes/index.md

# Deep search in notes
git grep -i "pattern\|concept" -- "{VAULT}/Projects/{TARGET}/notes/"

# Also search specs for related work
git grep -i "pattern\|concept" -- "{VAULT}/Projects/{TARGET}/specs/"
```

Read relevant notes and document findings in story's Technical Notes section.

### 1.2 Explore Codebase

- Find similar implementations
- Identify existing patterns and conventions
- Locate relevant files and modules
- Check test patterns used in project

### 1.3 Verify Assumptions

For each assumption, document in the story's Assumptions table:

| Assumption | Verified? | Source |
|------------|-----------|--------|
| Pattern X is used | ✅ | src/module.py:L45 |
| Library Y supports Z | ❓ | _ask human_ |
| Config is loaded from env | ✅ | config.py:L12 |

**Rules**:
- ✅ = Verified with code/notes reference
- ❓ = Needs human input
- ❌ = Assumption is wrong, adjust plan

### 1.4 STOP: Ask Human (If Needed)

```
STOP CHECK: Are there any ❓ in the assumptions table?
  → If YES: Present questions to user. Do NOT proceed to Phase 2 until resolved.
  → If NO: Proceed to Phase 2.
```

If any assumption is ❓ or cannot be verified:

```
"I need clarification before implementing:

1. {Question 1}?
   - Context: {why this matters}
   
2. {Question 2}?
   - Context: {why this matters}

Please clarify so I can proceed without assumptions."
```

### 1.5 Document Findings

Update story file's Technical Notes section:

```markdown
## Technical Notes

### Patterns Found
- Pattern X: Used in src/a.py, src/b.py
- Pattern Y: Used for handling errors

### Relevant Knowledge
- [Note Name](../../notes/note-name.md): Key insight about X

### Implementation Approach
1. Create module Z following pattern X
2. Use library W for Y
3. Handle edge case: ...

### Edge Cases
- Edge case 1: Handle by ...
- Edge case 2: Handle by ...
```

**Mark Phase 1 complete** — edit the story file and check off every Research task:

```markdown
### Phase 1: Research

- [x] Search memnotes for relevant knowledge
- [x] Explore codebase for patterns/conventions
- [x] Identify and verify all assumptions
- [x] Ask human for clarification if needed
- [x] Document findings in Technical Notes
```

Also bump `updated:` in the frontmatter:

```yaml
updated: {DATE}
```

---

## Step 2: Write Tests (TDD)

**Goal**: Define expected behavior before implementation.

Invoke `tdd` for the red-green implementation method. Before the first test, agree the highest external test seam; invoke `codebase-design` when a seam, module boundary, or module interface changes, and `domain-modeling` when terminology changes. Keep one vertical slice at a time and do not replace Kosmic research, review, or completion gates.

### 2.1 Map Acceptance Criteria to Tests

For each acceptance criterion, create at least one test:

```markdown
AC: Given user is logged in, when they click logout, then session is cleared

Test: test_logout_clears_session()
- Setup: Create authenticated session
- Action: Call logout endpoint
- Assert: Session is null/empty
```

### 2.2 Write Failing Tests

```bash
# Run tests to confirm they fail
pytest tests/test_feature.py -v  # or project's test command
```

```
STOP CHECK: Do tests FAIL as expected?
  → If tests pass without implementation code → tests are wrong, fix them
  → If tests fail with expected errors → proceed to Phase 3
```

**Principles**:
- One test per acceptance criterion minimum
- Include edge cases discovered in research
- Follow existing test patterns in project
- Tests should be clear and self-documenting

### 2.3 Update Story

Open the story file and mark each TEST-xxx task `[x]` as you write it. Use the **exact task text from the story file** — do not invent new names.

```markdown
### Phase 2: Tests (TDD - Write First!)

- [x] TEST-001: Write test for {scenario}   ← change [ ] to [x]
- [x] TEST-002: Write test for {scenario}   ← change [ ] to [x]
```

Also bump `updated:` in the frontmatter:

```yaml
updated: {DATE}
```

---

## Step 3: Implement

**Goal**: Write minimal code to pass tests.

### 3.1 Implement Following Patterns

Use patterns discovered in research phase:
- Follow existing code style
- Reuse existing utilities
- Apply architectural decisions from ADRs

Apply SKILL.md **Managed Run Before Scratch** while implementing. Begin the run before creating disposable output and use only its returned path; terminally succeed or fail it before final status. Keep pending tests under `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` with `MANIFEST.md`, commit those packages before finishing, and preserve durable evidence/spec/log rules.

**Vault commit cadence**: when the story (and, on its final story, the epic)
reaches `done`, commit the whole vault tree together with source —
`git add -A && git commit` — before reporting final status. Uncommitted vault
records break dream harvesting and Git-derived provenance.

### 3.2 Run Tests Continuously

```bash
# Run tests frequently during implementation
pytest tests/test_feature.py -v  # or project's test command
```

### 3.3 Keep It Simple

- YAGNI: Don't add features not in acceptance criteria
- KISS: Simplest solution that passes tests
- DRY: Extract common code, but not prematurely

### 3.4 STOP: Verify Tests Pass

```
STOP CHECK: Do ALL tests pass?
  → Run full test suite: pytest (or project's test command)
  → If any test fails → fix before proceeding to Phase 4
  → If all pass → proceed to Phase 4
```

### 3.5 Update Story

Open the story file and do **all three** of the following:

**a) Mark each IMPL-xxx task `[x]`** (use the exact task text from the story file):

```markdown
### Phase 3: Implementation

- [x] IMPL-001: {task description}   ← change [ ] to [x]
- [x] IMPL-002: {task description}   ← change [ ] to [x]
```

**b) Mark each Acceptance Criterion `[x]`** that is now satisfied by passing tests:

```markdown
## Acceptance Criteria

- [x] Given {context}, when {action}, then {outcome}
- [x] Given {context}, when {action}, then {outcome}
```

**c) Bump `updated:` in the frontmatter:**

```yaml
updated: {DATE}
```

---

## Step 4: Review Phase

**Goal**: Ensure quality before marking done.

Update story status to `review` and bump the date:
```yaml
status: review
updated: {DATE}
```

### 4.1 Verify All Tests Pass

```bash
# Run full test suite
pytest  # or project's test command

# Check coverage if configured
pytest --cov
```

### 4.2 Convergent Code Review (MANDATORY - NO EXCEPTIONS)

```
STOP: Story CANNOT be marked "done" without Task 7's convergent review.
  → Round 1 performs one complete Standards axis and one complete Spec axis.
  → Record every finding in the stable ledger before requesting changes.
  → Later rounds verify open findings, changed code, and fix-introduced regressions.
  → Non-blocking suggestions do not prevent approval.
```

Use Task 7 (`references/task_review_spec.md`) rather than starting an ad hoc fresh review. Preserve finding IDs and update the same ledger each round. After the maximum automated round, escalate the remaining ledger instead of beginning another unrestricted review.

### 4.3 Update Knowledge

If you learned something during implementation:

1. Create/update atomic notes (Task 2: Add Note)
2. Update notation if new terms introduced
3. Link notes from story file
4. Assign each changed note an explicit Audience Scope and regenerate the atomic Skill Pair.
5. If the story changes a Consumer Interface, set `consumer_interface_change: true` and list its current stable `usage` or `both` notes in `related_notes`.
6. Classify changed procedure mechanics. Declare `routine_edge_change: true` whenever the story adds or changes a procedure's `uses_routines` edge; this requires `routine_decision_required: true`. When reusable deterministic mechanics are introduced or materially changed, set `routine_decision_required: true`, query the generated inventory, and list one governed Task P artifact per unique proposal path in `routine_proposals`; otherwise keep the gate false and the list empty.
7. If the work captured raw experience (review findings, test-run summaries, debug transcripts), write an Evidence Pack under `{VAULT}/Projects/{TARGET}/evidence/{YYYY-MM-DD}-{slug}/` with a `MANIFEST.md`, declare its slug in the story's `evidence_packs:` frontmatter, and run Task 9: Distill (`references/task_distill.md`) over it.
8. Run the `check-completion` command from `references/task_project_skills.md` before marking the story done — it fails when any declared evidence pack lacks a draft-or-stable note linking it via `evidence:`.

### 4.4 Update Story

Open the story file and apply **all four** of the following:

**a) Mark Phase 4 review tasks `[x]`:**

```markdown
### Phase 4: Review

- [x] All tests pass
- [x] Code review completed
- [x] Knowledge notes updated
```

**b) Mark the Definition of Done `[x]`:**

```markdown
## Definition of Done

- [x] All acceptance criteria met
- [x] All tests pass
- [x] Code reviewed and approved
- [x] Knowledge notes updated
- [x] No regressions introduced
```

**c) Add a row to the Progress Log:**

```markdown
## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| ... | ... | ... |
| {DATE} | Reviewed | Code review passed |
```

**d) Bump frontmatter status to `review` and update the date** (if not already done at the start of Step 4):

```yaml
status: review
updated: {DATE}
```

---

## Step 5: Mark Done

Execute **all of the following in one pass** — do not skip any item:

### 5.1 Update Story Frontmatter

```yaml
---
status: done
updated: {DATE}
---
```

### 5.2 Add Final Row to Story Progress Log

```markdown
## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| ... | ... | ... |
| {DATE} | Done | Story complete |
```

### 5.3 Update Epic

Open the linked epic file (from `linked_epic:` in story frontmatter). Update the stories table and progress:

```markdown
## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-{N}](../stories/story-{N}-{slug}.md) | {title} | done |

## Progress

- Stories: {X}/{N} done
- Last updated: {DATE}
```

### 5.4 Update Daily Log

```markdown
## Session {N}
- Completed: [Story {N}](../specs/stories/story-{N}-{slug}.md) - {brief description}
- Added notes: [{note}](../notes/{note}.md)   ← only if knowledge notes were created
```

---

### Completion Checklist (verify before considering story done)

- [ ] Story frontmatter: `status: done`, `updated: {DATE}`
- [ ] All Phase 1–4 task checkboxes are `[x]` in the story file
- [ ] All Acceptance Criteria are `[x]` in the story file
- [ ] All Definition of Done items are `[x]` in the story file
- [ ] Progress Log has a "Done" row in the story file
- [ ] Epic stories table shows `done` for this story
- [ ] Epic progress count updated
- [ ] Daily log entry added

---

## Troubleshooting

### Tests Won't Pass

1. Re-read acceptance criteria
2. Check test assumptions
3. Ask human for clarification
4. Update story with blockers

### Found Bug in Existing Code

1. Create separate bug fix story
2. Document in knowledge notes
3. Continue with current story if unrelated

### Scope Creep

1. New requirements → create new story
2. Update current story's scope if minor
3. Do not add untracked features

### Blocked on External

1. Document blocker in story
2. Keep current story status and add a `## Blockers` section with owner and next action
3. Create follow-up task in log

---

## Checklist

### Before Starting Implementation
- [ ] Story status is `approved`
- [ ] All linked specs exist (epic, architecture, PRD)
- [ ] Searched existing notes and specs (Task 3)

### After Research Phase
- [ ] All assumptions verified (no ❓ in table)
- [ ] Technical notes documented
- [ ] Implementation approach clear

### After Test Phase
- [ ] Tests for all acceptance criteria
- [ ] Tests are failing (will pass after implementation)
- [ ] Edge cases covered

### After Implementation
- [ ] All tests pass
- [ ] Code follows project patterns
- [ ] No unnecessary complexity

### Before Marking Done
- [ ] Code review completed (MANDATORY)
- [ ] Review fixed point recorded before implementation
- [ ] Complete Round 1 finding ledger recorded
- [ ] All Blocking findings resolved or escalated at the convergence limit
- [ ] Knowledge notes updated
- [ ] Consumer Interface impact declared
- [ ] Completion gate passed
- [ ] Canonical Skill Pair regenerated after eligible knowledge changes
- [ ] Epic progress updated
- [ ] Log updated
