# Managed Run Lifecycle

Use a managed run for Kosmic-owned disposable material.

## Begin and finalize

```bash
python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py scratch begin --project {VAULT}/Projects/{TARGET} --purpose {task-slug} --work-record {QUALIFIED_RECORD}
```

Write only inside the returned `scratch_path`. Finalize the same handle with `scratch succeed` or `scratch fail`; both must return `code: OK`. A non-Git vault or a root that does not ignore `.tmp/` fails closed.

## Retention and promotion

Diagnostic failures remain for 72 hours and can be extended only to seven days after failure. Disposable and successful runs clean through the journaled cleanup transaction. Promote a useful regular file with `scratch promote --handle-file HANDLE --source RUN-RELATIVE --destination WORKTREE-RELATIVE`; default behavior refuses an existing destination.

## Status and cleanup

`scratch status` and `scratch gc --dry-run` classify without mutation. `scratch gc --apply --work-record REF` is an explicit authorized mutation that removes only validated expired immediate run children and returns receipts/diagnostics. Read-only commands report required maintenance; they never silently collect runs or create persistent command-run state.

## Boundary

Every managed run started by a supported mutating command carries its governing record identity. The command resolves ownership/status before creating run state. A record-less bare begin is denied while enforcement is active. Registration remains a bounded bootstrap action; manifests carry record identity, never work-session reservations or session IDs.

Runs never own durable source, pending tests, Evidence Packs, specs, logs, or user-created files. Destination-sibling staging for atomic publication is governed by the atomic publication routine, not run cleanup.