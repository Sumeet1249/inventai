from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.base_memory import BaseMemorySchema

class CacheMemory:
    """
    Key-Value store wrapper tailored for Tool and Model memoization.
    """
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        self.namespace = "cache"

    async def set(self, key: str, value: dict, ttl: int = 3600):
        mem = BaseMemorySchema(
            id=key,
            namespace=self.namespace,
            owner_id="system",
            payload=value
        )
        await self.manager.save(mem, ttl=ttl)

    async def get(self, key: str) -> dict:
        try:
            mem = await self.manager.load(self.namespace, "system", key)
            return mem.payload
        except Exception:
            return None
