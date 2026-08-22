from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class InventorSchema(BaseModel):
    name: str
    company: Optional[str] = None

class PatentBase(BaseModel):
    title: str
    abstract: str
    claims: List[str] = Field(default_factory=list)

class PatentCreate(PatentBase):
    inventors: List[InventorSchema] = Field(default_factory=list)

class PatentResponse(PatentBase):
    id: str
    filing_date: datetime
    status: str
    inventors: List[InventorSchema]
    
    class Config:
        orm_mode = True

class SearchQuerySchema(BaseModel):
    query: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10

class AnalysisResultSchema(BaseModel):
    id: str
    analysis_type: str
    findings: Dict[str, Any]
    created_at: datetime
    
    class Config:
        orm_mode = True
