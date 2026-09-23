# Adapter Byte Verification — Managed-Run Release (2026-09-16)

`check-library-installation --vault memnotes` (the Shared Skill Router is the
active distribution surface; project-local pair install is superseded):

- opencode: bytes and identity verified at ~/.config/opencode/skill/memnotes-skills
- claude-code: bytes and identity verified at ~/.claude/skills/memnotes-skills
- codex: bytes and identity verified at ~/.agents/skills/memnotes-skills
- omp: bytes and identity verified at ~/.omp/agent/skills/memnotes-skills;
  additionally reports managed Project Skill Pairs still installed for the
  **abinit** project (abinit-development, abinit-usage) — a pre-existing
  cross-project state owned by the abinit migration, out of scope for the
  kosmic managed-run release and left untouched.

Activation of a fresh session's skill inventory is inherently session-scoped
and cannot be byte-verified from a build step; the checks above prove on-disk
installation and identity only.
