import json
from typing import AsyncGenerator, List
from langchain_core.messages import BaseMessage
from packages.ai_core.models.response import NormalizedAIResponse, TokenUsage
from packages.ai_core.models.registry import ModelRegistry
from packages.ai_core.models.config import config
import logging

logger = logging.getLogger("ai_streaming")

class StreamNormalizer:
    """
    Standardizes the chaotic streaming outputs of different LLM providers 
    into a clean, predictable SSE generator.
    """
    def __init__(self, provider: str, model_name: str):
        self.provider = provider
        self.model_name = model_name

    def _get_api_key(self) -> str:
        keys = {
            "openai": config.openai_api_key,
            "anthropic": config.anthropic_api_key,
            "gemini": config.gemini_api_key,
        }
        return keys.get(self.provider, "dummy_key")

    async def stream(self, messages: List[BaseMessage]) -> AsyncGenerator[str, None]:
        langchain_cls = ModelRegistry.get_langchain_class(self.provider)
        llm = langchain_cls(
            model=self.model_name,
            api_key=self._get_api_key()
        )
        
        try:
            async for chunk in llm.astream(messages):
                # Standardize chunks for frontend consumption
                payload = {
                    "type": "content_chunk",
                    "content": chunk.content,
                    "provider": self.provider
                }
                yield f"data: {json.dumps(payload)}\n\n"
                
            # Stream finished payload
            yield f"data: {json.dumps({'type': 'stream_finished', 'provider': self.provider})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming failed for {self.provider}: {e}")
            yield f"data: {json.dumps({'type': 'error', 'details': str(e)})}\n\n"
