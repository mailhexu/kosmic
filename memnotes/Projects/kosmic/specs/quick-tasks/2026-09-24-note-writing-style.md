---
status: done
created: 2026-09-24
updated: 2026-09-24
related_notes: [notes/note-writing-style.md]
related_specs: []
related_files: [skills/references/task_add_note.md, skills/references/task_math_note.md]
consumer_interface_change: false
proposal_required: false
routine_edge_change: false
routine_decision_required: false
routine_proposals: []
review_base: ""
review_round: 0
---

# Quick Task: Note writing style

## Request

Notes read as broken, context-dependent language. Adopt a Simplified Technical
English (ASD-STE100) subset as the writing style for Project Knowledge notes
and SymPy Math Derivation notes.

## Scope

- New stable guideline note `notes/note-writing-style.md` (10 operational rules).
- Task 2 (`task_add_note.md`) and Task M (`task_math_note.md`) enforce the
  style; machine-owned math regions are exempt.

## Verification

- `generate` + `validate --project` green after the note entered the bundle.

## Outcome

Implemented 2026-09-24.
