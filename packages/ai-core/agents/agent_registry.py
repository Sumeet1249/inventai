from typing import Dict, Type
from packages.ai_core.agents.interfaces import BaseAgentInterface
from packages.ai_core.agents.exceptions import AgentRegistryError

class AgentRegistry:
    """
    Dynamic registry for specialized enterprise agents.
    Allows discovery and delegation by role.
    """
    _agents: Dict[str, Type[BaseAgentInterface]] = {}

    @classmethod
    def register(cls, role_name: str):
        def wrapper(agent_class: Type[BaseAgentInterface]):
            cls._agents[role_name] = agent_class
            return agent_class
        return wrapper

    @classmethod
    def get_agent_class(cls, role_name: str) -> Type[BaseAgentInterface]:
        agent_cls = cls._agents.get(role_name)
        if not agent_cls:
            raise AgentRegistryError(f"Agent role '{role_name}' not found in registry.")
        return agent_cls
