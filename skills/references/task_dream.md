# Task D: Dream Reflection

Reflect on the previous workday across the whole vault and publish one dream record.

Choose a compatible governing record before persistent harvest scratch or dream publication; publication requires the explicitly declared vault/dreams scope and session. Reflection cannot approve implementation, broader scope, migration or installation. Preserve the existing bounded read-set contract; read-only questions do not run mutating harvest/cleanup. The bare-harvest run caller must adopt a verified context before Story-079 enforcement activation; do not claim that migration is already active.

## When to Use

- Starting the first session of a new day with prior work in the vault
- After a release, to capture what finished and what remains open

## Procedure

1. **Harvest** (deterministic; never rediscover yourself):

   ```bash
   python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py dream-harvest --vault {VAULT} [--date YYYY-MM-DD] [--timezone IANA] [--project {TARGET}]
   ```

   Read `harvest` from the printed JSON. You may read ONLY files hash-pinned in
   its `read_set` (materialized under the run) plus this procedure and the
   `dream-reflection-workflow` usage note. Never read other vault paths to
   "discover more".

2. **Reflect** (judgment): write the printed `candidate_record` path with
   frontmatter exactly `schema: kosmic.dream.candidate/1`, `type:
   dream-candidate`, `date:` matching the harvest, then the seven sections in
   order: Done, In Flight, Notes Digest, Knowledge Flags, Skill Candidates,
   Ideas, Today. Rules:

   - Done/In Flight must match `status_changes` and `open_work` evidence.
   - Deterministic Knowledge Flags come from `knowledge_checks`; a
     `possible-contradiction` is your judgment and must link both notes.
   - A Skill Candidate needs two evidence references and a proposed Task P
     scope; it stays prose — never create proposal files.
   - Ideas entries use `- {date}-{slug} — {idea} — trigger: {link} — next:
     {action} (added {date})`; write them to the printed `candidate_ideas`
     path too.
   - Links are vault-relative from `memnotes/dreams/` (`../Projects/...`);
     never link outside the vault, and never copy credentials or run handles.

3. **Publish** (deterministic):

   ```bash
   python3 {KOSMIC_SKILL_DIR}/scripts/kosmic_project_skills.py dream-publish --vault {VAULT} --handle {HANDLE} [--replace]
   ```

   `--replace` is required only after a human edited the same-date record. On
   drift/errors the run stays retryable; fix the candidate and re-publish. To
   cancel: `dream-abort --vault {VAULT} --handle {HANDLE} --reason TEXT`.

4. **Never** write anywhere outside the printed candidate paths. The CLI alone
   rebuilds the index, merges ideas, redacts, and publishes atomically.
