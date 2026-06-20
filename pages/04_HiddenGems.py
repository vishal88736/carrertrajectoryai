"""
CareerTrajectory AI — Page 4: Hidden Gems
Discover high-potential candidates that traditional ATS systems miss.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

st.set_page_config(page_title="Hidden Gems · CareerTrajectory AI", page_icon="💎", layout="wide")

from ui.components import (inject_css, render_page_header, render_score_bars,
                            render_fps_gauge, render_skills_tags, get_score_color,
                            render_metric_row)
from data.sample_data import get_candidates, get_job_by_id
from backend.scoring_engine import rank_candidates, detect_hidden_gems, generate_shap_values

inject_css()

import plotly.graph_objects as go

if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = "j001"
if "custom_candidates" not in st.session_state:
    st.session_state.custom_candidates = []

candidates = get_candidates() + st.session_state.custom_candidates
job = get_job_by_id(st.session_state.selected_job_id)
ranked = rank_candidates(candidates, job)

# Configurable thresholds
render_page_header("Hidden Gem Detection Engine", 
    "Discover high-momentum, high-potential candidates that traditional ATS systems would miss.",
    "💎")

st.markdown("""
<div style="background:linear-gradient(135deg,rgba(245,158,11,0.1),rgba(251,191,36,0.05));
     border:1px solid rgba(245,158,11,0.3);border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;">
    <h3 style="color:#fbbf24;margin:0 0 0.5rem;">💡 What is a Hidden Gem?</h3>
    <p style="color:#94a3b8;margin:0;font-size:0.9rem;line-height:1.6;">
        A <strong style="color:#fcd34d;">Hidden Gem</strong> is a candidate with 
        <em>low years of experience</em> but <em>exceptional career momentum</em> and 
        <em>strong behavioral evidence</em>. Traditional ATS systems rank them low due to 
        experience requirements — but CareerTrajectory AI identifies their trajectory and 
        predicts they will outperform more "experienced" candidates in 12–18 months.
    </p>
