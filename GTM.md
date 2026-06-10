# Ghosted — Go-To-Market Strategy

> A free, local-first Instagram story & follower tool. Monetized by **donations**,
> not subscriptions. Distributed as a **desktop download**, not a hosted service.

## 0. The model (why this shape)

- **Tool runs locally** on each user's machine — their IP, their session, their
  password never leaves their device. This is the *only* model that (a) works
  (no shared-server IP bans) and (b) avoids credential/legal liability.
- **Marketing site is hosted** (Vercel/Netlify) for SEO, downloads, and donations.
- **Free + donation**, not paid — lowers payment-processor and legal exposure.

Everything below follows from this. Do not build a hosted multi-tenant version
that collects users' Instagram logins; it bans your users and exposes you.

## 1. Positioning

**One-liner:** "Hide your Instagram story from everyone — in one click."

**Who it's for:** people who want story privacy from large parts of their follower
list, and who want to clean up who they follow. The native app only lets you do
this one person at a time; that gap is the wedge.

**Honest framing (also the legally safest):**
"Free tool. Runs on your computer. Your password never leaves your device.
Use at your own risk — automation can violate Instagram's terms."

## 2. The wedge: SEO

There is real, steady search demand for the core job. Target these intents with
the content pages already built (`/faq`, `/about`) plus blog posts:

- "how to hide instagram story from everyone"
- "hide instagram story from all followers at once"
- "unhide instagram story from everyone"
- "who doesn't follow me back on instagram"
- "bulk unfollow instagram"

**Actions**
- Each query → a dedicated, genuinely useful page (how-to + screenshots + the
  download CTA). The native-app limitation is the hook; the tool is the payoff.
- Ship `sitemap.xml` (done), clean titles/meta (done), fast static pages (done).
- Earn backlinks: answer the same questions on Reddit/Quora and link the guide.

This is the cheapest, most durable channel because **you cannot run paid Meta
ads** for this (they reject + flag IG-automation tools).

## 3. Channels (ranked)

1. **SEO / content** — primary. Owns the demand, compounds over time.
2. **Reddit / Quora / forums** — answer the exact questions, link the guide. No spam.
3. **Word of mouth** — the "hide from everyone" feature is share-worthy.
4. **Product Hutt / Hacker News / indie directories** — a launch spike.
5. ❌ **Paid social ads** — Meta will reject and may flag the account. Skip.
6. ❌ **App stores** — Apple/Google reject IG-automation apps. Distribute via your site.

## 4. Funnel

Search → guide page → "Download Ghosted (free)" → run locally → value →
soft donation prompt (♥) → optional tip.

- Keep the donation a *thank-you*, never a gate. Free stays free.
- Add a one-screen onboarding the first run (what it does, the risk warning,
  "use Safe speed").

## 5. Monetization (donations only)

- **India-friendly:** UPI link/QR, Razorpay Payment Page, or Instamojo.
- Surface the ♥ button after the user gets value (post-job), not on arrival.
- Realistic: side income (tens–low hundreds $/mo) if SEO ranks. Not a salary.
- Do **not** add in-app ads (no traffic model, AdSense rejects the niche).

## 6. Trust & safety (also retention)

- Safe speed is the default; loud warnings on fast tiers (done).
- Daily caps, whitelist, "rest your account" messaging (done).
- Clear Terms/Privacy: not affiliated with Instagram, local-first, no data sold (done).
- This honesty *is* the brand. Users who don't get banned come back and tip.

## 7. Metrics

- Organic sessions to guide pages; download clicks; download→first-run rate.
- Donation conversion (tips / active users).
- Qualitative: feedback form submissions (already wired to `/api/feedback`).

## 8. Roadmap to launch

1. **Package desktop app** (PyInstaller) for macOS + Windows. ← unlocks distribution
2. **Marketing site** on Vercel/Netlify: landing + 5 SEO guide pages + download links.
3. **Donation link** live (UPI/Razorpay).
4. **Soft launch:** Reddit threads + the guides indexed.
5. Iterate on feedback; add 1 SEO post/week.

## 9. Risks (own them)

- Instagram changes its private API → tool breaks; ship updates.
- A user's account gets blocked → they blame you. Mitigate with Safe defaults +
  upfront warnings; never promise safety.
- Meta legal pressure if it gets big and visible → staying free/local/donation
  keeps you a small, non-commercial target, not a lawsuit target.
