"""
CareerTrajectory AI — Page 7: Recruiter Copilot
AI-powered natural language assistant for recruiter queries.

Phase 2: Powered by LangGraph multi-agent orchestration + Llama 3 (Groq).
Falls back to template-based responses when LLM is unavailable.
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
if "copilot_ai_mode" not in st.session_state:
    st.session_state.copilot_ai_mode = True

candidates = get_candidates() + st.session_state.custom_candidates
job = get_job_by_id(st.session_state.selected_job_id)
ranked = rank_candidates(candidates, job)
gems = detect_hidden_gems(ranked)

render_page_header("Recruiter Copilot", 
    "Ask anything about your candidate pool in natural language. AI-powered insights.",
    "🤖")


# ── AI Status Bar ──────────────────────────────────────────────────────────────

def _get_ai_status():
    """Check which AI systems are available."""
    status = {"llm": False, "langgraph": False, "embeddings": False, "chromadb": False}
    try:
        from backend.ai.llm_client import get_llm_client
        status["llm"] = get_llm_client().is_available
    except Exception:
        pass
    try:
        from backend.ai.orchestrator import get_orchestrator
        orch = get_orchestrator()
        status["langgraph"] = orch._graph is not None
    except Exception:
        pass
    try:
        from backend.ai.embeddings import get_embedder
        status["embeddings"] = get_embedder().is_available
    except Exception:
        pass
    try:
        from backend.ai.vector_store import get_vector_store
        status["chromadb"] = get_vector_store().is_available
    except Exception:
        pass
    return status

ai_status = _get_ai_status()

# AI mode toggle
col_toggle, col_status = st.columns([1, 3])
with col_toggle:
    st.session_state.copilot_ai_mode = st.toggle(
        "🧠 AI Mode",
        value=st.session_state.copilot_ai_mode,
        help="Toggle between AI-powered (Llama 3) and template-based responses"
    )

with col_status:
    indicators = []
    indicators.append(f"{'🟢' if ai_status['llm'] else '🔴'} LLM (Llama 3)")
    indicators.append(f"{'🟢' if ai_status['langgraph'] else '🟡'} LangGraph")
    indicators.append(f"{'🟢' if ai_status['embeddings'] else '🟡'} Embeddings")
    indicators.append(f"{'🟢' if ai_status['chromadb'] else '🟡'} ChromaDB")
    st.markdown(
        f"<div style='color:#64748b;font-size:0.78rem;padding-top:0.5rem;'>"
        f"{'  ·  '.join(indicators)}</div>",
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)


# ── Copilot Engine ─────────────────────────────────────────────────────────────

def generate_copilot_response(query: str, ranked_candidates, job_data, hidden_gems) -> dict:
    """
    Routes query through AI orchestrator (Phase 2) or template engine.
    Returns: {"response": str, "intent": str, "agent_trace": list}
    """
    # ── Phase 2: AI-powered response ──
    if st.session_state.copilot_ai_mode:
        try:
            from backend.ai.orchestrator import get_orchestrator
            orchestrator = get_orchestrator()
            result = orchestrator.process_query(
                query=query,
                candidates=ranked_candidates,
                job=job_data,
                hidden_gems=hidden_gems,
            )
            if result.get("response"):
                return result
        except Exception as e:
            pass  # Fall through to template

    # ── Template-based fallback ──
    response = _template_response(query, ranked_candidates, job_data, hidden_gems)
    return {"response": response, "intent": "TEMPLATE", "agent_trace": ["📝 Template Engine"]}


def _template_response(query: str, ranked_candidates, job_data, hidden_gems) -> str:
    """Original template-based copilot response (Phase 1 logic)."""
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

**Phase 2 AI Enhancements:**

- **Semantic Fit**: Now uses **Sentence Transformers** (all-MiniLM-L6-v2) for real embedding-based skill matching. 70% neural similarity + 30% lexical overlap.
  
- **Career Momentum**: `√(Velocity × Direction Alignment)`. Velocity = skills/6 months. Direction = how well recent skills align with job domain.

- **Behavioral Evidence**: Can fetch **live data** from GitHub API, LeetCode GraphQL, and Kaggle API for real-time signals.

- **ML Ranking**: Optional **LightGBM LambdaRank** model can be trained from recruiter feedback to learn optimal ranking.

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

*{'🧠 AI Mode: ON — powered by LangGraph + Llama 3' if st.session_state.copilot_ai_mode else '📝 Template Mode — set GROQ_API_KEY for AI-powered responses'}*
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
            result = generate_copilot_response(sug, ranked, job, gems)
            st.session_state.copilot_history.append({
                "role": "assistant", 
                "content": result["response"],
                "intent": result.get("intent", ""),
                "agent_trace": result.get("agent_trace", []),
                "time": datetime.now().strftime("%H:%M")
            })

st.markdown("<br>", unsafe_allow_html=True)

# Chat Interface
chat_container = st.container()
with chat_container:
    st.markdown("### 💬 Chat with Copilot")
    
    if not st.session_state.copilot_history:
        ai_badge = "🧠 LangGraph + Llama 3" if ai_status["llm"] else "📝 Template Engine"
        st.markdown(f"""
        <div style="text-align:center;padding:2rem;background:#1a1a2e;
             border-radius:16px;border:1px solid #334155;">
            <div style="font-size:2.5rem;margin-bottom:0.7rem;">🤖</div>
            <div style="font-weight:700;color:#a5b4fc;margin-bottom:0.4rem;">
                Recruiter Copilot is ready!
            </div>
            <div style="color:#64748b;font-size:0.88rem;margin-bottom:0.5rem;">
                Ask anything about your {len(ranked)} candidates for {job['title']}.
            </div>
            <div style="color:#475569;font-size:0.75rem;">
                Powered by {ai_badge}
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
                
                # Show agent trace if available
                trace = msg.get("agent_trace", [])
                intent = msg.get("intent", "")
                if trace or intent:
                    with st.expander("🔬 Agent Trace", expanded=False):
                        if intent:
                            st.markdown(f"**Intent:** `{intent}`")
                        if trace:
                            st.markdown(f"**Pipeline:** {' → '.join(trace)}")

