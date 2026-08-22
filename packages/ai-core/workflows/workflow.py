from packages.ai_core.workflows.workflow_builder import WorkflowBuilder
from packages.ai_core.workflows.checkpoint import WorkflowCheckpointManager
from packages.ai_core.workflows.stream import WorkflowStreamer
from packages.ai_core.workflows.events import publish_workflow_event
from packages.ai_core.workflows.planner import PlannerNode
from packages.ai_core.workflows.executor import ExecutorNode
from packages.ai_core.workflows.reviewer import ReviewerNode
from packages.ai_core.workflows.retry import RetryNode
import uuid

class ExecutionEngine:
    """
    The main entrypoint for executing workflows (Synchronous and Asynchronous).
    """
    def __init__(self, compiled_app):
        self.app = compiled_app

    async def execute_async(self, initial_state: dict, session_id: str = None) -> dict:
        """Executes a workflow asynchronously from start to finish."""
        session_id = session_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}
        
        await publish_workflow_event("workflow_started", session_id=session_id)
        
        final_state = await self.app.ainvoke(initial_state, config=config)
        
        await publish_workflow_event("workflow_finished", session_id=session_id)
        return final_state

    async def stream_async(self, initial_state: dict, session_id: str = None):
        """Streams a workflow's execution."""
        session_id = session_id or str(uuid.uuid4())
        config = {"configurable": {"thread_id": session_id}}
        
        await publish_workflow_event("workflow_started", session_id=session_id)
        
        async for chunk in WorkflowStreamer.stream_graph(self.app, initial_state, config):
            yield chunk
            
        await publish_workflow_event("workflow_finished", session_id=session_id)

    def execute_sync(self, initial_state: dict, session_id: str = None) -> dict:
        """Synchronous wrapper for legacy integrations."""
        import asyncio
        return asyncio.run(self.execute_async(initial_state, session_id))
