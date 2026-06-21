"""
CareerTrajectory AI — Core Scoring Engine
Implements FPS, Career Momentum, Semantic Fit, and Behavioral Evidence scoring.

Phase 2: Integrated with AI subsystems:
  - Sentence Transformers for semantic fit
  - ChromaDB for vector search
  - Live GitHub / LeetCode / Kaggle API collectors
  - LightGBM LambdaRank for ML-based FPS prediction
"""

import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Tuple
import math
from loguru import logger


# ─── Constants ────────────────────────────────────────────────────────────────

FPS_WEIGHTS = {
    "semantic_fit": 0.35,
    "career_momentum": 0.30,
    "behavioral_evidence": 0.20,
    "contextual_intelligence": 0.15,
}

SKILL_DOMAIN_MAP = {
    # ML / AI
    "pytorch": "ml_ai", "tensorflow": "ml_ai", "scikit-learn": "ml_ai",
    "nlp": "ml_ai", "transformers": "ml_ai", "langchain": "ml_ai",
    "huggingface": "ml_ai", "llm": "ml_ai", "rag": "ml_ai",
    "keras": "ml_ai", "xgboost": "ml_ai", "lightgbm": "ml_ai",
    # DevOps / Platform
    "kubernetes": "devops", "docker": "devops", "terraform": "devops",
    "aws": "devops", "gcp": "devops", "azure": "devops",
    "ci/cd": "devops", "ansible": "devops", "helm": "devops",
    "prometheus": "devops", "grafana": "devops", "argocd": "devops",
    # Full Stack / Frontend
    "react": "fullstack", "next.js": "fullstack", "typescript": "fullstack",
    "node.js": "fullstack", "graphql": "fullstack", "vue": "fullstack",
    "angular": "fullstack", "svelte": "fullstack",
    # Systems
    "rust": "systems", "c++": "systems", "ebpf": "systems",
    "linux kernel": "systems", "llvm": "systems", "wasm": "systems",
    # Data
    "python": "data", "pandas": "data", "sql": "data", "spark": "data",
    "dbt": "data", "airflow": "data", "kafka": "data",
}


# ─── Future Potential Score ────────────────────────────────────────────────────

def compute_fps(semantic_fit: float, career_momentum: float,
                behavioral_evidence: float, contextual_intelligence: float) -> float:
    """
    FPS = 0.35 × Semantic Fit
        + 0.30 × Career Momentum
        + 0.20 × Behavioral Evidence
        + 0.15 × Contextual Intelligence
    Range: [0.0, 1.0]
    """
    fps = (
        FPS_WEIGHTS["semantic_fit"] * semantic_fit
        + FPS_WEIGHTS["career_momentum"] * career_momentum
        + FPS_WEIGHTS["behavioral_evidence"] * behavioral_evidence
        + FPS_WEIGHTS["contextual_intelligence"] * contextual_intelligence
    )
    return round(min(max(fps, 0.0), 1.0), 4)


# ─── Career Momentum Engine ────────────────────────────────────────────────────

def compute_career_velocity(skill_history: List[Dict]) -> float:
    """
    Career Velocity = Rate of new skill acquisition over time.
    Measured as: skills_per_6_months (normalized to [0,1])
    """
    if not skill_history or len(skill_history) < 2:
        return 0.1

    # Parse dates and sort
    dated_skills = []
    for item in skill_history:
        try:
            dt = datetime.strptime(item["acquired"], "%Y-%m")
            dated_skills.append(dt)
        except Exception:
            continue

    if len(dated_skills) < 2:
        return 0.1

    dated_skills.sort()
    # Calculate time window in months
    earliest = dated_skills[0]
    latest = dated_skills[-1]
    months_elapsed = max((latest.year - earliest.year) * 12 + (latest.month - earliest.month), 1)

    # Skills per 6 months
    skills_per_6m = (len(dated_skills) / months_elapsed) * 6

    # Normalize: 1.0 = acquiring 3+ skills per 6 months
    velocity = min(skills_per_6m / 3.0, 1.0)
    return round(velocity, 4)


