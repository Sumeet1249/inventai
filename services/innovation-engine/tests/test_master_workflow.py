import pytest
from services.innovation_engine.domain.project_models import ProjectRequest
from services.innovation_engine.application.innovation_service import InnovationApplicationService
from services.innovation_engine.repositories.project_repo import InMemoryProjectRepository
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.tests.test_agent_lifecycle import MockMemoryProvider

@pytest.mark.asyncio
async def test_master_innovation_workflow():
    manager = MemoryManager(MockMemoryProvider())
    repo = InMemoryProjectRepository()
    service = InnovationApplicationService(repo, manager)
    
    req = ProjectRequest(name="Project X", idea_description="A new drone design")
    
    # Execute the Master LangGraph workflow end-to-end
    result = await service.start_invention_project(req)
    
    assert result.status == "Completed"
    assert result.patent_data is not None
    assert result.cad_data is not None
    assert result.cad_data.get("status") == "generated"
