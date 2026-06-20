"""
CareerTrajectory AI — Main Streamlit Entry Point
"Don't hire the best candidate today. Hire the fastest-growing candidate for tomorrow."
"""

import streamlit as st
import sys
import os

# ── Path Setup ────────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Page Config (MUST be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="CareerTrajectory AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": None,
        "Report a bug": None,
        "About": "CareerTrajectory AI — Next-Generation Talent Intelligence Platform"
    }
)

from ui.components import inject_css, render_sidebar_logo, GLOBAL_CSS
inject_css()

# ── Session State Initialization ──────────────────────────────────────────────
if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = "j001"
if "selected_candidate_id" not in st.session_state:
    st.session_state.selected_candidate_id = None
if "uploaded_resume" not in st.session_state:
    st.session_state.uploaded_resume = None
if "copilot_history" not in st.session_state:
    st.session_state.copilot_history = []
if "custom_candidates" not in st.session_state:
    st.session_state.custom_candidates = []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar_logo()

    st.markdown("### Navigation")

    pages = [
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
        st.markdown(f"""
        <a href="/{path.split('/')[-1].replace('.py','').replace('0','').lstrip('_1234567890')}" 
           style="text-decoration:none;">
        <div class="sidebar-nav-item">{icon} {name}</div>
        </a>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Job selector
    from data.sample_data import get_jobs
    jobs = get_jobs()
    job_names = {j["id"]: f"{j['title']} @ {j['company']}" for j in jobs}
    selected_job = st.selectbox(
        "🎯 Active Job Requisition",
        options=list(job_names.keys()),
        format_func=lambda x: job_names[x],
        index=0,
        key="sidebar_job_select"
    )
    st.session_state.selected_job_id = selected_job

    st.markdown("---")
    st.markdown("""
    <div style="color:#475569; font-size:0.72rem; text-align:center; padding:0.5rem 0;">
        <div style="margin-bottom:0.3rem;">🔒 Enterprise Grade · GDPR Compliant</div>
        <div>Bias-Mitigated · Explainable AI</div>
        <div style="margin-top:0.5rem; color:#334155;">v1.0.0 · CareerTrajectory AI</div>
    </div>
    """, unsafe_allow_html=True)

# ── Hero Landing Page ─────────────────────────────────────────────────────────

st.markdown("""
<div style="text-align:center; padding: 3rem 0 2rem; animate-fade-in;">
    <div style="font-size:4rem; margin-bottom:0.5rem;">🚀</div>
    <h1 style="font-size:3rem; font-weight:900; margin-bottom:0.5rem;
        background:linear-gradient(135deg,#6366f1,#8b5cf6,#06b6d4);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;">
        CareerTrajectory AI
    </h1>
    <p style="color:#94a3b8; font-size:1.15rem; font-style:italic; margin-bottom:2rem;">
        "Don't hire the best candidate today.<br>Hire the fastest-growing candidate for tomorrow."
    </p>
</div>
""", unsafe_allow_html=True)

# ── Platform Stats ────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

stats = [
    (col1, "7", "AI Agents", "🤖"),
    (col2, "FPS™", "Future Potential Score", "📊"),
    (col3, "4D", "Scoring Dimensions", "🎯"),
    (col4, "SHAP", "Explainable AI", "🔍"),
    (col5, "0 Bias", "Fairness Guaranteed", "⚖️"),
]

for col, val, label, icon in stats:
    with col:
        st.markdown(f"""
        <div class="metric-card" style="padding:1.5rem 1rem;">
            <div style="font-size:1.8rem; margin-bottom:0.4rem;">{icon}</div>
            <div class="metric-value" style="font-size:1.8rem;">{val}</div>
            <div class="metric-label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Action Cards ────────────────────────────────────────────────────────
st.markdown("### ⚡ Quick Actions")

qcol1, qcol2, qcol3 = st.columns(3)

with qcol1:
    st.markdown("""
    <div class="ct-card" style="text-align:center; cursor:pointer;">
        <div style="font-size:2.5rem; margin-bottom:0.7rem;">📊</div>
        <h3 style="color:#e2e8f0; margin:0 0 0.5rem;">View Rankings</h3>
        <p style="color:#64748b; font-size:0.88rem; margin:0;">
            See FPS-ranked candidates for your active job requisition.
            Powered by Career Momentum Engine.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Rankings →", key="btn_rankings", use_container_width=True):
        st.switch_page("pages/02_Ranking.py")

with qcol2:
    st.markdown("""
    <div class="ct-card" style="text-align:center; cursor:pointer;">
        <div style="font-size:2.5rem; margin-bottom:0.7rem;">💎</div>
        <h3 style="color:#e2e8f0; margin:0 0 0.5rem;">Discover Hidden Gems</h3>
        <p style="color:#64748b; font-size:0.88rem; margin:0;">
            Find high-potential candidates that traditional ATS systems would miss.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Find Gems →", key="btn_gems", use_container_width=True):
        st.switch_page("pages/04_HiddenGems.py")

with qcol3:
    st.markdown("""
    <div class="ct-card" style="text-align:center; cursor:pointer;">
        <div style="font-size:2.5rem; margin-bottom:0.7rem;">🤖</div>
        <h3 style="color:#e2e8f0; margin:0 0 0.5rem;">Recruiter Copilot</h3>
        <p style="color:#64748b; font-size:0.88rem; margin:0;">
            Ask AI anything about your candidate pool. Natural language insights.
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Open Copilot →", key="btn_copilot", use_container_width=True):
        st.switch_page("pages/07_Copilot.py")

st.markdown("<br>", unsafe_allow_html=True)

# ── FPS Formula Explainer ─────────────────────────────────────────────────────
st.markdown("### 📐 Future Potential Score (FPS) Formula")

col_formula, col_vs = st.columns([3, 2])

with col_formula:
    st.markdown("""
    <div class="ct-card">
        <h3 style="color:#a5b4fc; margin-bottom:1rem;">🔬 FPS = Weighted Multi-Dimensional Score</h3>
        <div style="font-family:'JetBrains Mono',monospace; font-size:0.95rem; line-height:2;">
            <div style="color:#e2e8f0;">
                <span style="color:#6366f1; font-weight:700;">FPS</span> = 
                <span style="color:#10b981;">0.35</span> × Semantic Fit
            </div>
            <div style="color:#e2e8f0; padding-left:2.5rem;">
                + <span style="color:#10b981;">0.30</span> × Career Momentum
            </div>
            <div style="color:#e2e8f0; padding-left:2.5rem;">
                + <span style="color:#10b981;">0.20</span> × Behavioral Evidence
            </div>
            <div style="color:#e2e8f0; padding-left:2.5rem;">
                + <span style="color:#10b981;">0.15</span> × Contextual Intelligence
            </div>
        </div>
        <div style="margin-top:1rem; padding-top:1rem; border-top:1px solid #334155;">
            <div style="color:#64748b; font-size:0.82rem;">
                <strong style="color:#94a3b8;">Career Momentum</strong> = √(Velocity × Direction Alignment)<br>
                <strong style="color:#94a3b8;">Career Velocity</strong> = Rate of skill acquisition (skills/6 months)<br>
                <strong style="color:#94a3b8;">Direction Alignment</strong> = Recency-weighted match to job domain
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_vs:
    st.markdown("""
    <div class="ct-card" style="border-color:#ef4444;">
        <h4 style="color:#f87171; margin-bottom:0.8rem;">❌ Traditional ATS</h4>
        <div style="color:#64748b; font-size:0.85rem; line-height:1.8;">
            • Keyword matching only<br>
            • Ignores growth potential<br>
            • Penalizes career switchers<br>
            • No behavioral validation<br>
            • Black-box decisions<br>
            • Can't adapt to new skills
        </div>
    </div>
    <div class="ct-card" style="border-color:#10b981; margin-top:0;">
        <h4 style="color:#6ee7b7; margin-bottom:0.8rem;">✅ CareerTrajectory AI</h4>
        <div style="color:#94a3b8; font-size:0.85rem; line-height:1.8;">
            • Semantic capability matching<br>
            • Career Momentum Engine<br>
            • Rewards fast learners<br>
            • GitHub / Kaggle validation<br>
            • SHAP explainability<br>
            • Continuous learning
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── 7 Agent Architecture ──────────────────────────────────────────────────────
st.markdown("### 🤖 Multi-Agent Architecture")

agents = [
    ("📄", "Resume Intelligence", "Parses PDFs/DOCX. Extracts skills, projects, timelines, achievements."),
    ("💼", "Job Intelligence", "Understands JD semantics. Creates requirement graphs for matching."),
    ("🚀", "Career Momentum", "Computes velocity × alignment. Identifies growth direction."),
    ("🔬", "Behavior Validator", "Validates GitHub, Kaggle, LeetCode, Codeforces signals."),
    ("🏆", "Talent Ranker", "Combines all signals → FPS. Uses LightGBM/LambdaMART."),
    ("🔍", "Explainability", "SHAP explanations, counterfactuals, recruiter-friendly insights."),
    ("💬", "Recruiter Copilot", "Natural language Q&A about candidates. Hidden gem discovery."),
]

agent_cols = st.columns(4)
for i, (icon, name, desc) in enumerate(agents):
    col = agent_cols[i % 4]
    with col:
        st.markdown(f"""
        <div class="ct-card" style="padding:1.2rem; text-align:center; min-height:160px;">
            <div style="font-size:1.8rem; margin-bottom:0.5rem;">{icon}</div>
            <div style="font-weight:700; color:#a5b4fc; font-size:0.9rem; margin-bottom:0.4rem;">
                Agent {i+1}: {name}
            </div>
            <div style="color:#64748b; font-size:0.78rem; line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:2rem 0 1rem; border-top:1px solid #1e293b; color:#334155; font-size:0.8rem;">
    Built with ❤️ by the CareerTrajectory AI Team · 
    <span style="color:#475569;">Powered by Multi-Agent AI, Career Momentum Engine, SHAP Explainability</span>
</div>
""", unsafe_allow_html=True)