def compute_direction_alignment(skill_history: List[Dict], job_required_skills: List[str]) -> float:
    """
    Direction Alignment = How closely recent skill acquisitions match the job domain.
    Uses last 12 months of skill acquisition vs job skill domains.
    """
    if not skill_history or not job_required_skills:
        return 0.5

    # Determine job domain
    job_domain_counts = {}
    for skill in job_required_skills:
        domain = SKILL_DOMAIN_MAP.get(skill.lower(), "other")
        job_domain_counts[domain] = job_domain_counts.get(domain, 0) + 1
    primary_domain = max(job_domain_counts, key=job_domain_counts.get) if job_domain_counts else "other"

    # Look at recent skills (last 18 months)
    cutoff = datetime.now()
    cutoff = cutoff.replace(year=cutoff.year - 2)

    recent_skills = []
    for item in skill_history:
        try:
            dt = datetime.strptime(item["acquired"], "%Y-%m")
            if dt >= cutoff:
                recent_skills.append(item["skill"].lower())
        except Exception:
            continue

    if not recent_skills:
        # Fall back to all skills
        recent_skills = [item["skill"].lower() for item in skill_history]

    # Check how many recent skills match job domain
    job_required_lower = [s.lower() for s in job_required_skills]
    direct_matches = sum(1 for s in recent_skills if s in job_required_lower)
    domain_matches = sum(1 for s in recent_skills
                         if SKILL_DOMAIN_MAP.get(s, "other") == primary_domain)

    if not recent_skills:
        return 0.5

    alignment = (0.6 * direct_matches + 0.4 * domain_matches) / len(recent_skills)
    return round(min(alignment, 1.0), 4)


def compute_career_momentum(skill_history: List[Dict], job_required_skills: List[str]) -> float:
    """
    Career Momentum = Career Velocity × Direction Alignment
    Both factors amplify each other — fast learner going the right direction = high momentum.
    """
    velocity = compute_career_velocity(skill_history)
    alignment = compute_direction_alignment(skill_history, job_required_skills)

    # Geometric mean ensures both matter
    momentum = math.sqrt(velocity * alignment)

    # Boost for strong alignment even with moderate velocity
    if alignment > 0.8 and velocity > 0.6:
        momentum = min(momentum * 1.15, 1.0)

    return round(momentum, 4)


# ─── Semantic Fit Score ────────────────────────────────────────────────────────

def compute_semantic_fit(candidate_skills: List[str], job_required_skills: List[str],
                         job_good_to_have: List[str] = None) -> float:
    """
    Computes semantic fit using Sentence Transformers embeddings (Phase 2).
    Falls back to lexical + domain similarity if embeddings unavailable.
    """
    if not candidate_skills or not job_required_skills:
        return 0.0

    # ── Phase 2: Try Sentence Transformer embeddings first ──
    try:
        from backend.ai.embeddings import get_embedder
        embedder = get_embedder()
        if embedder.is_available:
            all_job_skills = list(job_required_skills) + list(job_good_to_have or [])
            semantic_score = embedder.compute_semantic_similarity(
                candidate_skills, all_job_skills
            )
            if semantic_score >= 0:  # -1 signals fallback needed
                # Blend with lexical overlap for robustness
                lexical_score = _lexical_semantic_fit(
                    candidate_skills, job_required_skills, job_good_to_have
                )
                # 70% embedding, 30% lexical
                blended = 0.70 * semantic_score + 0.30 * lexical_score
                return round(min(blended, 1.0), 4)
    except Exception as e:
        logger.debug(f"Embedding semantic fit failed, using lexical fallback: {e}")

    # ── Fallback: lexical + domain similarity ──
    return _lexical_semantic_fit(candidate_skills, job_required_skills, job_good_to_have)


def _lexical_semantic_fit(candidate_skills: List[str], job_required_skills: List[str],
                           job_good_to_have: List[str] = None) -> float:
    """Original lexical skill overlap + domain proximity scoring."""
    if not candidate_skills or not job_required_skills:
        return 0.0

    candidate_lower = set(s.lower() for s in candidate_skills)
    required_lower = set(s.lower() for s in job_required_skills)
    optional_lower = set(s.lower() for s in (job_good_to_have or []))

    # Direct matches
    required_matches = len(candidate_lower & required_lower)
    optional_matches = len(candidate_lower & optional_lower)

    # Domain proximity (partial credit for same-domain skills)
    candidate_domains = set(SKILL_DOMAIN_MAP.get(s, "other") for s in candidate_lower)
    required_domains = set(SKILL_DOMAIN_MAP.get(s, "other") for s in required_lower)
    domain_overlap = len(candidate_domains & required_domains)

    # Weighted score
    required_score = required_matches / max(len(required_lower), 1)
    optional_score = optional_matches / max(len(optional_lower), 1) if optional_lower else 0
    domain_score = domain_overlap / max(len(required_domains), 1)

    semantic_fit = (0.60 * required_score + 0.20 * optional_score + 0.20 * domain_score)
    return round(min(semantic_fit, 1.0), 4)


