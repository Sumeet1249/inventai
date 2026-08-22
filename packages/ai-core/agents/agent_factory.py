from packages.ai_core.agents.agent_registry import AgentRegistry
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.models.factory import AIModelFactory
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.agents.interfaces import BaseAgentInterface

# Auto-import all agents so their @AgentRegistry.register decorators fire
# before any call to AgentFactory.create_agent(). This eliminates the fragile
# side-effect import pattern where callers had to manually import agents first.
from packages.ai_core.agents import planner_agent as _pa   # noqa: F401
from packages.ai_core.agents import worker_agent as _wa    # noqa: F401


class AgentFactory:
    """
    Dependency Injection Container for instantiating specialized Agents.
    Automatically injects the standard ModelFactory and MemoryManager.
    """
    @staticmethod
    def create_agent(role_name: str, context: AgentContext, memory_manager: MemoryManager) -> BaseAgentInterface:
        agent_cls = AgentRegistry.get_agent_class(role_name)

        # Inject standard dependencies
        model_factory = AIModelFactory()

        return agent_cls(
            context=context,
            llm=model_factory,
            memory=memory_manager
        )
