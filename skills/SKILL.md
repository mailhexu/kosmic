---
name: kosmic
description: Kosmic governance for vault-backed work. Use when a project requires Kosmic, or when managing its knowledge, specifications, Shared Skill Library, or reusable routines.
version: 6.1.0
license: MIT
compatibility: markdown-agent-skill, python>=3.11
---

# Kosmic

Knowledge-oriented, spec-driven infrastructure for coding. Kosmic manages authoritative Project Knowledge and a vault-level Shared Skill Library. One installed router (`memnotes-skills`) dynamically loads bounded Usage/Development topics and hash-pinned deterministic routines. Task 2 captures durable knowledge; Task P governs reuse, extension, or creation. Judgment and approval stay in prose. Works with OpenCode, Claude Code, Codex, and OMP. Complete guide: `README.md`.

**Path variables**: `{KOSMIC_SKILL_DIR}` is the directory containing this `SKILL.md`. `{PROJECT_ROOT}` is the owning vault Project directory `{VAULT}/Projects/{TARGET}` (the `--project` value). `{REGISTERED_ROOT}` is the registered writer worktree root (the `--worktree` value). `{VAULT}`, `{TARGET}`, `{PROJECT_ID}` resolve below.

---

## Entry Process (MANDATORY ORDER)

Resolve bootstrap BEFORE loading any audience skill or searching.

1. **Resolve the vault.**
   - Search project instructions for Kosmic Vault, Target, and Project ID fields.
   - Vault absent → check `$KOSMIC_VAULT`, then default `./memnotes`.
   - `TARGET` = configured vault Project folder; otherwise the current package name.
2. **Bootstrap or validate.**
   - `{VAULT}/Projects/{TARGET}/` missing → run [Task 1: Initialize](references/task_init.md).
   - Present but `ProjectEntry.md` lacks `project_id`, or the Usage/Development skill pair is missing/stale/mismatched, or the Shared Skill Library is unresolved → run the migration/validation in [Task 8](references/task_project_skills.md).
   - **Bootstrap exemption**: initialization (Task 1) and migration (Task 8) are exempt ONLY from the prerequisite they themselves establish (Project identity, skill pair, or library). They perform no other prerequisite-free work; after validation, resume all normal checks (remaining required-skills verification, search, audience loading) for any subsequent task.
3. **Before Contributor work, verify the required procedure-skill set** for the active Install Adapter:

   ```bash
   python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py check-required-skills --adapter {opencode|claude-code|codex|omp}
   ```

   Missing skills or unsupported adapter → stop and follow the required-procedure-skills section of the installed `README.md`. Required skills supply bounded methods and never replace Kosmic's vault records, approval gates, Shared Skill Library, or Projection CLI.

4. **Resolve identity.** `PROJECT_ID` = immutable `project_id` from `ProjectEntry.md`; `USAGE_SKILL = {PROJECT_ID}-usage`; `DEVELOPMENT_SKILL = {PROJECT_ID}-development`.
5. **Load the audience skill** matching the work, then search (Task 3):
   - **Contributor work** (planning, changing, testing, reviewing, releasing Project code) → load `{DEVELOPMENT_SKILL}`; follow its required reference to `{USAGE_SKILL}` whenever the work invokes or changes a Consumer Interface.
   - **Consumer work** (invocation/configuration/integration/troubleshooting without implementation change) → load `{USAGE_SKILL}`. Read-only questions/checks need no spec workflow; persistent configuration or experiment outputs still need compatible bounded record/scope authority and never imply feature-implementation approval.
   - **Knowledge/spec maintenance** → use Kosmic tasks and load the Project skill matching the knowledge audience.
   - Missing, stale, mismatched, or unresolved skill pair → stop and run validation or migration. Never continue contributor work without Project guidance.

**STOP**: Do not proceed past step 2 until the vault Project, immutable Project Identifier, and Usage/Development skill pair resolve; contributor workflows must also resolve a valid Shared Skill Library.

---

## Paths

