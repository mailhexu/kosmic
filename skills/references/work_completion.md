# Receipt completion

Load before recording completion observations and review, or `work finish` for a Story or Quick Task. This reference defines proof mechanics; Task 7 defines how reviewers reach their decisions.

## 1. Prepare the record

Start in a registered clean writer with `work start`. Pin `review_base` before implementation and retain it through all review rounds. Completion evidence lives inside the governing work record's frontmatter; declare the review binding up front:

```yaml
review_base: "<pinned review baseline>"
review_round: 0
completion_observations: []
completion_review: {}
```

Start `review_round` at 0; advance it only after a completed Standards + Spec pair on the held snapshot (1..3). The requested pair/round number belongs to the frozen handoff, not to a pre-incremented completed count.

Use the exact case-sensitive heading `## Acceptance Criteria`. Put each complete criterion on one physical checklist line (`- [ ] ...` or `- [x] ...`). The validator matches that line's text exactly; wrapped continuation lines do not extend the criterion.

**Complete when:** the approved record, baseline and every criterion are unambiguous.

Before any routine re-review submission, apply the Task 7 §2.6 readiness barrier (`task_review_spec.md`): every unresolved Blocking row carries a complete worker response, and genuinely blocked prerequisites are escalated — not submitted.

## 2. Record embedded completion observations

Run the changed behavior and record actual observations, including limitations, directly in the record frontmatter as `completion_observations` — a list of entries, each with non-empty `criterion`, `observation` and `source` strings. There is no outcome field and no artifact manifest: the validator applies a structural gate only, requiring the set of `criterion` texts to equal exactly the `## Acceptance Criteria` checkbox texts (unknown, repeated or uncovered criteria are rejected with `ACCEPTANCE_INVALID`). Sufficiency of the observations — including adverse findings — is judged by the recorded independent review, never by parsing wording.

```yaml
completion_observations:
  - criterion: "Export preserves the input identifiers."
    observation: "The exercised export retained identifiers A and B; a wrapped identifier truncated once at 4096 bytes, recorded as a non-blocking finding."
    source: "python3 scripts/export.py --check; output retained in the session log"
```

`source` names where the observation comes from (command, exercise, or captured output). Paths mentioned in observations are informational; the validator hashes no artifacts. Keep observations truthful and complete: they are the durable record of what was actually exercised, published verbatim in the receipt's bound record bytes.

**Complete when:** every criterion has exactly one truthful embedded observation with a concrete source.

## 3. Pin reviewed source and decisions

`review_base` is the fixed review baseline; `review_round` is an integer 1..3 recorded in the record frontmatter by the time of finish, after the approved pair — 0 is the pre-review initializer value, never a finish state. `reviewed_revision` is **not Git HEAD**: it is the SHA-256 reported as `source_revision` by `work prepare-completion` with an explicit `--worktree`. It binds the current uncommitted writer delta, excluding `.tmp`, `.git` and STATUS output. When Project and writer coincide it also excludes Project metadata directories; when the Project is nested inside the writer it excludes **every path under that Project prefix**, including any Project-local source. With a separate external Project it excludes no writer Project prefix. This is the current validator's boundary, not comprehensive review coverage: reviewers must inspect all owned deltas against the pinned baseline, including excluded or already committed files. An empty source delta has its own hash and does not prove those files were reviewed.

After implementation, obtain the value from the read-only completion preparation command; replace the absolute paths and the record reference:

```bash
python3 /absolute/kosmic/scripts/kosmic_project_skills.py work prepare-completion \
  --project /absolute/Project \
  --work-record example/quick-task/check-export \
  --worktree /absolute/writer
```

The successful JSON keeps the existing `identity`, `record_path` and `completion_observations` payload, preserving every authored observation, and adds the top-level `source_revision` string only because `--worktree` is supplied — that value is the reviewer pin. Preparation resolves the authorized record live, computes the digest through the same unchanged function finish enforces, and writes nothing: the returned digest is a point-in-time observation, never cached permission, evidence, or approval.

Independent Standards and Spec reviewers review the actual delta against the pinned baseline. The review packet bounds to the actual delta plus its acceptance context — the fixed review base, acceptance criteria, embedded observations, checks, and adverse facts. Two distinct independent axes, stable finding IDs, rounds 1–3, and the fixed base never shrink; low risk limits packet scope and depth only, while numerics/scientific claims, methods, security, and API/data/schema/publication/receipt content always receives the stronger domain review, judged from content and blast radius — never from line count. Unchanged inputs receive no fresh audit round; a changed input or contract, or a previously failed check, reruns only the affected checks on the fixed base, and scientific validation is never skipped. Record their real identities and decisions in the embedded `completion_review` frontmatter dict, with stable finding IDs. Preserve the ledger during re-review; after three automated rounds escalate remaining blockers for explicit human acceptance — a failed review never downgrades to a lighter pass.

