---
type: Domain Topic
id: kosmic/development/edit-tool-boundary-repair
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Recover when a line-range PUT edit mangles adjacent markdown structure or the tool warns about a boundary echo.
triggers: [boundary echo, edit mangled table, line range put, edit repair]
source_project: native
source_sha256: empty
aliases: [boundary repair]
---

# Edit Tool Boundary Repair

Use this procedure when a line-range PUT edit warns about a repaired
replacement boundary echo, or when adjacent lines such as table separators,
headings, or blank lines get dropped or duplicated after an edit.

## Procedure

1. Before a multi-line PUT on structured markdown such as tables or
   frontmatter, read the exact target line range first. Anchor to observed
   content, not memory.
2. When the tool warns about a boundary echo or reports no change, stop
   issuing retries with wider payloads. Re-read the file instead.
3. Re-read the surrounding 10 lines of the file.
4. Repair with minimal single-purpose edits: restore missing table
   separator rows, section headings, and blank-line separation between
   blocks.
5. Re-read once more and confirm the region renders correctly before other
   work continues.

## Why

A PUT replaces a line range wholesale. An off-by-one range silently
consumes or duplicates neighbor lines, and the auto-repair trims echoes but
not structural damage. Four mangling incidents occurred in one session,
across specs index tables, a research memo, and a knowledge note, before
this procedure was adopted.
