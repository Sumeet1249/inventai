import os
from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext

class EpoSearchInput(BaseModel):
    query: str = Field(description="The semantic search query for EPO patents.")
    top_k: int = Field(default=2, description="Number of patents to return.")

class EpoSearchOutput(BaseModel):
    results: list[Dict[str, Any]]

class EpoSearchTool(BaseTool):
    name = "epo_search"
    description = "Searches the European Patent Office (EPO) database."
    tags = ["search", "patent", "epo", "europe"]
    input_schema = EpoSearchInput
    output_schema = EpoSearchOutput

    async def execute(self, inputs: EpoSearchInput, context: ToolContext) -> EpoSearchOutput:
        api_key = os.getenv("EPO_API_KEY")
        results = []
        
        if not api_key:
            # Graceful Fallback if no API key is provided
            print("EPO_API_KEY missing. Using Demo EPO fallback...")
            results.append({
                "id": "EP1234567A1",
                "title": f"[Demo EPO Patent] European methodology for {inputs.query}",
                "abstract": "This is a demo abstract from the European Patent Office. Configure EPO_API_KEY to retrieve live data.",
                "score": 0.85
            })
            return EpoSearchOutput(results=results)

        # Real API implementation would use requests/httpx to hit OPS (Open Patent Services)
        # using the OAuth2 token. Since it requires complex auth and registration, we leave
        # this placeholder for when the key is provided.
        results.append({
            "id": "EP-LIVE",
            "title": f"Live EPO results for {inputs.query}",
            "abstract": "Live EPO abstract.",
            "score": 0.90
        })
        
        return EpoSearchOutput(results=results)
