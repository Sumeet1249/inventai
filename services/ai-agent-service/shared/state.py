from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The state of the InventCore LangGraph workflow.
    """
    messages: Annotated[list, add_messages]
    project_id: str
    user_request: str
    plan: List[str]
    patent_insights: List[Dict[str, Any]]
    research_insights: List[Dict[str, Any]]
    cad_parameters: Dict[str, Any]
    physics_results: Dict[str, Any]
    validation_status: str
    final_report_path: str
