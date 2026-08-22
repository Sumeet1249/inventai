from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseMemory(ABC):
    """Abstract interface for Long-Term memory persistence."""
    
    @abstractmethod
    async def get_history(self, session_id: str) -> list:
        pass
        
    @abstractmethod
    async def save_context(self, session_id: str, context: Dict[str, Any]):
        pass

class BaseCheckpoint(ABC):
    """Abstract interface for LangGraph short-term execution checkpoints."""
    
    @abstractmethod
    def get_saver(self):
        pass

class BaseToolInterface(ABC):
    """Abstract interface for all tools registered in the ToolRegistry."""
    
    @abstractmethod
    def get_tool_definition(self) -> Any:
        pass