| Item | Path |
|------|------|
| Vault | `{VAULT}` |
| Target | `{TARGET}` |
| Project ID | `project_id` in `{VAULT}/Projects/{TARGET}/ProjectEntry.md` |
| Shared Skill Library | `{VAULT}/Skills/` |
| Shared Skill Router | `{VAULT}/Skills/SKILL.md`; installed as `memnotes-skills` |
| Domain Skill | `{VAULT}/Skills/{DOMAIN}/SKILL.md` |
| Skill Topics | `{VAULT}/Skills/{DOMAIN}/{usage\|development}/*.md` |
| Shared records (Quick Tasks, proposals, shared-authority research) | `{VAULT}/Projects/{TARGET}/specs/` |
| Feature records (PRD/Architecture/Epics/Stories, feature-linked research) | `{VAULT}/Projects/{TARGET}/subprojects/{SUBPROJECT_ID}/specs/` — owner-local hierarchy reserved by `spec-create --kind prd`; derive all child records inside it |
| Legacy migration pair | `{VAULT}/Projects/{TARGET}/skills/` |
| Projection CLI | `scripts/kosmic_project_skills.py` in the installed Kosmic skill |
| Notes / Index / Notation | `{VAULT}/Projects/{TARGET}/notes/{TOPIC}.md`, `index.md`, `notation.md` |
| Log | `{VAULT}/Projects/{TARGET}/log/{TARGET}-{YYYY-MM-DD}.md` |
| Research memo | feature-linked: `subprojects/{SUBPROJECT_ID}/specs/research/{YYYY-MM-DD}-{slug}.md`; shared-authority only: `specs/research/{YYYY-MM-DD}-{slug}.md` |
| Pending tests | `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` |

**CLI invocation**: every command shown here (`work start`, `generate-status`, `validate-library`, …) is a **subcommand of the single Projection CLI** — never a standalone executable. Run it as `python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py <subcommand> …`.

**Project Knowledge format**: `notes/` is one authoritative bundle, Obsidian-readable and OKF v0.2 conformant; `index.md` is the reserved progressive-disclosure entry point; every other note starts with YAML frontmatter on line 1, declares a non-empty `type`, uses `status: draft | stable | deprecated`, and links with relative standard Markdown. No separate OKF export tree.

---

## Authority & Isolation (apply to every task)

**Record-first authority.** Before a substantive source, docs, vault, configuration, or experiment change, select or create its governing record. Feature implementation needs an approved owner-local Story → Epic → Architecture → PRD chain. A standalone low-risk change needs an approved Quick Task; PRD creation/success never approves code. Questions, searches, and unchanged checks need no record and stay read-only — never hide durable cleanup, publication, or installation in them. Planning creates only its draft hierarchy and bounded planning outputs; bootstrap establishes a bounded governing Quick Task whose scope does not authorize unrelated implementation.

**Owner-aware catalog.** Feature records live under `subprojects/{SUBPROJECT_ID}/specs/` (owner-local); shared Quick Tasks/proposals live under `specs/`. Existing flat feature specs stay bootstrap until separately approved migration. Notes, mathdocs, and canonical skills stay shared at the Project root. Register each exact working directory; a fixed subproject constrains a directory, never selects its task; never persist selection in a shared mutable pointer.

**Isolation.** Start writable changes with:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py work start --project {PROJECT_ROOT} --worktree {REGISTERED_ROOT} --work-record {QUALIFIED_RECORD}
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py work show --project {PROJECT_ROOT} --work-record {QUALIFIED_RECORD}
```

Each mutating command takes the same explicit `--work-record`, re-resolving authority at invocation time — never cached approval. One clean worktree per record, one writer per worktree. `work start` refuses a dirty worktree and lists conflicting paths; never write in a worktree containing unrelated in-progress work — use a separate clean worktree with a separate writer and leave unrelated work untouched. Raw editor/shell writes remain agent compliance, not an OS sandbox.

**Completion.** Declare intended outputs with `--scope` on `work finish`; it checks the Git diff against those claims. A checkbox or command exit code alone is not acceptance evidence; reports must name qualified identity, canonical path, and observed acceptance/smoke/review results. Never edit `done` by hand; the `work finish` receipt is the completion marker, so unreceipted `done` is pending. If interrupted, rerun finish — there is no recovery journal or `work recover`.

**Record-owned commits.** Capture the destination baseline before edits and commit only record-owned source and vault outputs in the isolated writer. Before integration compare each destination path with that baseline; reconcile source drift rather than overwriting it. `work start` checks authority and cleanliness; it does not capture a baseline or maintain a work session. Preserve unrelated work. Commit verified records, evidence, logs and receipts before ending a session with vault changes.

Before constructing any proof of finish or running `work finish`, load [Work Completion](references/work_completion.md) and follow it.

---

## Managed Scratch & Hygiene

Before creating Kosmic-owned scratch, runtime output, generated intermediates, or a temporary Git index:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py scratch begin --project {VAULT}/Projects/{TARGET} --purpose {task-slug} --work-record {QUALIFIED_RECORD}
```

