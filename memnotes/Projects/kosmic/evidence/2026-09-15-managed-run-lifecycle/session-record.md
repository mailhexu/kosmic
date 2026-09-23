# Session Record — Managed Run Lifecycle Implementation

- Date: 2026-09-15.
- Scope: Stories 044 (Git evidence and run store), 045 (lease-backed lifecycle), 046 (retention and receipts), 052 (owner cleanup transaction and recovery), 047 (promotion and complete reporting), 048 (temporary caller migration), plus the Task P intake for Stories 053 and 056.
- Review base pinned at `c52ab6a15b2dab0df9cbd450a76fcdc386612cdb`; the working copy additionally held pre-existing unrelated changes recorded in `log/kosmic-2026-09-14.md`.
- Implementation lives in `skills/scripts/kosmic_runs.py` (lifecycle) and `kosmic_project_skills.py` (`scratch` verbs, `managed_command_run`, migrated `validate_current_projection` and `collect_provenance`).
- Verification commands and outcomes are recorded in `behavioral-validation.md` and `log/kosmic-2026-09-15.md`.
- Deliberately not delivered: general `gc --apply` (constant `GC_APPLY_ENABLED = False`), publication markers and detection (Story 056, Task P-blocked), skill-prose cutover (Story 053, Task P-blocked).
