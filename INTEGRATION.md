# Daleel Rx site update — 28 September 2026

Drop-in changes for the `altaherdesigns/Daleel-Rx` Jekyll repo (GitHub Pages).
Claude will apply these directly once the repo is attached to the session; this file is the manual route.

## New files

| Path | What it is |
|---|---|
| `index.html` | New homepage. Launch-list signup and a **Try it now** demo. Self-contained (`layout: null`). |
| `_includes/home-styles.html` | Homepage styles (light and dark). |
| `_includes/home-script.html` | Signup handling and the demo logic. |
| `_includes/demo-data.html` | 15 real products from the 5 Sep 2026 snapshot. No prices, no registration numbers. Pregnancy and breastfeeding only where the product value matches the verified overlay. |
| `_includes/article-schema.html` | Article + MedicalWebPage + Person + BreadcrumbList JSON-LD for posts. |
| `_includes/byline.html` | "By Muaaz Butt, Licensed Pharmacist…" with published and last-reviewed dates. |
| `about.md` | About page, the author entity that the schema and bylines point to. |
| `_posts/2026-09-28-*.md` | Five new articles, fully cited. |

## Edits to existing files

### `_config.yml`

```yaml
url: "https://daleelrx.com"
signup_action: ""   # set to the existing form endpoint (whatever /thanks/ is wired to today)

exclude:
  - SETUP.md
  - SETUP
  - docs
  - INTEGRATION.md
  - README.md

defaults:
  - scope: { path: "", type: posts }
    values:
      layout: post
      author: "Muaaz Butt"
      author_credentials: "Licensed Pharmacist, MOH Northern Emirates and DHA Dubai"
```

`exclude` removes `/SETUP/` and `/docs/blog-topics/` from the public site and the sitemap. Both are live and indexed today.

### `thanks` page front matter

```yaml
sitemap: false
```

and add `<meta name="robots" content="noindex">` to its head.

### `_layouts/post.html`

- Inside `<head>`: `{% include article-schema.html %}`
- Directly under the post `<h1>`: `{% include byline.html %}`
- Make sure the root element is `<html lang="en">`.

### Existing six posts

Add `last_modified_at:` when they are next reviewed. The defaults above give them the byline automatically.

## Technical SEO findings on the live site (28 Sep 2026)

1. **Critical** — `/SETUP/` and `/docs/blog-topics/` are public and in the sitemap. Fixed by `exclude`.
2. **High** — no Article or Person structured data on any post. Fixed by `article-schema.html`.
3. **High** — no author byline on posts; the licence only appears as a "Reviewed by" line on some. Fixed by `byline.html` and `about.md`.
4. **High** — homepage meta description promises "registered pricing". The dataset is not being published; the new homepage copy removes the claim.
5. **Medium** — `/thanks/` is in the sitemap. Fixed by `sitemap: false` + noindex.
6. **Medium** — `og:image` for posts is SVG, which Facebook, LinkedIn, WhatsApp and X do not render. Replace with 1200×630 PNGs.
7. **Medium** — no `dateModified` on posts. Fixed via `last_modified_at` and the schema include.
8. **Low** — GitHub Pages cannot set security headers (HSTS, CSP). Add them in Cloudflare with a Transform Rule if wanted.
