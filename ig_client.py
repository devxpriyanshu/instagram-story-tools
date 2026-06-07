"""
Wrapper around instagrapi with session persistence, rate limiting, and the
specific bulk actions the web UI needs.

Sessions are stored as JSON in ./data/{username}.json so we don't hit the
re-login flow every time — Instagram flags repeated fresh logins.
"""
from __future__ import annotations

import json
import os
import random
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

from instagrapi import Client
from instagrapi.exceptions import (
    BadPassword,
    ChallengeRequired,
    LoginRequired,
    PleaseWaitFewMinutes,
    TwoFactorRequired,
)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
COUNTER_PATH = DATA_DIR / "counter.json"

# Conservative pacing. Instagram action-blocks accounts that move too fast.
DEFAULT_MIN_DELAY = 45
DEFAULT_MAX_DELAY = 90
DAILY_ACTION_CAP = 150

# Per-action daily caps. hide/unhide story (block_friend_reel) is a "soft" action
# IG tolerates far more of than follow/unfollow/block, so it gets a higher ceiling.
# Anything not listed falls back to DAILY_ACTION_CAP.
ACTION_DAILY_CAP = {
    "hide_story": 1000,
    "unhide_story": 1000,
}


class LoginError(Exception):
    pass


class TwoFactorNeeded(Exception):
    def __init__(self, two_factor_identifier: str, username: str):
        self.two_factor_identifier = two_factor_identifier
        self.username = username


class ChallengeNeeded(Exception):
    pass


@dataclass
class ActionCounter:
    """Persistent daily counter so we don't exceed DAILY_ACTION_CAP across restarts."""
    day: str = ""
    count: int = 0

    def __post_init__(self):
        self.load()

    def load(self):
        if COUNTER_PATH.exists():
            try:
                data = json.loads(COUNTER_PATH.read_text())
                self.day = data.get("day", "")
                self.count = data.get("count", 0)
            except Exception:
                pass
        
        today = time.strftime("%Y-%m-%d")
        if self.day != today:
            self.day = today
            self.count = 0
            self.save()

    def save(self):
        COUNTER_PATH.write_text(json.dumps({"day": self.day, "count": self.count}))

    def bump(self) -> int:
        self.load()  # Refresh in case of concurrent updates
        self.count += 1
        self.save()
        return self.count


