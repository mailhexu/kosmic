---
status: done
created: 2026-09-06
updated: 2026-09-06
linked_prd: ../prd-skill-proposer.md
linked_architecture: ../architecture-skill-proposer.md
linked_stories: [../stories/story-023-installation-activation-diagnostics.md, ../stories/story-024-proposer-dogfood-release.md]
---

# Epic 13: Activation and Release

## Description

Separate installation from runtime discovery, improve generated activation descriptions, and dogfood the complete proposer loop on Kosmic itself.

## Scope

### In Scope
- Concrete generated descriptions
- Installed-byte verification and honest activation reporting
- One real fresh-context proposal through review, outcome, release, and adapter verification

### Out of Scope
- Private runtime database introspection or full skill injection

## Stories

| Story | Title | Status |
|-------|-------|--------|
| [story-023](../stories/story-023-installation-activation-diagnostics.md) | Installation and activation diagnostics | draft |
| [story-024](../stories/story-024-proposer-dogfood-release.md) | Proposer dogfood and release | draft |

## Success Criteria

- [x] Installation bytes and active-session discovery are never conflated
- [x] Generated descriptions carry concrete task triggers
- [x] Real proposal outcome is reviewed, recorded, published if accepted, and installed
