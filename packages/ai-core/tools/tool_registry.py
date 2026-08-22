from langchain_core.tools import BaseTool
from typing import Dict, List, Type

class ToolRegistry:
    """
    Enterprise Tool Registry for injecting LangChain tools dynamically.
    """
    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, tool_class: Type[BaseTool]):
        """Registers a BaseTool class."""
        cls._tools[tool_class.name] = tool_class
        return tool_class

    @classmethod
    def get_tool_instance(cls, name: str, **kwargs) -> BaseTool:
        tool_cls = cls._tools.get(name)
        if not tool_cls:
            raise ValueError(f"Tool {name} not found in registry.")
        return tool_cls(**kwargs)

    @classmethod
    def get_all_tools(cls, **kwargs) -> List[BaseTool]:
        return [tool_cls(**kwargs) for tool_cls in cls._tools.values()]
