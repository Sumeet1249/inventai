from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class AuthorSchema(BaseModel):
    name: str
    affiliation: Optional[str] = None

class ResearchPaperBase(BaseModel):
    title: str
    abstract: str
    url: Optional[str] = None
    published_date: Optional[datetime] = None

class ResearchPaperCreate(ResearchPaperBase):
    authors: List[AuthorSchema] = Field(default_factory=list)

class ResearchPaperResponse(ResearchPaperBase):
    id: str
    uploaded_at: datetime
    status: str
    authors: List[AuthorSchema]
    
    class Config:
        orm_mode = True

class ResearchQuerySchema(BaseModel):
    query: str
    paper_ids: Optional[List[str]] = None
    top_k: int = 5

class AnalysisResponseSchema(BaseModel):
    id: str
    analysis_type: str
    content: Dict[str, Any]
    created_at: datetime
    
    class Config:
        orm_mode = True
