---
type: Domain Topic
id: docs-papers/usage/hugo-html-components
domain: docs-papers
audience: usage
artifact_role: guideline
status: draft
summary: Hugo content components must be shortcodes, and subpath figure URLs must strip the leading slash before resolution.
triggers: [hugo html stripped, gallery cards missing, figure 404 subpath, goldmark unsafe]
source_project: native
source_sha256: empty
aliases: [hugo shortcodes, hugo figure subpath]
---

# Hugo HTML Components and Subpath Figures

This topic covers a Hugo site that uses the goldmark renderer and deploys
to GitHub project Pages under a subpath such as `/repo/`.

## Symptom

Goldmark strips raw HTML in content because
`markup.goldmark.renderer.unsafe` defaults to `false`. Markdown and `{{<
shortcode >}}` calls inside stripped tags still render, so the page shows
unstyled content. A local build stays green; the defect appears only in
the deployed HTML.

## Rule: components are shortcodes

1. Put each styled component in a shortcode, for example
   `layouts/shortcodes/card.html`. Shortcode output is final HTML and
   never passes through goldmark.
2. Wrap components in a container shortcode pair, for example `{{< gallery
   >}} ... {{< /gallery >}}`, whose template emits the wrapper `<div>`
   around `{{ .Inner }}`.
3. Put component CSS in `layouts/partials/custom-header.html`. An inline
   `<style>` block in content is also stripped.

## Rule: subpath-safe URLs

Hugo emits a shortcode `src` verbatim. A leading `/` means the host root,
so `src="/images/x.png"` misses the `/repo/` prefix. For inputs that start
with `/`, both `absURL` and `relURL` keep the URL at the host root
(verified on Hugo 0.131). Only slash-free inputs resolve against the
baseURL path. Content markdown keeps `src="/images/..."`; resolution
happens at build time. Override the built-in `figure.html` and `file.html`
shortcodes with `strings.TrimPrefix "/"` before `absURL`:

```
{{- $src := .Get "src" | strings.TrimPrefix "/" | absURL -}}
```

## Verification

1. Build with the production baseURL and no override. Check the built
   HTML: count component-class occurrences; assert `src="/images/` count
   is zero.
2. Assert every `href` and `src` maps to a file in the build output.
3. Deploy. In a browser, assert each image satisfies `img.complete &&
   img.naturalWidth > 0` and navigation works.
4. Verify against the latest workflow run sha: `concurrency: cancel-in-
   progress` cancels an in-flight deploy for a newer commit.
