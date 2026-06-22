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

from data.database import (
    save_custom_candidates_batch, 
    get_upload_history, 
    load_custom_candidates_by_batch
)

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

def map_candidate_json_to_internal(c: dict) -> dict:
    import random
    from datetime import datetime
    profile = c.get("profile", {})
    
    # Map education
    education = []
    for edu in c.get("education", []):
        degree = edu.get("degree", "")
        field = edu.get("field_of_study", "")
        full_degree = f"{degree} in {field}" if field else degree
        education.append({
            "degree": full_degree,
            "institution": edu.get("institution", ""),
            "year": edu.get("end_year", edu.get("start_year", ""))
        })
        
    # Map career history to experience
    experience = []
    for job in c.get("career_history", []):
        start = job.get("start_date", "")
        if start:
            start = start[:7] # YYYY-MM
        end = job.get("end_date", "")
        if end:
            end = end[:7]
        else:
            end = "present" if job.get("is_current") else "Unknown"
        experience.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "start": start,
            "end": end,
            "description": job.get("description", "")
        })
        
    # Map skills
    skills_list = c.get("skills", [])
    current_skills = []
    skills_history = []
    for s in skills_list:
        name = s.get("name", "")
        if not name:
            continue
        current_skills.append(name)
        # Construct history using duration_months
        duration = s.get("duration_months", 0)
        # Estimate acquired date
        acq_year = 2026
        acq_month = 6 - duration
        while acq_month <= 0:
            acq_month += 12
            acq_year -= 1
        skills_history.append({
            "skill": name,
            "acquired": f"{acq_year}-{acq_month:02d}"
        })
        
    # Map certifications
    certifications = []
    for cert in c.get("certifications", []):
        certifications.append({
            "name": cert.get("name", ""),
            "issuer": cert.get("issuer", "Unknown"),
            "date": str(cert.get("year", ""))
        })
        
    # Map behavioral signals from redrob_signals
    redrob = c.get("redrob_signals", {})
    behavioral_signals = {
        "certifications_count": len(certifications),
        "open_source_contributions": int(redrob.get("github_activity_score", 0) * 1.5) if redrob.get("github_activity_score", -1) > 0 else 0,
        "stackoverflow_reputation": int(redrob.get("profile_completeness_score", 0) * 15)
    }
    
    # Check github activity
    github_score = redrob.get("github_activity_score", -1)
    if github_score > 0:
        behavioral_signals["github"] = {
            "username": profile.get("anonymized_name", "user").lower().replace(" ", "") + "_dev",
            "commit_frequency": github_score * 2.0,
            "public_repos": int(github_score * 3),
            "followers": int(github_score * 12),
            "stars_earned": int(github_score * 45),
            "streak_days": int(github_score * 25),
            "top_languages": [s for s in current_skills[:3]]
        }
        
    # Check leetcode / skill assessment scores
    assessments = redrob.get("skill_assessment_scores", {})
    if assessments:
        avg_score = sum(assessments.values()) / len(assessments)
        behavioral_signals["leetcode"] = {
            "username": profile.get("anonymized_name", "user").lower().replace(" ", "") + "_codes",
            "problems_solved": int(avg_score * 4.5),
            "contest_rating": int(1000 + avg_score * 10),
            "contest_rank_percentile": int(avg_score)
        }
        
    # Projects: we can create some mock projects based on their headline & skills
    projects = []
    if current_skills:
        # Create a mock project using top skills
        proj_skills = current_skills[:3]
        projects.append({
            "name": f"Open Source {proj_skills[0]} Engine",
            "description": f"A high-performance implementation of an engine focusing on {', '.join(proj_skills)}. Feature-rich and highly optimized.",
            "skills": proj_skills,
            "url": f"https://github.com/candidate/{proj_skills[0].lower()}-engine",
            "stars": int(github_score * 10) if github_score > 0 else 0
        })

    # Assemble candidate
    mapped = {
        "id": c.get("candidate_id", f"c_json_{random.randint(1000, 9999)}"),
        "name": profile.get("anonymized_name", "Anonymous Candidate"),
        "email": f"{profile.get('anonymized_name', 'candidate').lower().replace(' ', '.')}@example.com",
        "location": f"{profile.get('location', 'Unknown')}, {profile.get('country', '')}".strip(", "),
        "years_of_experience": profile.get("years_of_experience", 0),
        "education": education,
        "skills": {
            "current": current_skills,
            "learning": current_skills[-3:] if len(current_skills) > 3 else [],
            "history": skills_history
        },
        "experience": experience,
        "certifications": certifications,
        "projects": projects,
        "behavioral_signals": behavioral_signals,
        "scores": {"semantic_fit": 0, "career_momentum": 0, "behavioral_evidence": 0, "contextual_intelligence": 0, "fps": 0},
        "hidden_gem": False
    }
    return mapped