</div>
""", unsafe_allow_html=True)

# Threshold Controls
st.markdown("### ⚙️ Detection Sensitivity")
t1, t2, t3 = st.columns(3)
with t1:
    yoe_threshold = st.slider("Max Experience (Years)", 1, 6, 3,
                               help="Candidates with fewer years of experience than this threshold")
with t2:
    momentum_threshold = st.slider("Min Career Momentum", 0.5, 0.95, 0.75, 0.05,
                                   help="Minimum career momentum score required")
with t3:
    behavioral_threshold = st.slider("Min Behavioral Evidence", 0.5, 0.95, 0.70, 0.05,
                                     help="Minimum behavioral evidence score required")

gems = detect_hidden_gems(ranked, yoe_threshold, momentum_threshold, behavioral_threshold)

# Metrics
st.markdown("<br>", unsafe_allow_html=True)
render_metric_row([
    {"label": "Hidden Gems Found", "value": str(len(gems)), "icon": "💎"},
    {"label": "Would Be Missed by ATS", "value": f"{len([g for g in gems if g['scores']['semantic_fit'] < 0.75])}", "icon": "⚠️"},
    {"label": "Avg Momentum Score", "value": f"{sum(g['scores']['career_momentum'] for g in gems)/max(len(gems),1):.2f}" if gems else "N/A", "icon": "🚀"},
    {"label": "Top Gem FPS", "value": f"{max((g['scores']['fps'] for g in gems), default=0):.3f}", "icon": "🏆"},
])

st.markdown("<br>", unsafe_allow_html=True)

if not gems:
    st.markdown("""
    <div style="text-align:center;padding:3rem;background:#1a1a2e;border-radius:16px;border:1px solid #334155;">
        <div style="font-size:3rem;margin-bottom:1rem;">🔍</div>
        <div style="color:#64748b;font-size:1rem;">No hidden gems found with current thresholds.</div>
        <div style="color:#475569;font-size:0.85rem;margin-top:0.5rem;">
            Try lowering the momentum or behavioral thresholds to discover more candidates.
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Visual comparison: ATS rank vs CareerTrajectory rank
    st.markdown("### 📊 ATS vs CareerTrajectory AI Ranking Comparison")
    
    # Simulate what ATS would give (just semantic fit + experience)
    def ats_rank(c):
        yoe_bonus = min(c.get("years_of_experience", 0) / 10.0, 1.0) * 0.4
        semantic = c["scores"]["semantic_fit"] * 0.6
        return yoe_bonus + semantic

    all_ranked_ats = sorted(ranked, key=ats_rank, reverse=True)
    ats_positions = {c["id"]: i+1 for i, c in enumerate(all_ranked_ats)}

    comp_data = []
    for c in gems:
        ats_pos = ats_positions.get(c["id"], len(ranked))
        ct_pos = c.get("rank", len(ranked))
        comp_data.append({
            "name": c["name"],
            "ats_rank": ats_pos,
            "ct_rank": ct_pos,
            "improvement": ats_pos - ct_pos,
            "fps": c["scores"]["fps"],
            "momentum": c["scores"]["career_momentum"]
        })

    if comp_data:
        import pandas as pd
        df_comp = pd.DataFrame(comp_data)
        
        fig = go.Figure()
        for _, row in df_comp.iterrows():
            fig.add_trace(go.Scatter(
                x=[0, 1],
                y=[row["ats_rank"], row["ct_rank"]],
                mode="lines+markers+text",
                line=dict(color="#f59e0b", width=2),
                marker=dict(size=[12, 14], color=["#ef4444", "#10b981"]),
                text=[f"ATS: #{row['ats_rank']}", f"CT: #{row['ct_rank']}"],
                textposition=["middle left", "middle right"],
                textfont=dict(color="#e2e8f0", size=11),
                name=row["name"],
                showlegend=True,
            ))
        
        fig.update_layout(
            height=300,
            margin=dict(l=60, r=60, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1a2e",
            xaxis=dict(
                ticktext=["Traditional ATS", "CareerTrajectory AI"],
                tickvals=[0, 1],
                range=[-0.3, 1.3],
                gridcolor="#334155",
                tickfont=dict(color="#e2e8f0", size=13),
            ),
            yaxis=dict(
                autorange="reversed",
                gridcolor="#334155",
                tickfont=dict(color="#94a3b8"),
                title=dict(text="Rank (lower = better)", font=dict(color="#64748b")),
            ),
            legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
            font=dict(family="Inter"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Gem Cards
    st.markdown("### 💎 Hidden Gems — Detailed Analysis")

    for gem in gems:
        scores = gem["scores"]
        fps = scores["fps"]
        color = get_score_color(fps)
        ats_pos = ats_positions.get(gem["id"], len(ranked))
        ct_pos = gem.get("rank", len(ranked))
        rank_diff = ats_pos - ct_pos

        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a1a2e,#16213e);
             border:2px solid #f59e0b;border-radius:20px;padding:1.5rem;
             margin-bottom:1.5rem;box-shadow:0 0 30px rgba(245,158,11,0.15);
             position:relative;overflow:hidden;">
            <div style="position:absolute;top:1rem;right:1rem;
                 background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#000;
                 font-weight:800;font-size:0.75rem;padding:0.3rem 0.8rem;
                 border-radius:999px;">💎 HIDDEN GEM</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            gem_cols = st.columns([2, 1.5, 1.5])
            
            with gem_cols[0]:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem;">
                    <div style="width:56px;height:56px;border-radius:50%;
                        background:linear-gradient(135deg,#f59e0b,#fbbf24);
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.4rem;font-weight:900;color:#000;">
                        {gem['name'][0]}
                    </div>
                    <div>
                        <div style="font-weight:800;font-size:1.1rem;color:#e2e8f0;">{gem['name']}</div>
                        <div style="color:#64748b;font-size:0.82rem;">
                            📍 {gem.get('location','N/A')} · 💼 {gem.get('years_of_experience',0)} yrs exp
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gem reason
                reason = gem.get("gem_reason", "")
                if reason:
                    st.markdown(f"""
                    <div class="gem-box">
                        <strong>🤖 AI Insight:</strong> {reason}
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("**Skills:**")
                render_skills_tags(gem["skills"]["current"][:6], job_required=job["required_skills"])
                if gem["skills"].get("learning"):
                    render_skills_tags(gem["skills"]["learning"][:4], tag_type="learning")
            
            with gem_cols[1]:
                render_score_bars(scores)
            
            with gem_cols[2]:
                # Rank comparison
                st.markdown(f"""
                <div style="background:#0f0f1a;border-radius:12px;padding:1rem;text-align:center;margin-bottom:0.7rem;">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;margin-bottom:0.3rem;">ATS Would Rank</div>
                    <div style="font-size:2rem;font-weight:900;color:#ef4444;
                         font-family:'JetBrains Mono',monospace;">#{ats_pos}</div>
                </div>
                <div style="background:#0f0f1a;border-radius:12px;padding:1rem;text-align:center;margin-bottom:0.7rem;">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;margin-bottom:0.3rem;">CareerTrajectory Rank</div>
                    <div style="font-size:2rem;font-weight:900;color:#10b981;
                         font-family:'JetBrains Mono',monospace;">#{ct_pos}</div>
                </div>
                <div style="background:#0f0f1a;border-radius:12px;padding:1rem;text-align:center;">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;margin-bottom:0.3rem;">Positions Improved</div>
                    <div style="font-size:2rem;font-weight:900;color:#f59e0b;
                         font-family:'JetBrains Mono',monospace;">+{rank_diff}</div>
                </div>
                """, unsafe_allow_html=True)

            # Action buttons
            btn1, btn2 = st.columns(2)
            with btn1:
                if st.button(f"👤 View Full Profile", key=f"gem_profile_{gem['id']}", use_container_width=True):
                    st.session_state.selected_candidate_id = gem["id"]
                    st.switch_page("pages/03_Profile.py")
            with btn2:
                if st.button(f"🔮 Run Skill Gap Sim", key=f"gem_gap_{gem['id']}", use_container_width=True):
                    st.session_state.selected_candidate_id = gem["id"]
                    st.switch_page("pages/05_SkillGap.py")

        st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)

# Why Traditional ATS Fails
st.markdown("---")
st.markdown("### 🚨 Why Traditional ATS Misses These Candidates")

fail_cols = st.columns(3)
reasons = [
    ("🔑", "Keyword Matching", "Traditional ATS scores only current skills. A candidate who learned Docker 3 months ago but had 2 years of Linux experience ranks lower than someone with 5 years of Docker listed on resume."),
    ("⏳", "Experience Gates", "Strict '3 years required' filters eliminate candidates who compressed 5 years of learning into 18 months through intensive self-study and open-source contributions."),
    ("📊", "No Trajectory Data", "ATS systems don't model learning velocity. They can't see that Candidate B with 1 year of experience is acquiring skills 3x faster than the average 5-year candidate."),
]
for col, (icon, title, desc) in zip(fail_cols, reasons):
    with col:
        st.markdown(f"""
        <div class="ct-card" style="border-color:#ef444444;text-align:center;">
            <div style="font-size:2rem;margin-bottom:0.7rem;">{icon}</div>
            <div style="font-weight:700;color:#f87171;margin-bottom:0.5rem;">{title}</div>
            <div style="color:#64748b;font-size:0.82rem;line-height:1.6;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
