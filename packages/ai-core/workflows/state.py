from typing import TypedDict, Annotated, List, Dict, Any, Optional
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
import time

def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Reducer to merge dictionaries in LangGraph state."""
    result = a.copy()
    result.update(b)
    return result

class WorkflowState(TypedDict):
    """
    Advanced Execution State for LangGraph Workflows.
    """
    # 1. Conversation & Memory
    messages: Annotated[list[BaseMessage], add_messages]
    
    # 2. Execution Context
    workflow_id: str
    session_id: str
    
    # 3. Planning & Tasks
    plan: List[str]
    tasks_completed: List[str]
    current_task: Optional[str]
    
    # 4. Storage & Results
    context: Annotated[Dict[str, Any], merge_dicts]
    final_output: Optional[Any]
    
    # 5. Resilience & Errors
    error: Optional[str]
    retry_count: int
    
    # 6. Metrics
    token_usage: Annotated[Dict[str, int], merge_dicts]
    start_time: float

    # 7. Custom Data for Services
    input_data: Dict[str, Any]
    metadata: Annotated[Dict[str, Any], merge_dicts]
    output_data: Dict[str, Any]
