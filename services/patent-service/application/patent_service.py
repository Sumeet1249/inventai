from services.patent_service.repositories.patent_repo import PatentRepository
from services.patent_service.schemas.patent_schemas import PatentCreate, PatentResponse
from services.patent_service.workflows.patent_workflow import build_patent_analysis_workflow
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.workflows.state import WorkflowState
from services.patent_service.pqai.pqai_client import pqai_client
from fastapi import HTTPException

class PatentApplicationService:
    """
    Business use case orchestrator.
    Ties together Repositories, AI Workflows, and External APIs.
    """
    def __init__(self, repo: PatentRepository, memory_manager: MemoryManager):
        self.repo = repo
        self.memory = memory_manager
        self.workflow = build_patent_analysis_workflow(self.memory)

    async def submit_patent_idea(self, idea_description: str) -> dict:
        """
        Triggers the AI orchestration to analyze an idea for patentability.
        """
        initial_state = WorkflowState(
            workflow_id="temp", 
            session_id="temp", 
            input_data={"idea": idea_description}
        )
        
        # Execute the compiled LangGraph workflow
        final_state = await self.workflow.ainvoke(initial_state)
        
        return final_state.get("output_data", {})

    async def search_prior_art(self, query: str):
        """Direct PQAI search bypass without full RAG workflow."""
        results = await pqai_client.search_prior_art(query)
        return {"results": results}

    async def get_patent_by_id(self, patent_id: int):
        patent = await self.repo.get_by_id(patent_id)
        if not patent:
            raise HTTPException(status_code=404, detail="Patent not found")
        return patent

    async def get_similar_patents(self, patent_id: int):
        # Stub for returning similar based on vector search of the patent's abstract
        return {"results": []}

    async def get_search_history(self):
        # Stub for returning user's past search queries from DB
        return {"history": []}

    async def create_patent_record(self, patent_in: PatentCreate) -> PatentResponse:
        """Standard CRUD operation leveraging the repository."""
        patent_db = await self.repo.create(patent_in)
        return PatentResponse.from_orm(patent_db)
