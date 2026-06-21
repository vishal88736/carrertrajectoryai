"""
CareerTrajectory AI — LangGraph Multi-Agent Orchestrator
Routes recruiter queries through specialized agent nodes:
  Router → Analysis/Search → Response

Falls back to template-based copilot if LangGraph or LLM unavailable.
"""

from typing import Dict, List, Any, Optional, TypedDict, Annotated
from loguru import logger
import json

from backend.ai.config import USE_LLM_COPILOT
from backend.ai.llm_client import get_llm_client, SYSTEM_PROMPT
from backend.ai.embeddings import get_embedder
from backend.ai.vector_store import get_vector_store


# ── State Schema ───────────────────────────────────────────────────────────────

class CopilotState(TypedDict, total=False):
    """State object flowing through the LangGraph pipeline."""
    query: str
    intent: str
    candidates: List[Dict]
    job: Dict
    hidden_gems: List[Dict]
    context: str
    search_results: List[Dict]
    analysis: str
    response: str
    agent_trace: List[str]
    error: str


# ── Agent Nodes ────────────────────────────────────────────────────────────────

def router_node(state: CopilotState) -> CopilotState:
    """Classify user intent and route to appropriate agent."""
    llm = get_llm_client()
    query = state.get("query", "")

    trace = list(state.get("agent_trace", []))
    trace.append("🔀 Router Agent")

    if llm.is_available:
        intent = llm.classify_intent(query)
    else:
        # Fallback rule-based classification
        intent = _rule_based_intent(query)

    state["intent"] = intent
    state["agent_trace"] = trace
    logger.debug(f"Router: query='{query[:60]}...' → intent={intent}")
    return state


def analysis_node(state: CopilotState) -> CopilotState:
    """Perform candidate comparisons, deep dives, and SHAP analysis."""
    trace = list(state.get("agent_trace", []))
    trace.append("📊 Analysis Agent")

    candidates = state.get("candidates", [])
    job = state.get("job", {})
    query = state.get("query", "")
    intent = state.get("intent", "GENERAL")

    # Build context for LLM
    context_parts = []
    context_parts.append(f"**Job:** {job.get('title', 'N/A')} at {job.get('company', 'N/A')}")
    context_parts.append(f"**Required Skills:** {', '.join(job.get('required_skills', []))}")
    context_parts.append(f"**Total Candidates:** {len(candidates)}")

    # Find relevant candidates based on intent
    relevant = _find_relevant_candidates(query, candidates, intent)

    if relevant:
        for c in relevant[:5]:
            scores = c.get("scores", {})
            context_parts.append(
                f"\n**{c['name']}** (Rank #{c.get('rank', '?')}):\n"
                f"  - FPS: {scores.get('fps', 0):.3f}\n"
                f"  - Semantic Fit: {scores.get('semantic_fit', 0):.2f}\n"
                f"  - Career Momentum: {scores.get('career_momentum', 0):.2f}\n"
                f"  - Behavioral Evidence: {scores.get('behavioral_evidence', 0):.2f}\n"
                f"  - Contextual Intelligence: {scores.get('contextual_intelligence', 0):.2f}\n"
                f"  - Skills: {', '.join(c.get('skills', {}).get('current', [])[:8])}\n"
                f"  - YoE: {c.get('years_of_experience', 0)}\n"
                f"  - Hidden Gem: {'Yes' if c.get('hidden_gem') else 'No'}"
            )

    state["context"] = "\n".join(context_parts)
    state["agent_trace"] = trace
    return state


def search_node(state: CopilotState) -> CopilotState:
    """Use ChromaDB vector search for skill-based candidate discovery."""
    trace = list(state.get("agent_trace", []))
    trace.append("🔍 Search Agent")

    query = state.get("query", "")
    job = state.get("job", {})

    # Try vector search
    store = get_vector_store()
    if store.is_available:
        job_skills = job.get("required_skills", [])
        search_results = store.search_by_job(job_skills, top_k=10)
        state["search_results"] = search_results
        if search_results:
            search_context = "\n**Vector Search Results (most semantically similar):**\n"
            for r in search_results[:5]:
                meta = r.get("metadata", {})
                search_context += (
                    f"  - {meta.get('name', r['id'])} "
                    f"(similarity: {r.get('similarity', 0):.3f}, "
                    f"FPS: {meta.get('fps', 0):.3f})\n"
                )
            state["context"] = state.get("context", "") + "\n" + search_context

    state["agent_trace"] = trace
    return state


