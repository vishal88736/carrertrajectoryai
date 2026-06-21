"""
CareerTrajectory AI — Semantic Skill Embeddings
Uses Sentence Transformers (all-MiniLM-L6-v2) for real embedding-based skill matching.
Replaces lexical set-intersection with cosine similarity in embedding space.
"""

import numpy as np
from typing import List, Tuple, Optional, Dict
from loguru import logger
import threading

from backend.ai.config import EMBEDDING_MODEL_NAME, USE_SEMANTIC_EMBEDDINGS


class SkillEmbedder:
    """
    Singleton skill embedding service.
    Lazy-loads the SentenceTransformer model on first use to avoid
    reloading on every Streamlit rerun.
    """

    _instance: Optional["SkillEmbedder"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "SkillEmbedder":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._model = None
        self._cache: Dict[str, np.ndarray] = {}
        self._initialized = True

    # ── Lazy Model Loading ─────────────────────────────────────────────────

    def _ensure_model(self):
        """Load model on first access."""
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model: {EMBEDDING_MODEL_NAME}")
            self._model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info(f"✅ SentenceTransformer loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load SentenceTransformer: {e}")
            self._model = None

    @property
    def is_available(self) -> bool:
        """Check if model can be loaded."""
        if not USE_SEMANTIC_EMBEDDINGS:
            return False
        self._ensure_model()
        return self._model is not None

    # ── Core Embedding Functions ───────────────────────────────────────────

    def encode_text(self, text: str) -> Optional[np.ndarray]:
        """Encode a single text string to an embedding vector."""
        if text in self._cache:
            return self._cache[text]
        self._ensure_model()
        if self._model is None:
            return None
        try:
            embedding = self._model.encode(text, normalize_embeddings=True)
            self._cache[text] = embedding
            return embedding
        except Exception as e:
            logger.warning(f"Encoding failed for '{text[:50]}': {e}")
            return None

    def encode_skills(self, skills: List[str]) -> Optional[np.ndarray]:
        """
        Encode a list of skills into a single embedding vector (mean-pooled).
        Each skill is encoded individually and averaged.
        """
        if not skills:
            return None
        self._ensure_model()
        if self._model is None:
            return None

        try:
            # Encode each skill with context
            skill_texts = [f"technical skill: {s}" for s in skills]
            embeddings = self._model.encode(skill_texts, normalize_embeddings=True)
            # Mean-pool all skill embeddings into one vector
            mean_embedding = np.mean(embeddings, axis=0)
            # Normalize the mean
            norm = np.linalg.norm(mean_embedding)
            if norm > 0:
                mean_embedding = mean_embedding / norm
            return mean_embedding
        except Exception as e:
            logger.warning(f"Skill encoding failed: {e}")
            return None

    def encode_skills_matrix(self, skills: List[str]) -> Optional[np.ndarray]:
        """Encode each skill separately, returning a matrix (N x dim)."""
        if not skills:
            return None
        self._ensure_model()
        if self._model is None:
            return None
        try:
            skill_texts = [f"technical skill: {s}" for s in skills]
            return self._model.encode(skill_texts, normalize_embeddings=True)
        except Exception as e:
            logger.warning(f"Skill matrix encoding failed: {e}")
            return None

    # ── Similarity Functions ───────────────────────────────────────────────

    def compute_semantic_similarity(
        self,
        candidate_skills: List[str],
        job_skills: List[str]
    ) -> float:
        """
        Compute semantic similarity between candidate skills and job skills.
        Uses a combination of:
          1. Mean-pooled cosine similarity (overall alignment)
          2. Max-match similarity (best individual skill matches)
        Returns a score in [0.0, 1.0].
        """
        if not candidate_skills or not job_skills:
            return 0.0

        if not self.is_available:
            return -1.0  # Signal to caller to use fallback

        try:
            # Encode both sets
            cand_matrix = self.encode_skills_matrix(candidate_skills)
            job_matrix = self.encode_skills_matrix(job_skills)

            if cand_matrix is None or job_matrix is None:
                return -1.0

            # 1. Mean-pooled similarity (how aligned are the overall profiles)
            cand_mean = np.mean(cand_matrix, axis=0)
            job_mean = np.mean(job_matrix, axis=0)
            cand_mean = cand_mean / (np.linalg.norm(cand_mean) + 1e-9)
            job_mean = job_mean / (np.linalg.norm(job_mean) + 1e-9)
            overall_sim = float(np.dot(cand_mean, job_mean))

            # 2. Max-match similarity (for each job skill, find best matching candidate skill)
            # This rewards having at least *some* skill close to each requirement
            sim_matrix = cand_matrix @ job_matrix.T  # (N_cand x N_job)
            max_matches = sim_matrix.max(axis=0)  # best candidate skill for each job skill
            match_score = float(np.mean(max_matches))

            # Weighted combination
            semantic_fit = 0.4 * overall_sim + 0.6 * match_score

            # Clamp to [0, 1]
            return round(max(0.0, min(1.0, semantic_fit)), 4)

        except Exception as e:
            logger.warning(f"Semantic similarity computation failed: {e}")
            return -1.0

    def find_similar_skills(
        self,
        skill: str,
        all_skills: List[str],
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find skills most similar to the given skill from a skill pool.
        Returns list of (skill_name, similarity_score) tuples.
        """
        if not self.is_available or not all_skills:
            return []

        try:
            query_emb = self.encode_text(f"technical skill: {skill}")
            if query_emb is None:
                return []

            pool_texts = [f"technical skill: {s}" for s in all_skills]
            pool_embs = self._model.encode(pool_texts, normalize_embeddings=True)

            similarities = pool_embs @ query_emb
            top_indices = np.argsort(similarities)[::-1][:top_k]

            results = []
            for idx in top_indices:
                if all_skills[idx].lower() != skill.lower():
                    results.append((all_skills[idx], float(similarities[idx])))

            return results[:top_k]

        except Exception as e:
            logger.warning(f"Similar skill search failed: {e}")
            return []

    def get_embedding_dim(self) -> int:
        """Return the embedding dimension."""
        self._ensure_model()
        if self._model is None:
            return 384  # default for all-MiniLM-L6-v2
        return self._model.get_sentence_embedding_dimension()

    def clear_cache(self):
        """Clear the embedding cache."""
        self._cache.clear()


# ── Module-level convenience functions ─────────────────────────────────────

def get_embedder() -> SkillEmbedder:
    """Get the singleton SkillEmbedder instance."""
    return SkillEmbedder()
