# Task: Implement Story

Execute story implementation following TDD with mandatory research phase.

## When to Use

- Story status is `approved` and ready for implementation
- User says: "implement story", "start story", "work on story"

## Prerequisites

```
STOP CHECK before starting:
  1. Story resolves through the owner catalog to {VAULT}/Projects/{TARGET}/subprojects/{SUBPROJECT_ID}/specs/stories/story-{N}.md (retain its returned canonical path).
  2. Story status is "approved" OR "in_progress"
     → grep "status:" {story_file}
     → If approved: transition it to in_progress and begin at Phase 1.
     → If in_progress: a resumed session — skip phases already recorded as done in
       the story's checklist and address any review findings recorded in the story
       before writing new code; rerun only checks whose inputs or contracts changed
       or that previously failed (no blanket re-verification of completed steps).
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
│  ├── Write red-capable tests for new/changed behavior   │
│  └── Tests define expected behavior                     │
└─────────────────────────────────────────────────────────┘
                          │
                    STOP: Do the NEW-behavior tests fail first?
                    Existing passing guards are never forced to fail.
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
│  └── Notes updated only if reusable knowledge emerged   │
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

Before the first implementation write, run `work start --project PROJECT_ROOT --worktree ROOT --work-record QUALIFIED_RECORD`. It re-resolves the approved Story and requires a clean worktree. Use one record, one worktree, one writer; scope expansion requires an updated reviewed Story/Quick Task. Follow SKILL.md Record-first authority; code review is evidence, not permission to expand the slice. The story starts work once: a resumed session continues inside its recorded scope and the existing worktree — no restart, no extra record, no fresh worktree per step, and no silent recorded-scope widening. Questions, code search, and unchanged-input checks are record-free; a mid-episode scope or approval change makes the next mutating command re-derive authority live and reject the stale attempt.
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

Invoke `tdd` for the red-green implementation method. Before the first test, agree the highest external test seam; invoke `codebase-design` when a seam, module boundary, or module interface changes, and `domain-modeling` when terminology changes. Keep one vertical slice at a time and do not replace Kosmic research, review, or completion gates. Red-first applies to NEW or changed behavior only: a failing-before test is required for the new changed behavior, while existing passing guards are preserved and never forced to fail.

### 2.1 Map Acceptance Criteria to Observable Verification

Map every criterion to an observable check. Add a permanent test for a
consumer-visible runtime boundary; reuse existing proofs while their inputs
and contracts remain unchanged. Policy and human-handoff criteria use real
workflow/producer exercises, never source-text or incidental-wording tests.

```markdown
AC: Given user is logged in, when they click logout, then session is cleared

Test: test_logout_clears_session()
- Setup: Create authenticated session
- Action: Call logout endpoint
- Assert: Session is null/empty
```

### 2.2 Write Failing Tests

Write tests for NEW or changed runtime behavior at the agreed external seam.

```bash
# Run tests to confirm the new-behavior tests fail
pytest tests/test_feature.py -v  # or project's test command
```

```
STOP CHECK: Do the NEW-behavior tests FAIL before implementation?
  → Only NEW changed behavior needs red first; existing passing guards stay green — never force them to fail
  → A new test that already passes against current code tests nothing new — sharpen or replace it
  → If new tests fail with expected errors → proceed to Phase 3
```

**Principles**:
- One observable check per acceptance criterion
- Permanent tests for new or changed consumer-visible runtime boundaries
- Real workflow/producer exercises for policy and human-handoff criteria
- Include edge cases discovered in research
- Follow existing test patterns in project
- Tests should be clear and self-documenting
- Never delete or weaken an existing passing safety test to make a new test red

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

Delegation to subagents is discretionary and must be justified per checkpoint: genuine independence, useful parallelism, or context isolation, each with a concrete bounded question or slice, explicit input/output, and a named integration owner in the existing launch trace. No phase-default fanout, tiny clerical delegation, nested exploration without benefit, or authority expansion; coupled work keeps one owner. Mandatory fresh-context proposer/reviewer independence and host-mandated delegation are unchanged, and no new delegation artifact is created.

### 3.1 Implement Following Patterns

Use patterns discovered in research phase:
- Follow existing code style
- Reuse existing utilities
- Apply architectural decisions from ADRs

Apply SKILL.md **Managed Run Before Scratch** while implementing. Begin the run before creating disposable output and use only its returned path; terminally succeed or fail it before final status. Keep pending tests under `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` with `MANIFEST.md`, commit those packages before finishing, and preserve durable evidence/spec/log rules.

**Spec-event step**: whenever a spec or work-item status changes, run `generate-status --project ...` so the working-directory STATUS.md stays drift-free (validation and the completion gate fail on `STATUS_STALE`).

**Commit cadence**: retain verified record-owned source, vault outputs and the
successful receipt in the isolated writer before final reporting. Load
[Receipt completion](work_completion.md) for scope, proof and integration.
Preserve unrelated changes in destination checkouts; integrate only owned,
baseline-checked deltas.

### 3.2 Verification Cadence

Focused checks run during implementation; the integrated suite runs once after the affected changes stabilize. Rerun only checks whose inputs or contracts changed or that previously failed — never reuse a pass over changed inputs and never skip scientific validation to save time.

```bash
# focused checks while implementing
pytest tests/test_feature.py -v  # or project's test command
# one integrated run once the affected changes stabilize
pytest  # full suite, or the project's integrated command
```

### 3.3 Keep It Simple

- YAGNI: Don't add features not in acceptance criteria
- KISS: Simplest solution that passes tests
- DRY: Extract common code, but not prematurely

### 3.4 STOP: Verify the Stabilized Change

Run focused checks during implementation and integrated verification once the
affected changes stabilize. Fix failures before review. Re-run affected checks
when their inputs/contracts change or a prior run failed; do not repeat an
unchanged passing full suite at every phase boundary. Scientific validation
remains mandatory.

### 3.5 Update Story

Open the story file and do **all three** of the following:

**a) Mark each IMPL-xxx task `[x]`** (use the exact task text from the story file):

```markdown
### Phase 3: Implementation

