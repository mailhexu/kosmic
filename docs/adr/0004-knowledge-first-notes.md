# Knowledge-first notes; no separate evidence layer

Accepted through the approved `knowledge-first-notes-and-evidence-retirement` PRD, Architecture, Epic 001 and Stories 001–005. Supersedes [ADR 0002](0002-single-evidence-layer.md) by reference; that historical decision is not rewritten.

## Decision

Do not require an Evidence Pack, manifest, acceptance/review sidecar, forced pack-to-note distillation, or publication impact ledger. Verification remains required. Record each acceptance criterion's actual observation and source, the independent Standards and Spec review, and its source/scope binding in the governing work record. Checked completion publishes a receipt bound to the completed record. A missing or drifted original historical proof remains pending or invalid; retirement does not refresh or bless historical bytes.

Admit a note only when it contains reusable knowledge beyond a single task or dataset. Open with the supported current conclusion and state assumptions, limits, negative results and reproducibility links. Update an existing concept instead of duplicating it. Refine, merge, split, correct, retract or deprecate notes while preserving meaningful contrary results and repairing links. Stable promotion remains human-gated. Work without a reusable finding creates no note.

Keep data-specific metadata, units, settings, schemas, calibration and single-dataset interpretation with or near native data, even outside memnotes. A central pointer note is not mandatory. Research findings that explain a reusable result belong in notes; a bounded forward-looking research memo may still support an unresolved specification decision.

Assess skill candidacy when creating or substantively revising a note; `skill_candidate` defaults to false. `skill_resources` defaults to an empty list and records stable IDs of topics actually using the note, only through an approved publication/removal flow. Semantic changes advance the UTC `updated` instant; resource bookkeeping and checks do not. Current generated content and full source-byte pins must be regenerated together from the final source. Historical curated inputs and approvals are immutable, not current-source projections.

Optional manual or externally scheduled curation uses the interval `(last successful checkpoint, frozen run-start cutoff]` per declared scope. Preparation selects revision identities; an agent performs semantic review; finalization revalidates coverage and revisions before advancing. No model call, installed scheduler, automatic publication or automatic promotion is implied. Failed, incomplete or targeted-subset runs do not consume the full-scope interval. Ambiguous legacy dates are explicit blockers, not invented historical instants.

## Consequences

- Notes remain atomic, connected and independently useful; dataset documentation remains dataset-local.
- Real smoke verification, math/derivation checks, proposal approval, identity, scope and independent review survive unchanged except for the approved compact completion proof contract.
- Scientific `artifact_role: evidence` topics remain valid; retiring pack bureaucracy does not retire scientific evidence.
- Existing receipts, snapshots, completed records and ADR 0002 remain unchanged and validate against their original proof. Missing originals are surfaced, not reconstructed as approval.
- Legacy live-vault migration/deletion and installed skill changes require separate approved work. This cutover demonstrates transformations on bounded copies only.
