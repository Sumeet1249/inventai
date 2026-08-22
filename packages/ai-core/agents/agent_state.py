from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from langchain_core.messages import BaseMessage

class AgentState(BaseModel):
    """
    Standard state schema passed between agents during delegation.
    """
    session_id: str
    messages: List[BaseMessage] = Field(default_factory=list)
    context_data: Dict[str, Any] = Field(default_factory=dict)
    current_task: Optional[str] = None
    delegation_depth: int = 0
    errors: List[str] = Field(default_factory=list)
