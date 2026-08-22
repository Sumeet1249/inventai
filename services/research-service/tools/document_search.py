from typing import Any, Dict, List
from pydantic import BaseModel, Field
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.context import ToolContext
from services.research_service.infrastructure.vector_provider import LocalVectorProvider
from services.research_service.embeddings.embedding_service import EmbeddingService

class DocumentSearchInput(BaseModel):
    query: str = Field(description="The semantic question or search query.")
    paper_ids: List[str] = Field(default_factory=list, description="Optional filters by paper IDs.")
    top_k: int = Field(default=5, description="Number of chunks to retrieve.")

class DocumentSearchOutput(BaseModel):
    results: list[Dict[str, Any]]

class DocumentSearchTool(BaseTool):
    """
    RAG retrieval tool. Connects the AI Core to the abstracted Vector database
    to pull relevant semantic chunks from ingested PDFs.
    """
    name = "document_search"
    description = "Searches ingested research documents for relevant context."
    tags = ["search", "rag", "research"]
    input_schema = DocumentSearchInput
    output_schema = DocumentSearchOutput

    def __init__(self, vector_db: LocalVectorProvider = None, embedding_service: EmbeddingService = None):
        self.vector_db = vector_db or LocalVectorProvider()
        self.embedding_service = embedding_service or EmbeddingService()

    async def execute(self, inputs: DocumentSearchInput, context: ToolContext) -> DocumentSearchOutput:
        query_embedding = self.embedding_service.get_embedding(inputs.query)
        results = await self.vector_db.semantic_search(query_embedding, inputs.top_k)
        
        # If filtering by paper_ids
        if inputs.paper_ids:
            results = [r for r in results if r.get("paper_id") in inputs.paper_ids]
            
        return DocumentSearchOutput(results=results)
