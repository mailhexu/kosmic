---
type: Domain Topic
id: docs-papers/usage/markdown-latex-render-validation
domain: docs-papers
audience: usage
artifact_role: guideline
status: draft
summary: Format and validate Markdown reports that contain MathJax or LaTeX equations, tables, and numbered sections.
triggers: [markdown math validation, mathjax check, display fence pairs, pandoc math render]
source_project: native
source_sha256: empty
aliases: [markdown latex qa]
---

# Markdown + LaTeX Render Validation

Run this check after editing a technical Markdown report with mathematics.

## Formatting rules

- Write inline math as `$...$`.
- Write display math as: blank line, `$$`, formula, `$$`, blank line.
- Write bra-ket notation with `\lvert`, `\rangle`, `\langle`, `\rvert`,
  and `\mid`. Avoid a raw `|` inside Markdown tables.
- Put identifiers in backticks. Use `\mathrm{...}` only when an identifier
  must sit inside a formula.
- Replace raw Unicode math glyphs with LaTeX for PDF output.
- Put long equations in display blocks, not inline spans.
- A display block inside an ordered-list item can end the list. Prefer
  explicit numbered subsections for equation-heavy material.

## Structural checks

Verify programmatically:

1. Expected numbered headings, equation tags, references, and validation
   rows exist.
2. `$$` fences form ordered pairs, each `\tag{N}` sits inside exactly one
   pair, and each fence has blank-line separation on both sides.
5. Each non-display line holds an even count of unescaped `$` delimiters.
6. Each contiguous table keeps a constant pipe count per row.
7. Source links and local `path:line` targets still resolve.

Global `$$` parity is not sufficient. Deleting the opening fence from an
even number of equations still passes it.

## Render checks

Render both targets when the tools exist:

```bash
pandoc --from=gfm+tex_math_dollars --to=html5 --standalone --mathjax \
  --metadata title="Report title" report.md -o .tmp/report.html

pandoc --from=gfm+tex_math_dollars --standalone --pdf-engine=xelatex \
  --metadata title="Report title" report.md -o .tmp/report.pdf
```

Inspect headings, lists around display equations, and table column
counts. Treat missing-glyph warnings as defects; delete render artifacts
after validation.
