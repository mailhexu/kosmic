---
name: memnotes-skills
description: Resolve and load bounded procedures from the Memnotes Shared Skill Library.
---

# Memnotes Shared Skills

Use this router for maintained technical procedures. Do not scan the vault or load every domain.

1. Run `python3 "/home/hexu/projects/myagentskills/kosmic/skills/scripts/kosmic_project_skills.py" resolve-library --vault "/home/hexu/projects/myagentskills/kosmic/memnotes"` with exactly one query or route and the task role.
2. Inspect ambiguity, exclusions, dependencies, and byte cost in the returned plan; save the unchanged JSON.
3. Run `python3 "/home/hexu/projects/myagentskills/kosmic/skills/scripts/kosmic_project_skills.py" load-library --vault "/home/hexu/projects/myagentskills/kosmic/memnotes" --plan PLAN.json`.
4. Follow the emitted Domain Skill and topic packet. Never omit required dependencies or silently truncate a topic.

Library budget policy: 32768 packet bytes, 4 domains, 8 topics; requests are clamped to these maxima.
Authoritative library: `/home/hexu/projects/myagentskills/kosmic/memnotes/Skills`
Manifest SHA-256 at publication: `a4bfb88ff792b164152c8f7675f3d72d697a779f2d1369f64dd5525aad602dcc`
Failure is closed: stale hashes, ambiguity, missing dependencies, cycles, and budget overflow return no recipe bodies.
