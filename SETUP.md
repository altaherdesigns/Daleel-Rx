# Daleel Rx — complete setup, start to finish

Everything in this repo is already written. This is the order to actually turn it on.
If you've done a phase already, skip it — just confirm it matches what's described.

---

## Phase 0 — Accounts you need

- [ ] A GitHub account, and this code pushed to a repo on it
      (yours: `https://github.com/altaherdesigns/Daleel-Rx`)
- [ ] A Cloudflare account — free, dash.cloudflare.com
- [ ] An Anthropic API key — console.anthropic.com → API Keys → Create Key
      (this is what pays for the daily blog post; set a monthly spend limit there)
- [ ] *(Optional)* An Unsplash API key if you want real stock photos instead of the
      generated on-brand graphics — unsplash.com/developers → New Application

---

## Phase 1 — Code on GitHub

1. Unzip the package I gave you.
2. Inside that folder:
   ```bash
   git init
   git add -A
   git commit -m "Initial site: homepage, blog, automation"
   git remote add origin https://github.com/altaherdesigns/Daleel-Rx.git
   git branch -M main
   git push -u origin main
   ```
   If the repo already has commits in it (it does, if you did this before), `git pull`
   first, or just push to a fresh empty repo instead — don't fight a conflict, start clean.

---

## Phase 2 — Turn on GitHub Pages

1. `https://github.com/altaherdesigns/Daleel-Rx/settings/pages`
2. Build and deployment → Source: **Deploy from a branch** → Branch: **main / (root)** → Save
3. Custom domain field → type `daleelrx.com` → Save
   (the `CNAME` file is already in the repo, so this should just confirm it)
4. Leave "Enforce HTTPS" alone for now — it's greyed out until DNS is ready (Phase 3)

---

## Phase 3 — Point the domain at it, via Cloudflare

1. dash.cloudflare.com → **Add a site** → `daleelrx.com` → Free plan
2. Cloudflare shows you two nameservers. Go to wherever you registered `daleelrx.com`
   and replace its nameservers with those two. Takes minutes to a few hours to activate;
   Cloudflare emails you when it's done.
3. Once active, in Cloudflare's DNS tab, add exactly these (delete any conflicting
   existing A/CNAME record on `@` or `www` first):

   | Type | Name | Content | Proxy |
   |---|---|---|---|
   | A | @ | 185.199.108.153 | DNS only |
   | A | @ | 185.199.109.153 | DNS only |
   | A | @ | 185.199.110.153 | DNS only |
   | A | @ | 185.199.111.153 | DNS only |
   | CNAME | www | `altaherdesigns.github.io` | DNS only |

4. Back on the GitHub Pages settings page, wait for **"DNS check successful"** and a
   certificate to issue (minutes, occasionally up to an hour). Then tick **Enforce HTTPS**.
5. Only now, flip those five Cloudflare records to **Proxied** (orange cloud).
6. Cloudflare → SSL/TLS → set mode to **Full (strict)**. Under Edge Certificates, turn on
   **Always Use HTTPS**.

---

## Phase 4 — Verify it's actually live

- Visit `https://daleelrx.com` — homepage loads, padlock shows.
- Visit `https://daleelrx.com/blog/` — lists the one existing post.
- Open that post — header image and content render.

---

## Phase 5 — Turn on daily auto-publishing

1. Repo → Settings → Secrets and variables → Actions → New repository secret:
   - Name: `ANTHROPIC_API_KEY` → value: your Anthropic key
   - *(Optional)* Name: `UNSPLASH_ACCESS_KEY` → value: your Unsplash key, only if you want
     real photos instead of generated graphics
2. Actions tab → **"Publish blog post"** workflow → **Run workflow** (don't wait for the
   6am schedule — trigger it manually to test).
3. Watch it run. Then check:
   - **Success** → a new commit appears, and the post is live at `/blog/` within a few
     minutes once GitHub Pages rebuilds.
   - **Blocked** → check the **Issues** tab for why (banned phrase, or a dead source link)
     — nothing goes live when this happens, by design.
4. From here it runs itself daily at 06:00 UTC (~10am Gulf time), including topping up
   its own topic list when it runs low.

---

## If something doesn't match this

Tell me exactly which numbered step you're on and what you're actually seeing (error
text, blank screen, wrong page) — don't guess past it, since the next step usually
depends on the previous one having actually worked.
