# 10 — Install Skill Pairs in Codex

**What to build:** Implement the shared Install Adapter contract for Codex so the same canonical Skill Pair is natively discoverable without changing Project Knowledge or projection semantics.

**Blocked by:** 08 — Install Skill Pairs in OpenCode.

**Status:** done

- [x] The adapter exposes both canonical skills under `{project}-usage` and `{project}-development` in an isolated Codex environment.
- [x] Codex discovers and invokes both skills by their canonical names.
- [x] Development resolves Usage after installation.
- [x] Installation is atomic and preserves the previous valid pair after failure.
- [x] Installed projections remain traceable to canonical vault packages.
- [x] Agent-specific behavior is confined to the shared Install Adapter boundary.
- [x] Black-box tests use a temporary agent home and never modify the real user environment.
