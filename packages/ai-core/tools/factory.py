from typing import Type, Any
from langchain_core.tools import BaseTool as LangchainBaseTool, StructuredTool
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.executor import ToolExecutor
from packages.ai_core.tools.context import ToolContext
from pydantic import BaseModel

class ToolFactory:
    """
    Instantiates tools, injects dependencies, and converts them to LangChain format.
    """
    
    @staticmethod
    def create_tool(tool_class: Type[BaseTool], **dependencies) -> BaseTool:
        """Instantiates the tool, passing any required dependencies (e.g., DB clients)."""
        return tool_class(**dependencies)
        
    @staticmethod
    def to_langchain_tool(tool: BaseTool, context: ToolContext) -> LangchainBaseTool:
        """
        Wraps our strict Enterprise tool inside a LangChain StructuredTool.
        The wrapper routes execution through our secure ToolExecutor.
        """
        async def async_wrapper(**kwargs):
            result = await ToolExecutor.execute(tool, kwargs, context)
            return result.data
            
        def sync_wrapper(**kwargs):
            import asyncio
            return asyncio.run(async_wrapper(**kwargs))
            
        return StructuredTool.from_function(
            func=sync_wrapper,
            coroutine=async_wrapper,
            name=tool.name,
            description=tool.description,
            args_schema=tool.input_schema
        )
