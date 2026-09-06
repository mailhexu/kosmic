# Skill Proposal Loop review findings

## Independent Task 7 round 1

Standards review judged the implementation correct and reported three non-blocking defects: a duplicate `SHA256_RE`, positional construction of a widened `SkillProposal` dataclass, and proposal headings inside fenced code being accepted as real sections.

Spec review reported two blocking deviations—the lifecycle/template did not represent `draft -> approved -> done`, and candidate paths were not machine-checked against the canonical pair—and one disputed independence finding that treated every direct update as shared despite the approved project-local same-agent fallback.

## Resolutions

- Removed the duplicate hash constant and switched `SkillProposal` construction to named fields matching AD-P3.
- Made section extraction fence-aware and added a regression test.
- Implemented `draft|approved|done` with valid decision-state combinations; removed the duplicate `action` field; renamed `inputs_manifest` to the architecture's `input_manifest` list.
- Kept subagent mode mandatory for `global-procedure` (the shared/global scope) while preserving the approved same-agent fallback with reason for `project-procedure`; added a local-update regression test.
- Required `Candidate paths: [...]` for create/update proposals and rejected paths beneath the canonical Skill Pair root.
- Added tests for approved/pending state, fenced headings, and canonical candidate rejection.

## Re-review

The Standards re-review confirmed the initial three code-quality findings resolved, then caught an over-broad interim rule requiring subagents for every update. That rule was corrected to preserve the documented project-local fallback, covered by a regression test, and received a final PASS. The independent Spec re-review found no remaining implementation defect across AD-P1..P8 and Stories 018-024.
