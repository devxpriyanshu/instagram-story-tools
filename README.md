# IG Tools

Local web dashboard for personal Instagram account hygiene:

- See followers / following / mutuals at a glance
- Find users who don't follow you back
- Find users who follow you that you don't follow back
- Bulk **unfollow / follow / block / unblock**
- Bulk **hide story** from a list, or **unhide** for a list
- Username **whitelist** (never act on these)
- Safe pacing: 45–90s jitter between actions, hard daily cap of 150

Single-user, runs on `localhost`. Credentials stay on your machine.

## Read this first

This uses Instagram's **private mobile API** via `instagrapi`. That API is not officially supported and using it violates Instagram's Terms of Use. Realistic risks:

- Temporary action blocks (hours to days)
- Permanent account disable, especially for new or low-activity accounts
- Reach throttling

The defaults err on the safe side. **Don't lower the delays. Don't run it on a brand-new account. Don't run it on an account you can't afford to lose.** Try it on a throwaway first.

## Setup

```bash
cd /Users/priyanshudutta/Desktop/Web_Dev/Instgram
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn server:app --port 8000
```

Open <http://localhost:8000>.

## How login works

1. Enter your Instagram username + password.
2. If 2FA is on, you'll be told to retry — paste the 6-digit code from your authenticator into the third box and click sign in again.
3. If Instagram sends a "challenge" (suspicious login prompt), open the Instagram app on your phone, approve the login, then retry.
4. After the first successful login, your session is saved to `data/{username}.json` and reused. This avoids repeated fresh logins, which is what usually trips checkpoints.

## Pacing & safety

- Default delay between actions: **45–90 seconds (random jitter)**
- Hard cap: **150 actions per day** per process
- Whitelist: edit on the dashboard, stored in `data/whitelist.json`. Whitelisted usernames are skipped automatically.
- If Instagram rate-limits you mid-job (`PleaseWaitFewMinutes`), the job stops and the rest of the queue is preserved as "failed" with the reason — wait several hours before resuming.

## File layout

- [requirements.txt](requirements.txt) — Python deps
- [server.py](server.py) — FastAPI app, job runner, whitelist
- [ig_client.py](ig_client.py) — `instagrapi` wrapper, session persistence, bulk action engine
- [static/index.html](static/index.html) — single-page dashboard (vanilla JS + Tailwind CDN)
- `data/` — created at runtime; holds session JSON and whitelist (gitignored)

## Known limits

- The `Stop` button on a running job is cooperative — it sets a flag, but the worker only checks between actions. Worst case, one more action runs before it stops.
- Insights are computed each time you load the dashboard; for accounts with tens of thousands of followers this can take a minute. There's no caching layer yet.
- Single user only — no auth on the local server. Don't expose port 8000 to the internet.
