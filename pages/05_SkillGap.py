"""
CareerTrajectory AI — Page 5: Skill Gap Simulator
Predict how acquiring new skills would change FPS and ranking.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

st.set_page_config(page_title="Skill Gap Simulator · CareerTrajectory AI", page_icon="🔮", layout="wide")

from ui.components import (inject_css, render_page_header, render_score_bars,
                            render_fps_gauge, render_skills_tags, get_score_color)
from data.sample_data import get_candidates, get_job_by_id
from backend.scoring_engine import rank_candidates, simulate_skill_gap, SKILL_DOMAIN_MAP

inject_css()

import plotly.graph_objects as go
import plotly.express as px

if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = "j001"
if "selected_candidate_id" not in st.session_state:
    st.session_state.selected_candidate_id = "c001"
if "custom_candidates" not in st.session_state:
    st.session_state.custom_candidates = []

candidates = get_candidates() + st.session_state.custom_candidates
job = get_job_by_id(st.session_state.selected_job_id)
ranked = rank_candidates(candidates, job)

render_page_header("Skill Gap Simulator", 
    "Predict how acquiring specific skills would improve a candidate's FPS and ranking.",
    "🔮")

st.markdown("""
<div class="info-box">
    <strong>🔮 Skill Gap Simulator</strong> — Select a candidate and skills to acquire.
    The AI predicts how their <strong>FPS score</strong> and <strong>ranking</strong> 
    would change — helping candidates focus on the highest-impact skills for a specific role.
