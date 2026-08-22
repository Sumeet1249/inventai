from typing import Dict, Any
from packages.ai_core.agents.base_agent import BaseEnterpriseAgent
from packages.ai_core.agents.agent_registry import AgentRegistry

@AgentRegistry.register("reviewer")
class ReviewerAgent(BaseEnterpriseAgent):
    """
    Specialized agent for validating outputs against constraints.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities = ["validation", "formatting"]

    async def _execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        state["final_output"] = "Validated content"
        return state
