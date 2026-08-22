class AgentError(Exception):
    """Base exception for all AI Agent Framework errors."""
    pass

class AgentExecutionError(AgentError):
    """Raised when an agent fails to execute a task."""
    pass

class AgentDelegationError(AgentError):
    """Raised when an agent fails to delegate a task to a subordinate."""
    pass

class AgentTimeoutError(AgentError):
    """Raised when an agent execution exceeds the configured timeout."""
    pass

class AgentRegistryError(AgentError):
    """Raised when an unknown agent is requested from the registry."""
    pass
