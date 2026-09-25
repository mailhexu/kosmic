---
type: Domain Topic
id: kosmic/development/install-agent-skill-plugin
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Install third-party skills or MCP plugins into both omp and opencode on this workstation, with registry refresh and live verification.
triggers: [install skill, omp plugin, opencode plugin, mcp install]
source_project: native
source_sha256: empty
aliases: [skill install, plugin install]
---

# Install Skills and Plugins into omp + opencode

## Skills in SKILL.md format

1. Download the skill into `~/projects/myagentskills/<name>/`. That
   directory is the single source of truth; both harnesses symlink into it.
2. Link it into both harnesses:

   ```bash
   ln -sfn ~/projects/myagentskills/<name> ~/.omp/agent/skills/<name>
   ln -sfn ~/projects/myagentskills/<name> ~/.config/opencode/skill/<name>
   ```

   opencode's live directory is `skill/`, not `skills/`.
3. Verify in fresh sessions; registries cache at session start. For omp,
   run `omp -p --no-session --model smol "Read skill://<name> and reply
   with its name field"`. For opencode, run
   `opencode run "Do you have a skill named '<name>'?"`.

## MCP servers and plugins

- **omp**: run `omp plugin install <npm-pkg>`. The plugin self-registers
  its MCP server under `~/.omp/agent/mcp.json` on first load. Verify with
  `omp plugin list` and one live tool call in a fresh headless session.
- **opencode**: run `bun add <pkg>` in `~/.config/opencode`, then add the
  package to the `plugin` array in `opencode.jsonc`. Both `opencode.json`
  and `opencode.jsonc` load and merge; check `opencode debug config` for
  the resolved result. Plugins run in-process under the Bun runtime.

## Native-module pitfalls on this machine

- Only Node 20.12.2 exists, through nvm, with no node-gyp. Bun cannot load
  `better-sqlite3` through dlopen. Under Bun, a package must use its own
  `bun:sqlite` adapter.
- `better-sqlite3` 12.7 and later ship no Node ABI v115 prebuild; the
  install falls to node-gyp and exits 127. Pin
  `"better-sqlite3": "12.6.2"` in the install root's package.json
  `overrides`.
- Diagnose prebuild 404s with
  `npm exec prebuild-install -- -r node -t <ver> --verbose`; it prints the
  exact asset URL it tried.

## Verification rule

Always end-to-end verify in a fresh headless session of each harness.
Mid-session registries and MCP tables are stale.
