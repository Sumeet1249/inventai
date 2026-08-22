from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class CADProjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class CADProjectCreate(CADProjectBase):
    pass

class CADModelSchema(BaseModel):
    name: str
    parameters: Dict[str, Any]

class CADModelResponse(CADModelSchema):
    id: str
    project_id: str
    volume: Optional[float] = None
    surface_area: Optional[float] = None
    status: str
    
    class Config:
        orm_mode = True

class CADExportResponse(BaseModel):
    id: str
    model_id: str
    format: str
    file_path: str
    
    class Config:
        orm_mode = True

class CADGenerationRequest(BaseModel):
    project_id: str
    prompt: str = Field(description="Natural language description of the part.")
    constraints: Optional[Dict[str, Any]] = None
