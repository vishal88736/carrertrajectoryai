"""
CareerTrajectory AI — LeetCode Signal Collector
Fetches user statistics from LeetCode's public GraphQL API.
No authentication required.
"""

import time
from typing import Dict, Optional
from loguru import logger

from backend.ai.config import USE_LIVE_LEETCODE

_CACHE: Dict[str, Dict] = {}
_CACHE_TTL = 3600


class LeetCodeCollector:
    """Collects competitive programming signals from LeetCode GraphQL API."""

    GRAPHQL_URL = "https://leetcode.com/graphql"

    def __init__(self):
        self._headers = {
            "Content-Type": "application/json",
            "User-Agent": "CareerTrajectoryAI/2.0",
        }

    @property
    def is_available(self) -> bool:
        return USE_LIVE_LEETCODE

    def _graphql(self, query: str, variables: Dict) -> Optional[Dict]:
        """Execute a GraphQL query against LeetCode."""
        cache_key = f"lc:{variables}"
        if cache_key in _CACHE:
            entry = _CACHE[cache_key]
            if time.time() - entry["ts"] < _CACHE_TTL:
                return entry["data"]

        try:
            import httpx
            resp = httpx.post(
                self.GRAPHQL_URL,
                json={"query": query, "variables": variables},
                headers=self._headers,
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
            _CACHE[cache_key] = {"data": data, "ts": time.time()}
            return data
        except Exception as e:
            logger.warning(f"LeetCode GraphQL request failed: {e}")
            return None

    def fetch_user_stats(self, username: str) -> Optional[Dict]:
        """
        Fetch LeetCode user stats: problems solved, acceptance rate, ranking.
        Uses the public matchedUser query.
        """
        if not self.is_available or not username:
            return None

        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    ranking
                    reputation
                    starRating
                }
                submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                    }
                }
            }
        }
        """

        data = self._graphql(query, {"username": username})
        if not data or "errors" in data:
            return None

        user = data.get("data", {}).get("matchedUser")
        if not user:
            return None

        # Parse submission stats
        submissions = user.get("submitStatsGlobal", {}).get("acSubmissionNum", [])
        total_solved = 0
        difficulty_breakdown = {}
        for entry in submissions:
            diff = entry.get("difficulty", "All")
            count = entry.get("count", 0)
            if diff == "All":
                total_solved = count
            else:
                difficulty_breakdown[diff.lower()] = count

        profile = user.get("profile", {})

        return {
            "username": username,
            "problems_solved": total_solved,
            "easy": difficulty_breakdown.get("easy", 0),
            "medium": difficulty_breakdown.get("medium", 0),
            "hard": difficulty_breakdown.get("hard", 0),
            "ranking": profile.get("ranking", 0),
            "reputation": profile.get("reputation", 0),
        }

    def fetch_contest_history(self, username: str) -> Optional[Dict]:
        """Fetch LeetCode contest rating and history."""
        if not self.is_available or not username:
            return None

        query = """
        query getUserContestRanking($username: String!) {
            userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
                topPercentage
            }
        }
        """

        data = self._graphql(query, {"username": username})
        if not data or "errors" in data:
            return None

        ranking = data.get("data", {}).get("userContestRanking")
        if not ranking:
            return {"username": username, "contest_rating": 1200, "contest_rank_percentile": 50}

        return {
            "username": username,
            "contest_rating": int(ranking.get("rating", 1200)),
            "contests_attended": ranking.get("attendedContestsCount", 0),
            "global_ranking": ranking.get("globalRanking", 0),
            "contest_rank_percentile": round(
                100 - (ranking.get("topPercentage", 50) or 50), 1
            ),
        }

    def compute_leetcode_signals(self, username: str) -> Optional[Dict]:
        """
        Compute full LeetCode signals matching the existing schema:
        {
            "username": str,
            "problems_solved": int,
            "contest_rating": int,
            "contest_rank_percentile": float,
        }
        """
        if not self.is_available or not username:
            return None

        stats = self.fetch_user_stats(username)
        contest = self.fetch_contest_history(username)

        if not stats and not contest:
            return None

        problems_solved = (stats or {}).get("problems_solved", 0)
        contest_rating = (contest or {}).get("contest_rating", 1200)
        percentile = (contest or {}).get("contest_rank_percentile", 50)

        return {
            "username": username,
            "problems_solved": problems_solved,
            "contest_rating": contest_rating,
            "contest_rank_percentile": percentile,
            # Extra detail
            "easy": (stats or {}).get("easy", 0),
            "medium": (stats or {}).get("medium", 0),
            "hard": (stats or {}).get("hard", 0),
        }


def get_leetcode_collector() -> LeetCodeCollector:
    return LeetCodeCollector()
