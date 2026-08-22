from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Patent(BaseModel):
    id: str = Field(..., description="Unique patent identifier")
    title: str
    abstract: str
    filing_date: Optional[datetime] = None
    assignee: Optional[str] = None
    technology_domain: Optional[str] = None
    url: Optional[str] = None

class Material(BaseModel):
    id: str
    name: str
    chemical_formula: Optional[str] = None
    properties: Optional[dict] = None

class ResearchPaper(BaseModel):
    doi: str
    title: str
    authors: List[str]
    publication_date: Optional[datetime] = None
    abstract: str

class AIResponse(BaseModel):
    status: str = Field(..., description="'success' or 'error'")
    message: str
    data: Optional[dict] = None
    agent_id: Optional[str] = None

class GraphNode(BaseModel):
    id: str
    label: str
    properties: dict

class GraphRelationship(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: dict
