---
project_id: "kosmic"
subproject_id: null
status: "approved"
record_kind: "quick-task"
local_id: "preserve-missing-mathdoc-knowledge-as-drafts"
approval_note: User selected Preserve as draft knowledge for unavailable legacy derivations.
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: "f4e7feabbf067ed93043cafa19aeabc557a9d060"
review_round: 0
acceptance_evidence: [evidence/2026-10-13-missing-mathdoc-drafts/acceptance.json]
review_record: evidence/2026-10-13-missing-mathdoc-drafts/review.json
---

# Preserve missing MathDoc knowledge as drafts

## Scope

Preserve equations and original note bodies in the shared vault. Change only affected stable notes with missing MathDoc provenance to draft and explain the missing verification in frontmatter. Verified notes and their registered derivations remain strict and unchanged. Existing unpaired executable derivations may receive truthful draft companions recording that they have not been verified; no source script, verification fields or generated result regions may be invented.

Continue compatible, record-authorized projection hygiene; do not migrate records under new unapproved digests or change validators. Use baseline-checked note changes and retain per-file before/after evidence.

## Acceptance Criteria

- [ ] Every changed knowledge note retains its original body and equations byte-for-byte.
- [ ] Notes lacking mathematical provenance remain accessible as drafts and are excluded from projections.
- [ ] No verified derivation or verification marker is invented or weakened.
- [ ] Reachable projection checks pass or identify concrete independent prerequisites.
