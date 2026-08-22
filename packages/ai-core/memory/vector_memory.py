from typing import List, Dict, Any
from packages.ai_core.memory.interfaces import VectorStoreProvider

class VectorMemory:
    """
    Knowledge Memory Layer.
    Provides semantic search abstractions without hardcoding ChromaDB or Pinecone.
    """
    def __init__(self, provider: VectorStoreProvider):
        # The concrete provider (e.g., ChromaStoreAdapter) is injected via DI.
        self.provider = provider

    async def index_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Indexes unstructured knowledge for RAG."""
        await self.provider.add_documents(documents, embeddings)

    async def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves semantically similar documents."""
        return await self.provider.semantic_search(query_embedding, top_k)
