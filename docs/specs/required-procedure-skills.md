# Require Matt Pocock procedure skills in Kosmic

## Problem Statement

Kosmic currently describes a complete knowledge and delivery workflow, but its procedures do not consistently invoke the specialized methods selected for test-driven implementation, diagnosis, review, research, domain modeling, design, deliberation, and prototypes. An agent can therefore execute a Kosmic task with weaker or inconsistent method guidance. Making those methods merely optional would preserve this variance.

## Solution

Kosmic requires an independently installed, curated upstream skill set and verifies it during installation or initialization. Kosmic continues to own all workflow routing and artifacts. Each selected upstream skill is invoked only within a defined Kosmic procedure; it does not replace Kosmic Search, approval gates, project vault records, Project Skill Pair gates, or the Projection CLI.

The required dependency set is:

- `tdd`
- `code-review`
- `diagnosing-bugs`
- `research`
- `domain-modeling`
- `codebase-design`
- `grill-with-docs`, including its `grilling` subroutine
- `prototype`

## User Stories

1. As a Kosmic installer, I want installation to verify every required procedure skill, so that a usable Kosmic installation cannot silently omit its required methods.
2. As a Kosmic installer, I want actionable agent-specific setup guidance when a dependency is missing, so that I can repair the installation without guessing which skill or installer is needed.
3. As a Story implementer, I want Kosmic to invoke `tdd` at the approved Story's highest agreed external test seam, so that tests defend observable behavior through red-green-refactor rather than implementation details.
4. As a reviewer, I want Kosmic review to apply the `code-review` Standards and Spec axes against the pinned review base and local Story/Quick Task artifact, so that repository conformance and acceptance-criteria conformance remain independently visible.
5. As a bug fixer, I want bug-oriented work to use `diagnosing-bugs` before implementation, so that a reproducible cause and regression test replace symptom patches.
6. As a researcher, I want Task R to use the upstream primary-source research method while retaining the Kosmic research memo and architecture gates, so that research is both rigorous and part of Project Knowledge.
7. As an architect, I want terminology and seams to use `domain-modeling` and `codebase-design`, so that `CONTEXT.md`, ADRs, test seams, and module boundaries share a precise vocabulary.
8. As a requester of a high-risk design decision, I want Kosmic to use `grill-with-docs` before the applicable approval gate, so that unresolved trade-offs are exposed without turning every approval into an interview.
9. As a designer exploring uncertain behavior, I want Kosmic to use `prototype` only as disposable decision evidence, so that prototype code never becomes unreviewed production implementation.
10. As a Project Consumer, I want the Project Usage Skill and Consumer Interface completion gate to remain unaffected by upstream skill installation, so that the required dependency does not blur the Contributor/Consumer boundary.
11. As a maintainer, I want upstream dependency changes to be explicit and compatibility-reviewed, so that an upstream skill update cannot silently change Kosmic workflow guarantees.

## Implementation Decisions

- Kosmic is the only workflow orchestrator. It remains authoritative for task selection, Project Knowledge, specifications, approval/status transitions, logs, Project Skill Pair generation, Consumer Interface completion, and projection validation.
- The upstream set is a required external dependency, not vendored source. Kosmic must not duplicate upstream skill content or define competing aliases under the same names.
- Setup/initialization verifies the complete set before allowing a new or existing Project to enter a contributor workflow. Missing dependencies produce one actionable failure identifying each missing skill and the supported installer route for the current agent.
- Verification is adapter-specific: inspect the exact curated skill names in each supported adapter's documented installation location. The Python CLI does not claim universal semantic named-skill discovery.
- Agents without a supported adapter fail setup clearly; there is no silent degraded mode. Each supported adapter documents a native smoke-load command or interaction, but that smoke check is verification evidence rather than a Projection CLI runtime dependency.
- `tdd` is called only after Kosmic's Story prerequisites and mandatory research phase. `codebase-design` and `domain-modeling` are available whenever `tdd` is invoked.
- `code-review` is the review method for Task 7. The fixed review base remains Kosmic-owned; the approved Story or Quick Task is the Spec-axis source. Findings remain in Kosmic's stable review ledger and follow its convergence/status rules.
- Bug classification selects `diagnosing-bugs` before the normal Quick Task or Story implementation sequence. The result must include a repeatable failing case and a regression test at the established seam before the fix may complete.
- Task R invokes `research` as its investigation method. It still writes a Kosmic research memo, feeds Architecture, and follows existing gates.
- `domain-modeling` and `codebase-design` are invoked when a task creates or sharpens domain terms, creates an ADR-worthy boundary decision, or proposes/changes a test seam or module interface.
- `grill-with-docs` is mandatory for Architecture approval and ADR-worthy Quick Tasks only when material alternatives or unresolved design trade-offs exist. It is not a universal approval prerequisite.
- Kosmic deliberately adapts `prototype`'s artifact lifecycle: run prototype code in the disposable `.tmp/` area; capture its question, verdict, and supporting evidence in the relevant Kosmic research memo, Quick Task, or Story Technical Notes; then delete the prototype. A committed throwaway branch and external implementation issue pointer are not required.
- `ask-matt`, `implement`, `setup-matt-pocock-skills`, `triage`, `to-spec`, and `to-tickets` are not invoked by Kosmic. Their tracker-oriented orchestration must not bypass or duplicate Kosmic.
- The Projection CLI has no runtime dependency on upstream skills. It continues to validate and publish Project Knowledge projections deterministically.
- The integration records the upstream revision/installer contract used for compatibility tests. Updating it requires review against this specification and ADR 0001.

## Testing Decisions

- Test through the highest externally observable seam: installer/adapter behavior and Kosmic task-routing instructions, not source-text presence alone.
- Verify a complete supported-agent installation succeeds only when every required skill is discoverable.
- Verify every missing required skill produces a failure that names the missing skill and setup remedy, with no Project initialization or contributor workflow continuation.
- Verify adapter discovery includes the transitive `grilling` requirement for `grill-with-docs` and the design-vocabulary availability expected by `tdd`.
- Exercise Story implementation routing and assert it preserves prerequisite checks, research, red-capable behavior tests, review, knowledge refresh, and Consumer Interface completion.
- Exercise review routing against a pinned base and a local Story/Quick Task spec; assert Standards and Spec findings are separately retained in the Kosmic ledger.
- Exercise a bug workflow from a reproducible failure through regression test and review; assert an unsupported symptom-only completion cannot pass.
- Exercise high-risk Architecture and ADR-worthy Quick Task decisions with and without material alternatives; assert grilling occurs only for the former.
- Exercise a prototype path; assert its artifacts stay disposable and cannot satisfy code-completion or release gates.
- Run the existing Projection CLI behavioral suite unchanged to prove the external procedure dependency does not alter deterministic project-skill generation.

## Out of Scope

- Vendoring, forking, or rewriting Matt Pocock skills.
- Installing the complete upstream catalogue or invoking its top-level routers.
- Introducing an external issue tracker, issue labels, or a second spec/ticket lifecycle.
- Changing the Project Knowledge format, Audience Scope rules, Project Skill Pair shape, or Projection CLI output format.
- Providing a native fallback when required skills are unavailable.
- Automatically updating upstream skills without explicit compatibility review.

## Further Notes

The required dependency is compatible with the upstream MIT license because Kosmic references independently installed skills rather than redistributing their contents. If future distribution vendors any upstream material, preserve its license notice, record the exact upstream revision, and add license compliance to release verification.
