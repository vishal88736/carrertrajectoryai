"""
CareerTrajectory AI — LightGBM Learning-to-Rank Model
Replaces the weighted-sum FPS formula with a trained LambdaRank model.
Supports online learning from recruiter feedback.
"""

import numpy as np
import json
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from loguru import logger

from backend.ai.config import MODELS_DIR, USE_ML_RANKING


class RankingModel:
    """
    LightGBM LambdaRank model for candidate ranking.
    Falls back to the weighted-sum FPS formula if not trained.
    """

    MODEL_FILE = MODELS_DIR / "lightgbm_ranker.txt"
    FEATURE_NAMES = [
        "semantic_fit",
        "career_momentum",
        "behavioral_evidence",
        "contextual_intelligence",
        "years_of_experience",
        "skill_count",
        "cert_count",
        "project_count",
        "learning_velocity",
    ]

    def __init__(self):
        self._model = None
        self._is_trained = False
        self._load_if_exists()

    def _load_if_exists(self):
        """Load previously saved model if it exists."""
        if self.MODEL_FILE.exists():
            try:
                import lightgbm as lgb
                self._model = lgb.Booster(model_file=str(self.MODEL_FILE))
                self._is_trained = True
                logger.info("✅ LightGBM ranking model loaded from disk")
            except Exception as e:
                logger.warning(f"Failed to load LightGBM model: {e}")

    @property
    def is_available(self) -> bool:
        return USE_ML_RANKING and self._is_trained and self._model is not None

    # ── Feature Engineering ────────────────────────────────────────────────

    def extract_features(self, candidate: Dict, job: Dict = None) -> np.ndarray:
        """Extract feature vector from candidate for ranking."""
        scores = candidate.get("scores", {})
        skills = candidate.get("skills", {})
        history = skills.get("history", [])

        features = [
            scores.get("semantic_fit", 0.0),
            scores.get("career_momentum", 0.0),
            scores.get("behavioral_evidence", 0.0),
            scores.get("contextual_intelligence", 0.0),
            float(candidate.get("years_of_experience", 0)),
            float(len(skills.get("current", []))),
            float(len(candidate.get("certifications", []))),
            float(len(candidate.get("projects", []))),
            float(len(history)) / max(float(candidate.get("years_of_experience", 1)), 1.0),
        ]

        return np.array(features, dtype=np.float32)

    def extract_features_batch(
        self,
        candidates: List[Dict],
        job: Dict = None,
    ) -> np.ndarray:
        """Extract features for multiple candidates."""
        return np.array([
            self.extract_features(c, job) for c in candidates
        ], dtype=np.float32)

    # ── Training ───────────────────────────────────────────────────────────

    def train(
        self,
        candidates: List[Dict],
        labels: List[float],
        group_sizes: Optional[List[int]] = None,
    ):
        """
        Train the ranking model on labeled candidate-job pairs.
        
        Args:
            candidates: List of candidate dicts (with scores pre-computed)
            labels: Relevance labels (higher = better fit)
            group_sizes: Number of candidates per query group.
                         If None, all candidates form one group.
        """
        try:
            import lightgbm as lgb

            X = self.extract_features_batch(candidates)
            
            # Lambdarank objective in LightGBM requires integer labels (relevance grades)
            labels_arr = np.array(labels, dtype=np.float32)
            if np.all(labels_arr <= 1.0):
                y = np.clip((labels_arr * 10).astype(np.int32), 0, 10)
            else:
                y = labels_arr.astype(np.int32)

            if group_sizes is None:
                group_sizes = [len(candidates)]

            train_data = lgb.Dataset(
                X, label=y, group=group_sizes,
                feature_name=self.FEATURE_NAMES,
            )

            params = {
                "objective": "lambdarank",
                "metric": "ndcg",
                "ndcg_eval_at": [3, 5, 10],
                "learning_rate": 0.05,
                "num_leaves": 31,
                "min_data_in_leaf": 1,
                "min_sum_hessian_in_leaf": 0.001,
                "verbose": -1,
            }

            self._model = lgb.train(
                params,
                train_data,
                num_boost_round=100,
                valid_sets=[train_data],
            )
            self._is_trained = True

            # Save to disk
            self._model.save_model(str(self.MODEL_FILE))
            logger.info(f"✅ LightGBM ranking model trained and saved — {len(candidates)} samples")

        except Exception as e:
            logger.error(f"LightGBM training failed: {e}")

    def train_synthetic(self, candidates: List[Dict] = None):
        """
        Train on synthetic data derived from existing candidates.
        Uses the current FPS scores as pseudo-labels.
        """
        if candidates is None:
            from data.sample_data import get_candidates, get_jobs
            from backend.scoring_engine import rank_candidates
            candidates = get_candidates()
            jobs = get_jobs()
            # Rank against first job
            candidates = rank_candidates(candidates, jobs[0])

        if not candidates:
            logger.warning("No candidates for synthetic training")
            return

        # Use FPS as relevance label (already 0-1)
        labels = [c.get("scores", {}).get("fps", 0.5) for c in candidates]

        # Data augmentation: add noise variants
        augmented_candidates = list(candidates)
        augmented_labels = list(labels)

        for c in candidates:
            for _ in range(3):
                noisy = dict(c)
                noisy_scores = dict(c.get("scores", {}))
                for key in ["semantic_fit", "career_momentum",
                            "behavioral_evidence", "contextual_intelligence"]:
                    val = noisy_scores.get(key, 0.5)
                    noisy_scores[key] = max(0, min(1, val + np.random.normal(0, 0.05)))
                noisy_scores["fps"] = (
                    0.35 * noisy_scores["semantic_fit"]
                    + 0.30 * noisy_scores["career_momentum"]
                    + 0.20 * noisy_scores["behavioral_evidence"]
                    + 0.15 * noisy_scores["contextual_intelligence"]
                )
                noisy["scores"] = noisy_scores
                augmented_candidates.append(noisy)
                augmented_labels.append(noisy_scores["fps"])

        self.train(augmented_candidates, augmented_labels)

    # ── Prediction ─────────────────────────────────────────────────────────

    def predict(self, candidate: Dict, job: Dict = None) -> float:
        """Predict FPS score for a single candidate."""
        if not self.is_available:
            return -1.0  # Signal to use fallback

        features = self.extract_features(candidate, job).reshape(1, -1)
        try:
            raw_score = self._model.predict(features)[0]
            # Normalize to [0, 1] using sigmoid
            normalized = 1.0 / (1.0 + np.exp(-raw_score))
            return round(float(normalized), 4)
        except Exception as e:
            logger.warning(f"LightGBM prediction failed: {e}")
            return -1.0

    def predict_batch(
        self,
        candidates: List[Dict],
        job: Dict = None,
    ) -> List[float]:
        """Predict FPS scores for multiple candidates."""
        if not self.is_available:
            return [-1.0] * len(candidates)

        X = self.extract_features_batch(candidates, job)
        try:
            raw_scores = self._model.predict(X)
            normalized = 1.0 / (1.0 + np.exp(-raw_scores))
            return [round(float(s), 4) for s in normalized]
        except Exception as e:
            logger.warning(f"LightGBM batch prediction failed: {e}")
            return [-1.0] * len(candidates)

    # ── Feature Importance ─────────────────────────────────────────────────

    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importances (gain-based)."""
        if not self.is_available:
            return {}
        try:
            importances = self._model.feature_importance(importance_type="gain")
            total = sum(importances) or 1
            return {
                name: round(imp / total, 4)
                for name, imp in zip(self.FEATURE_NAMES, importances)
            }
        except Exception:
            return {}

    def get_status(self) -> Dict:
        """Return model status info."""
        return {
            "trained": self._is_trained,
            "available": self.is_available,
            "model_file": str(self.MODEL_FILE),
            "model_exists": self.MODEL_FILE.exists(),
            "feature_names": self.FEATURE_NAMES,
            "feature_importance": self.get_feature_importance(),
        }


# ── Module-level convenience ───────────────────────────────────────────────

_model_instance: Optional[RankingModel] = None

def get_ranking_model() -> RankingModel:
    global _model_instance
    if _model_instance is None:
        _model_instance = RankingModel()
    return _model_instance
