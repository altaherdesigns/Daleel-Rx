# daleelrx.com — SEO landing page

Single static page, centered layout, no framework, no dependencies beyond two Google Fonts.
Built to hold the domain and start SEO now, with app store links to be added once the app
ships.

## Before you flip this to indexable / live

1. **`<meta name="robots" content="noindex, nofollow">` is deliberately still on.** Per your
   own Phase 0 tracker: *"Nothing may be published on it while G1b is open."* P0-29 (Ehsaan's
   written scope, specifically covering public display) is the tracker's stated
   "critical path for any public launch." This page makes no product or data claim, so the
   exposure is low — but confirm P0-29 has actually cleared, or that you're knowingly
   proceeding without it, before removing this line.
2. To go live once decided: delete the `noindex, nofollow` line, keep `index, follow`
   behaviour (i.e. just remove the meta tag), then connect the custom domain in
   GitHub Pages settings.
3. **Contact email** is `daleelrxapp@gmail.com` (per P0-9b, the account in use). Swap to
   `muaaz@daleelrx.com` once P0-9c is set up.

## What's deliberately not on the page

- No CME, sponsorship, or B2B language — no such model exists (D31).
- No claim about where data comes from, or that it's live/complete — rights unresolved (P0-29).
- No screenshots, no pricing, no "trusted by" — nothing to walk back later.
- App Store / Google Play badges are a text placeholder, not real links, until the app ships.

## SEO notes

- Title + meta description target "UAE medicine reference" / "pharmacists" naturally, no
  keyword stuffing.
- Open Graph tags set for clean link previews when shared.
- Minimal `WebSite` JSON-LD — safe, makes no factual claim beyond the site's existence.
- Page is intentionally light (no images, two font weights) for fast load, which itself
  helps ranking.

## To push it yourself

```bash
cd daleelrx-site
git add -A
git commit -m "SEO landing page: simplified, centered, launch-ready"
git remote add origin https://github.com/<your-username>/daleelrx-site.git
git branch -M main
git push -u origin main
```

Enable GitHub Pages under `Settings → Pages`, custom domain `daleelrx.com`, only once you've
confirmed the P0-29 point above.