- [x] IMPL-001: {task description}   ← change [ ] to [x]
- [x] IMPL-002: {task description}   ← change [ ] to [x]
```

**b) Mark each Acceptance Criterion `[x]`** only after its observed behavior and required checks establish it; a passing test alone is not smoke proof:

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

Capture the actual pinned two-axis review decision while the governed implementation record remains live. The receipt transaction—not a hand-edited status—publishes `done`. A separate administrative `review` state grants no new implementation authority.

### 4.1 Confirm Verification Is Current

Use the stabilized integrated result from Step 3.4 if its inputs and contracts
are unchanged. Otherwise run the affected checks and required integrated
verification. Exercise the changed CLI/API/UI path and record its actual
output/state; do not replace this smoke with tests or add redundant coverage
runs when no applicable coverage requirement exists.

### 4.2 Convergent Code Review (MANDATORY - NO EXCEPTIONS)

```
STOP: Story CANNOT be marked "done" without Task 7's convergent review.
  → Round 1 performs one complete Standards axis and one complete Spec axis.
  → Record every finding in the stable ledger before requesting changes.
  → Later rounds verify open findings, changed code, and fix-introduced regressions.
  → Non-blocking suggestions do not prevent approval.
```

Use Task 7 (`references/task_review_spec.md`) rather than starting an ad hoc fresh review. Preserve finding IDs and update the same ledger each round. Worker responses to Blocking findings are claims, never closures: supply `fixed` with observable evidence, `refuted` with rationale and evidence, or — for a genuinely blocked prerequisite — `blocked` with escalation rationale, recorded and escalated instead of submitted as routine re-review. Only the independent reviewer closes a row (`resolved`, optionally `resolution: fixed|refuted`); a rejected refutation stays open/Blocking. One completed Standards + Spec pair is one automated round; your repairs and partial callbacks consume none. After the maximum automated round, escalate the remaining ledger instead of beginning another unrestricted review.

### 4.3 Update Knowledge

If the story produced durable, reusable knowledge:

1. Create/update atomic notes (Task 2: Add Note) — only for genuinely reusable knowledge (root cause, convention, decision, correction); a story yielding no reusable finding writes no note, and that is a valid outcome.
2. Update notation if new terms were introduced (same conditionality).
3. Link any created or updated notes from the story file.
4. Assign each changed note an explicit Audience Scope and regenerate the atomic Skill Pair.
5. If the story changes a Consumer Interface, set `consumer_interface_change: true` and list its current stable `usage` or `both` notes in `related_notes`.
6. Classify changed procedure mechanics. Declare `routine_edge_change: true` whenever the story adds or changes a procedure's `uses_routines` edge; this requires `routine_decision_required: true`. When reusable deterministic mechanics are introduced or materially changed, set `routine_decision_required: true`, query the generated inventory, and list one governed Task P artifact per unique proposal path in `routine_proposals`; otherwise keep the gate false and the list empty.
7. Record what was actually observed per acceptance criterion compactly in the story record (observation + source per criterion); task-specific review stays in the record, dataset-specific metadata stays with its dataset. Run Task 2 only for genuinely reusable knowledge — a story yielding no reusable finding writes no note.
8. Before marking the story done, ensure the completion gates are satisfied: one ordinary `work finish` validates the record-embedded completion observations, the two-axis independent review (`completion_review` with Standards and Spec axes), the source-revision binding, and the shared domain precheck. Standalone `check-completion` (see `references/task_project_skills.md`) remains an optional fail-fast diagnostic — never a required second command.

If nothing reusable emerged, record the observations per criterion, skip note creation, and state that outcome in the progress log.

### 4.4 Update Story

Open the story file and apply **all four** of the following:

**a) Mark Phase 4 review tasks `[x]`:**

```markdown
### Phase 4: Review

