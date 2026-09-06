---
status: approved
created: 2026-09-06
updated: 2026-09-06
linked_research: [../evidence/2026-09-02-wikiskill-experience-compilation/memo.md]
linked_epics: [epics/epic-10-proposer-contract.md, epics/epic-11-proposal-governance.md, epics/epic-12-proposal-behavior.md, epics/epic-13-proposal-activation-release.md]
---

# Skill Proposal Loop

## Problem Statement

Kosmic compiles experience into Evidence Packs and maintained Project Knowledge, then deterministically projects stable notes into a fixed Usage/Development Skill Pair. It does not execute WikiSkill's distinct Skill Proposer role. Consequently, accumulated Patterns can improve project references, but no mandatory stage decides whether repeated evidence warrants creating or updating a reusable procedural skill. Treating the normal story or quick-task flow as the proposer made skill evolution discretionary and produced the observed failure: useful knowledge is retained, but skill changes are rarely proposed.

A second, separate problem is runtime activation. WikiSkill injects every active skill into the Inference Agent's system prompt specifically to remove retrieval failures from its experiment. Kosmic relies on native skill discovery and generated descriptions. Proposal quality and runtime activation therefore require separate checks and must not be conflated.

## Goals

- Add an explicit Task P that always evaluates qualifying distilled experience and emits one atomic `create`, `update`, or `no_action` proposal.
- Preserve role separation by using a fresh-context proposer with a deliberately bounded evidence package.
- Require a dedicated proposer subagent for shared or global skill changes; allow a recorded constrained same-agent fallback only for project-local proposals and `no_action`.
- Keep proposal reasoning separate from deterministic Projection CLI validation and publication.
- Gate every proposed skill mutation through human approval, behavioral comparison, independent Task 7 review, and an Impact Ledger decision.
- Make existing projected skills easier to discover through concrete generated descriptions and verifiable install/runtime guidance.

## Non-Goals

- Reproduce WikiSkill's benchmark-training loop, scalar reward optimization, or automatic rollback machinery.
- Give the proposer unrestricted access to the parent conversation or entire repository by default.
- Let Task P edit canonical or installed skills directly.
- Replace the fixed per-project Usage/Development Skill Pair with an unbounded set of generated project skills.
- Auto-approve, auto-install, or auto-publish a proposed procedural skill.
- Treat every Project Knowledge note as a procedural skill candidate.

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-P01 | Kosmic defines `Task P: Propose Skill Change`. New story, quick-task, and maintenance templates require an explicit `proposal_required: true | false` decision; `true` is required whenever Distillation yields or materially updates a reusable Pattern. | must |
| FR-P02 | Task P receives a curated proposer package: proposal instructions, Knowledge Index, relevant Patterns and Evidence Packs, current candidate skills, Impact Ledger history, and concise task outcomes; the full parent transcript is excluded by default. | must |
| FR-P03 | Each Task P run emits exactly one atomic result: `create` one skill, `update` one skill, or `no_action`, with target, scope, evidence, rationale, and validation plan. | must |
| FR-P04 | Proposal scope is one of `project-knowledge`, `project-procedure`, or `global-procedure`; project knowledge continues through deterministic Skill Pair projection, while procedural scopes enter the proposal lifecycle. | must |
| FR-P05 | Shared/global skill creation or modification requires a dedicated fresh-context proposer subagent. Project-local proposals and `no_action` may use a constrained same-agent fallback only when the artifact records mode and reason. | must |
| FR-P06 | Proposal artifacts live under `specs/skill-proposals/`, use the existing review lifecycle, retain links to motivating Evidence Packs/Patterns, and remain distinct from canonical/generated skill directories. | must |
| FR-P07 | The Projection CLI deterministically validates proposal schema, path resolution, atomicity, target existence rules, proposer independence policy, and completion state; it performs no LLM inference. | must |
| FR-P08 | `check-completion` fails a work item declaring `proposal_required: true` unless `skill_proposal` resolves to one validated proposal artifact whose result is `create`, `update`, or `no_action`; `no_action` requires a non-empty reason. | must |
| FR-P09 | Implementing an approved proposal requires a predeclared behavioral comparison at the real task seam: candidate versus no skill for creation, or candidate versus current skill for update. | must |
| FR-P10 | Acceptance requires human approval, convergent Task 7 review, passing behavioral evidence, and an append-only `impact.md` decision; rejection is also recorded so an equivalent failed intervention is not proposed again without new evidence. | must |
| FR-P11 | Task P must search existing skills and rejected proposals before proposing creation, preferring an update over a near-duplicate skill. | must |
| FR-P12 | Generated Usage/Development `description` fields name concrete task triggers derived deterministically from project identity and audience; installation documentation states that runtimes may require registry reload or a new session. | should |
| FR-P13 | A runtime-health command or documented probe distinguishes "installed on disk" from "surfaced in the active agent skill inventory" where an adapter exposes that capability. | should |
| FR-P14 | The first release dogfoods Task P on existing Kosmic evidence and carries one proposal through accept/reject, ledger recording, and runtime verification. | must |

## Non-Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| NFR-P01 | Proposal validation and completion gating remain deterministic, offline, and Python 3.11+ standard-library-only. | must |
| NFR-P02 | Canonical/generated/installed Skill Pair publication remains atomic and generated outputs remain hand-edit prohibited. | must |
| NFR-P03 | A proposal is auditable from evidence through Pattern, candidate diff, behavioral result, review finding, and ledger outcome. | must |
| NFR-P04 | The proposer interface is self-sufficient and bounded so a fresh agent can execute it without hidden conversation state. | must |
| NFR-P05 | Existing projects and work items without `proposal_required` remain valid; new templates always declare it, making the gate explicit without retroactively invalidating completed work. | must |
| NFR-P06 | Proposal execution must fail closed when a mandatory independent proposer is unavailable; it must not silently downgrade to same-agent mode for shared/global changes. | must |
| NFR-P07 | Candidate evaluation must not mutate canonical or installed skills before acceptance. | must |

## Success Criteria

- [ ] A completed Evidence Pack and distilled Pattern produce a schema-valid atomic Task P result.
- [ ] A shared/global proposal fails validation when authored in same-agent mode and passes when a dedicated proposer subagent is recorded.
- [ ] `create`, `update`, and `no_action` fixtures exercise all schema and completion-gate branches.
- [ ] A proposed creation is behaviorally compared against a no-skill baseline without modifying canonical or installed skills.
- [ ] An accepted or rejected proposal appends one valid `impact.md` decision and equivalent rejected proposals are detected on the next Task P run.
- [ ] Existing work items without proposal metadata retain their current behavior.
- [ ] Generated descriptions contain concrete activation triggers, and adapter guidance distinguishes file installation from active-session discovery.
- [ ] One real Kosmic proposal completes proposal, approval, implementation, independent review, ledger recording, publication, and runtime verification.

## Open Questions

- [x] Is a separate subagent always required? No. It is mandatory for shared/global changes; constrained same-agent execution is permitted for project-local proposals and `no_action`, with disclosure.
- [x] Should Task P mutate skills directly? No. It produces a reviewable atomic proposal only.
- [x] Should the Projection CLI call an LLM? No. Agent reasoning and deterministic validation remain separate.
- [x] Should project Skill Pair projection be replaced? No. Task P supplements the fixed pair for procedural evolution.
- [x] How is WikiSkill score gating adapted? Use predeclared behavioral comparison plus human approval and convergent Task 7 review.
