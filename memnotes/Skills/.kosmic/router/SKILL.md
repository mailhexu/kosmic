---
name: memnotes-skills
description: Resolve and load bounded role-aware packets from the Memnotes Shared Skill Library.
---

# Memnotes Shared Skills

Use this router for maintained procedures, governing guidelines, reference knowledge, and dated evidence. Do not scan the vault or load every domain.

1. Run `python3 "/home/hexu/projects/myagentskills/kosmic/skills/scripts/kosmic_project_skills.py" resolve-library --vault "/home/hexu/projects/myagentskills/kosmic/memnotes"` with exactly one query or route, the audience role, and optional `--intent do|check|understand|investigate`.
2. Inspect the inferred intent, primary topic, typed closure, exclusions, and exact byte cost; save the unchanged JSON plan.
3. Run `python3 "/home/hexu/projects/myagentskills/kosmic/skills/scripts/kosmic_project_skills.py" load-library --vault "/home/hexu/projects/myagentskills/kosmic/memnotes" --plan PLAN.json`.
4. Execute only a `procedure` selected for `do`; treat guidelines as constraints, knowledge as reference, and evidence as historical support.

Library budget policy: 32768 packet bytes, 4 domains, 8 topics; requests are clamped to these maxima.
Authoritative library: `/home/hexu/projects/myagentskills/kosmic/memnotes/Skills`
Manifest SHA-256 at publication: `a73328773419a4c28c50e1800305a0d3da30de0ce54c8e14b352dc0c1ebabdc5`
Failure is closed: stale hashes, ambiguity, missing dependencies, cycles, and budget overflow return no recipe bodies.
