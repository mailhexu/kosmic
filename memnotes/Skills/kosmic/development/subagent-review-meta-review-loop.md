---
type: Domain Topic
id: kosmic/development/subagent-review-meta-review-loop
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Convert fast parallel review findings into facts through a slow meta-review against primary sources, then correct, revalidate, and commit.
triggers: [meta-review, review findings table, review loop, adjudicate findings]
source_project: native
source_sha256: empty
aliases: [meta-review loop]
---

# Subagent Review to Meta-Review Loop

Fast reviews generate findings. A slow meta-review converts them into
facts.

## Procedure

1. **Spawn in parallel**: one numeric comparison agent against an
   independent implementation, plus one reviewer per artifact class, for
   example paper or oracle and source commits. Reviews must cite `file:line`
   and reproduce claims numerically.
2. **Table.** Record every finding in a review-results table with columns
   `# | Report | Finding | Priority | Status after meta-review | Action`.
   Include PASS and CONFIRMED rows. Negative results are evidence.
3. **Meta-review.** Adjudicate each finding and each author rebuttal
   against primary sources. Read the Fortran or math directly, and re-run
   the decisive number. Expect wrong findings and wrong rebuttals. One
   cycle produced one of each, plus meta-review-only findings such as a
   mislocalized bug, a false equivalence claim, and a dropped verification
   obligation.
4. **Correct, revalidate, commit.** Apply corrections, re-run all
   validations from scratch with no partial reruns, commit fixes separately
   from features, and refresh pinned copies of derived documents.
5. **Close-out.** Update the table status columns. Promote unfixed but real
   items to explicit port-time or Wave-N action-list entries.

## Rules

- Author rebuttals are claims, not verdicts. Sign conventions in the source
  beat both the review and the rebuttal.
- An assertion that replaces an open verification is itself a finding.
- Byte-identical or bit-stable claims must carry hash-command output, not
  prose.
