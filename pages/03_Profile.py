"""
CareerTrajectory AI — Page 3: Candidate Profile
Deep-dive profile with career timeline, SHAP explanations, and future trajectory.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

st.set_page_config(page_title="Profile · CareerTrajectory AI", page_icon="👤", layout="wide")

from ui.components import (inject_css, render_page_header, render_fps_gauge,
                            render_score_bars, render_skills_tags, render_shap_waterfall,
                            render_radar_chart, render_momentum_timeline, get_score_color,
                            get_score_label)
from data.sample_data import get_candidates, get_jobs, get_job_by_id, get_candidate_by_id
from backend.scoring_engine import (rank_candidates, generate_shap_values,
                                    predict_future_role, compute_career_momentum,
                                    compute_career_velocity, compute_direction_alignment)
from backend.resume_parser import build_career_timeline

inject_css()

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# ── State ─────────────────────────────────────────────────────────────────────
if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = "j001"
if "selected_candidate_id" not in st.session_state:
    st.session_state.selected_candidate_id = "c001"
if "custom_candidates" not in st.session_state:
    st.session_state.custom_candidates = []

all_candidates = get_candidates() + st.session_state.custom_candidates
job = get_job_by_id(st.session_state.selected_job_id)
ranked = rank_candidates(all_candidates, job)

# Candidate selector in sidebar-ish expander
with st.expander("🔄 Switch Candidate", expanded=False):
    candidate_options = {c["id"]: f"#{c.get('rank','?')} · {c['name']} (FPS: {c['scores']['fps']:.3f})"
                         for c in ranked}
    selected_id = st.selectbox(
        "Select Candidate",
        options=list(candidate_options.keys()),
        format_func=lambda x: candidate_options[x],
        index=0 if not st.session_state.selected_candidate_id else
              next((i for i, c in enumerate(ranked) if c["id"] == st.session_state.selected_candidate_id), 0)
    )
    st.session_state.selected_candidate_id = selected_id

# Get selected candidate with fresh scores
if not ranked:
    st.markdown("""
    <div class="info-box" style="text-align:center; margin-top:2rem;">
        <div style="font-size:2rem; margin-bottom:0.5rem;">📥</div>
        <strong>No candidates available.</strong>
        <div style="color:#64748b; margin-top:0.3rem;">Upload a resume or JSON to view a profile, or enable Sample Data in the sidebar.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

cand = next((c for c in ranked if c["id"] == st.session_state.selected_candidate_id), ranked[0])
scores = cand["scores"]
fps = scores["fps"]
color = get_score_color(fps)

# ── Page Header ───────────────────────────────────────────────────────────────
render_page_header(
    cand["name"],
    f"Deep Intelligence Profile · {job['title']} @ {job['company']}",
    "👤"
)

# ── Top section: Avatar + FPS + Key Stats ──────────────────────────────────────
hero_col, gauge_col, stats_col = st.columns([2, 1.2, 1.8])

