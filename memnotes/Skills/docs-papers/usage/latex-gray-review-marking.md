---
type: Domain Topic
id: docs-papers/usage/latex-gray-review-marking
domain: docs-papers
audience: usage
artifact_role: guideline
status: draft
summary: Mark to-be-removed LaTeX content as gray text for review, then delete the marked spans scriptedly after approval.
triggers: [gray review text, latex remove later, mark for deletion, color gray review]
source_project: native
source_sha256: empty
aliases: [gray marking, latex review marking]
---

# LaTeX Gray Review Marking

Mark content GRAY for review first. Delete the marked spans only after the
user approves. Keep the document compiling throughout the review.

## Marking rules

1. Insert `\color{gray}  % [TO BE REMOVED - gray for review <date>:
   <description>]` after the anchor line, usually the section header. The
   header stays un-grayed.
2. Append `  % [END TO BE REMOVED: <tag>]` to the line that restores the
   color. When a kept line such as a following `\section` terminates the
   span, put the END comment on that kept line and strip it during
   deletion.
3. Floats reset color: modern LaTeX `\@floatboxreset` calls
   `\normalcolor`. Declare `\color{gray}` again as the first line inside
   every `\begin{table}` or `\begin{figure}` in the span, or the body and
   caption render black.
4. Comment out interior bare `\color{blue}` or `\color{black}` switches.
   They end the gray mid-span.
5. Convert inline `\textcolor{blue}{`, `\rev{`, `\mjv{`, and `\com{` inside
   the span to `\textcolor{gray}{`. These balanced one-argument swaps are
   safe.
6. Keep all labels. Gray content still resolves cross-references.

## Scripted deletion

Delete each span through exact anchor strings, from the start-marker line
through the END-marker line inclusive. Use a Python find/slice script with
asserts. Remove a whole appendix when 100 percent of its content is gray.
Keep section headers when live content remains, for example a kept
subsection. Collapse runs of three or more blank lines after removal. Copy
the pre-removal file to `backup/<name>_<state>_<date>.tex` first; git
history is the second recovery path.

## Verification

- Rebuild clean with `latexmk -pdf -gg`. A stale aux file from an
  interrupted run can fake brace errors. Rebuild before diagnosing the
  source.
- Confirm colors and boundaries through `pdftotext` page locations plus a
  `pdftoppm` raster with ink-fraction classification. Use vision inspection
  when available.
- After deletion, grep the log for `undefined`; every removed label must be
  unreferenced. Grep the PDF text for stale terms.
- Do not verify a push through `git push ... | tail`. The pipeline exit
  status comes from `tail` and masks failures.
