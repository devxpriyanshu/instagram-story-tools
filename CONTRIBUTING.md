# Contributing & Feedback

Thanks for your interest in Ghosted! This is a free, local-first project and
feedback is very welcome.

## 💬 Give feedback / connect

- **Found a bug or have a feature idea?** Open a
  [GitHub Issue](../../issues/new/choose).
- **Questions, ideas, or just want to connect?** Use
  [GitHub Discussions](../../discussions).
- There's also an in-app feedback form (Contact page) — note it only saves
  locally on your machine, so for anything you want *us* to see, use Issues or
  Discussions.

## 🛠️ Develop

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --port 8001 --reload
```

- Backend: [server.py](server.py) (FastAPI), [ig_client.py](ig_client.py)
  (Instagram + bulk engine), [pages.py](pages.py) (content pages).
- Frontend: [static/index.html](static/index.html) — single file, vanilla JS +
  Tailwind CDN, no build step. Edit and refresh.

## ✅ Pull requests

- Keep changes focused and match the surrounding style.
- Don't commit anything from `data/` (sessions/cache) — it's gitignored.
- Be mindful of safety: the default pacing exists to protect users' accounts.
  Don't lower defaults or remove warnings.

## ⚠️ A note on responsibility

Ghosted uses Instagram's private API, which may violate Instagram's Terms.
Contributions should keep the project honest about that risk. Please don't add
features designed purely to evade detection or to target other users.
