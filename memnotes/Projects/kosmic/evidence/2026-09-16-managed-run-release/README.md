# Managed-Run Release Dogfood (Stories 049 and 055)

Real-worktree acceptance for the managed-run initial release (Story 049) and
the combined destructive matrix (Story 055), executed inside managed run
`20260915T235202Z-story-049-initial-releas-b07740ea40706ab48c577b5e745b6671`
(diagnostic retention, succeeded after evidence promotion).

## Method

`dogfood_049.py` drives only public surfaces — the `scratch` CLI across
independent processes and the library's documented collection/recovery APIs —
and builds its isolated Git vault under the run's own scratch area:

1. **live-status** — cross-process `scratch status` reports a live active run.
2. **promotion** — cross-process `scratch promote` verifies source/destination
   hashes (`destination_sha256 == source_sha256`).
3. **success-cleanup** — `scratch succeed` removes the disposable run.
4. **retention-extension-accounting** — exact 72 h failure retention, 7-day
   extension cap enforced (rejection then acceptance), dry-run GC byte
   accounting with the failed run classified `retained`.
5. **holder-crash-recovery** — killed holder yields an abandoned candidate with
   a grace window; owner replay succeeds and removes the run.
6. **secret-redaction** — a credential-shaped purpose never reaches the
   manifest, history, or handle (redacted at begin).
7. **combined-destructive-matrix** — `gc --apply` removes only the abandoned
   run while the unexpired failed run is retained; after expiry, bounded
   startup collection removes it; unrelated worktree files are untouched; every
   cleanup history record carries a Git delta; a crashed whole-tree
   publication restores the prior canonical tree.

## Results

`dogfood-results.json` records `all_ok: true` with all seven checks green.

## Reproduction

```bash
python3 memnotes/Projects/kosmic/evidence/2026-09-16-managed-run-release/dogfood_049.py /tmp/out.json
```
