import pytest
from services.research_service.schemas.research_schemas import ResearchPaperCreate, AuthorSchema
from services.research_service.application.research_service import ResearchApplicationService
from services.research_service.repositories.research_repo import ResearchRepository
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.memory.interfaces import BaseMemoryProvider

class MockMemoryProvider(BaseMemoryProvider):
    async def get(self, key): return None
    async def set(self, key, value, ttl=None): pass
    async def delete(self, key): pass

class MockRepo:
    async def create(self, paper_in):
        class MockPaper:
            id = "test_paper_id"
            title = paper_in.title
            abstract = paper_in.abstract
            url = paper_in.url
            status = "Processing"
            published_date = None
            uploaded_at = None
            authors = []
        return MockPaper()

@pytest.mark.asyncio
async def test_rag_query_workflow():
    manager = MemoryManager(MockMemoryProvider())
    repo = MockRepo()
    service = ResearchApplicationService(repo, manager)
    
    # We will mock the ainvoke of the compiled workflow to avoid hitting OpenAI 
    # since we are running isolated tests
    from unittest.mock import AsyncMock
    service.workflow.ainvoke = AsyncMock(return_value={
        "output_data": {
            "summary": "Mocked summary",
            "key_findings": ["Finding 1"],
            "citations": []
        }
    })

    result = await service.query_knowledge_base("How does LangGraph work?")
    
    assert "summary" in result
    assert result["summary"] == "Mocked summary"
    assert "key_findings" in result
