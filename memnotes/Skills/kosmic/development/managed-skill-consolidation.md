---
type: Domain Topic
id: kosmic/development/managed-skill-consolidation
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Consolidate OMP managed skills into the kosmic vault through a triage table, parallel distillation, index assembly, and retirement.
triggers: [managed skill consolidation, distill managed skills, skill triage, retire managed skills]
source_project: native
source_sha256: empty
aliases: [consolidation campaign]
---

# Managed-Skill Consolidation

Unify OMP managed skills at `~/.omp/agent/managed-skills/` with the kosmic
vault, so the vault becomes the single authority. The procedure fits phase
2 and later campaigns.

## Procedure

1. **Inventory.** Dump each managed skill's name and frontmatter
   description.
2. **Triage table.** Give each skill one verdict, and get user approval
   before anything moves: Distill into project notes, Merge a cluster into
   one note, promote to a Library topic in `memnotes/Skills/<domain>/` for
   cross-project reuse, or Drop as a one-off recorded only in the project
   log. Check overlap against existing notes and topics with grep first.
3. **Parallel distillation.** Fan out `task` subagents, about eight skills
   each. Each brief pins: read-only source paths, target note paths with
   slug, the frontmatter template copied from an existing note, a mandatory
   read of `memnotes/Projects/kosmic/notes/note-writing-style.md`, a line
   budget, and two prohibitions: never edit a generated `index.md`, and
   never delete managed skills.
4. **Assemble.** Append all returned index lines yourself under a dated
   heading. Parallel agents must not edit the shared index.
5. **Library topics.** Copy an existing Domain Topic frontmatter exactly.
   `observed_on:` is valid only for `artifact_role: evidence`; strip it
   from guideline topics or validate-library fails.
6. **Regenerate and validate.** Run `generate-library` and
   `validate-library` with `--vault memnotes`, then `generate` and
   `validate` with `--project <project>`. Regenerate the library after
   every frontmatter fix; catalog drift reports STALE_LIBRARY otherwise.
7. **Retire.** Delete the consolidated managed directories with
   `shutil.rmtree`. `managed-skills` is the agent-writable surface; never
   touch `~/.omp/agent/skills`.
8. **Close.** Record a quick task with status done, write the project log
   entry with any drops, run the test suite, reinstall the router on all
   four adapters (omp, opencode, claude-code, codex), and make one vault
   commit per batch.

## Known traps

- The library index is generated. Never hand-edit
  `memnotes/Skills/<domain>/index.md`.
- Notes stay `status: draft`. Promotion to stable is the human's Task 4
  gate.
- Name-variant duplicates may exist in `managed-skills`. Count directories
  before and after retirement.
- The OMP session keeps listing retired skills until restart.
