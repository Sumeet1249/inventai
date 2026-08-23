"""
Summarization Tool
───────────────────
LLM: OpenAI gpt-4o-mini (primary) → Gemini gemini-1.5-flash (fallback)
Never uses the deprecated gemini-2.0-flash.
"""
import logging
import os

from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext

logger = logging.getLogger(__name__)


class SummarizationInput(BaseModel):
    chunks:     list[str] = Field(description="Text chunks to synthesise")
    focus_area: str       = Field(default="general", description="Topic to focus on")


class SummarizationOutput(BaseModel):
    summary:      str       = Field(description="Synthesised summary")
    key_findings: list[str] = Field(description="Bullet-point findings")


def _make_llm():
    """OpenAI gpt-4o-mini first, Gemini gemini-1.5-flash fallback."""
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    google_key  = os.environ.get("GOOGLE_API_KEY", "")

    if openai_key and not openai_key.startswith("sk-your"):
        try:
            from langchain_openai import ChatOpenAI
            logger.info("Summarization: using OpenAI gpt-4o-mini")
            return ChatOpenAI(
                model="gpt-4o-mini",
                temperature=0.2,
                openai_api_key=openai_key,
                max_retries=2,
                request_timeout=30,
            )
        except Exception as exc:
            logger.warning("Summarization: OpenAI init failed: %s", exc)

    if google_key and not google_key.startswith("AQ."):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            logger.info("Summarization: using Gemini gemini-1.5-flash")
            return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
        except Exception as exc:
            logger.warning("Summarization: Gemini init failed: %s", exc)

    from langchain_openai import ChatOpenAI
    return ChatOpenAI(model="gpt-4o-mini", temperature=0.2)


class SummarizationTool(BaseTool):
    """Synthesises large amounts of retrieved RAG context into a concise summary."""

    name          = "paper_summarization"
    description   = "Synthesises extracted text chunks into a coherent summary."
    tags          = ["analysis", "research"]
    input_schema  = SummarizationInput
    output_schema = SummarizationOutput

    def __init__(self, llm=None):
        self.llm = llm or _make_llm()

        template = (
            "You are an expert AI Research assistant.\n"
            "Summarise the following extracted text chunks, focusing specifically on: {focus_area}.\n\n"
            "Extracted Text:\n{text}\n\n"
            "Provide output in exactly this format:\n"
            "SUMMARY:\n<comprehensive summary>\n\n"
            "KEY FINDINGS:\n- <finding 1>\n- <finding 2>"
        )
        self.prompt = PromptTemplate(
            template=template, input_variables=["focus_area", "text"]
        )
        self.chain = self.prompt | self.llm

    async def execute(
        self, inputs: SummarizationInput, context: ToolContext
    ) -> SummarizationOutput:
        text = "\n\n".join(inputs.chunks)

        try:
            response = await self.chain.ainvoke({
                "focus_area": inputs.focus_area,
                "text":       text,
            })
            content = response.content

            summary_part  = content
            findings_part: list[str] = []

            if "KEY FINDINGS:" in content:
                parts         = content.split("KEY FINDINGS:")
                summary_part  = parts[0].replace("SUMMARY:", "").strip()
                findings_part = [
                    line.lstrip("- ").strip()
                    for line in parts[1].split("\n")
                    if line.strip().startswith("-")
                ]
        except Exception as exc:
            logger.warning("SummarizationTool LLM failed: %s", exc)
            summary_part  = f"Summary unavailable ({exc}). Raw content provided above."
            findings_part = ["LLM quota exceeded — manual review recommended"]

        return SummarizationOutput(
            summary=summary_part,
            key_findings=findings_part,
        )
