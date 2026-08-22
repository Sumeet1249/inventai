from typing import Any, Callable, Dict, List
from langchain_core.tools import tool

class ToolRegistry:
    """
    A dynamic registry for storing and retrieving tools for agents.
    Allows microservices to inject their own specific tools into the workflow.
    """
    _tools: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a tool."""
        def decorator(func):
            langchain_tool = tool(func)
            cls._tools[name] = langchain_tool
            return langchain_tool
        return decorator

    @classmethod
    def get_tool(cls, name: str) -> Callable:
        return cls._tools.get(name)

    @classmethod
    def get_all_tools(cls) -> List[Callable]:
        return list(cls._tools.values())
