---
type: Task Reference
title: Task P - Propose Skill Change
---

# Task P: Propose Skill Change

**When**: After Task 9 Distillation creates or materially updates a reusable Pattern, or before completing any work item with `proposal_required: true`.

**Purpose**: decide whether observed repeated behavior should create one procedural skill, update one existing skill, or produce `no_action`. Task P proposes; it never edits canonical or installed skills.

## Independence

Use a dedicated **fresh-context proposer** subagent whenever the scope is `global-procedure` or the target is a shared skill. It receives only the curated package below. If that agent is unavailable, fail closed. For `project-knowledge`, `project-procedure`, or `no_action`, the current agent may run the same procedure only when it records `proposer_mode: same-agent` and a concrete `proposer_reason`.

## Curated input package

Create a manifest that lists exactly the materials supplied:

1. this Task P procedure and proposal template;
2. `notes/index.md`, then only relevant stable Patterns;
3. declared Evidence Pack manifests and selected payloads;
4. current candidate and installed skill files for the named target, if updating;
5. relevant accepted/rejected proposal history from `impact.md` and proposal artifacts;
6. concise work-item outcomes, with implementation conversation excluded by default.

Every listed file carries a Project-relative path and SHA-256. The proposer follows references deliberately; it gets no hidden transcript.

## Decision procedure

1. Establish a repeatable procedural trigger: recurring task, stable inputs, ordered actions, decision points, expected output, and failure handling. Project facts or vocabulary alone imply `no_action`.
2. Search current skills and prior proposals. Prefer updating one deep skill over creating overlapping instructions.
3. Inspect rejected fingerprints. Reconsider an equivalent proposal only with materially new evidence.
4. Emit **exactly one atomic result**: `create`, `update`, or `no_action`.
5. Write `specs/skill-proposals/YYYY-MM-DD-{slug}.md` from the template with `status: draft`. Keep `decision: pending`; compute the canonical fingerprint with `validate-proposal`.
6. Ask the human to approve or reject. Approval sets `status: approved`; do not implement before approval.
7. For approved `create`/`update`, declare `Candidate paths: [project-relative/path]` under `Behavioral Validation` and implement only at those paths, outside canonical and installed skill paths. Predeclare one motivating failure or success criterion and run the same observable scenario against baseline and candidate.
8. Store baseline and candidate records in an execution Evidence Pack. Run Task 7 independently. Set `status: done` and `decision: accepted` or `rejected`, retain the proposal and evidence, and append the prescribed `impact.md` decision entry.
9. Only an accepted, reviewed proposal may flow through the ordinary approved Story or Quick Task publication path.

## Output constraints

- `create` for a Project-local or global skill: target is a new skill name; `target_ref` is `skill://{name}`; `target_sha256` is `empty`.
- `update` for those targets: target, `target_ref`, and exact pre-change `target_sha256` are mandatory.
- `shared-procedure`: target is `{domain}/{usage|development}/{slug}` and `target_ref` is `library-skill://{target}`. A fresh-context subagent is mandatory. Accepted proposals record `approved_by` matching the target Domain Skill's `maintainers`; Task 7 verifies the human authorization.
- `no_action`: target fields are empty; `## No-Action Reason` replaces `## Proposed Change`; behavioral evidence may be empty.
- Project evidence slugs remain valid. Cross-project evidence uses an explicit vault-contained `Projects/{project}/evidence/{pack}` path; Evidence stays with the Project that produced it.
- Proposal paths and note references are Project-root-relative and contained within the Project.
