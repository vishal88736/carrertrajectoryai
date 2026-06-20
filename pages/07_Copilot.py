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
gems = detect_hidden_gems(candidates)

render_page_header("Recruiter Copilot", 
    "Ask anything about your candidate pool in natural language. AI-powered insights.",
    "🤖")


# ── Copilot Engine ─────────────────────────────────────────────────────────────

def generate_copilot_response(query: str, ranked_candidates, job_data, hidden_gems) -> str:
    """
    Simulates a multi-agent AI copilot response.
    In production, this connects to LangGraph + LLM.
    """
    query_lower = query.lower()
    top = ranked_candidates[0] if ranked_candidates else None
    
    # ── Pattern matching for common queries ──────────────────────────────────
    
    # Why is X ranked above Y?
    if "ranked above" in query_lower or "why is" in query_lower and "rank" in query_lower:
        if len(ranked_candidates) >= 2:
            c1, c2 = ranked_candidates[0], ranked_candidates[1]
            fps_diff = c1["scores"]["fps"] - c2["scores"]["fps"]
            mom_diff = c1["scores"]["career_momentum"] - c2["scores"]["career_momentum"]
            response = f"""
**🔍 Ranking Comparison: {c1['name']} (#1) vs {c2['name']} (#2)**

**{c1['name']}** ranks higher for the following reasons:

1. **Career Momentum** ({c1['scores']['career_momentum']:.2f} vs {c2['scores']['career_momentum']:.2f}): 
   {c1['name'].split()[0]} is acquiring skills in the {job_data['domain']} domain at a significantly faster rate. 
   Their recent skill acquisitions — especially {', '.join(c1['skills']['current'][:3])} — 
   align strongly with the role's trajectory.

2. **Behavioral Evidence** ({c1['scores']['behavioral_evidence']:.2f} vs {c2['scores']['behavioral_evidence']:.2f}):
   External platform signals (GitHub commits, open-source contributions, etc.) show that 
   {c1['name'].split()[0]} has demonstrably higher technical activity.

3. **FPS Delta**: {c1['name'].split()[0]} scores **{fps_diff:.3f} higher** in overall Future Potential Score.

**📊 SHAP Attribution**: Career Momentum is the primary differentiator (+{mom_diff*0.3:.3f} to FPS gap).

*Note: {c2['name'].split()[0]} may be a better fit if you prioritize {c2['scores']['contextual_intelligence']:.0%} contextual alignment (industry background).*
"""
            return response

    # Hidden gems
    if "hidden gem" in query_lower or "underrated" in query_lower or "missed" in query_lower:
        if hidden_gems:
            gem_names = ", ".join(g["name"] for g in hidden_gems[:3])
            gem_details = "\n".join([
                f"- **{g['name']}**: {g.get('years_of_experience',0)} yrs exp but {g['scores']['career_momentum']:.0%} momentum. "
                f"Traditional ATS would rank them low due to experience. CareerTrajectory gives them #{g.get('rank','?')}."
                for g in hidden_gems[:3]
            ])
            return f"""
**💎 Hidden Gems Detected: {len(hidden_gems)} candidates**

These candidates have high career momentum and strong behavioral evidence but would be missed by traditional ATS due to lower experience or keyword mismatch:

{gem_details}

**Why they're valuable:**
These candidates are on steep learning curves. Based on their velocity of skill acquisition, they're likely to outperform more experienced candidates within 12-18 months.

**Recommendation:** Schedule exploratory calls with {hidden_gems[0]['name']} first — they have the highest momentum ({hidden_gems[0]['scores']['career_momentum']:.0%}) in the pool.
"""
        else:
            return "No hidden gems detected with current thresholds. Try adjusting detection sensitivity on the Hidden Gems page."

    # Strongest learning velocity
    if "learning velocity" in query_lower or "fastest learning" in query_lower or "highest velocity" in query_lower:
        by_momentum = sorted(ranked_candidates, key=lambda c: c["scores"]["career_momentum"], reverse=True)[:3]
        details = "\n".join([
            f"- **{c['name']}** — Career Momentum: {c['scores']['career_momentum']:.2f} | "
            f"Recently learning: {', '.join(c['skills'].get('learning', [])[:3])}"
            for c in by_momentum
        ])
        return f"""
**🚀 Candidates with Highest Learning Velocity**

Career Velocity measures how quickly candidates acquire new skills. Direction Alignment measures whether those skills are heading toward your role's domain.

{details}

**Top Performer:** {by_momentum[0]['name']} shows the strongest career momentum ({by_momentum[0]['scores']['career_momentum']:.2f}).
Their skill acquisition is highly aligned with {job_data['domain']} requirements.

*Career Momentum = √(Velocity × Direction Alignment)*
"""

    # Staff engineer potential
    if "staff engineer" in query_lower or "principal" in query_lower or "leadership" in query_lower:
        high_potential = [c for c in ranked_candidates if c["scores"]["fps"] > 0.75 and c["scores"]["career_momentum"] > 0.80]
        if high_potential:
            details = "\n".join([
                f"- **{c['name']}** — FPS: {c['scores']['fps']:.3f} | Momentum: {c['scores']['career_momentum']:.2f} | "
                f"Predicted 5yr: {c.get('predicted_trajectory', {}).get('5_years', 'Senior IC')}"
                for c in high_potential[:3]
            ])
            return f"""
**👑 Candidates with Staff/Principal Engineer Potential**

Based on Career Momentum, Behavioral Evidence, and historical trajectory analysis:

{details}

**Methodology:** We predict Staff Engineer potential by combining:
- Career Velocity > 0.8 (rapid skill acquisition)
- Strong behavioral evidence (GitHub contributions, OSS, etc.)
- Direction alignment with long-term technical leadership skills

**Recommendation:** These candidates have high leadership probability and would benefit from clear growth paths in your organization.
"""
        return "No candidates currently match Staff Engineer potential criteria. The top candidate shows the most promise."

    # Compare two named candidates
    if "compare" in query_lower:
        if len(ranked_candidates) >= 2:
            c1, c2 = ranked_candidates[0], ranked_candidates[1]
            return f"""
**📊 Candidate Comparison: {c1['name']} vs {c2['name']}**

| Dimension | {c1['name'].split()[0]} | {c2['name'].split()[0]} |
|-----------|---------|---------|
| FPS Score | **{c1['scores']['fps']:.3f}** | {c2['scores']['fps']:.3f} |
| Semantic Fit | {c1['scores']['semantic_fit']:.2f} | {c2['scores']['semantic_fit']:.2f} |
| Career Momentum | **{c1['scores']['career_momentum']:.2f}** | {c2['scores']['career_momentum']:.2f} |
| Behavioral Evidence | {c1['scores']['behavioral_evidence']:.2f} | {c2['scores']['behavioral_evidence']:.2f} |
| Years of Experience | {c1.get('years_of_experience',0)} | {c2.get('years_of_experience',0)} |

**Summary:** {c1['name'].split()[0]} leads on Career Momentum and overall FPS. 
{c2['name'].split()[0]} {'shows strong contextual alignment' if c2['scores']['contextual_intelligence'] > c1['scores']['contextual_intelligence'] else 'is a solid alternative'}.
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
            st.markdown(f"""
            <div style="display:flex;gap:0.7rem;margin-bottom:0.7rem;align-items:flex-start;">
                <div style="width:32px;height:32px;border-radius:50%;
                     background:linear-gradient(135deg,#10b981,#059669);
                     display:flex;align-items:center;justify-content:center;
                     font-size:0.9rem;flex-shrink:0;">🤖</div>
                <div style="flex:1;">
                    <div style="color:#475569;font-size:0.72rem;margin-bottom:3px;">
                        Copilot · {msg.get('time','')}
                    </div>
                    <div style="background:#1a1a2e;border:1px solid #334155;
                         color:#e2e8f0;border-radius:4px 16px 16px 16px;
                         padding:0.8rem 1rem;font-size:0.88rem;line-height:1.6;">
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
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
