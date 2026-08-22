import os
from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext

class WipoSearchInput(BaseModel):
    query: str = Field(description="The semantic search query for WIPO patents.")
    top_k: int = Field(default=2, description="Number of patents to return.")

class WipoSearchOutput(BaseModel):
    results: list[Dict[str, Any]]

class WipoSearchTool(BaseTool):
    name = "wipo_search"
    description = "Searches the World Intellectual Property Organization (WIPO) database."
    tags = ["search", "patent", "wipo", "international"]
    input_schema = WipoSearchInput
    output_schema = WipoSearchOutput

    async def execute(self, inputs: WipoSearchInput, context: ToolContext) -> WipoSearchOutput:
        api_key = os.getenv("WIPO_API_KEY")
        results = []
        
        if not api_key:
            # Graceful Fallback if no API key is provided
            print("WIPO_API_KEY missing. Using Demo WIPO fallback...")
            results.append({
                "id": "WO2023123456A1",
                "title": f"[Demo WIPO Patent] International apparatus for {inputs.query}",
                "abstract": "This is a demo abstract from the World Intellectual Property Organization. Configure WIPO_API_KEY to retrieve live data.",
                "score": 0.88
            })
            return WipoSearchOutput(results=results)

        # Real API implementation would use requests/httpx to hit Patentscope API.
        results.append({
            "id": "WO-LIVE",
            "title": f"Live WIPO results for {inputs.query}",
            "abstract": "Live WIPO abstract.",
            "score": 0.92
        })
        
        return WipoSearchOutput(results=results)
