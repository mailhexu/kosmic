# Task R: Research

Run optional discovery before Architecture when the PRD is clear enough to define the problem, but the solution space is still uncertain.

Research is not Task 3 Search. Task 3 Search is mandatory retrieval of existing notes and specs. Research starts after Search when existing knowledge is not enough and produces a written memo with findings, options, recommendations, and open questions.

Read-only research/search is record-free. A persisted research memo must name its local governing planning record and stay within the bounded approved planning outputs; a PRD is not implementation authority. Persistent experiments/config/source changes require an approved Story or qualifying approved Quick Task, explicit roots/scope and observed evidence. Do not infer an extra research approval gate where this procedure supplies none.

---

## When to Use

Use Research after a PRD exists when any are true:

- Technical feasibility is unclear.
- Multiple architecture approaches are plausible.
- An unfamiliar library, framework, service, or protocol may be needed.
- Risks or assumptions would make Architecture speculative.
- The user says "research", "do discovery", "spike", "investigate options", or "validate assumptions".

Skip Research when Task 3 Search answers the question well enough to draft Architecture confidently.

---

## Output

Create one research memo per topic, inside the governing subproject owner
root returned by `spec-create --kind prd`:

```text
{VAULT}/Projects/{TARGET}/subprojects/{SUBPROJECT_ID}/specs/research/{YYYY-MM-DD}-{slug}.md
```

Never write research memos into the shared Project `specs/` tree or a
guessed subproject path; use the recorded owner root of the linked PRD.

Use `references/templates/template-research.md`.

---

## Procedure

1. **Start with Task 3 Search**
   - Search notes and specs first.
   - If existing knowledge is enough, summarize it and skip the research memo.

2. **Frame the research question**
   - Link the PRD.
   - State the decision or uncertainty to resolve.
   - Timebox the investigation when possible.

3. **Investigate**
   - Read relevant code and existing patterns.
   - Check external documentation or examples when libraries/services are involved.
   - Compare viable options and document tradeoffs.
   - Invoke `research`: investigate through primary sources and capture citations in the Kosmic research memo.

4. **Document findings**
   - Write the research memo.
   - Set `status: done` only when findings, recommendation, and open questions are captured.
   - Add notes for durable knowledge that should outlive the spec.

5. **Feed Architecture**
   - Link the research memo from Architecture.
   - Convert recommendations into ADRs or design constraints.
   - If findings change product scope, update the PRD and return to PRD approval.

---

## Gate Behavior

Research does not add a new approval gate. It feeds existing gates:

- Product-scope changes → update PRD and use PRD approval.
- Technical-direction changes → include in Architecture and use Architecture approval.
- Implementation details → carry into stories and story Phase 1 research.

---

## Distinction From Other Research

| Activity | Required? | Purpose | Output |
|----------|-----------|---------|--------|
| Task 3 Search | Mandatory | Retrieve existing notes/specs | Relevant notes/specs read |
| Optional Research | Optional | Resolve planning uncertainty before Architecture | Research memo |
| Story Phase 1 Research | Mandatory for implementation | Verify concrete implementation details | Story Technical Notes |