@dataclass
class IGSession:
    username: str
    client: Client
    counter: ActionCounter = field(default_factory=ActionCounter)

    # ---------- session persistence ----------
    def session_path(self) -> Path:
        return DATA_DIR / f"{self.username}.json"

    def save(self) -> None:
        path = self.session_path()
        path.write_text(json.dumps(self.client.get_settings()))
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass

    # ---------- account info ----------
    def me(self) -> dict:
        u = self.client.account_info()
        return {
            "pk": str(u.pk),
            "username": u.username,
            "full_name": u.full_name,
            "profile_pic_url": str(u.profile_pic_url) if u.profile_pic_url else None,
            "follower_count": getattr(u, "follower_count", None),
            "following_count": getattr(u, "following_count", None),
        }

    # ---------- audience ----------
    def follower_ids(self) -> list[str]:
        """All follower user IDs — the set whose stories you can hide/unhide."""
        my_id = self.client.user_id
        followers = self.client.user_followers(my_id, amount=0)  # 0 = all
        return [str(uid) for uid in followers.keys()]

    def hidden_story_user_ids(self) -> set[str]:
        """IDs you've already hidden your story from (IG's 'blocked reels' list).
        Used so the UI can badge people as already-hidden and so a hide-all run
        can skip them. Returns empty set if the endpoint is unavailable."""
        try:
            result = self.client.private_request("friendships/blocked_reels/")
        except Exception:
            return set()
        users = result.get("users") or []
        return {str(u.get("pk")) for u in users if u.get("pk") is not None}

    # ---------- insights ----------
    def insights(self) -> dict:
        my_id = self.client.user_id
        followers = self.client.user_followers(my_id, amount=0)  # 0 = all
        following = self.client.user_following(my_id, amount=0)

        follower_ids = set(followers.keys())
        following_ids = set(following.keys())

        non_followers_ids = following_ids - follower_ids   # you follow, they don't follow back
        fans_ids = follower_ids - following_ids            # they follow you, you don't follow back
        mutuals_ids = follower_ids & following_ids

        hidden_ids = self.hidden_story_user_ids()          # already hidden-from

        def to_list(ids: Iterable, source: dict) -> list[dict]:
            out = []
            for uid in ids:
                u = source.get(uid)
                if not u:
                    continue
                out.append({
                    "pk": str(u.pk),
                    "username": u.username,
                    "full_name": u.full_name,
                    "profile_pic_url": str(u.profile_pic_url) if u.profile_pic_url else None,
                    "is_private": getattr(u, "is_private", False),
                    "is_verified": getattr(u, "is_verified", False),
                    "story_hidden": str(u.pk) in hidden_ids,
                })
            out.sort(key=lambda x: x["username"].lower())
            return out

        return {
            "follower_count": len(follower_ids),
            "following_count": len(following_ids),
            "mutual_count": len(mutuals_ids),
            "hidden_count": len(hidden_ids & follower_ids),
            "non_followers": to_list(non_followers_ids, following),
            "fans": to_list(fans_ids, followers),
        }

    # ---------- bulk actions ----------
    def bulk(
        self,
        action: str,
        user_ids: list[str],
        whitelist_usernames: set[str] | None = None,
        on_progress: Callable[[dict], None] | None = None,
        should_stop: Callable[[], bool] | None = None,
        min_delay: int = DEFAULT_MIN_DELAY,
        max_delay: int = DEFAULT_MAX_DELAY,
    ) -> dict:
        """
        action: unfollow | follow | hide_story | unhide_story | block | unblock
        Returns a summary dict. Calls on_progress after each item.
        """
        runner = {
            "unfollow": self.client.user_unfollow,
            "follow": self.client.user_follow,
            "block": self.client.user_block,
            "unblock": self.client.user_unblock,
            "hide_story": self._hide_story_from,
            "unhide_story": self._unhide_story_from,
        }.get(action)

        if not runner:
            raise ValueError(f"unknown action: {action}")

        whitelist = {u.lower() for u in (whitelist_usernames or set())}
        cap = ACTION_DAILY_CAP.get(action, DAILY_ACTION_CAP)
        results = {"ok": [], "skipped": [], "failed": [], "stopped": False}

        for idx, uid in enumerate(user_ids):
            if should_stop and should_stop():
                results["stopped"] = True
                break

            # Resolve username for whitelist check + reporting (cheap if cached)
            try:
                username = self.client.username_from_user_id(int(uid))
            except Exception:
                username = uid

            if username and username.lower() in whitelist:
                results["skipped"].append({"user_id": uid, "username": username, "reason": "whitelist"})
                if on_progress:
                    on_progress({"index": idx + 1, "total": len(user_ids), "username": username, "status": "skipped"})
                continue

            if self.counter.bump() > cap:
                results["stopped"] = True
                results["failed"].append({"user_id": uid, "username": username, "reason": f"daily cap reached ({cap})"})
                break

            try:
                runner(int(uid))
                results["ok"].append({"user_id": uid, "username": username})
                status = "ok"
            except PleaseWaitFewMinutes as e:
                results["failed"].append({"user_id": uid, "username": username, "reason": f"rate limited: {e}"})
                results["stopped"] = True
                if on_progress:
                    on_progress({"index": idx + 1, "total": len(user_ids), "username": username, "status": "rate_limited"})
                break
            except Exception as e:
                results["failed"].append({"user_id": uid, "username": username, "reason": str(e)})
                status = "failed"

            if on_progress:
                on_progress({"index": idx + 1, "total": len(user_ids), "username": username, "status": status})

            # Persist session frequently in case the process dies mid-run.
            if idx % 10 == 0:
                self.save()

            if idx < len(user_ids) - 1:
                time.sleep(random.uniform(min_delay, max_delay))

        self.save()
        return results

    # ---------- story hide / unhide via private API ----------
    # instagrapi doesn't ship a top-level helper for these, so we hit the
    # private endpoints directly. These are the same calls the mobile app makes.
    def _hide_story_from(self, user_id: int) -> bool:
        return self._story_visibility(user_id, hide=True)

    def _unhide_story_from(self, user_id: int) -> bool:
        return self._story_visibility(user_id, hide=False)

    def _story_visibility(self, user_id: int, hide: bool) -> bool:
        endpoint = f"friendships/block_friend_reel/{user_id}/" if hide else f"friendships/unblock_friend_reel/{user_id}/"
        data = self.client.with_action_data({
            "_uuid": self.client.uuid,
            "source": "profile",
        })
        result = self.client.private_request(endpoint, data)
        return result.get("status") == "ok"


# ---------- login flow ----------
def login(username: str, password: str, verification_code: str | None = None) -> IGSession:
    cl = Client()
    cl.delay_range = [1, 3]  # tiny jitter inside instagrapi itself

    settings_path = DATA_DIR / f"{username}.json"
    if settings_path.exists():
        try:
            # Fast path: restore the saved session and verify it with ONE cheap
            # call. Skips instagrapi's full login() pre/post-login flow (several
            # network round-trips) whenever the session is still alive — this is
            # the difference between a ~1s and a ~15s "login".
            cl.set_settings(json.loads(settings_path.read_text()))
            cl.get_timeline_feed()  # raises LoginRequired if the session is dead
            return IGSession(username=username, client=cl)
        except LoginRequired:
            cl = Client()
            cl.delay_range = [1, 3]
        except Exception:
            # fall through to fresh login
            cl = Client()
            cl.delay_range = [1, 3]

    try:
        cl.login(username, password, verification_code=verification_code or "")
    except TwoFactorRequired:
        # instagrapi raises this when 2FA is needed; the verification_code arg
        # above handles it on the *retry* call from the UI.
        raise TwoFactorNeeded(two_factor_identifier=cl.last_json.get("two_factor_info", {}).get("two_factor_identifier", ""), username=username)
    except ChallengeRequired:
        raise ChallengeNeeded()
    except BadPassword as e:
        raise LoginError(f"bad password: {e}")
    except Exception as e:
        raise LoginError(str(e))

    sess = IGSession(username=username, client=cl)
    sess.save()
    return sess
