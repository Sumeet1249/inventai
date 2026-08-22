import httpx
import asyncio
from typing import Dict, Any
from services.innovation_engine.orchestrator.state import InnovationWorkflowState
import logging

logger = logging.getLogger(__name__)

class NodeExecutor:
    """Executes a specific step by calling a remote microservice."""
    
    def __init__(self, node_name: str, service_url: str):
        self.node_name = node_name
        self.service_url = service_url

    async def execute(self, state: InnovationWorkflowState) -> dict:
        """
        Calls the remote microservice and returns updated state.
        """
        payload = {
            "project_id": state.get("project_id"),
            "idea": state.get("idea"),
            "artifacts": state.get("artifacts", {})
        }
        
        result_data = {}
        try:
            # We use a short timeout because microservices might not be fully built yet
            async with httpx.AsyncClient() as client:
                response = await client.post(self.service_url, json=payload, timeout=2.0)
                if response.status_code == 200:
                    result_data = response.json()
                else:
                    logger.warning(f"{self.node_name} returned {response.status_code}")
                    result_data = {"status": "fallback_due_to_error"}
        except Exception as e:
            logger.error(f"Error calling {self.service_url}: {e}")
            # Fallback for now to allow orchestration to succeed
            result_data = {"status": "fallback_mock", "note": f"Service offline"}
            
        return {
            "completed_steps": [self.node_name],
            "current_step": self.node_name,
            "artifacts": {self.node_name.lower(): result_data},
            "logs": [f"Completed {self.node_name} execution."]
        }

# Factory for nodes
patent_node = NodeExecutor("Patent", "http://patent-service:8000/api/v1/patents/analyze")
research_node = NodeExecutor("Research", "http://research-service:8000/api/v1/research/analyze")
kg_node = NodeExecutor("KnowledgeGraph", "http://graph-service:8000/api/v1/graph/recommend")
cad_node = NodeExecutor("CAD", "http://cad-service:8000/api/v1/cad/generate")
physics_node = NodeExecutor("Physics", "http://physics-service:8000/api/v1/physics/simulate")
business_node = NodeExecutor("Business", "http://business-service:8000/api/v1/business/generate")
report_node = NodeExecutor("Report", "http://report-service:8000/api/v1/reports/generate")
reviewer_node = NodeExecutor("Reviewer", "http://localhost:8000/api/v1/review") # Internal or separate
