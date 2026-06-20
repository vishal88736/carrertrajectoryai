"""
CareerTrajectory AI — Page 2: Candidate Ranking
Full ranked list with FPS scores, filters, and upload capability.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

st.set_page_config(page_title="Rankings · CareerTrajectory AI", page_icon="📊", layout="wide")

from ui.components import (inject_css, render_page_header, render_score_bars,
                            render_fps_gauge, render_radar_chart, get_score_color,
                            render_skills_tags, render_candidate_card_mini)
from data.sample_data import get_candidates, get_jobs, get_job_by_id
from backend.scoring_engine import rank_candidates, detect_hidden_gems, generate_shap_values
from backend.resume_parser import parse_resume

inject_css()

import plotly.graph_objects as go
import pandas as pd

# ── State ─────────────────────────────────────────────────────────────────────
if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = "j001"
if "custom_candidates" not in st.session_state:
    st.session_state.custom_candidates = []

candidates = get_candidates() + st.session_state.custom_candidates
job = get_job_by_id(st.session_state.selected_job_id)
ranked = rank_candidates(candidates, job)

render_page_header(
    "Candidate Rankings",
    f"FPS-ranked candidates for: {job['title']} @ {job['company']}",
    "📊"
)

# ── Upload Resume Section ─────────────────────────────────────────────────────
with st.expander("📤 Upload New Resume to Rank", expanded=False):
    st.markdown("""
    <div class="info-box">
        <strong>🤖 Resume Intelligence Agent</strong> — Upload a PDF or DOCX resume.
        The AI will extract skills, parse timeline, compute FPS, and rank the candidate.
    </div>
    """, unsafe_allow_html=True)

    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Drop resume here",
            type=["pdf", "docx", "txt"],
            help="Supports PDF, DOCX, and plain text resumes"
        )
    with col_up2:
        manual_name = st.text_input("Candidate Name (optional)", placeholder="Auto-extracted from resume")
        manual_location = st.text_input("Location (optional)", placeholder="City, Country")

    if uploaded_file and st.button("🚀 Parse & Rank Resume", use_container_width=True):
        with st.spinner("🤖 Resume Intelligence Agent processing..."):
            file_bytes = uploaded_file.read()
            file_type = uploaded_file.name.split(".")[-1]
            parsed = parse_resume(file_bytes, file_type)

            if manual_name:
                parsed["name"] = manual_name
            if manual_location:
                parsed["location"] = manual_location

            # Build a candidate object from parsed data
            new_candidate = {
                "id": f"c_upload_{len(st.session_state.custom_candidates)+1}",
                "name": parsed.get("name", "Uploaded Candidate"),
                "email": parsed.get("email", ""),
                "location": parsed.get("location", "Unknown"),
                "years_of_experience": parsed.get("years_of_experience", 0),
                "education": parsed.get("education", []),
                "skills": parsed.get("skills", {"current": [], "learning": [], "history": []}),
                "certifications": parsed.get("certifications", []),
                "experience": [],
                "projects": [],
                "behavioral_signals": {},
                "scores": {"semantic_fit": 0, "career_momentum": 0, "behavioral_evidence": 0,
                           "contextual_intelligence": 0, "fps": 0},
                "hidden_gem": False,
            }

            st.session_state.custom_candidates.append(new_candidate)
            st.success(f"✅ Successfully parsed resume for **{new_candidate['name']}**!")
            st.json({
                "Name": new_candidate["name"],
                "Skills Found": new_candidate["skills"]["current"][:10],
                "Years of Exp": new_candidate["years_of_experience"],
                "Certifications": len(new_candidate["certifications"]),
            })
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ── Filters Row ───────────────────────────────────────────────────────────────
st.markdown("### 🔧 Filter & Sort")
fcol1, fcol2, fcol3, fcol4 = st.columns(4)

with fcol1:
    min_fps = st.slider("Min FPS Score", 0.0, 1.0, 0.0, 0.05)
with fcol2:
    max_yoe = st.slider("Max Experience (Years)", 0, 15, 15)
with fcol3:
    show_gems_only = st.checkbox("💎 Hidden Gems Only", value=False)
with fcol4:
    sort_by = st.selectbox("Sort By", ["FPS Score", "Career Momentum", "Semantic Fit", "Behavioral Evidence"])

sort_key_map = {
    "FPS Score": "fps",
    "Career Momentum": "career_momentum",
    "Semantic Fit": "semantic_fit",
    "Behavioral Evidence": "behavioral_evidence"
}
sort_key = sort_key_map[sort_by]

# Apply filters
filtered = [c for c in ranked
            if c["scores"]["fps"] >= min_fps
            and c.get("years_of_experience", 0) <= max_yoe
            and (not show_gems_only or c.get("hidden_gem", False))]

filtered.sort(key=lambda x: x["scores"].get(sort_key, 0), reverse=True)
for i, c in enumerate(filtered):
    c["rank"] = i + 1

st.markdown(f"<div style='color:#64748b;font-size:0.85rem;margin-bottom:1rem;'>Showing {len(filtered)} of {len(ranked)} candidates</div>", unsafe_allow_html=True)

# ── Comparison Table ──────────────────────────────────────────────────────────
with st.expander("📋 Comparison Table View", expanded=False):
    df = pd.DataFrame([{
        "Rank": c["rank"],
        "Name": c["name"],
        "FPS": f"{c['scores']['fps']:.3f}",
        "Semantic Fit": f"{c['scores']['semantic_fit']:.2f}",
        "Momentum": f"{c['scores']['career_momentum']:.2f}",
        "Behavior": f"{c['scores']['behavioral_evidence']:.2f}",
        "Context": f"{c['scores']['contextual_intelligence']:.2f}",
        "YoE": c.get("years_of_experience", 0),
        "Gem": "💎" if c.get("hidden_gem") else "",
    } for c in filtered])
    st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Candidate Cards ───────────────────────────────────────────────────────────
if not filtered:
    st.markdown("""
    <div class="info-box" style="text-align:center;">
        <div style="font-size:2rem; margin-bottom:0.5rem;">🔍</div>
        <strong>No candidates match the current filters.</strong>
        <div style="color:#64748b; margin-top:0.3rem;">Try adjusting the FPS threshold or experience filter.</div>
    </div>
    """, unsafe_allow_html=True)
else:
    for c in filtered:
        fps = c["scores"]["fps"]
        color = get_score_color(fps)
        is_gem = c.get("hidden_gem", False)
        rank = c.get("rank", "—")

        # Card container
        gem_style = "border-color:#f59e0b; box-shadow:0 0 20px rgba(245,158,11,0.15);" if is_gem else ""
        st.markdown(f"""
        <div class="candidate-card" style="{gem_style} position:relative;">
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            main_col, score_col = st.columns([3, 1])

            with main_col:
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.8rem;">
                    <div style="width:42px;height:42px;border-radius:50%;
                        background:{'linear-gradient(135deg,#f59e0b,#fbbf24)' if rank==1 else 'linear-gradient(135deg,#6366f1,#8b5cf6)'};
                        display:flex;align-items:center;justify-content:center;
                        font-weight:800;font-size:0.9rem;flex-shrink:0;
                        color:{'#000' if rank==1 else 'white'};">
                        {'🥇' if rank==1 else '#'+str(rank)}
                    </div>
                    <div>
                        <div style="font-weight:700;font-size:1.05rem;color:#e2e8f0;">
                            {c['name']}
                            {'<span style="background:linear-gradient(135deg,#f59e0b,#fbbf24);color:#000;font-size:0.68rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:999px;margin-left:0.5rem;">💎 HIDDEN GEM</span>' if is_gem else ''}
                        </div>
                        <div style="color:#64748b;font-size:0.8rem;margin-top:2px;">
                            📍 {c.get('location','N/A')} · 💼 {c.get('years_of_experience',0)} years experience
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Skills
                st.markdown("<div style='margin-bottom:0.5rem;color:#64748b;font-size:0.78rem;font-weight:600;'>SKILLS</div>", unsafe_allow_html=True)
                render_skills_tags(c["skills"]["current"][:8], job_required=job["required_skills"])
                if c["skills"].get("learning"):
                    st.markdown("<div style='color:#64748b;font-size:0.72rem;margin-top:0.3rem;'>Learning →</div>", unsafe_allow_html=True)
                    render_skills_tags(c["skills"]["learning"][:4], tag_type="learning")

            with score_col:
                st.markdown(f"""
                <div style="text-align:center;padding:0.5rem;">
                    <div style="font-size:2.8rem;font-weight:900;color:{color};
                         font-family:'JetBrains Mono',monospace;line-height:1;">
                        {fps:.3f}
                    </div>
                    <div style="color:#64748b;font-size:0.72rem;font-weight:600;
                         text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.7rem;">
                        Future Potential Score
                    </div>
                </div>
                """, unsafe_allow_html=True)
                render_score_bars(c["scores"])

            # Action row
            btn_col1, btn_col2, btn_col3 = st.columns(3)
            with btn_col1:
                if st.button(f"👤 View Profile", key=f"profile_{c['id']}", use_container_width=True):
                    st.session_state.selected_candidate_id = c["id"]
                    st.switch_page("pages/03_Profile.py")
            with btn_col2:
                if st.button(f"🔮 Skill Gap Sim", key=f"gap_{c['id']}", use_container_width=True):
                    st.session_state.selected_candidate_id = c["id"]
                    st.switch_page("pages/05_SkillGap.py")
            with btn_col3:
                shap_data = generate_shap_values(c)
                with st.expander(f"🔍 SHAP Explanation", expanded=False):
                    st.markdown(f"""
                    <div class="info-box">
                        {shap_data['explanation']}
                    </div>
                    """, unsafe_allow_html=True)
                    if shap_data.get("counterfactuals"):
                        st.markdown("**💡 Counterfactual Insights:**")
                        for cf in shap_data["counterfactuals"]:
                            st.markdown(f"- {cf}")

        st.markdown("<hr style='border-color:#1e293b;margin:0.5rem 0 1rem;'>", unsafe_allow_html=True)
