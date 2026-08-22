from typing import List, Optional
from pydantic import BaseModel, Field

# Base Node Model
class NodeBase(BaseModel):
    id: str
    label: str

# Concrete Nodes
class PatentNode(NodeBase):
    label: str = "Patent"
    title: str
    assignee: Optional[str] = None
    date: Optional[str] = None

class ResearchPaperNode(NodeBase):
    label: str = "ResearchPaper"
    title: str
    authors: Optional[List[str]] = []
    year: Optional[int] = None
    abstract: Optional[str] = None

class TechnologyNode(NodeBase):
    label: str = "Technology"
    name: str
    domain: Optional[str] = None

class InventorNode(NodeBase):
    label: str = "Inventor"
    name: str

class OrganizationNode(NodeBase):
    label: str = "Organization"
    name: str
    type: Optional[str] = None

class MaterialNode(NodeBase):
    label: str = "Material"
    name: str
    properties: Optional[dict] = {}

class CADModelNode(NodeBase):
    label: str = "CADModel"
    file_path: str

class SimulationNode(NodeBase):
    label: str = "Simulation"
    results: Optional[dict] = {}

class ProjectNode(NodeBase):
    label: str = "Project"
    name: str
    status: Optional[str] = None

# Base Edge Model
class EdgeBase(BaseModel):
    source_id: str
    target_id: str
    type: str
    properties: Optional[dict] = {}
