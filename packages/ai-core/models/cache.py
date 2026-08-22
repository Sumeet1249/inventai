import hashlib
import json
from typing import Optional
from packages.ai_core.models.response import NormalizedAIResponse

class SemanticCache:
    """
    A Redis-backed cache to prevent redundant LLM API calls.
    Hashes the input messages and returns cached normalized responses.
    """
    def __init__(self, redis_client=None):
        # Placeholder for actual Redis connection
        self.redis = redis_client
        self._in_memory = {} # Fallback

    def _hash_messages(self, messages: list) -> str:
        # Simplistic hash of text content
        text = "".join(m.content for m in messages if hasattr(m, 'content'))
        return hashlib.sha256(text.encode()).hexdigest()

    async def get(self, messages: list) -> Optional[NormalizedAIResponse]:
        key = self._hash_messages(messages)
        cached = self._in_memory.get(key)
        if cached:
            cached.is_cached = True
            return cached
        return None

    async def set(self, messages: list, response: NormalizedAIResponse):
        key = self._hash_messages(messages)
        self._in_memory[key] = response
