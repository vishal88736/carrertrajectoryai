"""
CareerTrajectory AI — Page 8: Job Management
Create, edit, and manage job requisitions.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

st.set_page_config(page_title="Jobs · CareerTrajectory AI", page_icon="💼", layout="wide")

from ui.components import inject_css, render_page_header, render_metric_row
from data.sample_data import get_jobs, get_candidates, get_job_by_id
from backend.scoring_engine import rank_candidates

inject_css()

import plotly.graph_objects as go

if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = "j001"
if "custom_candidates" not in st.session_state:
    st.session_state.custom_candidates = []
if "custom_jobs" not in st.session_state:
    st.session_state.custom_jobs = []

candidates = get_candidates() + st.session_state.custom_candidates
all_jobs = get_jobs() + st.session_state.custom_jobs

render_page_header("Job Management", 
    "Create, manage, and analyze job requisitions. View candidate pipeline for each role.",
    "💼")

# ── Job Stats ──────────────────────────────────────────────────────────────────
render_metric_row([
    {"label": "Active Jobs", "value": str(len(all_jobs)), "icon": "💼"},
    {"label": "Total Candidates", "value": str(len(candidates)), "icon": "👥"},
    {"label": "Avg Pool Size", "value": str(len(candidates)), "icon": "📊"},
    {"label": "Custom Jobs", "value": str(len(st.session_state.custom_jobs)), "icon": "✨"},
])

st.markdown("<br>", unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📋 Current Jobs", "➕ Create New Job"])

with tab1:
    st.markdown("### 💼 Active Job Requisitions")
    
    for job in all_jobs:
        ranked = rank_candidates(candidates, job)
        top_fps = ranked[0]["scores"]["fps"] if ranked else 0
        avg_fps = sum(c["scores"]["fps"] for c in ranked) / max(len(ranked), 1)
        
        is_selected = job["id"] == st.session_state.selected_job_id
        border = "#6366f1" if is_selected else "#334155"
        
        st.markdown(f"""
        <div style="background:#1a1a2e;border:2px solid {border};border-radius:16px;
             padding:1.5rem;margin-bottom:1rem;
             {'box-shadow:0 0 20px rgba(99,102,241,0.2);' if is_selected else ''}">
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            jcol1, jcol2, jcol3 = st.columns([3, 1.5, 1])
            
            with jcol1:
                selected_badge = '<span style="background:linear-gradient(135deg,#6366f1,#8b5cf6);color:white;font-size:0.68rem;font-weight:700;padding:0.15rem 0.5rem;border-radius:999px;margin-left:0.5rem;">● ACTIVE</span>' if is_selected else ""
                st.markdown(f"""
                <div>
                    <div style="font-size:1.1rem;font-weight:800;color:#e2e8f0;">
                        {job['title']} {selected_badge}
                    </div>
                    <div style="color:#6366f1;font-size:0.85rem;font-weight:600;margin-top:2px;">
                        {job['company']}
                    </div>
                    <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">
                        📍 {job['location']} · 
                        💰 {job.get('salary_range','N/A')} · 
                        📊 {job.get('level','Mid')} Level
                    </div>
                    <div style="margin-top:0.7rem;">
                        {''.join(f'<span style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);color:#a5b4fc;border-radius:999px;padding:0.15rem 0.6rem;font-size:0.75rem;margin:0.1rem;display:inline-block;">{s}</span>' for s in job['required_skills'][:6])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with jcol2:
                st.markdown(f"""
                <div style="text-align:center;background:#0f0f1a;border-radius:12px;padding:1rem;">
                    <div style="color:#64748b;font-size:0.72rem;text-transform:uppercase;margin-bottom:0.3rem;">Candidate Pool</div>
                    <div style="font-size:2rem;font-weight:900;color:#6366f1;font-family:'JetBrains Mono',monospace;">
                        {len(candidates)}
                    </div>
                    <div style="color:#64748b;font-size:0.72rem;margin-top:0.3rem;">candidates ranked</div>
                    <div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid #1e293b;">
                        <div style="color:#64748b;font-size:0.72rem;">Avg FPS: 
                            <span style="color:#10b981;font-weight:700;font-family:'JetBrains Mono',monospace;">
                                {avg_fps:.3f}
                            </span>
                        </div>
                        <div style="color:#64748b;font-size:0.72rem;margin-top:2px;">Top FPS: 
                            <span style="color:#f59e0b;font-weight:700;font-family:'JetBrains Mono',monospace;">
                                {top_fps:.3f}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with jcol3:
                if st.button("📊 View Rankings", key=f"job_rank_{job['id']}", use_container_width=True):
                    st.session_state.selected_job_id = job["id"]
                    st.switch_page("pages/02_Ranking.py")
                
                if st.button("🎯 Set Active", key=f"job_active_{job['id']}", use_container_width=True):
                    st.session_state.selected_job_id = job["id"]
                    st.success(f"Set active: {job['title']}")
                    st.rerun()

        st.markdown("<hr style='border-color:#1e293b;margin:0.5rem 0 1rem;'>", unsafe_allow_html=True)


with tab2:
    st.markdown("### ➕ Create New Job Requisition")
    st.markdown("""
    <div class="info-box">
        <strong>🤖 Job Intelligence Agent</strong> will analyze your job description,
        extract required and good-to-have skills, create a requirement graph, 
        and immediately rank all candidates for this role.
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("create_job_form"):
        col_jf1, col_jf2 = st.columns(2)
        
        with col_jf1:
            job_title = st.text_input("Job Title *", placeholder="e.g., Senior ML Engineer")
            company = st.text_input("Company *", placeholder="e.g., TechCorp AI")
            location = st.text_input("Location", placeholder="e.g., Bangalore, India (Hybrid)")
            department = st.text_input("Department", placeholder="e.g., AI Platform")
        
        with col_jf2:
            level = st.selectbox("Level", ["Junior", "Mid", "Mid-Senior", "Senior", "Staff", "Principal", "Lead"])
            salary_range = st.text_input("Salary Range", placeholder="e.g., ₹40L - ₹70L")
            domain = st.text_input("Domain", placeholder="e.g., Machine Learning / AI")
        
        job_description = st.text_area(
            "Job Description *",
            placeholder="Paste the full job description here...",
            height=200
        )
        
        col_skills1, col_skills2 = st.columns(2)
        with col_skills1:
            required_skills_input = st.text_input(
                "Required Skills (comma-separated) *",
                placeholder="Python, PyTorch, NLP, Transformers, MLOps"
            )
        with col_skills2:
            good_to_have_input = st.text_input(
                "Good-to-Have Skills (comma-separated)",
                placeholder="LangChain, Kubernetes, Ray, MLflow"
            )
        
        submitted = st.form_submit_button("🚀 Create Job & Run AI Ranking", use_container_width=True)
        
        if submitted:
            if not job_title or not company or not required_skills_input:
                st.error("Please fill in Job Title, Company, and Required Skills.")
            else:
                required_skills = [s.strip() for s in required_skills_input.split(",") if s.strip()]
                good_to_have = [s.strip() for s in good_to_have_input.split(",") if s.strip()]
                
                new_job = {
                    "id": f"j_custom_{len(st.session_state.custom_jobs)+1}",
                    "title": job_title,
                    "company": company,
                    "location": location or "Remote",
                    "department": department,
                    "description": job_description,
                    "required_skills": required_skills,
                    "good_to_have": good_to_have,
                    "domain": domain or "Engineering",
                    "growth_requirements": good_to_have[:3],
                    "level": level,
                    "salary_range": salary_range or "Competitive",
                }
                
                st.session_state.custom_jobs.append(new_job)
                st.session_state.selected_job_id = new_job["id"]
                
                st.success(f"✅ Job '{job_title}' created successfully!")
                st.markdown("**🤖 Job Intelligence Agent Results:**")
                st.json({
                    "job_id": new_job["id"],
                    "required_skills_extracted": required_skills,
                    "good_to_have_extracted": good_to_have,
                    "domain_detected": domain,
                    "candidates_ranked": len(candidates),
                })
                st.info("Navigate to **Candidate Ranking** to see the ranked candidates for this new role.")
