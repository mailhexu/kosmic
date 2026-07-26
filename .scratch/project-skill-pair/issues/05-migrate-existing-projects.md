# 05 — Migrate existing Projects conservatively

**What to build:** Provide a restartable migration that gives an existing vault Project immutable identity and projection support without exposing Unscoped Knowledge, overwriting another Project, or damaging authoritative notes.

**Blocked by:** 03 — Make Skill Pair publication transactional.

**Status:** done

- [x] Migration assigns or validates an explicit immutable Project Identifier before generating skills.
- [x] Identifier collisions are reported before canonical or installed output is changed.
- [x] Existing notes without Audience Scope remain Development-only until explicitly reviewed.
- [x] Migration reports the notes requiring audience classification and the Consumer knowledge needed for publication.
- [x] Interrupted or repeated migration is non-destructive and converges to the same result.
- [x] A valid prior pair remains available when migration cannot produce a valid replacement.
- [x] After reviewed Usage knowledge exists, rerunning migration publishes a valid atomic Skill Pair.
