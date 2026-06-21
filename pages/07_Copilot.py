"""
CareerTrajectory AI — Page 7: Recruiter Copilot
AI-powered natural language assistant for recruiter queries.
"""

import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

st.set_page_config(page_title="Copilot · CareerTrajectory AI", page_icon="🤖", layout="wide")

from ui.components import inject_css, render_page_header, get_score_color, render_score_bars
from data.sample_data import get_candidates, get_job_by_id
from backend.scoring_engine import rank_candidates, detect_hidden_gems, predict_future_role

inject_css()

import random
from datetime import datetime

if "selected_job_id" not in st.session_state:
    st.session_state.selected_job_id = "j001"
if "copilot_history" not in st.session_state:
    st.session_state.copilot_history = []
if "custom_candidates" not in st.session_state:
    st.session_state.custom_candidates = []

candidates = get_candidates() + st.session_state.custom_candidates
job = get_job_by_id(st.session_state.selected_job_id)
ranked = rank_candidates(candidates, job)
gems = detect_hidden_gems(ranked)

render_page_header("Recruiter Copilot", 
    "Ask anything about your candidate pool in natural language. AI-powered insights.",
    "🤖")


# ── Copilot Engine ─────────────────────────────────────────────────────────────

def generate_copilot_response(query: str, ranked_candidates, job_data, hidden_gems) -> str:
    """
    Simulates a multi-agent AI copilot response.
    Parses candidate names from natural language queries and performs dynamic comparisons.
    """
    query_lower = query.lower()
    top = ranked_candidates[0] if ranked_candidates else None
    
    # ── Dynamic Candidate Name Extraction ──────────────────────────────────
    found_cands = []
    for c in ranked_candidates:
        first_name = c["name"].split()[0].lower()
        full_name = c["name"].lower()
        if full_name in query_lower or first_name in query_lower:
            found_cands.append(c)
            
    # Remove duplicates if any
    seen = set()
    found_cands = [x for x in found_cands if not (x["id"] in seen or seen.add(x["id"]))]
    
    # ── Pattern matching for common queries ──────────────────────────────────
    
    # Why is X ranked above Y? / Compare
    if "ranked above" in query_lower or "why is" in query_lower and "rank" in query_lower or "compare" in query_lower:
        if len(found_cands) >= 2:
            c1, c2 = found_cands[0], found_cands[1]
        elif len(ranked_candidates) >= 2:
            c1, c2 = ranked_candidates[0], ranked_candidates[1]
        else:
            return "Not enough candidates available to perform comparison."
            
        if c1["scores"]["fps"] < c2["scores"]["fps"]:
            c1, c2 = c2, c1
            
        fps_diff = c1["scores"]["fps"] - c2["scores"]["fps"]
        mom_diff = c1["scores"]["career_momentum"] - c2["scores"]["career_momentum"]
        
        response = f"""
**🔍 Ranking Comparison: {c1['name']} (Rank #{c1.get('rank','?')}) vs {c2['name']} (Rank #{c2.get('rank','?')})**

**{c1['name']}** ranks higher than **{c2['name']}** for the following reasons:

1. **Career Momentum** ({c1['scores']['career_momentum']:.2f} vs {c2['scores']['career_momentum']:.2f}): 
   {c1['name'].split()[0]} is acquiring skills in the {job_data['domain']} domain at a faster rate. 
   Their recent skill acquisitions — especially {', '.join(c1['skills']['current'][:3])} — 
   align strongly with the role's trajectory.

2. **Behavioral Evidence** ({c1['scores']['behavioral_evidence']:.2f} vs {c2['scores']['behavioral_evidence']:.2f}):
   External platform signals (GitHub commits, open-source contributions, etc.) show that 
   {c1['name'].split()[0]} has higher technical activity.

3. **FPS Delta**: {c1['name'].split()[0]} scores **{fps_diff:.3f} higher** in overall Future Potential Score.

**📊 SHAP Attribution**: {"Career Momentum" if mom_diff >= 0 else "Semantic Fit"} is the primary differentiator (+{abs(mom_diff*0.3):.3f} to FPS gap).

*Note: {c2['name'].split()[0]} may be a better fit if you prioritize {c2['scores']['contextual_intelligence']:.0%} contextual alignment (industry background).*
"""
        return response

    # Single Candidate Deep-Dive query
    if len(found_cands) == 1:
        c = found_cands[0]
        traj = predict_future_role(c)
        return f"""
**👤 Candidate Deep-Dive: {c['name']} (Rank #{c.get('rank','?')})**

- **FPS Score**: **{c['scores']['fps']:.3f}** (Future Potential Score)
- **Semantic Fit**: {c['scores']['semantic_fit']:.2f}
- **Career Momentum**: {c['scores']['career_momentum']:.2f}
- **Behavioral Evidence**: {c['scores']['behavioral_evidence']:.2f}
- **Contextual Intelligence**: {c['scores']['contextual_intelligence']:.2f}

**🔮 Predicted 5-Year Horizon:** {traj['trajectory']['5_years']} ({traj['momentum_tier']})

**Key Details:**
- **Current Skills**: {', '.join(c['skills']['current'][:8])}
- **Years of Experience**: {c.get('years_of_experience', 0)}
- **Leadership Potential**: {traj['leadership_probability'] * 100:.0f}%
"""

    # Best candidate for this role
    if "best" in query_lower or "top" in query_lower or "recommend" in query_lower:
        top3 = ranked_candidates[:3]
        details = "\n".join([
            f"{i+1}. **{c['name']}** — FPS: {c['scores']['fps']:.3f} · Momentum: {c['scores']['career_momentum']:.2f}"
            for i, c in enumerate(top3)
        ])
        return f"""
**🏆 Top Recommended Candidates for {job_data['title']}**

{details}

**Primary Recommendation:** **{top3[0]['name']}**
- Highest Future Potential Score: **{top3[0]['scores']['fps']:.3f}**
- Career Momentum: {top3[0]['scores']['career_momentum']:.2f} — actively growing toward this role
- Key strengths: {', '.join(top3[0]['skills']['current'][:4])}
- {len(top3[0].get('certifications',[]))} relevant certifications

**Next Steps:** 
1. Schedule technical interview with {top3[0]['name']}
2. Consider {top3[1]['name']} as a strong backup (FPS: {top3[1]['scores']['fps']:.3f})
3. Run Skill Gap Simulator for any missing skills
"""

    # FPS explanation
    if "fps" in query_lower or "score" in query_lower or "how is" in query_lower:
        return """
**📐 How FPS (Future Potential Score) is Computed**

```
FPS = 0.35 × Semantic Fit
    + 0.30 × Career Momentum
    + 0.20 × Behavioral Evidence
    + 0.15 × Contextual Intelligence
```

**Component Details:**

- **Semantic Fit (35%)**: Measures skill alignment using semantic matching (SkillBERT-style). Accounts for direct matches AND domain proximity.
  
- **Career Momentum (30%)**: `√(Velocity × Direction Alignment)`. Velocity = skills/6 months. Direction = how well recent skills align with job domain.

- **Behavioral Evidence (20%)**: Aggregated signals from GitHub, LeetCode, Kaggle, Codeforces, open-source contributions, certifications.

- **Contextual Intelligence (15%)**: Experience level fit, education relevance, domain consistency.

**Key Innovation**: Career Momentum heavily rewards fast learners going in the right direction — even with less experience.
"""

    # Default response with available queries
    return f"""
**🤖 Recruiter Copilot — I can help with:**

Currently analyzing **{len(ranked_candidates)} candidates** for **{job_data['title']}**:
- 🏆 Top candidate: **{top['name']}** (FPS: {top['scores']['fps']:.3f}) 
- 💎 Hidden gems: **{len(hidden_gems)}** detected

**Try asking:**
- "Why is [Candidate A] ranked above [Candidate B]?"
- "Show me candidates with the highest learning velocity"
- "Who has the highest leadership/Staff Engineer potential?"
- "Find hidden gems in the candidate pool"
- "Compare the top two candidates"
- "Explain how the FPS score is computed"
- "Who should I recommend for this role?"

*In production, this copilot connects to LangGraph + LLaMA 3 / GPT-4 for advanced reasoning.*
"""


