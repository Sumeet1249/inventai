from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator
from langchain_core.messages import BaseMessage
from packages.ai_core.models.response import NormalizedAIResponse

class BaseAIModel(ABC):
    """Abstract interface for all AI models."""
    pass

class ChatModel(BaseAIModel):
    """Interface for text-based chat completions."""
    
    @abstractmethod
    async def generate(self, messages: List[BaseMessage], **kwargs) -> NormalizedAIResponse:
        pass

    @abstractmethod
    async def stream(self, messages: List[BaseMessage], **kwargs) -> AsyncGenerator[NormalizedAIResponse, None]:
        pass

class EmbeddingModel(BaseAIModel):
    """Interface for text embeddings."""
    
    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        pass

class VisionModel(ChatModel):
    """Interface for models that support image inputs."""
    pass

class ReasoningModel(ChatModel):
    """Interface for models that output internal reasoning traces (e.g., o1)."""
    pass
