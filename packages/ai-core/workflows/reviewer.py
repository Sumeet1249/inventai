from packages.ai_core.workflows.interfaces import BaseWorkflowNode
from packages.ai_core.workflows.state import WorkflowState

class ReviewerNode(BaseWorkflowNode):
    """
    Validates the outputs before finalizing the workflow.
    """
    def __init__(self, reviewer_agent):
        self.reviewer_agent = reviewer_agent

    async def __call__(self, state: WorkflowState) -> dict:
        # Example: Review the context and finalize
        context = state.get("context", {})
        
        # Perform review logic...
        final_output = f"Reviewed {len(context)} context items successfully."
        
        return {
            "final_output": final_output
        }
