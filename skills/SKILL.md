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

**Read-only inspection fast path:** to answer a question from authoritative notes/specs, resolve their configured paths and read them directly. Missing or stale identity/projections/router are observations, not permission to initialize, migrate, install or repair anything. A missing Project has no recorded knowledge. This path authorizes no execution, publication or mutation; operations that consume generated skills or routed material follow the entry process below.
**Idea capture fast path:** for `kosmic idea <description>` or an equivalent explicit save request, follow [Idea capture](references/task_idea.md) before any bootstrap/Contributor prerequisites. Resolve the configured or explicitly selected Project; for an explicit general idea resolve the vault instead, without requiring a Project. Clarify an ambiguous destination before writing. The bounded capture creates one note and its missing child directory only, with no work record, registration, clean-Git check, review, repair or session bookkeeping; return the saved full-path link and stop.

1. **Resolve the vault.**
   - Search project instructions for Kosmic Vault, Target, and Project ID fields.
   - Vault absent → check `$KOSMIC_VAULT`, then default `./memnotes`.
   - `TARGET` = configured vault Project folder; otherwise the current package name.
2. **Bootstrap or validate.**
   - `{VAULT}/Projects/{TARGET}/` missing → run [Task 1: Initialize](references/task_init.md).
   - Present but `ProjectEntry.md` lacks `project_id`, or the Usage/Development skill pair is missing/stale/mismatched, or the Shared Skill Library is unresolved → run the migration/validation in [Task 8](references/task_project_skills.md).
   - **Routine initialization** follows Task 1 directly, without a Quick Task, implementation review, or `work start`/`work finish`. Its authority covers only initialization outputs; migration and unrelated changes retain their own gates.
3. **Required procedure skills**: check once at init/migration or before Contributor work if the active adapter environment has not yet been verified. Reuse that result while the adapter and installed skills are unchanged; rerun on an actual skill-resolution error or an environment change:

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

**STOP (outside direct read-only inspection and explicit capture-only `idea`):** do not load generated guidance or execute Project operations until the Project identity and required Skill Pair resolve; contributor workflows and routed-library operations must also resolve their required Shared Skill Library. Neither fast path authorizes other operations or bypasses their prerequisites.

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
| Project ideas (lazy) | `{PROJECT_ROOT}/ideas/<title-slug>.md` |
| General ideas (lazy, no Project) | `{VAULT}/GeneralIdeas/<title-slug>.md` |
| Log | `{VAULT}/Projects/{TARGET}/log/{TARGET}-{YYYY-MM-DD}.md` |
| Research memo | feature-linked: `subprojects/{SUBPROJECT_ID}/specs/research/{YYYY-MM-DD}-{slug}.md`; shared-authority only: `specs/research/{YYYY-MM-DD}-{slug}.md` |
| Pending tests | `pending_tests/<project>/<YYYY-MM-DD>-<slug>/original-paths/<original-path>` |

**CLI invocation**: every command shown here (`work start`, `generate-status`, `validate-library`, …) is a **subcommand of the single Projection CLI** — never a standalone executable. Run it as `python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py <subcommand> …`.

**Command contract.** Use the complete invocation in the owning task reference, substituting its path variables; consult `--help` only for an undocumented operation. Exit 0 is authoritative for that command's documented outputs: use the returned identities, paths, and receipts without a second listing, read-back, validation, or confirmation command. Read generated drafts to edit their content, not to check that creation worked.

On error, follow the diagnostic and documented recovery; do not assume failure rolled back writes (`work finish` publishes stepwise). This trusts operation results, not new implementation or scientific claims: their acceptance checks, approvals, and reviews remain required.

**Project Knowledge format**: `notes/` is one authoritative bundle, Obsidian-readable and OKF v0.2 conformant; `index.md` is the reserved progressive-disclosure entry point; every other note starts with YAML frontmatter on line 1, declares a non-empty `type`, uses `status: draft | stable | deprecated`, and links with relative standard Markdown. No separate OKF export tree.