```yaml
completion_review:
  reviewer: "<coordinating reviewer identity>"
  axes:
    standards: {decision: "approved", reviewer: "<actual reviewer identity>"}
    spec:      {decision: "approved", reviewer: "<different actual reviewer identity>"}
  decision: "approved"
  review_base: "<pinned review baseline commit>"
  reviewed_revision: "<computed source_revision value>"
  findings: []
  scope: ["<declared finish --scope claims, e.g. worktree:src/export.py>"]
```

The review binds to the record through the fixed `review_base` and `review_round` metadata (`review_base` in the review must equal the record's; `review_round` must be an integer between 1 and 3) and requires a non-empty top-level `reviewer` identity plus independent named reviewers on both the `standards` and `spec` axes under the nested `axes` mapping, each with `decision: approved`; the legacy root-level axes shape is not accepted on new records. The overall `decision` must be `approved`, or `user-accepted` with a non-empty `approved_by`; any other value fails as `REVIEW_INVALID`. Findings is a list of objects with stable non-empty `id`s. A blocking finding (`disposition: Blocking`) must carry `status: resolved`, or an explicit risk acceptance with `status: risk-accepted` plus non-empty `risk_accepted_by` and `risk_acceptance_note` naming the human who accepted the risk and why. Finally `reviewed_revision` must equal the current `source_revision(worktree, project, record)` — any source change after the recorded review fails completion as `REVIEW_INVALID` ("reviewed revision differs from current work"). Preserve actual decisions and escalate a mismatch rather than manufacture approvals. A computed digest is a binding, not approval. Source edits or commits can change that binding: reconcile with reviewers before updating it; preserve independent coverage of excluded paths and never commit unrelated drift to manufacture an empty delta.

**Complete when:** actual review decisions cover the current source and the computed revision matches the work being completed.

The coordinator re-review protocol — pre-submit readiness barrier, blocked escalation, the frozen identical handoff payload delivered to both axes, pair-based round counting with the max-3 human decision packet, and worker-response/resolution semantics — is defined once in Task 7 §2.6 (`task_review_spec.md`); follow it there before assembling any handoff. Note only that `source_revision` **excludes nested Project record bytes** and therefore does not freeze acceptance observations, ledger or context: when the nested record/context changed while the computed revision is unchanged, reviewers recheck the changed context and the coordinator re-freezes the handoff. No persistent context hash or sidecar exists.

## 4. Finish with precise scope

Trust the successful `work finish` receipt: one invocation runs every gate below (observations, scope, review, domain precheck, freshness) and publishes the receipt as the authoritative completion marker — no `--help` discovery and no second validation command follow a successful finish. Standalone `check-completion` is an optional fail-fast diagnostic, run only when a gate has failed or to preview a refusal before finishing, with its exact documented flags:

```bash
python3 /absolute/kosmic/scripts/kosmic_project_skills.py check-completion \
  --project /absolute/Project \
  --work-item /absolute/Project/specs/quick-tasks/check-export.md \
  --source-root /absolute/writer \
  --work-record example/quick-task/check-export
```

(`--source-root` defaults to the current directory; `--work-record` is optional and names the record authority.) Pass every output scope separately to the checked finish command:

```bash
python3 /absolute/kosmic/scripts/kosmic_project_skills.py work finish \
  --project /absolute/Project --worktree /absolute/writer \
  --work-record example/quick-task/check-export \
  --scope worktree:src/export.py \
  --scope project:specs/quick-tasks/check-export.md
```

For a Project nested in the writer, `project:PATH` claims use Project-relative paths; `worktree:PATH` claims cover paths outside that Project and use writer-relative paths. For a separate external Project, writer changes use `worktree:` claims. If Project and writer roots coincide, declared paths are relative to that common root. Declare actual owned outputs; broad scope does not authorize unrelated edits. Finish checks the current uncommitted delta, not a historical attribution ledger: preserve the pinned baseline and owned-delta review separately.

The reviewed `completion_review.scope` claims are part of that contract: a typed list that may be empty for record-only work, they must be valid `worktree:PATH`/`project:PATH` claims, and at finish the actual changed paths (checked with the same publication exemptions) must be covered by the finish claims first (`SCOPE_DENIED` precedence unchanged) and by the reviewed claims (`REVIEW_INVALID`, "reviewed scope does not cover the actual work"). Reviewed claims may be broader than the finish claims — harmless narrowing of the executed finish is accepted; exact raw-string equality is not required.

**Runtime phase requirement**: checked `work finish` accepts records in an active phase (`approved` or `in_progress`) and refuses a record set to `review` (`WORK_PHASE_DENIED`). The code-review decision lives in the embedded `completion_review` mapping, not in the record status: keep the record in its active phase after review approval, and let only a successful finish write `done`. Never move a record into `review` ahead of finish — the generic `review` lifecycle status remains valid for legacy records, but the checked finish sequence must never strand a record in it; if a record sits in `review`, return it to `in_progress` (decision already recorded) and finish.

One ordinary finish resolves record authority first, then checks the embedded observations, the finish-claim scope diff (`SCOPE_DENIED` precedence), the review decision (nested axes, revision binding, reviewed-scope coverage) and finally the complete shared read-only domain precheck — the same helper standalone `check-completion` runs — covering depends_on, STATUS freshness, retired inputs, `consumer_interface_change`, math/proposal/routine contracts, related stable usage notes, and projection. A truthy non-mapping `completion_review` (list, string, number) is never coerced: the entry snapshot stays safe and the malformed value is refused `REVIEW_INVALID` at that same ordered review gate, after the observation and finish-claim checks. A domain refusal surfaces as `COMPLETION_PRECHECK_FAILED` with the original diagnostic retained; the other codes above are unchanged. Keep the derived STATUS current (`generate-status` after record edits) so the freshness gate observes a clean state, and keep the Project config readable — a missing or unreadable config is reported on this path, not swallowed. A final freshness recheck immediately before publication rejects any record, source-binding, or authority change that happened while the gates ran; nothing is repinned or auto-repaired, so rerun finish. The former `evidence_packs` completion gate and the pack-to-note linkage check are retired with no replacement (knowledge-first notes per `docs/adr/0004-knowledge-first-notes.md`): no pack, sidecar, or ledger entry is required to complete a work record, and no current command audits or blesses legacy packs.

Finish then updates the record status, indexes and log, publishes the successful receipt as the authoritative completion marker, and only then derives the STATUS projections from that receipt. The published receipt binds exactly the completed record: `proof` is exactly `{record_path: record_sha256}`, where `record_path` is the record path relative to the Project root and `record_sha256` is the SHA-256 of the completed record bytes at finish. Because only the record bytes are bound, later refinement of linked notes or data documents never revokes completion; conversely any post-receipt edit of the work record itself breaks the receipt by design — drift detection, not adversarial authentication, and reviewer attribution and the trusted publication path remain required. Publication is stepwise, not cross-file atomic: an interruption between steps can leave a valid receipt with stale derived reports. After interruption rerun finish; when the existing receipt is already valid, the retry regenerates the derived reports without rewriting the receipt or duplicating the completion log. Validate the successful terminal receipt through `kosmic_completion.check_terminal_receipt(project, record)` (resolve with `allow_terminal=True`) only when recovering from an interruption or diagnosing a refused finish — never as a routine post-success step; `work start` and ordinary implementation gates deny terminal records.

A rerun with a receipt already present takes the terminal route: identity and approved ancestry are re-resolved, the receipt is validated over the unchanged record bytes (legacy receipts byte-verify only their recorded originals below), the record's declared formal math/proposal/routine contracts are rechecked exactly as the plain done path checks them, and only the derived STATUS reports are repaired while the receipt and completion log stay byte-identical. Evolving notes, data, and the current source delta are never re-hashed, and historical pins are never refreshed. A present but unreadable or inconsistent receipt is refused (`COMPLETION_PENDING`/`COMPLETION_DRIFT`) without re-blessing or repinning; only an absent receipt reruns every nonterminal gate, so an interrupted episode recovers through the full gate order and is never conflated with terminal success.

### Legacy receipts

Receipts published before this contract recorded their proof against acceptance/review sidecar files and artifact digests. The completed record itself still names its recorded originals through `acceptance_evidence` and `review_record`; terminal validation classifies the legacy originals from those references and byte-verifies exactly them (a missing original surfaces as explicit `COMPLETION_PENDING`, "historical receipt original missing"; a changed original as `COMPLETION_DRIFT`, "historical receipt original changed"), together with each original's schema/identity/record binding and the artifact digest maps recorded inside it. The recorded artifact, note, and dataset digests are historical facts: current raw files are never opened or re-hashed after the receipt, so later note or dataset evolution cannot revoke a legacy completion. A legacy receipt whose proof no longer names every recorded original — including an empty proof map — stays explicitly pending. A future approved migration carries legacy receipts onto the record-bound shape only through an explicit field-by-field mapping record — criteria, outcomes, observations, artifact references and digests, reviewer identities, findings, revisions — demonstrated against the unchanged originals before and after the carry-over; it never re-blesses or repins current bytes. Legacy receipts are never repinned or re-blessed against current bytes: rerunning `finish` on a drifted legacy receipt propagates the terminal error or fails the embedded gates; it does not rewrite the receipt.

**Complete when:** `work finish` returns a successful receipt — that receipt is sufficient proof of completion; no second terminal validation or STATUS inspection follows a successful finish. Terminal receipt validation applies only when recovering from an interruption or diagnosing a refusal. Until then, report review/verification results separately from lifecycle completion.

## 5. Preserve the writer and integrate

Commit the verified record-owned source, review-bound record, log and receipt in the isolated writer. Preserve unrelated work in every destination. Before integration compare destination bytes with the captured baseline for each owned path; source drift requires reconciliation, not overwrite. Integrate only those owned deltas. Installation has its own approved adapter plan and validation; canonical skill edits do not authorize editing installed user-authored skills.
