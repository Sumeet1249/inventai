"""
Planner Agent
──────────────
LLM: OpenAI gpt-4o-mini (primary) → Gemini gemini-1.5-flash (fallback)
Never uses the deprecated gemini-2.0-flash.
"""
import json
import logging
import os

from langchain_core.messages import SystemMessage
from services.innovation_engine.orchestrator.state import InnovationWorkflowState

logger = logging.getLogger(__name__)

_DEFAULT_PLAN = ["Patent", "Research", "KnowledgeGraph", "CAD", "Physics", "Report"]


def _make_llm():
    """OpenAI gpt-4o-mini first, Gemini gemini-1.5-flash fallback."""
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    google_key  = os.environ.get("GOOGLE_API_KEY", "")

    if openai_key and not openai_key.startswith("sk-your"):
        try:
            from langchain_openai import ChatOpenAI
            logger.info("Planner: using OpenAI gpt-4o-mini")
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0,
                openai_api_key=openai_key,
                max_retries=2,
                request_timeout=25,
            )
        except Exception as exc:
            logger.warning("Planner: OpenAI init failed: %s", exc)

    if google_key and not google_key.startswith("AQ."):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info("Planner: using Gemini gemini-1.5-flash")
            return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        except Exception as exc:
            logger.warning("Planner: Gemini init failed: %s", exc)

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-4o-mini", temperature=0)


class PlannerAgent:
    def __init__(self, llm=None):
        self.llm = llm or _make_llm()

    async def execute(self, state: InnovationWorkflowState) -> dict:
        idea = state.get("idea", "")

        prompt = f"""
You are the Master Innovation Planner.
Analyse this invention idea: "{idea}"

Choose the required execution nodes from:
["Patent", "Research", "KnowledgeGraph", "CAD", "Physics", "Report"]

Rules:
- Always include Patent and Report
- Include CAD and Physics for physical products
- Include Research and KnowledgeGraph for literature-heavy topics

Output ONLY valid JSON: {{"plan": ["Patent", "Research", ...]}}
"""
        try:
            response = await self.llm.ainvoke([SystemMessage(content=prompt)])
            content  = response.content.strip()
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            data = json.loads(content.strip())
            plan = data.get("plan", _DEFAULT_PLAN)
            logger.info("Planner produced plan: %s", plan)
        except Exception as exc:
            logger.warning("Planner LLM failed (%s) — using default plan", exc)
            plan = _DEFAULT_PLAN

        return {
            "plan":         plan,
            "logs":         [f"Planner generated {len(plan)}-step plan."],
            "current_step": "Planner",
        }
