from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Standard Base State for any LangGraph workflow in InventAI.
    Services can inherit this TypedDict to add domain-specific fields.
    """
    # Tracks the conversation history and agent outputs
    messages: Annotated[list[BaseMessage], add_messages]
    
    # Context injected at the start of the workflow
    project_id: str
    user_id: str
    
    # Planner outputs
    plan: List[str]
    current_step: int
    
    # Generic key-value store for tool outputs
    context: Dict[str, Any]
    
    # Error tracking
    error: Optional[str]
    retry_count: int
