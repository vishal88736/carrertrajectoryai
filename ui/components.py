"""
CareerTrajectory AI — Shared UI Components & Styling
Common Streamlit UI utilities, color palette, and reusable widgets.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional


# ─── Color Palette ─────────────────────────────────────────────────────────────

COLORS = {
    "primary": "#6366f1",       # Indigo
    "primary_dark": "#4f46e5",
    "secondary": "#8b5cf6",     # Violet
    "accent": "#06b6d4",        # Cyan
    "success": "#10b981",       # Emerald
    "warning": "#f59e0b",       # Amber
    "danger": "#ef4444",        # Red
    "bg_dark": "#0f0f1a",       # Deep Navy
    "bg_card": "#1a1a2e",       # Card Dark
    "bg_card2": "#16213e",      # Card Alt
    "text_primary": "#e2e8f0",  # Light text
    "text_secondary": "#94a3b8", # Muted text
    "border": "#334155",        # Subtle border
    "gem_gold": "#f59e0b",      # Hidden gem highlight
    "momentum_high": "#10b981",
    "momentum_low": "#ef4444",
    "momentum_mid": "#f59e0b",
}

SCORE_COLORS = {
    "excellent": "#10b981",  # ≥0.8
    "good": "#6366f1",       # ≥0.65
    "moderate": "#f59e0b",   # ≥0.5
    "low": "#ef4444",        # <0.5
}


def get_score_color(score: float) -> str:
    if score >= 0.80:
        return SCORE_COLORS["excellent"]
    elif score >= 0.65:
        return SCORE_COLORS["good"]
    elif score >= 0.50:
        return SCORE_COLORS["moderate"]
    else:
        return SCORE_COLORS["low"]


def get_score_label(score: float) -> str:
    if score >= 0.85:
        return "🟢 Exceptional"
    elif score >= 0.75:
        return "🟢 Strong"
    elif score >= 0.65:
        return "🔵 Good"
    elif score >= 0.50:
        return "🟡 Moderate"
    else:
        return "🔴 Below Average"


# ─── Global CSS ───────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Root Variables ── */
:root {
    --primary: #6366f1;
    --primary-dark: #4f46e5;
    --secondary: #8b5cf6;
    --accent: #06b6d4;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --bg-dark: #0f0f1a;
    --bg-card: #1a1a2e;
    --bg-card2: #16213e;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --border: #334155;
    --radius: 12px;
    --radius-lg: 20px;
    --shadow: 0 4px 20px rgba(99, 102, 241, 0.15);
    --shadow-hover: 0 8px 30px rgba(99, 102, 241, 0.3);
    --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Global Reset ── */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg-dark) !important;
    color: var(--text-primary) !important;
}

/* ── Main Content Area ── */
.main .block-container {
    padding: 1.5rem 2rem 2rem !important;
    max-width: 1400px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1rem !important;
}

/* ── Headers ── */
h1 { 
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800 !important;
    letter-spacing: -0.02em !important;
}

h2, h3 { color: var(--text-primary) !important; font-weight: 700 !important; }

/* ── Cards ── */
.ct-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: var(--transition);
    position: relative;
    overflow: hidden;
}

.ct-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--secondary), var(--accent));
}

.ct-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-hover);
    border-color: var(--primary);
}

/* ── Metric Cards ── */
.metric-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.5rem;
    text-align: center;
    transition: var(--transition);
}

.metric-card:hover {
    border-color: var(--primary);
    box-shadow: var(--shadow);
}

.metric-value {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1;
    margin: 0.3rem 0;
}

.metric-label {
    color: var(--text-secondary);
    font-size: 0.8rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Score Badge ── */
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.85rem;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Rank Badge ── */
.rank-badge {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-weight: 800;
    font-size: 0.95rem;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    box-shadow: 0 0 15px rgba(99,102,241,0.5);
}

/* ── Progress Bar ── */
.fps-bar-container {
    background: #1e293b;
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin: 0.3rem 0;
}

.fps-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    transition: width 0.8s ease;
}

/* ── Candidate Card ── */
.candidate-card {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: var(--transition);
    cursor: pointer;
}

.candidate-card:hover {
    border-color: #6366f1;
    box-shadow: 0 0 30px rgba(99,102,241,0.2);
    transform: translateY(-2px);
}

.candidate-card.gem {
    border-color: #f59e0b;
    box-shadow: 0 0 20px rgba(245,158,11,0.2);
}

.candidate-card.gem::before {
    content: '💎 Hidden Gem';
    position: absolute;
    top: 1rem; right: 1rem;
    background: linear-gradient(135deg, #f59e0b, #fbbf24);
    color: #000;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.25rem 0.6rem;
    border-radius: 999px;
}

/* ── Skills Tags ── */
.skill-tag {
    display: inline-block;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    color: #a5b4fc;
    border-radius: 999px;
    padding: 0.2rem 0.7rem;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 0.15rem;
    transition: var(--transition);
}

.skill-tag:hover {
    background: rgba(99,102,241,0.3);
    border-color: #6366f1;
}

.skill-tag.matched {
    background: rgba(16,185,129,0.15);
    border-color: rgba(16,185,129,0.3);
    color: #6ee7b7;
}

.skill-tag.learning {
    background: rgba(245,158,11,0.15);
    border-color: rgba(245,158,11,0.3);
    color: #fcd34d;
}

/* ── Section Headers ── */
.section-header {
    display: flex;
    align-items: center;
    gap: 0.7rem;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--border);
}

.section-header h2 {
    margin: 0 !important;
    font-size: 1.4rem !important;
}

/* ── Info Box ── */
.info-box {
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.25);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin: 0.75rem 0;
    border-left: 3px solid #6366f1;
}

.gem-box {
    background: rgba(245,158,11,0.08);
    border: 1px solid rgba(245,158,11,0.25);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin: 0.75rem 0;
    border-left: 3px solid #f59e0b;
}

.success-box {
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.25);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin: 0.75rem 0;
    border-left: 3px solid #10b981;
}

.warning-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    margin: 0.75rem 0;
    border-left: 3px solid #ef4444;
}

/* ── Page Header ── */
.page-header {
    padding: 1.5rem 0 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}

.page-tagline {
    color: var(--text-secondary);
    font-size: 1rem;
    margin-top: 0.3rem;
}

/* ── Streamlit Overrides ── */
.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: var(--transition) !important;
    font-family: 'Inter', sans-serif !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: var(--shadow-hover) !important;
}

.stSelectbox > div > div,
.stMultiSelect > div > div,
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #1a1a2e !important;
    border: 1px solid var(--border) !important;
    color: var(--text-primary) !important;
    border-radius: var(--radius) !important;
}

.stSelectbox > div > div:hover,
.stTextInput > div > div > input:focus {
    border-color: var(--primary) !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #1a1a2e !important;
    border-radius: var(--radius) !important;
    padding: 0.3rem !important;
    gap: 0.2rem !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: var(--transition) !important;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important;
}

/* ── Metric deltas ── */
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ── Expander ── */
.streamlit-expanderHeader {
    background: #1a1a2e !important;
    border-radius: var(--radius) !important;
    border: 1px solid var(--border) !important;
}

/* ── Plotly charts dark ── */
.js-plotly-plot { border-radius: var(--radius) !important; }

/* ── Table ── */
.stDataFrame {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}

/* ── Sidebar nav ── */
.sidebar-nav-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    color: var(--text-secondary);
    cursor: pointer;
    transition: var(--transition);
    margin-bottom: 0.2rem;
    text-decoration: none;
    font-size: 0.9rem;
    font-weight: 500;
}

.sidebar-nav-item:hover, .sidebar-nav-item.active {
    background: rgba(99,102,241,0.15);
    color: #a5b4fc;
}

/* ── Copilot Chat ── */
.chat-bubble {
    border-radius: 16px;
    padding: 0.8rem 1.1rem;
    margin: 0.5rem 0;
    max-width: 85%;
    line-height: 1.5;
}

.chat-bubble.user {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    margin-left: auto;
    border-bottom-right-radius: 4px;
}

.chat-bubble.assistant {
    background: #1a1a2e;
    border: 1px solid var(--border);
    color: var(--text-primary);
    border-bottom-left-radius: 4px;
}

/* ── Upload Area ── */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border) !important;
    border-radius: var(--radius-lg) !important;
    background: rgba(99,102,241,0.04) !important;
    transition: var(--transition) !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--primary) !important;
    background: rgba(99,102,241,0.08) !important;
}

/* ── Timeline ── */
.timeline-item {
    display: flex;
    gap: 1rem;
    padding: 0.75rem 0;
    border-left: 2px solid var(--border);
    margin-left: 1rem;
    padding-left: 1.5rem;
    position: relative;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -6px;
    top: 1rem;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--primary);
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2);
}

/* ── Slider ── */
.stSlider [data-baseweb="slider"] {
    color: var(--primary) !important;
}

/* ── Progress ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--primary), var(--secondary)) !important;
}

/* ── Radio ── */
.stRadio > div > label {
    color: var(--text-primary) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-dark); }
::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--primary); }

/* ── Animation ── */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 0 10px rgba(99,102,241,0.3); }
    50% { box-shadow: 0 0 25px rgba(99,102,241,0.6); }
}

.animate-fade-in {
    animation: fadeInUp 0.5s ease forwards;
}

.pulse-glow {
    animation: pulse-glow 2s infinite;
}

/* ── FPS Gauge ── */
.fps-gauge-container {
    text-align: center;
    padding: 1rem;
}

.fps-number {
    font-size: 3.5rem;
    font-weight: 900;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}

/* ── Gradient Text ── */
.gradient-text {
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #06b6d4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
}

/* ── Hide Streamlit defaults ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
"""


