from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.base_memory import BaseMemorySchema

class WorkflowMemory:
    """
    Manages state persistence for LangGraph workflows.
    Allows long-running workflows to pause and resume seamlessly.
    """
    def __init__(self, manager: MemoryManager):
        self.manager = manager
        self.namespace = "workflow"

    async def save_state(self, workflow_id: str, state: dict):
        """Persists the entire workflow state dict."""
        try:
            mem = await self.manager.load(self.namespace, "system", workflow_id)
            mem.update_payload(state)
        except Exception:
            mem = BaseMemorySchema(
                id=workflow_id,
                namespace=self.namespace,
                owner_id="system",
                payload=state
            )
        await self.manager.save(mem)

    async def load_state(self, workflow_id: str) -> dict:
        """Retrieves the paused state to resume execution."""
        mem = await self.manager.load(self.namespace, "system", workflow_id)
        return mem.payload
