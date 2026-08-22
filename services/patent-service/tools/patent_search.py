from typing import Any, Dict
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext
from services.patent_service.pqai.pqai_client import pqai_client
from services.patent_service.embeddings.embedding_service import embedding_service
from services.patent_service.vectorstore.chroma_client import vector_store

class PatentSearchInput(BaseModel):
    query: str = Field(description="The semantic search query for patents.")
    top_k: int = Field(default=5, description="Number of patents to return.")

class PatentSearchOutput(BaseModel):
    results: list[Dict[str, Any]]

class PatentSearchTool(BaseTool):
    """
    Adapter tool that connects the AI Core to the PQAI / Vector Database
    for semantic patent search.
    """
    name = "semantic_patent_search"
    description = "Searches the patent knowledge base for similar prior-art."
    tags = ["search", "patent"]
    input_schema = PatentSearchInput
    output_schema = PatentSearchOutput

    async def execute(self, inputs: PatentSearchInput, context: ToolContext) -> PatentSearchOutput:
        # 1. Try PQAI Search via API
        results = await pqai_client.search_prior_art(inputs.query, inputs.top_k)
        
        # 2. Fallback to ChromaDB Vector Search if PQAI fails or returns empty
        if not results:
            print("PQAI empty or failed. Falling back to local ChromaDB search...")
            embedding = embedding_service.embed_text(inputs.query)
            chroma_results = vector_store.search_similar(embedding, inputs.top_k)
            
            for item in chroma_results:
                results.append({
                    "id": item.get("id"),
                    "title": item.get("metadata", {}).get("title", "Unknown"),
                    "abstract": item.get("document", ""),
                    "score": 1.0 - item.get("distance", 0.0)
                })
        
        # In a full system, we might index PQAI results back into ChromaDB here for future use
        
        return PatentSearchOutput(results=results)
