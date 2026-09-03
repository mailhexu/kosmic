# Single evidence layer

Research memos and execution evidence are one concept — the Evidence Pack — in one layer (`evidence/{YYYY-MM-DD}-{slug}/` with `kind: execution | research` in the manifest), rather than two concepts (`specs/research/` for forward-looking discovery, `evidence/` for backward-looking work output). Both exist to motivate knowledge; the direction of look (before a decision vs. after work) is recorded as a kind, not a directory split. Rejected the two-concept split because the split duplicates lifecycle, exclusion rules, and linking conventions for a distinction the glossary can carry alone.

## Consequences

- `specs/research/` is absorbed; specs link Evidence Packs via the same convention notes use.
- The glossary term "Research Memo" is deleted; "Evidence Pack" covers both kinds.
