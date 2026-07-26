# 01 — Generate a minimal atomic Skill Pair

**What to build:** Given a Project with an explicit Project Identifier and validated Contributor and Consumer knowledge, provide a Projection CLI command that generates exactly one Usage Skill and one Development Skill as router-plus-reference packages. The Development Skill must resolve its paired Usage Skill.

**Blocked by:** None — can start immediately.

**Status:** done

- [x] A Project with one validated `usage` note and one validated `development` note generates exactly `{project}-usage` and `{project}-development`.
- [x] Each generated skill has an invocable Skill Router and at least one usable topic reference.
- [x] The Development Skill explicitly resolves the generated Usage Skill by its canonical name.
- [x] Invalid or missing Project Identifiers fail with actionable diagnostics and no published output.
- [x] A black-box CLI test verifies generated package names, router behavior, references, and the Development-to-Usage relationship.
