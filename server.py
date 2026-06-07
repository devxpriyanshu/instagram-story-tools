"""
FastAPI backend for the Instagram tools dashboard.

Run:
    uvicorn server:app --reload --port 8000

Then open http://localhost:8000
"""
from __future__ import annotations

import json
import threading
import time
import uuid
from pathlib import Path
from typing import Optional

from urllib.parse import urlparse

import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ig_client import (
    DATA_DIR,
    ChallengeNeeded,
    IGSession,
    LoginError,
    TwoFactorNeeded,
    login as ig_login,
    restore_session,
)

app = FastAPI(title="IG Tools")

# Files in data/ that are NOT account sessions.
_NON_SESSION_FILES = {"counter.json", "whitelist.json"}


@app.on_event("startup")
def _restore_session_on_startup() -> None:
    """Survive restarts: if exactly one saved session exists, restore it from
    cookies so the user stays logged in without re-entering a password."""
    sessions = [p for p in DATA_DIR.glob("*.json") if p.name not in _NON_SESSION_FILES]
    if len(sessions) != 1:
        return
    username = sessions[0].stem
    sess = restore_session(username)
    if sess:
        _state["session"] = sess

# --------- in-memory state ---------
# Single-user local app — no auth, no multi-tenant. Keep the active session in
# memory and persist Instagram cookies to disk via IGSession.save().
_state: dict = {"session": None, "jobs": {}, "insights_cache": None, "insights_cached_at": 0.0}
_lock = threading.Lock()

# Insights (full follower + following pull) is the single most expensive call —
# cache it so repeat dashboard loads are instant. Bulk jobs invalidate it.
INSIGHTS_TTL = 600  # seconds

WHITELIST_PATH = DATA_DIR / "whitelist.json"


def _load_whitelist() -> list[str]:
    if WHITELIST_PATH.exists():
        try:
            items = json.loads(WHITELIST_PATH.read_text())
            return [str(u).lower() for u in items]
        except Exception:
            return []
    return []


def _save_whitelist(items: list[str]) -> None:
    WHITELIST_PATH.write_text(json.dumps(sorted(set(items))))


def _require_session() -> IGSession:
    sess = _state.get("session")
    if not sess:
        raise HTTPException(401, "not logged in")
    return sess


# --------- request models ---------
class LoginBody(BaseModel):
    username: str
    password: str
    verification_code: Optional[str] = None


class BulkBody(BaseModel):
    action: str  # unfollow | follow | hide_story | unhide_story | block | unblock
    user_ids: list[str]
    min_delay: int = 45
    max_delay: int = 90


class WhitelistBody(BaseModel):
    usernames: list[str]


# --------- routes: auth ---------
@app.post("/api/login")
def login(body: LoginBody):
    try:
        sess = ig_login(body.username, body.password, verification_code=body.verification_code)
    except TwoFactorNeeded as e:
        raise HTTPException(409, detail={"kind": "2fa", "username": e.username})
    except ChallengeNeeded:
        raise HTTPException(409, detail={"kind": "challenge", "message": "Instagram sent a challenge — open the app, approve the login, then retry."})
    except LoginError as e:
        raise HTTPException(401, detail={"kind": "login_error", "message": str(e)})

    _state["session"] = sess
    return {"ok": True, "me": sess.me()}


@app.post("/api/logout")
def logout():
    _state["session"] = None
    return {"ok": True}


@app.get("/api/me")
def me():
    sess = _require_session()
    return sess.me()


# Instagram CDN blocks hotlinked <img> from localhost (403 / expiring signed
# URLs), so profile pictures never render in the browser. Proxy them through the
# backend instead. Host is allowlisted to avoid turning this into an open proxy.
_ALLOWED_IMG_HOSTS = ("cdninstagram.com", "fbcdn.net")


@app.get("/api/img")
def img(url: str):
    host = (urlparse(url).hostname or "").lower()
    if not any(host == h or host.endswith("." + h) for h in _ALLOWED_IMG_HOSTS):
        raise HTTPException(400, "host not allowed")
    try:
        r = requests.get(url, timeout=10, headers={
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.instagram.com/",
        })
        r.raise_for_status()
    except Exception:
        raise HTTPException(502, "image fetch failed")
    return Response(
        content=r.content,
        media_type=r.headers.get("content-type", "image/jpeg"),
        headers={"Cache-Control": "public, max-age=86400"},
    )


