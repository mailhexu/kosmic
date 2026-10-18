---
type: Task Reference
title: Task P - Propose Skill Change
---

# Task P: Propose Skill Change

**When**: Implemented work yields a verified reusable procedure, or a work item declares `proposal_required: true`. Nomination may also come from the optional knowledge-curation routine (prepare/review/finalize), which nominates candidates only — it never triggers publication by itself.

**Purpose**: decide whether observed repeated behavior should create/update a procedural skill, create/extend/reuse a deterministic shared routine, remain prose, or produce `no_action`. Task P proposes; it never edits canonical or installed artifacts.

## Independence

Use a dedicated **fresh-context proposer** subagent whenever the scope is `global-procedure` or the target is a shared skill. It receives only the curated package below. If that agent is unavailable, fail closed. For `project-knowledge`, `project-procedure`, or `no_action`, the current agent may run the same procedure only when it records `proposer_mode: same-agent` and a concrete `proposer_reason`.

## Curated input package

Create a manifest that lists exactly the materials supplied:

1. this Task P procedure and proposal template;
2. `notes/index.md`, then only relevant stable Patterns;
3. the source note (stable Pattern) and the work records embedding the verified observations and review that support it;
4. current candidate and installed skill files for the named target, if updating;
5. relevant accepted/rejected proposal artifacts under `specs/skill-proposals/`;
6. concise work-item outcomes, with implementation conversation excluded by default.

Every listed file carries a Project-relative path and SHA-256. The proposer follows references deliberately; it gets no hidden transcript.

## Decision procedure

1. Read the source note's `artifact_role`. Only `procedure` is eligible for executable reuse. Guideline, knowledge, evidence, or uncertain classification produces `no_action`.
2. Classify procedure mechanics as `judgment`, `deterministic-routine`, or `mixed-procedure`. A routine candidate requires a repeatable trigger, typed inputs and outputs, explicit invariants and expected failures, successful behavioral evidence, and a named owning domain. A failure-derived procedure candidate is eligible only when its repair generalizes across independent cases and the evidence records the violated invariant, a meaningful recovery, and a reproducer plus verification matrix; otherwise emit `no_action` and retain the incident as evidence.
3. Search the generated routine inventory before proposing new mechanics. Prefer exact `reuse`; then `extend` an owning module; use `create` only when no appropriate implementation exists. Keep judgment as prose.
4. Search current skills and prior proposals. Prefer updating one deep skill over creating overlapping instructions.
5. Inspect rejected fingerprints. Reconsider an equivalent proposal only with materially new evidence.
6. Emit **exactly one atomic result** for the skill (`create`, `update`, `no_action`) and, when mechanics were classified, one routine action per canonical routine ID (`reuse`, `extend`, `create`, `keep_as_prose`, `none`). Preserve classification and routine fields in the fingerprint.
7. Ask the human to approve or reject. Approval sets `status: approved`; do not implement before approval.
8. Approved routine `create`/`extend` proposals declare a `## Routine Candidate` with Repetition, Contract, Expected failures, and Leverage, plus `consumer_approvals` from the owning and every consuming domain Maintainer. `reuse` requires behavioral evidence; `keep_as_prose` and `none` require a concrete rationale.
9. Retain the baseline and candidate records inside the governing work record, with each acceptance criterion's actual observation and the independent review. Run Task 7 independently. Set `status: done` and `decision: accepted` or `rejected`, retaining the proposal and its evidence in the record.
10. Only an accepted, reviewed proposal may flow through the ordinary approved Story or Quick Task publication path.

## Output constraints

- `create` for a Project-local or global skill: target is a new skill name; `target_ref` is `skill://{name}`; `target_sha256` is `empty`.
- `update` for those targets: target, `target_ref`, and exact pre-change `target_sha256` are mandatory.
- `shared-procedure`: target is `{domain}/{usage|development}/{slug}` and `target_ref` is `library-skill://{target}`. A fresh-context subagent is mandatory. Accepted proposals record `approved_by` matching the target Domain Skill's `maintainers`; Task 7 verifies the human authorization.
- `no_action`: target fields are empty; `## No-Action Reason` replaces `## Proposed Change`; behavioral evidence may be empty.
- `shared-routine`: target and `routine_id` are `{domain}/{slug}`. `target_kind: routine`, `routine_action`, `linked_proposals`, and `consumer_approvals` are fingerprinted. One proposal governs one routine ID. An `extend` proposal pins the generated routine coordinate as `- routine://{domain}/{slug}: {routine_sha256}` in its input manifest; ordinary source inputs remain `- path: {source_sha256}`.
- Proposal paths and note references are Project-root-relative and contained within the Project.
