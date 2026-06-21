"""
CareerTrajectory AI — LLM Client (Groq + Llama 3)
Provides chat completion, intent classification, and analysis generation.
Falls back to template-based responses if Groq API is unavailable.
"""

import time
from typing import List, Dict, Optional, Generator
from loguru import logger

from backend.ai.config import (
    GROQ_API_KEY, USE_LLM_COPILOT,
    LLM_MODEL_NAME, LLM_FALLBACK_MODEL,
    LLM_MAX_TOKENS, LLM_TEMPERATURE,
)

# ── System Prompts ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are the CareerTrajectory AI Recruiter Copilot — an expert AI assistant 
helping technical recruiters make data-driven hiring decisions.

You have access to candidate data including:
- FPS (Future Potential Score) — a 0-1 score combining Semantic Fit, Career Momentum, 
  Behavioral Evidence, and Contextual Intelligence
- Career Momentum — measures skill acquisition velocity × direction alignment
- Behavioral Evidence — validated signals from GitHub, LeetCode, Kaggle
- SHAP explanations for ranking decisions

Guidelines:
- Be concise, data-driven, and actionable
- Use specific numbers and scores when available
- Highlight non-obvious insights (hidden gems, momentum trends)
- Format responses with markdown for readability
- When comparing candidates, always explain WHY one ranks higher
- Suggest concrete next steps (interview, skill gap sim, etc.)
"""

INTENT_PROMPT = """Classify the user's recruiter query into exactly one intent category.
Categories:
- COMPARE: Comparing two or more candidates
- DEEP_DIVE: Detailed analysis of a single candidate
- RECOMMEND: Who is the best candidate / top recommendations
- EXPLAIN: How does scoring/FPS work
- SEARCH: Find candidates matching certain criteria
- HIDDEN_GEMS: Discovering undervalued high-potential candidates
- GENERAL: General question or greeting

Respond with ONLY the category name, nothing else."""


class LLMClient:
    """Groq API client for Llama 3 chat completions."""

    def __init__(self):
        self._client = None
        self._token_usage = {"prompt": 0, "completion": 0, "total": 0}
        self._call_count = 0
        self._total_latency = 0.0

    def _ensure_client(self):
        if self._client is not None:
            return
        if not GROQ_API_KEY:
            return
        try:
            from groq import Groq
            self._client = Groq(api_key=GROQ_API_KEY)
            logger.info("✅ Groq LLM client initialized")
        except Exception as e:
            logger.error(f"❌ Groq client init failed: {e}")
            self._client = None

    @property
    def is_available(self) -> bool:
        if not USE_LLM_COPILOT or not GROQ_API_KEY:
            return False
        self._ensure_client()
        return self._client is not None

    # ── Core Chat ──────────────────────────────────────────────────────────

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
        model: str = "",
    ) -> Optional[str]:
        """Send a chat completion request to Groq."""
        if not self.is_available:
            return None

        model = model or LLM_MODEL_NAME
        start = time.time()

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            latency = time.time() - start
            self._call_count += 1
            self._total_latency += latency

            # Track token usage
            usage = response.usage
            if usage:
                self._token_usage["prompt"] += usage.prompt_tokens
                self._token_usage["completion"] += usage.completion_tokens
                self._token_usage["total"] += usage.total_tokens

            content = response.choices[0].message.content
            logger.debug(
                f"LLM response: {len(content)} chars, "
                f"{usage.total_tokens if usage else '?'} tokens, "
                f"{latency:.2f}s"
            )
            return content

        except Exception as e:
            logger.warning(f"Groq API call failed ({model}): {e}")
            # Try fallback model
            if model != LLM_FALLBACK_MODEL:
                logger.info(f"Retrying with fallback model: {LLM_FALLBACK_MODEL}")
                return self.chat(messages, temperature, max_tokens, LLM_FALLBACK_MODEL)
            return None

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = LLM_TEMPERATURE,
        max_tokens: int = LLM_MAX_TOKENS,
    ) -> Generator[str, None, None]:
        """Stream chat completion tokens."""
        if not self.is_available:
            yield "⚠️ LLM is not available. Please set GROQ_API_KEY."
            return

        try:
            stream = self._client.chat.completions.create(
                model=LLM_MODEL_NAME,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content

        except Exception as e:
            logger.warning(f"Groq streaming failed: {e}")
            yield f"\n\n⚠️ LLM streaming error: {str(e)}"

    # ── Specialized Functions ──────────────────────────────────────────────

    def classify_intent(self, query: str) -> str:
        """Classify user query intent using lightweight LLM call."""
        if not self.is_available:
            return "GENERAL"

        result = self.chat(
            messages=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": query},
            ],
            temperature=0.1,
            max_tokens=20,
            model=LLM_FALLBACK_MODEL,  # Use small model for classification
        )

        if result:
            intent = result.strip().upper().replace(" ", "_")
            valid_intents = {
                "COMPARE", "DEEP_DIVE", "RECOMMEND", "EXPLAIN",
                "SEARCH", "HIDDEN_GEMS", "GENERAL",
            }
            if intent in valid_intents:
                return intent

        return "GENERAL"

    def generate_analysis(
        self,
        query: str,
        context: str,
        candidates_info: str = "",
    ) -> Optional[str]:
        """Generate a structured analysis response with candidate context."""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        if context or candidates_info:
            context_msg = f"## Current Context\n{context}\n\n"
            if candidates_info:
                context_msg += f"## Candidate Data\n{candidates_info}\n\n"
            messages.append({"role": "user", "content": context_msg})
            messages.append({
                "role": "assistant",
                "content": "I have the candidate data loaded. What would you like to know?",
            })

        messages.append({"role": "user", "content": query})

        return self.chat(messages, temperature=0.5)

    # ── Metrics ────────────────────────────────────────────────────────────

    def get_metrics(self) -> Dict:
        return {
            "available": self.is_available,
            "model": LLM_MODEL_NAME,
            "calls": self._call_count,
            "tokens": self._token_usage.copy(),
            "avg_latency": (
                round(self._total_latency / self._call_count, 2)
                if self._call_count > 0
                else 0
            ),
        }

    def reset_metrics(self):
        self._token_usage = {"prompt": 0, "completion": 0, "total": 0}
        self._call_count = 0
        self._total_latency = 0.0


# ── Module-level convenience ───────────────────────────────────────────────

_llm_instance: Optional[LLMClient] = None

def get_llm_client() -> LLMClient:
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = LLMClient()
    return _llm_instance
