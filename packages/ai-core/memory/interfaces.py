from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class BaseMemoryProvider(ABC):
    """
    Abstract interface for all standard persistence layers (SQL, Redis).
    """
    @abstractmethod
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        pass
        
    @abstractmethod
    async def set(self, key: str, value: Dict[str, Any], ttl: Optional[int] = None):
        pass

    @abstractmethod
    async def delete(self, key: str):
        pass

class VectorStoreProvider(ABC):
    """
    Abstract interface for all Vector databases (Chroma, Qdrant, Pinecone).
    Ensures the AI Core is decoupled from specific vendor SDKs.
    """
    @abstractmethod
    async def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        pass

    @abstractmethod
    async def semantic_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        pass
