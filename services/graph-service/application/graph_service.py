from fastapi import FastAPI
from services.graph_service.workflows.graph_workflow import build_graph_orchestration_workflow
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.workflows.state import WorkflowState
from services.graph_service.infrastructure.neo4j_driver import Neo4jDriver
from services.graph_service.cypher.queries import GET_SUBGRAPH_QUERY

class GraphApplicationService:
    """
    Business use case orchestrator for Knowledge Graph Intelligence.
    Ties together Neo4j infrastructure, AI Workflows, and NetworkX algorithms.
    """
    def __init__(self, memory_manager: MemoryManager, neo4j_driver: Neo4jDriver = None):
        self.memory = memory_manager
        self.neo4j = neo4j_driver or Neo4jDriver()
        self.workflow = build_graph_orchestration_workflow(self.memory)

    async def get_recommendation(self, entity_id: str) -> dict:
        """
        Triggers the LangGraph orchestration to traverse the Neo4j database 
        and discover hidden technological/material connections.
        """
        initial_state = WorkflowState(
            workflow_id="temp_graph", 
            session_id="temp_graph", 
            input_data={"entity_id": entity_id}
        )
        
        final_state = await self.workflow.ainvoke(initial_state.model_dump())
        
        return final_state.get("output_data", {})

    async def get_subgraph(self, node_id: str) -> dict:
        """
        Executes a real Cypher query to fetch the local neighborhood of a node.
        Formats the output specifically for Cytoscape.js frontend components.
        """
        records = await self.neo4j.execute_read(GET_SUBGRAPH_QUERY, {"node_id": node_id})
        
        nodes_dict = {}
        edges = []
        
        for record in records:
            n = record.get("n")
            m = record.get("m")
            r = record.get("r")
            
            if n:
                n_id = str(n.element_id if hasattr(n, 'element_id') else n.id)
                nodes_dict[n_id] = {"data": {"id": n_id, "label": n.get("title", n.get("name", list(n.labels)[0] if hasattr(n, 'labels') else "Node"))}}
            if m:
                m_id = str(m.element_id if hasattr(m, 'element_id') else m.id)
                nodes_dict[m_id] = {"data": {"id": m_id, "label": m.get("title", m.get("name", list(m.labels)[0] if hasattr(m, 'labels') else "Node"))}}
            if r and n and m:
                n_id = str(n.element_id if hasattr(n, 'element_id') else n.id)
                m_id = str(m.element_id if hasattr(m, 'element_id') else m.id)
                edges.append({"data": {"source": n_id, "target": m_id, "label": type(r).__name__}})
                
        return {
            "nodes": list(nodes_dict.values()),
            "edges": edges
        }

# Create and configure FastAPI app
app = FastAPI(
    title="InventAI Graph Service",
    description="Knowledge graph intelligence using Neo4j and LangGraph",
    version="1.0.0"
)

# Lazy import to avoid circular dependencies
from services.graph_service.api.routers import router
app.include_router(router)
