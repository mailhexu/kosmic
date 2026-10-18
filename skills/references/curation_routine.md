# Incremental Curation Routine (curation-prepare / curation-finalize)

One curation job = three explicit stages; one outer agent (manual or externally
scheduled) orchestrates them. The Project CLI stages are deterministic and
never invoke a model. Review authority stays with the human-approved work
record; nomination is the strongest automated outcome.

```text
python3 skills/scripts/kosmic_project_skills.py curation-prepare  \
    --project PROJECT --work-record REF --scope notes \
    (--from <UTC> | --baseline) [--note NOTE_PATH ...]

python3 skills/scripts/kosmic_project_skills.py curation-finalize \
    --project PROJECT --run RUN_HANDLE_FILE --work-record REF --scope notes
```

## Stage 1 — prepare (deterministic)

Prepare freezes the cutoff `U` at run start (never a `--cutoff` flag), takes
the first lower bound explicitly — `--from <exact-UTC>` or `--baseline` (a
deliberate zero-width window that scans nothing) — and selects every
interval-eligible note with `L < changed_at <= U` in the declared scope
(`notes` today). The semantic instant is frontmatter `updated`, falling back
to `created` only when the note was never updated; filesystem mtime is never
consulted.

Snapshot: revision identities only (path, `updated`, content sha256,
`skill_candidate`, `skill_resources`) for **every** eligible note — including
`skill_candidate: false` notes the reviewer may later skip — stored as
machine-JSON in the managed-run workspace. Candidate-flagged and
live-resource notes sort first (review priority). Note bytes are never
copied; nothing outside the Project `notes/` tree is scanned.

Legacy date-only `updated`/`created` values certify the whole UTC day: a day
wholly inside `(L, U]` may be reviewed with recorded uncertainty, a day wholly
outside is skipped, and a day overlapping the boundary is recorded as
**ambiguous** — it is excluded from review and blocks full-scope checkpoint
advancement until a bounded disposition resolves it. No historical times are
invented. A note with no usable timestamp fails closed (no all-history
sweep). `index.md` is the reserved bundle entry point and is never selected.

Prepare reserves the scope by writing ONE per-scope control JSON
(`.kosmic/curation/<scope>.json`): `last_successful` plus the `active_run`
reservation. While a reservation is live, a second prepare on the same scope
fails with `CURATION_SCOPE_BUSY`; a reservation whose run reached a terminal
state (or outlived the managed-run abandon grace) is cleared through the
existing `scratch fail` mechanism without touching the checkpoint. Different
scopes keep fully independent checkpoints.

The machine-JSON payload carries the frozen window, the reserved
`handle_file` (pass it back as `--run`), and the snapshot — kept inspectable
so tests can pin the frozen `U`.

## Stage 2 — semantic review (agent, not CLI)

The reviewing agent reads the selected notes in place and records outcomes
into the **existing** governing work record by adding a `curation_review`
frontmatter mapping (flow YAML, the same scalar semantics as every other
frontmatter field):

```yaml
curation_review:
  run_id: "<run_id returned by prepare>"
  reviewer: "<agent identity>"
  notes:
    - {path: "notes/example.md", revision: "<sha256 from prepare>", disposition: reviewed}
    - {path: "notes/other.md",   revision: "<sha256 from prepare>", disposition: no-action}
    - {path: "notes/legacy.md",  revision: "<sha256 from prepare>", disposition: skipped, reason: "creation-time-false candidate"}
```

Dispositions: `reviewed`, `no-action` (successful outcome; no paperwork), or
`skipped` (requires an explicit `reason`). Nominations follow the existing
proposal/review record concepts, prefer updating the existing skill topic
over creating a parallel one, and never auto-approve, publish, or install.

## Stage 3 — finalize (deterministic)

Finalize verifies, in order: the `--run` handle matches the scope's reserved
run; the `--work-record` is the currently governing `approved`/`in_progress`
record and is the SAME record the reservation carries (a foreign record fails
without touching the reserved run); the work-record review mapping names the
reserved `run_id` and gives **every** prepared identity an explicit
disposition with the exact prepared revision; and every prepared identity
still matches current instants/bytes. An in-window revision after prepare
(drift) blocks advancement; a revision saved after `U` simply belongs to the
next window. On full-scope success the checkpoint advances to exactly `U`,
the run is closed as `succeeded`, and the reservation is released.

Any missing/stale/wrong-run disposition, ambiguity, drift, or failure
releases the reservation without changing `last_successful`. A `--note`
subset run validates the same way but **never** advances the checkpoint,
whatever its outcome.

## Ground rules

- No model call, classifier, or semantic inference inside the CLI; review
  completion comes only from recorded dispositions, never from an exit
  status.
- No scheduler, daemon, queue, daily report, durable candidate list, or
  evidence pack; the only persistent outputs are the per-scope control JSON
  and the existing work record.
- Bookkeeping (linkage sync, check recording) does not bump the semantic
  `updated`; reassessment and candidate flags do (Story 002 contract).
- The routine requires an approved/in_progress work record for every stage,
  including prepare's managed scratch, re-resolved at each invocation.
