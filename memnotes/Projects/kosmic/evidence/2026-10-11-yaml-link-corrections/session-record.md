# YAML and internal-link corrections — 2026-10-11

Scope: follow-on correction to approved Story 001. User chose authoritative source Markdown only; evidence, logs and generated skills are audited/report-only during migration. Source integrated through captured-input hash guards. No live Project migration, adapter installation or lifecycle approval occurred.

## Observed behavior

- Original nested source-title parsing failed with a duplicate-title error; structured stdlib YAML parsing now isolates mapping keys, supports nested block/flow collections and rejects malformed/unsupported constructs through typed errors.
- Actual temporary-Project CLI plan/apply resolves local YAML URLs and plain/encoded/queried/titled Markdown destinations, preserves external references and query/fragment/title components, repairs a MathDoc wrong-directory reference by unique moved filename, and leaves historical evidence bytes identical.
- Actual CLI resolves quoted JSON flow keys and multiline flow-map URL values while preserving an identical non-link title. Valid encoded URLs in staying files remain byte-identical.
- Ambiguous filename matches block application. A resolved scalar that cannot be surgically placed produces an explicit unsupported-link-rewrite problem and apply blocker rather than losing its diagnostic.
- Final focused run: 74 tests passed. Final integrated complete runner: 17 modules in 86.0 seconds; zero failed. Integrated repository CLI smoke passed.

## Review

Independent Standards and Spec review ran three rounds against private-snapshot baseline 6e7b8bff170cff979015ef85899aad42b4714d8a. Earlier findings resolved; round3 identified quoted flow keys and multiline flow contexts (STD-YL-10, STD-YL-11, SPEC-YL-6). Their final changes were manually inspected and exercised after the automated review cap. The independent round3 verdict remains changes-requested in the ledger; no subsequent independent approval is fabricated.

## Canonical Project boundary

The read-only current Project planner exits with SPEC_INVALID at notes/cli-extension-conventions.md: updated: '2026-09-02' (promoted) has unexpected content following a quoted scalar. This pre-existing malformed authoritative header prevents a complete canonical-Project audit. It was not silently accepted or edited under the link-correction scope. Source behavior is verified in actual temporary fixtures; no claim of live Project correction or migration is made. Existing Story terminal closure remains pending separately approved migration and checked completion.
