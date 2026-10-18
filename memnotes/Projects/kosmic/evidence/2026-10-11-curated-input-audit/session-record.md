# Curated proposal input audit correction

Recursive authoritative specs discovery incorrectly included manifests and copied templates under specs/skill-proposals/inputs/. A copied template containing placeholder flow YAML caused SPEC_INVALID before the planner could complete.

The existing protected-root inventory now includes the entire proposal inputs tree. Authoritative inbound discovery excludes it; the existing protected scan hashes its Markdown inputs and reports references or nonparseable frontmatter with protected=true. It never rewrites copied inputs, invalidates their hashes, or loosens the YAML parser.

One behavioral regression failed before the correction, then proved hash pinning, protected moved-reference/unparsable-document reports, no snapshot outputs, byte preservation after staged application, and continued authoritative note-link rewriting. The integrated focused run passed 75 tests. Actual CLI fixture verified protected-template reporting. The read-only canonical planner exited 0 with 112 records, 155 rewrites, 467 link corrections, 86 link problems and zero ambiguities on that snapshot.

Source changes were made in an isolated clean worktree under approved Story kosmic/deterministic-flat-spec-migration/story/001, then integrated through original-source hash guards. The bounded change was manually reviewed against the protected inventory and publication contracts; it does not claim a new independent approval, reset the existing three-round review ledger, or mark the Story done. No live migration, installed skill mutation or input snapshot edits occurred. Plan counts/digest are historical observations, not application authority, and must be regenerated after later Project documentation changes.
