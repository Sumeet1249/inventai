from typing import List, Dict, Any
from packages.ai_core.memory.interfaces import VectorStoreProvider
from services.research_service.indexing.chroma_store import ChromaVectorStore

class LocalVectorProvider(VectorStoreProvider):
    """
    Concrete implementation of the AI Core VectorStoreProvider.
    Wraps ChromaDB.
    """
    def __init__(self):
        self.store = ChromaVectorStore()

    async def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Indexes parsed documents into the vector database."""
        return await self.store.add_documents(documents, embeddings)

    async def semantic_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieves semantically similar documents."""
        return await self.store.semantic_search(query_embedding, top_k)