</div>
""", unsafe_allow_html=True)

# ── Candidate & Skill Selection ───────────────────────────────────────────────
st.markdown("### 1️⃣ Select Candidate")
cand_options = {c["id"]: f"#{c.get('rank','?')} · {c['name']} (FPS: {c['scores']['fps']:.3f})"
                for c in ranked}

selected_id = st.selectbox(
    "Choose a candidate to simulate",
    options=list(cand_options.keys()),
    format_func=lambda x: cand_options[x],
    index=next((i for i, c in enumerate(ranked) if c["id"] == st.session_state.selected_candidate_id), 0),
    key="sim_candidate_select"
)
cand = next(c for c in ranked if c["id"] == selected_id)

# Current State Display
st.markdown("### 2️⃣ Current State")
cur1, cur2, cur3 = st.columns([1, 1.5, 1.5])

with cur1:
    render_fps_gauge(cand["scores"]["fps"], "Current FPS", size="small")

with cur2:
    st.markdown(f"""
    <div class="ct-card" style="padding:1.2rem;">
        <div style="font-weight:700;color:#a5b4fc;margin-bottom:0.8rem;">📊 Current Scores</div>
    </div>
    """, unsafe_allow_html=True)
    render_score_bars(cand["scores"])

with cur3:
    st.markdown(f"""
    <div class="ct-card" style="padding:1.2rem;">
        <div style="font-weight:700;color:#a5b4fc;margin-bottom:0.8rem;">✅ Current Skills</div>
    </div>
    """, unsafe_allow_html=True)
    render_skills_tags(cand["skills"]["current"], job_required=job["required_skills"])
    
    missing = [s for s in job["required_skills"] if s.lower() not in [c.lower() for c in cand["skills"]["current"]]]
    if missing:
        st.markdown(f"<div style='color:#64748b;font-size:0.75rem;margin:0.5rem 0 0.2rem;'>❌ Missing ({len(missing)}):</div>", unsafe_allow_html=True)
        render_skills_tags(missing)

# ── Skill Selection ───────────────────────────────────────────────────────────
st.markdown("### 3️⃣ Select Skills to Acquire")

all_skills_to_choose = sorted(list(set(
    list(job["required_skills"]) + list(job.get("good_to_have", [])) + [
        "AWS", "GCP", "Docker", "Kubernetes", "Terraform", "Python", "Go", "Rust",
        "PyTorch", "TensorFlow", "LangChain", "MLflow", "Ray", "FastAPI",
        "React", "TypeScript", "Node.js", "GraphQL", "PostgreSQL", "Redis",
        "Kafka", "Spark", "dbt", "Airflow", "eBPF", "Linux Kernel"
    ]
) - set(cand["skills"]["current"])))

skill_tabs = st.tabs(["🎯 Job-Required Missing", "⭐ Good-to-Have Missing", "🌐 All Skills"])

with skill_tabs[0]:
    missing_req = [s for s in job["required_skills"] if s.lower() not in [c.lower() for c in cand["skills"]["current"]]]
    if missing_req:
        selected_skills_req = st.multiselect(
            "Select from missing required skills",
            options=missing_req,
            default=missing_req[:2] if len(missing_req) >= 2 else missing_req,
            key="sim_req_skills"
        )
    else:
        st.success("✅ All required skills are present!")
        selected_skills_req = []

with skill_tabs[1]:
    missing_good = [s for s in job.get("good_to_have", []) if s.lower() not in [c.lower() for c in cand["skills"]["current"]]]
    if missing_good:
        selected_skills_good = st.multiselect(
            "Select from missing good-to-have skills",
            options=missing_good,
            key="sim_good_skills"
        )
    else:
        st.info("No missing good-to-have skills for this candidate.")
        selected_skills_good = []

with skill_tabs[2]:
    selected_skills_all = st.multiselect(
        "Select any skills",
        options=all_skills_to_choose,
        key="sim_all_skills"
    )

# Combine all selected skills
all_selected = list(set(
    st.session_state.get("sim_req_skills", []) +
    st.session_state.get("sim_good_skills", []) +
    st.session_state.get("sim_all_skills", [])
))

# ── Run Simulation ────────────────────────────────────────────────────────────
st.markdown("### 4️⃣ Run Simulation")

if st.button("🚀 Simulate Skill Impact", use_container_width=True, key="run_simulation"):
    if not all_selected:
        st.warning("Please select at least one skill to simulate.")
    else:
        with st.spinner("🤖 Running simulation..."):
            import time
            time.sleep(0.5)  # UX delay
            result = simulate_skill_gap(cand, job, all_selected)

        st.markdown("### 5️⃣ Simulation Results")
        
        improvement = result["improvement"]
        color_before = get_score_color(result["current_fps"])
        color_after = get_score_color(result["predicted_fps"])
        imp_color = "#10b981" if improvement > 0 else "#ef4444"

        # Impact Header
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.1));
             border:1px solid rgba(99,102,241,0.3);border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;">
            <div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">
                <div style="text-align:center;min-width:100px;">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;">Before</div>
                    <div style="font-size:2.5rem;font-weight:900;color:{color_before};
                         font-family:'JetBrains Mono',monospace;">{result['current_fps']:.3f}</div>
                    <div style="color:#64748b;font-size:0.75rem;">FPS Score</div>
                </div>
                <div style="font-size:2rem;color:#334155;">→</div>
                <div style="text-align:center;min-width:100px;">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;">After</div>
                    <div style="font-size:2.5rem;font-weight:900;color:{color_after};
                         font-family:'JetBrains Mono',monospace;">{result['predicted_fps']:.3f}</div>
                    <div style="color:#64748b;font-size:0.75rem;">FPS Score</div>
                </div>
                <div style="font-size:2rem;color:#334155;">=</div>
                <div style="text-align:center;min-width:120px;">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;">Improvement</div>
                    <div style="font-size:2.5rem;font-weight:900;color:{imp_color};
                         font-family:'JetBrains Mono',monospace;">+{improvement:.3f}</div>
                    <div style="color:#64748b;font-size:0.75rem;">FPS Delta</div>
                </div>
                <div style="font-size:2rem;color:#334155;">·</div>
                <div style="text-align:center;min-width:120px;">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;">Est. Rank Change</div>
                    <div style="font-size:2.5rem;font-weight:900;color:#f59e0b;
                         font-family:'JetBrains Mono',monospace;">
                         {"+" if result['estimated_rank_improvement'] > 0 else ""}{result['estimated_rank_improvement']}
                    </div>
                    <div style="color:#64748b;font-size:0.75rem;">Positions</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Recommendation
        st.markdown(f"""
        <div class="{'success-box' if improvement > 0.05 else 'info-box'}">
            {result['recommendation']}
        </div>
        """, unsafe_allow_html=True)

        # Before/After Chart
        breakdown = result["score_breakdown"]
        categories = ["Semantic Fit", "Career Momentum", "Behavioral Evidence", "Contextual Intelligence"]
        keys = ["semantic_fit", "career_momentum", "behavioral_evidence", "contextual_intelligence"]

        before_vals = [breakdown[k]["before"] * 100 for k in keys]
        after_vals = [breakdown[k]["after"] * 100 for k in keys]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name="Before",
            x=categories,
            y=before_vals,
            marker_color="#ef4444",
            opacity=0.8,
        ))
        fig.add_trace(go.Bar(
            name="After",
            x=categories,
            y=after_vals,
            marker_color="#10b981",
            opacity=0.8,
        ))
        fig.update_layout(
            barmode="group",
            height=320,
            margin=dict(l=10, r=10, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="#1a1a2e",
            xaxis={"gridcolor": "#334155", "tickfont": {"color": "#e2e8f0"}},
            yaxis={"gridcolor": "#334155", "tickfont": {"color": "#94a3b8"},
                   "range": [0, 100], "ticksuffix": "%"},
            legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
            font=dict(family="Inter"),
            title=dict(text="Score Component Comparison (Before vs After)", 
                      font=dict(color="#94a3b8", size=13)),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Side by side gauge comparison
        g1, g2 = st.columns(2)
        with g1:
            st.markdown("<div style='text-align:center;color:#64748b;font-size:0.85rem;'>Before</div>", unsafe_allow_html=True)
            render_fps_gauge(result["current_fps"], f"Current: {result['current_fps']:.3f}", size="small")
        with g2:
            st.markdown("<div style='text-align:center;color:#64748b;font-size:0.85rem;'>After (Predicted)</div>", unsafe_allow_html=True)
            render_fps_gauge(result["predicted_fps"], f"Predicted: {result['predicted_fps']:.3f}", size="small")

# ── Multi-Skill Impact Analysis ───────────────────────────────────────────────
st.markdown("---")
st.markdown("### 📊 Individual Skill Impact Analysis")
st.markdown("""
<div class="info-box" style="font-size:0.85rem;">
    See which individual skill would have the biggest impact on FPS for this candidate and role.