def response_node(state: CopilotState) -> CopilotState:
    """Generate final natural language response using LLM."""
    trace = list(state.get("agent_trace", []))
    trace.append("💬 Response Agent")

    llm = get_llm_client()
    query = state.get("query", "")
    context = state.get("context", "")
    intent = state.get("intent", "GENERAL")

    if llm.is_available:
        response = llm.generate_analysis(
            query=query,
            context=context,
            candidates_info="",  # Already in context
        )
        if response:
            state["response"] = response
            state["agent_trace"] = trace
            return state

    # Fallback: no LLM available
    state["response"] = _fallback_response(state)
    state["agent_trace"] = trace
    return state


# ── Orchestrator ───────────────────────────────────────────────────────────────

class CopilotOrchestrator:
    """
    LangGraph-based multi-agent orchestrator.
    Routes queries through: Router → Analysis/Search → Response.
    Falls back to sequential execution if LangGraph not installed.
    """

    def __init__(self):
        self._graph = None
        self._build_graph()

    def _build_graph(self):
        """Build the LangGraph state graph."""
        try:
            from langgraph.graph import StateGraph, END

            builder = StateGraph(CopilotState)

            # Add nodes
            builder.add_node("router_agent", router_node)
            builder.add_node("analysis_agent", analysis_node)
            builder.add_node("search_agent", search_node)
            builder.add_node("response_agent", response_node)

            # Set entry point
            builder.set_entry_point("router_agent")

            # Conditional routing based on intent
            def route_by_intent(state: CopilotState) -> str:
                intent = state.get("intent", "GENERAL")
                if intent in ("SEARCH", "HIDDEN_GEMS"):
                    return "search_agent"
                return "analysis_agent"

            builder.add_conditional_edges(
                "router_agent",
                route_by_intent,
                {"search_agent": "search_agent", "analysis_agent": "analysis_agent"},
            )

            # Both search and analysis flow to response
            builder.add_edge("search_agent", "analysis_agent")
            builder.add_edge("analysis_agent", "response_agent")
            builder.add_edge("response_agent", END)

            self._graph = builder.compile()
            logger.info("✅ LangGraph orchestrator compiled")

        except ImportError:
            logger.warning("LangGraph not installed — using sequential fallback")
            self._graph = None
        except Exception as e:
            logger.warning(f"LangGraph build failed: {e} — using sequential fallback")
            self._graph = None

    def process_query(
        self,
        query: str,
        candidates: List[Dict],
        job: Dict,
        hidden_gems: List[Dict] = None,
    ) -> Dict:
        """
        Process a recruiter query through the multi-agent pipeline.
        Returns: {"response": str, "intent": str, "agent_trace": List[str]}
        """
        initial_state: CopilotState = {
            "query": query,
            "intent": "",
            "candidates": candidates,
            "job": job,
            "hidden_gems": hidden_gems or [],
            "context": "",
            "search_results": [],
            "analysis": "",
            "response": "",
            "agent_trace": [],
            "error": "",
        }

        try:
            if self._graph is not None:
                # Run through LangGraph
                result = self._graph.invoke(initial_state)
            else:
                # Sequential fallback
                result = self._sequential_fallback(initial_state)

            return {
                "response": result.get("response", "No response generated."),
                "intent": result.get("intent", "GENERAL"),
                "agent_trace": result.get("agent_trace", []),
            }

        except Exception as e:
            logger.error(f"Orchestrator error: {e}")
            return {
                "response": f"⚠️ An error occurred: {str(e)}",
                "intent": "ERROR",
                "agent_trace": ["❌ Error"],
            }

    def _sequential_fallback(self, state: CopilotState) -> CopilotState:
        """Run agents sequentially when LangGraph is not available."""
        state = router_node(state)
        intent = state.get("intent", "GENERAL")

        if intent in ("SEARCH", "HIDDEN_GEMS"):
            state = search_node(state)

        state = analysis_node(state)
        state = response_node(state)
        return state

    def process_query_stream(
        self,
        query: str,
        candidates: List[Dict],
        job: Dict,
        hidden_gems: List[Dict] = None,
    ):
        """Stream the response for real-time display."""
        # First, run analysis pipeline (non-streaming)
        initial_state: CopilotState = {
            "query": query,
            "intent": "",
            "candidates": candidates,
            "job": job,
            "hidden_gems": hidden_gems or [],
            "context": "",
            "search_results": [],
            "analysis": "",
            "response": "",
            "agent_trace": [],
            "error": "",
        }

        # Run through router + analysis/search
        state = router_node(initial_state)
        intent = state.get("intent", "GENERAL")
        if intent in ("SEARCH", "HIDDEN_GEMS"):
            state = search_node(state)
        state = analysis_node(state)

        # Stream the response
        llm = get_llm_client()
        if llm.is_available:
            context = state.get("context", "")
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
            ]
            if context:
                messages.append({"role": "user", "content": f"## Context\n{context}"})
                messages.append({
                    "role": "assistant",
                    "content": "I have the candidate data. What would you like to know?",
                })
            messages.append({"role": "user", "content": query})

            yield from llm.chat_stream(messages)
        else:
            yield _fallback_response(state)


