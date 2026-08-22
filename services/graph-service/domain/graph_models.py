from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class GraphNode(BaseModel):
    id: str
    label: str # e.g., 'Patent', 'ResearchPaper', 'Technology', 'Inventor', 'Material', 'CADModel'
    properties: Dict[str, Any]

class GraphEdge(BaseModel):
    id: str
    source_id: str
    target_id: str
    type: str # e.g., 'INVENTED_BY', 'RELATED_TO', 'CITES', 'USES', 'SIMILAR_TO'
    properties: Optional[Dict[str, Any]] = None

class GraphVisualizationResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class RecommendationQuery(BaseModel):
    node_id: str
    node_label: str
    target_label: str
    limit: int = 5
