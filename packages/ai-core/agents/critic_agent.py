from typing import Dict, Any
from packages.ai_core.agents.base_agent import BaseEnterpriseAgent
from packages.ai_core.agents.agent_registry import AgentRegistry

@AgentRegistry.register("critic")
class CriticAgent(BaseEnterpriseAgent):
    """
    Challenges assumptions and identifies flaws in generated plans/outputs.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities = ["critique"]

    async def _execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state
