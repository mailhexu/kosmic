# 04 — Initialize new Projects with a publishable Skill Pair

**What to build:** Extend Kosmic initialization so a new Project receives immutable identity, real Contributor and Consumer knowledge, a canonical atomic Skill Pair, and enough integration metadata for later refresh and installation.

**Blocked by:** 03 — Make Skill Pair publication transactional.

**Status:** done

- [x] Initialization assigns and records an explicit immutable, collision-resistant Project Identifier.
- [x] Initialization identifies at least one real Consumer Interface and captures validated Consumer guidance rather than generating an empty placeholder.
- [x] Initialization captures enough validated Contributor knowledge to produce a useful Development Skill.
- [x] The canonical Skill Pair is generated transactionally before initialization reports success.
- [x] Initialization records canonical skill names, vault location, and adapter configuration for later sessions.
- [x] If useful Usage cannot be produced, initialization reports the missing prerequisite and leaves no partial pair.