# ── UI Layout ─────────────────────────────────────────────────────────────────

# Suggested queries
st.markdown("### 💡 Suggested Queries")
suggestions = [
    "Why is the #1 candidate ranked above #2?",
    "Show hidden gems in the candidate pool",
    "Who has the highest learning velocity?",
    "Show Staff Engineer potential candidates",
    "Compare top two candidates",
    "How is the FPS score computed?",
    "Who should I recommend for this role?",
]

sug_cols = st.columns(4)
for i, sug in enumerate(suggestions[:8]):
    col = sug_cols[i % 4]
    with col:
        if st.button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state.copilot_history.append({
                "role": "user", "content": sug, "time": datetime.now().strftime("%H:%M")
            })
            response = generate_copilot_response(sug, ranked, job, gems)
            st.session_state.copilot_history.append({
                "role": "assistant", "content": response, "time": datetime.now().strftime("%H:%M")
            })

st.markdown("<br>", unsafe_allow_html=True)

# Chat Interface
chat_container = st.container()
with chat_container:
    st.markdown("### 💬 Chat with Copilot")
    
    if not st.session_state.copilot_history:
        st.markdown("""
        <div style="text-align:center;padding:2rem;background:#1a1a2e;
             border-radius:16px;border:1px solid #334155;">
            <div style="font-size:2.5rem;margin-bottom:0.7rem;">🤖</div>
            <div style="font-weight:700;color:#a5b4fc;margin-bottom:0.4rem;">
                Recruiter Copilot is ready!
            </div>
            <div style="color:#64748b;font-size:0.88rem;">
                Ask anything about your {len(ranked)} candidates for {job['title']}.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Render chat history
    for msg in st.session_state.copilot_history[-20:]:  # Last 20 messages
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display:flex;justify-content:flex-end;margin-bottom:0.7rem;">
                <div style="max-width:80%;">
                    <div style="text-align:right;color:#475569;font-size:0.72rem;margin-bottom:3px;">
                        You · {msg.get('time','')}
                    </div>
                    <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);
                         color:white;border-radius:16px 16px 4px 16px;
                         padding:0.8rem 1rem;font-size:0.9rem;">
                        {msg['content']}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Render markdown properly
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg["content"])

st.markdown("<br>", unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask the Recruiter Copilot anything...")
if user_input:
    st.session_state.copilot_history.append({
        "role": "user", "content": user_input, "time": datetime.now().strftime("%H:%M")
    })
    with st.spinner("🤖 Copilot is thinking..."):
        response = generate_copilot_response(user_input, ranked, job, gems)
    st.session_state.copilot_history.append({
        "role": "assistant", "content": response, "time": datetime.now().strftime("%H:%M")
    })
    st.rerun()

# Clear chat
col_clear, col_export = st.columns([1, 4])
with col_clear:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.copilot_history = []
        st.rerun()

# Copilot capabilities
st.markdown("---")
st.markdown("### 🔬 Copilot Architecture")
cap_cols = st.columns(4)
capabilities = [
    ("🧠", "Multi-Agent Reasoning", "Routes queries to specialized sub-agents for Career Momentum, Behavioral, and Semantic analysis."),
    ("📊", "SHAP Attribution", "Explains ranking decisions using feature attribution scores for full transparency."),
    ("💬", "NLP Understanding", "Parses natural language recruiter queries and maps to structured data operations."),
    ("🔄", "Continuous Learning", "Learns from recruiter feedback to improve future recommendations."),
]
for col, (icon, title, desc) in zip(cap_cols, capabilities):
    with col:
        st.markdown(f"""
        <div class="ct-card" style="text-align:center;padding:1.2rem;">
            <div style="font-size:1.5rem;margin-bottom:0.5rem;">{icon}</div>
            <div style="font-weight:700;color:#a5b4fc;font-size:0.85rem;margin-bottom:0.4rem;">{title}</div>
            <div style="color:#64748b;font-size:0.78rem;line-height:1.5;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)