**Done when**: JSON reports `code: OK`; write disposable material only below the returned run path. `NO_GIT_WORKTREE` is a stop condition: place the vault in a Git worktree whose root ignores `.tmp/`. Before final status run `scratch succeed` or `scratch fail`; **done when** it reports `code: OK` with terminal Git evidence.

Durable source and documentation remain in the project tree. Pending tests remain under `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` with `MANIFEST.md` and must be committed; specs, mathdocs, and logs retain their own governance. Destination-sibling atomic-publication staging is not run scratch. Load [Managed Run Lifecycle](references/managed_run_lifecycle.md) only when retention, promotion, status, or recovery detail is needed.

**Math formatting**: write display equations with `$$` delimiters on their own lines; use inline `$...$` only for short symbols embedded in prose. Never leave standalone LaTeX equations as raw paragraphs.

---

## Tasks

Pick exactly one task per unit of work; the linked reference is authoritative for procedure detail. Do not improvise from the table.

| Task | Trigger | Load | Complete when (observable) |
|------|---------|------|----------------------------|
| **0: Quick Task** | Small, low-risk implementation user explicitly requested or clearly below spec-hierarchy scope; concrete scope, obvious acceptance, no new architecture/data models/APIs | [task_quick_task.md](references/task_quick_task.md) · template: [template-quick-task.md](references/templates/template-quick-task.md) | Approved Quick Task record; implemented change verified; review + verification passed; completion = successful `work finish` receipt (`status: done` only with receipt); log/notes updated |
| **1: Initialize** | New Project/package, or no Kosmic structure / Project Identifier exists | [task_init.md](references/task_init.md) | Real stable knowledge exists; Project structure, immutable Project Identifier, dual-native OKF/Obsidian notes, AGENTS.md integration, specs index in place |
| **2: Add Note** | Verified durable, reusable knowledge emerged (root cause, convention, decision, correction) not already represented | [task_add_note.md](references/task_add_note.md) | One atomic note per concept (update, never duplicate); TOC + log updated; one-off activity/session state/error text kept out of notes |
| **3: Search** | Before ANY implementation or change, or when unsure | [task_search.md](references/task_search.md) | Relevant notes/specs read: TOC first → deep notes search → specs search |
| **4: Review** | End of session/week, returning to project, knowledge seems outdated | [task_review.md](references/task_review.md) | Notes extracted, stale notes updated, log hygiene done |
| **5: Create Spec** | New feature/project planning; user requests spec creation | [task_create_spec.md](references/task_create_spec.md) | Draft hierarchy under owner-local `subprojects/{ID}/specs/`: PRD → optional Research → Architecture → Epics → Stories, bidirectionally linked, `draft` status, specs index + log updated; each gate explicitly user-approved |
| **6: Implement Story** | Story `status: approved` | [task_implement_story.md](references/task_implement_story.md) | Tests + implementation + story/notes updates complete; convergent Task 7 code review passed; completion = successful `work finish` receipt — Task 7 approves the review but never itself marks the story `done` |
| **7: Review Spec** | Spec review requested, "review"/"approve", or code review after implementation | [task_review_spec.md](references/task_review_spec.md) | Pinned review base; complete Standards + Spec axes; stable finding IDs; decision recorded — `draft → approved` (spec review) or code-review decision recorded, without itself marking `done`; after 3 automated rounds, remaining ledger escalated, never a fresh review |
| **8: Migrate Project Skills** | Existing Project lacks immutable identity, OKF conformance, or Shared Library assignment | [task_project_skills.md](references/task_project_skills.md) | Identity recorded, notes normalized, complete explicit domain/topic assignment map, valid atomic catalog, behavior-compared atomic publication, one router installed; ambiguous Wikilinks/unassigned legacy references stop migration with no partial authoritative change |
| **R: Research** | After PRD, before Architecture, when Task 3 was insufficient (unclear feasibility, unfamiliar libraries, competing approaches, risky assumptions) | [task_research.md](references/task_research.md) | Research memo at `{SPEC_ROOT}/research/{YYYY-MM-DD}-{slug}.md` under the owning subproject (shared `specs/research/` only for shared-authority research), linked from Architecture; no new gate — findings feed PRD/Architecture review |
| **M: Math Note** | Reusable symbolic result created/corrected, note or implementation relies on an equation, or equation-level discrepancy appears | [task_math_note.md](references/task_math_note.md) | Derivation-first: executable SymPy file authoritative, generated results never hand-edited; `check-math`, structural validation, human review (assumptions/units/domains), and completion linkage pass; stable dependent notes carry exact result/exposition markers; math-derived implementation declares derivations + finite implementation files |
| **P: Propose Skill Change** | Implemented work yields a verified reusable procedure, or work item declares `proposal_required: true` | [task_propose_skill.md](references/task_propose_skill.md) | Exactly one atomic `create`/`update`/`no_action` proposal from a curated fresh-context proposer; canonical/installed skills never edited directly; `proposal_required: true` work completes only with one valid proposal; shared/global proposals need a separate proposer subagent, behavioral evidence, human approval, and Task 7 review — knowledge, guidelines, or evidence never trigger publication |

