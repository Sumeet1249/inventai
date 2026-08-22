from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.base_memory import BaseMemorySchema

class ProjectMemory:
    """
    Manages long-term persistence for InventAI Projects.
    e.g., Storing the overall goal, extracted constraints, and generated patents.
    """
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        self.namespace = "project"

    async def initialize_project(self, project_id: str, metadata: dict) -> str:
        mem = BaseMemorySchema(
            id=project_id,
            namespace=self.namespace,
            owner_id="system",
            payload={"state": "initialized"},
            metadata=metadata
        )
        await self.manager.save(mem)
        return mem.id

    async def get_project_state(self, project_id: str) -> BaseMemorySchema:
        return await self.manager.load(self.namespace, "system", project_id)
