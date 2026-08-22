from abc import ABC, abstractmethod
from typing import Type, Any, Optional
from pydantic import BaseModel
from langchain_core.tools import BaseTool as LangchainBaseTool
from packages.ai_core.tools.context import ToolContext

class BaseTool(ABC):
    """
    Enterprise Base Tool.
    Enforces strict metadata definition and I/O typing.
    """
    
    # Metadata required for all tools
    name: str
    description: str
    version: str = "1.0.0"
    category: str = "general"
    author: str = "system"
    tags: list[str] = []
    capabilities: list[str] = []
    
    # Strict Pydantic schemas for I/O
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]

    @abstractmethod
    async def execute(self, inputs: BaseModel, context: ToolContext) -> BaseModel:
        """The actual business logic of the tool."""
        pass
        
    def to_langchain_tool(self) -> LangchainBaseTool:
        """Dynamically builds a LangChain compatible tool wrapper."""
        # We will implement this generation within the Factory/Executor
        pass
