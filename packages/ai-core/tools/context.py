from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

class ToolContext(BaseModel):
    """
    Context injected into every tool execution.
    Contains metadata about who is calling the tool and why.
    """
    session_id: str
    workflow_id: str
    agent_id: str
    roles: list[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
