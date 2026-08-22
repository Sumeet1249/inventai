from typing import Dict, Type
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.exceptions import ToolNotFoundError

class ToolRegistry:
    """
    Dynamic registry for enterprise tools.
    """
    _tools: Dict[str, Type[BaseTool]] = {}

    @classmethod
    def register(cls, tool_class: Type[BaseTool]):
        cls._tools[tool_class.name] = tool_class
        return tool_class

    @classmethod
    def get_tool_class(cls, name: str) -> Type[BaseTool]:
        tool_cls = cls._tools.get(name)
        if not tool_cls:
            raise ToolNotFoundError(f"Tool {name} not found in registry.")
        return tool_cls

    @classmethod
    def get_all_classes(cls) -> list[Type[BaseTool]]:
        return list(cls._tools.values())