with hero_col:
    gem_badge = '<span style="background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#000;font-size:0.72rem;font-weight:700;padding:0.2rem 0.6rem;border-radius:999px;">💎 Hidden Gem</span>' if cand.get('hidden_gem') else ''
    
    st.markdown(f"""
    <div class="ct-card" style="padding:2rem;">
        <div style="display:flex;align-items:center;gap:1.2rem;margin-bottom:1.5rem;">
            <div style="width:70px;height:70px;border-radius:50%;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:1.8rem;font-weight:900;color:white;box-shadow:0 0 20px rgba(99,102,241,0.4);">
                {cand['name'][0]}
            </div>
            <div>
                <div style="font-size:1.4rem;font-weight:800;color:#e2e8f0;">{cand['name']}</div>
                <div style="color:#64748b;font-size:0.85rem;margin-top:3px;">📍 {cand.get('location','N/A')}</div>
                <div style="margin-top:5px;">{gem_badge}</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.7rem;">
            <div style="background:#0f0f1a;border-radius:8px;padding:0.7rem;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;">Experience</div>
                <div style="font-weight:700;color:#e2e8f0;margin-top:2px;">{cand.get('years_of_experience',0)} Years</div>
            </div>
            <div style="background:#0f0f1a;border-radius:8px;padding:0.7rem;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;">Rank</div>
                <div style="font-weight:700;color:#6366f1;margin-top:2px;">#{cand.get('rank','?')} of {len(ranked)}</div>
            </div>
            <div style="background:#0f0f1a;border-radius:8px;padding:0.7rem;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;">Skills</div>
                <div style="font-weight:700;color:#e2e8f0;margin-top:2px;">{len(cand['skills']['current'])} Current</div>
            </div>
            <div style="background:#0f0f1a;border-radius:8px;padding:0.7rem;">
                <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.08em;">Certifications</div>
                <div style="font-weight:700;color:#e2e8f0;margin-top:2px;">{len(cand.get('certifications',[]))}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Education
    for edu in cand.get("education", [])[:2]:
        st.markdown(f"""
        <div style="background:#1a1a2e;border:1px solid #334155;border-radius:10px;
             padding:0.7rem 1rem;margin-top:0.5rem;display:flex;align-items:center;gap:0.7rem;">
            <span style="font-size:1.2rem;">🎓</span>
            <div>
                <div style="font-size:0.85rem;font-weight:600;color:#e2e8f0;">{edu.get('degree','')}</div>
                <div style="font-size:0.75rem;color:#64748b;">{edu.get('institution','')} · {edu.get('year','')}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with gauge_col:
    st.markdown(f"""
    <div class="ct-card" style="text-align:center;padding-top:1rem;">
        <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;
             letter-spacing:0.1em;margin-bottom:0.5rem;">Future Potential Score</div>
    </div>
    """, unsafe_allow_html=True)
    render_fps_gauge(fps, f"FPS: {fps:.3f}")
    st.markdown(f"""
    <div style="text-align:center;margin-top:0.3rem;">
        <span style="color:{color};font-weight:700;font-size:1rem;">{get_score_label(fps)}</span>
    </div>
    """, unsafe_allow_html=True)

with stats_col:
    st.markdown('<div class="ct-card" style="padding:1rem;">', unsafe_allow_html=True)
    render_score_bars(scores)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🚀 Career Momentum", "🔍 SHAP Analysis", "🔬 Behavioral Evidence",
    "🔮 Future Trajectory", "📋 Full Profile"
])

# ── Tab 1: Career Momentum ────────────────────────────────────────────────────
with tab1:
    st.markdown("### 🚀 Career Momentum Engine Analysis")

    m1, m2, m3 = st.columns(3)
    velocity = compute_career_velocity(cand["skills"].get("history", []))
    alignment = compute_direction_alignment(cand["skills"].get("history", []), job["required_skills"])
    momentum = scores["career_momentum"]

    with m1:
        v_color = get_score_color(velocity)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.3rem;margin-bottom:0.3rem;">⚡</div>
            <div style="font-size:2rem;font-weight:900;color:{v_color};
                 font-family:'JetBrains Mono',monospace;">{velocity:.2f}</div>
            <div class="metric-label">Career Velocity</div>
            <div style="color:#64748b;font-size:0.72rem;margin-top:0.3rem;">Skills per 6 months</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        a_color = get_score_color(alignment)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.3rem;margin-bottom:0.3rem;">🧭</div>
            <div style="font-size:2rem;font-weight:900;color:{a_color};
                 font-family:'JetBrains Mono',monospace;">{alignment:.2f}</div>
            <div class="metric-label">Direction Alignment</div>
            <div style="color:#64748b;font-size:0.72rem;margin-top:0.3rem;">Match to job domain</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        mm_color = get_score_color(momentum)
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size:1.3rem;margin-bottom:0.3rem;">🚀</div>
            <div style="font-size:2rem;font-weight:900;color:{mm_color};
                 font-family:'JetBrains Mono',monospace;">{momentum:.2f}</div>
            <div class="metric-label">Career Momentum</div>
            <div style="color:#64748b;font-size:0.72rem;margin-top:0.3rem;">√(Velocity × Alignment)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#1a1a2e;border:1px solid #334155;border-radius:12px;
         padding:1rem;margin:1rem 0;">
        <strong style="color:#a5b4fc;">📐 Formula:</strong>
        <span style="font-family:'JetBrains Mono',monospace;color:#e2e8f0;"> 
        Career Momentum = √(Career Velocity × Direction Alignment)</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📈 Skill Acquisition Timeline")
    render_momentum_timeline(cand["skills"].get("history", []))

    # Skill comparison
    st.markdown("#### 🎯 Skill Match Analysis")
    sc1, sc2 = st.columns(2)
    with sc1:
        st.markdown(f"**✅ Matched Required Skills** ({len(set(s.lower() for s in cand['skills']['current']) & set(s.lower() for s in job['required_skills']))})")
        matched = [s for s in cand["skills"]["current"] if s.lower() in [r.lower() for r in job["required_skills"]]]
        render_skills_tags(matched if matched else ["None matched"], tag_type="current", job_required=job["required_skills"])
    with sc2:
        st.markdown(f"**❌ Missing Required Skills**")
        missing = [s for s in job["required_skills"] if s.lower() not in [c.lower() for c in cand["skills"]["current"]]]
        if missing:
            render_skills_tags(missing, tag_type="current")
        else:
            st.success("All required skills present!")

    sc3, sc4 = st.columns(2)
    with sc3:
        st.markdown("**🟡 Currently Learning**")
        render_skills_tags(cand["skills"].get("learning", [])[:6], tag_type="learning")
    with sc4:
        st.markdown("**🌟 Good-to-Have Matches**")
        good_matched = [s for s in cand["skills"]["current"] if s.lower() in [g.lower() for g in job.get("good_to_have", [])]]
        render_skills_tags(good_matched if good_matched else ["None matched"])


