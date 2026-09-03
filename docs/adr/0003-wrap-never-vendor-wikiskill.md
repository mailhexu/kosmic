# Wrap, never vendor, for WikiSkill-derived machinery

Stage-2 transcript-capture adapters (from the third-party MIT `wikiskill` package) are wrapped on demand via the installed package, never vendored into this repository. Kosmic ships stdlib-only Python forever; the MIT code carries benchmark machinery (graders, score gating) Kosmic deliberately does not adopt, and vendoring would pin us to pruning that surface on every upstream change. Attribution to arXiv 2608.27454 and the pinned upstream revision is recorded in docs regardless.

## Considered Options

- Vendor the adapters/scripts into `skills/scripts/` — rejected: permanent dependency surface + pruning burden.
- Subprocess the PyPI package with a hard version pin — the chosen shape, limited to Stage 2, optional per install.