Task P authority: repeated failure is a Task P signal only when a general invariant, recovery, reproducer, and verification matrix show the repair generalizes; it never causes automatic publication. Rejected equivalent interventions require materially new evidence before reconsideration.

Optional curation: outside the task table, a manual or externally scheduled curation routine (`references/curation_routine.md`: prepare → agent semantic review → finalize) may nominate candidate notes for Task P between runs, over the exact `(last-success, run-start]` interval with a persisted per-scope checkpoint. It is separate from note writing, never a required task or gate, and nominates only — no automatic approval, publication, installation, or scheduler.

---

## Spec-Driven Workflow & Gates

**Feature gate rule**: feature work proceeds strictly in order — PRD → optional Research (post-PRD, no new gate) → Architecture → per-Story approval → implementation (Research → TDD → Code) → convergent code review — and you MUST pause for the user's explicit decision at the PRD, Architecture, and per-Story gates before the next step, NEVER skipping the hierarchy, implementing feature code without an approved story (approved Quick Task allowed for small, low-risk work), or marking `done` without convergent review; if research changes product scope, update and re-approve the PRD, and if it changes technical direction, feed the findings into Architecture review. Human-facing walkthroughs and gate-by-gate session scripts live in the installed `README.md`; load them only when guiding a user through the workflow.

**Status policy** — use only these statuses; never invent others (e.g. `blocked`: keep current status, add a blocker note to the artifact and a log entry).

| Artifact | Statuses |
|----------|----------|
| Specs, stories, quick tasks | `draft`, `approved`, `in_progress`, `review`, `done` (approval gates apply to PRD, Architecture, Stories, and code review; quick-task review/verification still mandatory) |
| Research memos | `draft`, `done` (no approval gate) |
| Notes | `draft`, `stable`, `deprecated` (currentness is `stale_after`, not a fourth status) |

Lifecycle: `draft → approved → in_progress → review → done`, with `changes requested` returning to `approved` from `in_progress`/`review`.

---

## Publication & Install Safety

When initializing a new project, use [agents_template.md](references/agents_template.md) to add the Kosmic Integration section to that project's `AGENTS.md`. The Shared Skill Library is authoritative in the vault. Install only its generated `memnotes-skills` router; Domain Skills and detailed topics load dynamically through a verified Resolution Plan. Never hand-edit generated catalogs, manifests, router packages, or installed copies, and never edit installed user-authored skills. Migration and installation retain their separate approved target plans, including disposable adapter validation.
