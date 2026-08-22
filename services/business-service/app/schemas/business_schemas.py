from pydantic import BaseModel
from typing import Dict, Any

class BusinessRequest(BaseModel):
    project_id: str
    idea_description: str
    project_data: Dict[str, Any]
