# Deterministic Flat Spec Migration Specs

- [PRD](prd.md) — approved 2026-10-11.
- [Architecture](architecture.md) — approved 2026-10-11.
- [Epic 001: Script-driven flat-spec migration](epics/epic-001.md) — approved 2026-10-11.

## Implementation Stories

| Story | Status | Dependency | Scope |
|---|---|---|---|
| [001: Complete and save deterministic migration plans](stories/story-001.md) | done | done | Saved plans, nested YAML and corrected inbound-link handling; user accepted three post-cap source findings. |
| [002: Apply approved plans and recover interruption](stories/story-002.md) | done | done | Approved plan apply, rollback, interruption recovery, candidate-run finalization and idempotent receipts. |
| [003: Integrate and verify the migration workflow](stories/story-003.md) | done | done | Integrated CLI plan/apply/recover behavior and final catalog/link validation. |

All three Stories have checked completion receipts. The separately approved live Kosmic Project migration was applied successfully; the receipt and 112-record mapping are recorded at `.kosmic/migrations/b1a87b1dd0c4626b2946b99cc2f757161ba001c7f2794ff4a2ad63991140575f/receipt.json`. The Project remains unbound and installed skills were not changed. Source review retains the original capped three-round ledger; the user accepted its three remaining findings, and separate scoped review approved later scratch/index fixes.
