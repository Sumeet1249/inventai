from typing import Dict, Any
from packages.ai_core.agents.base_agent import BaseEnterpriseAgent
from packages.ai_core.agents.agent_registry import AgentRegistry

@AgentRegistry.register("supervisor")
class SupervisorAgent(BaseEnterpriseAgent):
    """
    Oversees other agents, managing retry loops and completion criteria.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities = ["orchestration"]

    async def _execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state
