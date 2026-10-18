# Task 0: Quick Task

Use this procedure for small, low-risk implementation work that does not justify the full PRD → optional Research → Architecture → Epics → Stories workflow.

Quick Task is an escape hatch, not a shortcut around quality. Search, acceptance criteria, verification, review, logging, and knowledge capture still apply.

---

## When to Use

Use Quick Task only when all are true:

- The user asked for a concrete fix, change, or small addition.
- Scope is narrow and can be completed in one focused session.
- Acceptance criteria are obvious or can be stated in a few bullets.
- The change is low risk and does not need product or architecture discussion.
- The work does not introduce a new feature area, data model, public API, security boundary, or broad user-facing workflow.

If any item is false or uncertain, use Task 5: Create Spec instead.

---

## Do Not Use For

- New feature areas
- Multi-module product behavior
- Architecture decisions or ADR-worthy tradeoffs
- Database, persistence, or data model changes
- Public API or protocol changes
- Security-sensitive behavior
- Requirements that need user discovery or approval gates

Deterministic subproject flat-spec migration is such a governed workflow: it uses exactly one shared Quick Task created and approved per `task_project_skills.md` ("Subproject Flat-Spec Migration"), with the approved plan `digest` recorded in the record; the Quick Task path here covers its approval gate only, never direct application of a plan.

---

## Quick Task File

Create one file per quick task:

```text
{VAULT}/Projects/{TARGET}/specs/quick-tasks/{YYYY-MM-DD}-{slug}.md
```

Quick Tasks are shared, Project-level specs — create them without
`--subproject`; they never live in a subproject owner root. `spec-create`
creates the `quick-tasks/` directory; do not create it by hand.

Use `references/templates/template-quick-task.md`.

---

## Procedure

1. **Search first**
   - Run Task 3: Search for relevant notes and specs.
   - Read related code before planning the change.

2. **Create Quick Task record**
   - Establish the draft with `spec-create --project {PROJECT_ROOT} --kind quick-task --title {TITLE}`; retain the returned qualified identity/canonical path. Use the template for its body, not to guess owner/ID fields.
   - Flat legacy feature specs may prevent the owner-aware catalog from loading. Shared Quick Task creation remains a bounded draft bootstrap in that case; it does not migrate feature specs, enable the catalog, or authorize implementation. After explicit approval, `work start` resolves the flat task through the migration fallback.
   - Keep `status: draft` until the compatible approval gate passes.
   - Define exact roots, allowed outputs, out-of-scope work, and observable acceptance criteria.
   - Declare `consumer_interface_change: true` when supported CLI, API, configuration, integration, or troubleshooting behavior changes; otherwise explicitly keep `false`.
   - For `true`, list the current stable Consumer knowledge in `related_notes`.
   - Pin `review_base` before implementation and set `review_round: 0`; do not move the baseline during re-review.
   - Declare `routine_edge_change: true` whenever the task adds or changes a procedure's `uses_routines` edge; this requires `routine_decision_required: true`. Declare `routine_decision_required: true` when the task introduces or materially changes reusable deterministic mechanics; list one governed Task P artifact per unique proposal path in `routine_proposals`. Otherwise keep both fields false and the list empty.
   - When the work yields durable reusable knowledge (root cause, convention, decision, correction), capture it atomically with Task 2: Add Note; dataset-specific observations stay embedded or adjacent to their data, and task-specific review stays in this record. No pack, sidecar, or forced note is produced — a session with no reusable finding manufactures no note.

3. **Approval gate**
   - If the user already explicitly asked to implement the change, set `Status: approved` and proceed.
   - Otherwise present the quick task and wait for approval.

   - If the task exposes a material design trade-off, invoke `grill-with-docs` before approval. An ADR-worthy trade-off is not a Quick Task; promote it to Task 5: Create Spec.

4. **Diagnose bug fixes**
   - For a reported defect, invoke `diagnosing-bugs` before changing code.
   - Establish a reproducible failure, minimize it, distinguish hypotheses with evidence, and add a regression test at the agreed seam.
   - Do not complete a symptom-only patch.

5. **Implement**
   - Before substantive writes, use `work start --project PROJECT_ROOT --worktree ROOT --work-record REF`. The start check requires a clean worktree.
   - Use one worktree and one writer per record. Every mutating command re-resolves the approved record with `--work-record`; completion checks the Git diff against its `--scope` claims.
   - Preserve unrelated work: never commit, stash, discard, or rebase changes you did not make. If the target worktree is dirty with unrelated changes, commit/stash only with the user's work preserved, or select another worktree via `work start`. Raw editors/shell are agent compliance, not OS enforcement.

6. **Verify and review**
   - Exercise the actual path and focused checks. Record each criterion's observation and source as an entry in the record's `completion_observations` list; exit success alone is not proof.
   - Run Task 7's independent Standards/Spec review against the pinned base. Preserve its stable finding ledger, actual decision and reviewed revision in the record's `completion_review` mapping as described in `work_completion.md`. Never manufacture approvals.
   - Re-review preserves finding IDs; accept only resolved blockers or explicit recorded human acceptance. Consumer knowledge/projection gates still apply.

7. **Complete**
   - Run read-only `check-completion` for existing gates, then `work finish --project PROJECT_ROOT --worktree ROOT --work-record REF --scope CLAIM` (repeat scope). Never hand-edit `done`.
   - Finish verifies evidence/review/scope first, then updates status/index/log, publishes its authoritative receipt, and derives STATUS from it — stepwise, not cross-file atomic. Interruption before the receipt leaves completion pending; interruption after it can leave stale derived reports only. Rerun finish — an already-valid receipt is kept while the derived reports regenerate.
   - Report qualified identity/canonical path and actual acceptance/smoke/review results; terminal authority cannot start new implementation.
   - For the exact proof mechanics — evidence schemas, review ledger fields, receipt rules, and `work finish` scope claims — follow `references/work_completion.md`.
   - Capture durable knowledge; classify changes without bulk-committing others' work. Read-only questions/checks need no new record or durable cleanup.

---

## Status Lifecycle

```text
draft → approved → in_progress → review → done
         ↑             ↓           │
         └─────────────┴───────────┘ (changes requested)
```

---

## Log Entry

Add a log entry with:

- Quick Task file path
- Summary of the change
- Verification performed
- Specs index update
- Links to any notes created or updated
