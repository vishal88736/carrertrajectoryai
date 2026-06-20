"""
CareerTrajectory AI — Page 1: Dashboard
Real-time recruiter dashboard with key metrics and insights.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

st.set_page_config(page_title="Dashboard · CareerTrajectory AI", page_icon="🏠", layout="wide")

from ui.components import inject_css, render_page_header, render_metric_row, render_fps_gauge, get_score_color
from data.sample_data import get_candidates, get_jobs, get_job_by_id
from backend.scoring_engine import rank_candidates, detect_hidden_gems

inject_css()

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# ── State ────────────────────────────────────────────────────────────────────
if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = "j001"

candidates = get_candidates()
jobs = get_jobs()
job = get_job_by_id(st.session_state.selected_job_id)
ranked = rank_candidates(candidates, job)
gems = detect_hidden_gems(candidates)

# ── Header ────────────────────────────────────────────────────────────────────
render_page_header(
    "Recruiter Dashboard",
    f"Intelligence overview for: {job['title']} @ {job['company']}",
    "🏠"
)

# ── Top Metrics ───────────────────────────────────────────────────────────────
render_metric_row([
    {"label": "Total Candidates", "value": str(len(candidates)), "delta": "+3 this week", "icon": "👥"},
    {"label": "Hidden Gems", "value": str(len(gems)), "delta": "AI discovered", "icon": "💎"},
    {"label": "Avg FPS Score", "value": f"{sum(c['scores']['fps'] for c in ranked)/len(ranked):.3f}", "icon": "📊"},
    {"label": "Top FPS Score", "value": f"{ranked[0]['scores']['fps']:.3f}", "delta": f"#{ranked[0]['name'].split()[0]}", "icon": "🏆"},
    {"label": "Active Jobs", "value": str(len(jobs)), "icon": "💼"},
])

st.markdown("<br>", unsafe_allow_html=True)

# ── Main Columns ──────────────────────────────────────────────────────────────
col_left, col_right = st.columns([2, 1])

with col_left:
    # Top 5 Ranked Candidates
    st.markdown("""
    <div class="section-header">
        <span style="font-size:1.3rem;">🏆</span>
        <h2>Top Ranked Candidates</h2>
    </div>
    """, unsafe_allow_html=True)

    for i, c in enumerate(ranked[:5]):
        fps = c["scores"]["fps"]
        color = get_score_color(fps)
        is_gem = c.get("hidden_gem", False)
        gem_icon = "💎 " if is_gem else ""
        bar_pct = fps * 100

        st.markdown(f"""
        <div class="candidate-card" style="{'border-color:#f59e0b;box-shadow:0 0 15px rgba(245,158,11,0.15);' if is_gem else ''}">
            <div style="display:flex; align-items:center; gap:1rem;">
                <div style="width:40px;height:40px;border-radius:50%;
                    background:{'linear-gradient(135deg,#f59e0b,#fbbf24)' if i==0 else 'linear-gradient(135deg,#6366f1,#8b5cf6)'};
                    display:flex;align-items:center;justify-content:center;
                    font-weight:800;color:{'#000' if i==0 else 'white'};font-size:0.95rem;flex-shrink:0;">
                    {'🥇' if i==0 else '#'+str(i+1)}
                </div>
                <div style="flex:1; min-width:0;">
                    <div style="font-weight:700;font-size:0.95rem;color:#e2e8f0;">
                        {gem_icon}{c['name']}
                        {'<span style="background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#000;font-size:0.65rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:999px;margin-left:0.4rem;">HIDDEN GEM</span>' if is_gem else ''}
                    </div>
                    <div style="color:#64748b;font-size:0.78rem;margin-top:1px;">
                        {c.get('location','N/A')} · {c.get('years_of_experience',0)} yrs · {', '.join(c['skills']['current'][:3])}...
                    </div>
                    <div style="margin-top:0.5rem;">
                        <div style="background:#1e293b;border-radius:999px;height:5px;overflow:hidden;">
                            <div style="width:{bar_pct}%;height:100%;border-radius:999px;
                                background:linear-gradient(90deg,{color}88,{color});"></div>
                        </div>
                    </div>
                </div>
                <div style="text-align:right;flex-shrink:0;">
                    <div style="font-size:1.6rem;font-weight:900;color:{color};
                         font-family:'JetBrains Mono',monospace;line-height:1;">{fps:.3f}</div>
                    <div style="color:#64748b;font-size:0.7rem;font-weight:500;">FPS</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    # FPS Distribution
    st.markdown("""
    <div class="section-header">
        <span style="font-size:1.3rem;">📊</span>
        <h2>FPS Distribution</h2>
    </div>
    """, unsafe_allow_html=True)

    fps_values = [c["scores"]["fps"] for c in ranked]
    fig_hist = go.Figure()
    fig_hist.add_trace(go.Histogram(
        x=fps_values, nbinsx=8,
        marker_color="#6366f1",
        marker_line_color="#4f46e5",
        marker_line_width=1,
        opacity=0.8,
        name="Candidates"
    ))
    fig_hist.update_layout(
        height=220, margin=dict(l=10, r=10, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1a2e",
        xaxis={"gridcolor": "#334155", "tickfont": {"color": "#94a3b8"}, "title": {"text": "FPS Score", "font": {"color": "#64748b"}}},
        yaxis={"gridcolor": "#334155", "tickfont": {"color": "#94a3b8"}},
        showlegend=False,
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    # Score breakdown pie
    st.markdown("""
    <div class="section-header" style="margin-top:1rem;">
        <span style="font-size:1.3rem;">🎯</span>
        <h2>FPS Weight Distribution</h2>
    </div>
    """, unsafe_allow_html=True)

    weights_fig = go.Figure(go.Pie(
        labels=["Semantic Fit", "Career Momentum", "Behavioral Evidence", "Contextual Intelligence"],
        values=[35, 30, 20, 15],
        hole=0.55,
        marker=dict(
            colors=["#6366f1", "#10b981", "#f59e0b", "#06b6d4"],
            line=dict(color="#0f0f1a", width=2)
        ),
        textfont={"color": "#e2e8f0", "size": 11},
        textposition="outside",
    ))
    weights_fig.update_layout(
        height=220, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(font=dict(color="#94a3b8", size=10), bgcolor="rgba(0,0,0,0)"),
        showlegend=True,
    )
    st.plotly_chart(weights_fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Career Momentum Scatter ────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <span style="font-size:1.3rem;">🚀</span>
    <h2>Career Momentum vs Semantic Fit</h2>
</div>
""", unsafe_allow_html=True)

df_scatter = pd.DataFrame([{
    "Name": c["name"],
    "Semantic Fit": c["scores"]["semantic_fit"],
    "Career Momentum": c["scores"]["career_momentum"],
    "FPS": c["scores"]["fps"],
    "Experience": c["years_of_experience"],
    "Hidden Gem": "💎 Hidden Gem" if c.get("hidden_gem") else "Regular",
} for c in ranked])

fig_scatter = go.Figure()

for gem_type, color, symbol in [("Regular", "#6366f1", "circle"), ("💎 Hidden Gem", "#f59e0b", "star")]:
    subset = df_scatter[df_scatter["Hidden Gem"] == gem_type]
    if not subset.empty:
        fig_scatter.add_trace(go.Scatter(
            x=subset["Semantic Fit"],
            y=subset["Career Momentum"],
            mode="markers+text",
            marker=dict(
                size=subset["FPS"] * 60 + 10,
                color=color,
                opacity=0.85,
                line=dict(color="#0f0f1a", width=2)
            ),
            text=subset["Name"].apply(lambda n: n.split()[0]),
            textposition="top center",
            textfont={"size": 10, "color": "#e2e8f0"},
            name=gem_type,
            hovertemplate=(
                "<b>%{text}</b><br>"
                "Semantic Fit: %{x:.2f}<br>"
                "Career Momentum: %{y:.2f}<br>"
                "<extra></extra>"
            )
        ))

# Add quadrant lines
fig_scatter.add_shape(type="line", x0=0.5, x1=0.5, y0=0, y1=1,
    line=dict(color="#334155", width=1, dash="dot"))
fig_scatter.add_shape(type="line", x0=0, x1=1, y0=0.5, y1=0.5,
    line=dict(color="#334155", width=1, dash="dot"))

# Quadrant labels
for x, y, text in [(0.75, 0.95, "🏆 Top Talent"), (0.25, 0.95, "💎 Hidden Gems"),
                    (0.75, 0.05, "📚 Experienced"), (0.25, 0.05, "⚠️ Below Bar")]:
    fig_scatter.add_annotation(x=x, y=y, text=text, showarrow=False,
        font=dict(color="#475569", size=10))

fig_scatter.update_layout(
    height=380, margin=dict(l=20, r=20, t=20, b=20),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#1a1a2e",
    xaxis={"gridcolor": "#334155", "range": [0, 1], "title": {"text": "Semantic Fit →", "font": {"color": "#64748b"}},
           "tickfont": {"color": "#94a3b8"}},
    yaxis={"gridcolor": "#334155", "range": [0, 1], "title": {"text": "Career Momentum →", "font": {"color": "#64748b"}},
           "tickfont": {"color": "#94a3b8"}},
    legend=dict(font=dict(color="#94a3b8"), bgcolor="rgba(0,0,0,0)"),
    font={"family": "Inter"},
)
st.plotly_chart(fig_scatter, use_container_width=True)

# ── Recent Activity ────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-header">
    <span style="font-size:1.3rem;">🔔</span>
    <h2>System Activity Log</h2>
</div>
""", unsafe_allow_html=True)

activities = [
    ("🤖", "Resume Intelligence Agent", "Processed 6 resumes, extracted 47 skills across all candidates", "2 min ago", "#6366f1"),
    ("🚀", "Career Momentum Engine", f"Detected {len(gems)} hidden gems with high momentum but low ATS score", "5 min ago", "#10b981"),
    ("🔬", "Behavior Validation Agent", "Verified GitHub signals for 5 candidates, found 3 with 200+ day streaks", "8 min ago", "#8b5cf6"),
    ("🏆", "Talent Ranking Agent", f"Re-ranked {len(candidates)} candidates for: {job['title']}", "12 min ago", "#06b6d4"),
    ("🔍", "Explainability Agent", "Generated SHAP explanations for top 5 candidates", "15 min ago", "#f59e0b"),
]

for icon, agent, msg, time, color in activities:
    st.markdown(f"""
    <div style="display:flex;gap:1rem;align-items:flex-start;padding:0.75rem;
         border-radius:10px;background:#1a1a2e;border:1px solid #1e293b;margin-bottom:0.5rem;">
        <div style="width:36px;height:36px;border-radius:50%;
             background:{color}22;border:1px solid {color}44;
             display:flex;align-items:center;justify-content:center;
             font-size:1rem;flex-shrink:0;">{icon}</div>
        <div style="flex:1;">
            <div style="font-weight:600;font-size:0.85rem;color:#a5b4fc;">{agent}</div>
            <div style="color:#94a3b8;font-size:0.82rem;margin-top:2px;">{msg}</div>
        </div>
        <div style="color:#475569;font-size:0.75rem;flex-shrink:0;">{time}</div>
    </div>
    """, unsafe_allow_html=True)