# ── Tab 2: SHAP Analysis ──────────────────────────────────────────────────────
with tab2:
    st.markdown("### 🔍 SHAP Explainability Analysis")
    st.markdown("""
    <div class="info-box">
        <strong>Explainability Agent</strong> uses SHAP (SHapley Additive exPlanations) to show
        the contribution of each scoring component to the final FPS. This makes every ranking decision 
        fully transparent and auditable.
    </div>
    """, unsafe_allow_html=True)

    shap_data = generate_shap_values(cand)

    shap_col1, shap_col2 = st.columns([1.5, 1])

    with shap_col1:
        st.markdown("#### 📊 SHAP Waterfall Chart")
        render_shap_waterfall(shap_data)

        st.markdown("#### 💬 AI-Generated Explanation")
        st.markdown(f"""
        <div class="success-box">
            {shap_data['explanation']}
        </div>
        """, unsafe_allow_html=True)

    with shap_col2:
        st.markdown("#### 🕸️ Capability Radar")
        render_radar_chart(scores, cand["name"])

        st.markdown("#### 💡 Counterfactual Insights")
        st.markdown("""
        <div style="color:#64748b;font-size:0.82rem;margin-bottom:0.5rem;">
            What would change this candidate's ranking?
        </div>
        """, unsafe_allow_html=True)
        if shap_data.get("counterfactuals"):
            for cf in shap_data["counterfactuals"]:
                st.markdown(f"""
                <div style="background:#1a1a2e;border:1px solid #334155;border-left:3px solid #f59e0b;
                     border-radius:8px;padding:0.7rem 0.9rem;margin-bottom:0.5rem;
                     font-size:0.83rem;color:#94a3b8;">
                    💡 {cf}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant counterfactuals — this candidate is well-optimized for this role.")

        # Component breakdown table
        st.markdown("#### 📋 Contribution Breakdown")
        breakdown = shap_data.get("contributions", {})
        for key, val in breakdown.items():
            weight = {"Semantic Fit": 0.35, "Career Momentum": 0.30,
                      "Behavioral Evidence": 0.20, "Contextual Intelligence": 0.15}.get(key, 0)
            raw_score = val / weight if weight else 0
            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:center;
                 padding:0.4rem 0;border-bottom:1px solid #1e293b;">
                <span style="color:#94a3b8;font-size:0.82rem;">{key}</span>
                <span style="color:{get_score_color(raw_score)};font-weight:700;
                     font-family:'JetBrains Mono',monospace;font-size:0.85rem;">
                    +{val:.4f}
                </span>
            </div>
            """, unsafe_allow_html=True)


