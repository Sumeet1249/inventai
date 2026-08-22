from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseWorkflowNode(ABC):
    """Abstract interface for all nodes in the workflow."""
    
    @abstractmethod
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the state and return updates."""
        pass

class BaseWorkflowRouter(ABC):
    """Abstract interface for conditional routing logic."""
    
    @abstractmethod
    def route(self, state: Dict[str, Any]) -> str:
        """Evaluate the state and return the next node name."""
        pass
