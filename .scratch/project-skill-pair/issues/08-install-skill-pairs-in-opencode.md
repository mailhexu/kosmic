# 08 — Install Skill Pairs in OpenCode

**What to build:** Expose a canonical vault-hosted Skill Pair through OpenCode's native skill discovery while preserving pair atomicity, provenance, stable names, and the Development-to-Usage relationship. Establish the reusable Install Adapter contract for subsequent agents.

**Blocked by:** 03 — Make Skill Pair publication transactional.

**Status:** done

- [x] The adapter installs or exposes both canonical skills under `{project}-usage` and `{project}-development` in an isolated OpenCode environment.
- [x] OpenCode discovers and invokes both skills by their canonical names.
- [x] Development resolves Usage after installation.
- [x] A failure while exposing either member leaves the previous installed pair unchanged.
- [x] Installed projections remain traceable to the canonical vault packages and are not treated as authoritative copies.
- [x] The adapter contract separates agent-specific discovery behavior from core projection generation.
- [x] Black-box tests use a temporary agent home and never modify the real user environment.
