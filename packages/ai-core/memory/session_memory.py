from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.base_memory import BaseMemorySchema
from packages.ai_core.memory.config import config

class SessionMemory:
    """
    Manages ephemeral data for active user sessions.
    Automatically expires based on config TTL.
    """
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        self.namespace = "session"

    async def set_session_data(self, user_id: str, session_id: str, data: dict):
        mem = BaseMemorySchema(
            id=session_id,
            namespace=self.namespace,
            owner_id=user_id,
            payload=data
        )
        # Apply TTL for short-term persistence
        await self.manager.save(mem, ttl=config.session_ttl_seconds)

    async def get_session_data(self, user_id: str, session_id: str) -> BaseMemorySchema:
        return await self.manager.load(self.namespace, user_id, session_id)
