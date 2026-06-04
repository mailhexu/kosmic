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
   - Mark in log entry: `- [Extracted] [[note_name]]`

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
- [Extracted] [[interface_batch_processing]] - Discovered that interface requires batch processing
- [Extracted] [[memory_leak_converter]] - Found memory leak in converter
```

## 2. Review Stale Notes

Find and review notes that haven't been used recently:

```bash
# Find stale notes
git grep "usage_stale: true" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Find notes not validated recently
git grep "last_validated: 2025-0[12]" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Find draft notes
git grep "status: draft" -- "{VAULT}/Projects/{TARGET}/notes/*.md"
```

### For each stale note:

1. **Read the note**
2. **Verify**: Is the knowledge still accurate?
3. **Update**: If changed, update content and `last_validated`
4. **Deprecate**: If obsolete, move to `deprecated/` and set `status: deprecated`

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

## 4. Review Schedule

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

## 5. End-of-Session Checklist

Before finishing:
- [ ] Log entry exists for today
- [ ] Discoveries extracted to atomic notes
- [ ] TOC updated
- [ ] Log has session summary

## Commands Summary

```bash
# Recent log entries
ls -t {VAULT}/Projects/{TARGET}/log/ | head -5

# Unextracted entries
grep -L "\[Extracted\]" {VAULT}/Projects/{TARGET}/log/*.md

# Stale notes
git grep "usage_stale: true" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Draft notes
git grep "status: draft" -- "{VAULT}/Projects/{TARGET}/notes/*.md"

# Low confidence
git grep "confidence: 0\.[0-5]" -- "{VAULT}/Projects/{TARGET}/notes/*.md"
```
