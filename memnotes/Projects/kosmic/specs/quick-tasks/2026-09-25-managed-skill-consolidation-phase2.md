---
status: "done"
created: "2026-09-25"
updated: "2026-09-25"
related_notes: ["notes/dream-reflection-workflow.md"]
related_specs: []
related_files: []
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
project_id: "kosmic"
subproject_id: null
record_kind: "quick-task"
local_id: "2026-09-25-managed-skill-consolidation-phase2"
---

# Quick Task: Managed-skill consolidation (phase 2, all domains)

## Request

Consolidate the remaining 103 managed OMP skills into the Shared Skill
Library. Phase 1 (49 abinit skills -> Project notes) completed earlier today.

## Approved triage

- G1: 8 duplicate name-variants retired (already distilled in phase 1)
- G2: new domain `siesta` (19 -> ~12 topics)
- G3: new domain `lawaf` (6 -> 4)
- G4: new domain `fourstate` (3 -> 2)
- G5: existing `tb2j` domain (6 -> 5)
- G6: existing `abinit` domain (10 -> 10)
- G7: new domain `methods` (12 -> 11)
- G8: new domain `workstation` (13 -> 10)
- G9: new domain `docs-papers` (7 -> 5)
- G10: agent tooling -> `Skills/kosmic` domain topics (option a, user choice)

Books: 103 managed skills -> ~62 library topics; all managed copies retired.

## Verification

- `generate-library` + `validate-library` green with the new domains.
- Router reinstalled and byte-verified on all four adapters.
- Full suite green; vault committed.

## Outcome

Done 2026-09-25: 103 managed skills -> 55 new library topics across six domains (siesta, lawaf, fourstate, methods, workstation, docs-papers new; tb2j, abinit, kosmic extended) + 8 duplicate retirements; managed-skills directory emptied (swmgr symlink removed, target untouched); library regenerated and validated; router verified on four adapters.
