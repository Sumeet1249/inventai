from packages.ai_core.workflows.state import WorkflowState
from packages.ai_core.workflows.interfaces import BaseWorkflowRouter

class TaskRouter(BaseWorkflowRouter):
    """
    Evaluates the state and routes to the appropriate node.
    Supports sequential and conditional workflows.
    """
    def route(self, state: WorkflowState) -> str:
        if state.get("error"):
            # Check retry limits (we can check the config here, assuming 3 for now)
            if state.get("retry_count", 0) >= 3:
                return "fallback"
            return "retry"
            
        plan = state.get("plan", [])
        tasks_completed = state.get("tasks_completed", [])
        
        if len(tasks_completed) < len(plan):
            return "executor"
            
        return "reviewer"
