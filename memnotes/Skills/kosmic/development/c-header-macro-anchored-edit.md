---
type: Domain Topic
id: kosmic/development/c-header-macro-anchored-edit
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Edit long C headers with repeated preprocessor blocks through unique multi-line anchors, never line ranges.
triggers: [repeated define blocks, header edit, macro anchored edit, abi_common.h]
source_project: native
source_sha256: empty
aliases: [header anchored edit]
---

# C Header Macro-Anchored Edit

Long C and C++ headers hold dozens of near-identical `#define` lines inside
`#ifdef` and `#else` branches, for example ABINIT's
`shared/common/src/incs/abi_common.h`. Line-range edits mis-target inside
such files: the replacement lands on the wrong duplicate-looking line or
rewrites adjacent macro continuations, and the preprocessor structure is
silently corrupted.

## Recipe

1. Record a baseline before touching the file: `git diff` it or copy it
   aside. Recover a corrupted prior edit with `git checkout -- <file>`, not
   by patching the patch.
2. Edit through exact anchors, not line ranges, in a scripted replace:

   ```python
   s = open(p).read()
   anchor = '<unique multi-line text exactly as in file>'
   assert s.count(anchor) == 1, s.count(anchor)
   s = s.replace(anchor, replacement)
   open(p, 'w').write(s)
   ```

   Make each anchor span 2 to 4 lines, so it stays unique among repeated
   macro bodies. Apply one anchored replace per logical change and re-assert
   after each. For macro continuations, copy the backslash-newline bytes
   from the file; never retype them.
3. Verify structure before compiling: read the diff, and check that every
   `#if`, `#ifdef`, `#else`, and `#endif` still pairs. For headers consumed
   by other builds, preprocess or compile one small consumer translation
   unit instead of a full build.
4. When a scripted shell call times out mid-write, assume the file may be
   half-written. Check `git status` and `git diff`, restore the baseline,
   and retry with a smaller single anchor.

## Anti-patterns

- Never use a range PUT on a file with repeated `#define NAME(...)` blocks.
- Never trust an edit-tool success result in these files; always read the
  region back.
- Never chain two dependent range edits in one turn; the second anchor
  shifts.
