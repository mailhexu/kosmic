---
project_id: "kosmic"
subproject_id: null
record_kind: "quick-task"
local_id: "explicit-command-contract-and-lean-verification-guidance"
status: done
consumer_interface_change: true
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
created: "2026-10-23"
updated: "2026-10-23"
review_base: "b7ac790dea70bf9c18e190c60518f6da3e91ebc4"
review_round: 2
related_notes: ["notes/cli-projection-commands.md"]
completion_observations:
  - criterion: "The command contract (trust documented success, error-driven recovery without a global atomicity claim, no routine `--help` discovery) is stated in `skills/SKILL.md` and reflected consistently by the touched references."
    observation: "The entry skill now trusts documented command outputs and reserves diagnostics for actual errors; it explicitly preserves acceptance verification and warns that finish errors need not roll back publication."
    source: "Held guidance delta against b7ac790dea70bf9c18e190c60518f6da3e91ebc4; session history discovery commands at 2026-10-22T07:17:08.891Z and 2026-10-22T20:25:16.770Z."
  - criterion: "`task_create_spec.md`, `task_quick_task.md`, `task_init.md` and `work_completion.md` provide complete invocations; routine initialization explicitly creates no Quick Task and triggers no implementation review."
    observation: "Task-local CLI recipes supply invocation prefixes and required flags. Task 1, the entry policy, generated pair guidance and initialization inventory explicitly exempt routine initialization from a work record, implementation review and work start/finish."
    source: "Guidance delta; actual init --project disposable-Project --project-id routine-init-demo --status-root existing-directory returned initialized Project and published skills, exit 0, without --work-record."
  - criterion: "No touched reference mandates administrative re-verification after success; actual implementation/scientific acceptance gates and error-driven recovery remain explicit."
    observation: "Removed post-finish terminal validation/STATUS inspection, migration stage-4 re-plan/validate/check-completion, and post-install router checks. Real changed-behavior observations and independent implementation-review gates remain; interruption recovery is retained."
    source: "Held task/reference delta and unchanged checked-completion admission logic."
  - criterion: "Durable Usage knowledge and the regenerated Skill Pair state the contract; the installed OMP pair and orchestrator package match the source after refresh."
    observation: "Updated the stable CLI invariant note. Native generate published the atomic pair; native install --adapter omp reported on-disk success. Published the orchestrator from the 45 tracked non-cache source files using successful copy and publish_tree operations. Active-session discovery was not claimed; the global memnotes-skills router was not changed."
    source: "generate and install --project canonical-kosmic-Project --work-record kosmic/quick-task/explicit-command-contract-and-lean-verification-guidance, exit 0; orchestrator publisher returned /home/hexu/.omp/agent/skills/kosmic, exit 0."
  - criterion: "Real CLI initialization and spec creation succeed using the documented commands without a governing init record or post-success confirmation commands; guidance review covers the unchanged implementation gates."
    observation: "The disposable Project initialized successfully without a work record. One spec-create --kind quick-task --title 'Use the documented command result' returned draft identity routine-init-demo/quick-task/use-the-documented-command-result and canonical path specs/quick-tasks/use-the-documented-command-result.md, exit 0. Results were consumed directly without read-back, listing, validation or help commands."
    source: "Actual writer CLI init and spec-create smoke invocations retained in this session. No permanent wording tests added; implementation-review decisions are recorded separately below."
completion_review:
  reviewer: "OMP-main"
  axes:
    standards: {decision: "approved", reviewer: "LeanStandardsReview"}
    spec: {decision: "approved", reviewer: "LeanSpecReview"}
  decision: "approved"
  review_base: "b7ac790dea70bf9c18e190c60518f6da3e91ebc4"
  reviewed_revision: "b1165702dc59f04630f32d00907e7b853c612aa88edb2f3fa5b21fefb3352a59"
  findings:
    - id: "STD-S1"
      disposition: "Non-blocking"
      status: "open"
      detail: "Optional placeholder consistency: PROJECT_ROOT and VAULT/Projects/TARGET denote the same defined path; no behavior change required."
    - id: "STD-S2"
      disposition: "Non-blocking"
      status: "open"
      detail: "Optional placeholder consistency: PRD_QUALIFIED_RECORD is deliberately explicit and defined inline; no behavior change required."
    - id: "F1-template-index-quicktask-row"
      disposition: "Non-blocking"
      status: "resolved"
      resolution: "fixed"
      detail: "The specs-index template still guessed a date-prefixed Quick Task filename."
      worker_response:
        kind: "fixed"
        detail: "Changed the template row to use quick-tasks/{returned-local-id}.md."
        evidence: "One-line template edit, integrated and republished in the OMP orchestrator; existing actual spec-create JSON supplies that local ID."
  scope: ["worktree:skills/SKILL.md", "worktree:skills/references/task_init.md", "worktree:skills/references/task_create_spec.md", "worktree:skills/references/task_quick_task.md", "worktree:skills/references/task_implement_story.md", "worktree:skills/references/task_project_skills.md", "worktree:skills/references/work_completion.md", "worktree:skills/references/agents_template.md", "worktree:skills/README.md", "worktree:skills/scripts/kosmic_project_skills.py", "worktree:skills/references/task_review_spec.md", "worktree:skills/references/managed_run_lifecycle.md", "worktree:skills/references/templates/template-specs-index.md", "project:specs/quick-tasks/explicit-command-contract-and-lean-verification-guidance.md", "project:notes/cli-projection-commands.md", "project:skills"]
