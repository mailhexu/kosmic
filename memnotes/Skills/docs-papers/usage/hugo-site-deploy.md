---
type: Domain Topic
id: docs-papers/usage/hugo-site-deploy
domain: docs-papers
audience: usage
artifact_role: guideline
status: draft
summary: Scaffold a Hugo Techdoc documentation site in a package repository and deploy it to GitHub project Pages.
triggers: [techdoc site, docs github pages, hugo sidebar menu empty, partial head.html not found]
source_project: native
source_sha256: empty
aliases: [techdoc deploy, hugo pages workflow]
---

# Hugo Techdoc Site on GitHub Project Pages

## Scaffold

1. Put the site root in `docs/`. Add the theme as a git submodule at
   `https://github.com/thingsym/hugo-theme-techdoc`.
2. Theme v1.1.0 needs Hugo 0.146+; Hugo 0.131 fails with `partial
   "head.html" not found`. Pin `peaceiris/action-hugo` 0.146+.
3. Set `baseURL = "https://user.github.io/repo/"` with the trailing slash.

## Sidebar menu

`_partials/menu/open-menu.html` iterates `.Site.Home.Sections`; flat
`content/foo.md` pages never appear. Use `content/docs/*.md` pages with a
`weight`, plus `content/docs/_index.md` for the section entry.

## Subpath hardening

- Add `layouts/_default/_markup/render-link.html`; resolve `*.md`
  destinations through `$.Page.GetPage $u` to `.RelPermalink`.
- Override the `figure` and `file` shortcodes to trim the leading `/`
  before `absURL`.
- Publish extra directories through `staticDir`; set `github_doc_repository`
  (trailing slash) plus `_branch` and `_path` params.

## Math and code highlighting

Techdoc has no math support; add MathJax 3 through the
`layouts/_partials/custom-head.html` override. Use class-based Chroma:
`pygmentsCodeFences = true`, `pygmentsUseClasses = true`,
`[markup.highlight] noClasses = false`.

## Deploy workflow

`.github/workflows/docs-pages.yml` chains checkout with `submodules:
recursive`, `peaceiris/action-hugo@v3`, `hugo --source docs --minify`,
`configure-pages@v5`, `upload-pages-artifact@v3` (path `docs/public`), and
`deploy-pages@v4`. Grant `pages: write` and `id-token: write`; trigger on
`main` pushes touching `docs/**`; set the Pages source to GitHub Actions;
gitignore `docs/public/`, `docs/.hugo_build.lock`, `docs/resources/`.

## Verification

Build with the production baseURL and no override. Assert zero root-
absolute `href` or `src` references and that every internal href maps to
an output file (grep `href=[^ >]+`; minification drops quotes). Serve
locally; check the menu, `mjx-container`, and a clean console.
