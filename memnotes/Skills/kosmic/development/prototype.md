---
type: Domain Topic
id: kosmic/development/prototype
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Build throwaway prototypes that answer one explicit design question, then dispose of them after capturing the verdict.
triggers: [prototype, throwaway demo, sanity check state model, ui variant prototype]
source_project: native
source_sha256: empty
aliases: [prototype]
---

# Prototype

A prototype is throwaway code that answers one explicit design question.
The question decides the shape.

## Pick the branch

- **Logic or state question**: create one self-contained HTML file that a
  non-developer can open directly. State the question visibly. Keep the
  answer-bearing logic as a pure reducer, state machine, or pure functions;
  keep DOM code as a thin shell. Render the full relevant state after every
  action. Include free-play action buttons plus resettable guided
  walkthroughs for happy, edge, and illegal cases. Use domain language and
  no framework.
- **UI question**: generate at least three genuinely structural variants,
  preferably on an existing route. Switch variants through a `?variant=`
  parameter and a fixed bottom switcher. Keep existing data loading outside
  the variants, gate the switcher out of production, and do not wire real
  mutations.

When the question is ambiguous and the user is unreachable, match the
surrounding code: a backend module points to logic, a page points to UI.
State the assumption at the top of the prototype.

## Rules

1. Mark the prototype obviously and make it trivial to run: one command, or
   one double-click for an HTML file.
2. Keep state in memory by default. Persistence is what a prototype checks,
   not what it depends on. Any persistence is isolated and clearly
   wipeable.
3. Skip polish, exhaustive error handling, and speculative abstraction.
4. Surface the relevant state or variant change after every action.
5. Under Kosmic, run prototype artifacts under `.tmp/`. Record the
   question, the verdict, and the evidence in the relevant Research memo or
   Story Technical Notes, then delete the prototype. The prototype never
   satisfies an implementation, review, or release gate.
