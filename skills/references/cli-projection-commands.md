# CLI Projection Commands

Consumer reference for Projection CLI commands. Each command's owning story
maintains its section here; cross-cutting reconciliation is Story 005's.

## generate-status

Regenerate the derived `STATUS.md` inside the Project's bound status root:

```bash
python3 skills/scripts/kosmic_project_skills.py generate-status \
    --project {VAULT}/Projects/{TARGET} \
    --work-record {QUALIFIED_RECORD}
```

STATUS is a deterministic, receipt-aware projection of the spec catalog. The
explicit `--work-record` authority is re-resolved at invocation time and
never cached; the only mutated path is the bound `<status-root>/STATUS.md` —
records, receipts, and sources are never written by this command.

Completion and valid-receipt retries likewise publish only to the already
configured `ProjectEntry.status_root`; registered directories are not
additional STATUS destinations, and without a bound root completion writes no
external STATUS file. On `generate-status`, a healthy catalog still renders in
full. If unrelated catalog or ancestry defects prevent that render, the
command can use a clearly labeled bounded view of the current record's owner
only after the explicit record's identity, authority, and applicable ancestry have passed validation.
Defects in the current record's authority or applicable ancestry still refuse
in every case. Without a configured history policy, a defect in any retained
owner/shared hierarchy refuses as well; a configured history policy keeps its
existing structural bounded rendering. `validate` remains strict.

**Record authority (ADR-E).** Implementation records keep their exact legacy
grants at this command: a `story` or `quick-task` with `approved` or
`in_progress` status authorizes the refresh unchanged, including
project-level quick-task authority against a fixed-subproject bound
directory. Additionally, bounded planning records authorize this one
derived-output refresh under a selective matrix:

- an **approved** `prd` or `architecture` record;
- a **draft** `prd`, `architecture`, `epic`, or `story` record, while the
  record's own hierarchy governs the derived output path — with a
  Project-wide (unregistered) status root, or with a registered directory
  whose binding is fixed to the record's own subproject; a draft `story`
  additionally requires its approved ancestry chain.

Everything else is refused with `WORK_PHASE_DENIED` and nothing is written:
a `draft` quick-task, an `in_progress` prd/architecture, an approved
`epic`, terminal statuses, and any planning record whose ancestry does not
govern the bound directory (for example, a foreign owner against a
fixed-subproject bound directory). A draft record never narrows the
Project-wide rendered view, and planning authority never creates, replaces,
or silently drops the status-root binding.

**Failure codes**: `STATUS_ROOT_UNBOUND` (no bound status root),
`STATUS_ROOT_MISSING` (bound root is not a directory), `WORK_PHASE_DENIED`
(record kind/status or scope does not authorize this refresh),
`WORK_RECORD_REQUIRED` (missing `--work-record`).

Planning refreshes validate no receipt and write none; validation and
completion checks still fail with `STATUS_STALE` while the generated file
drifts. STATUS is generated — hand edits are never preserved or merged; the
next authorized run regenerates over them.

## validate --history-audit

`validate --history-audit` forces the existing read-only historical integrity
inspection for the exact records configured by the Project's
`history_integrity.records` policy, regardless of whether its mode is `warn`
or `strict`:

```bash
python3 skills/scripts/kosmic_project_skills.py validate \
    --project {VAULT}/Projects/{TARGET} \
    --history-audit
```

The option is available only on `validate`. It requires a configured,
non-empty record scope; missing or empty scope is a configuration error
(exit 2), and malformed, stale, or otherwise invalid configured paths fail
before other validation. Under `warn`, the flag performs the same strict
integrity checks as the configured `strict` mode, so detected integrity
failures make validation fail before STATUS freshness is checked. Without the
flag, validation order and behavior are unchanged.

This is an invocation-time audit of configured records only. It does not
change policy, records, receipts, proposal pins, `STATUS.md`, or any other
file, and it is not completion proof or authority. The override is not passed
to generation or operational commands; it neither changes the standing
policy nor establishes persistent audit state.
