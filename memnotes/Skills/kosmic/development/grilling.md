---
type: Domain Topic
id: kosmic/development/grilling
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Interview the user in frontier rounds over a design tree until no decision is silently assumed.
triggers: [grill me, stress-test plan, question rounds, design tree interview]
source_project: native
source_sha256: empty
aliases: [grilling]
---

# Grilling

Interview the user relentlessly until both sides share one understanding.
Map the discussion as a design tree: every decision branches into the
decisions that hang off it.

## Rounds and the frontier

The frontier is every decision whose prerequisites are already settled, so
the question can be asked now without guessing. Ask the whole frontier in
one round:

- Number each question.
- Give a recommended answer for each question.
- Wait for the user's answers before the next round.

Each answer reshapes the tree. Settled decisions push the frontier outward
and unblock dependent questions. Recompute the frontier after every round.
A question that depends on a question still open in this round belongs to a
later round.

Format each question as:

```
❓ **Q1** - **<question title>**: <question body>

➡️ <recommended answer>
```

## Facts and decisions

Finding facts is the interviewer's job, never the user's. When a frontier
question needs an environment fact, dispatch a subagent to look it up. Do
not block the round on it: only the questions downstream of the running
exploration wait; ask the rest of the frontier now. Decisions stay with the
user. Put each decision to the user and wait.

## End state

The session ends when the frontier is empty: every branch visited, nothing
silently assumed. Do not act on the plan until the user confirms the shared
understanding.