---
# Explicit command contract and lean verification guidance

## Request and Approval

The user reported recurring agent-token waste: `--help` discovery before commands the guidance already governs, and post-success re-verification of atomic commands. The user directed: "If this is always going to happen, just put the --help result in the skill. ... We should make the workflow solid and then we trust it, and no check unless an error message is there! The instruction should be clear, not a lot of going back and forth." This approves the bounded guidance revision below; no CLI source-behavior change is authorized.

The user's later clarification also authorizes a bounded routine-initialization exception: initialization itself creates no Quick Task and needs no implementation review. Developing initialization behavior remains governed.

## Scope and Plan

- State the command contract once in `skills/SKILL.md`: exit 0 is authoritative for documented operation outputs; use returned paths, identities and receipts directly. Do not promise global atomicity or rollback on error: finish publishes stepwise and diagnostics determine recovery. New implementation/scientific acceptance checks remain required.
- Forbid `--help` discovery for guided commands: every task reference carries complete invocations; `--help` is only for genuinely novel surfaces.
- Supply complete documented invocations for spec creation, work start/finish and initialization; replace `check-completion --help` discovery with the documented finish sequence and optional diagnostics only on need.
- Remove administrative post-success confirms from creation, migration, installation and completion; retain actual acceptance verification and operation-internal gates.
- Reuse required-procedure-skill verification for an unchanged adapter environment; check at initialization/migration or if not yet verified, and rerun on resolution errors or adapter/installed-skill changes. No new cache metadata.
- Exempt routine initialization from record creation, implementation isolation/completion and review; retain explicit target approval for registration, migration and installation, and normal review for development changes.
- Update the generated Skill Pair's shared `record_first_contract` strings and initialization mutation-inventory description so generated guidance does not reintroduce an init record/review. No command admission, mutation, validation or receipt logic changes.
- Consumer docs coherence in the same episode: durable invariant line in `notes/cli-projection-commands.md`, native Skill Pair regeneration, and refresh of the installed OMP pair plus orchestrator package under this record.

## Out of Scope

CLI operational behavior (apart from generated guidance text), implementation-review/round protocol, ceremony outside routine initialization, router-ownership decisions, and unrelated guidance surfaces.

## Acceptance Criteria

- [x] The command contract (trust documented success, error-driven recovery without a global atomicity claim, no routine `--help` discovery) is stated in `skills/SKILL.md` and reflected consistently by the touched references.
- [x] `task_create_spec.md`, `task_quick_task.md`, `task_init.md` and `work_completion.md` provide complete invocations; routine initialization explicitly creates no Quick Task and triggers no implementation review.
- [x] No touched reference mandates administrative re-verification after success; actual implementation/scientific acceptance gates and error-driven recovery remain explicit.
- [x] Durable Usage knowledge and the regenerated Skill Pair state the contract; the installed OMP pair and orchestrator package match the source after refresh.
- [x] Real CLI initialization and spec creation succeed using the documented commands without a governing init record or post-success confirmation commands; guidance review covers the unchanged implementation gates.

## Routine Decision

No reusable deterministic routine mechanics: this revises caller guidance only.

## Observed Causes

- Session history at `2026-10-22T07:17:08.891Z` contains a seven-command `--help` discovery loop; `2026-10-22T20:25:16.770Z` separately probes install and check-installation help.
- The original Work Completion reference explicitly directed `check-completion --help` and required terminal validation after successful finish, although finish already performs its gates.
- Initialization guidance required a bootstrap Quick Task, and generated Skill Pair guidance repeated it; CLI `init` has no `--work-record` argument and already runs without a review gate.
- `init --status-root` records the binding but does not generate STATUS. The first normal record publishes STATUS; optional adapter installation also stays outside init, avoiding indirect creation of an init Quick Task.
