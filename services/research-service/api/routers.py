from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from services.research_service.infrastructure.database import get_db
from services.research_service.schemas.research_schemas import ResearchPaperCreate, ResearchPaperResponse, ResearchQuerySchema
from services.research_service.repositories.research_repo import ResearchRepository
from services.research_service.application.research_service import ResearchApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider

router = APIRouter(prefix="/api/v1/research", tags=["Research"])

# Mock memory provider for DI
class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): pass
    async def delete(self, key): pass

def get_research_service(db: AsyncSession = Depends(get_db)):
    repo = ResearchRepository(db)
    memory_manager = MemoryManager(MockMemoryProvider())
    return ResearchApplicationService(repo, memory_manager)

@router.post("/papers", response_model=ResearchPaperResponse)
async def upload_paper(
    paper_in: ResearchPaperCreate,
    service: ResearchApplicationService = Depends(get_research_service)
):
    """Uploads a new research paper and triggers background OCR/Indexing."""
    return await service.upload_paper(paper_in)

@router.post("/search")
async def search_knowledge_base(
    query: ResearchQuerySchema,
    service: ResearchApplicationService = Depends(get_research_service)
):
    """
    Triggers the LangGraph RAG Workflow to perform Semantic Search, 
    and synthesize an answer from indexed PDFs.
    """
    result = await service.query_knowledge_base(query.query)
    return result

@router.post("/analyze")
async def analyze_research(
    query: ResearchQuerySchema,
    service: ResearchApplicationService = Depends(get_research_service)
):
    """Performs deep analysis, trends and gap analysis."""
    result = await service.analyze_research(query.query)
    return result

@router.get("/{id}")
async def get_paper(
    id: str,
    service: ResearchApplicationService = Depends(get_research_service)
):
    """Gets a paper by ID."""
    result = await service.get_paper(id)
    return result

@router.get("/summary/{id}")
async def get_paper_summary(
    id: str,
    service: ResearchApplicationService = Depends(get_research_service)
):
    """Gets AI summary of a paper."""
    result = await service.get_paper_summary(id)
    return result

@router.get("/citations/{id}")
async def get_citations(
    id: str,
    service: ResearchApplicationService = Depends(get_research_service)
):
    """Gets citation graph for a paper."""
    result = await service.get_citations(id)
    return result

@router.get("/history")
async def get_history(
    service: ResearchApplicationService = Depends(get_research_service)
):
    """Gets search history."""
    result = await service.get_history()
    return result
