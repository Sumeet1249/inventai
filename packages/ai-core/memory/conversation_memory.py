from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.base_memory import BaseMemorySchema
from packages.ai_core.memory.history import HistoryUtils
from langchain_core.messages import BaseMessage
from typing import List

class ConversationMemory:
    """
    Manages continuous chat histories between a user and an agent.
    Provides hooks for automatic compression when context windows grow too large.
    """
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        self.namespace = "conversation"

    async def append_message(self, user_id: str, thread_id: str, message: BaseMessage):
        try:
            mem = await self.manager.load(self.namespace, user_id, thread_id)
        except Exception:
            # Initialize if not found
            mem = BaseMemorySchema(
                id=thread_id,
                namespace=self.namespace,
                owner_id=user_id,
                payload={"messages": []}
            )
            
        mem.payload["messages"].append(message.model_dump())
        await self.manager.save(mem)

    async def get_recent_history(self, user_id: str, thread_id: str, k: int = 10) -> List[dict]:
        mem = await self.manager.load(self.namespace, user_id, thread_id)
        # Note: In production we would deserialize dicts back to LangChain BaseMessages
        messages = mem.payload.get("messages", [])
        return messages[-k:] if len(messages) > k else messages