# ─── Behavioral Evidence Score ────────────────────────────────────────────────

def compute_behavioral_evidence(
    signals: Dict[str, Any],
    live_fetch: bool = False,
    github_username: str = "",
    leetcode_username: str = "",
    kaggle_username: str = "",
) -> float:
    """
    Aggregates behavioral evidence from GitHub, LeetCode, Kaggle, etc.
    Phase 2: Optionally fetches live data from APIs before scoring.
    Returns a score in [0, 1].
    """
    # ── Phase 2: Live API data refresh ──
    if live_fetch:
        signals = _refresh_live_signals(
            dict(signals), github_username, leetcode_username, kaggle_username
        )

    score_components = []

    # GitHub signals
    github = signals.get("github", {})
    if github:
        commit_score = min(github.get("commit_frequency", 0) / 25.0, 1.0)  # 25 commits/week = max
        stars_score = min(math.log1p(github.get("stars_earned", 0)) / math.log1p(5000), 1.0)
        streak_score = min(github.get("streak_days", 0) / 365.0, 1.0)
        repo_score = min(github.get("public_repos", 0) / 50.0, 1.0)
        followers_score = min(math.log1p(github.get("followers", 0)) / math.log1p(1000), 1.0)
        github_score = np.mean([commit_score, stars_score, streak_score, repo_score, followers_score])
        score_components.append(("github", github_score, 0.35))

    # LeetCode signals
    leetcode = signals.get("leetcode", {})
    if leetcode:
        problems_score = min(leetcode.get("problems_solved", 0) / 500.0, 1.0)
        rating_score = min((leetcode.get("contest_rating", 1200) - 1200) / 800.0, 1.0)
        rating_score = max(rating_score, 0)
        percentile_score = leetcode.get("contest_rank_percentile", 0) / 100.0
        lc_score = np.mean([problems_score, rating_score, percentile_score])
        score_components.append(("leetcode", lc_score, 0.20))

    # Kaggle signals
    kaggle = signals.get("kaggle", {})
    if kaggle:
        medals = kaggle.get("medals", {})
        medal_score = min(
            (medals.get("gold", 0) * 1.0 + medals.get("silver", 0) * 0.6 + medals.get("bronze", 0) * 0.3)
            / 5.0, 1.0
        )
        competition_score = min(kaggle.get("competitions", 0) / 20.0, 1.0)
        percentile_score = kaggle.get("ranking_percentile", 0) / 100.0
        kaggle_score = np.mean([medal_score, competition_score, percentile_score])
        score_components.append(("kaggle", kaggle_score, 0.20))

    # Codeforces signals
    cf = signals.get("codeforces", {})
    if cf:
        rating = cf.get("rating", 800)
        cf_score = min((rating - 800) / 1400.0, 1.0)  # 800=novice, 2200=grandmaster
        score_components.append(("codeforces", cf_score, 0.15))

    # Open Source Contributions
    oss = signals.get("open_source_contributions", 0)
    if oss:
        oss_score = min(math.log1p(oss) / math.log1p(100), 1.0)
        score_components.append(("oss", oss_score, 0.10))

    # Certifications
    certs = signals.get("certifications_count", 0)
    cert_score = min(certs / 5.0, 1.0)
    score_components.append(("certs", cert_score, 0.10))

    # Stack Overflow reputation
    so_rep = signals.get("stackoverflow_reputation", 0)
    if so_rep:
        so_score = min(math.log1p(so_rep) / math.log1p(10000), 1.0)
        score_components.append(("stackoverflow", so_score, 0.05))

    if not score_components:
        return 0.1

    # Weighted sum
    total_weight = sum(w for _, _, w in score_components)
    weighted_sum = sum(score * weight for _, score, weight in score_components)
    final_score = weighted_sum / total_weight

    return round(min(final_score, 1.0), 4)


