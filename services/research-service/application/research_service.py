from fastapi import FastAPI
from services.research_service.repositories.research_repo import ResearchRepository
from services.research_service.schemas.research_schemas import ResearchPaperCreate, ResearchPaperResponse
from services.research_service.workflows.research_workflow import build_research_rag_workflow
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.workflows.state import WorkflowState

class ResearchApplicationService:
    """
    Business use case orchestrator for RAG.
    Ties together Repositories, Vector DBs, and AI Workflows.
    """
    def __init__(self, repo: ResearchRepository, memory_manager: MemoryManager):
        self.repo = repo
        self.memory = memory_manager
        self.workflow = build_research_rag_workflow(self.memory)

    async def query_knowledge_base(self, query: str) -> dict:
        """
        Triggers the AI RAG orchestration to answer a research question.
        """
        initial_state = {
            "workflow_id": "temp_res", 
            "session_id": "temp_res", 
            "input_data": {"query": query},
            "metadata": {},
            "output_data": {},
            "messages": []
        }
        final_state = await self.workflow.ainvoke(initial_state)
        return final_state.get("output_data", {})

    async def analyze_research(self, topic: str) -> dict:
        """
        Deeper analysis: gap analysis, technology trends, future work.
        """
        return await self.query_knowledge_base(f"Analyze the research landscape, gap analysis, and technology trends for: {topic}")

    async def get_citations(self, paper_id: str) -> dict:
        from services.research_service.citations.citation_engine import CitationEngine
        # In a real impl, fetch from db/cache
        engine = CitationEngine()
        engine.add_paper(paper_id, {"title": f"Paper {paper_id}"})
        engine.add_paper("ref1", {"title": "Reference 1"})
        engine.add_citation(paper_id, "ref1")
        return engine.get_citation_graph(paper_id)

    async def get_history(self) -> list:
        # Mocking history retrieval
        return [{"query": "AI Agents", "timestamp": "2026-07-19T10:00:00Z"}]

    async def get_paper_summary(self, paper_id: str) -> dict:
        paper = await self.repo.get_by_id(paper_id)
        return {"summary": paper.abstract if paper else "No summary available"}

    async def get_paper(self, paper_id: str):
        return await self.repo.get_by_id(paper_id)

    async def upload_paper(self, paper_in: ResearchPaperCreate) -> ResearchPaperResponse:
        """
        CRUD operation and real ingestion.
        """
        paper_db = await self.repo.create(paper_in)
        # Background task for ingestion would go here using document_parser and chroma_store
        # e.g., BackgroundTask.add(index_pdf(paper_db.url))
        return ResearchPaperResponse.from_orm(paper_db)

# Create and configure FastAPI app
app = FastAPI(
    title="InventAI Research Service",
    description="RAG-based academic research knowledge base",
    version="1.0.0"
)

# Lazy import to avoid circular dependencies
from services.research_service.api.routers import router
app.include_router(router)
