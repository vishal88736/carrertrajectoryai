"""
CareerTrajectory AI — ChromaDB Vector Store
Persistent vector database for candidate skill profiles.
Enables semantic search: "find candidates like X" and "best match for job Y".
"""

import hashlib
from typing import List, Dict, Optional, Any
from loguru import logger
import threading

from backend.ai.config import (
    CHROMADB_DIR, USE_CHROMADB,
    CHROMA_COLLECTION_CANDIDATES, CHROMA_COLLECTION_JOBS,
)
from backend.ai.embeddings import get_embedder


class CandidateVectorStore:
    """
    ChromaDB-backed vector store for candidate skill profiles.
    Singleton pattern — shared across Streamlit reruns.
    """

    _instance: Optional["CandidateVectorStore"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "CandidateVectorStore":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._client = None
        self._candidate_collection = None
        self._job_collection = None
        self._initialized = True

    # ── Lazy Init ──────────────────────────────────────────────────────────

    def _ensure_client(self):
        """Initialize ChromaDB client and collections on first use."""
        if self._client is not None:
            return
        if not USE_CHROMADB:
            return

        try:
            import chromadb
            from chromadb.config import Settings

            self._client = chromadb.PersistentClient(
                path=str(CHROMADB_DIR),
                settings=Settings(anonymized_telemetry=False),
            )

            embedder = get_embedder()
            dim = embedder.get_embedding_dim()

            # Create or get collections
            self._candidate_collection = self._client.get_or_create_collection(
                name=CHROMA_COLLECTION_CANDIDATES,
                metadata={"hnsw:space": "cosine", "dimension": dim},
            )
            self._job_collection = self._client.get_or_create_collection(
                name=CHROMA_COLLECTION_JOBS,
                metadata={"hnsw:space": "cosine", "dimension": dim},
            )

            logger.info(
                f"✅ ChromaDB initialized — "
                f"candidates: {self._candidate_collection.count()}, "
                f"jobs: {self._job_collection.count()}"
            )
        except Exception as e:
            logger.error(f"❌ ChromaDB initialization failed: {e}")
            self._client = None

    @property
    def is_available(self) -> bool:
        if not USE_CHROMADB:
            return False
        self._ensure_client()
        return self._client is not None

    # ── Candidate Operations ───────────────────────────────────────────────

    def upsert_candidate(
        self,
        candidate_id: str,
        skills: List[str],
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Store or update a candidate's skill embedding in ChromaDB."""
        if not self.is_available:
            return

        embedder = get_embedder()
        embedding = embedder.encode_skills(skills)
        if embedding is None:
            return

        safe_metadata = {}
        if metadata:
            for k, v in metadata.items():
                if isinstance(v, (str, int, float, bool)):
                    safe_metadata[k] = v
                elif isinstance(v, list):
                    safe_metadata[k] = ", ".join(str(x) for x in v[:20])

        safe_metadata["skills_text"] = ", ".join(skills[:30])
        safe_metadata["skills_count"] = len(skills)

        try:
            self._candidate_collection.upsert(
                ids=[candidate_id],
                embeddings=[embedding.tolist()],
                metadatas=[safe_metadata],
                documents=[f"Candidate skills: {', '.join(skills)}"],
            )
        except Exception as e:
            logger.warning(f"ChromaDB upsert failed for {candidate_id}: {e}")

    def upsert_candidates_batch(self, candidates: List[Dict]):
        """Batch upsert multiple candidates."""
        if not self.is_available:
            return

        embedder = get_embedder()
        ids, embeddings, metadatas, documents = [], [], [], []

        for c in candidates:
            cid = c.get("id", "")
            skills = c.get("skills", {}).get("current", [])
            if not cid or not skills:
                continue

            emb = embedder.encode_skills(skills)
            if emb is None:
                continue

            ids.append(cid)
            embeddings.append(emb.tolist())
            metadatas.append({
                "name": c.get("name", ""),
                "skills_text": ", ".join(skills[:30]),
                "skills_count": len(skills),
                "yoe": c.get("years_of_experience", 0),
                "fps": c.get("scores", {}).get("fps", 0.0),
            })
            documents.append(f"Candidate {c.get('name','')}: {', '.join(skills)}")

        if ids:
            try:
                self._candidate_collection.upsert(
                    ids=ids,
                    embeddings=embeddings,
                    metadatas=metadatas,
                    documents=documents,
                )
                logger.info(f"ChromaDB: batch upserted {len(ids)} candidates")
            except Exception as e:
                logger.warning(f"ChromaDB batch upsert failed: {e}")

    def search_similar_candidates(
        self,
        query_skills: List[str],
        top_k: int = 10,
        filter_metadata: Optional[Dict] = None,
    ) -> List[Dict]:
        """Find candidates with similar skill profiles."""
        if not self.is_available:
            return []

        embedder = get_embedder()
        query_embedding = embedder.encode_skills(query_skills)
        if query_embedding is None:
            return []

        try:
            where = filter_metadata if filter_metadata else None
            results = self._candidate_collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                where=where,
                include=["metadatas", "distances", "documents"],
            )

            candidates = []
            if results and results["ids"]:
                for i, cid in enumerate(results["ids"][0]):
                    candidates.append({
                        "id": cid,
                        "similarity": 1.0 - (results["distances"][0][i] if results["distances"] else 0),
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    })
            return candidates

        except Exception as e:
            logger.warning(f"ChromaDB search failed: {e}")
            return []

    def search_by_job(
        self,
        job_required_skills: List[str],
        top_k: int = 20,
    ) -> List[Dict]:
        """Find candidates most semantically aligned with a job's requirements."""
        return self.search_similar_candidates(job_required_skills, top_k=top_k)

    # ── Stats ──────────────────────────────────────────────────────────────

    def get_stats(self) -> Dict:
        """Return ChromaDB collection statistics."""
        if not self.is_available:
            return {"available": False, "candidates": 0, "jobs": 0}

        return {
            "available": True,
            "candidates": self._candidate_collection.count(),
            "jobs": self._job_collection.count(),
            "path": str(CHROMADB_DIR),
        }

    def clear_all(self):
        """Delete all data from collections."""
        if not self.is_available:
            return
        try:
            self._client.delete_collection(CHROMA_COLLECTION_CANDIDATES)
            self._client.delete_collection(CHROMA_COLLECTION_JOBS)
            self._candidate_collection = None
            self._job_collection = None
            self._client = None
            self._initialized = False
            CandidateVectorStore._instance = None
            logger.info("ChromaDB collections cleared")
        except Exception as e:
            logger.warning(f"ChromaDB clear failed: {e}")


# ── Module-level convenience ───────────────────────────────────────────────

def get_vector_store() -> CandidateVectorStore:
    """Get the singleton CandidateVectorStore instance."""
    return CandidateVectorStore()
