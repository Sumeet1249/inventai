from fastapi import APIRouter
from services.patent_service.app.services.pqai_client import PQAIClient
from packages.graph.neo4j_client import graph_store

router = APIRouter()
pqai = PQAIClient()

@router.get("/search")
async def search_patents(q: str):
    # 1. Search Neo4j Knowledge Graph first (Local Graph)
    graph_query = """
    MATCH (p:Patent)-[:IMPLEMENTS]->(t:Technology)
    WHERE t.name CONTAINS $query
    RETURN p.id AS patent_id, p.title AS title
    """
    local_results = graph_store.execute_query(graph_query, {"query": q})
    
    # 2. Search PQAI (Global Search)
    global_results = await pqai.search_prior_art(q)
    
    return {
        "local_graph_matches": local_results,
        "pqai_global_matches": global_results
    }
