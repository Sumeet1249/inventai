import networkx as nx
from typing import List, Dict, Any

class CitationEngine:
    """Builds and analyzes citation graphs between research papers."""
    
    def __init__(self):
        self.graph = nx.DiGraph()

    def add_paper(self, paper_id: str, metadata: Dict[str, Any]):
        self.graph.add_node(paper_id, **metadata)

    def add_citation(self, source_id: str, target_id: str):
        self.graph.add_edge(source_id, target_id)

    def extract_citations(self, text: str) -> List[str]:
        # Dummy citation extraction logic for now, in reality use regex or LLM
        return []

    def get_citation_graph(self, paper_id: str = None) -> Dict[str, Any]:
        # Return graph format suitable for frontend visualization
        nodes = [{"id": str(n), "label": self.graph.nodes[n].get("title", str(n))} for n in self.graph.nodes]
        edges = [{"source": str(u), "target": str(v)} for u, v in self.graph.edges]
        return {"nodes": nodes, "edges": edges}
