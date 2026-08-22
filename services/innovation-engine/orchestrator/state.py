from typing import TypedDict, Annotated, List, Dict, Any, Optional
from pydantic import BaseModel, Field
import operator

def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """Reducer to merge dictionaries in LangGraph state."""
    if not a: a = {}
    if not b: b = {}
    result = a.copy()
    result.update(b)
    return result

class InnovationWorkflowState(TypedDict):
    """Shared state for the Innovation Engine LangGraph workflow."""
    
    # Context
    project_id: str
    user_id: Optional[str]
    idea: str
    
    # Execution State
    plan: List[str]
    current_step: Optional[str]
    completed_steps: Annotated[List[str], operator.add]
    
    # Results & Logs
    artifacts: Annotated[Dict[str, Any], merge_dicts]
    logs: Annotated[List[str], operator.add]
    metadata: Annotated[Dict[str, Any], merge_dicts]
    
    # Resilience
    errors: Annotated[List[str], operator.add]
    timing: Annotated[Dict[str, float], merge_dicts]

class WorkflowStartRequest(BaseModel):
    project_id: str
    idea: str
    user_id: Optional[str] = "system"
