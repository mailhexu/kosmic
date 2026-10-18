---
type: Project Knowledge
title: Note writing style
status: stable
created: 2026-09-24
updated: '2026-10-18T17:42:47.416663Z'
audience: both
artifact_role: guideline
skill_candidate: false
skill_resources: []
---

# Note writing style

Project Knowledge notes and Math Derivation notes use a restricted subset of
Simplified Technical English (ASD-STE100). The goal is a note that a reader
can understand without session context.

## Rules

1. **Keep sentences short.** One fact per sentence. Aim for at most 15 words.
   Split longer sentences.
2. **Use the active voice and the present tense.** Say "the validator rejects
   the file", not "the file was found to be rejected by the validator".
3. **Use one word for one concept.** Do not alternate between near-synonyms
   (record/entry/artifact) for the same thing. If two words mean two things,
   say so once and stay consistent.
4. **Do not use idioms, metaphors, or vague quantifiers.** Replace "a bunch
   of", "some", "several", "a bit" with a number, a list, or "all".
5. **Write instructions as imperatives.** Write facts as simple statements.
   One instruction per line.
6. **Name every actor and artifact.** Replace "it", "this", "the tool", "the
   module" with the exact name. A pronoun may refer only to the noun in the
   same sentence.
7. **Expand each acronym at first use in each note.** After that, use the
   acronym.
8. **Keep paragraphs short.** At most 6 sentences. Each paragraph has one
   topic.
9. **State context explicitly.** A note must say which command, which file,
   and which version it talks about. Do not rely on "as above" or "as before".
10. **Math Derivation notes follow the same rules** in the human-owned prose
    (assumptions, units, interpretation, `## Corrections`). The machine-owned
    region is exempt.

## Not STE-compatible

Version-control history, log entries, and work records stay in their own
registers; these rules bind `notes/*.md` and `mathdocs/*.md` prose.

## Note format

Name a note by concept, question, or result. Open the note with the current
takeaway. Make the note self-contained: state assumptions, conditions,
uncertainty, supporting links, and reproducibility links. Connect the note to
related concepts and to `notes/index.md`. A note has no length cap. A note
has no confidence score. Use the ungated `sources:` links for
reproducibility; an old `evidence: []` frontmatter value stays valid.

## Lifecycle

Evolve an existing note by substance. Do not append a parallel conflict
section. Do not create a duplicate conflict note. Do not create redirect or
alias notes.

- Correct or retract: state the supported current conclusion first. Keep the
  superseded interpretation below, clearly labeled. Keep the failure
  explanation, the settings and conditions that produced it, and any negative
  findings.
- Merge two notes about one concept into one current-truth-first note.
  Choose the surviving note substantively. Differing settings, uncertainty,
  and negative findings all survive. Repair
  every incoming and `index.md` link to the surviving note. One file remains.
- Split a note with independently maintainable aspects into self-contained
  notes. Each result has its own frontmatter and links. Replace duplicated
  content with cross-references. Repair incoming and `index.md` links.
- Deprecate knowledge that no longer holds: set `status: deprecated`, keep the
  note readable in place, and link to its successor note when one exists. Do
  not create an alias or redirect-only note.
- Choose a merge survivor by substantive concept coherence — which note can
  hold the combined current truth, conditions, and negative findings most
  coherently — never by older or newer timestamp.

A newer `updated` or a higher status never resolves a conflicting claim.
Only substantive content resolves a claim. Promoting `draft` to `stable`
requires a substantive human review of the content; checks, formatting, and
timestamps never substitute for that review. Merge, split, and retraction
edits need bounded substantive content review under the existing governing
record — not an additional approval gate.

## Locality

Placement is audience-keyed, not path-keyed. Documentation that supports only
one dataset — metadata, units, run settings, schemas, calibration, and
single-dataset interpretation — stays embedded in or adjacent to that dataset
in its native data repository, including a dataset living entirely outside the
memnotes vault. No central pointer stub, per-dataset note, or registry entry
is created or required for it. No machine scanner classifies placement;
misplacement is caught only by bounded human content review. An independently
reusable insight demonstrated on a dataset — including a qualified negative or
provisional result — becomes a concept-named note with precise source and
reproducibility links. The native dataset is never flattened into Markdown,
moved, or destroyed.

## Curation metadata

Every new note emits two frontmatter fields:

    skill_candidate: false   # true only when the writer judges skill material
    skill_resources: []      # stable ids of skills that actually use this note

The writer assesses candidacy at creation and at each substantive content
update. The default is false. Candidacy never forces a skill proposal. An
explicit no-proposal outcome is valid. `skill_resources` lists only skill
topics that actually use this note. Fill it only after an approved skill
publication or removal. It is never a wish list. The two fields are
independent. Absent fields read as the defaults; legacy notes stay valid
without a rewrite.

Changing `skill_candidate` from false to true, or clearing it for a new
assessment, is a semantic change. It must bump `updated`. A
`skill_resources` sync and any check-only write never bump `updated`.

## Timestamps

`updated` accepts a legacy date `YYYY-MM-DD` or a real UTC instant
`YYYY-MM-DDTHH:MM:SS[.ffffff]Z`. Never invent a past instant. Never round a
timestamp back into a consumed interval. A date-only legacy value stays a
date; a reader that needs an exact instant resolves the note explicitly.

## Linked Concepts

- [Notation](./notation.md): one symbol, one definition — the same principle
  for symbols as this note applies to words.
- **Task 2 / Task M procedures** in the Kosmic skill enforce this style.
