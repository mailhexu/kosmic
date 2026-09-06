# Task: Review

Periodically review log entries and update atomic notes.

## 1. Review Log Entries

Extract knowledge from log entries to create/update atomic notes.

### Find Log Entries to Review

```bash
# List recent log entries
ls -t {VAULT}/Projects/{TARGET}/log/ | head -5

# Find entries not yet extracted (no [Extracted] marker)
grep -L "\[Extracted\]" {VAULT}/Projects/{TARGET}/log/*.md
```

### Extract Knowledge

For each log entry:

1. **Read the log entry**:
   ```bash
   cat {VAULT}/Projects/{TARGET}/log/{TARGET}-{DATE}.md
   ```

2. **Identify**:
   - New discoveries → Create atomic notes
   - Updates needed → Update existing atomic notes
   - Conflicts → Flag for resolution

3. **Process each item**:
   - Create/update atomic note (see task_add_note.md)
   - Mark in log entry: `- [Extracted] [Note Name](../notes/note_name.md)`

### Example

Before:
```markdown
## Session 1
- Discovered that interface requires batch processing
- Found memory leak in converter
```

After:
```markdown
## Session 1
- [Extracted] [Interface Batch Processing](../notes/interface_batch_processing.md) - Discovered that interface requires batch processing
- [Extracted] [Memory Leak Converter](../notes/memory_leak_converter.md) - Found memory leak in converter
```

## 2. Review Stale Notes

Find and review notes that haven't been used recently:

```bash
# Find notes with explicit staleness or audience-specific staleness
grep -rln -E "stale_after:|usage_stale: true" "{VAULT}/Projects/{TARGET}/notes/"

# Find notes not updated recently (dynamic cutoff, e.g. last 90 days)
find "{VAULT}/Projects/{TARGET}/notes" -name "*.md" -mtime +90

# Find draft notes
grep -rln "status: draft" "{VAULT}/Projects/{TARGET}/notes/"
```

### For each stale note:

1. **Read the note**
2. **Verify**: Is the knowledge still accurate?
3. **Update**: If corrected, update content and `updated`; remove or advance `stale_after` only with evidence
4. **Deprecate**: If obsolete, move to `deprecated/` and set `status: deprecated`
5. **Trust**: Add `verified` only when the actor and timestamp are both known

## 3. Review Notation Consistency

Check that all notes use consistent notation:

```bash
# Read notation reference
cat {VAULT}/Projects/{TARGET}/notes/notation.md

# Find notes using a specific symbol
git grep "x_i" -- "{VAULT}/Projects/{TARGET}/notes/*.md"
```

### If inconsistency found:

1. **Update notation.md** with correct definition
2. **Find all affected notes**:
   ```bash
   git grep "wrong_symbol" -- "{VAULT}/Projects/{TARGET}/notes/*.md"
   ```
3. **Update all related notes**
4. **Log change in log entry**

## 4. Review the Project Skill Pair

Run the review command in `references/task_project_skills.md`.

- Resolve every Unscoped Knowledge report by explicitly reviewing its Audience Scope; until then it remains Development-only.
- Fix missing source, provenance drift, stale generated content, and broken Development-to-Usage relationships at the source note.
- Regenerate after any eligible note change, then rerun review.
- Never edit canonical or installed projection output.

## 4b. Review Evidence Packs and the Impact Ledger

**Retention (flag-only)**: list packs under `{VAULT}/Projects/{TARGET}/evidence/` that (a) are referenced by no note's `evidence:` frontmatter and (b) carry a directory date older than 3 months. Flag them in the log for distillation or explicit dismissal — never delete or archive them automatically.

**Ledger hygiene**: `impact.md` is append-only and machine-validated (`validate` fails malformed entries). Never rewrite, reorder, or delete entries. `generate` appends publication entries itself; accept/reject decisions for knowledge changes come from Task 7 review, not from this task.

Review decisions on knowledge changes (Task 7) append one entry:

```markdown
- date: {YYYY-MM-DD} | kind: decision | targets: [{note paths}] | refs: {story id} | outcome: {accepted|rejected} | reason: "{≤1 line}"
```

Skill Proposal decisions use the same fixed schema; do not add ledger fields:

```markdown
- date: {YYYY-MM-DD} | kind: decision | targets: [{skill target or proposal path}] | refs: proposal:{Project-relative proposal path}#{fingerprint} | outcome: {accepted|rejected} | reason: "{≤1 line}"
```

Before accepting a `create` or `update`, independently confirm: exact target pin, candidate isolation from canonical/installed paths, one invariant baseline/candidate scenario, resolvable execution Evidence, and no equivalent rejected fingerprint without `reconsiders` plus non-empty New Evidence. A `no_action` decision needs a reviewable reason, not fabricated behavioral output.

## 5. Review Schedule

- **Daily**: Quick scan at end of session
- **Weekly**: Review all notes from past week
- **Monthly**: Review stale notes, check notation consistency

### Session-Start Review Check

At the **start** of each session, check when the last review happened:

```bash
# Check the most recent log entry date
ls -t {VAULT}/Projects/{TARGET}/log/ | head -1

# If more than 7 days since last review, do a weekly review first
```

## 6. End-of-Session Checklist

Before finishing:
- [ ] Log entry exists for today
- [ ] Discoveries extracted to atomic notes
- [ ] Knowledge index updated
- [ ] Log has session summary
- [ ] Authoritative `notes/` OKF bundle validation passed
- [ ] Project Skill Pair review passed

## Commands Summary

```bash
# Recent log entries
ls -t {VAULT}/Projects/{TARGET}/log/ | head -5

# Unextracted entries
grep -L "\[Extracted\]" {VAULT}/Projects/{TARGET}/log/*.md

# Stale notes
git grep -E "stale_after:|usage_stale: true" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Draft notes
git grep "status: draft" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Low confidence
git grep "confidence: 0\.[0-5]" -- "{VAULT}/Projects/{TARGET}/notes/*.md"
```
