from packages.ai_core.workflows.interfaces import BaseWorkflowNode
from packages.ai_core.workflows.state import WorkflowState
from packages.ai_core.workflows.events import publish_workflow_event

class ExecutorNode(BaseWorkflowNode):
    """
    Executes tasks sequentially or in parallel based on the plan.
    """
    def __init__(self, tool_executor):
        self.tool_executor = tool_executor

    async def __call__(self, state: WorkflowState) -> dict:
        plan = state.get("plan", [])
        completed = state.get("tasks_completed", [])
        
        if len(completed) >= len(plan):
            return {} # Nothing to do
            
        current_task = plan[len(completed)]
        await publish_workflow_event("node_started", node="executor", task=current_task)
        
        # Execute the task (this would use self.tool_executor and LLM in reality)
        # We simulate adding it to context.
        result_context = {f"task_{len(completed)}_result": f"Executed: {current_task}"}
        
        await publish_workflow_event("node_finished", node="executor", task=current_task)
        
        return {
            "current_task": current_task,
            "tasks_completed": completed + [current_task],
            "context": result_context
        }
