from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext
from services.patent_service.rag.novelty_chain import novelty_chain

class NoveltyInput(BaseModel):
    idea: str = Field(description="The original invention idea text.")
    prior_art: list[Dict[str, Any]] = Field(description="The retrieved prior art to compare against.")

class NoveltyOutput(BaseModel):
    novelty_score: float = Field(description="Score from 0.0 to 1.0 indicating novelty.")
    gaps_found: list[str] = Field(description="Identified novel gaps not covered by prior art.")
    rejections: list[str] = Field(description="Claims that are likely anticipated by prior art.")
    summary: str = Field(default="", description="Summary of patentability.")

class NoveltyAnalysisTool(BaseTool):
    """
    Analyzes an invention idea against prior art to determine novelty.
    """
    name = "novelty_analysis"
    description = "Calculates novelty score and identifies gaps based on prior art."
    tags = ["analysis", "patent"]
    input_schema = NoveltyInput
    output_schema = NoveltyOutput

    async def execute(self, inputs: NoveltyInput, context: ToolContext) -> NoveltyOutput:
        result = await novelty_chain.analyze(inputs.idea, inputs.prior_art)
        
        return NoveltyOutput(
            novelty_score=result.get("novelty_score", 0.0),
            gaps_found=result.get("gaps_found", []),
            rejections=result.get("rejections", []),
            summary=result.get("summary", "")
        )