st.markdown("<br>", unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Ask the Recruiter Copilot anything...")
if user_input:
    st.session_state.copilot_history.append({
        "role": "user", "content": user_input, "time": datetime.now().strftime("%H:%M")
    })
    with st.spinner("🤖 Copilot is thinking..."):
        result = generate_copilot_response(user_input, ranked, job, gems)
    st.session_state.copilot_history.append({
        "role": "assistant",
        "content": result["response"],
        "intent": result.get("intent", ""),
        "agent_trace": result.get("agent_trace", []),
        "time": datetime.now().strftime("%H:%M")
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
st.markdown("### 🔬 Copilot Architecture — Phase 2 AI")
cap_cols = st.columns(4)
capabilities = [
    ("🧠", "LangGraph Orchestrator", "Routes queries through Router → Analysis → Search → Response agents using LangGraph state machine."),
    ("🦙", "Llama 3 (Groq)", "70B parameter LLM for natural language understanding and recruiter-specific analysis generation."),
    ("🔍", "Semantic Search", "Sentence Transformers + ChromaDB vector search for finding candidates by skill similarity."),
    ("📊", "Live Signals", "Real-time GitHub, LeetCode, and Kaggle API integration for behavioral evidence."),
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

# LLM Metrics (if available)
if ai_status["llm"]:
    try:
        from backend.ai.llm_client import get_llm_client
        metrics = get_llm_client().get_metrics()
        if metrics["calls"] > 0:
            st.markdown("---")
            st.markdown("### 📈 AI Session Metrics")
            m_cols = st.columns(4)
            with m_cols[0]:
                st.metric("LLM Calls", metrics["calls"])
            with m_cols[1]:
                st.metric("Total Tokens", metrics["tokens"]["total"])
            with m_cols[2]:
                st.metric("Avg Latency", f"{metrics['avg_latency']:.1f}s")
            with m_cols[3]:
                st.metric("Model", metrics["model"].split("/")[-1][:20])
    except Exception:
        pass
