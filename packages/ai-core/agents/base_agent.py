from typing import Dict, Any, List
from packages.ai_core.agents.interfaces import BaseAgentInterface
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.models.base_model import ChatModel
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.agents.agent_metrics import AgentMetrics
from packages.ai_core.agents.exceptions import AgentExecutionError
from packages.ai_core.agents.agent_config import config

class BaseEnterpriseAgent(BaseAgentInterface):
    """
    The foundational class for all specialized agents.
    Injects memory and models. Wraps execution in telemetry.
    """
    def __init__(self, context: AgentContext, llm: ChatModel, memory: MemoryManager):
        self.context = context
        self.llm = llm
        self.memory = memory
        self.capabilities: List[str] = []

    def get_capabilities(self) -> List[str]:
        return self.capabilities

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Wraps the internal _execute logic with AgentMetrics.
        """
        async def _run():
            if state.get("delegation_depth", 0) > config.max_delegation_depth:
                raise AgentExecutionError("Max delegation depth exceeded.")
            return await self._execute(state)
            
        return await AgentMetrics.track_execution(self.context.agent_id, _run)

    async def _execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Override this method in subclasses to implement domain logic."""
        raise NotImplementedError("Subclasses must implement _execute")
