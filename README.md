# Ghosted — Instagram Story & Follower Manager

> Hide or unhide your Instagram story from **every follower in one click** — plus find
> who doesn't follow you back, bulk-unfollow, and clean up your audience. Local-first,
> private, with safety pacing built in.

A full-stack web app (FastAPI + vanilla-JS SPA) that wraps Instagram's private mobile
API to do the bulk actions the official app and API won't let you do — one person at a
time is the only native option; Ghosted does the whole list.

![status](https://img.shields.io/badge/status-v1.0-6366f1) ![python](https://img.shields.io/badge/python-3.11-blue) ![license](https://img.shields.io/badge/license-personal%20use-lightgrey)

---

## ✨ Features

- **Hide / unhide your story from all followers** in one click — the headline feature,
  with already-hidden people detected and skipped automatically.
- **Find non-followers** — see who you follow that doesn't follow you back, and vice versa.
- **Bulk actions** — unfollow, follow back, block, unblock, hide/unhide story.
- **Smart filters** — Story-hidden, Mutual, Private/Public, Verified, No-photo, No-name,
  Whitelisted — combinable with live search.
- **Speed tiers** — Safe → Fast → Reckless → Max (parallel), each with its own daily cap,
  so you trade speed for risk consciously.
- **Safety first** — per-day action caps, 45–90s pacing on Safe, whitelist, and clear
  warnings when Instagram rate-limits you.
- **Live job tracking** — progress bar, event log, desktop notifications, stop button.
- **Clickable profiles, avatars, dark mode**, and a responsive UI.

## 🧱 Tech stack & architecture

| Layer | Tech |
|-------|------|
| Backend | **FastAPI** + Uvicorn |
| Instagram | **instagrapi** (private API wrapper) |
| Frontend | Vanilla-JS SPA + **Tailwind** (CDN), no build step |
| Concurrency | `threading` job runner + `ThreadPoolExecutor` for parallel "Max" mode |
| Persistence | JSON session/cache on disk (local-first) |

Notable engineering:

- **Stale-while-revalidate insights cache** (in-memory + disk) so the dashboard loads
  instantly and refreshes in the background instead of blocking on a slow, throttled
  full follower/following pull.
- **Background, non-blocking session restore** on startup (survives restarts without a
  re-login) — runs off the request thread so the server binds instantly.
- **Image proxy** so Instagram-CDN avatars actually render cross-origin from localhost.
- **Adaptive bulk engine** — per-action + per-speed daily caps, whitelist skipping,
  cooperative stop, username map to avoid per-user lookups, and a parallel path that
  hits ~3.7 actions/sec while staying thread-safe.
- **SEO + content** — server-rendered About/FAQ/Privacy/Terms/Contact pages, Open Graph,
  sitemap, manifest, favicon, and a feedback API.

## 🚀 Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --port 8001
```

Open <http://localhost:8001>, sign in with your Instagram credentials (stored only on
your machine), and use the dashboard.

There's also a desktop launcher (`python desktop.py`) that opens it in a native window.

## 📁 Project layout

- [server.py](server.py) — FastAPI app: auth, insights cache, bulk jobs, feedback, pages
- [ig_client.py](ig_client.py) — instagrapi wrapper: session, insights, bulk engine, caps
- [pages.py](pages.py) — server-rendered SEO/legal content pages
- [static/index.html](static/index.html) — single-page dashboard (vanilla JS + Tailwind)
- [desktop.py](desktop.py) — desktop launcher (pywebview / browser)
- [GTM.md](GTM.md) — go-to-market analysis

## 🔒 Privacy

Your Instagram password is used only to create a session **on your own device** and is
never sent anywhere else. Follower data is cached locally. Nothing is sold or shared.

## ⚠️ Disclaimer

Ghosted is an independent project and is **not affiliated with, endorsed by, or sponsored
by Instagram or Meta**. It uses Instagram's private API, which automation tools rely on but
which **violates Instagram's Terms of Use**. Risks include temporary action-blocks, reach
throttling, or account suspension. Use the **Safe** speed, don't run it on a brand-new
account, and don't use an account you can't afford to lose. **Use at your own risk.**

Built as a learning / portfolio project.
