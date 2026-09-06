---
type: Shared Skill Router
id: memnotes-skills
status: stable
description: Route technical tasks to bounded, maintained domain procedures.
max_packet_bytes: 32768
max_domains: 4
max_topics: 8
---

# Memnotes Shared Skill Library

Resolve one bounded Recipe Packet. Use an exact route when known; otherwise query deterministically. Load only the returned Domain Skills and topics. Stop on ambiguity, stale hashes, broken dependencies, or budget failure.