# ── Tab 3: Behavioral Evidence ────────────────────────────────────────────────
with tab3:
    st.markdown("### 🔬 Behavioral Evidence Analysis")
    st.markdown("""
    <div class="info-box">
        <strong>Behavior Validation Agent</strong> collects and validates signals from external platforms.
        This provides objective evidence of skills beyond what's written on a resume.
    </div>
    """, unsafe_allow_html=True)

    signals = cand.get("behavioral_signals", {})

    if not signals:
        st.info("No behavioral signals available for this candidate. In production, signals would be fetched via APIs.")
    else:
        b_cols = st.columns(4)
        platform_cards = []

        if "github" in signals:
            gh = signals["github"]
            platform_cards.append({
                "icon": "🐙", "name": "GitHub", "col": 0,
                "metrics": [
                    ("Commit Freq", f"{gh.get('commit_frequency', 0):.1f}/week"),
                    ("Stars Earned", f"{gh.get('stars_earned', 0):,}"),
                    ("Streak", f"{gh.get('streak_days', 0)} days"),
                    ("Repos", str(gh.get('public_repos', 0))),
                    ("Followers", f"{gh.get('followers', 0):,}"),
                ]
            })

        if "leetcode" in signals:
            lc = signals["leetcode"]
            platform_cards.append({
                "icon": "💻", "name": "LeetCode", "col": 1,
                "metrics": [
                    ("Problems", f"{lc.get('problems_solved', 0)}"),
                    ("Rating", f"{lc.get('contest_rating', 0):,}"),
                    ("Percentile", f"{lc.get('contest_rank_percentile', 0)}%"),
                ]
            })

        if "kaggle" in signals:
            kg = signals["kaggle"]
            medals = kg.get("medals", {})
            platform_cards.append({
                "icon": "🏅", "name": "Kaggle", "col": 2,
                "metrics": [
                    ("Competitions", str(kg.get("competitions", 0))),
                    ("Gold Medals", f"🥇 {medals.get('gold', 0)}"),
                    ("Silver", f"🥈 {medals.get('silver', 0)}"),
                    ("Percentile", f"{kg.get('ranking_percentile', 0)}%"),
                ]
            })

        if "codeforces" in signals:
            cf = signals["codeforces"]
            platform_cards.append({
                "icon": "⚔️", "name": "Codeforces", "col": 3,
                "metrics": [
                    ("Rating", f"{cf.get('rating', 0):,}"),
                    ("Rank", cf.get("rank", "N/A").title()),
                    ("Contests", str(cf.get("contests_participated", 0))),
                ]
            })

        # Render platform cards
        b_cols = st.columns(max(len(platform_cards), 1))
        for i, card in enumerate(platform_cards):
            with b_cols[i]:
                metrics_html = "".join([
                    f"""<div style="display:flex;justify-content:space-between;padding:0.4rem 0;
                         border-bottom:1px solid #1e293b;">
                         <span style="color:#64748b;font-size:0.78rem;">{k}</span>
                         <span style="color:#e2e8f0;font-weight:700;font-size:0.82rem;
                              font-family:'JetBrains Mono',monospace;">{v}</span>
                         </div>"""
                    for k, v in card["metrics"]
                ])
                st.markdown(f"""
                <div class="ct-card" style="padding:1.2rem;">
                    <div style="text-align:center;margin-bottom:1rem;">
                        <div style="font-size:1.8rem;">{card['icon']}</div>
                        <div style="font-weight:700;color:#a5b4fc;">{card['name']}</div>
                    </div>
                    {metrics_html}
                </div>
                """, unsafe_allow_html=True)

        # OSS and Certifications
        st.markdown("<br>", unsafe_allow_html=True)
        oss_col, cert_col = st.columns(2)
        with oss_col:
            oss = signals.get("open_source_contributions", 0)
            st.markdown(f"""
            <div class="ct-card">
                <div style="font-size:1.3rem;margin-bottom:0.5rem;">🌐</div>
                <div style="font-weight:700;color:#a5b4fc;margin-bottom:0.3rem;">Open Source Contributions</div>
                <div style="font-size:2rem;font-weight:900;color:#10b981;
                     font-family:'JetBrains Mono',monospace;">{oss}</div>
                <div style="color:#64748b;font-size:0.8rem;">PR/Issue contributions across repos</div>
            </div>
            """, unsafe_allow_html=True)

        with cert_col:
            cert_count = signals.get("certifications_count", 0)
            st.markdown(f"""
            <div class="ct-card">
                <div style="font-size:1.3rem;margin-bottom:0.5rem;">🏆</div>
                <div style="font-weight:700;color:#a5b4fc;margin-bottom:0.3rem;">Certifications</div>
                <div style="font-size:2rem;font-weight:900;color:#f59e0b;
                     font-family:'JetBrains Mono',monospace;">{cert_count}</div>
                <div style="color:#64748b;font-size:0.8rem;">Verified industry certifications</div>
            </div>
            """, unsafe_allow_html=True)


