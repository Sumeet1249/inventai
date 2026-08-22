from packages.ai_core.state import AgentState

def fallback_recovery_node(state: AgentState) -> dict:
    """
    A generic LangGraph node to handle catastrophic tool or LLM failures.
    Routes the graph to an end state gracefully rather than crashing.
    """
    error_msg = state.get("error", "Unknown error occurred during AI execution.")
    
    return {
        "error": f"SYSTEM RECOVERY: {error_msg}",
        # Force the workflow to stop
        "plan": [],
        "current_step": 999 
    }

def route_on_error(state: AgentState) -> str:
    """
    Conditional edge router. Checks if the retry count exceeds limits.
    Returns 'fallback' if limits exceeded, else 'continue'.
    """
    from packages.ai_core.config import config
    
    if state.get("retry_count", 0) >= config.max_retries:
        return "fallback"
    if state.get("error"):
        return "retry"
    return "continue"
