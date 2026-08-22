from packages.ai_core.workflows.events import publish_workflow_event

class RetryNode:
    """
    Dedicated node in LangGraph to handle retry increments and backoffs
    before looping back to a failed node.
    """
    async def __call__(self, state: dict) -> dict:
        current_retry = state.get("retry_count", 0) + 1
        
        await publish_workflow_event(
            "node_retry", 
            retry_attempt=current_retry,
            error=state.get("error")
        )
        
        return {
            "retry_count": current_retry,
            "error": None # Clear error to try again
        }
