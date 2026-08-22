class ToolError(Exception):
    """Base exception for all Tool Framework errors."""
    pass

class ToolValidationError(ToolError):
    """Raised when tool inputs or outputs fail Pydantic validation."""
    pass

class ToolPermissionError(ToolError):
    """Raised when an agent lacks permissions to execute a tool."""
    pass

class ToolExecutionError(ToolError):
    """Raised when the underlying tool logic fails."""
    pass

class ToolTimeoutError(ToolError):
    """Raised when a tool execution exceeds the configured timeout."""
    pass

class ToolNotFoundError(ToolError):
    """Raised when an unregistered tool is requested."""
    pass