# ── Upload Resume Section ─────────────────────────────────────────────────────

# Show persistent success message from previous upload (survives st.rerun)
if st.session_state.get("_upload_success"):
    msg = st.session_state._upload_success
    if msg.get("is_json"):
        st.success(f"✅ Successfully loaded and ranked **{msg['count']}** candidates from candidate JSON data!")
    else:
        st.success(f"✅ Successfully parsed & ranked **{msg['name']}** — found **{msg['skills_count']}** skills, "
                   f"**{msg['yoe']}** years experience, **{msg['certs']}** certifications!")
    if st.button("✕ Dismiss", key="dismiss_upload_success"):
        del st.session_state._upload_success
        st.rerun()

with st.expander("📤 Upload New Resume or Candidate JSON", expanded=False):
    st.markdown("""
    <div class="info-box">
        <strong>🤖 Resume & Candidate Intelligence Agent</strong> — Upload a PDF/DOCX/TXT resume or a structured candidate JSON file.
        The AI will parse, map candidate schemas, compute FPS, and rank them.
    </div>
    """, unsafe_allow_html=True)
    
    # ── History Selector ──
    history = get_upload_history()
    if history:
        st.markdown("##### 📂 Load Past Upload")
        hist_options = {"": "Select a past upload..."}
        for h in history:
            # e.g., "resume.pdf (2026-06-21 14:30) - 1 candidates"
            lbl = f"{h['batch_name']} ({h['timestamp'][:16].replace('T', ' ')}) - {h['count']} candidate(s)"
            hist_options[h['batch_name']] = lbl
            
        selected_batch = st.selectbox("Restore previous candidates", options=list(hist_options.keys()), format_func=lambda x: hist_options[x])
        if selected_batch and st.button("Restore Selected Batch", use_container_width=True):
            with st.spinner(f"Loading {selected_batch}..."):
                restored = load_custom_candidates_by_batch(selected_batch)
                st.session_state.custom_candidates = restored
                st.rerun()
        st.markdown("<hr style='border-color:#334155;margin:0.8rem 0;'>", unsafe_allow_html=True)

    # ── Load sample candidate JSON button ──
    st.markdown("##### ⚡ Quick Load Sample Candidates")
    if st.button("📥 Load 50 Candidates from sample_candidates.json", key="load_sample_json_btn", use_container_width=True):
        with st.spinner("Loading and mapping 50 sample candidates..."):
            try:
                import json
                file_path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_candidates.json")
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                if not isinstance(data, list):
                    data = [data]
                
                st.session_state.custom_candidates = []  # Clear previous
                new_batch = []
                
                for c_data in data:
                    new_candidate = map_candidate_json_to_internal(c_data)
                    st.session_state.custom_candidates.append(new_candidate)
                    new_batch.append(new_candidate)
                
                if new_batch:
                    save_custom_candidates_batch(new_batch, "sample_candidates.json")
                    
                    st.session_state._upload_success = {
                        "is_json": True,
                        "count": len(new_batch)
                    }
                    st.rerun()
                else:
                    st.info("ℹ️ 50 Candidates from sample_candidates.json are already loaded.")
            except Exception as e:
                st.error(f"❌ Failed to load local sample JSON: {str(e)}")

    st.markdown("<hr style='border-color:#334155;margin:0.8rem 0;'>", unsafe_allow_html=True)
    st.markdown("##### 📁 Upload Custom File")

    col_up1, col_up2 = st.columns([2, 1])
    with col_up1:
        uploaded_file = st.file_uploader(
            "Drop resume or candidate JSON here",
            type=["pdf", "docx", "txt", "json"],
            help="Supports PDF, DOCX, plain text resumes, or candidate JSON files"
        )
    with col_up2:
        manual_name = st.text_input("Candidate Name (optional)", placeholder="Auto-extracted from resume")
        manual_location = st.text_input("Location (optional)", placeholder="City, Country")

    if uploaded_file and st.button("🚀 Parse & Rank Resume / JSON", use_container_width=True):
        with st.spinner("🤖 Processing uploaded file..."):
            file_bytes = uploaded_file.read()
            file_name = uploaded_file.name
            file_type = file_name.split(".")[-1].lower()
            
            if file_type == "json":
                try:
                    import json
                    data = json.loads(file_bytes.decode("utf-8"))
                    if not isinstance(data, list):
                        data = [data]
                    
                    st.session_state.custom_candidates = []  # Clear previous
                    new_batch = []
                    
                    for c_data in data:
                        new_candidate = map_candidate_json_to_internal(c_data)
                        st.session_state.custom_candidates.append(new_candidate)
                        new_batch.append(new_candidate)
                    
                    if new_batch:
                        save_custom_candidates_batch(new_batch, file_name)
                    
                    st.session_state._upload_success = {
                        "is_json": True,
                        "count": len(new_batch)
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to parse JSON candidate file: {str(e)}")
            else:
                parsed = parse_resume(file_bytes, file_type)
                
                # ── Check for parse errors ──
                if "error" in parsed:
                    st.error(f"❌ **Resume Parsing Failed:** {parsed['error']}")
                    st.markdown("""
                    <div style="background:#1a1a2e;border:1px solid #ef4444;border-radius:10px;
                         padding:1rem;margin-top:0.5rem;">
                        <strong style="color:#f87171;">💡 Troubleshooting Tips:</strong>
                        <ul style="color:#94a3b8;font-size:0.85rem;margin-top:0.5rem;">
                            <li>Make sure the PDF is text-based, not a scanned image</li>
                            <li>Try saving your resume as a different format (PDF → DOCX or TXT)</li>
                            <li>Ensure the file isn't password-protected or corrupted</li>
                            <li>Try a plain text (.txt) version of your resume</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                else:
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
                        "experience": parsed.get("experience", []),
                        "projects": parsed.get("projects", []),
                        "github_url": parsed.get("github_url", ""),
                        "github_username": parsed.get("github_username", None),
                        "behavioral_signals": {
                            "certifications_count": len(parsed.get("certifications", [])),
                            "github_active": parsed.get("behavioral_signals", {}).get("github_active", False),
                            "has_projects": parsed.get("behavioral_signals", {}).get("has_projects", False),
                            "has_certifications": parsed.get("behavioral_signals", {}).get("has_certifications", False),
                        },
                        "scores": {"semantic_fit": 0, "career_momentum": 0, "behavioral_evidence": 0,
                                   "contextual_intelligence": 0, "fps": 0},
                        "hidden_gem": False,
                    }
    
                    st.session_state.custom_candidates = [new_candidate]  # Clear previous and add new
                    save_custom_candidates_batch([new_candidate], file_name)
    
                    # Store success info in session state so it survives rerun
                    st.session_state._upload_success = {
                        "name": new_candidate["name"],
                        "skills_count": len(new_candidate["skills"]["current"]),
                        "yoe": new_candidate["years_of_experience"],
                        "certs": len(new_candidate["certifications"]),
                    }
    
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
with st.expander("📋 Comparison Table View", expanded=True):
    if not filtered:
        st.info("No candidates match the current filters.")
    else:
        df = pd.DataFrame([{
            "Rank": c["rank"],
            "Name": c["name"],
            "FPS": f"{c['scores']['fps']:.3f}",
            "Semantic Fit": f"{c['scores']['semantic_fit']:.2f}",
            "Trajectory": f"{c['scores']['career_momentum']:.2f}",
            "Behavioral": f"{c['scores']['behavioral_evidence']:.2f}",
            "Proj Quality": f"{c['scores']['contextual_intelligence']:.2f}",
            "Future Growth": f"{c['scores']['career_momentum']*0.3 + c['scores']['fps']*0.7:.2f}",
            "YoE": c.get("years_of_experience", 0),
            "Gem": "💎" if c.get("hidden_gem") else "",
        } for c in filtered])
        st.dataframe(df, use_container_width=True, hide_index=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Candidate Cards ───────────────────────────────────────────────────────────
if not ranked:
    st.markdown("""
    <div class="info-box" style="text-align:center;">
        <div style="font-size:2rem; margin-bottom:0.5rem;">📥</div>
        <strong>No candidates available.</strong>
        <div style="color:#64748b; margin-top:0.3rem;">Upload a resume or JSON above, or enable Sample Data in the sidebar.</div>
    </div>
    """, unsafe_allow_html=True)
elif not filtered:
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


        with st.container():
            main_col, score_col = st.columns([3, 1])

            with main_col:
                # Header: Name and rank
                gem_badge = " 💎 HIDDEN GEM" if is_gem else ""
                rank_icon = "🥇" if rank == 1 else f"#{rank}"
                st.markdown(f"### {rank_icon} {c['name']}{gem_badge}")
                
                # Location and experience
                st.markdown(f"📍 {c.get('location','N/A')} · 💼 {c.get('years_of_experience',0)} years experience")
                
                # Skills
                st.markdown("**SKILLS**")
                render_skills_tags(c["skills"]["current"][:8], job_required=job["required_skills"])
                if c["skills"].get("learning"):
                    st.markdown("*Learning →*")
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