def _refresh_live_signals(
    signals: Dict, github_username: str,
    leetcode_username: str, kaggle_username: str,
) -> Dict:
    """Fetch live data from GitHub/LeetCode/Kaggle and merge into signals."""
    # GitHub
    if github_username:
        try:
            from backend.ai.github_collector import get_github_collector
            collector = get_github_collector()
            if collector.is_available:
                live_gh = collector.compute_github_signals(github_username)
                if live_gh:
                    signals["github"] = live_gh
                    logger.debug(f"Live GitHub data for {github_username}: {live_gh.get('public_repos', 0)} repos")
        except Exception as e:
            logger.debug(f"Live GitHub fetch failed: {e}")

    # LeetCode
    if leetcode_username:
        try:
            from backend.ai.leetcode_collector import get_leetcode_collector
            collector = get_leetcode_collector()
            if collector.is_available:
                live_lc = collector.compute_leetcode_signals(leetcode_username)
                if live_lc:
                    signals["leetcode"] = live_lc
                    logger.debug(f"Live LeetCode data for {leetcode_username}: {live_lc.get('problems_solved', 0)} solved")
        except Exception as e:
            logger.debug(f"Live LeetCode fetch failed: {e}")

    # Kaggle
    if kaggle_username:
        try:
            from backend.ai.kaggle_collector import get_kaggle_collector
            collector = get_kaggle_collector()
            if collector.is_available:
                live_kg = collector.compute_kaggle_signals(kaggle_username)
                if live_kg:
                    signals["kaggle"] = live_kg
                    logger.debug(f"Live Kaggle data for {kaggle_username}")
        except Exception as e:
            logger.debug(f"Live Kaggle fetch failed: {e}")

    return signals


# ─── Contextual Intelligence Score ────────────────────────────────────────────

def compute_contextual_intelligence(candidate: Dict, job: Dict) -> float:
    """
    Contextual Intelligence captures:
    - Domain experience alignment
    - Level appropriateness
    - Education relevance
    - Career trajectory coherence
    """
    score = 0.5  # baseline

    # Years of experience vs job level
    yoe = candidate.get("years_of_experience", 0)
    job_level = job.get("level", "Mid").lower()

    level_yoe_map = {
        "junior": (0, 2), "entry": (0, 2),
        "mid": (2, 5), "mid-senior": (3, 7),
        "senior": (4, 8), "staff": (6, 12),
        "principal": (8, 20), "lead": (5, 15)
    }
    expected_range = level_yoe_map.get(job_level, (2, 6))
    if expected_range[0] <= yoe <= expected_range[1]:
        score += 0.2
    elif yoe > expected_range[1]:
        score += 0.1  # Overqualified but still valuable
    else:
        score -= 0.1  # Underqualified

    # Education alignment
    education = candidate.get("education", [])
    for edu in education:
        deg = edu.get("degree", "").lower()
        if any(kw in deg for kw in ["computer", "software", "cs", "engineering", "data", "mathematics"]):
            score += 0.15
            break
        elif any(kw in deg for kw in ["electronics", "electrical", "physics"]):
            score += 0.10
            break

    # Domain consistency
    all_skills = candidate.get("skills", {}).get("current", [])
    domain_check = compute_semantic_fit(all_skills, job.get("required_skills", []))
    score += 0.15 * domain_check

    return round(min(max(score, 0.0), 1.0), 4)


# ─── Skill Gap Simulator ───────────────────────────────────────────────────────

