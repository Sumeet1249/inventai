from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseAgentInterface(ABC):
    """Abstract interface for all enterprise agents."""
    
    @abstractmethod
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Core execution loop for the agent."""
        pass
        
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Returns a list of capabilities this agent possesses."""
        pass
