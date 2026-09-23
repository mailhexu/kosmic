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

---

## Quick Task File

Create one file per quick task:

```text
{VAULT}/Projects/{TARGET}/specs/quick-tasks/{YYYY-MM-DD}-{slug}.md
```

Create the `quick-tasks/` directory if missing.

Use `references/templates/template-quick-task.md`.

---

## Procedure

1. **Search first**
   - Run Task 3: Search for relevant notes and specs.
   - Read related code before planning the change.

2. **Create Quick Task record**
   - Write the quick task file using `references/templates/template-quick-task.md`.
   - Set `Status: draft`.
   - Define scope, out of scope, and acceptance criteria.
   - Declare `consumer_interface_change: true` when supported CLI, API, configuration, integration, or troubleshooting behavior changes; otherwise explicitly keep `false`.
   - For `true`, list the current stable Consumer knowledge in `related_notes`.
   - Pin `review_base` before implementation and set `review_round: 0`; do not move the baseline during re-review.
   - Declare `routine_edge_change: true` whenever the task adds or changes a procedure's `uses_routines` edge; this requires `routine_decision_required: true`. Declare `routine_decision_required: true` when the task introduces or materially changes reusable deterministic mechanics; list one governed Task P artifact per unique proposal path in `routine_proposals`. Otherwise keep both fields false and the list empty.
   - When the work produces raw experience worth keeping (review findings, test runs, debug transcripts), capture it as an Evidence Pack (`evidence/{YYYY-MM-DD}-{slug}/` with `MANIFEST.md`), declare the slug in `evidence_packs:`, and distill it with Task 9 before completion — `check-completion` enforces the linkage.

3. **Approval gate**
   - If the user already explicitly asked to implement the change, set `Status: approved` and proceed.
   - Otherwise present the quick task and wait for approval.

   - If the task exposes a material design trade-off, invoke `grill-with-docs` before approval. An ADR-worthy trade-off is not a Quick Task; promote it to Task 5: Create Spec.

4. **Diagnose bug fixes**
   - For a reported defect, invoke `diagnosing-bugs` before changing code.
   - Establish a reproducible failure, minimize it, distinguish hypotheses with evidence, and add a regression test at the agreed seam.
   - Do not complete a symptom-only patch.

5. **Implement**
   - Set `Status: in_progress`.
   - Make the minimal change that satisfies acceptance criteria.
   - Add or update tests when the codebase has a relevant test pattern.
   - Follow SKILL.md **Managed Run Before Scratch** for disposable scratch; it does not replace durable pending-test, Evidence Pack, specification, or log rules.

6. **Verify and review**
   - Run diagnostics and focused tests or an equivalent manual check.
   - Run the `check-completion` command from `references/task_project_skills.md`.
   - Set `Status: review` and run Task 7's complete two-axis Round 1 against `review_base`.
   - Record all Standards and Spec findings in one stable ledger with Blocking or Non-blocking disposition.
   - If changes are requested, preserve finding IDs; later rounds inspect only open findings, changed code, and regressions.
   - A Consumer Interface change cannot pass while related Consumer knowledge or the canonical pair is stale.
   - Approve when all Blocking findings are resolved even if Non-blocking suggestions remain.

7. **Complete**
   - Set `Status: done` only after verification and review pass.
   - Run `git status --short`; classify every modified/untracked file as committed, recoverably preserved, or deleted.
   - Update `{VAULT}/Projects/{TARGET}/specs/INDEX.md`.
   - Update the log.
   - Add notes for durable knowledge learned during the work.

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