</div>
""", unsafe_allow_html=True)

candidate_missing = [s for s in job["required_skills"] + job.get("good_to_have", [])
                     if s.lower() not in [c.lower() for c in cand["skills"]["current"]]]
candidate_missing = candidate_missing[:12]  # Limit for performance

if candidate_missing:
    impact_data = []
    for skill in candidate_missing:
        sim = simulate_skill_gap(cand, job, [skill])
        impact_data.append({"skill": skill, "delta": sim["improvement"], "new_fps": sim["predicted_fps"]})

    impact_data.sort(key=lambda x: x["delta"], reverse=True)

    fig_impact = go.Figure(go.Bar(
        x=[d["skill"] for d in impact_data],
        y=[d["delta"] * 100 for d in impact_data],
        marker_color=[get_score_color(d["delta"] / 0.15) for d in impact_data],
        text=[f"+{d['delta']*100:.1f}%" for d in impact_data],
        textposition="outside",
        textfont={"color": "#e2e8f0", "size": 10},
    ))
    fig_impact.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=40),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1a2e",
        xaxis={"gridcolor": "#334155", "tickfont": {"color": "#e2e8f0", "size": 10}},
        yaxis={"gridcolor": "#334155", "tickfont": {"color": "#94a3b8"},
               "title": {"text": "FPS Improvement (%)", "font": {"color": "#64748b"}}},
        showlegend=False,
        font={"family": "Inter"},
    )
    st.plotly_chart(fig_impact, use_container_width=True)

    # Top recommendations
    top3 = impact_data[:3]
    st.markdown("#### 🏆 Top 3 Highest-Impact Skills to Acquire")
    r1, r2, r3 = st.columns(3)
    cols = [r1, r2, r3]
    medals = ["🥇", "🥈", "🥉"]
    for i, (col, skill_data) in enumerate(zip(cols, top3)):
        with col:
            delta_pct = skill_data["delta"] * 100
            color = get_score_color(skill_data["new_fps"])
            st.markdown(f"""
            <div class="ct-card" style="text-align:center;padding:1.5rem;">
                <div style="font-size:2rem;margin-bottom:0.5rem;">{medals[i]}</div>
                <div style="font-weight:800;color:#e2e8f0;font-size:1rem;margin-bottom:0.4rem;">
                    {skill_data['skill']}
                </div>
                <div style="font-size:1.8rem;font-weight:900;color:#10b981;
                     font-family:'JetBrains Mono',monospace;">+{delta_pct:.1f}%</div>
                <div style="color:#64748b;font-size:0.75rem;margin-top:0.3rem;">FPS Improvement</div>
                <div style="color:{color};font-size:0.85rem;font-weight:700;margin-top:0.3rem;">
                    New FPS: {skill_data['new_fps']:.3f}
                </div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.success("✅ This candidate already has all required and good-to-have skills for this role!")
