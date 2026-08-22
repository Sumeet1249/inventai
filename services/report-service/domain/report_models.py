from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class ReportRequest(BaseModel):
    project_id: str
    report_type: str = Field(description="'patent_draft', 'engineering_report', 'executive_summary'")
    theme: str = Field(default="corporate")
    project_data: Dict[str, Any]

class ReportMetadata(BaseModel):
    id: str = Field(default_factory=generate_uuid)
    project_id: str
    report_type: str
    status: str = Field(default="Drafting")
    download_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
