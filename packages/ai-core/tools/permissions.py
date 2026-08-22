from packages.ai_core.tools.context import ToolContext
from packages.ai_core.tools.base_tool import BaseTool
from packages.ai_core.tools.exceptions import ToolPermissionError

class ToolPermissionManager:
    """
    Sandbox Interface evaluating if an agent/context has permission to run a tool.
    """
    @staticmethod
    def check_permissions(tool: BaseTool, context: ToolContext) -> bool:
        """
        Validates roles against tool capabilities/tags.
        In production, this could query a PostgreSQL permissions table.
        """
        # Example hardcoded rule: 'admin' tag requires 'admin' role
        if "admin" in tool.tags and "admin" not in context.roles:
            raise ToolPermissionError(f"Context {context.agent_id} lacks 'admin' role for tool {tool.name}")
            
        return True