---

## Authority & Isolation (apply to every task)

**Record-first authority.** Before a substantive source, docs, vault, configuration, or experiment change, select its governing record — reuse the existing approved record that already authorizes the work, and create a new one only when none covers the scope. Feature implementation needs an approved owner-local Story → Epic → Architecture → PRD chain. A standalone low-risk change needs an approved Quick Task; choose by actual scope and risk. PRD creation never approves code. Questions, searches, and unchanged checks need no record and stay read-only. Planning creates only its draft hierarchy and bounded planning outputs. Routine Task 1 initialization is a bounded record-free exception; explicit idea capture is also bounded to one selected Project/general idea note and its destination directory. Developing or changing initialization behavior and all other mutations retain their normal gates.

**One bounded episode.** A record starts work once: resuming continues inside its recorded scope and the existing worktree — no restart per step, no extra record, no fresh worktree per step, and no silent widening of recorded scope (a real scope change updates and re-approves the record). A mid-episode scope or approval change makes the next mutating command reject the stale or over-broad attempt, because every mutating command re-derives identity, ancestry, scope, and approval live at invocation — context is reused while valid; permission is never cached.

**Owner-aware catalog.** Feature records live under `subprojects/{SUBPROJECT_ID}/specs/` (owner-local); shared Quick Tasks/proposals live under `specs/`. Existing flat feature specs stay bootstrap until separately approved migration. Notes, mathdocs, and canonical skills stay shared at the Project root. Register each exact working directory; a fixed subproject constrains a directory, never selects its task; never persist selection in a shared mutable pointer.

