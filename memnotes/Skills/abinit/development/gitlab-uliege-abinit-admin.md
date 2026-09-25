---
type: Domain Topic
id: abinit/development/gitlab-uliege-abinit-admin
domain: abinit
audience: development
artifact_role: guideline
status: draft
summary: Admin API operations on gitlab.uliege.be for the ABINIT migration with the group token (subgroups, projects, transfers, MR and pipeline checks).
triggers: [gitlab uliege admin, ABINIT migration GitLab, create subgroup project API, project transfer namespace]
aliases: [GitLab uliege operations]
outcome: 
requires_procedures: []
governed_by: []
uses_knowledge: []
supported_by: []
supersedes: []
evidence: []
source_project: abinit
source_sha256: a4d48bf663c5762dba7df0b954179e66a9a46ba94fb67088dc0ad1d27f0a682d
---

# GitLab uliege.be Admin Operations

Perform admin API operations on gitlab.uliege.be for the ABINIT migration. Manage subgroups, projects, transfers, and merge request (MR) or pipeline checks with the group token.

## Setup

API base: `https://gitlab.uliege.be/api/v4`. Read the token from `/home/hexu/.config/abinit-migration/tokens.env`, variable `ABINIT_GITLAB_GROUP_TOKEN` (lines look like `export VAR="..."`); it is a group bot token with Owner on group `abinit` (id 17890). Run all HTTP through the ctx_execute python sandbox (urllib), not curl, and URL-quote project and group paths with `urllib.parse.quote(path, safe='')`. Helper skeleton:

```python
import json, urllib.request, urllib.parse
tok = next(l.split('=', 1)[1].strip().strip('"').strip("'")
           for l in open('/home/hexu/.config/abinit-migration/tokens.env')
           if l.strip().startswith('export') and 'ABINIT_GITLAB_GROUP_TOKEN' in l)
API = 'https://gitlab.uliege.be/api/v4'
def req(method, path, data=None):
    r = urllib.request.Request(API + path, method=method,
        data=json.dumps(data).encode() if data else None,
        headers={'PRIVATE-TOKEN': tok, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as e:
        return e.code, json.load(e)
```

## Recipes

- Subgroup: `GET /groups/<quoted-full-path>` (404 means absent), then `POST /groups {"name","path","parent_id":<parent group id>,"visibility":"private","description"}`.
- Project: `POST /projects {"name","path","namespace_id":<subgroup id>,"visibility":"private","initialize_with_readme":False,"description"}`; the response field `ssh_url_to_repo` uses host `ssh.gitlab.uliege.be`, not `gitlab.uliege.be`.
- Move a project between groups (keeps project id, issues, members): `PUT /projects/<id>/transfer?namespace=<new-subgroup-id>`; then delete the now-empty old subgroup with `DELETE /groups/<id>` (202 Accepted).
- Check MRs and pipelines (trunk path `abinit/developers/trunk/abinit`): `GET /projects/<q>/merge_requests?state=all&order_by=updated_at` and `GET /projects/<q>/merge_requests/<iid>/pipelines`. Merge requests created with this token are authored by the bot; the user prefers MRs authored as X.He and recreates them by hand, so do not open trunk MRs through the API.
- Disable CI on a reference repo: `PUT /projects/<id> {"default_branch":..., "builds_access_level":"disabled"}`.

## Gotchas

- Git over SSH uses host `ssh.gitlab.uliege.be`; `git@gitlab.uliege.be:22` times out. HTTPS and API on `gitlab.uliege.be` are unaffected.
- A fresh push makes GitLab set HEAD to the first pushed branch and create `refs/pipelines/*`; set `default_branch` explicitly afterward.
- `git fetch --dry-run` against a multi-GB repo hangs in negotiation; verify ref wiring with `git ls-remote`.
- The old server gitlab.abinit.org is DOWN (2026-09-10); nothing may be fetched from it. Frozen migration references live in `abinit/developers/migration/abinit` (id 8869).
