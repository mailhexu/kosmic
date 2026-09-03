# Task 7 review findings — Experience Compilation

Reviewer: self-review round 1 (cloud reviewer quota exhausted; local fallback agent unconfigured — disclosed).
Command evidence: `python3 -m unittest tests.test_project_skills_cli` → 67/67 OK after fixes.

## Ledger

| ID | Axis | Severity | Finding | Disposition |
|---|---|---|---|---|
| F-01 | Standards | Blocking | task_add_note.md template line `evidence: [] # comment` — parse_scalar returns junk string for the value; verbatim-template stable notes would fail resolution confusingly | Fixed: template line is now bare `evidence: []`; guidance stays in Step-6 prose |
| F-02 | Spec | Non-blocking | No test pinned "deprecated note does not satisfy linkage" | Fixed: test_deprecated_note_does_not_satisfy_linkage added (67/67) |
| F-03 | Standards | Non-blocking | validate_evidence_pack present-check is non-recursive; nested unlisted files escape | Accepted (flat-pack convention); revisit if packs grow subdirectories |
| F-04 | Standards | Non-blocking | Ledger reason containing " | " fails entry parse | Accepted: fail-loud is correct |
| F-05 | Spec | — | FR-010 Stage 2 not implemented | By design (could; separately approved per ADR-0003) |
| F-06 | Spec | Pass | FR-001..009, 011, 012 and AD-1..6 verified implemented; NFR-001/002/004 hold | — |
| F-07 | Standards | Pass | Exit-code discipline, append-only ledger, gate placement, 67/67 tests | — |

Verdict: **approve** (after F-01/F-02 fixes, verified by suite re-run).

Owed follow-up: an independent reviewer pass when subagent quota returns; scope = the same change set.