**Isolation (record-governed work).** Start writable changes with:

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py work start --project {PROJECT_ROOT} --worktree {REGISTERED_ROOT} --work-record {QUALIFIED_RECORD}
```

Each mutating command takes the same explicit `--work-record`, re-resolving authority at invocation time — never cached approval. Work in the current checkout by default; create a new worktree only when the user asks. `work start` refuses a dirty worktree and lists conflicting paths; never write in a worktree containing unrelated in-progress work — leave unrelated work untouched and ask the user how to clear it before starting. Run at most one record-governed session per checkout at a time. Raw editor/shell writes remain agent compliance, not an OS sandbox.

**Completion.** One ordinary `work finish` runs the full safety gate set — embedded proof, scope, the pinned two-axis review, and the shared domain precheck — before publishing; standalone `check-completion` is an optional diagnostic, never a required second command. Declare intended outputs with `--scope` on `work finish`; it checks the Git diff against those claims. A checkbox or command exit code alone is not acceptance evidence; reports must name qualified identity, canonical path, and observed acceptance/smoke/review results. Never edit `done` by hand; the `work finish` receipt is the completion marker, so unreceipted `done` is pending. If interrupted, rerun finish — there is no recovery journal or `work recover`.

**Record-owned commits.** Capture the baseline before edits and commit only record-owned source and vault outputs in the writer checkout. When a separate worktree was used, compare each destination path with that baseline before integration; reconcile source drift rather than overwriting it. `work start` checks authority and cleanliness; it does not capture a baseline or maintain a work session. Preserve unrelated work. Commit verified records, evidence, logs and receipts before ending a session with vault changes.

Before constructing any proof of finish or running `work finish`, load [Work Completion](references/work_completion.md) and follow it.

---

## Lean Delegation & Verification Cadence

**Justified delegation.** Use a subagent checkpoint only for genuine independence, useful parallelism, or context isolation, and only with a concrete bounded question or slice, explicit input/output, and a named integration owner in the existing launch trace. No phase-default fanout, tiny clerical delegation, nested exploration without benefit, or authority expansion; coupled work keeps one owner. Mandatory fresh-context proposer/reviewer independence and host-mandated delegation are unchanged, and no new delegation artifact is created.

**Stopping rule.** After the approved scope and required checks/review pass, finish it. Non-blocking suggestions remain advisory in the existing ledger; they do not automatically cause extra edits, tasks, review rounds or publication. Any chosen source change still requires the applicable revision-bound review.

**Verification cadence.** Focused checks run during the work; the integrated suite runs once after the affected changes stabilize. Rerun only checks whose inputs or contracts changed or that previously failed — never reuse a pass over changed inputs, and never skip scientific validation to save time.

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
| **Idea: Capture** | Explicit `kosmic idea` or equivalent save request | [task_idea.md](references/task_idea.md) | One Project/general idea saved; return its full-path Markdown link and stop; no implementation workflow |
| **0: Quick Task** | Small, low-risk implementation user explicitly requested or clearly below spec-hierarchy scope; concrete scope, obvious acceptance, no new architecture/data models/APIs | [task_quick_task.md](references/task_quick_task.md) · template: [template-quick-task.md](references/templates/template-quick-task.md) | Approved record; implemented change and required review/verification passed; successful `work finish` receipt; capture durable knowledge only when needed, with completion bookkeeping owned by finish |
| **1: Initialize** | New Project/package, or no Kosmic structure / Project Identifier exists | [task_init.md](references/task_init.md) | Requested structure, real knowledge, Project identity, skills and instructions established; successful CLI result accepted directly; no Quick Task or review |
| **2: Add Note** | Verified durable, reusable knowledge emerged (root cause, convention, decision, correction) not already represented | [task_add_note.md](references/task_add_note.md) | One atomic note per concept (update, never duplicate); TOC + log updated; one-off activity/session state/error text kept out of notes |
| **3: Search** | Before implementation/change, or a knowledge question | [task_search.md](references/task_search.md) | Question answered from relevant notes/specs; deepen only when needed, and check existing specs before creating records or implementing features |
| **4: Review** | Requested or scheduled knowledge maintenance | [task_review.md](references/task_review.md) | Requested review complete; durable findings/corrections captured only when present; read-only/no-discovery sessions require no bookkeeping |
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

**Handoff links.** Whenever a PRD, Architecture, Epic, or Story is created or presented — alone or in a batch — every artifact carries its own Markdown link whose visible label is the file's full absolute path and whose target opens that actual file; a directory, index, relative, shortened, or future path is never a substitute. Receipted Story completions repeat those links, with final canonical locations after integration. CLI JSON output stays unchanged, and review approval is never presented as completion.

**Status policy** — use only these statuses; never invent others (e.g. `blocked`: keep current status, add a blocker note to the artifact and a log entry).

| Artifact | Statuses |
|----------|----------|
| Specs, stories, quick tasks | `draft`, `approved`, `in_progress`, `review`, `done` (approval gates apply to PRD, Architecture, Stories, and code review; quick-task review/verification still mandatory) |
| Research memos | `draft`, `done` (no approval gate) |
| Notes | `draft`, `stable`, `deprecated` (currentness is `stale_after`, not a fourth status) |

Lifecycle: `draft → approved → in_progress → review → done`, with `changes requested` returning to `approved` from `in_progress`/`review`. `review` is a valid legacy status, but checked `work finish` refuses it (`WORK_PHASE_DENIED`): keep the record in an active phase (`approved`/`in_progress`), record the code-review decision in the embedded `completion_review` mapping, and let finish alone write `done`.

---

## Publication & Install Safety

When initializing a new project, use [agents_template.md](references/agents_template.md) to add the Kosmic Integration section to that project's `AGENTS.md`. The Shared Skill Library is authoritative in the vault. Install only its generated `memnotes-skills` router; Domain Skills and detailed topics load dynamically through a verified Resolution Plan. Never hand-edit generated catalogs, manifests, router packages, or installed copies, and never edit installed user-authored skills. Migration and installation retain their separate approved target plans, including disposable adapter validation.
