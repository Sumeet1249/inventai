from pydantic import BaseModel, Field
from typing import Any, Dict

class AgentContext(BaseModel):
    """
    Dependency Injection context passed to agents upon instantiation.
    Contains configurations and permissions.
    """
    agent_id: str
    role: str
    permissions: list[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
