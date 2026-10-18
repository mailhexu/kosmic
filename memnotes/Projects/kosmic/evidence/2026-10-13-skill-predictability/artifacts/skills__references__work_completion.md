# Receipt completion

Load before preparing acceptance evidence, a review record, or `work finish` for a Story or Quick Task. This reference defines proof mechanics; Task 7 defines how reviewers reach their decisions.

## 1. Prepare the record

Start in a registered clean writer with `work start`. Pin `review_base` before implementation and retain it through all review rounds. Declare Project-relative proof files:

```yaml
acceptance_evidence: [evidence/example/acceptance.json]
review_record: evidence/example/review.json
review_base: "<pinned review baseline>"
```

Use the exact case-sensitive heading `## Acceptance Criteria`. Put each complete criterion on one physical checklist line (`- [ ] ...` or `- [x] ...`). The validator matches that line's text exactly; wrapped continuation lines do not extend the criterion.

**Complete when:** the approved record, baseline and every criterion are unambiguous.

## 2. Capture observations and artifacts

Run the changed behavior and record actual observations, including limitations. `acceptance.json` has one result for every criterion, with exact text, `outcome: passed`, and an observation. An unsuccessful or unexercised criterion prevents completion.

```json
{
  "schema": "kosmic.acceptance-evidence/1",
  "identity": "example/quick-task/check-export",
  "record_path": "specs/quick-tasks/check-export.md",
  "results": [{
    "criterion": "Export preserves the input identifiers.",
    "outcome": "passed",
    "observation": "The exercised export retained identifiers A and B.",
    "artifacts": [{"path": "evidence/example/export.json", "sha256": "<actual 64-character SHA-256>"}]
  }]
}
```

All proof and artifact paths are relative to the owning Project root, not the evidence directory or repository root. They must resolve to regular files inside that Project, without traversal or symlinks. For source/tests/Shared Library artifacts outside the Project, retain verified byte-identical evidence copies inside `evidence/`; name the original source and capture time in the observation. Hash the retained bytes. Keep artifacts independent of the record that finish rewrites; using that record itself as an artifact makes its hash stale at completion.

**Complete when:** every criterion has truthful evidence and every declared artifact is contained and hash-verifiable.

## 3. Pin reviewed source and decisions

`review_base` is the fixed review baseline. `reviewed_revision` is **not Git HEAD**: it is the SHA-256 returned by `kosmic_completion.source_revision(worktree, project, record)`. It binds the current uncommitted writer delta, excluding `.tmp`, `.git` and STATUS output. When Project and writer coincide it also excludes Project metadata directories; when the Project is nested inside the writer it excludes **every path under that Project prefix**, including any Project-local source. With a separate external Project it excludes no writer Project prefix. This is the current validator's boundary, not comprehensive review coverage: reviewers must inspect all owned deltas against the pinned baseline, including excluded or already committed files. An empty source delta has its own hash and does not prove those files were reviewed.

After implementation, compute the value using the same installed/source scripts as the CLI. The following is a read-only Python invocation; replace the three absolute paths and the record reference:

```bash
python3 - /absolute/kosmic/scripts /absolute/Project /absolute/writer specs/quick-tasks/check-export.md <<'PY'
import sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from kosmic_work import resolve_work_record
from kosmic_completion import source_revision
project, writer = Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve()
record = resolve_work_record(project, sys.argv[4])
print(source_revision(writer, project, record))
PY
```

Independent Standards and Spec reviewers review the actual delta against the pinned baseline. Record their real identities and decisions, with stable finding IDs. Preserve the ledger during re-review; after three automated rounds escalate remaining blockers for explicit human acceptance.

```json
{
  "schema": "kosmic.work-review/1",
  "identity": "example/quick-task/check-export",
  "record_path": "specs/quick-tasks/check-export.md",
  "review_base": "<same pinned baseline as the record>",
  "reviewed_revision": "<computed source_revision value>",
  "round": 1,
  "standards": {"decision": "approved", "reviewer": "<actual reviewer identity>"},
  "spec": {"decision": "approved", "reviewer": "<different actual reviewer identity>"},
  "findings": [],
  "decision": "approved"
}
```

Blocking findings use `disposition: Blocking` and `status: resolved` when fixed. Unresolved blockers require the governed `user-accepted` final decision and `approved_by`, with explicit human acceptance. The current proof validator also requires both axis decisions to be `approved`; human acceptance alone does not satisfy that check. Preserve actual decisions and escalate a mismatch rather than manufacture approvals. A computed digest is a binding, not approval. Source edits or commits can change that binding: reconcile with reviewers before updating it; preserve independent coverage of excluded paths and never commit unrelated drift to manufacture an empty delta.

**Complete when:** actual review decisions cover the current source and the computed revision matches the work being completed.

## 4. Finish with precise scope

Run existing read-only completion gates with `check-completion --help` for that CLI's flags. Pass every output scope separately to the checked finish command:

```bash
python3 /absolute/kosmic/scripts/kosmic_project_skills.py work finish \
  --project /absolute/Project --worktree /absolute/writer \
  --work-record example/quick-task/check-export \
  --scope worktree:src/export.py \
  --scope project:evidence/example
```

For a Project nested in the writer, `project:PATH` claims use Project-relative paths; `worktree:PATH` claims cover paths outside that Project and use writer-relative paths. For a separate external Project, writer changes use `worktree:` claims. If Project and writer roots coincide, declared paths are relative to that common root. Declare actual owned outputs; broad scope does not authorize unrelated edits. Finish checks the current uncommitted delta, not a historical attribution ledger: preserve the pinned baseline and owned-delta review separately.

Finish checks evidence, review revision, scope and authority, then updates status/indexes/STATUS/log and writes its receipt last. After interruption rerun finish. Validate the successful terminal receipt through `kosmic_completion.check_terminal_receipt(project, record)` (resolve with `allow_terminal=True`); `work start` and ordinary implementation gates deny terminal records.

**Complete when:** finish returns a successful receipt and terminal receipt validation confirms the current record and proof. Until then, report review/verification results separately from lifecycle completion.

## 5. Preserve the writer and integrate

Commit the verified record-owned source, evidence, review, log and receipt in the isolated writer. Preserve unrelated work in every destination. Before integration compare destination bytes with the captured baseline for each owned path; source drift requires reconciliation, not overwrite. Integrate only those owned deltas. Installation has its own approved adapter plan and validation; canonical skill edits do not authorize editing installed user-authored skills.
