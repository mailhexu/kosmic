# Matt Pocock skills as Kosmic procedure enhancements

**Question.** Which Matt Pocock skills can improve Kosmic procedures without replacing its vault-based knowledge model, approval gates, and Project Skill Pair workflow?

## Decision summary

Adopt **selective composition**, not a wholesale import. Kosmic remains the outer orchestrator and source of workflow truth: Search → Quick Task or PRD/Architecture/Epics/Stories → implementation → mandatory review → Project Knowledge refresh/projection. Matt Pocock skills may improve one bounded procedure inside that flow.

Do **not** copy or invoke the whole upstream suite as a second orchestrator. Several skills assume an external issue tracker, `docs/agents/` configuration, commits, or a different spec lifecycle. Duplicating their routing causes conflicting gates and two sources of process truth.

**Chosen posture (2026-08-09): Required dependency.** Every Kosmic installation must include the selected upstream Matt Pocock skills. Kosmic still owns workflow orchestration; its procedures may rely on these skills being available rather than providing a native fallback.

## First-party upstream facts

- Repository: [mattpocock/skills](https://github.com/mattpocock/skills).
- License: [MIT](https://github.com/mattpocock/skills/blob/master/LICENSE), copyright 2026 Matt Pocock. Retain the license notice when copying material.
- The repository describes skills as small, composable, and model-agnostic. It supports either its managed Claude plugin or `npx skills@latest add mattpocock/skills` for other agents; its README says not to install both.
- Install/update instructions: [README](https://github.com/mattpocock/skills/blob/master/README.md), [package metadata](https://github.com/mattpocock/skills/blob/master/package.json).
- Local inspection shows the current relevant, non-deprecated skills are: `tdd`, `code-review`, `diagnosing-bugs`, `research`, `domain-modeling`, `codebase-design`, `grilling`, `grill-with-docs`, `to-spec`, `to-tickets`, `implement`, `wayfinder`, `improve-codebase-architecture`, `triage`, and supporting productivity skills. The upstream README labels other items as deprecated, in-progress, or personal; do not adopt those as Kosmic dependencies.

## Procedure fit

| Kosmic procedure | Upstream skill | Recommendation | Integration boundary |
|---|---|---|---|
| Task 6: Implement Story | `tdd` | **Adopt** | Use after Kosmic Research and Story approval. Retain Kosmic's required knowledge search, story metadata, completion gate, and note refresh. Use Matt's public-interface / red-green-refactor discipline only. |
| Task 7: Code Review | `code-review` | **Adopt** | Replace or augment the review *method*: fixed review base and separate Standards vs Spec axes. Retain Kosmic's mandatory review status gate, Project Skill Pair completion gate, and local story/spec artifacts. |
| Bug fixing | `diagnosing-bugs` | **Adopt** | Add an explicit branch before Quick Task/Story implementation: reproduce → minimize → hypotheses → instrumentation → regression test. Keep Kosmic approval and logging requirements. |
| Task R: Research | `research` | **Already aligned** | Kosmic already requires primary-source research captured as a repo memo. Align its wording with upstream's background-agent method; do not duplicate another research lifecycle. |
| Architecture and terms | `domain-modeling`, `codebase-design` | **Adopt selectively** | Use when terminology or a module seam changes. Keep `notes/` as Project Knowledge; use `CONTEXT.md`/ADRs only for their stated domain-decision role. |
| Design decisions / approval | `grilling`, `grill-with-docs` | **Optional** | Use as a subroutine before approving Architecture or a high-risk Quick Task. Do not make every Kosmic approval gate an interview. |
| PRD/spec authoring | `to-spec` | **Do not adopt wholesale** | Its “no interview, publish to issue tracker” model conflicts with Kosmic's PRD→Architecture→Epics→Stories artifacts and explicit approval gates. Borrow only its test-seam-first prompt. |
| Ticket breakdown | `to-tickets`, `wayfinder` | **Defer** | Useful only if Kosmic later integrates a configured issue tracker. Existing Kosmic Epics/Stories remain canonical now. |
| Architecture scans | `improve-codebase-architecture` | **Optional** | Use as an on-demand diagnostic. Its HTML report can inform Architecture; it must not create a second roadmap. |
| Setup, triage, implement | `setup-matt-pocock-skills`, `triage`, `implement` | **Reject as defaults** | They assume upstream tracker/docs configuration or take ownership of implementation/commit flow. Kosmic owns these areas. |

## Recommended initial integration

### 1. TDD inside Task 6

After a Story is approved and Kosmic Search/Research records the relevant Project Knowledge:

1. Identify and agree the highest external test seam.
2. Use `tdd` for a single vertical slice: red test → minimal implementation → green → refactor.
3. Preserve Kosmic's story checklist, Consumer Interface completion gate, stable-note updates, pair regeneration, and mandatory code review.

**Benefit:** raises test quality without changing who owns planning, approvals, knowledge, or release gates.

### 2. Two-axis review inside Task 7

Before `done`, run Matt's `code-review` method against the fixed `review_base` already maintained by Kosmic:

- **Standards:** repository conventions plus design smells.
- **Spec:** Story/Quick Task acceptance criteria and scope.

Then apply Kosmic's existing convergence rule, log, knowledge refresh, and Projection CLI validation. Do not require an external issue tracker: the Kosmic Story or Quick Task file is the spec source.

**Benefit:** a concrete review lens; no duplicate artifact lifecycle.

### 3. Diagnosis branch for bugs

For bug-oriented Quick Tasks or Stories, require `diagnosing-bugs` before the normal implementation step:

1. Establish a repeatable failing reproduction.
2. Minimize it and state 3–5 falsifiable hypotheses.
3. Instrument only as needed to discriminate hypotheses.
4. Add a regression test at the discovered seam.
5. Continue through Kosmic verification, review, and knowledge capture.

**Benefit:** prevents symptom patches while preserving the lightweight Quick Task route for genuinely narrow fixes.

## Implementation shape

Use **required external skills, referenced rather than copied**:

- Keep Kosmic `SKILL.md` as the single mandatory router.
- Require the independently installed upstream `tdd`, `code-review`, `diagnosing-bugs`, `research`, `domain-modeling`, and `codebase-design` skills. `tdd` is installed with its declared design-vocabulary dependencies.
- Add explicit “use `<skill>` here” subroutine calls in `task_implement_story.md`, `task_review_spec.md`, `task_quick_task.md`, and `task_research.md`.
- Fail Kosmic setup/initialization with actionable installation instructions if the required skills are unavailable.
- Do not add a runtime dependency to the Projection CLI.
- If copied into the Kosmic distribution later, vendor only the necessary text, retain MIT attribution, record the upstream revision, and add behavioral tests for the combined gate—not source-text tests.

## Risks and controls

| Risk | Control |
|---|---|
| Two orchestrators issue conflicting instructions | Kosmic controls task selection, artifacts, approvals, status transitions, logs, and Project Skill Pair gates. Upstream skills are local methods only. |
| External tracker assumptions leak into vault workflow | Use Kosmic Story/Quick Task files as the review/spec source; do not invoke `to-spec`, `to-tickets`, `triage`, or setup by default. |
| Duplicate skill names overwrite installed skills | Do not vendor under original names unless explicitly distributing them separately. Prefer references to an independently installed upstream skill. |
| Upstream changes silently alter process | Pin an upstream revision before vendoring; review changes and retain local compatibility tests. |
| License omission when copying | Preserve the upstream MIT notice and source reference. |

## Proposed adoption sequence

1. **TDD** — highest leverage and lowest conflict.
2. **Code review** — add two-axis review while retaining Kosmic gates.
3. **Diagnosing bugs** — improve fix quality without affecting feature planning.
4. Evaluate optional domain modeling / grilling integration after two real feature cycles.
5. Defer issue-tracker-oriented skills until a tracker becomes a deliberate Kosmic architectural decision.

## Primary sources

- Matt Pocock, [skills repository](https://github.com/mattpocock/skills).
- Matt Pocock, [README: installation, skill catalogue, and managed-plugin model](https://github.com/mattpocock/skills/blob/master/README.md).
- Matt Pocock, [MIT license](https://github.com/mattpocock/skills/blob/master/LICENSE).
- Matt Pocock, [`tdd` skill](https://github.com/mattpocock/skills/tree/master/engineering/tdd).
- Matt Pocock, [`code-review` skill](https://github.com/mattpocock/skills/tree/master/engineering/code-review).
- Matt Pocock, [`diagnosing-bugs` skill](https://github.com/mattpocock/skills/tree/master/engineering/diagnosing-bugs).
- Matt Pocock, [`research` skill](https://github.com/mattpocock/skills/tree/master/engineering/research).
- Matt Pocock, [`to-spec` skill](https://github.com/mattpocock/skills/tree/master/engineering/to-spec).
- Matt Pocock, [CHANGELOG: dependency and skill-status changes](https://github.com/mattpocock/skills/blob/master/CHANGELOG.md).
