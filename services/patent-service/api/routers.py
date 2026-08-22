from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from services.patent_service.infrastructure.database import get_db
from services.patent_service.schemas.patent_schemas import PatentCreate, PatentResponse, SearchQuerySchema, AnalysisResultSchema
from services.patent_service.repositories.patent_repo import PatentRepository
from services.patent_service.application.patent_service import PatentApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider

router = APIRouter(prefix="/api/v1/patents", tags=["Patents"])

# Mock memory provider for DI
class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): pass
    async def delete(self, key): pass

def get_patent_service(db: AsyncSession = Depends(get_db)):
    repo = PatentRepository(db)
    memory_manager = MemoryManager(MockMemoryProvider())
    return PatentApplicationService(repo, memory_manager)

@router.post("/", response_model=PatentResponse)
async def create_patent(
    patent_in: PatentCreate,
    service: PatentApplicationService = Depends(get_patent_service)
):
    """Creates a new patent record."""
    return await service.create_patent_record(patent_in)

@router.post("/analyze")
async def analyze_idea(
    query: SearchQuerySchema,
    service: PatentApplicationService = Depends(get_patent_service)
):
    """
    Triggers the LangGraph AI Workflow to perform Semantic Search, 
    Novelty Analysis, and Prior-Art detection.
    """
    result = await service.submit_patent_idea(query.query)
    return {"analysis": result}

@router.post("/search")
async def search_patents(
    query: SearchQuerySchema,
    service: PatentApplicationService = Depends(get_patent_service)
):
    """Direct semantic search against prior art."""
    return await service.search_prior_art(query.query)

@router.get("/{patent_id}", response_model=PatentResponse)
async def get_patent(
    patent_id: int,
    service: PatentApplicationService = Depends(get_patent_service)
):
    """Get a specific patent by ID."""
    return await service.get_patent_by_id(patent_id)

@router.get("/similar")
async def get_similar_patents(
    id: int,
    service: PatentApplicationService = Depends(get_patent_service)
):
    """Finds patents similar to the given patent ID."""
    return await service.get_similar_patents(id)

@router.get("/history")
async def get_search_history(
    service: PatentApplicationService = Depends(get_patent_service)
):
    """Returns past search history."""
    return await service.get_search_history()