def simulate_skill_gap(candidate: Dict, job: Dict, new_skills: List[str]) -> Dict:
    """
    Predicts how FPS would improve if candidate acquires the specified new skills.
    """
    current_fps = candidate["scores"]["fps"]

    # Augment candidate skills
    augmented_skills = list(candidate["skills"]["current"]) + new_skills
    augmented_skill_history = list(candidate["skills"].get("history", []))

    # Add new skills to history (simulate 3 months from now)
    for skill in new_skills:
        augmented_skill_history.append({
            "skill": skill,
            "acquired": datetime.now().strftime("%Y-%m")
        })

    # Recompute scores
    new_semantic_fit = compute_semantic_fit(
        augmented_skills,
        job["required_skills"],
        job.get("good_to_have", [])
    )
    new_momentum = compute_career_momentum(augmented_skill_history, job["required_skills"])
    # Behavioral and contextual stay the same (can't simulate external validation)
    new_behavioral = candidate["scores"]["behavioral_evidence"]
    new_contextual = compute_contextual_intelligence(candidate, job)

    new_fps = compute_fps(new_semantic_fit, new_momentum, new_behavioral, new_contextual)

    improvement = round(new_fps - current_fps, 4)
    rank_improvement = int(improvement * 20)  # Rough rank change estimate

    return {
        "current_fps": current_fps,
        "predicted_fps": new_fps,
        "improvement": improvement,
        "estimated_rank_improvement": rank_improvement,
        "score_breakdown": {
            "semantic_fit": {"before": candidate["scores"]["semantic_fit"], "after": new_semantic_fit},
            "career_momentum": {"before": candidate["scores"]["career_momentum"], "after": new_momentum},
            "behavioral_evidence": {"before": new_behavioral, "after": new_behavioral},
            "contextual_intelligence": {"before": candidate["scores"]["contextual_intelligence"], "after": new_contextual},
        },
        "acquired_skills": new_skills,
        "recommendation": _generate_skill_recommendation(new_skills, improvement)
    }


def _generate_skill_recommendation(skills: List[str], improvement: float) -> str:
    if improvement > 0.1:
        return f"🚀 High Impact! Acquiring {', '.join(skills)} would significantly boost your FPS by {improvement:.2%}"
    elif improvement > 0.05:
        return f"✅ Moderate Impact. {', '.join(skills)} would improve your ranking meaningfully."
    else:
        return f"ℹ️ Low Impact. These skills have limited effect on your score for this specific role."


# ─── Hidden Gem Detection ─────────────────────────────────────────────────────

def detect_hidden_gems(candidates: List[Dict], threshold_yoe: int = 3,
                       momentum_threshold: float = 0.75,
                       behavioral_threshold: float = 0.70) -> List[Dict]:
    """
    Identifies candidates with:
    - Low years of experience (< threshold_yoe)
    - High career momentum (> momentum_threshold)
    - Strong behavioral evidence (> behavioral_threshold)
    but potentially lower semantic fit that traditional ATS would penalize.
    """
    gems = []
    for c in candidates:
        yoe = c.get("years_of_experience", 99)
        momentum = c["scores"].get("career_momentum", 0)
        behavioral = c["scores"].get("behavioral_evidence", 0)
        semantic = c["scores"].get("semantic_fit", 0)

        is_gem = (
            yoe <= threshold_yoe
            and momentum >= momentum_threshold
            and behavioral >= behavioral_threshold
            and semantic < 0.85  # Traditional ATS would rank them lower
        )
        if is_gem:
            c["hidden_gem"] = True
            c["gem_reason"] = _explain_gem(c, yoe, momentum, behavioral, semantic)
            gems.append(c)
        else:
            c["hidden_gem"] = False
            c.pop("gem_reason", None)

    return gems


def _explain_gem(c: Dict, yoe: float, momentum: float, behavioral: float, semantic: float) -> str:
    return (
        f"{c['name']} has only {yoe} year(s) of experience but shows exceptional "
        f"career momentum ({momentum:.0%}) and strong behavioral evidence ({behavioral:.0%}). "
        f"Traditional ATS would penalize low experience — CareerTrajectory AI sees the trajectory."
    )


# ─── Ranking Pipeline ─────────────────────────────────────────────────────────

