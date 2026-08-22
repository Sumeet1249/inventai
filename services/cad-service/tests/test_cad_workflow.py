import pytest
from services.cad_service.schemas.cad_schemas import CADGenerationRequest
from services.cad_service.application.cad_service import CADApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.tests.test_agent_lifecycle import MockMemoryProvider

@pytest.mark.asyncio
async def test_cad_generation_workflow():
    manager = MemoryManager(MockMemoryProvider())
    service = CADApplicationService(manager)
    
    req = CADGenerationRequest(project_id="p1", prompt="Generate a simple box with length 10")
    
    # Execute the LangGraph CAD workflow end-to-end
    result = await service.generate_model(req)
    
    assert "status" in result
    assert result["status"] == "completed"
    assert "gltf_url" in result
    assert "step_url" in result
    assert "parameters" in result
