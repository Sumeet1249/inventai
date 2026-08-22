import asyncio
import logging
from typing import List
from langchain_core.messages import BaseMessage
from packages.ai_core.models.config import config
from packages.ai_core.models.exceptions import ExhaustedFailoverError
from packages.ai_core.models.registry import ModelRegistry
from packages.ai_core.models.response import NormalizedAIResponse, TokenUsage
from packages.ai_core.models.cache import SemanticCache
from packages.ai_core.models.metrics import ModelMetrics
from packages.ai_core.models.base_model import ChatModel

logger = logging.getLogger("ai_factory")
cache = SemanticCache()

class AIModelFactory(ChatModel):
    """
    The central unified interface for all Domain Services.
    Implements Automatic Failover, Retries, Timeouts, and Caching.
    """
    def __init__(self, preferred_provider: str = None, model_name: str = "gpt-4-turbo"):
        self.preferred_provider = preferred_provider or config.failover_providers[0]
        self.model_name = model_name

    def _get_api_key(self, provider: str) -> str:
        keys = {
            "openai": config.openai_api_key,
            "anthropic": config.anthropic_api_key,
            "gemini": config.gemini_api_key,
        }
        return keys.get(provider, "dummy_key")

    def _normalize_langchain_response(self, provider: str, lc_response) -> NormalizedAIResponse:
        """Converts diverse LangChain outputs into a strict NormalizedAIResponse."""
        usage_metadata = lc_response.response_metadata.get("token_usage", {})
        
        # Safe extraction of tokens
        prompt_t = usage_metadata.get("prompt_tokens", 0)
        comp_t = usage_metadata.get("completion_tokens", 0)
        
        # Safe extraction of finish reason
        finish = lc_response.response_metadata.get("finish_reason", "stop")
        
        return NormalizedAIResponse(
            content=lc_response.content,
            provider=provider,
            model=self.model_name,
            usage=TokenUsage(
                prompt_tokens=prompt_t,
                completion_tokens=comp_t,
                total_tokens=prompt_t + comp_t
            ),
            finish_reason=finish
        )

    async def generate(self, messages: List[BaseMessage], **kwargs) -> NormalizedAIResponse:
        """Executes the LLM call with a robust failover chain."""
        
        # 1. Check Cache
        if config.enable_caching:
            cached = await cache.get(messages)
            if cached:
                return cached

        # 2. Build Failover Chain
        chain = [self.preferred_provider] + [p for p in config.failover_providers if p != self.preferred_provider]
        
        for provider in chain:
            try:
                # Resolve underlying LangChain implementation
                langchain_cls = ModelRegistry.get_langchain_class(provider)
                llm = langchain_cls(
                    model=self.model_name,
                    api_key=self._get_api_key(provider),
                    max_retries=config.max_retries,
                    timeout=config.timeout_ms / 1000
                )
                
                # Execute with Metrics
                logger.info(f"Attempting inference with provider: {provider}")
                raw_response = await ModelMetrics.track_latency(provider, llm.ainvoke, messages)
                
                # Normalize
                normalized = self._normalize_langchain_response(provider, raw_response)
                
                # Cache and return
                if config.enable_caching:
                    await cache.set(messages, normalized)
                    
                return normalized
                
            except Exception as e:
                logger.warning(f"Provider {provider} failed: {e}. Failing over...")
                continue
                
        raise ExhaustedFailoverError(f"All providers in the failover chain failed.")

    async def stream(self, messages: List[BaseMessage], **kwargs):
        raise NotImplementedError("Streaming is implemented in streaming.py wrapper")