def render_sidebar():
    """Renders the unified custom sidebar navigation."""
    with st.sidebar:
        render_sidebar_logo()

        st.markdown("### Navigation")

        pages = [
            ("🚀", "Home", "app.py"),
            ("🏠", "Dashboard", "pages/01_Dashboard.py"),
            ("📊", "Candidate Ranking", "pages/02_Ranking.py"),
            ("👤", "Candidate Profile", "pages/03_Profile.py"),
            ("💎", "Hidden Gems", "pages/04_HiddenGems.py"),
            ("🔮", "Skill Gap Simulator", "pages/05_SkillGap.py"),
            ("📈", "Talent Analytics", "pages/06_Analytics.py"),
            ("🤖", "Recruiter Copilot", "pages/07_Copilot.py"),
            ("💼", "Job Management", "pages/08_Jobs.py"),
            ("⚙️", "Admin Panel", "pages/09_Admin.py"),
        ]

        for icon, name, path in pages:
            if st.button(f"{icon} {name}", key=f"nav_{name}", use_container_width=True):
                st.switch_page(path)

        st.markdown("---")

        # Job selector
        from data.sample_data import get_jobs
        jobs = get_jobs()
        job_names = {j["id"]: f"{j['title']} @ {j['company']}" for j in jobs}
        
        if "selected_job_id" not in st.session_state:
            st.session_state.selected_job_id = "j001"
            
        job_ids = list(job_names.keys())
        try:
            default_index = job_ids.index(st.session_state.selected_job_id)
        except ValueError:
            default_index = 0

        selected_job = st.selectbox(
            "🎯 Active Job Requisition",
            options=job_ids,
            format_func=lambda x: job_names[x],
            index=default_index,
            key="sidebar_job_select"
        )
        
        if selected_job != st.session_state.selected_job_id:
            st.session_state.selected_job_id = selected_job
            st.rerun()

        st.markdown("---")
        
        # Toggle for Sample Data
        use_sample = st.checkbox(
            "Include Sample Candidates", 
            value=st.session_state.get("use_sample_data", False),
            key="sidebar_sample_toggle",
            help="Check to include 6 dummy candidates for demonstration purposes. Uncheck to start with an empty database."
        )
        if use_sample != st.session_state.get("use_sample_data", False):
            st.session_state.use_sample_data = use_sample
            st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="color:#475569; font-size:0.72rem; text-align:center; padding:0.5rem 0;">
            <div style="margin-bottom:0.3rem;">🔒 Enterprise Grade · GDPR Compliant</div>
            <div>Bias-Mitigated · Explainable AI</div>
            <div style="margin-top:0.5rem; color:#334155;">v1.0.0 · CareerTrajectory AI</div>
        </div>
        """, unsafe_allow_html=True)


def inject_css():
    """Inject global CSS into the Streamlit app and render the sidebar."""
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    render_sidebar()


# ─── Reusable Components ──────────────────────────────────────────────────────


def render_page_header(title: str, subtitle: str, icon: str = ""):
    """Renders a styled page header."""
    st.markdown(f"""
    <div class="page-header animate-fade-in">
        <h1>{icon} {title}</h1>
        <p class="page-tagline">{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def render_fps_gauge(fps: float, label: str = "FPS", size: str = "large"):
    """Renders a circular FPS gauge using Plotly."""
    color = get_score_color(fps)
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=fps * 100,
        number={"suffix": "", "font": {"size": 36, "color": "#e2e8f0", "family": "JetBrains Mono"}},
        title={"text": label, "font": {"size": 14, "color": "#94a3b8", "family": "Inter"}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#334155",
                "tickfont": {"color": "#475569"},
            },
            "bar": {"color": color, "thickness": 0.7},
            "bgcolor": "#1a1a2e",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "rgba(239,68,68,0.1)"},
                {"range": [50, 65], "color": "rgba(245,158,11,0.1)"},
                {"range": [65, 80], "color": "rgba(99,102,241,0.1)"},
                {"range": [80, 100], "color": "rgba(16,185,129,0.1)"},
            ],
            "threshold": {
                "line": {"color": "#f59e0b", "width": 2},
                "thickness": 0.7,
                "value": fps * 100
            }
        }
    ))
    h = 220 if size == "small" else 280
    fig.update_layout(
        height=h,
        margin=dict(l=20, r=20, t=40, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_score_bars(scores: Dict[str, float]):
    """Renders horizontal score bars for each component."""
    labels = {
        "semantic_fit": "Semantic Fit",
        "career_momentum": "Career Momentum",
        "behavioral_evidence": "Behavioral Evidence",
        "contextual_intelligence": "Contextual Intelligence",
    }
    icons = {
        "semantic_fit": "🎯",
        "career_momentum": "🚀",
        "behavioral_evidence": "🔬",
        "contextual_intelligence": "🧠",
    }

    for key, label in labels.items():
        val = scores.get(key, 0)
        color = get_score_color(val)
        pct = val * 100
        icon = icons.get(key, "•")
        st.markdown(f"""
        <div style="margin-bottom: 0.8rem;">
            <div style="display:flex; justify-content:space-between; margin-bottom:4px;">
                <span style="color:#94a3b8; font-size:0.85rem; font-weight:500;">{icon} {label}</span>
                <span style="color:{color}; font-weight:700; font-family:'JetBrains Mono',monospace; font-size:0.9rem;">{val:.2f}</span>
            </div>
            <div style="background:#1e293b; border-radius:999px; height:6px; overflow:hidden;">
                <div style="width:{pct}%; height:100%; border-radius:999px; 
                     background:linear-gradient(90deg, {color}aa, {color}); 
                     transition:width 0.8s ease;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_skills_tags(skills: List[str], tag_type: str = "current",
                       job_required: List[str] = None):
    """Renders skills as styled tags."""
    if not skills:
        return

    job_req_lower = set(s.lower() for s in (job_required or []))
    tags_html = ""
    for skill in skills:
        css_class = "skill-tag"
        if tag_type == "learning":
            css_class += " learning"
        elif skill.lower() in job_req_lower:
            css_class += " matched"
        tags_html += f'<span class="{css_class}">{skill}</span>'

    st.markdown(f'<div style="margin: 0.5rem 0;">{tags_html}</div>', unsafe_allow_html=True)


def render_candidate_card_mini(candidate: Dict, job: Optional[Dict] = None):
    """Renders a compact candidate card for list views."""
    scores = candidate.get("scores", {})
    fps = scores.get("fps", 0)
    rank = candidate.get("rank", "—")
    is_gem = candidate.get("hidden_gem", False)
    color = get_score_color(fps)
    gem_badge = "💎 Hidden Gem" if is_gem else ""
    gem_style = "border-color: #f59e0b; box-shadow: 0 0 20px rgba(245,158,11,0.15);" if is_gem else ""

    st.markdown(f"""
    <div class="candidate-card" style="{gem_style} position:relative;">
        <div style="display:flex; align-items:center; gap:1rem;">
            <div style="width:44px; height:44px; border-radius:50%; 
                background:linear-gradient(135deg,#6366f1,#8b5cf6);
                display:flex; align-items:center; justify-content:center;
                font-weight:800; font-size:1.1rem; flex-shrink:0; color:white;">
                #{rank}
            </div>
            <div style="flex:1;">
                <div style="font-weight:700; font-size:1rem; color:#e2e8f0;">
                    {candidate['name']} 
                    {f'<span style="background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#000;font-size:0.7rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:999px;margin-left:0.5rem;">{gem_badge}</span>' if is_gem else ''}
                </div>
                <div style="color:#64748b; font-size:0.82rem; margin-top:2px;">
                    {candidate.get('location','N/A')} · {candidate.get('years_of_experience',0)} yrs exp
                </div>
            </div>
            <div style="text-align:right; flex-shrink:0;">
                <div style="font-size:1.5rem; font-weight:900; color:{color}; 
                     font-family:'JetBrains Mono',monospace; line-height:1;">{fps:.3f}</div>
                <div style="color:#64748b; font-size:0.72rem; font-weight:500; margin-top:2px;">FPS Score</div>
            </div>
        </div>
        <div style="margin-top:0.8rem; display:flex; gap:0.5rem; flex-wrap:wrap; align-items:center;">
            {_mini_score_pill("🎯", "Fit", scores.get("semantic_fit",0))}
            {_mini_score_pill("🚀", "Momentum", scores.get("career_momentum",0))}
            {_mini_score_pill("🔬", "Behavior", scores.get("behavioral_evidence",0))}
            {_mini_score_pill("🧠", "Context", scores.get("contextual_intelligence",0))}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _mini_score_pill(icon: str, label: str, value: float) -> str:
    color = get_score_color(value)
    return f"""<span style="background:rgba(30,41,59,0.8);border:1px solid #334155;
        border-radius:999px;padding:0.2rem 0.6rem;font-size:0.75rem;color:#94a3b8;
        font-weight:500;">{icon} {label}: <span style="color:{color};font-weight:700;
        font-family:'JetBrains Mono',monospace;">{value:.2f}</span></span>"""


def render_metric_row(metrics: List[Dict]):
    """
    Renders a row of metric cards.
    Each metric dict: {"label": str, "value": str, "delta": str, "icon": str}
    """
    cols = st.columns(len(metrics))
    for col, m in zip(cols, metrics):
        with col:
            delta_html = ""
            if m.get("delta"):
                delta_color = "#10b981" if not m["delta"].startswith("-") else "#ef4444"
                delta_html = f'<div style="color:{delta_color};font-size:0.78rem;margin-top:0.2rem;">{m["delta"]}</div>'

            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.6rem; margin-bottom:0.3rem;">{m.get("icon","")}</div>
                <div class="metric-value">{m["value"]}</div>
                <div class="metric-label">{m["label"]}</div>
                {delta_html}
            </div>
            """, unsafe_allow_html=True)


def render_shap_waterfall(shap_data: Dict):
    """Renders a SHAP waterfall chart."""
    contributions = shap_data.get("contributions", {})
    baseline = shap_data.get("baseline", 0.5)
    fps = shap_data.get("fps", 0)

    labels = list(contributions.keys())
    values = list(contributions.values())
    colors = [get_score_color(v / 0.35) for v in values]  # Normalize by max possible

    fig = go.Figure(go.Waterfall(
        name="FPS Components",
        orientation="h",
        measure=["relative"] * len(labels) + ["total"],
        x=values + [fps],
        y=labels + ["FPS Score"],
        connector={"line": {"color": "#334155", "width": 1}},
        decreasing={"marker": {"color": "#ef4444", "line": {"color": "#dc2626", "width": 1}}},
        increasing={"marker": {"color": "#10b981", "line": {"color": "#059669", "width": 1}}},
        totals={"marker": {"color": "#6366f1", "line": {"color": "#4f46e5", "width": 2}}},
        textposition="outside",
        text=[f"+{v:.3f}" if v >= 0 else f"{v:.3f}" for v in values] + [f"{fps:.3f}"],
        textfont={"color": "#e2e8f0", "size": 11, "family": "JetBrains Mono"},
    ))

    fig.update_layout(
        height=320,
        margin=dict(l=20, r=20, t=20, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#1a1a2e",
        xaxis={"gridcolor": "#334155", "range": [0, 1.0], "tickfont": {"color": "#94a3b8"}},
        yaxis={"gridcolor": "#334155", "tickfont": {"color": "#e2e8f0", "size": 12}},
        showlegend=False,
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_momentum_timeline(skill_history: List[Dict]):
    """Renders skill acquisition timeline chart."""
    if not skill_history:
        st.info("No skill timeline data available.")
        return

    from datetime import datetime
    data = []
    for i, item in enumerate(skill_history):
        try:
            dt = datetime.strptime(item["acquired"], "%Y-%m")
            data.append({"date": dt, "skill": item["skill"], "count": i + 1})
        except Exception:
            continue

    if not data:
        return

    df = pd.DataFrame(data)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["count"],
        mode="lines+markers+text",
        text=df["skill"],
        textposition="top center",
        textfont={"size": 9, "color": "#a5b4fc"},
        line={"color": "#6366f1", "width": 2},
        marker={
            "size": 8, "color": "#8b5cf6",
            "line": {"color": "#6366f1", "width": 2}
        },
        fill="tozeroy",
        fillcolor="rgba(99,102,241,0.08)",
        name="Skills Acquired"
    ))
    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=10, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#1a1a2e",
        xaxis={"gridcolor": "#334155", "tickfont": {"color": "#94a3b8"}},
        yaxis={"gridcolor": "#334155", "tickfont": {"color": "#94a3b8"},
               "title": {"text": "Cumulative Skills", "font": {"color": "#94a3b8"}}},
        showlegend=False,
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_radar_chart(scores: Dict[str, float], name: str):
    """Renders a radar chart for score components."""
    categories = ["Semantic Fit", "Career Momentum", "Behavioral Evidence", "Contextual Intelligence"]
    values = [
        scores.get("semantic_fit", 0),
        scores.get("career_momentum", 0),
        scores.get("behavioral_evidence", 0),
        scores.get("contextual_intelligence", 0),
    ]
    values_pct = [v * 100 for v in values]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values_pct + [values_pct[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(99,102,241,0.15)",
        line={"color": "#6366f1", "width": 2},
        marker={"color": "#8b5cf6", "size": 6},
        name=name
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor="#334155",
                tickfont={"color": "#64748b", "size": 9},
                ticksuffix="%",
            ),
            angularaxis=dict(
                gridcolor="#334155",
                tickfont={"color": "#94a3b8", "size": 11},
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        showlegend=False,
        height=300,
        margin=dict(l=40, r=40, t=30, b=30),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_sidebar_logo():
    """Renders the app logo and branding in sidebar."""
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem;">
        <div style="font-size:2rem; margin-bottom:0.3rem;">🚀</div>
        <div style="font-size:1.1rem; font-weight:800; 
             background:linear-gradient(135deg,#6366f1,#8b5cf6,#06b6d4);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;
             line-height:1.2;">CareerTrajectory AI</div>
        <div style="color:#475569; font-size:0.72rem; margin-top:0.3rem; font-style:italic;">
            Talent Intelligence Platform
        </div>
        <div style="height:1px; background:linear-gradient(90deg,transparent,#334155,transparent);
             margin: 1rem 0 0;"></div>
    </div>
    """, unsafe_allow_html=True)


def fps_color_gradient(fps: float) -> str:
    """Returns a CSS gradient color string based on FPS."""
    if fps >= 0.80:
        return "linear-gradient(135deg, #10b981, #059669)"
    elif fps >= 0.65:
        return "linear-gradient(135deg, #6366f1, #8b5cf6)"
    elif fps >= 0.50:
        return "linear-gradient(135deg, #f59e0b, #d97706)"
    else:
        return "linear-gradient(135deg, #ef4444, #dc2626)"
