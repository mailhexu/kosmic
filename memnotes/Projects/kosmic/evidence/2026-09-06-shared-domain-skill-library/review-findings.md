# Shared Domain Skill Library review findings

## Independent Task 7 review

Standards and Spec reviewers ran in parallel against the approved PRD, Architecture, Epics 14–16, and Stories 025–030.

Initial verdict: FAIL. Findings:

1. Stable topics could load draft/deprecated dependencies.
2. A failure moving the prior installed router could delete it during rollback.
3. Migration could reclassify Development content as Usage.
4. Skill Proposal fingerprints omitted Evidence Pack paths and governance tests were incomplete.
5. Domain-root progressive routes were unsupported.
6. Recipe Packet byte budgets omitted generated framing.
7. Generated router instructions named a nonexistent executable and omitted policy limits.
8. Typed errors, exclusion traces, check-install activation wording, and pre-swap migration generation were incomplete.
9. Release Evidence, ledger, log, and behavioral-equivalence records were pending.

## Resolution

All implementation findings were fixed and regression-tested. Stable dependencies now fail with `BROKEN_DEPENDENCY`; domain routes return domain-only plans; packet totals equal emitted UTF-8 bytes; migration preserves audience and builds generated artifacts before one atomic swap; install rollback preserves pre-replace state; proposal fingerprints include Evidence paths; router instructions use the real CLI path and fixed budgets; typed failures and exclusions are emitted; install checks state that runtime activation is unverified.

## Re-review

- Independent Standards re-review: PASS; no remaining defects.
- Independent Spec re-review: implementation PASS, followed by one delivery finding that installed router artifacts were stale.
- All four router packages were regenerated, reinstalled, and byte/identity checked after that finding.

Final release gate: PASS, with runtime adapter inventory discovery explicitly unverified until fresh sessions are opened.
