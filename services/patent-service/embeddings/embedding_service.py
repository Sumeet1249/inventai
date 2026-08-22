from sentence_transformers import SentenceTransformer
from typing import List
import os

class EmbeddingService:
    """
    Generates dense vector embeddings using SentenceTransformers.
    """
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # We can configure this via environment variable in production
        self.model_name = os.getenv("EMBEDDING_MODEL", model_name)
        # Lazy loading to avoid memory overhead if not used
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def embed_text(self, text: str) -> List[float]:
        """Generates an embedding for a single string."""
        return self.model.encode(text).tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generates embeddings for a batch of strings."""
        return self.model.encode(texts).tolist()

# Singleton instance
embedding_service = EmbeddingService()
