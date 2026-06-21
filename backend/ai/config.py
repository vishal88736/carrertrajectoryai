"""
CareerTrajectory AI — Central AI Configuration
Loads API keys, model paths, and feature flags from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load .env from project root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ─── API Keys ─────────────────────────────────────────────────────────────────

GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
KAGGLE_USERNAME: str = os.getenv("KAGGLE_USERNAME", "")
KAGGLE_KEY: str = os.getenv("KAGGLE_KEY", "")

# ─── Model Configuration ─────────────────────────────────────────────────────

EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
LLM_MODEL_NAME: str = "llama-3.3-70b-versatile"       # Groq model ID
LLM_FALLBACK_MODEL: str = "llama-3.1-8b-instant"      # Smaller fallback
LLM_MAX_TOKENS: int = 1024
LLM_TEMPERATURE: float = 0.7

# ─── Paths ────────────────────────────────────────────────────────────────────

MODELS_DIR: Path = _PROJECT_ROOT / "backend" / "models"
CHROMADB_DIR: Path = _PROJECT_ROOT / "data" / "chromadb"
FEEDBACK_DIR: Path = _PROJECT_ROOT / "data" / "feedback"

# Ensure directories exist
MODELS_DIR.mkdir(parents=True, exist_ok=True)
CHROMADB_DIR.mkdir(parents=True, exist_ok=True)
FEEDBACK_DIR.mkdir(parents=True, exist_ok=True)

# ─── ChromaDB ─────────────────────────────────────────────────────────────────

CHROMA_COLLECTION_CANDIDATES = "candidate_skills"
CHROMA_COLLECTION_JOBS = "job_requirements"

# ─── Feature Flags (graceful degradation) ─────────────────────────────────────

def _flag(key: str, default: bool = True) -> bool:
    val = os.getenv(key, str(default)).lower()
    return val in ("true", "1", "yes")

USE_SEMANTIC_EMBEDDINGS: bool = _flag("CT_USE_SEMANTIC_EMBEDDINGS", True)
USE_CHROMADB: bool = _flag("CT_USE_CHROMADB", True)
USE_LIVE_GITHUB: bool = _flag("CT_USE_LIVE_GITHUB", bool(GITHUB_TOKEN))
USE_LIVE_LEETCODE: bool = _flag("CT_USE_LIVE_LEETCODE", True)
USE_LIVE_KAGGLE: bool = _flag("CT_USE_LIVE_KAGGLE", bool(KAGGLE_KEY))
USE_LLM_COPILOT: bool = _flag("CT_USE_LLM_COPILOT", bool(GROQ_API_KEY))
USE_ML_RANKING: bool = _flag("CT_USE_ML_RANKING", True)

# ─── Logging ──────────────────────────────────────────────────────────────────

def log_ai_status():
    """Logs the status of all AI subsystems."""
    logger.info("═══ CareerTrajectory AI — Phase 2 Status ═══")
    logger.info(f"  Semantic Embeddings : {'✅ ON' if USE_SEMANTIC_EMBEDDINGS else '❌ OFF'} (model={EMBEDDING_MODEL_NAME})")
    logger.info(f"  ChromaDB Vector DB  : {'✅ ON' if USE_CHROMADB else '❌ OFF'} (path={CHROMADB_DIR})")
    logger.info(f"  Live GitHub API     : {'✅ ON' if USE_LIVE_GITHUB else '❌ OFF (no GITHUB_TOKEN)'}")
    logger.info(f"  Live LeetCode API   : {'✅ ON' if USE_LIVE_LEETCODE else '❌ OFF'}")
    logger.info(f"  Live Kaggle API     : {'✅ ON' if USE_LIVE_KAGGLE else '❌ OFF (no KAGGLE_KEY)'}")
    logger.info(f"  LLM Copilot (Groq)  : {'✅ ON' if USE_LLM_COPILOT else '❌ OFF (no GROQ_API_KEY)'}")
    logger.info(f"  ML Ranking (LightGBM): {'✅ ON' if USE_ML_RANKING else '❌ OFF'}")
    logger.info("═════════════════════════════════════════════")
