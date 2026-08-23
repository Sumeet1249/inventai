from packages.ai_core.agents.agent_registry import AgentRegistry
from packages.ai_core.agents.agent_context import AgentContext
from packages.ai_core.models.factory import AIModelFactory
from packages.ai_core.memory.memory_manager import MemoryManager
# In production, memory provider is passed in or loaded from env
from packages.ai_core.agents.interfaces import BaseAgentInterface

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