- [x] All tests pass
- [x] Code review completed
- [x] Knowledge notes updated (or: none needed — no reusable knowledge emerged)
```

**b) Mark the Definition of Done `[x]`:**

```markdown
## Definition of Done

- [x] All acceptance criteria met
- [x] All tests pass
- [x] Code reviewed and approved
- [x] Knowledge notes updated when reusable knowledge emerged (none otherwise)
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

**d) Capture the record-embedded completion observations and the real converged review artifact**, including qualified record identity, canonical path, pinned base, current reviewed revision, stable finding IDs and actual decisions. See `task_project_skills.md`; never synthesize approval.

---

## Step 5: Mark Done

Execute **all of the following in one pass** — do not skip any item:

### 5.1 Publish receipt-backed completion

Run `python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py work finish --project PROJECT_ROOT --worktree ROOT --work-record QUALIFIED_RECORD --scope CLAIM` (repeat for every declared scope). Do not set `done` directly. Keep the record in an active phase (`approved`/`in_progress`) when finishing: finish refuses a record set to `review` (`WORK_PHASE_DENIED`), holds the review decision in `completion_review`, and alone publishes `done` — never strand a record in `review`. One ordinary invocation runs embedded proof, primary scope, pinned two-axis review, the shared domain precheck, and the pre-write freshness recheck before publishing. Domain failures retain their diagnostic through `COMPLETION_PRECHECK_FAILED`. Keep STATUS current with `generate-status` after record edits; stale inputs are not auto-repaired by the precheck. Standalone `check-completion` is an optional fail-fast diagnostic, never required second choreography.

Finish publishes record status/indexes/log, then the authoritative receipt, then derived STATUS. Publication is stepwise, not cross-file atomic. A successful finish receipt is sufficient — no second receipt validation or STATUS inspection follows it. Only when finish was interrupted or refused, rerun finish: a valid terminal receipt and completion log remain unchanged while only derived reports regenerate. Unreceipted `done` stays pending.

### 5.2 Add Final Row to Story Progress Log

```markdown
## Progress Log

| Date | Action | Notes |
|------|--------|-------|
| ... | ... | ... |
| {DATE} | Done | Story complete |
```

### 5.3 Verify associated Epic progress

The completion transaction updates only the current Story's owner-local Epic row and associated index/STATUS/log outputs; the successful finish receipt covers these projections — no separate post-success audit. It does not approve or close the entire Epic, rewrite another feature's specs, or authorize unrelated implementation.

### 5.4 Update Daily Log

```markdown
## Session {N}
- Completed: [Story {N}](../subprojects/{SUBPROJECT_ID}/specs/stories/story-{N}.md) - {brief description}
- Added notes: [{note}](../notes/{note}.md)   ← only if knowledge notes were created
```

### 5.5 Hand off with individual full-absolute-path links

In the human-facing completion report, every receipted finished Story carries its own Markdown link whose visible label is the record file's full absolute path and whose target opens that actual file; when several Stories finish in one episode, list each file individually. After integration moves a record, report its final canonical link too. A directory, index, relative, shortened, or future path is never a substitute; CLI JSON output stays unchanged, and review approval is never presented as completion.

---

### Completion Checklist (verify before considering story done)

- [ ] Story frontmatter: `status: done`, `updated: {DATE}`
- [ ] All Phase 1–4 task checkboxes are `[x]` in the story file
- [ ] All Acceptance Criteria are `[x]` in the story file
- [ ] All Definition of Done items are `[x]` in the story file
- [ ] Progress Log has a "Done" row in the story file
- [ ] Epic stories table shows `done` for this story (published by finish; no separate audit)
- [ ] Epic progress count updated (published by finish)
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
- [ ] New/changed-behavior tests were red before implementation; existing passing guards untouched
- [ ] Edge cases covered

### After Implementation
- [ ] All tests pass
- [ ] Code follows project patterns
- [ ] No unnecessary complexity

### Before Marking Done
- [ ] Code review completed (MANDATORY)
- [ ] Review fixed point recorded before implementation
- [ ] Complete Round 1 finding ledger recorded
- [ ] All Blocking findings resolved or explicitly risk-accepted by the human; reaching the review-round limit only escalates and never grants completion
- [ ] Knowledge notes updated when reusable knowledge emerged (none otherwise)
- [ ] Human handoff links every receipted Story by its full absolute path
- [ ] Consumer Interface impact declared
- [ ] Completion gate passed
- [ ] Canonical Skill Pair regenerated after eligible knowledge changes
- [ ] Epic progress updated
- [ ] Log updated