# ── Helper Functions ───────────────────────────────────────────────────────────

def _rule_based_intent(query: str) -> str:
    """Fallback intent classification using keyword matching."""
    q = query.lower()

    if any(w in q for w in ["compare", "versus", "vs", "ranked above", "difference"]):
        return "COMPARE"
    if any(w in q for w in ["best", "top", "recommend", "who should"]):
        return "RECOMMEND"
    if any(w in q for w in ["how", "explain", "fps", "score", "formula", "computed"]):
        return "EXPLAIN"
    if any(w in q for w in ["hidden gem", "undervalued", "overlooked", "potential"]):
        return "HIDDEN_GEMS"
    if any(w in q for w in ["find", "search", "show me", "candidates with", "who has"]):
        return "SEARCH"

    # Check if a specific candidate name is mentioned → deep dive
    # (names will be matched by the analysis agent)
    return "DEEP_DIVE"


def _find_relevant_candidates(
    query: str,
    candidates: List[Dict],
    intent: str,
) -> List[Dict]:
    """Find candidates mentioned in the query or relevant to the intent."""
    q_lower = query.lower()
    found = []

    # Name-based matching
    for c in candidates:
        name = c.get("name", "")
        first_name = name.split()[0].lower() if name else ""
        full_name = name.lower()
        if full_name in q_lower or (first_name and first_name in q_lower):
            found.append(c)

    if found:
        return found

    # Intent-based selection
    if intent == "RECOMMEND":
        return candidates[:3]
    if intent == "COMPARE":
        return candidates[:2]
    if intent == "HIDDEN_GEMS":
        return [c for c in candidates if c.get("hidden_gem")][:5]

    return candidates[:5]


def _fallback_response(state: CopilotState) -> str:
    """Generate a template-based response when LLM is unavailable."""
    intent = state.get("intent", "GENERAL")
    candidates = state.get("candidates", [])
    job = state.get("job", {})
    query = state.get("query", "")

    if intent == "RECOMMEND" and candidates:
        top3 = candidates[:3]
        lines = [f"**🏆 Top Recommended Candidates for {job.get('title', 'this role')}**\n"]
        for i, c in enumerate(top3):
            fps = c.get("scores", {}).get("fps", 0)
            mom = c.get("scores", {}).get("career_momentum", 0)
            lines.append(
                f"{i+1}. **{c['name']}** — FPS: {fps:.3f} · Momentum: {mom:.2f}"
            )
        lines.append(f"\n**Primary Recommendation:** **{top3[0]['name']}**")
        lines.append(f"\n*Connect GROQ_API_KEY for AI-powered analysis.*")
        return "\n".join(lines)

    if intent == "EXPLAIN":
        return (
            "**📐 How FPS is Computed**\n\n"
            "```\n"
            "FPS = 0.35 × Semantic Fit + 0.30 × Career Momentum\n"
            "    + 0.20 × Behavioral Evidence + 0.15 × Contextual Intelligence\n"
            "```\n\n"
            "With Phase 2 AI:\n"
            "- **Semantic Fit** uses Sentence Transformers (all-MiniLM-L6-v2) embeddings\n"
            "- **Behavioral Evidence** pulls live GitHub/LeetCode/Kaggle data\n"
            "- **Ranking** can be trained with LightGBM LambdaRank\n"
        )

    # Default
    top = candidates[0] if candidates else None
    gems_count = sum(1 for c in candidates if c.get("hidden_gem"))
    top_str = f"- 🏆 Top: **{top['name']}** (FPS: {top['scores']['fps']:.3f})\n" if top else ""
    return (
        f"**🤖 Recruiter Copilot**\n\n"
        f"Analyzing **{len(candidates)} candidates** for **{job.get('title', 'this role')}**.\n"
        f"{top_str}"
        f"- 💎 Hidden gems: **{gems_count}** detected\n\n"
        f"*Set GROQ_API_KEY for full AI-powered analysis with Llama 3.*"
    )


# ── Module-level convenience ───────────────────────────────────────────────

_orchestrator: Optional[CopilotOrchestrator] = None

def get_orchestrator() -> CopilotOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = CopilotOrchestrator()
    return _orchestrator