# --------- routes: insights ---------
def _invalidate_insights() -> None:
    with _lock:
        _state["insights_cache"] = None
        _state["insights_cached_at"] = 0.0


@app.get("/api/insights")
def insights(refresh: bool = False):
    sess = _require_session()
    now = time.time()
    with _lock:
        cached = _state["insights_cache"]
        age = now - _state["insights_cached_at"]
    if cached and not refresh and age < INSIGHTS_TTL:
        return {**cached, "cached": True, "cached_at": _state["insights_cached_at"]}

    data = sess.insights()
    with _lock:
        _state["insights_cache"] = data
        _state["insights_cached_at"] = now
    return {**data, "cached": False, "cached_at": now}


@app.get("/api/followers/ids")
def follower_ids():
    """All follower IDs plus the subset already hidden-from. The frontend skips
    already-hidden on a hide-all run (and already-visible on an unhide-all run),
    so we only fire the actions that actually change something."""
    sess = _require_session()
    ids = sess.follower_ids()
    hidden = sorted(sess.hidden_story_user_ids() & set(ids))
    return {"ids": ids, "count": len(ids), "hidden_ids": hidden, "hidden_count": len(hidden)}


# --------- routes: bulk jobs ---------
@app.post("/api/bulk")
def bulk(body: BulkBody):
    sess = _require_session()
    job_id = uuid.uuid4().hex[:12]
    whitelist = set(_load_whitelist())

    with _lock:
        # Cap memory: keep only 50 most recent jobs
        if len(_state["jobs"]) >= 50:
            # Sort by whatever means or just pop first (dicts are ordered in 3.7+)
            oldest_id = next(iter(_state["jobs"]))
            _state["jobs"].pop(oldest_id)

        job = {
            "id": job_id,
            "action": body.action,
            "total": len(body.user_ids),
            "done": 0,
            "current": None,
            "status": "running",
            "events": [],
            "result": None,
        }
        _state["jobs"][job_id] = job

    def on_progress(ev: dict):
        with _lock:
            job["done"] = ev["index"]
            job["current"] = ev.get("username")
            # Keep events bounded — UI only needs a tail
            job["events"].append(ev)
            if len(job["events"]) > 200:
                job["events"] = job["events"][-200:]

    def should_stop():
        with _lock:
            return job["status"] == "stop_requested"

    def run():
        try:
            result = sess.bulk(
                body.action,
                body.user_ids,
                whitelist_usernames=whitelist,
                on_progress=on_progress,
                should_stop=should_stop,
                min_delay=body.min_delay,
                max_delay=body.max_delay,
            )
            with _lock:
                job["result"] = result
                job["status"] = "stopped" if result.get("stopped") else "done"
            _invalidate_insights()  # follows/hides changed the data
        except Exception as e:
            with _lock:
                job["status"] = "error"
                job["result"] = {"error": str(e)}

    threading.Thread(target=run, daemon=True).start()
    return {"job_id": job_id}


@app.get("/api/job/{job_id}")
def job_status(job_id: str):
    with _lock:
        job = _state["jobs"].get(job_id)
        if not job:
            raise HTTPException(404, "job not found")
        # Return a copy with tail of events to keep payload small
        return {**job, "events": job["events"][-25:]}


@app.post("/api/job/{job_id}/stop")
def job_stop(job_id: str):
    # Cooperative stop: we just mark it; the worker checks daily cap / rate
    # limit naturally. For a true kill switch see TODO in README.
    with _lock:
        job = _state["jobs"].get(job_id)
        if not job:
            raise HTTPException(404, "job not found")
        job["status"] = "stop_requested"
    return {"ok": True}


# --------- routes: whitelist ---------
@app.get("/api/whitelist")
def get_whitelist():
    return {"usernames": _load_whitelist()}


@app.put("/api/whitelist")
def put_whitelist(body: WhitelistBody):
    cleaned = [u.strip().lstrip("@").lower() for u in body.usernames if u.strip()]
    _save_whitelist(cleaned)
    return {"usernames": _load_whitelist()}


# --------- static frontend ---------
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
