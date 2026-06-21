"""
CareerTrajectory AI — Kaggle Signal Collector
Fetches user statistics from the Kaggle API.
Requires KAGGLE_USERNAME and KAGGLE_KEY environment variables.
"""

import time
from typing import Dict, Optional
from loguru import logger

from backend.ai.config import KAGGLE_USERNAME, KAGGLE_KEY, USE_LIVE_KAGGLE

_CACHE: Dict[str, Dict] = {}
_CACHE_TTL = 3600


class KaggleCollector:
    """Collects competitive data science signals from Kaggle."""

    BASE_URL = "https://www.kaggle.com/api/v1"

    def __init__(self):
        self._auth = (KAGGLE_USERNAME, KAGGLE_KEY) if KAGGLE_USERNAME and KAGGLE_KEY else None

    @property
    def is_available(self) -> bool:
        return USE_LIVE_KAGGLE and self._auth is not None

    def _get(self, endpoint: str) -> Optional[Dict]:
        """Make authenticated GET request to Kaggle API."""
        cache_key = f"kaggle:{endpoint}"
        if cache_key in _CACHE:
            entry = _CACHE[cache_key]
            if time.time() - entry["ts"] < _CACHE_TTL:
                return entry["data"]

        if not self._auth:
            return None

        try:
            import httpx
            resp = httpx.get(
                f"{self.BASE_URL}{endpoint}",
                auth=self._auth,
                headers={"User-Agent": "CareerTrajectoryAI/2.0"},
                timeout=15.0,
            )
            if resp.status_code == 404:
                logger.warning(f"Kaggle user not found: {endpoint}")
                return None
            resp.raise_for_status()
            data = resp.json()
            _CACHE[cache_key] = {"data": data, "ts": time.time()}
            return data
        except Exception as e:
            logger.warning(f"Kaggle API request failed: {e}")
            return None

    def fetch_user_profile(self, username: str) -> Optional[Dict]:
        """Fetch Kaggle user profile: tier, medals, bio."""
        if not self.is_available or not username:
            return None

        # Kaggle doesn't have a direct user profile endpoint in the public API,
        # so we scrape the user's competitions list and kernel list for metadata.
        # For now, use the competitions list endpoint as a proxy.
        try:
            import httpx
            resp = httpx.get(
                f"https://www.kaggle.com/api/v1/users/{username}",
                auth=self._auth,
                headers={"User-Agent": "CareerTrajectoryAI/2.0"},
                timeout=15.0,
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            pass

        return None

    def fetch_competitions(self, username: str) -> Optional[list]:
        """Fetch user's competition history."""
        if not self.is_available or not username:
            return None
        # Kaggle public API doesn't expose per-user competition history directly.
        # This is a placeholder for the interface.
        return None

    def compute_kaggle_signals(self, username: str) -> Optional[Dict]:
        """
        Compute Kaggle signals matching the existing schema:
        {
            "username": str,
            "competitions": int,
            "medals": {"gold": int, "silver": int, "bronze": int},
            "ranking_percentile": float,
        }
        Falls back to reasonable defaults if API unavailable.
        """
        if not username:
            return None

        if not self.is_available:
            # Return None to signal that caller should use existing data
            return None

        profile = self.fetch_user_profile(username)
        if not profile:
            return None

        # Parse Kaggle profile response
        tier = profile.get("tier", "Novice")
        tier_percentile_map = {
            "Grandmaster": 99,
            "Master": 95,
            "Expert": 85,
            "Contributor": 60,
            "Novice": 30,
        }

        return {
            "username": username,
            "competitions": profile.get("totalCompetitions", 0),
            "medals": {
                "gold": profile.get("totalGoldMedals", 0),
                "silver": profile.get("totalSilverMedals", 0),
                "bronze": profile.get("totalBronzeMedals", 0),
            },
            "ranking_percentile": tier_percentile_map.get(tier, 50),
            "tier": tier,
            "datasets": profile.get("totalDatasets", 0),
            "notebooks": profile.get("totalKernels", 0),
        }


def get_kaggle_collector() -> KaggleCollector:
    return KaggleCollector()
