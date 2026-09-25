---
type: Domain Topic
id: docs-papers/usage/github-org-profile-logo
domain: docs-papers
audience: usage
artifact_role: guideline
status: draft
summary: Add an image to a GitHub organization profile README after checking asset provenance and repository write access.
triggers: [org profile readme, org logo, profile image, github .github repo]
source_project: native
source_sha256: empty
aliases: [org profile logo]
---

# GitHub Organization Profile Logo

1. The organization profile README lives at
   `<ORG>/.github/profile/README.md` in the organization `.github`
   repository. Read the current README and inspect the repository contents
   before editing. Preserve the existing content and style.
2. Confirm an authorized logo asset exists. Add the asset to the profile
   folder or use a stable approved hosted asset, and reference it with a
   relative repository path.
3. Convert a PDF source to a README-renderable raster such as PNG. PDF is
   not a reliable inline README image format. Use an HTML `<img>` element
   with an explicit width when the natural raster size would dominate the
   profile.
4. Verify that the image loads and renders at the intended size in a
   preview. After a remote update, verify the organization overview when
   access permits. If only a local commit is requested, do not push, and
   state that the remote profile remains unchanged until pushed.
5. When GitHub access is logged out or write permission is missing, do not
   claim completion. Provide the exact README location, sample Markdown,
   and the required access.