def rank_candidates(candidates: List[Dict], job: Dict, use_ml: bool = False) -> List[Dict]:
    """
    Full ranking pipeline: computes all scores and sorts by FPS.
    Phase 2: Optionally uses LightGBM ML ranking and indexes into ChromaDB.
    """
    ranked = []
    for c in candidates:
        # Compute fresh scores against this specific job
        all_skills = c["skills"]["current"] + c["skills"].get("learning", [])
        semantic_fit = compute_semantic_fit(
            all_skills, job["required_skills"], job.get("good_to_have", [])
        )
        momentum = compute_career_momentum(
            c["skills"].get("history", []), job["required_skills"]
        )
        behavioral = compute_behavioral_evidence(c.get("behavioral_signals", {}))
        contextual = compute_contextual_intelligence(c, job)
        fps = compute_fps(semantic_fit, momentum, behavioral, contextual)

        c_copy = dict(c)
        c_copy["scores"] = {
            "semantic_fit": semantic_fit,
            "career_momentum": momentum,
            "behavioral_evidence": behavioral,
            "contextual_intelligence": contextual,
            "fps": fps
        }
        ranked.append(c_copy)

    # ── Phase 2: ML-based FPS override ──
    if use_ml:
        try:
            from backend.ai.ranking_model import get_ranking_model
            model = get_ranking_model()
            if model.is_available:
                ml_scores = model.predict_batch(ranked, job)
                for c, ml_fps in zip(ranked, ml_scores):
                    if ml_fps >= 0:
                        c["scores"]["fps_formula"] = c["scores"]["fps"]  # Keep original
                        c["scores"]["fps"] = ml_fps
                        c["scores"]["ranking_method"] = "lightgbm"
                    else:
                        c["scores"]["ranking_method"] = "formula"
                logger.debug(f"ML ranking applied to {len(ranked)} candidates")
        except Exception as e:
            logger.debug(f"ML ranking failed, using formula: {e}")

    ranked.sort(key=lambda x: x["scores"]["fps"], reverse=True)
    for i, c in enumerate(ranked):
        c["rank"] = i + 1

    # ── Phase 2: Index into ChromaDB for vector search ──
    try:
        from backend.ai.vector_store import get_vector_store
        store = get_vector_store()
        if store.is_available:
            store.upsert_candidates_batch(ranked)
    except Exception as e:
        logger.debug(f"ChromaDB indexing skipped: {e}")

    return ranked


# ─── SHAP-style Explanations ───────────────────────────────────────────────────

def generate_shap_values(candidate: Dict) -> Dict:
    """
    Generates SHAP-style feature attributions for the FPS score.
    Shows contribution of each component.
    """
    scores = candidate["scores"]
    fps = scores["fps"]

    contributions = {
        "Semantic Fit": round(FPS_WEIGHTS["semantic_fit"] * scores["semantic_fit"], 4),
        "Career Momentum": round(FPS_WEIGHTS["career_momentum"] * scores["career_momentum"], 4),
        "Behavioral Evidence": round(FPS_WEIGHTS["behavioral_evidence"] * scores["behavioral_evidence"], 4),
        "Contextual Intelligence": round(FPS_WEIGHTS["contextual_intelligence"] * scores["contextual_intelligence"], 4),
    }

    baseline = 0.5  # Average candidate baseline
    shap_values = {k: round(v - baseline * w, 4)
                   for (k, v), w in zip(contributions.items(), FPS_WEIGHTS.values())}

    return {
        "fps": fps,
        "baseline": baseline,
        "contributions": contributions,
        "shap_values": shap_values,
        "explanation": _generate_natural_language_explanation(candidate, contributions),
        "counterfactuals": _generate_counterfactuals(candidate),
    }


def _generate_natural_language_explanation(candidate: Dict, contributions: Dict) -> str:
    name = candidate["name"]
    top_factors = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
    top_2 = top_factors[:2]

    strengths = []
    weaknesses = []

    if candidate["scores"]["career_momentum"] > 0.85:
        strengths.append("exceptional career momentum and rapid skill acquisition")
    if candidate["scores"]["behavioral_evidence"] > 0.85:
        strengths.append("verified high-quality GitHub contributions and community engagement")
    if candidate["scores"]["semantic_fit"] > 0.80:
        strengths.append("strong alignment with role requirements")

    if candidate["scores"]["semantic_fit"] < 0.60:
        weaknesses.append("partial skill gap in required technologies")
    if candidate["scores"]["behavioral_evidence"] < 0.50:
        weaknesses.append("limited verified external behavioral evidence")
    if candidate["scores"]["career_momentum"] < 0.50:
        weaknesses.append("slower skill acquisition velocity in the target domain")

    strength_str = " and ".join(strengths) if strengths else "solid overall profile"
    weakness_str = "; ".join(weaknesses) if weaknesses else "no critical gaps identified"

    return (
        f"**{name}** ranks here primarily due to {strength_str}. "
        f"The highest contributing factor is **{top_2[0][0]}** "
        f"(+{top_2[0][1]:.3f} to FPS), followed by **{top_2[1][0]}** "
        f"(+{top_2[1][1]:.3f}). Areas to note: {weakness_str}."
    )


