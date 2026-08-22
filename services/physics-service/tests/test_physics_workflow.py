import pytest
from services.physics_service.schemas.physics_schemas import SimulationRequest
from services.physics_service.application.physics_service import PhysicsApplicationService
from packages.ai_core.memory.memory_manager import MemoryManager
from packages.ai_core.tests.test_agent_lifecycle import MockMemoryProvider

@pytest.mark.asyncio
async def test_physics_simulation_workflow():
    manager = MemoryManager(MockMemoryProvider())
    service = PhysicsApplicationService(manager)
    
    req = SimulationRequest(
        cad_model_id="cad_123", 
        simulation_type="stress",
        material_id="steel_304",
        boundary_conditions={"force": 1000, "fixed_face": "bottom"}
    )
    
    # Execute the LangGraph PINN workflow end-to-end
    result = await service.run_simulation(req)
    
    assert "status" in result
    assert result["status"] == "Pass" # Safety factor > 1.0
    assert "results" in result
