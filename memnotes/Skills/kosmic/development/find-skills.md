---
type: Domain Topic
id: kosmic/development/find-skills
domain: kosmic
audience: development
artifact_role: guideline
status: draft
summary: Discover and install third-party agent skills through the npx skills CLI and the skills.sh leaderboard.
triggers: [find a skill, install skill, skills cli, is there a skill for]
source_project: native
source_sha256: empty
aliases: [find-skills]
---

# Find Skills

Use this procedure when a user asks for a capability that an existing skill
may cover, or wants to extend agent capabilities.

## Recognize the request

The user may ask "how do I do X" for a common task, ask "find a skill for
X", or wish for help in a domain such as design, testing, or deployment.

## Search and install

1. Check the leaderboard at `https://skills.sh/` first. It ranks skills by
   install count and surfaces the most tested options.
2. Search the ecosystem with the skills CLI:

   ```bash
   npx skills find [query] [--owner <owner>]
   ```

3. Install a package with `npx skills add <package>`.
4. Check and apply updates with `npx skills check` and
   `npx skills update`.

## After install

Verify the skill in a fresh session of each harness. Skill registries cache
at session start. For the symlink layout and the harness-specific
verification commands, load the kosmic/development/install-agent-skill-plugin
topic.
