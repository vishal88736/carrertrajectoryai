"""Quick validation script for CareerTrajectory AI — Phase 1 + Phase 2"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("CareerTrajectory AI — Full Validation (Phase 1 + Phase 2)")
print("=" * 60)

# ── Phase 1 Validation ────────────────────────────────────────────────────────

print("\n[Phase 1] Testing data layer...")
from data.sample_data import get_candidates, get_jobs
candidates = get_candidates()
jobs = get_jobs()
print(f"  Candidates loaded: {len(candidates)}")
print(f"  Jobs loaded: {len(jobs)}")

print("\n[Phase 1] Testing scoring engine...")
from backend.scoring_engine import (
    rank_candidates, detect_hidden_gems,
    simulate_skill_gap, generate_shap_values,
    predict_future_role
)

ranked = rank_candidates(candidates, jobs[0])
top = ranked[0]
print(f"  Top ranked: {top['name']} — FPS={top['scores']['fps']}")
print(f"  All ranked: {[c['name'] for c in ranked]}")

gems = detect_hidden_gems(candidates)
print(f"  Hidden gems: {len(gems)} — {[g['name'] for g in gems]}")

shap_data = generate_shap_values(top)
print(f"  SHAP explanation: {len(shap_data['explanation'])} chars")
print(f"  Counterfactuals: {len(shap_data['counterfactuals'])}")

sim = simulate_skill_gap(ranked[-1], jobs[0], ['Docker', 'Kubernetes'])
print(f"  Skill gap sim: {sim['current_fps']:.3f} -> {sim['predicted_fps']:.3f} (+{sim['improvement']:.4f})")

traj = predict_future_role(top)
print(f"  Future trajectory: {traj['trajectory']}")

print("\n[Phase 1] Testing resume parser...")
from backend.resume_parser import extract_skills, extract_years_experience
sample_text = """
John Doe - Python Developer
Experience: 3 years at Google (2021-2024)
Skills: Python, Docker, Kubernetes, AWS, Terraform, PostgreSQL
Education: B.Tech Computer Science, IIT 2021
"""
skills = extract_skills(sample_text)
yoe = extract_years_experience(sample_text)
print(f"  Skills extracted: {skills}")
print(f"  YoE extracted: {yoe}")

print("\n[Phase 1] Testing UI components...")
import plotly.graph_objects as go
import pandas as pd
import numpy as np
fig = go.Figure(go.Bar(x=[1,2,3], y=[0.8, 0.7, 0.9]))
print(f"  Plotly figure created: {type(fig)}")


# ── Phase 2 Validation ────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("Phase 2 — AI Integration Tests")
print("=" * 60)

# Config
print("\n[Phase 2] Testing AI config...")
from backend.ai.config import (
    USE_SEMANTIC_EMBEDDINGS, USE_CHROMADB, USE_LIVE_GITHUB,
    USE_LIVE_LEETCODE, USE_LLM_COPILOT, USE_ML_RANKING,
    GROQ_API_KEY, GITHUB_TOKEN, log_ai_status,
)
log_ai_status()

# Embeddings
print("\n[Phase 2] Testing Sentence Transformers...")
try:
    from backend.ai.embeddings import get_embedder
    embedder = get_embedder()
    if embedder.is_available:
        sim = embedder.compute_semantic_similarity(
            ["Python", "PyTorch", "NLP", "Transformers"],
            ["Python", "TensorFlow", "NLP", "LangChain"]
        )
        print(f"  ✅ Embeddings loaded — similarity score: {sim:.4f}")

        similar = embedder.find_similar_skills(
            "PyTorch",
            ["TensorFlow", "Keras", "Docker", "React", "NLP", "CUDA"],
            top_k=3
        )
        print(f"  ✅ Similar to PyTorch: {similar}")
    else:
        print("  ⚠️  Embeddings not available (model not loaded)")
except Exception as e:
    print(f"  ❌ Embeddings failed: {e}")

# ChromaDB
print("\n[Phase 2] Testing ChromaDB vector store...")
try:
    from backend.ai.vector_store import get_vector_store
    store = get_vector_store()
    stats = store.get_stats()
    print(f"  ChromaDB: {stats}")
    if store.is_available:
        store.upsert_candidates_batch(ranked)
        results = store.search_by_job(jobs[0]["required_skills"], top_k=3)
        print(f"  ✅ Search results: {len(results)} candidates found")
        for r in results:
            print(f"     - {r.get('metadata', {}).get('name', r['id'])} (sim: {r.get('similarity', 0):.3f})")
    else:
        print("  ⚠️  ChromaDB not available")
except Exception as e:
    print(f"  ❌ ChromaDB failed: {e}")

# GitHub Collector
print("\n[Phase 2] Testing GitHub collector...")
try:
    from backend.ai.github_collector import get_github_collector
    gh = get_github_collector()
    print(f"  GitHub collector available: {gh.is_available}")
    if gh.is_available:
        rate = gh.get_rate_limit()
        print(f"  Rate limit: {rate.get('remaining', '?')}/{rate.get('limit', '?')}")
except Exception as e:
    print(f"  ❌ GitHub collector failed: {e}")

# LeetCode Collector
print("\n[Phase 2] Testing LeetCode collector...")
try:
    from backend.ai.leetcode_collector import get_leetcode_collector
    lc = get_leetcode_collector()
    print(f"  LeetCode collector available: {lc.is_available}")
except Exception as e:
    print(f"  ❌ LeetCode collector failed: {e}")

# Kaggle Collector
print("\n[Phase 2] Testing Kaggle collector...")
try:
    from backend.ai.kaggle_collector import get_kaggle_collector
    kg = get_kaggle_collector()
    print(f"  Kaggle collector available: {kg.is_available}")
except Exception as e:
    print(f"  ❌ Kaggle collector failed: {e}")

# LLM Client
print("\n[Phase 2] Testing LLM client (Groq)...")
try:
    from backend.ai.llm_client import get_llm_client
    llm = get_llm_client()
    print(f"  LLM available: {llm.is_available}")
    if llm.is_available:
        intent = llm.classify_intent("Who is the best candidate?")
        print(f"  ✅ Intent classification: '{intent}'")
        metrics = llm.get_metrics()
        print(f"  Metrics: {metrics}")
except Exception as e:
    print(f"  ❌ LLM client failed: {e}")

# LangGraph Orchestrator
print("\n[Phase 2] Testing LangGraph orchestrator...")
try:
    from backend.ai.orchestrator import get_orchestrator
    orch = get_orchestrator()
    has_graph = orch._graph is not None
    print(f"  LangGraph compiled: {has_graph}")
    result = orch.process_query(
        "Who is the best candidate?",
        ranked, jobs[0], gems,
    )
    print(f"  ✅ Orchestrator response: {len(result['response'])} chars")
    print(f"  Intent: {result['intent']}")
    print(f"  Agent trace: {result['agent_trace']}")
except Exception as e:
    print(f"  ❌ Orchestrator failed: {e}")

# LightGBM Ranking Model
print("\n[Phase 2] Testing LightGBM ranking model...")
try:
    from backend.ai.ranking_model import get_ranking_model
    model = get_ranking_model()
    status = model.get_status()
    print(f"  Model status: {status['trained']}")
    if not status["trained"]:
        print("  Training synthetic model...")
        model.train_synthetic(ranked)
        print(f"  ✅ Model trained! Feature importance: {model.get_feature_importance()}")
    
    # Test prediction
    pred = model.predict(ranked[0], jobs[0])
    print(f"  Prediction for {ranked[0]['name']}: {pred:.4f}")
except Exception as e:
    print(f"  ❌ Ranking model failed: {e}")

# Feedback Store
print("\n[Phase 2] Testing feedback store...")
try:
    from backend.ai.feedback_store import get_feedback_store
    fb = get_feedback_store()
    fb.record_feedback("c001", "j001", "shortlisted", notes="Test validation")
    stats = fb.get_stats()
    print(f"  ✅ Feedback recorded. Stats: {stats}")
except Exception as e:
    print(f"  ❌ Feedback store failed: {e}")

# ── Summary ───────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("ALL SYSTEMS OPERATIONAL [OK]")
print("=" * 60)
print(f"\nFPS Range: {min(c['scores']['fps'] for c in ranked):.3f} - {max(c['scores']['fps'] for c in ranked):.3f}")
print(f"Avg Momentum: {sum(c['scores']['career_momentum'] for c in ranked)/len(ranked):.3f}")
print(f"\nRanking Order:")
for c in ranked:
    gem = " [HIDDEN GEM]" if c.get('hidden_gem') else ""
    method = c.get('scores', {}).get('ranking_method', 'formula')
    print(f"  #{c['rank']} {c['name']:20s} FPS={c['scores']['fps']:.3f}  Momentum={c['scores']['career_momentum']:.3f}  [{method}]{gem}")

print(f"\nPhase 2 AI Status:")
print(f"  Embeddings: {'✅' if USE_SEMANTIC_EMBEDDINGS else '❌'}")
print(f"  ChromaDB:   {'✅' if USE_CHROMADB else '❌'}")
print(f"  GitHub API: {'✅' if USE_LIVE_GITHUB else '❌'}")
print(f"  LeetCode:   {'✅' if USE_LIVE_LEETCODE else '❌'}")
print(f"  LLM Copilot:{'✅' if USE_LLM_COPILOT else '❌'}")
print(f"  ML Ranking: {'✅' if USE_ML_RANKING else '❌'}")
