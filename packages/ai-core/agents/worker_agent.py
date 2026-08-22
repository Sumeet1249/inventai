from typing import Dict, Any
from packages.ai_core.agents.base_agent import BaseEnterpriseAgent
from packages.ai_core.agents.agent_registry import AgentRegistry

@AgentRegistry.register("worker")
class WorkerAgent(BaseEnterpriseAgent):
    """
    Specialized agent for executing specific tools.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities = ["tool_execution"]

    async def _execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation interacts with ToolRegistry
        state["tasks_completed"] = state.get("tasks_completed", []) + [state.get("current_task")]
        return state
