import pytest
from services.patent_service.schemas.patent_schemas import PatentCreate, InventorSchema
from services.patent_service.application.patent_service import PatentApplicationService
from services.patent_service.repositories.patent_repo import PatentRepository
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider

class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): pass
    async def delete(self, key): pass

class MockRepo:
    async def create(self, patent_in):
        # Return mock patent
        class MockPatent:
            id = "test_id"
            title = patent_in.title
            abstract = patent_in.abstract
            claims = patent_in.claims
            status = "Pending"
            filing_date = None
            inventors = []
        return MockPatent()

@pytest.mark.asyncio
async def test_analyze_idea_workflow():
    manager = MemoryManager(MockMemoryProvider())
    repo = MockRepo()
    service = PatentApplicationService(repo, manager)
    
    # Execute the LangGraph workflow end-to-end
    result = await service.submit_patent_idea("A new way to orchestrate AI agents")
    
    # Reviewer agent currently returns "Validated content" as mock
    assert result == "Validated content"