def _generate_counterfactuals(candidate: Dict) -> List[str]:
    """Counterfactual explanations: what would change the ranking."""
    counterfactuals = []
    scores = candidate["scores"]

    if scores["behavioral_evidence"] < 0.75:
        delta = round((0.80 - scores["behavioral_evidence"]) * FPS_WEIGHTS["behavioral_evidence"], 3)
        counterfactuals.append(
            f"Increasing GitHub activity and open-source contributions could improve FPS by ~{delta:.3f}"
        )

    if scores["semantic_fit"] < 0.75:
        delta = round((0.85 - scores["semantic_fit"]) * FPS_WEIGHTS["semantic_fit"], 3)
        counterfactuals.append(
            f"Adding 2-3 missing required skills could improve FPS by ~{delta:.3f} — use Skill Gap Simulator"
        )

    if scores["career_momentum"] < 0.80:
        delta = round((0.85 - scores["career_momentum"]) * FPS_WEIGHTS["career_momentum"], 3)
        counterfactuals.append(
            f"Accelerating skill acquisition in the target domain could improve FPS by ~{delta:.3f}"
        )

    return counterfactuals


# ─── Future Role Prediction ───────────────────────────────────────────────────

ROLE_TRAJECTORIES = {
    "ml_ai": {
        "high_momentum": {
            "1_year": "Senior ML Engineer",
            "3_years": "Staff ML Engineer / Tech Lead",
            "5_years": "Principal ML Engineer / Research Lead"
        },
        "moderate": {
            "1_year": "ML Engineer",
            "3_years": "Senior ML Engineer",
            "5_years": "ML Lead / ML Manager"
        }
    },
    "devops": {
        "high_momentum": {
            "1_year": "Senior DevOps / SRE",
            "3_years": "Staff Platform Engineer",
            "5_years": "Principal Infrastructure Architect"
        },
        "moderate": {
            "1_year": "DevOps Engineer",
            "3_years": "Senior DevOps / Platform Lead",
            "5_years": "Engineering Manager (Platform)"
        }
    },
    "fullstack": {
        "high_momentum": {
            "1_year": "Senior Full Stack Engineer",
            "3_years": "Staff Engineer / Frontend Architect",
            "5_years": "Principal Engineer / VP Engineering"
        },
        "moderate": {
            "1_year": "Full Stack Engineer",
            "3_years": "Senior Engineer",
            "5_years": "Tech Lead / Engineering Manager"
        }
    },
    "systems": {
        "high_momentum": {
            "1_year": "Systems Software Engineer",
            "3_years": "Senior Systems Engineer",
            "5_years": "Principal Systems Architect"
        },
        "moderate": {
            "1_year": "Software Engineer",
            "3_years": "Systems Engineer",
            "5_years": "Senior Systems Engineer"
        }
    },
    "data": {
        "high_momentum": {
            "1_year": "Data Scientist",
            "3_years": "Senior Data Scientist",
            "5_years": "Lead Data Scientist / ML Platform Engineer"
        },
        "moderate": {
            "1_year": "Junior Data Scientist",
            "3_years": "Data Scientist",
            "5_years": "Senior Data Analyst / BI Lead"
        }
    }
}


def predict_future_role(candidate: Dict) -> Dict:
    """Predicts the candidate's future role trajectory."""
    current_skills = [s.lower() for s in candidate["skills"]["current"]]

    # Determine primary domain
    domain_counts = {}
    for skill in current_skills:
        domain = SKILL_DOMAIN_MAP.get(skill, "other")
        domain_counts[domain] = domain_counts.get(domain, 0) + 1

    primary_domain = max(domain_counts, key=domain_counts.get) if domain_counts else "fullstack"
    if primary_domain == "other":
        primary_domain = "fullstack"  # Default

    momentum = candidate["scores"].get("career_momentum", 0.5)
    tier = "high_momentum" if momentum >= 0.75 else "moderate"

    trajectory = ROLE_TRAJECTORIES.get(primary_domain, ROLE_TRAJECTORIES["fullstack"])[tier]

    leadership_probability = min(
        0.3 + momentum * 0.4 + candidate["scores"].get("behavioral_evidence", 0) * 0.3, 1.0
    )

    return {
        "primary_domain": primary_domain.replace("_", " / ").title(),
        "trajectory": trajectory,
        "leadership_probability": round(leadership_probability, 2),
        "momentum_tier": tier.replace("_", " ").title(),
        "confidence": round(min(0.5 + momentum * 0.5, 0.95), 2)
    }
