"""
CareerTrajectory AI — Recruiter Feedback Store
Stores recruiter interactions (shortlist, reject, hire) for online learning.
JSON-based storage, upgradeable to PostgreSQL.
"""

import json
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from loguru import logger

from backend.ai.config import FEEDBACK_DIR


class FeedbackStore:
    """
    Simple JSON-backed feedback storage.
    Records recruiter actions on candidates for use as training labels.
    """

    FEEDBACK_FILE = FEEDBACK_DIR / "recruiter_feedback.jsonl"

    # Action → relevance label mapping for LightGBM training
    ACTION_LABELS = {
        "hired": 4.0,
        "interviewed": 3.0,
        "shortlisted": 2.0,
        "thumbs_up": 2.0,
        "bookmarked": 1.5,
        "thumbs_down": 0.5,
        "rejected": 0.0,
        "skipped": 0.5,
    }

    def __init__(self):
        self.FEEDBACK_FILE.parent.mkdir(parents=True, exist_ok=True)

    def record_feedback(
        self,
        candidate_id: str,
        job_id: str,
        action: str,
        rating: Optional[float] = None,
        recruiter_id: str = "default",
        notes: str = "",
    ):
        """
        Store a recruiter feedback event.

        Args:
            candidate_id: The candidate being evaluated
            job_id: The job requisition context
            action: One of: shortlisted, rejected, interviewed, hired, 
                    thumbs_up, thumbs_down, bookmarked, skipped
            rating: Optional explicit relevance rating (0-5)
            recruiter_id: Who provided the feedback
            notes: Optional text notes
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "recruiter_id": recruiter_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "action": action,
            "rating": rating if rating is not None else self.ACTION_LABELS.get(action, 1.0),
            "notes": notes,
        }

        try:
            with open(self.FEEDBACK_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
            logger.debug(f"Feedback recorded: {action} on {candidate_id} for {job_id}")
        except Exception as e:
            logger.warning(f"Failed to record feedback: {e}")

    def get_all_feedback(self) -> List[Dict]:
        """Read all feedback entries."""
        if not self.FEEDBACK_FILE.exists():
            return []
        entries = []
        try:
            with open(self.FEEDBACK_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entries.append(json.loads(line))
        except Exception as e:
            logger.warning(f"Failed to read feedback: {e}")
        return entries

    def get_feedback_for_job(self, job_id: str) -> List[Dict]:
        """Get all feedback for a specific job."""
        return [f for f in self.get_all_feedback() if f.get("job_id") == job_id]

    def get_training_labels(self) -> Dict[str, Dict[str, float]]:
        """
        Export feedback as training labels.
        Returns: {candidate_id: {job_id: relevance_label}}
        """
        labels = {}
        for entry in self.get_all_feedback():
            cid = entry.get("candidate_id", "")
            jid = entry.get("job_id", "")
            rating = entry.get("rating", 1.0)
            if cid and jid:
                if cid not in labels:
                    labels[cid] = {}
                # Take the latest / highest rating per candidate-job pair
                labels[cid][jid] = max(labels[cid].get(jid, 0), rating)
        return labels

    def get_stats(self) -> Dict:
        """Return feedback statistics."""
        entries = self.get_all_feedback()
        if not entries:
            return {
                "total": 0,
                "actions": {},
                "unique_candidates": 0,
                "unique_jobs": 0,
            }

        action_counts = {}
        candidates = set()
        jobs = set()
        for e in entries:
            action = e.get("action", "unknown")
            action_counts[action] = action_counts.get(action, 0) + 1
            candidates.add(e.get("candidate_id", ""))
            jobs.add(e.get("job_id", ""))

        return {
            "total": len(entries),
            "actions": action_counts,
            "unique_candidates": len(candidates),
            "unique_jobs": len(jobs),
        }

    def clear(self):
        """Delete all feedback data."""
        if self.FEEDBACK_FILE.exists():
            self.FEEDBACK_FILE.unlink()
            logger.info("Feedback store cleared")


# ── Module-level convenience ───────────────────────────────────────────────

_store_instance: Optional[FeedbackStore] = None

def get_feedback_store() -> FeedbackStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = FeedbackStore()
    return _store_instance
