from typing import Dict, Any
from packages.ai_core.agents.base_agent import BaseEnterpriseAgent
from packages.ai_core.agents.agent_registry import AgentRegistry

@AgentRegistry.register("planner")
class PlannerAgent(BaseEnterpriseAgent):
    """
    Specialized agent for decomposing complex tasks into steps.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.capabilities = ["task_decomposition", "planning"]

    async def _execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation interacts with self.llm to generate a plan
        state["plan"] = ["step_1", "step_2"]
        return state