# ── Tab 4: Future Trajectory ──────────────────────────────────────────────────
with tab4:
    st.markdown("### 🔮 Future Role Prediction Engine")
    st.markdown("""
    <div class="info-box">
        <strong>Future Potential Predictor</strong> uses Career Momentum, behavioral signals,
        and domain expertise to predict likely career trajectory at 1, 3, and 5 year horizons.
    </div>
    """, unsafe_allow_html=True)

    trajectory = predict_future_role(cand)

    traj_col1, traj_col2 = st.columns([1.5, 1])

    with traj_col1:
        st.markdown(f"""
        <div class="ct-card" style="padding:2rem;">
            <div style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem;">
                Primary Domain: <strong style="color:#a5b4fc;">{trajectory['primary_domain']}</strong>
                · Momentum: <strong style="color:{'#10b981' if trajectory['momentum_tier']=='High Momentum' else '#f59e0b'};">{trajectory['momentum_tier']}</strong>
            </div>
            <div style="position:relative;padding-left:2rem;">
                <div style="position:relative;padding-bottom:1.5rem;">
                    <div style="position:absolute;left:-1.5rem;top:0.3rem;width:12px;height:12px;border-radius:50%;background:#6366f1;box-shadow:0 0 0 3px rgba(99,102,241,0.2);"></div>
                    <div style="position:absolute;left:-0.95rem;top:1rem;width:2px;height:100%;background:#334155;"></div>
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;">Now</div>
                    <div style="font-weight:700;color:#e2e8f0;margin-top:2px;">{cand.get('experience', [{'title': 'Engineer'}])[-1]['title'] if cand.get('experience') else 'Software Engineer'}</div>
                </div>
                <div style="position:relative;padding-bottom:1.5rem;">
                    <div style="position:absolute;left:-1.5rem;top:0.3rem;width:12px;height:12px;border-radius:50%;background:#10b981;box-shadow:0 0 0 3px rgba(16,185,129,0.2);"></div>
                    <div style="position:absolute;left:-0.95rem;top:1rem;width:2px;height:100%;background:#334155;"></div>
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;">1 Year</div>
                    <div style="font-weight:700;color:#10b981;margin-top:2px;font-size:1.05rem;">{trajectory['trajectory']['1_year']}</div>
                </div>
                <div style="position:relative;padding-bottom:1.5rem;">
                    <div style="position:absolute;left:-1.5rem;top:0.3rem;width:14px;height:14px;border-radius:50%;background:#8b5cf6;box-shadow:0 0 0 3px rgba(139,92,246,0.2);"></div>
                    <div style="position:absolute;left:-0.95rem;top:1rem;width:2px;height:100%;background:#334155;"></div>
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;">3 Years</div>
                    <div style="font-weight:700;color:#8b5cf6;margin-top:2px;font-size:1.1rem;">{trajectory['trajectory']['3_years']}</div>
                </div>
                <div style="position:relative;">
                    <div style="position:absolute;left:-1.5rem;top:0.3rem;width:16px;height:16px;border-radius:50%;background:#f59e0b;box-shadow:0 0 0 4px rgba(245,158,11,0.25);animation:pulse-glow 2s infinite;"></div>
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;">5 Years</div>
                    <div style="font-weight:800;color:#f59e0b;margin-top:2px;font-size:1.15rem;">{trajectory['trajectory']['5_years']}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with traj_col2:
        # Leadership probability
        lp = trajectory["leadership_probability"]
        lp_color = get_score_color(lp)
        st.markdown(f"""
        <div class="ct-card" style="text-align:center;padding:2rem;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">👑</div>
            <div style="color:#64748b;font-size:0.78rem;text-transform:uppercase;
                 letter-spacing:0.08em;margin-bottom:0.5rem;">Leadership Potential</div>
            <div style="font-size:3rem;font-weight:900;color:{lp_color};
                 font-family:'JetBrains Mono',monospace;">{lp*100:.0f}%</div>
            <div style="color:#64748b;font-size:0.78rem;margin-top:0.5rem;">
                Probability of reaching<br>leadership role in 5 years
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="ct-card" style="text-align:center;padding:1.5rem;">
            <div style="font-size:1.8rem;margin-bottom:0.5rem;">🎯</div>
            <div style="color:#64748b;font-size:0.78rem;text-transform:uppercase;
                 letter-spacing:0.08em;margin-bottom:0.5rem;">Prediction Confidence</div>
            <div style="font-size:2.5rem;font-weight:900;color:#6366f1;
                 font-family:'JetBrains Mono',monospace;">{trajectory['confidence']*100:.0f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Predicted trajectory of similar candidates
    if cand.get("predicted_trajectory"):
        st.markdown("#### 🔮 AI-Predicted Career Path")
        pred = cand["predicted_trajectory"]
        path_cols = st.columns(3)
        for col, (horizon, role) in zip(path_cols, pred.items()):
            with col:
                color_map = {"1_year": "#10b981", "3_years": "#8b5cf6", "5_years": "#f59e0b"}
                c_color = color_map.get(horizon, "#6366f1")
                label = horizon.replace("_", " ").title()
                st.markdown(f"""
                <div style="background:#1a1a2e;border:1px solid #334155;border-radius:12px;
                     padding:1.2rem;text-align:center;border-top:3px solid {c_color};">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;
                         letter-spacing:0.08em;margin-bottom:0.4rem;">{label}</div>
                    <div style="font-weight:700;color:{c_color};font-size:0.9rem;">{role}</div>
                </div>
                """, unsafe_allow_html=True)


# ── Tab 5: Full Profile ───────────────────────────────────────────────────────
with tab5:
    st.markdown("### 📋 Complete Candidate Profile")

    p1, p2 = st.columns(2)

    with p1:
        st.markdown("#### 💼 Work Experience")
        for exp in cand.get("experience", []):
            end_date = exp.get("end", "Present")
            st.markdown(f"""
            <div style="background:#1a1a2e;border:1px solid #334155;border-radius:10px;
                 padding:1rem;margin-bottom:0.7rem;border-left:3px solid #6366f1;">
                <div style="font-weight:700;color:#e2e8f0;">{exp.get('title','')}</div>
                <div style="color:#a5b4fc;font-size:0.85rem;margin:2px 0;">
                    🏢 {exp.get('company','')}
                </div>
                <div style="color:#64748b;font-size:0.75rem;">
                    📅 {exp.get('start','')} → {end_date}
                </div>
                <div style="color:#94a3b8;font-size:0.82rem;margin-top:0.5rem;line-height:1.5;">
                    {exp.get('description','')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with p2:
        st.markdown("#### 🏆 Certifications")
        for cert in cand.get("certifications", []):
            st.markdown(f"""
            <div style="background:#1a1a2e;border:1px solid #334155;border-radius:10px;
                 padding:0.8rem 1rem;margin-bottom:0.5rem;display:flex;gap:0.8rem;
                 border-left:3px solid #f59e0b;">
                <span style="font-size:1.2rem;">🏅</span>
                <div>
                    <div style="font-weight:600;color:#e2e8f0;font-size:0.88rem;">{cert.get('name','')}</div>
                    <div style="color:#64748b;font-size:0.75rem;">{cert.get('issuer','')} · {cert.get('date','')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### 🚀 Projects")
        for proj in cand.get("projects", []):
            stars = proj.get("stars", 0)
            st.markdown(f"""
            <div style="background:#1a1a2e;border:1px solid #334155;border-radius:10px;
                 padding:1rem;margin-bottom:0.7rem;border-left:3px solid #10b981;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div style="font-weight:700;color:#e2e8f0;font-size:0.9rem;">🛠️ {proj.get('name','')}</div>
                    {f'<div style="color:#f59e0b;font-size:0.8rem;">⭐ {stars:,}</div>' if stars else ''}
                </div>
                <div style="color:#94a3b8;font-size:0.82rem;margin-top:0.4rem;line-height:1.4;">
                    {proj.get('description','')}
                </div>
                <div style="margin-top:0.5rem;">
                    {''.join(f'<span class="skill-tag" style="font-size:0.72rem;">{s}</span>' for s in proj.get('skills',[]))}
                </div>
            </div>
            """, unsafe_allow_html=True)
