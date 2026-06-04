# Task: Review Spec

Review specifications, optional research memos, and code. Mandatory for story completion.

## When to Use

- Reviewing a spec document (PRD, Architecture, Epic, Story)
- Reviewing a Research memo for completeness before Architecture
- Story implementation complete, needs code review
- User says: "review this", "approve spec", "code review"

---

## Part 1: Spec Review

Review spec documents before implementation begins.

### PRD Review Checklist

| Aspect | Check |
|--------|-------|
| Problem | Is the problem clearly stated? |
| Goals | Are goals specific and measurable? |
| Non-goals | Is scope clearly bounded? |
| Requirements | Are FRs/NFRs complete and prioritized? |
| Success Criteria | Can each criterion be objectively verified? |
| Open Questions | Are all blockers identified? |

**Decision**: 
- ✅ **Approve** → status: `approved`
- ⚠️ **Request Changes** → Add comments, keep `draft`
- ❌ **Reject** → Major rework needed

### Architecture Review Checklist

| Aspect | Check |
|--------|-------|
| ADRs | Is every significant decision documented? |
| Context | Is the "why" clear for each decision? |
| Alternatives | Were alternatives considered and evaluated? |
| Consequences | Are trade-offs documented? |
| Test Strategy | Is testing approach defined? |
| Risks | Are risks identified with mitigations? |

**Decision**:
- ✅ **Approve** → status: `approved`
- ⚠️ **Request Changes** → Add comments
- ❌ **Reject** → Fundamental issues

### Research Memo Checklist (Non-Gating)

Research review does not approve or block the main spec lifecycle. It checks whether the memo is useful input for Architecture.

| Aspect | Check |
|--------|-------|
| Question | Is the uncertainty or decision clearly stated? |
| Sources | Are notes, code, docs, or examples cited? |
| Findings | Are findings specific and evidence-backed? |
| Options | Are viable options compared with trade-offs? |
| Recommendation | Is the recommended direction justified? |
| Impact | Is Architecture/ADR impact clearly stated? |
| Open Questions | Are unresolved blockers captured? |

**Decision**:
- ✅ **Complete** → status: `done`, link from Architecture
- ⚠️ **Needs More Research** → keep `draft`, list missing evidence/questions

### Epic Review Checklist

| Aspect | Check |
|--------|-------|
| Value | Does this epic deliver standalone value? |
| Scope | Is in/out of scope clear? |
| Stories | Can this be broken into stories? |
| Success | Are completion criteria defined? |

**Decision**:
- ✅ **Approve** → status: `approved`
- ⚠️ **Request Changes** → Add comments

### Story Review Checklist

| Aspect | Check |
|--------|-------|
| User Story | Is it in proper format (As a... I want... So that...)? |
| Acceptance Criteria | Are all criteria testable? |
| Tasks | Are research/test/impl/review phases present? |
| DoD | Is Definition of Done complete? |
| Links | Are epic/architecture/PRD linked? |

**Decision**:
- ✅ **Approve** → status: `approved`, ready for implementation
- ⚠️ **Request Changes** → Add comments

---

## Part 2: Code Review

**MANDATORY**: Story cannot reach `done` status without code review.

### When to Review Code

- Story implementation complete (all tests pass)
- Story status is `review`
- Before marking story as `done`

### Code Review Process

#### 2.1 Preparation

```bash
# Check which files changed
git diff --name-only

# Check tests pass
pytest  # or project's test command

# Review test coverage
pytest --cov  # if configured
```

#### 2.2 Review Checklist

| Category | Check |
|----------|-------|
| **Functionality** | |
| | Does code meet all acceptance criteria? |
| | Are edge cases handled? |
| | Are error cases handled? |
| **Tests** | |
| | Do tests cover all acceptance criteria? |
| | Are edge cases tested? |
| | Are tests clear and maintainable? |
| | Do all tests pass? |
| **Code Quality** | |
| | Is code readable? |
| | Are names descriptive? |
| | Is code DRY (no unnecessary duplication)? |
| | Is code simple (no unnecessary complexity)? |
| | Are functions focused (single responsibility)? |
| **Patterns** | |
| | Does code follow project conventions? |
| | Does code match architectural decisions? |
| | Are existing utilities reused? |
| **Security** | |
| | Are inputs validated? |
| | Are secrets handled properly? |
| | Are there injection risks? |
| **Performance** | |
| | Are there obvious performance issues? |
| | Are resources properly managed? |

#### 2.3 Decision

**Approve**:
```markdown
## Review Result

**Status**: ✅ Approved

**Summary**: Implementation meets all acceptance criteria.

**Highlights**:
- Good test coverage
- Follows existing patterns
- Clean implementation

**Reviewer**: {name/ai}
**Date**: {DATE}
```

Update story status to `done`.

**Request Changes**:
```markdown
## Review Result

**Status**: ⚠️ Changes Requested

**Required Changes**:
1. [Critical] {issue}: {location} - {fix needed}
2. [Important] {issue}: {location} - {fix needed}

**Suggestions** (optional):
- {suggestion}

**Reviewer**: {name/ai}
**Date**: {DATE}
```

Update story status back to `in_progress`.

**Reject** (rare, major issues):
```markdown
## Review Result

**Status**: ❌ Rejected

**Reason**: {fundamental issue}

**Recommended Action**: {what to do}

**Reviewer**: {name/ai}
**Date**: {DATE}
```

Update story status to `draft` or create new story.

---

## Review Output Format

Add review section to story file:

```markdown
## Code Review

### Review 1

**Date**: {DATE}
**Reviewer**: {name}

**Status**: ✅ Approved / ⚠️ Changes Requested / ❌ Rejected

**Checklist**:
- [x] Functionality: Meets acceptance criteria
- [x] Tests: All tests pass, good coverage
- [x] Code Quality: Clean and readable
- [x] Patterns: Follows project conventions
- [x] Security: No issues
- [x] Performance: No issues

**Comments**:
- {comment 1}
- {comment 2}

**Required Changes** (if any):
1. {change 1}
2. {change 2}
```

---

## Status Transitions

### After Spec Review

```
draft ──[approve]──→ approved
draft ──[changes]──→ draft (with comments)
```

### After Code Review

```
review ──[approve]──→ done
review ──[changes]──→ in_progress
review ──[reject]───→ draft (rare)
```

---

## Update Log

```markdown
## Session {N}
- Reviewed: [[specs/stories/story-001|Story 001]] - ✅ Approved
- Reviewed: [[specs/prd|PRD]] - ⚠️ Changes requested
```

---

## Checklist

### After Spec Review
- [ ] All checklist items evaluated
- [ ] Decision documented in spec
- [ ] Status updated
- [ ] Log updated

### After Code Review
- [ ] All code reviewed
- [ ] All tests verified passing
- [ ] Review result documented in story
- [ ] Story status updated
- [ ] Log updated
