"""
CareerTrajectory AI — GitHub API Real-Time Signal Collector
Fetches live GitHub data: repos, commits, contributions, streaks, stars.
Replaces hardcoded behavioral_signals.github with real data.
"""

import time
import math
from typing import Dict, Optional, List, Any
from datetime import datetime, timedelta
from loguru import logger

from backend.ai.config import GITHUB_TOKEN, USE_LIVE_GITHUB

# ── In-memory cache with TTL ──────────────────────────────────────────────────

_CACHE: Dict[str, Dict] = {}
_CACHE_TTL = 3600  # 1 hour


class GitHubCollector:
    """Collects real-time signals from the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self, token: str = ""):
        self._token = token or GITHUB_TOKEN
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CareerTrajectoryAI/2.0",
        }
        if self._token:
            self._headers["Authorization"] = f"token {self._token}"

    @property
    def is_available(self) -> bool:
        return USE_LIVE_GITHUB

    # ── HTTP Client ────────────────────────────────────────────────────────

    def _get(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict | List]:
        """Make a GET request to GitHub API with caching."""
        cache_key = f"{endpoint}:{params}"
        if cache_key in _CACHE:
            entry = _CACHE[cache_key]
            if time.time() - entry["ts"] < _CACHE_TTL:
                return entry["data"]

        try:
            import httpx
            url = f"{self.BASE_URL}{endpoint}"
            resp = httpx.get(url, headers=self._headers, params=params, timeout=10.0)

            if resp.status_code == 403:
                logger.warning("GitHub API rate limit exceeded")
                return None
            if resp.status_code == 404:
                logger.warning(f"GitHub user/resource not found: {endpoint}")
                return None

            resp.raise_for_status()
            data = resp.json()
            _CACHE[cache_key] = {"data": data, "ts": time.time()}
            return data

        except Exception as e:
            logger.warning(f"GitHub API request failed: {endpoint} — {e}")
            return None

    # ── Data Fetchers ──────────────────────────────────────────────────────

    def fetch_user_profile(self, username: str) -> Optional[Dict]:
        """Fetch basic GitHub user profile."""
        if not self.is_available or not username:
            return None
        return self._get(f"/users/{username}")

    def fetch_repos(self, username: str, per_page: int = 30) -> Optional[List]:
        """Fetch user's public repositories sorted by last updated."""
        if not self.is_available or not username:
            return None
        return self._get(
            f"/users/{username}/repos",
            params={"sort": "updated", "per_page": per_page, "type": "owner"},
        )

    def fetch_events(self, username: str, per_page: int = 100) -> Optional[List]:
        """Fetch recent public events (commits, PRs, issues)."""
        if not self.is_available or not username:
            return None
        return self._get(
            f"/users/{username}/events/public",
            params={"per_page": per_page},
        )

    # ── Aggregated Scores ──────────────────────────────────────────────────

    def compute_github_signals(self, username: str) -> Optional[Dict]:
        """
        Compute full GitHub behavioral signals matching the existing schema:
        {
            "username": str,
            "commit_frequency": float (commits/week),
            "public_repos": int,
            "followers": int,
            "stars_earned": int,
            "streak_days": int,
            "top_languages": List[str],
        }
        """
        if not self.is_available or not username:
            return None

        profile = self.fetch_user_profile(username)
        if not profile:
            return None

        repos = self.fetch_repos(username, per_page=100) or []
        events = self.fetch_events(username, per_page=100) or []

        # ── Stars earned ──
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)

        # ── Top languages ──
        lang_counts: Dict[str, int] = {}
        for r in repos:
            lang = r.get("language")
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        top_languages = sorted(lang_counts, key=lang_counts.get, reverse=True)[:5]

        # ── Commit frequency (commits/week from recent events) ──
        push_events = [e for e in events if e.get("type") == "PushEvent"]
        total_commits = 0
        for pe in push_events:
            payload = pe.get("payload", {})
            total_commits += payload.get("size", 1)

        # Events span at most ~90 days for public events
        weeks = max(len(set(
            e.get("created_at", "")[:10] for e in events
        )) / 7.0, 1.0)
        commit_frequency = round(total_commits / weeks, 1)

        # ── Streak (approximate from events) ──
        event_dates = set()
        for e in events:
            created = e.get("created_at", "")
            if created:
                event_dates.add(created[:10])

        streak_days = 0
        if event_dates:
            sorted_dates = sorted(event_dates, reverse=True)
            try:
                streak = 1
                for i in range(1, len(sorted_dates)):
                    d1 = datetime.strptime(sorted_dates[i - 1], "%Y-%m-%d")
                    d2 = datetime.strptime(sorted_dates[i], "%Y-%m-%d")
                    if (d1 - d2).days <= 1:
                        streak += 1
                    else:
                        break
                streak_days = streak
            except Exception:
                streak_days = len(event_dates)

        return {
            "username": username,
            "commit_frequency": commit_frequency,
            "public_repos": profile.get("public_repos", len(repos)),
            "followers": profile.get("followers", 0),
            "stars_earned": total_stars,
            "streak_days": streak_days,
            "top_languages": top_languages,
            # Extra fields
            "bio": profile.get("bio", ""),
            "blog": profile.get("blog", ""),
            "created_at": profile.get("created_at", ""),
            "total_events_analyzed": len(events),
        }

    def get_rate_limit(self) -> Dict:
        """Check current rate limit status."""
        try:
            import httpx
            resp = httpx.get(
                f"{self.BASE_URL}/rate_limit",
                headers=self._headers,
                timeout=5.0,
            )
            data = resp.json()
            core = data.get("resources", {}).get("core", {})
            return {
                "remaining": core.get("remaining", 0),
                "limit": core.get("limit", 60),
                "reset_at": datetime.fromtimestamp(
                    core.get("reset", 0)
                ).isoformat() if core.get("reset") else "",
            }
        except Exception:
            return {"remaining": -1, "limit": -1, "reset_at": ""}


# ── Module-level convenience ───────────────────────────────────────────────

def get_github_collector() -> GitHubCollector:
    return GitHubCollector()
