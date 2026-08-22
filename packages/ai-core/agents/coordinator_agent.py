from typing import Dict, Any
from packages.ai_core.agents.base_agent import BaseEnterpriseAgent
from packages.ai_core.agents.agent_registry import AgentRegistry

@AgentRegistry.register("coordinator")
class CoordinatorAgent(BaseEnterpriseAgent):
    """
    Coordinates complex parallel tasks across multiple domain agents.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities = ["parallel_coordination"]

    async def _execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state
