from typing import List, Dict, Any
from packages.ai_core.memory.interfaces import BaseMemoryProvider
from packages.ai_core.memory.base_memory import BaseMemorySchema
from packages.ai_core.memory.serializer import MemorySerializer
from packages.ai_core.memory.exceptions import MemoryNotFoundError

class MemoryManager:
    """
    The central facade for CRUD operations on short-term and long-term memory.
    """
    def __init__(self, provider: BaseMemoryProvider):
        self.provider = provider

    async def save(self, memory: BaseMemorySchema, ttl: int = None) -> BaseMemorySchema:
        """Serializes and saves a memory object."""
        data = MemorySerializer.serialize(memory.model_dump())
        # We store by composite key
        key = f"{memory.namespace}:{memory.owner_id}:{memory.id}"
        
        await self.provider.set(key, {"data": data}, ttl=ttl)
        return memory

    async def load(self, namespace: str, owner_id: str, memory_id: str) -> BaseMemorySchema:
        """Loads and deserializes a memory object."""
        key = f"{namespace}:{owner_id}:{memory_id}"
        result = await self.provider.get(key)
        
        if not result:
            raise MemoryNotFoundError(f"Memory {key} not found.")
            
        parsed_data = MemorySerializer.deserialize(result["data"])
        return BaseMemorySchema(**parsed_data)

    async def compress_context(self, conversation_history: List[Dict[str, Any]]) -> str:
        """
        Stub for memory compression. In production, this calls a cheap LLM to 
        summarize old messages, freeing up tokens for the main reasoning model.
        """
        # Compression logic...
        return "Summarized history..."
