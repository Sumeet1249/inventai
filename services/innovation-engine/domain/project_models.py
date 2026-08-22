from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class ProjectState(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    name: str
    description: str
    status: str = Field(default="Initializing")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # State tracking across modules
    patent_data: Optional[Dict[str, Any]] = None
    research_data: Optional[Dict[str, Any]] = None
    cad_data: Optional[Dict[str, Any]] = None
    physics_data: Optional[Dict[str, Any]] = None
    graph_data: Optional[Dict[str, Any]] = None

class WorkflowEvent(BaseModel):
    project_id: str
    event_type: str # e.g., 'NodeCompleted', 'WorkflowFailed'
    node: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ProjectRequest(BaseModel):
    name: str
    idea_description: str
