from packages.ai_core.interfaces.core_interfaces import BaseCheckpoint
from packages.ai_core.workflows.events import publish_workflow_event
from langgraph.checkpoint.memory import MemorySaver

class WorkflowCheckpointManager(BaseCheckpoint):
    """
    Advanced Checkpoint Manager for LangGraph workflows.
    Handles persistence hooks and interrupt/resume states.
    """
    def __init__(self):
        self._saver = MemorySaver()

    def get_saver(self):
        return self._saver

    async def save_hook(self, thread_id: str, state: dict):
        """Hook called when state is persisted."""
        await publish_workflow_event("checkpoint_saved", thread_id=thread_id, state=state)

    async def load_hook(self, thread_id: str):
        """Hook called when state is resumed."""
        await publish_workflow_event("checkpoint_loaded", thread_id=thread_id)
